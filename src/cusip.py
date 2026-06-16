"""
CUISP to ticker via OpenFIGI API
"""
import json 
import time 
import requests

from pathlib import Path
from config import (
    OPENFIGI_API_KEY,
    OPENFIGI_URL,
    OPENFIGI_BATCH_SIZE,
    OPENFIGI_RATE_LIMIT_S,
    CUSIP_CACHE_PATH,
)    

# NOTE: These are the preferred US equity exchange codes (in order) 
_US_EXCHANGES = {"US", "UN", "UA", "UW"}

def _load_cache() -> dict[str, str]:
    if CUSIP_CACHE_PATH.exists():
        return json.loads(CUSIP_CACHE_PATH.read_text())
    return {}


def _save_cache(cache: dict[str, str]) -> None:
    CUSIP_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CUSIP_CACHE_PATH.write_text(json.dumps(cache, indent=2))

def resolve_cusips(cusips: list[str]) -> dict[str, str]:
    # Returns {cusip: ticker} for every CUSIP in the input list
    # NOTE: For unknown CUSIPs, they are resolved via OpenFIGI and added to the local cache
    cache = _load_cache()
    unknown = [c for c in cusips if c not in cache]

    if not unknown:
        return {c: cache.get(c, "") for c in cusips}

    headers = {"Content-Type": "application/json"}
    if OPENFIGI_API_KEY:
        headers["X-OPENFIGI-APIKEY"] = OPENFIGI_API_KEY

    for i in range(0, len(unknown), OPENFIGI_BATCH_SIZE):
        batch = unknown[i : i + OPENFIGI_BATCH_SIZE]
        payload = [{"idType": "ID_CUSIP", "idValue": c} for c in batch]

        resp = requests.post(OPENFIGI_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()

        for cusip, result in zip(batch, resp.json()):
            ticker = ""
            if "data" in result and result["data"]:
                for item in result["data"]:
                    if item.get("exchCode") in _US_EXCHANGES:
                        ticker = item.get("ticker", "")
                        break
                else:
                    ticker = result["data"][0].get("ticker", "")
            cache[cusip] = ticker

        time.sleep(OPENFIGI_RATE_LIMIT_S)

    _save_cache(cache)
    return {c: cache.get(c, "") for c in cusips}
    