from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi_utils.cbv import cbv
from Library_Management import database, models
from Library_Management.Schema import schema
from Library_Management.utils import admin_required

author = APIRouter(tags=["Author Api"])

@cbv(author)
class AuthorView:
    db: AsyncSession = Depends(database.get_db)

    @author.post("/author/create")
    async def author_create(self,
        model: schema.Author_Created,
        user=Depends(admin_required)
    ):
        new_author = models.Author(**model.__dict__)

        self.db.add(new_author)
        await self.db.commit()
        await self.db.refresh(new_author)

        return {"details": "Author Created Successfully", "author": new_author}


    @author.get("/author/get/")
    async def author_get(self,
        user=Depends(admin_required),
    ):
        result = await self.self.db.execute(
            select(models.Author).options(joinedload(models.Author.books))
        )
        authors = result.scalars().all()

        if not authors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author Not Found"
            )

        return authors


    @author.delete("/author/delete")
    async def author_delete(self,
        id: str,
        user=Depends(admin_required),
    ):
        result = await self.db.execute(select(models.Author).where(models.Author.id == id))
        author = result.scalars().first()

        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author Not Found"
            )

        await self.db.delete(author)
        await self.db.commit()

        return {"detail": "Author deleted successfully"}


    @author.put("/author/update/{id}")
    async def author_update(self,
        id: str,
        model: schema.Author_Created,
        user=Depends(admin_required),
    ):
        result = await self.db.execute(select(models.Author).where(models.Author.id == id))
        author = result.scalars().first()

        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author Not Found"
            )

        for key, value in model.model_dump().items():
            setattr(author, key, value)

        await self.db.commit()
        await self.db.refresh(author)

        return author
