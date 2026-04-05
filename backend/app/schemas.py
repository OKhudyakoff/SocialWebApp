from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    is_online: bool = False

    class Config:
        from_attributes=True
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class CommentCreate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserOut

    class Config:
        from_attributes=True
        orm_mode = True

class LikeOut(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    content: str

class PostOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserOut
    comments: list[CommentOut] = []
    comments_count: int = 0
    likes_count: int = 0
    liked: bool = False

    class Config:
        from_attributes=True
        orm_mode = True

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime
    is_read: bool

    class Config:
        orm_mode = True