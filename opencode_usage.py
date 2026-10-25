#!/usr/bin/env python3
"""Show context use for OpenCode's favorited models."""

import json
import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote


STATE_FILE = Path(os.environ.get("XDG_STATE_HOME", "~/.local/state")).expanduser() / "opencode/model.json"
MODEL_CACHE = Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser() / "opencode/models.json"
DATABASE = Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser() / "opencode/opencode.db"


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def latest_model_usage(favorite_ids):
    usage = {}
    if not DATABASE.exists() or not favorite_ids:
        return usage

    uri = f"file:{quote(str(DATABASE))}?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=2) as db:
        for (raw_data,) in db.execute("SELECT data FROM message ORDER BY time_created DESC LIMIT 5000"):
            try:
                message = json.loads(raw_data)
                model_key = f"{message.get('providerID')}/{message.get('modelID')}"
                if model_key not in favorite_ids or model_key in usage or message.get("role") != "assistant":
                    continue
                tokens = message.get("tokens") or {}
                # OpenCode's total represents the context consumed by this response.
                consumed = tokens.get("total")
                if consumed is None:
                    consumed = sum(tokens.get(key, 0) or 0 for key in ("input", "output", "reasoning"))
                usage[model_key] = max(0, int(consumed))
            except (ValueError, TypeError):
                continue
    return usage


def read_favorites():
    state = read_json(STATE_FILE)
    catalog = read_json(MODEL_CACHE)
    favorites = state.get("favorite") or []
    favorite_ids = {
        f"{item.get('providerID')}/{item.get('modelID')}"
        for item in favorites
        if item.get("providerID") and item.get("modelID")
    }
    usage_by_model = latest_model_usage(favorite_ids)

    result = []
    for item in favorites:
        provider_id = item.get("providerID")
        model_id = item.get("modelID")
        if not provider_id or not model_id:
            continue

        model_key = f"{provider_id}/{model_id}"
        model_info = (catalog.get(provider_id, {}).get("models") or {}).get(model_id, {})
        context_limit = (model_info.get("limit") or {}).get("context")
        consumed = usage_by_model.get(model_key)
        percent = None
        bar = "░" * 10
        if consumed is not None and context_limit:
            percent = min(100, round(consumed * 100 / context_limit))
            filled = min(10, round(percent / 10))
            bar = "█" * filled + "░" * (10 - filled)

        result.append({
            "id": model_key,
            "name": model_info.get("name") or model_id,
            "percent": percent,
            "bar": bar,
            "used_tokens": consumed,
            "context_limit": context_limit,
        })
    return {"ok": True, "favorites": result}


try:
    print(json.dumps(read_favorites()))
except (OSError, ValueError, TypeError, sqlite3.Error) as error:
    # Do not expose database contents or credentials in GNOME Shell logs.
    print(json.dumps({"ok": False, "error": str(error)}))
    sys.exit(1)
