from fastapi import Request, HTTPException
from .api_client import BackendClient
from contextlib import asynccontextmanager
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

@asynccontextmanager
async def get_backend_client():
    client = BackendClient(BACKEND_URL)
    try:
        yield client
    finally:
        await client.close()

async def get_current_user_info(request: Request, token: str, client: BackendClient):
    resp = await client.get("/auth/me", token=token)
    if resp.status_code == 200:
        return resp.json()
    return {"username": "User", "id": 0}