"""LLM-powered vision module for candlestick chart interpretation."""

from __future__ import annotations

import httpx


async def describe_chart(image_bytes: bytes, model_endpoint: str, api_key: str) -> str:
    """Send chart image to an LLM vision model and return description."""
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"file": ("chart.png", image_bytes, "image/png")}
    async with httpx.AsyncClient() as client:
        resp = await client.post(model_endpoint, headers=headers, files=files, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    return data.get("description", "")
