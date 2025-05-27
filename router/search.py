from fastapi import APIRouter,Query,Depends
from typing import Optional,Literal
from sqlalchemy.orm import Session
from Library_Management.models import Book,Author,Category
from Library_Management.database import get_db
search_router =APIRouter()

@search_router.get("/search")
def searchApi(
    keyword: str = Query(..., min_length=1, description="Keyword to search"),
    type: Optional[Literal["book", "author", "category"]] = Query(
        None, description="Filter by item type"
    ),
    db: Session = Depends(get_db)
):
    results = {}

    if type in (None, "book"):
        books = db.query(Book).filter(Book.name.ilike(f"%{keyword}%")).all()
        results["books"] = [{"id": b.name, "title": b.author} for b in books]

    if type in (None, "author"):
        authors = db.query(Author).filter(Author.name.ilike(f"%{keyword}%")).all()
        results["authors"] = [{"id": a.id, "name": a.name} for a in authors]

    if type in (None, "category"):
        categories = db.query(Category).filter(Category.name.ilike(f"%{keyword}%")).all()
        results["categories"] = [{"id": c.id, "name": c.name} for c in categories]

    return {"results": results}