from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, feed, profile, interactions, contacts, messenger
import uvicorn

app = FastAPI(title="Social Network Frontend")

# Статика
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(profile.router)
app.include_router(interactions.router)
app.include_router(contacts.router)
app.include_router(messenger.router)

@app.get("/")
async def home():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/login")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)