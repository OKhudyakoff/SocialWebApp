from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud, schemas
from .auth import get_user_from_token
import json
from ..models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    # Проверяем токен в query-параметре (например, ?token=...)
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    user = get_user_from_token(token, db)
    if not user or user.id != user_id:
        await websocket.close(code=1008)
        return

    from ..websocket_manager import manager
    user.is_online = True
    db.commit()
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            receiver_id = message_data.get("receiver_id")
            content = message_data.get("content")

            # Сохраняем сообщение в БД
            msg_create = schemas.MessageCreate(receiver_id=receiver_id, content=content)
            db_message = crud.create_message(db, msg_create, user_id)

            # Отправляем сообщение получателю, если он онлайн
            sender_user = db.query(User).filter(User.id == user_id).first()
            await manager.send_personal_message({
                "type": "new_message",
                "message": {
                    "id": db_message.id,
                    "sender_id": user_id,
                    "sender_name": sender_user.username,   # добавить
                    "receiver_id": receiver_id,
                    "content": content,
                    "created_at": db_message.created_at.isoformat(),
                    "is_read": False
                }
            }, receiver_id)

            # Подтверждение отправителю
            await websocket.send_json({"type": "sent", "message_id": db_message.id})
    except WebSocketDisconnect:
        user = db.query(User).filter(User.id == user_id).first()
        user.is_online = False
        db.commit()
        manager.disconnect(user_id)