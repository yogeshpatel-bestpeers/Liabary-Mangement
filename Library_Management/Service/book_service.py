# services/book_service.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Library_Management.Repository.AuthorRepository import BookRepository
from Library_Management.Schema.schema import Book_Created

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    async def create_book(self, db: AsyncSession, data: Book_Created):
        return await self.repo.create(db, data)

    async def get_books(self, db: AsyncSession):
        books = await self.repo.get_all(db,relationships=["category","author"])
        if not books:
            raise HTTPException(status_code=404, detail="No Books found")
        return books

    async def delete_book(self, db: AsyncSession, id: str):
        book = await self.repo.get_by_id(db, id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        await self.repo.delete(db, book)

    async def update_book(self, db: AsyncSession, id: str, data: Book_Created):
        book = await self.repo.get_by_id(db, id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return await self.repo.update(db, book, data)
