from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from Library_Management.database import get_db
from Library_Management.models import Book, Cart, IssuedBook
from Library_Management.utils import admin_required, user_required
from fastapi_utils.cbv import cbv
from .fine import create_fine, get_fine

issuedBook = APIRouter(tags=['Book Issue Api'])

@cbv(issuedBook)
class BokkIssueView():
    db: AsyncSession = Depends(get_db)

    @issuedBook.get("/admin/get/issuedBook")
    async def get__issued_books(self,
        user=Depends(admin_required)
    ):
        result = await self.db.execute(
            select(IssuedBook)
            .options(joinedload(IssuedBook.user), joinedload(IssuedBook.fine))
            .filter(IssuedBook.returned_date == None)
        )
        return result.scalars().all()


    @issuedBook.post(
        "/book/issue",
        status_code=status.HTTP_201_CREATED,
    )
    async def issued_book(self, user=Depends(user_required)):

        cart_result = await self.db.execute(select(Cart).where(Cart.user_id == user.id))
        cart_items = cart_result.scalars().all()

        if not cart_items:
            raise HTTPException(
                detail="Your cart is empty.", status_code=status.HTTP_404_NOT_FOUND
            )

        due_date = datetime.now() + timedelta(days=2)
        issued_books = []

        for item in cart_items:

            book_result = await self.db.execute(select(Book).where(Book.id == item.book_id))
            book = book_result.scalars().first()

            if not book:
                continue

            if book.quantity <= 0:
                continue

            book.quantity -= 1

            new_issue = IssuedBook(book_id=book.id, user_id=user.id, due_date=due_date)
            self.db.add(new_issue)
            issued_books.append(new_issue)
            await self.db.delete(item)

        if not issued_books:
            raise HTTPException(
                detail="No books could be issued due to out-of-stock or missing data.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        await self.db.commit()

        await self.db.refresh(issued_books[-1])

        return {
            "details": "Book(s) issued successfully",
            "issued_count": len(issued_books),
            "due_date": due_date.strftime("%Y-%m-%d %H:%M:%S"),
        }


    @issuedBook.delete("/book/return/{book_id}")
    async def return_book(self,
        book_id: str, user=Depends(user_required)
    ):
        result = await self.db.execute(
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

        result = await self.db.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(
                detail="Book Not Found", status_code=status.HTTP_404_NOT_FOUND
            )

        fine_info = get_fine(issued_book)
        fine = 0
        if fine_info["amount"] > 0:
            fine = await create_fine(self.db, fine_info)

        book.quantity += 1
        issued_book.returned_date = datetime.now()
        await self.db.commit()

        if fine != 0:
            return {"detail": "Book returned successfully", "fine amount": fine}

        return {"detail": "Book returned successfully"}
