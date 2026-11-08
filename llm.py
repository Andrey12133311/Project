from __future__ import annotations
import json
import os
from typing import Any, Dict, Optional
import httpx

class LLMClient:
    """OpenAI-compatible adapter with no vendor lock-in."""

    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "")

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.model)

    def json_completion(self, system: str, user: str, timeout: float = 60.0) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        with httpx.Client(timeout=timeout) as client:
            r = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
        return json.loads(content)
