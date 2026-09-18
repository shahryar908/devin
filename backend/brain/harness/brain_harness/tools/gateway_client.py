from __future__ import annotations

from typing import Optional

import httpx


class GatewayHTTPClient:
    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _post(self, endpoint: str, **payload) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/{endpoint}", json=payload)
            response.raise_for_status()
        data = response.json()
        return data.get("output") or data.get("content") or ""

    async def exec(self, command: str, cwd: Optional[str] = None, timeout: Optional[int] = None) -> str:
        return await self._post("exec", command=command, cwd=cwd, timeout=timeout)

    async def read_file(self, path: str) -> str:
        return await self._post("read_file", path=path)

    async def write_file(self, path: str, content: str) -> str:
        return await self._post("write_file", path=path, content=content)

    async def list_dir(self, path: str = ".") -> str:
        return await self._post("list_dir", path=path)

    async def git_commit(self, message: str) -> str:
        return await self._post("git_commit", message=message)

    async def git_push(self, branch: str = "main") -> str:
        return await self._post("git_push", branch=branch)

    async def browser_open(self, url: str) -> str:
        return await self._post("browser_open", url=url)

    async def desktop_screenshot(self) -> str:
        return await self._post("desktop_screenshot")


def create_devbox_tools_client(base_url: str) -> GatewayHTTPClient:
    return GatewayHTTPClient(base_url)