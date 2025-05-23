from fastapi import APIRouter,Depends,status
from fastapi.exceptions import HTTPException
from Library_Management.database import get_db
from sqlalchemy.orm import Session,joinedload
from Library_Management import models,database


book = APIRouter()


@book.post('/book/create',tags=['Book Api'])
def book_create(model:models.Book_Created,db : Session =Depends(get_db)):
  new_book = database.Book(**model.__dict__)

  db.add(new_book)
  db.commit()
  db.refresh(new_book) 

  return{'details':'Book Created Sucessfully','book':new_book}

@book.get('/book/get/',tags=['Book Api'])
def auther_get(db : Session =Depends(get_db)):
  book = db.query(database.Book).options(joinedload(database.Book.category),joinedload(database.Book.author)).all()

  if not book:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail ='Book Not Found')

  return book

@book.delete('/book/delete',tags=['Book Api'])
def book_delete(id : str,db : Session =Depends(get_db)):
    book = db.query(database.Book).filter(database.Book.id == id).first()
    if not book:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND, detail=f"Book Not Found"
          )
    db.delete(book)
    db.commit()
    return {"detail": "Book deleted Sucesfully"}

@book.put('/book/update/{id}',tags=['Book Api'])
def book_update(id : str,model: models.Book_Created,db : Session =Depends(get_db)):
    book = db.query(database.Book).filter(database.Book.id == id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book Not Found"
        )

    book.update(model)
    db.commit()
    db.refresh(book) 
    return book


