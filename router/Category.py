from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session, joinedload

from Library_Management import database, models
from Library_Management.database import get_db

category = APIRouter()


@category.post("/category/create", tags=["Category Api"])
def category_create(model: models.Category_Created, db: Session = Depends(get_db)):
    new_category = database.Category(**model.__dict__)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {"details": "Category Created Sucessfully", "category": new_category}


@category.get("/category/get/", tags=["Category Api"])
def auther_get(db: Session = Depends(get_db)):
    category = (
        db.query(database.Category).options(joinedload(database.Category.books)).all()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )

    return category


@category.delete("/category/delete", tags=["Category Api"])
def category_delete(id: str, db: Session = Depends(get_db)):
    category = db.query(database.Category).filter(database.Category.id == id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )
    db.delete(category)
    db.commit()

    return {"detail": "Category and related books deleted successfully"}


@category.put("/category/update/{id}", tags=["Category Api"])
def category_update(
    id: str, model: models.Category_Created, db: Session = Depends(get_db)
):
    category = db.query(database.Category).filter(database.Category.id == id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )

    category.update(model)
    db.commit()
    db.refresh(category)
    return category
