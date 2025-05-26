from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Library_Management.database import Fine, get_db
from Library_Management.models import FineCreate, FineUpdate

fine = APIRouter()


@fine.get("/fine/get")
def create_fine(db: Session, fine: FineCreate):
    db_fine = Fine(**fine.__dict__)
    db.add(db_fine)
    db.commit()
    db.refresh(db_fine)
    return db_fine


@fine.get("/fine/get/{fine_id}")
def get_fine(fine_id: int, db: Session = Depends(get_db)):
    return db.query(Fine).filter(Fine.id == fine_id).first()


@fine.get("/fine/get/{issued_book_id}")
def get_fines_by_book(issued_book_id: int, db: Session = Depends(get_db)):
    return db.query(Fine).filter(Fine.issued_book_id == issued_book_id).all()


@fine.put("/fine/update/{fine_id}")
def update_fine(fine_id: int, fine_data: FineUpdate, db: Session = Depends(get_db)):
    db_fine_query = db.query(Fine).filter(Fine.id == fine_id)
    db_fine = db_fine.first()
    if not db_fine:
        return None
    db_fine_query.update(fine_data.__dict__)
    db.commit()
    db.refresh(db_fine)
    return db_fine


@fine.delete("/fine/delete/{fine_id}")
def delete_fine(fine_id: int, db: Session = Depends(get_db)):
    db_fine = db.query(Fine).filter(Fine.id == fine_id).first()
    if not db_fine:
        return None
    db.delete(db_fine)
    db.commit()
    return db_fine
