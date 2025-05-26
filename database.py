import os
import uuid
from typing import List,Optional

from dotenv import load_dotenv
from sqlalchemy import ForeignKey, create_engine,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy import Enum as sqlEnum
from enum import Enum
from datetime import datetime


class UserRole(str,Enum):
    ADMIN = "admin"
    Student = "student"

load_dotenv()

db_password = os.getenv("DB_PASSWORD")
db_user = os.getenv("DB_USER")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_user}:{db_password}@localhost/{db_name}"
engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Author, Category, Book, Course, Student, IssuedBook, and Fine

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)

    books: Mapped[List["Book"]] = relationship("Book", back_populates="author",cascade="all, delete")


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)

    books: Mapped[List["Book"]] = relationship("Book", back_populates="category",cascade="all, delete")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)

    author_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("authors.id", ondelete='CASCADE'), nullable=False
)

    category_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("categories.id", ondelete='CASCADE'), nullable=False
    )


    author: Mapped["Author"] = relationship("Author", back_populates="books",cascade="all, delete")
    category: Mapped["Category"] = relationship("Category", back_populates="books",cascade="all, delete")
    issued_books: Mapped[List["IssuedBook"]] = relationship(
        "IssuedBook", back_populates="book",cascade="all, delete"
    )


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email : Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    first_name : Mapped[str] = mapped_column( nullable=True)
    last_name: Mapped[str] = mapped_column( nullable=True)
    passwords : Mapped[str] = mapped_column( nullable=False,server_default="")
    role: Mapped[UserRole] = mapped_column(
        sqlEnum(UserRole, name="userrole"),
        nullable=False,
        default=UserRole.Student,
    )

    issued_books: Mapped[List["IssuedBook"]] = relationship(
        "IssuedBook", back_populates="user",cascade="all, delete"
    )


class IssuedBook(Base):
    __tablename__ = "issuedbooks"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    due_date: Mapped[datetime] = mapped_column(DateTime)
    returned_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id",ondelete='CASCADE'), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id",ondelete='CASCADE'), nullable=False
    )

    book: Mapped["Book"] = relationship("Book", back_populates="issued_books",cascade="all, delete")
    user: Mapped["User"] = relationship("User", back_populates="issued_books",cascade="all, delete")
    fine: Mapped["Fine"] = relationship("Fine", back_populates="issued_book",cascade="all, delete")


class Fine(Base):
    __tablename__ = "fines"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    amount: Mapped[float] = mapped_column(nullable=False)
    issued_book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("issuedbooks.id",ondelete='CASCADE'), nullable=False
    )

    issued_book: Mapped["IssuedBook"] = relationship(
        "IssuedBook", back_populates="fine",cascade="all, delete"
    )