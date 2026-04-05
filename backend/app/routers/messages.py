from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud, schemas
from .auth import get_current_user
from ..models import Message

router = APIRouter(prefix="/messages", tags=["messages"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dialogs")
def get_dialogs(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_dialogs(db, current_user.id)

@router.get("/history/{user_id}")
def get_history(user_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    messages = crud.get_messages_between_users(db, current_user.id, user_id)
    return messages

@router.put("/read/{user_id}")
def mark_messages_as_read(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Обновляем все сообщения от user_id к current_user, где is_read = False
    updated = db.query(Message).filter(
        Message.sender_id == user_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"updated": updated}