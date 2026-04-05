from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..dependencies import get_backend_client, get_current_user_info

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/feed", response_class=HTMLResponse)
async def feed(request: Request, token: str):
    async with get_backend_client() as client:
        # Получаем посты
        resp_posts = await client.get("/posts/", token=token)
        if resp_posts.status_code != 200:
            return RedirectResponse(url="/login")
        posts = resp_posts.json()
        
        # Получаем текущего пользователя
        user_data = await get_current_user_info(request, token, client)
    
    return templates.TemplateResponse("feed.html", {
        "request": request,
        "posts": posts,
        "token": token,
        "current_username": user_data["username"],
        "current_user_id": user_data["id"]
    })

@router.post("/feed")
async def create_post(request: Request, token: str = Form(...), content: str = Form(...)):
    async with get_backend_client() as client:
        await client.post("/posts/", json={"content": content}, token=token)
    return RedirectResponse(url=f"/feed?token={token}", status_code=303)