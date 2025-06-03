from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Library_Management.database import get_db
from Library_Management.models import Fine

fine = APIRouter()


def get_fine(issued_book):
    if datetime.now() > issued_book.due_date:
        days_late = (datetime.now() - issued_book.due_date).days
        return {"amount": days_late * 5, "issued_book_id": issued_book.id}
    return {"amount": 0, "issued_book_id": issued_book.id}


async def create_fine(db: AsyncSession, fine_data: dict):
    db_fine = Fine(**fine_data)
    db.add(db_fine)
    await db.commit()
    await db.refresh(db_fine)
    return db_fine


@fine.get("/fine/get/{issued_book_id}")
async def get_fines_by_book(
    issued_book_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Fine).filter(Fine.issued_book_id == issued_book_id))
    fines = result.scalars().all()
    return fines
