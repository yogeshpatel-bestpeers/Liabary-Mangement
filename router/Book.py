from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from Library_Management import models
from Library_Management.database import get_db
from Library_Management.Schema import schema

book = APIRouter()


@book.post("/book/create", tags=["Book Api"],status_code=status.HTTP_201_CREATED)
async def book_create(model: schema.Book_Created, db: AsyncSession = Depends(get_db)):
    new_book = models.Book(**model.model_dump())

    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)

    return {"details": "Book Created Successfully", "book": new_book}


@book.get("/book/get/", tags=["Book Api"])
async def book_get(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
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


@book.delete("/book/delete", tags=["Book Api"],status_code=status.HTTP_204_NO_CONTENT)
async def book_delete(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Book).where(models.Book.id == id))
    book = result.scalars().first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
        )

    await db.delete(book)
    await db.commit()
    return {"details": "Book deleted successfully"}


@book.put("/book/update/{id}", tags=["Book Api"],status_code=status.HTTP_202_ACCEPTED)
async def book_update(
    id: str, model: schema.Book_Created, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Book).where(models.Book.id == id))
    book = result.scalars().first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
        )

    for key, value in model.dict().items():
        setattr(book, key, value)

    await db.commit()
    await db.refresh(book)
    return book
