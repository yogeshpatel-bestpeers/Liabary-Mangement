from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Library_Management import models
from Library_Management.Schema import schema
from Library_Management.database import get_db
from Library_Management.utils import admin_required, Helper

user_router = APIRouter()
utils = Helper()


@user_router.post("/signup", status_code=status.HTTP_201_CREATED, tags=["Admin Api"])
async def create_User(
    model: schema.User_Created,
    db: AsyncSession = Depends(get_db),
):
    hashed_password = utils.hash_password(model.passwords)

    result = await db.execute(select(models.User).filter(models.User.email == model.email))
    email = result.scalars().first()

    if email:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, detail="Email Already Exist"
        )

    User_data = model.dict()
    User_data["passwords"] = hashed_password

    new_User = models.User(**User_data)
    db.add(new_User)
    await db.commit()
    await db.refresh(new_User)

    return new_User


@user_router.delete("/User/delete", status_code=status.HTTP_200_OK, tags=["Admin Api"])
async def delete_User(
    id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required),
):
    result = await db.execute(select(models.User).where(models.User.id == id))
    User = result.scalars().first()

    if not User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )

    await db.delete(User)
    await db.commit()
    return {"detail": "User deleted successfully"}


@user_router.put("/User/update/{id}", status_code=status.HTTP_202_ACCEPTED, tags=["Admin Api"])
async def update_User(
    id: str,
    model: schema.User_Update,
    db: AsyncSession = Depends(get_db),
    admin=Depends(admin_required),
):
    result = await db.execute(select(models.User).where(models.User.id == id))
    User = result.scalars().first()

    if not User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )

    model.passwords = utils.hash_password(model.passwords)
    for key, value in model.dict().items():
        setattr(User, key, value)

    await db.commit()
    await db.refresh(User)

    return User


@user_router.get("/User/getAll", tags=["Admin Api"])
async def showUser(db: AsyncSession = Depends(get_db), user=Depends(admin_required)):
    result = await db.execute(select(models.User))
    Users = result.scalars().all()

    if not Users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No User found",
        )

    return Users
