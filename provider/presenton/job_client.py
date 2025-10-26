from __future__ import annotations
from typing import Mapping
from ..core.transport.http_client import HttpClient

async def create_job(client: HttpClient, body: Mapping):
    return await client.post_json("/v1/jobs", json=body)
