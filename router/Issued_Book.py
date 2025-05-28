from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from Library_Management.database import get_db
from Library_Management.models import Book, IssuedBook
from Library_Management.utils import admin_required, user_required

from .fine import create_fine, get_fine

issuedBook = APIRouter()

@issuedBook.get("/admin/get/issuedBook", tags=["Admin Api"])
async def get__issued_books(db: AsyncSession = Depends(get_db), user=Depends(admin_required)):
    result = await db.execute(
        select(IssuedBook)
        .options(joinedload(IssuedBook.user), joinedload(IssuedBook.fine))
        .filter(IssuedBook.returned_date == None)
    )
    return result.scalars().all()

@issuedBook.get("/get/issuedBook", tags=["Issued Books Management"])
async def get_current_issued_books(db: AsyncSession = Depends(get_db), user=Depends(user_required)):
    result = await db.execute(
        select(IssuedBook)
        .options(joinedload(IssuedBook.fine))
        .filter(IssuedBook.returned_date == None, IssuedBook.user_id == user.id)
    )
    books = result.scalars().all()
    if not books:
        return {"detail": "No Book Issued"}
    return books

@issuedBook.post("/book/issue/{book_id}", status_code=status.HTTP_201_CREATED, tags=["Issued Books Management"])
async def issued_book(book_id: str, db: AsyncSession = Depends(get_db), user=Depends(user_required)):
    due_date = datetime.now() + timedelta(days=2)

    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()

    if not book:
        raise HTTPException(detail="Book Not Found", status_code=status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(IssuedBook).where(IssuedBook.user_id == user.id, IssuedBook.returned_date == None)
    )
    issued_book = result.scalars().first()
    if issued_book:
        raise HTTPException(detail="Already Issued By You", status_code=status.HTTP_400_BAD_REQUEST)

    if book.quantity <= 0:
        raise HTTPException(detail="Book out of stock", status_code=status.HTTP_400_BAD_REQUEST)

    book_issued = IssuedBook(book_id=book_id, user_id=user.id, due_date=due_date)
    book.quantity -= 1
    db.add(book_issued)
    await db.commit()
    await db.refresh(book_issued)

    return {"details": "Book issued successfully", "issued_book": book_issued}

@issuedBook.delete("/book/return/{book_id}", tags=["Issued Books Management"])
async def return_book(book_id: str, db: AsyncSession = Depends(get_db), user=Depends(user_required)):
    result = await db.execute(
        select(IssuedBook).where(
            IssuedBook.book_id == book_id,
            IssuedBook.user_id == user.id,
            IssuedBook.returned_date == None,
        )
    )
    issued_book = result.scalars().first()
    if not issued_book:
        raise HTTPException(
            detail="Issued Book Not Found or Already Returned",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(detail="Book Not Found", status_code=status.HTTP_404_NOT_FOUND)

    fine_info = get_fine(issued_book)
    fine = 0
    if fine_info["amount"] > 0:
        fine = create_fine(db, fine_info)

    book.quantity += 1
    issued_book.returned_date = datetime.now()
    await db.commit()

    if fine != 0:
        return {"detail": "Book returned successfully", "fine amount": fine}

    return {"detail": "Book returned successfully"}
