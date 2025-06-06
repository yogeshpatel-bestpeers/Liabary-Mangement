import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator,ConfigDict

from Library_Management.models import UserRole


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

    @field_validator("email")
    def validate_email(cls, value):
        regex = r"^[a-zA-Z0-9._%+-]+@gmail\.com$"
        if not re.match(regex, value):
            raise ValueError("Email must be in the format 'username@gmail.com'")
        return value

    @field_validator("passwords")
    def validate_password(cls, value):

        if not re.search(r"^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$", value):
            raise ValueError(
                "Password must be at least 8 characters long, contain at least one uppercase letter, one number, and one special character (e.g., !@#$%^&*)."
            )

        return value


class User_Update(BaseModel):
    email: str
    first_name: str
    last_name: str
    passwords: str
    role: UserRole


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

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
