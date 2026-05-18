"""
hsl.py – Stop-based departure boards from HSL.

Uses Digitransit Routing API v2 (GraphQL) – per-stop departure times.
API key from: https://portal-api.digitransit.fi/

Config:
  hsl:
    api_key: "your-subscription-key"
    boards:
      - name: "549 → Tapiola"
        stop_id: "HSL:2161207"     # Oravamäki E1605
        route_filter: "549"        # optional, only this route
        headsign_filter: "Tapiola" # optional, substring match on headsign
        max_departures: 2          # optional, default 3
      - name: "Kauniainen → Helsinki"
        stop_id: "HSL:3010551"     # Ka0151 (Helsinki-suunta)
        max_departures: 3
"""

import json
from datetime import datetime
from pathlib import Path

import requests

CACHE_FILE      = Path("cache/hsl.json")
DEFAULT_TTL_MIN = 10
API_URL         = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"

STOP_QUERY = """
query StopDepartures($id: String!, $n: Int!) {
  stop(id: $id) {
    name
    code
    stoptimesWithoutPatterns(numberOfDepartures: $n, omitCanceled: true) {
      realtimeDeparture
      scheduledDeparture
      serviceDay
      realtime
      headsign
      trip {
        route { shortName mode }
        directionId
      }
    }
  }
}
"""


class DataFetchError(Exception):
    pass


def _cache_is_fresh(ttl_minutes: int) -> bool:
    if not CACHE_FILE.exists():
        return False
    age = datetime.now().timestamp() - CACHE_FILE.stat().st_mtime
    return age < ttl_minutes * 60


def _load_cache() -> dict | None:
    try:
        return json.loads(CACHE_FILE.read_text())
    except Exception:
        return None


def _save_cache(data: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _within_active_hours(active_hours: list) -> bool:
    if not active_hours or len(active_hours) < 2:
        return True
    hour = datetime.now().hour
    return active_hours[0] <= hour <= active_hours[1]


def drop_past_departures(hsl: dict | None) -> dict | None:
    """Returns hsl with departures whose recomputed minutes_until <= 0 dropped.
    Used by --partial-only to keep the HSL cell fresh between API fetches."""
    if not hsl or not hsl.get("connections"):
        return hsl
    try:
        fetched_at = datetime.fromisoformat(hsl["fetched_at"])
    except (KeyError, ValueError):
        return hsl
    elapsed_min = (datetime.now() - fetched_at).total_seconds() / 60
    updated = []
    for c in hsl["connections"]:
        cur = c.get("minutes_until", 0) - elapsed_min
        if cur > 0:
            updated.append({**c, "minutes_until": int(cur)})
    return {**hsl, "connections": updated}


def _query_stop(api_key: str, stop_id: str, n: int) -> dict:
    headers = {
        "Content-Type":                 "application/json",
        "digitransit-subscription-key": api_key,
    }
    payload = {
        "query": STOP_QUERY,
        "variables": {"id": stop_id, "n": n},
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    raw = resp.json()
    errors = raw.get("errors")
    if errors:
        raise DataFetchError(
            f"HSL GraphQL error for stop {stop_id}: {errors[0].get('message', errors)}"
        )
    return raw.get("data", {}).get("stop") or {}


def _format_departures(board_cfg: dict, stop_data: dict, now_ts: float) -> list[dict]:
    route_filter    = (board_cfg.get("route_filter")    or "").strip()
    headsign_filter = (board_cfg.get("headsign_filter") or "").strip().lower()
    label           = board_cfg.get("name", stop_data.get("name", ""))
    max_dep         = int(board_cfg.get("max_departures", 3))

    stoptimes = stop_data.get("stoptimesWithoutPatterns") or []
    out = []

    for st in stoptimes:
        route_short = (st.get("trip") or {}).get("route", {}).get("shortName", "")
        headsign    = st.get("headsign") or ""

        if route_filter and route_short != route_filter:
            continue
        if headsign_filter and headsign_filter not in headsign.lower():
            continue

        service_day = st.get("serviceDay") or 0
        dep_secs    = st.get("realtimeDeparture")
        if dep_secs is None:
            dep_secs = st.get("scheduledDeparture")
        if dep_secs is None:
            continue

        dep_ts = float(service_day) + float(dep_secs)
        minutes_until = int((dep_ts - now_ts) / 60)
        if minutes_until < 0:
            continue

        depart_str = datetime.fromtimestamp(dep_ts).strftime("%H:%M")
        mode = (st.get("trip") or {}).get("route", {}).get("mode", "")

        out.append({
            "departure":     depart_str,
            "arrival":       "",
            "minutes_until": minutes_until,
            "lines":         label,
            "to":            label,
            "walk_minutes":  0,
            "first_mode":    mode,
            "first_stop":    stop_data.get("name", ""),
            "first_depart":  depart_str,
            "realtime":      bool(st.get("realtime")),
        })

        if len(out) >= max_dep:
            break

    return out


def fetch(config: dict, use_cache: bool = True) -> dict:
    cache_cfg    = config.get("cache", {})
    ttl          = cache_cfg.get("hsl_ttl_minutes", DEFAULT_TTL_MIN)
    active_hours = cache_cfg.get("hsl_active_hours", [])

    if use_cache and _cache_is_fresh(ttl):
        return _load_cache()

    if not _within_active_hours(active_hours):
        cached = _load_cache()
        if cached:
            cached["_stale"] = True
            return cached
        return {"connections": [], "to_name": "", "fetched_at": datetime.now().isoformat(timespec="seconds")}

    hsl_cfg = config.get("hsl", {})
    api_key = hsl_cfg.get("api_key", "")
    boards  = hsl_cfg.get("boards") or []

    if not api_key:
        raise DataFetchError(
            "HSL API key missing. Register at https://portal-api.digitransit.fi/ and add hsl.api_key to config."
        )
    if not boards:
        raise DataFetchError(
            "hsl.boards is empty — add at least one board with stop_id."
        )

    now_ts = datetime.now().timestamp()
    connections: list[dict] = []

    try:
        for board in boards:
            stop_id = board.get("stop_id")
            if not stop_id:
                continue
            n = int(board.get("max_departures", 3)) + 5  # over-fetch for filters
            stop_data = _query_stop(api_key, stop_id, n)
            connections.extend(_format_departures(board, stop_data, now_ts))
    except requests.RequestException as e:
        cached = _load_cache()
        if cached:
            cached["_stale"] = True
            return cached
        raise DataFetchError(f"HSL fetch failed: {e}") from e

    data = {
        "connections": connections,
        "to_name":     "",
        "fetched_at":  datetime.now().isoformat(timespec="seconds"),
    }
    _save_cache(data)
    return data
