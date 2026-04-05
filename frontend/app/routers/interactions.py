from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from ..api_client import BackendClient
from ..dependencies import get_backend_client

router = APIRouter()

@router.post("/like/{post_id}")
async def like_post(
    post_id: int,
    token: str = Form(...)
):
    async with get_backend_client() as client:
        await client.post(f"/posts/{post_id}/like", token=token)
        return RedirectResponse(url=f"/feed?token={token}", status_code=303)

@router.post("/unlike/{post_id}")
async def unlike_post(
    post_id: int,
    token: str = Form(...)
):
    async with get_backend_client() as client:
        await client.delete(f"/posts/{post_id}/like", token=token)
        return RedirectResponse(url=f"/feed?token={token}", status_code=303)

@router.post("/comment/{post_id}")
async def add_comment(
    post_id: int,
    token: str = Form(...),
    content: str = Form(...)
):
    async with get_backend_client() as client:
        await client.post(f"/posts/{post_id}/comments", json={"content": content}, token=token)
        return RedirectResponse(url=f"/feed?token={token}", status_code=303)