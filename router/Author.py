from fastapi import APIRouter,Depends,status
from fastapi.exceptions import HTTPException
from Library_Management.database import get_db
from sqlalchemy.orm import Session
from Library_Management import models,database

author = APIRouter()


@author.post('/author/create')
def author_create(model:models.Author_Created,db : Session =Depends(get_db)):
  new_author = database.Author(**model.__dict__)

  db.add(new_author)
  db.commit()
  db.refresh(new_author) 

  return{'details':'Author Created Sucessfully','author':new_author}

@author.get('/author/get/')
def auther_get(db : Session =Depends(get_db)):
  author = db.query(database.Author).all()

  if not author:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail ='Author Not Found')

  return author

@author.delete('/author/delete')
def author_delete(id : str,db : Session =Depends(get_db)):
    author = db.query(database.Author).filter(database.Author.id == id).first()
    if not author:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND, detail=f"Author Not Found"
          )
    db.delete(author)
    db.commit()
    return {"detail": "Author deleted Sucesfully"}

@author.put('/author/update/{id}')
def author_update(id : str,model: models.Author_Created,db : Session =Depends(get_db)):
    author = db.query(database.Author).filter(database.Author.id == id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author Not Found"
        )

    author.update(model)
    db.commit()
    db.refresh(author) 
    return author


