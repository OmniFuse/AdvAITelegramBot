import asyncio
from typing import Optional, Dict
import requests
from config import BOT_API_TOKEN, SITE_API_URL

HEADERS = {"Authorization": f"Bearer {BOT_API_TOKEN}"}

async def _async_request(method: str, endpoint: str, json: Optional[Dict] = None) -> Optional[Dict]:
    url = f"{SITE_API_URL}{endpoint}"
    def _send():
        try:
            if method == "GET":
                r = requests.get(url, headers=HEADERS, timeout=10)
            else:
                r = requests.post(url, headers=HEADERS, json=json, timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"Site API request error: {e}")
        return None
    return await asyncio.to_thread(_send)

async def fetch_user(telegram_id: str) -> Optional[Dict]:
    return await _async_request("GET", f"/api/v1/bot/users/{telegram_id}")

async def update_balance(telegram_id: str, amount: float, typ: str = "credit", description: str = "") -> Optional[Dict]:
    data = {"amount": amount, "type": typ, "description": description}
    return await _async_request("POST", f"/api/v1/bot/users/{telegram_id}/balance", data)

async def link_account(user_id: int, telegram_id: str) -> bool:
    data = {"user_id": user_id, "telegram_id": telegram_id}
    resp = await _async_request("POST", "/api/v1/bot/link", data)
    return bool(resp and resp.get("success"))
