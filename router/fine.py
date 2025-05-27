from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Library_Management.database import get_db
from Library_Management.models import Fine

fine = APIRouter()


def get_fine(issued_book):
    if issued_book.due_date and datetime.now() > issued_book.due_date:
        days_late = (datetime.now() - issued_book.due_date).days
        return {"amount": days_late * 5, "issued_book_id": issued_book.id}
    return {"amount": 0, "issued_book_id": issued_book.id}


def create_fine(db: Session, fine_data: dict):
    db_fine = Fine(**fine_data)
    db.add(db_fine)
    db.commit()
    db.refresh(db_fine)
    return db_fine


@fine.get("/fine/get/{issued_book_id}")
def get_fines_by_book(issued_book_id: int, db: Session = Depends(get_db)):
    return db.query(Fine).filter(Fine.issued_book_id == issued_book_id).all()
