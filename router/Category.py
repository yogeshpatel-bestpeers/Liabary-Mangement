from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session, joinedload

from Library_Management import models, schema
from Library_Management.database import get_db
from Library_Management.utils import admin_required

category = APIRouter()


@category.post("/category/create", tags=["Category Api"])
def category_create(
    model: schema.Category_Created, db: Session = Depends(get_db), user=admin_required
):
    new_category = models.Category(**model.__dict__)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {"details": "Category Created Sucessfully", "category": new_category}


@category.get("/category/get/", tags=["Category Api"])
def auther_get(db: Session = Depends(get_db), user=admin_required):
    category = (
        db.query(models.Category).options(joinedload(models.Category.books)).all()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )

    return category


@category.delete("/category/delete", tags=["Category Api"])
def category_delete(id: str, db: Session = Depends(get_db), user=admin_required):
    category = db.query(models.Category).filter(models.Category.id == id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )
    db.delete(category)
    db.commit()

    return {"detail": "Category and related books deleted successfully"}


@category.put("/category/update/{id}", tags=["Category Api"])
def category_update(
    id: str,
    model: schema.Category_Created,
    db: Session = Depends(get_db),
    user=admin_required,
):
    category = db.query(models.Category).filter(models.Category.id == id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
        )

    category.update(model)
    db.commit()
    db.refresh(category)
    return category
