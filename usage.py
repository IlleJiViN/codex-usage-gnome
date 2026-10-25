#!/usr/bin/env python3
"""Read Codex plan usage using the local Codex ChatGPT sign-in."""

import json
import os
import sys
import urllib.error
import urllib.request


AUTH_FILE = os.path.expanduser("~/.codex/auth.json")
USAGE_URL = "https://chatgpt.com/backend-api/wham/usage"


def read_usage():
    with open(AUTH_FILE, encoding="utf-8") as auth_file:
        auth = json.load(auth_file)
    tokens = auth.get("tokens") or {}
    access_token = tokens.get("access_token")
    account_id = tokens.get("account_id")
    if not access_token or not account_id:
        raise RuntimeError("Codex ChatGPT sign-in not found")

    request = urllib.request.Request(
        USAGE_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "ChatGPT-Account-Id": account_id,
            "Accept": "application/json",
            "User-Agent": "Codex-GNOME-Usage/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.load(response)

    rate_limit = payload.get("rate_limit") or {}
    primary = rate_limit.get("primary_window") or {}
    secondary = rate_limit.get("secondary_window") or {}
    if "used_percent" not in primary or "used_percent" not in secondary:
        raise RuntimeError("Codex usage data is incomplete")

    primary_used = max(0, min(100, round(primary["used_percent"])))
    weekly_used = max(0, min(100, round(secondary["used_percent"])))
    return {
        "ok": True,
        "plan": str(payload.get("plan_type", "Codex")).capitalize(),
        "primary": primary_used,
        "weekly": weekly_used,
        "primary_remaining": 100 - primary_used,
        "weekly_remaining": 100 - weekly_used,
    }


try:
    print(json.dumps(read_usage()))
except (OSError, ValueError, KeyError, RuntimeError, urllib.error.URLError) as error:
    # Never emit credentials or response bodies to the GNOME Shell log.
    print(json.dumps({"ok": False, "error": str(error)}))
    sys.exit(1)
