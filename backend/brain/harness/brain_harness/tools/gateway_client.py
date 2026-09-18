from __future__ import annotations

import os
from typing import Any, Optional

import httpx

# Endpoint contract.
#
# The gateway exposes a single HTTP server with one endpoint per devbox tool.
# Each endpoint accepts JSON POST bodies and returns JSON. The response body is a
# dict that maps an "output" or "content" field to the string result; a string
# value in an "error" field (or a non-2xx status) indicates a tool failure.
#
#   POST {base_url}/exec                 body: {"command", "cwd", "timeout"}
#   POST {base_url}/read_file            body: {"path"}
#   POST {base_url}/write_file           body: {"path", "content"}
#   POST {base_url}/list_dir             body: {"path"}
#   POST {base_url}/git_commit           body: {"message"}
#   POST {base_url}/git_push             body: {"branch"}
#   POST {base_url}/browser_open         body: {"url"}
#   POST {base_url}/desktop_screenshot   body: {}
#
#   response: {"output": "..."} | {"content": "..."} | {"error": "..."}
#


class GatewayHTTPClient:
    """HTTP client used to reach a devbox tools gateway.

    A single ``httpx.AsyncClient`` is reused for all calls on the instance.
    Call ``await client.aclose()`` (or use the async context manager) when done.
    """

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "GatewayHTTPClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.aclose()

    async def _post(self, endpoint: str, **payload: Any) -> str:
        response = await self._client.post(f"{self.base_url}/{endpoint}", json=payload)
        return await _parse(response)

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


async def _parse(response: httpx.Response) -> str:
    if response.status_code >= 400:
        try:
            data = response.json()
        except Exception:
            data = {}
        return str(data.get("error") or f"gateway error: HTTP {response.status_code}")
    try:
        data = response.json()
    except Exception:
        return response.text or ""
    if not isinstance(data, dict):
        return str(data)
    if data.get("error"):
        return str(data["error"])
    return str(data.get("output") or data.get("content") or "")


def create_devbox_tools_client(base_url: Optional[str] = None, timeout: float = 60.0) -> GatewayHTTPClient:
    url = base_url or os.environ.get("HARNESS_GATEWAY_URL")
    if not url:
        raise ValueError("a gateway base_url is required (or set HARNESS_GATEWAY_URL)")
    return GatewayHTTPClient(url, timeout=timeout)