from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from Library_Management import database, models
from Library_Management.Schema import schema
from Library_Management.utils import admin_required

author = APIRouter()


@author.post("/author/create", tags=["Author Api"])
async def author_create(
    model: schema.Author_Created,
    db: AsyncSession = Depends(database.get_db),
    user=Depends(admin_required),
):
    new_author = models.Author(**model.__dict__)

    db.add(new_author)
    await db.commit()
    await db.refresh(new_author)

    return {"details": "Author Created Successfully", "author": new_author}


@author.get("/author/get/", tags=["Author Api"])
async def author_get(
    db: AsyncSession = Depends(database.get_db),
    user=Depends(admin_required),
):
    result = await db.execute(
        select(models.Author).options(joinedload(models.Author.books))
    )
    authors = result.scalars().all()

    if not authors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author Not Found"
        )

    return authors


@author.delete("/author/delete", tags=["Author Api"])
async def author_delete(
    id: str,
    db: AsyncSession = Depends(database.get_db),
    user=Depends(admin_required),
):
    result = await db.execute(select(models.Author).where(models.Author.id == id))
    author = result.scalars().first()

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author Not Found"
        )

    await db.delete(author)
    await db.commit()

    return {"detail": "Author deleted successfully"}


@author.put("/author/update/{id}", tags=["Author Api"])
async def author_update(
    id: str,
    model: schema.Author_Created,
    db: AsyncSession = Depends(database.get_db),
    user=Depends(admin_required),
):
    result = await db.execute(select(models.Author).where(models.Author.id == id))
    author = result.scalars().first()

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author Not Found"
        )

    for key, value in model.dict().items():
        setattr(author, key, value)

    await db.commit()
    await db.refresh(author)

    return author
