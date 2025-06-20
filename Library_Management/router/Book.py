from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from Library_Management.Service.book_service import BookService
from Library_Management import models
from Library_Management.database import get_db
from Library_Management.Schema import schema

book = APIRouter(tags=["Book Api"])


@cbv(book)
class BookView:
    db: AsyncSession = Depends(get_db)
    book_service = BookService()

    @book.post("/book/create", status_code=status.HTTP_201_CREATED)
    async def book_create(self, model: schema.Book_Created):

        new_book = await self.book_service.create_book(self.db,model)

        return {"details": "Book Created Successfully", "book": new_book}

    @book.get("/book/get/")
    async def book_get(self):

        books = await self.book_service.get_books(self.db)

        return books

    @book.delete("/book/delete", status_code=status.HTTP_204_NO_CONTENT)
    async def book_delete(self, id: str):

        await self.book_service.delete_book(self.db,id)
        
        return {"details": "Book deleted successfully"}

    @book.put("/book/update/{id}", status_code=status.HTTP_202_ACCEPTED)
    async def book_update(self, id: str, model: schema.Book_Created):

        book = await self.book_service.update_book(self.db,id,model)

        return book
