import httpx
from typing import Optional, Dict, Any

class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def post(self, path: str, data: Optional[Dict] = None, json: Optional[Dict] = None, token: Optional[str] = None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient() as client:
            return await client.post(
                f"{self.base_url}{path}",
                data=data,
                json=json,
                headers=headers,
                timeout=10.0
            )

    async def get(self, path: str, token: Optional[str] = None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient() as client:
            return await client.get(f"{self.base_url}{path}", headers=headers, timeout=10.0)
        
    async def delete(self, path: str, token: Optional[str] = None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient() as client:
            return await client.delete(f"{self.base_url}{path}", headers=headers, timeout=10.0)
        
    async def close(self):
        await self.client.aclose()

    async def put(self, path: str, token: Optional[str] = None, json: Optional[Dict] = None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient() as client:
            return await client.put(
                f"{self.base_url}{path}",
                json=json,
                headers=headers,
                timeout=10.0
            )
        
# Проверка