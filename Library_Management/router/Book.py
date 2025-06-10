from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from Library_Management import models
from Library_Management.database import get_db
from Library_Management.Schema import schema

book = APIRouter(tags=["Book Api"])


@cbv(book)
class BookView:
    db: AsyncSession = Depends(get_db)

    @book.post("/book/create", status_code=status.HTTP_201_CREATED)
    async def book_create(self, model: schema.Book_Created):
        new_book = models.Book(**model.model_dump())

        self.db.add(new_book)
        await self.db.commit()
        await self.db.refresh(new_book)

        return {"details": "Book Created Successfully", "book": new_book}

    @book.get("/book/get/")
    async def book_get(self):
        result = await self.db.execute(
            select(models.Book).options(
                joinedload(models.Book.category), joinedload(models.Book.author)
            )
        )
        books = result.scalars().all()

        if not books:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
            )

        return books

    @book.delete("/book/delete", status_code=status.HTTP_204_NO_CONTENT)
    async def book_delete(self, id: str):
        result = await self.db.execute(select(models.Book).where(models.Book.id == id))
        book = result.scalars().first()

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
            )

        await self.db.delete(book)
        await self.db.commit()
        return {"details": "Book deleted successfully"}

    @book.put("/book/update/{id}", status_code=status.HTTP_202_ACCEPTED)
    async def book_update(self, id: str, model: schema.Book_Created):
        result = await self.db.execute(select(models.Book).where(models.Book.id == id))
        book = result.scalars().first()

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
            )

        for key, value in model.model_dump().items():
            setattr(book, key, value)

        await self.db.commit()
        await self.db.refresh(book)
        return book
