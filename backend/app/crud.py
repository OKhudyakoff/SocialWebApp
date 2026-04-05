from sqlalchemy.orm import Session
from . import models, schemas, auth

# Пользователи
def create_user(db: Session, user: schemas.UserCreate):
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(models.User).all()

# Посты
def get_posts(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(content=post.content, user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Комменты
def create_comment(db: Session, comment: schemas.CommentCreate, user_id: int, post_id: int):
    db_comment = models.Comment(content=comment.content, user_id=user_id, post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_for_post(db: Session, post_id: int, skip: int = 0, limit: int = 50):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id)\
        .order_by(models.Comment.created_at).offset(skip).limit(limit).all()

def get_comments_count(db: Session, post_id: int) -> int:
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).count()

# Лайки
def like_post(db: Session, user_id: int, post_id: int):
    existing = db.query(models.Like).filter_by(user_id=user_id, post_id=post_id).first()
    if existing:
        return None
    db_like = models.Like(user_id=user_id, post_id=post_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like

def unlike_post(db: Session, user_id: int, post_id: int):
    db_like = db.query(models.Like).filter_by(user_id=user_id, post_id=post_id).first()
    if db_like:
        db.delete(db_like)
        db.commit()
        return True
    return False

def get_likes_count(db: Session, post_id: int) -> int:
    return db.query(models.Like).filter(models.Like.post_id == post_id).count()

def user_liked_post(db: Session, user_id: int, post_id: int) -> bool:
    return db.query(models.Like).filter_by(user_id=user_id, post_id=post_id).first() is not None

# Сообщения
def create_message(db: Session, message: schemas.MessageCreate, sender_id: int):
    db_message = models.Message(
        sender_id=sender_id,
        receiver_id=message.receiver_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_between_users(db: Session, user1_id: int, user2_id: int, limit: int = 50):
    return db.query(models.Message).filter(
        ((models.Message.sender_id == user1_id) & (models.Message.receiver_id == user2_id)) |
        ((models.Message.sender_id == user2_id) & (models.Message.receiver_id == user1_id))
    ).order_by(models.Message.created_at).limit(limit).all()

def get_user_dialogs(db: Session, user_id: int):
    # Возвращает список уникальных собеседников с последним сообщением
    # Сложный запрос, упростим: сначала получаем всех, с кем пользователь обменивался сообщениями
    sent = db.query(models.Message.receiver_id).filter(models.Message.sender_id == user_id).distinct()
    received = db.query(models.Message.sender_id).filter(models.Message.receiver_id == user_id).distinct()
    user_ids = set([r[0] for r in sent]) | set([r[0] for r in received])
    dialogs = []
    for uid in user_ids:
        last_msg = db.query(models.Message).filter(
            ((models.Message.sender_id == user_id) & (models.Message.receiver_id == uid)) |
            ((models.Message.sender_id == uid) & (models.Message.receiver_id == user_id))
        ).order_by(models.Message.created_at.desc()).first()
        other_user = db.query(models.User).filter(models.User.id == uid).first()
        dialogs.append({
            "user": other_user,
            "last_message": last_msg,
            "unread_count": db.query(models.Message).filter(
                models.Message.sender_id == uid,
                models.Message.receiver_id == user_id,
                models.Message.is_read == False
            ).count()
        })
    return dialogs

def mark_messages_as_read(db: Session, sender_id: int, receiver_id: int):
    updated = db.query(models.Message).filter(
        models.Message.sender_id == sender_id,
        models.Message.receiver_id == receiver_id,
        models.Message.is_read == False
    ).update({"is_read": True})
    db.commit()
    return updated