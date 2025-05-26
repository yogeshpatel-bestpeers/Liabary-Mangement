from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Library_Management.database import get_db
from Library_Management.models import IssuedBook,Book

issuedBook = APIRouter()    


@issuedBook.get("/get/issuedBook", tags=["Issued Books Management"])
def get_current_issued_books(db: Session = Depends(get_db)):
    return db.query(IssuedBook).filter(IssuedBook.returned_date == None).all()


@issuedBook.post(
    "/book/issue/{student_id}/{book_id}",
    status_code=status.HTTP_201_CREATED,
    tags=["Issued Books Management"],
)
def issued_book(student_id: str, book_id: str, db: Session = Depends(get_db)):
    due_date = datetime.now() + timedelta(days=14)

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            detail="Book Not Found", status_code=status.HTTP_404_NOT_FOUND
        )

    issued_book = (
        db.query(IssuedBook)
        .filter(IssuedBook.book_id == book_id, IssuedBook.user_id == student_id)
        .first()
    )

    if issued_book:
        raise HTTPException(
            detail="Already Issued By You", status_code=status.HTTP_400_BAD_REQUEST
        )
    if book.quantity <= 0:
        raise HTTPException(
            detail="Book out of stock", status_code=status.HTTP_400_BAD_REQUEST
        )

    book_issued = IssuedBook(book_id=book_id, user_id=student_id, due_date=due_date)
    book.quantity -= 1
    db.add(book_issued)
    db.commit()
    db.refresh(book_issued)
    return {"details": "Book issued successfully", "issued_book": book_issued}


@issuedBook.delete("/book/return/{book_id}", tags=["Issued Books Management"])
def return_book(student_id: str, book_id: str, db: Session = Depends(get_db)):

    issued_book = (
        db.query(IssuedBook)
        .filter(
            IssuedBook.book_id == book_id,
            IssuedBook.user_id == student_id,
            IssuedBook.returned_date == None,
        )
        .first()
    )

    if not issued_book:
        raise HTTPException(
            detail="Issued Book Not Found or Already Returned",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            detail="Book Not Found", status_code=status.HTTP_404_NOT_FOUND
        )

    book.quantity += 1
    issued_book.returned_date = datetime.now()
    db.commit()

    return {"detail": "Book returned successfully"}
