from fastapi import FastAPI
from .database import engine, Base
from .routers import auth, users, posts, contacts, messages, websocket

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Social Network API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(contacts.router)
app.include_router(messages.router)
app.include_router(websocket.router)

@app.get("/")
def root():
    return {"message": "Social Network API"}