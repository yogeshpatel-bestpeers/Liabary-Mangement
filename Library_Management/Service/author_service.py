# services/author_service.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Library_Management.Repository.AuthorRepository import AuthorRepository
from Library_Management.Schema.schema import Author_Created

class AuthorService:
    def __init__(self):
        self.repo = AuthorRepository()

    async def create_author(self, db: AsyncSession, data: Author_Created):
        return await self.repo.create(db, data)

    async def get_authors(self, db: AsyncSession):
        authors = await self.repo.get_all(db)
        if not authors:
            raise HTTPException(status_code=404, detail="No authors found")
        return authors

    async def delete_author(self, db: AsyncSession, id: str):
        author = await self.repo.get_by_id(db, id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        await self.repo.delete(db, author)

    async def update_author(self, db: AsyncSession, id: str, data: Author_Created):
        author = await self.repo.get_by_id(db, id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        return await self.repo.update(db, author, data)
