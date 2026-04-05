from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud, schemas
from .auth import get_current_user
from ..models import User

router = APIRouter(prefix="/contacts", tags=["contacts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.UserOut])
def get_all_contacts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    contacts = crud.get_all_users(db)
    return contacts