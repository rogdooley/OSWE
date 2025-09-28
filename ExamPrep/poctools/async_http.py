import asyncio
from typing import Optional, Dict, Any
import httpx


class AsyncRequester:
    """Async HTTP client wrapper around httpx.AsyncClient with simple retries and proxy support."""

    def __init__(
        self,
        proxies: Optional[Dict[str, str]] = None,
        timeout: float = 10.0,
        max_retries: int = 2,
    ):
        self._proxies = proxies
        self._timeout = timeout
        self._max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(proxies=self._proxies, timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        assert self._client is not None, (
            "Use AsyncRequester as an async context manager"
        )
        attempts = 0
        last_exc: Optional[BaseException] = None
        while attempts <= self._max_retries:
            try:
                return await self._client.request(method, url, **kwargs)
            except Exception as e:
                last_exc = e
                attempts += 1
                await asyncio.sleep(0.2 * attempts)
        raise last_exc  # type: ignore[misc]

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("POST", url, **kwargs)
