from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from Library_Management.database import get_db
from Library_Management.models import Token
from Library_Management.utils import helper
from Library_Management.schema import TokenResponse
auth = helper()
auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="User API")


@auth_router.post("/login",tags=['User API'],response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = auth.authenticate_user(db, form_data.username, form_data.password)
    print(user.role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )
    token = auth.create_access_token(data={"email": user.email})
    return {"access_token": token, "token_type": "bearer"}


@auth_router.post("/logout",tags=['User API'])
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    existing = db.query(Token).filter(Token.token == token).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token already logged out"
        )

    db_token = Token(token=token)
    db.add(db_token)
    db.commit()

    return {"message": "Logged out successfully"}


