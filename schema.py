from datetime import datetime
from typing import Optional
from Library_Management.models import UserRole
from pydantic import BaseModel


class Author_Created(BaseModel):
    name: str


class Book_Created(BaseModel):
    name: str
    quantity: int
    author_id: str
    category_id: str


class Category_Created(BaseModel):
    name: str


class User_Created(BaseModel):
    email: str
    first_name: str
    last_name: str
    passwords: str

class User_Update(BaseModel):
    email: str
    first_name: str
    last_name: str
    passwords: str
    role : UserRole


class FineBase(BaseModel):
    amount: float
    reason: Optional[str]
    issued_book_id: int
    student_id: int


class FineCreate(FineBase):
    pass


class FineUpdate(BaseModel):
    amount: Optional[float]
    reason: Optional[str]


class FineOut(FineBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str