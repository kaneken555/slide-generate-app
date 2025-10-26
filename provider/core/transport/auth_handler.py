from __future__ import annotations
import os
def bearer_header(env_key:str) -> dict[str,str]:
    token = os.getenv(env_key, "")
    return {"Authorization": f"Bearer {token}"} if token else {}
