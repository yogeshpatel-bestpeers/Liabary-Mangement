from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from Library_Management.Service.author_service import AuthorService
from Library_Management import database
from Library_Management.Schema import schema
from Library_Management.utils import admin_required

author = APIRouter(tags=["Author Api"])


@cbv(author)
class AuthorView:
    db: AsyncSession = Depends(database.get_db)
    author_service = AuthorService()

    @author.post("/author/create")
    async def author_create(
        self, model: schema.Author_Created, user=Depends(admin_required)
    ):
        new_author = await self.author_service.create_author(self.db, model)

        return {"details": "Author Created Successfully", "author": new_author}

    @author.get("/author/get/")
    async def author_get(
        self,
        user=Depends(admin_required),
    ):  
        authors = await self.author_service.get_authors(self.db)
        return authors

    @author.delete("/author/delete",status_code= status.HTTP_200_OK)
    async def author_delete(
        self,
        id: str,
        user=Depends(admin_required),
    ):
        await self.author_service.delete_author(self.db,id)

        return JSONResponse(content={"detail": "Author deleted successfully"})

    @author.put("/author/update/{id}")
    async def author_update(
        self,
        id: str,
        model: schema.Author_Created,
        user=Depends(admin_required),
    ):
        await self.author_service.update_author(self.db,id,model)

        return JSONResponse(content={"detail": "Author updated successfully"},status_code=status.HTTP_202_ACCEPTED)
