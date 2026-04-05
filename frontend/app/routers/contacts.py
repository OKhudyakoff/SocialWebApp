from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..api_client import BackendClient
from ..dependencies import get_backend_client, get_current_user_info

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/contacts", response_class=HTMLResponse)
async def user_profile(request: Request, token: str):
    async with get_backend_client() as client:
        resp_contacts = await client.get("/contacts/", token=token)
        if resp_contacts.status_code != 200:
            return RedirectResponse(url="/login")
        contacts = resp_contacts.json()
        user_data = await get_current_user_info(request, token, client)
        return templates.TemplateResponse("contacts.html", {
            "request": request,
            "contacts": contacts,
            "token": token,
            "current_username": user_data["username"],
            "current_user_id": user_data["id"]
        })