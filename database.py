import os
import uuid
from typing import List

from dotenv import load_dotenv
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker

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

    books: Mapped[List["Book"]] = relationship("Book", back_populates="author")


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)

    books: Mapped[List["Book"]] = relationship("Book", back_populates="category")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)

    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("authors.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )

    author: Mapped["Author"] = relationship("Author", back_populates="books")
    category: Mapped["Category"] = relationship("Category", back_populates="books")
    issued_books: Mapped[List["IssuedBook"]] = relationship(
        "IssuedBook", back_populates="book"
    )


class Student(Base):
    __tablename__ = "students"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)

    issued_books: Mapped[List["IssuedBook"]] = relationship(
        "IssuedBook", back_populates="student"
    )


class IssuedBook(Base):
    __tablename__ = "issuedbooks"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )

    book: Mapped["Book"] = relationship("Book", back_populates="issued_books")
    student: Mapped["Student"] = relationship("Student", back_populates="issued_books")
    fine: Mapped["Fine"] = relationship("Fine", back_populates="issued_book")


class Fine(Base):
    __tablename__ = "fines"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    amount: Mapped[float] = mapped_column(nullable=False)
    issued_book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("issuedbooks.id"), nullable=False
    )

    issued_book: Mapped["IssuedBook"] = relationship(
        "IssuedBook", back_populates="fine"
    )