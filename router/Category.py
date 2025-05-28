from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from Library_Management import models, schema
from Library_Management.database import get_db
from Library_Management.utils import admin_required

category = APIRouter()


@category.post("/category/create", tags=["Category Api"])
async def category_create(
    model: schema.Category_Created,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required),
):
    new_category = models.Category(**model.dict())

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return {"details": "Category Created Successfully", "category": new_category}


@category.get("/category/get/", tags=["Category Api"])
async def category_get(
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required),
):
    result = await db.execute(
        select(models.Category).options(joinedload(models.Category.books))
    )
    categories = result.scalars().all()

    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )

    return categories


@category.delete("/category/delete", tags=["Category Api"])
async def category_delete(
    id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required),
):
    result = await db.execute(select(models.Category).where(models.Category.id == id))
    category_obj = result.scalars().first()

    if not category_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )

    await db.delete(category_obj)
    await db.commit()

    return {"detail": "Category and related books deleted successfully"}


@category.put("/category/update/{id}", tags=["Category Api"])
async def category_update(
    id: str,
    model: schema.Category_Created,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required),
):
    result = await db.execute(select(models.Category).where(models.Category.id == id))
    category_obj = result.scalars().first()

    if not category_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )

    for key, value in model.dict().items():
        setattr(category_obj, key, value)

    await db.commit()
    await db.refresh(category_obj)

    return category_obj
