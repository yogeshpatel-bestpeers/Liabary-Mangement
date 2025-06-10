from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Library_Management import models
from Library_Management.database import get_db
from Library_Management.Schema import schema
from Library_Management.utils import Helper, admin_required

user_router = APIRouter(tags=["User Api"])
utils = Helper()


@cbv(user_router)
class UserView:
    db: AsyncSession = Depends(get_db)

    @user_router.post("/signup", status_code=status.HTTP_201_CREATED)
    async def create_User(
        self,
        model: schema.User_Created,
    ):
        hashed_password = utils.hash_password(model.passwords)

        result = await self.db.execute(
            select(models.User).filter(models.User.email == model.email)
        )
        email = result.scalars().first()

        if email:
            raise HTTPException(
                status_code=status.HTTP_302_FOUND, detail="Email Already Exist"
            )

        User_data = model.__dict__
        User_data["passwords"] = hashed_password

        new_User = models.User(**User_data)
        self.db.add(new_User)
        await self.db.commit()
        await self.db.refresh(new_User)

        return new_User

    @user_router.delete("/User/delete", status_code=status.HTTP_200_OK)
    async def delete_User(
        self,
        id: str,
        user=Depends(admin_required),
    ):
        result = await self.db.execute(select(models.User).where(models.User.id == id))
        User = result.scalars().first()

        if not User:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {id} not found",
            )

        await self.db.delete(User)
        await self.db.commit()
        return {"detail": "User deleted successfully"}

    @user_router.put("/User/update/{id}", status_code=status.HTTP_202_ACCEPTED)
    async def update_User(
        self,
        id: str,
        model: schema.User_Update,
        admin=Depends(admin_required),
    ):
        result = await self.db.execute(select(models.User).where(models.User.id == id))
        User = result.scalars().first()

        if not User:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {id} not found",
            )

        model.passwords = utils.hash_password(model.passwords)
        for key, value in model.dict().items():
            setattr(User, key, value)

        await self.db.commit()
        await self.db.refresh(User)

        return User

    @user_router.get("/User/getAll")
    async def showUser(self, user=Depends(admin_required)):
        result = await self.db.execute(select(models.User))
        Users = result.scalars().all()

        if not Users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No User found",
            )

        return Users
