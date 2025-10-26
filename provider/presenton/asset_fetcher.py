from __future__ import annotations
from ..core.transport.http_client import HttpClient

async def fetch_artifact(client: HttpClient, job: dict):
    # job["result"] に artifact_url 等が入っている想定
    return {
        "artifact_url": job.get("result",{}).get("artifact_url"),
        "slides": job.get("result",{}).get("slides",[])
    }
