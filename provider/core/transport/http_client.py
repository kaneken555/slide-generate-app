from __future__ import annotations
import httpx, anyio
from dataclasses import dataclass
from typing import Mapping, Optional
from ..error_map.mapper import to_common
from ..error_map.taxonomy import ProviderError

@dataclass
class TransportConfig:
    base_url: str
    timeout_ms: int = 60000
    headers: Optional[Mapping[str,str]] = None

class HttpClient:
    def __init__(self, provider:str, cfg:TransportConfig):
        self._p = provider
        self._cfg = cfg
        self._client = httpx.AsyncClient(base_url=cfg.base_url, timeout=cfg.timeout_ms/1000)

    async def post_json(self, path:str, json:Mapping, headers:Mapping[str,str]|None=None):
        try:
            r = await self._client.post(path, json=json, headers={**(self._cfg.headers or {}), **(headers or {})})
            if r.status_code >= 400:
                raise to_common(self._p, r.status_code, r.text)
            return r.json()
        except httpx.TimeoutException as e:
            raise to_common(self._p, None, "timeout")
        except httpx.HTTPError as e:
            raise to_common(self._p, None, str(e))

    async def get_json(self, path:str, headers:Mapping[str,str]|None=None):
        try:
            r = await self._client.get(path, headers={**(self._cfg.headers or {}), **(headers or {})})
            if r.status_code >= 400:
                raise to_common(self._p, r.status_code, r.text)
            return r.json()
        except httpx.TimeoutException:
            raise to_common(self._p, None, "timeout")
        except httpx.HTTPError as e:
            raise to_common(self._p, None, str(e))

    async def aclose(self):
        await self._client.aclose()
