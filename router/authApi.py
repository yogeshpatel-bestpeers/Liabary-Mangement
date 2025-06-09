import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_mail import FastMail, MessageSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Library_Management.database import get_db
from Library_Management.models import Token, User
from Library_Management.Schema import password_rest, schema
from Library_Management.utils import Helper, conf

auth = Helper()
auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@auth_router.post("/login", tags=["User API"], response_model=schema.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    token = auth.create_access_token(data={"email": user.email})

    return {"access_token": token, "token_type": "bearer"}


@auth_router.post("/logout", tags=["User API"], status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Token).where(Token.token == token))
    print("result ", result)
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token already logged out"
        )

    db_token = Token(token=token)
    db.add(db_token)
    await db.commit()

    return {"message": "Logged out successfully"}


@auth_router.post("/forget-password")
async def forgetPassword(
    forget: password_rest.ForgetPasswordRequest, db: AsyncSession = Depends(get_db)
):

    user = await db.execute(select(User).where(User.email == forget.email))
    user = user.scalars().first()
    if not user:
        raise HTTPException(
            detail="Invlaid Email", status_code=status.HTTP_404_NOT_FOUND
        )

    token = auth.create_access_token_password(data={"email": user.email})

    reset_link = f"http://localhost:8000/reset-password?token={token}"

    message = MessageSchema(
        subject="Reset Your Password",
        recipients=[user.email],
        body=f"<p>Click the link to reset your password:</p><a href='{reset_link}'>{reset_link}</a>",
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"detail": "Reset link sent to your email"}


@auth_router.post("/reset-password")
async def reset_password(
    request: Request,
    password: password_rest.Password_Request,
    db: AsyncSession = Depends(get_db),
):
    token = request.headers.get("Authorization")
    token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, auth.FORGET_PWD_SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = auth.hash_password(password.new_password)
    user.passwords = hashed_password
    await db.commit()

    return {"detail": "Password has been reset successfully"}
