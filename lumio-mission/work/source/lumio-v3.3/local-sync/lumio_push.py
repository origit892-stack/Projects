#!/usr/bin/env python3
"""Lumio local sync — shared push module (stdlib only).

Pushes items to the Lumio apps-script-ingest edge function using the
student's sync key. No credentials are stored here: the sync key is a
per-user capability token created in Lumio (it is NOT a password).

Config resolution order (first found wins):
  CLI arg  >  env var  >  ~/.lumio/config.json  >  built-in default
The built-in ingest URL and anon key are the public ones shipped with the
Lumio app (same as config.mjs in the repo) — not secrets.
"""
import json
import os
import urllib.error
import urllib.request

DEFAULT_INGEST = "https://zijinurzzwkuqxwhkiuw.supabase.co/functions/v1/apps-script-ingest"
# Public anon key of the Lumio Supabase project (publishable, as in the app's config.mjs).
DEFAULT_ANON = "sb_publishable_YiFwqA7lOmOh1g9adNvo7Q_7QmY0rjs"
CONFIG_DIR = os.path.expanduser("~/.lumio")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    """Persist {sync_key, ingest_url?} on the student's own machine (0600)."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except Exception:
        pass


def resolve(key=None, url=None, anon=None):
    cfg = load_config()
    k = (key or os.environ.get("LUMIO_SYNC_KEY") or cfg.get("sync_key") or "").strip()
    u = (url or os.environ.get("LUMIO_INGEST_URL") or cfg.get("ingest_url") or DEFAULT_INGEST).strip()
    a = (anon or os.environ.get("LUMIO_ANON_KEY") or cfg.get("anon_key") or DEFAULT_ANON).strip()
    return k, u, a


def push(items, source, key=None, url=None, anon=None, timeout=30):
    """Push items to Lumio.

    item shape: {kind: 'task'|'grade', external_id: str, title: str,
                 course_title?: str, due_at?: ISO str | None,
                 score?: 0..100 (grades), status?: 'todo'|'done'}
    Returns (ok: bool, detail: str in Hebrew). Never raises.
    """
    items = [i for i in (items or []) if isinstance(i, dict)]
    if not items:
        return True, "אין פריטים לשליחה"
    k, u, a = resolve(key, url, anon)
    if not k:
        return False, ("חסר מפתח סנכרון. הוסף את המפתח בלחץ --sync-key (הועתק מלומיו) או רץ פעם אחת עם --save-key כדי שיושמר ב־~/.lumio/config.json.")
    body = json.dumps({"key": k, "source": source, "items": items[:500]}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        u, data=body, method="POST",
        headers={"Content-Type": "application/json", "apikey": a, "Authorization": "Bearer " + a},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", "replace") or "{}")
        if data.get("ok"):
            saved = data.get("saved", {})
            return True, "נשמר בלומיו: {} משימות, {} ציונים{}".format(
                saved.get("tasks", 0), saved.get("grades", 0),
                " (חלק מהרשימה בגלל מגבלת גודל)" if data.get("partial") else "")
        return False, "השרת דחה את השליחה: {}".format(data.get("error", "?"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = json.loads(e.read().decode("utf-8", "replace") or "{}").get("error", "")
        except Exception:
            pass
        if e.code == 401:
            return False, "מפתח הסנכרון לא מוכר — וודא שיוצר בלומיו (כרטיס המערכת → מפתח סנכרון) ושלא סובב מאז. ({})".format(detail or "401")
        if e.code == 413:
            return False, "גודל הגוף עבר את מגבלת השרת (413)."
        return False, "שגיאת שרת {} {}".format(e.code, detail)
    except Exception as e:
        return False, "שגיאת רשת (השרת לא ענה): {}".format(e)
