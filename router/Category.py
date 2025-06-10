from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi_utils.cbv import cbv
from Library_Management import models
from Library_Management.database import get_db
from Library_Management.Schema import schema
from Library_Management.utils import admin_required

category = APIRouter(tags=['Categary Api'])

@cbv(category)
class CategaryView():
    db: AsyncSession = Depends(get_db)

    @category.post("/category/create",status_code=status.HTTP_201_CREATED)
    async def category_create(self,
        model: schema.Category_Created,
        user=Depends(admin_required),
    ):
        new_category = models.Category(**model.model_dump())

        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)

        return {"details": "Category Created Successfully", "category": new_category}


    @category.get("/category/get",status_code = status.HTTP_200_OK)
    async def category_get(self,
        user=Depends(admin_required),
    ):
        result = await self.db.execute(
            select(models.Category).options(joinedload(models.Category.books))
        )
        categories = result.unique().scalars().all() 

        if not categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
            )

        return categories


    @category.delete("/category/delete",status_code=status.HTTP_204_NO_CONTENT)
    async def category_delete(self,
        id: str,
        user=Depends(admin_required),
    ):
        result = await self.db.execute(select(models.Category).where(models.Category.id == id))
        category_obj = result.scalars().first()

        if not category_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
            )

        await self.db.delete(category_obj)
        await self.db.commit()

        return {"detail": "Category and related books deleted successfully"}


    @category.put("/category/update/{id}",status_code=status.HTTP_202_ACCEPTED)
    async def category_update(self,
        id: str,
        model: schema.Category_Created,
        user=Depends(admin_required),
    ):
        result = await self.db.execute(select(models.Category).where(models.Category.id == id))
        category_obj = result.scalars().first()

        if not category_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
            )

        for key, value in model.model_dump().items():
            setattr(category_obj, key, value)

        await self.db.commit()
        await self.db.refresh(category_obj)

        return category_obj
