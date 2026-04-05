from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud, schemas
from .auth import get_current_user
from ..models import Post

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/posts", response_model=list[schemas.PostOut])
def get_user_posts(user_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    posts = db.query(Post).filter(Post.user_id == user_id)\
        .order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for post in posts:
        comments = crud.get_comments_for_post(db, post.id, limit=5)
        likes_count = crud.get_likes_count(db, post.id)
        liked = crud.user_liked_post(db, user_id, post.id)
        post_out = schemas.PostOut.from_orm(post)
        post_out.comments = comments
        post_out.likes_count = likes_count
        post_out.liked = liked
        result.append(post_out)
    return result