from fastapi import APIRouter, Query, Depends
from typing import Optional, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Library_Management.models import Book, Author, Category
from Library_Management.database import get_db

search_router = APIRouter()

@search_router.get("/search")
async def searchApi(
    keyword: str = Query(..., min_length=1, description="Keyword to search"),
    type: Optional[Literal["book", "author", "category"]] = Query(
        None, description="Filter by item type"
    ),
    db: AsyncSession = Depends(get_db),
):
    results = {}

    if type in (None, "book"):
        result = await db.execute(select(Book).filter(Book.name.ilike(f"%{keyword}%")))
        books = result.scalars().all()
        results["books"] = [{"id": b.id, "title": b.name, "author": b.author} for b in books]

    if type in (None, "author"):
        result = await db.execute(select(Author).filter(Author.name.ilike(f"%{keyword}%")))
        authors = result.scalars().all()
        results["authors"] = [{"id": a.id, "name": a.name} for a in authors]

    if type in (None, "category"):
        result = await db.execute(select(Category).filter(Category.name.ilike(f"%{keyword}%")))
        categories = result.scalars().all()
        results["categories"] = [{"id": c.id, "name": c.name} for c in categories]

    return {"results": results}
