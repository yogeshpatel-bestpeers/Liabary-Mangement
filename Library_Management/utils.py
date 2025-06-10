from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi_mail import ConnectionConfig
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Library_Management.config import get_settings

from .models import Token, User, UserRole

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_HOST_USER,
    MAIL_PASSWORD=settings.EMAIL_HOST_PASSWORD,
    MAIL_FROM=settings.EMAIL_HOST_USER,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_STARTTLS=settings.EMAIL_USE_TLS,
    MAIL_SSL_TLS=settings.EMAIL_USE_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


class Helper:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = settings.ALGORITHM
        self.FORGET_PWD_SECRET_KEY = settings.SECRET_KEY_FP
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.ACCESS_TOKEN_EXPIRE_MINUTES_FP = settings.ACCESS_TOKEN_EXPIRE_MINUTES_FP

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def create_access_token_password(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES_FP
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, self.FORGET_PWD_SECRET_KEY, algorithm=self.ALGORITHM
        )

    async def authenticate_user(self, db: AsyncSession, email: str, password: str):
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user or not self.verify_password(password, user.passwords):
            return None
        return user

    async def get_current_user(self, token: str, db: AsyncSession):

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get("email")

            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )

            result = await db.execute(select(User).where(User.email == email))
            user = result.scalars().first()

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found"
                )
            return user

        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired or Invalid",
            )

    def require_role(self, role: UserRole):
        async def checker(request: Request):
            user = request.state.user
            if not user or user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: Insufficient role",
                )
            return user

        return checker


auth_service = Helper()

admin_required = auth_service.require_role(UserRole.ADMIN)
user_required = auth_service.require_role(UserRole.Student)
