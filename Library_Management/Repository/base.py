from typing import TypeVar, Generic, Type, Optional, List, Union
from pydantic import BaseModel
from Library_Management.main import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

ModelType = TypeVar("ModelType",bound= Base)                # type: ignore
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)  

class BaseRepository(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_all(self,db: AsyncSession,relationships: Optional[List[str]] = None
        ) -> List[ModelType]:
            
        stmt = select(self.model)
        if relationships:
            for rel in relationships:
                stmt = stmt.options(joinedload(getattr(self.model, rel)))
        
        result = await db.execute(stmt)
        return result.unique().scalars().all()


    async def get_by_id(self, db: AsyncSession, id: Union[int, str]) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.__dict__)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, obj: ModelType) -> None:
        await db.delete(obj)
        await db.commit()

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: Union[dict, BaseModel]) -> ModelType:
        update_data = obj_in.__dict__ if isinstance(obj_in, BaseModel) else obj_in
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
        
    async def search_by_field( self,  db: AsyncSession,   field_name: str,   value: str,
        relationships: Optional[List[str]] = None
    ) -> List[ModelType]:
        field = getattr(self.model, field_name)
        stmt = select(self.model).where(field.ilike(f"%{value}%"))

        if relationships:
            for rel in relationships:
                stmt = stmt.options(joinedload(getattr(self.model, rel)))

        result = await db.execute(stmt)
        return result.scalars().all()