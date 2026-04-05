from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud, schemas
from .auth import get_current_user
from ..models import Post

router = APIRouter(prefix="/posts", tags=["posts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.PostOut])
def get_feed(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    result = []
    for post in posts:
        comments = crud.get_comments_for_post(db, post.id, limit=50)
        comments_count = crud.get_comments_count(db, post.id)
        likes_count = crud.get_likes_count(db, post.id)
        liked = crud.user_liked_post(db, current_user.id, post.id)
        post_out = schemas.PostOut.from_orm(post)
        post_out.comments = comments
        post_out.comments_count = comments_count
        post_out.likes_count = likes_count
        post_out.liked = liked
        result.append(post_out)
    return result

@router.post("/", response_model=schemas.PostOut)
def create_post(post: schemas.PostCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_post(db, post, current_user.id)

@router.post("/{post_id}/comments", response_model=schemas.CommentOut)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return crud.create_comment(db, comment, current_user.id, post_id)

@router.get("/{post_id}/comments", response_model=list[schemas.CommentOut])
def get_comments(post_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_comments_for_post(db, post_id, skip, limit)

@router.post("/{post_id}/like")
def like_post(post_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    like = crud.like_post(db, current_user.id, post_id)
    if not like:
        raise HTTPException(status_code=400, detail="Already liked")
    return {"message": "Liked"}

@router.delete("/{post_id}/like")
def unlike_post(post_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if crud.unlike_post(db, current_user.id, post_id):
        return {"message": "Unliked"}
    raise HTTPException(status_code=404, detail="Like not found")