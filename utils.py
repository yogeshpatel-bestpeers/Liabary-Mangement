import os
import jwt
from fastapi import Request,HTTPException,status,Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from .models import Token,User,UserRole

class helper:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")     
        self.SECRET_KEY = str(os.getenv("SECRET_KEY"))
        self.ALGORITHM = str(os.getenv("ALGORITHM"))
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    
    def authenticate_user(self, db, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.passwords):
            return None
        return user
    
    def get_current_user(self, token: str, db: Session):
        existing = db.query(Token).filter(Token.token == token).first()
        if existing:
            raise HTTPException(status_code=400, detail="Token has expired or Invalid")

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get("email")

            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )

            user = db.query(User).filter(User.email == email).first()

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
                )
            return user

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired or Invalid",
            )
    
    def require_role(self, role: User):
        def checker(request: Request):
            user = request.state.user
            if not user or user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: Insufficient role"
                )
            return user
        return checker
    
auth_service = helper()

admin_required = Depends(auth_service.require_role(UserRole.ADMIN))
user_required = Depends(auth_service.require_role(UserRole.Student))