from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session, joinedload

from Library_Management import database,schema,models

author = APIRouter()


@author.post("/author/create", tags=["Author Api"])
def author_create(model: schema.Author_Created, db: Session = Depends(database.get_db)):
    new_author = models.Author(**model.__dict__)

    db.add(new_author)
    db.commit()
    db.refresh(new_author)

    return {"details": "Author Created Sucessfully", "author": new_author}


@author.get("/author/get/", tags=["Author Api"])
def auther_get(db: Session = Depends(database.get_db)):
    author = db.query(models.Author).options(joinedload(models.Author.books)).all()

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author Not Found"
        )

    return author


@author.delete("/author/delete", tags=["Author Api"])
def author_delete(id: str, db: Session = Depends(database.get_db)):
    author = db.query(models.Author).filter(models.Author.id == id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Author Not Found"
        )
    db.delete(author)
    db.commit()
    return {"detail": "Author deleted Sucesfully"}


@author.put("/author/update/{id}", tags=["Author Api"])
def author_update(id: str, model: schema.Author_Created, db: Session = Depends(database.get_db)):
    author = db.query(models.Author).filter(models.Author.id == id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author Not Found"
        )

    author.update(model)
    db.commit()
    db.refresh(author)
    return author
