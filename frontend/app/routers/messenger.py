from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from ..dependencies import get_backend_client, get_current_user_info

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request, token: str):
    async with get_backend_client() as client:
        dialogs_resp = await client.get("/messages/dialogs", token=token)
        dialogs = dialogs_resp.json() if dialogs_resp.status_code == 200 else []
        current_user = await get_current_user_info(request, token, client)
    return templates.TemplateResponse("messenger.html", {
        "request": request,
        "dialogs": dialogs,
        "token": token,
        "current_user": current_user,
        "current_username": current_user["username"],
        "current_user_id": current_user["id"]
    })

@router.get("/chat/{user_id}", response_class=HTMLResponse)
async def chat_page(request: Request, user_id: int, token: str):
    async with get_backend_client() as client:
        msgs_resp = await client.get(f"/messages/history/{user_id}", token=token)
        messages = msgs_resp.json() if msgs_resp.status_code == 200 else []
        current_user = await get_current_user_info(request, token, client)
        other_user_resp = await client.get(f"/users/{user_id}", token=token)
        other_user = other_user_resp.json() if other_user_resp.status_code == 200 else {}
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "other_user": other_user,
        "messages": messages,
        "token": token,
        "current_user": current_user,
        "current_username": current_user["username"],
        "current_user_id": current_user["id"]
    })

@router.get("/messages/partial", response_class=HTMLResponse)
async def messages_partial(request: Request, token: str = Query(...)):
    async with get_backend_client() as client:
        dialogs_resp = await client.get("/messages/dialogs", token=token)
        dialogs = dialogs_resp.json() if dialogs_resp.status_code == 200 else []
    return templates.TemplateResponse("messages_partial.html", {"request": request, "dialogs": dialogs, "token": token})

@router.put("/messages/read/{user_id}")
async def mark_messages_as_read(request: Request, user_id: int, token: str):
    async with get_backend_client() as client:
        resp = await client.put(f"/messages/read/{user_id}", token=token)
        return JSONResponse(
            status_code=resp.status_code,
            content=resp.json() if resp.status_code == 200 else {"error": "Failed"}
        )