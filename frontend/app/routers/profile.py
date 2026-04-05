from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..api_client import BackendClient
from ..dependencies import get_backend_client, get_current_user_info

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/user/{user_id}", response_class=HTMLResponse)
async def user_profile(
    request: Request,
    user_id: int,
    token: str
):
    async with get_backend_client() as client:
        # Получаем данные пользователя
        resp_user = await client.get(f"/users/{user_id}", token=token)
        if resp_user.status_code != 200:
            return RedirectResponse(url=f"/feed?token={token}")
        user = resp_user.json()
        # Получаем посты пользователя
        resp_posts = await client.get(f"/users/{user_id}/posts", token=token)
        user_posts = resp_posts.json() if resp_posts.status_code == 200 else []
        # Текущий пользователь для меню
        current_user = await get_current_user_info(request, token, client)
        return templates.TemplateResponse("user.html", {
            "request": request,
            "user": user,
            "posts": user_posts,
            "token": token,
            "current_username": current_user["username"],
            "current_user_id": current_user["id"]
        })