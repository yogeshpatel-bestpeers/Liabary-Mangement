from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Library_Management.database import get_db
from Library_Management.models import Token
from Library_Management.schema import TokenResponse
from Library_Management.utils import Helper

auth = Helper()
auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="User API")


@auth_router.post("/login", tags=["User API"], response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    token = auth.create_access_token(data={"email": user.email})

    return {"access_token": token, "token_type": "bearer"}


@auth_router.post("/logout", tags=["User API"])
async def logout(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Token).where(Token.token == token))
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already logged out"
        )

    db_token = Token(token=token)
    db.add(db_token)
    await db.commit()

    return {"message": "Logged out successfully"}
