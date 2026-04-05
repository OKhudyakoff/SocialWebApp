from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..api_client import BackendClient
from ..dependencies import get_backend_client

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),):
    async with get_backend_client() as client:
        resp = await client.post("/auth/login", data={"username": username, "password": password})
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            return RedirectResponse(url=f"/feed?token={token}", status_code=303)
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    async with get_backend_client() as client:
        resp = await client.post("/auth/register", json={"username": username, "email": email, "password": password})
        if resp.status_code == 200:
            return RedirectResponse(url="/login", status_code=303)
        error = resp.json().get("detail", "Registration failed")
        return templates.TemplateResponse("register.html", {"request": request, "error": error})

@router.get("/logout")
async def logout():
    return RedirectResponse(url="/login", status_code=303)