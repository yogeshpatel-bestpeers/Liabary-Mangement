from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Library_Management import models, schema
from Library_Management.database import get_db
from Library_Management.utils import admin_required, helper

user_router = APIRouter()
utils = helper()


@user_router.post("/signup", status_code=status.HTTP_201_CREATED, tags=["Admin Api"])
async def create_User(
    model: schema.User_Created, db: Session = Depends(get_db), admin=admin_required
):
    hashed_password = utils.hash_password(model.passwords)

    email = db.query(models.User).filter(models.User.email == model.email).first()

    if email:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, detail=f"Email Already Exist"
        )

    User_data = model.__dict__
    User_data["passwords"] = hashed_password

    new_User = models.User(**User_data)
    db.add(new_User)
    db.commit()
    db.refresh(new_User)

    return new_User


@user_router.delete("/User/delete", status_code=status.HTTP_200_OK, tags=["Admin Api"])
async def delete_User(id: str, db: Session = Depends(get_db), user=admin_required):
    User = db.query(models.User).filter(models.User.id == id).first()
    if not User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )
    db.delete(User)
    db.commit()
    return {"detail": "User deleted Sucesfully"}


@user_router.put(
    "/User/update/{id}", status_code=status.HTTP_202_ACCEPTED, tags=["Admin Api"]
)
async def update_User(
    id: str,
    model: schema.User_Update,
    db: Session = Depends(get_db),
    admin=admin_required,
):
    User_query = db.query(models.User).filter(models.User.id == id)
    User = User_query.first()
    model.passwords = utils.hash_password(model.passwords)
    if not User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )

    User_query.update(model.__dict__)
    db.commit()
    return User_query.first()


@user_router.get("/User/getAll", tags=["Admin Api"])
async def showUser(db: Session = Depends(get_db), user=admin_required):
    Users = db.query(models.User).all()
    if not Users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No User found"
        )
    return Users
