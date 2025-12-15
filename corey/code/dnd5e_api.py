from __future__ import annotations

import random
import time
from typing import Dict, List, Optional

import requests

API_ROOT_2014 = "https://www.dnd5eapi.co/api/2014"
TRANSIENT_HTTP = {429, 500, 502, 503, 504, 520, 521, 522, 523, 524}


def get_json_with_retries(
    session: requests.Session,
    url: str,
    timeout: int = 30,
    max_retries: int = 8,
    base_sleep: float = 1.0,
) -> Dict:
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            r = session.get(url, timeout=timeout)
            if r.status_code in TRANSIENT_HTTP:
                raise requests.HTTPError(f"Transient HTTP {r.status_code}")
            r.raise_for_status()
            return r.json()
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError, ValueError) as e:
            last_exc = e
            sleep_s = min(base_sleep * (2 ** (attempt - 1)), 60.0) + random.uniform(0, 0.5)
            print(f"[retry {attempt}/{max_retries}] {e} -> sleeping {sleep_s:.2f}s")
            time.sleep(sleep_s)

    raise last_exc if last_exc else RuntimeError("Unknown error")


def list_spells(session: requests.Session) -> List[Dict]:
    """Returns list of {'index','name','url'}."""
    url = f"{API_ROOT_2014}/spells"
    data = get_json_with_retries(session, url)
    return data.get("results", [])


def fetch_spell_detail_trimmed(session: requests.Session, spell_url: str) -> Dict:
    """
    Fetch spell detail and return ONLY:
      - name
      - school_name
      - level
    """
    if not spell_url.startswith("http"):
        spell_url = "https://www.dnd5eapi.co" + spell_url

    detail = get_json_with_retries(session, spell_url)

    school = detail.get("school")
    school_name = None
    if isinstance(school, dict):
        school_name = school.get("name")

    return {
        "api_index": detail.get("index"),
        "name": detail.get("name"),
        "level": detail.get("level"),
        "school_name": school_name,
    }
