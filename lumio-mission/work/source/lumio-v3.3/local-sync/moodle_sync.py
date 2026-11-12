#!/usr/bin/env python3
"""Lumio × Moodle — סנכרון מקומי (לוח משימות + ציונים). סטנדרטלייב בלבד, בלי תלויות.

מיועד למערכות Moodle (למשל פטל של מכון ויצמן, או Moodle בית-ספרי שלכם).

שני מסלולים:
  1. משימות: השירות הפנימי של Moodle (core_calendar_get_action_events_by_timesort
     דרך /lib/ajax/service.php) — מחזיר JSON נקי של המשימות הפתוחות עם מועדי הגשה.
  2. ציונים: קריאת דף הדיווח /grade/report/overview/index.php וניתוח טבלת הציונים
     (ניתוח חישובי (heuristic) — דפי Moodle משתנים, לכן קיים --dry-run).

אבטחה:
  • שם המשתמש והסיסמה נכנסים במחשב שלך בלבד (או עוקמת סשן קיימת עם --sesskey).
    הם מעולם לא נשמרים בלומיו — רק הנתונים נשלחים.
  • אופצייה ללא סיסמה: אם אתה כבר מחובר בדפדפן, אפשר להעתיק את cookie הסשן
    (--cookie) ואת ה־sesskey (--sesskey) ולהימנע מהזנת סיסמה בכלל.

ריצות:
  python moodle_sync.py --base https://school.moodle.example --username user1 --password ...
  python moodle_sync.py --base ... --sesskey ABC123 --cookie "MoodleSession=..."
  python moodle_sync.py --base ... --username ... --password ... --dry-run
  python moodle_sync.py --base ... --username ... --password ... --loop 4 --save-key

הערה כנה: מסלול ה־AJAX תלוי בגרסה/הגדרות של Moodle האורגניזציה. אם הראשונה
נכשלת, רץ עם --dry-run, תעד את הפלט ושלח אותו — יותאם הניתוח. המסלול המוכח
תמיד: קישור ICS אישי של היומן (נתמך בלומיו ישירות כפיד).
"""
import argparse
import datetime
import hashlib
import html as _html
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lumio_push  # noqa: E402


def make_opener(cookie_header=None):
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [("User-Agent", "Mozilla/5.0 (Lumio local sync)")]
    if cookie_header:
        op.addheaders.append(("Cookie", cookie_header))
    return op, jar


def login(op, base, username, password):
    """Standard Moodle login (login/index.php). Returns True only on success."""
    data = urllib.parse.urlencode({"username": username, "password": password,
                                   "submitlogin": "Login"}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/login/index.php", data=data, method="POST")
    try:
        with op.open(req, timeout=20) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if e.code != 200:
            return False
    except Exception:
        return False
    return not re.search(r'id="error"|Login failed|ההתחברות נכשלה|Invalid credentials', body, re.I)


def get(op, url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Lumio local sync)"})
    with op.open(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def extract_sesskey(page_html):
    m = re.search(r'id="id_sesskey"[^>]*value="([^"]+)"', page_html)
    return m.group(1) if m else None


def ajax_calendar(op, base, sesskey):
    """core_calendar_get_action_events_by_timesort — the documented internal AJAX.

    Tries several argument shapes because Moodle versions differ. Returns a list
    of raw event dicts (empty if nothing parsed — caller reports honestly).
    """
    url = base.rstrip("/") + "/lib/ajax/service.php"
    now_ts = int(__import__("time").time())
    variants = [
        {"name": "core_calendar_get_action_events_by_timesort",
         "arguments": {"since.timestamp": now_ts - 86400 * 14, "until.timestamp": now_ts + 86400 * 90,
                       "limit": 100, "contextid": 1, "userid": 0}},
        {"name": "core_calendar_get_action_events_by_timesort",
         "arguments": {"since.timestamp": 0, "until.timestamp": now_ts + 86400 * 365,
                       "limit": 100, "contextid": 1, "userid": 0}},
    ]
    collected = []
    for v in variants:
        body = json.dumps([[v]], ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={
            "Content-Type": "application/json",
            "X-Moodle-Session": sesskey or "",
            "X-Requested-With": "XMLHttpRequest",
        })
        try:
            with op.open(req, timeout=20) as r:
                text = r.read().decode("utf-8", "replace")
        except Exception:
            continue
        try:
            data = json.loads(text)
        except Exception:
            continue
        # Shape: [{"status": true, "data": [ {event...} ]}]
        if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("status"):
            payload = data[0].get("data")
            if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                collected = payload
                break
    return collected


def event_to_task(ev, idx):
    """Map a Moodle calendar event (task-like) to a Lumio item. Never raises."""
    title = str(ev.get("title") or ev.get("name") or "").strip()
    if not title or title.lower() in ("(empty)",):
        return None
    # Tasks in Moodle calendar: eventtype 'assignment'/'forumpost'/'workshop' etc.
    et = str(ev.get("eventtype") or "").lower()
    if et and et not in ("assignment", "forumpost", "workshopsubmissions", "quiz"):
        # keep everything but flag: announcements are events too; only task-ish go as tasks
        if not re.search(r"(הגש|משימ|תרגול|דוח|עבודה|quiz|assignment|task)", title, re.I):
            return None
    due = None
    t = ev.get("timestart")
    if isinstance(t, (int, float)) and t > 0:
        due = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    course = str(ev.get("coursemodule") or ev.get("course") or "").strip()[:100]
    # 'course' may be a numeric id — only keep when it looks like a name
    if course.isdigit():
        course = ""
    return {
        "kind": "task",
        "external_id": f"moodle:task:{hashlib.sha1(str(ev.get('id') or idx + '|' + title).encode()).hexdigest()[:24]}"[:200],
        "title": _html.unescape(title)[:240],
        "course_title": course,
        "due_at": due,
        # Calendar events do not reliably say "completed" — honest default.
        "status": "todo",
    }


def parse_grades(page_html):
    """Heuristic grade-table parse from /grade/report/overview/index.php.

    Looks for course sections (a heading link to course/view.php) followed by
    table rows whose last numeric cell is 0..100. Best-effort: Moodle markup
    varies; unparseable rows are skipped, never guessed.
    """
    items = []
    current_course = ""
    # walk the page top-down: course headers set context, <tr> rows are scanned
    tokens = re.findall(r'(?:<h[23][^>]*>.*?</h[23]>|<tr[^>]*>.*?</tr>)', page_html, re.S | re.I)
    for tok in tokens:
        if tok.lower().startswith("<h"):
            m = re.search(r'course/view\.php\?id=\d+[^>]*>([^<]+)<', tok)
            current_course = _html.unescape(m.group(1)).strip() if m else current_course
            continue
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tok, re.S | re.I)
        if len(cells) < 2:
            continue
        texts = [_html.unescape(re.sub(r'<[^>]+>', ' ', c)).strip() for c in cells]
        texts = [re.sub(r'\s+', ' ', t) for t in texts if t != '']
        if not texts:
            continue
        score_m = re.fullmatch(r'(\d{1,3}(?:[.,]\d+)?)', texts[-1])
        if not score_m:
            continue
        score = float(score_m.group(1).replace(',', '.'))
        if score > 100:
            continue
        # title = first cell that is not purely numeric
        title = next((t for t in texts[:-1] if not re.fullmatch(r'[\d.,\-\s]+', t)), current_course or "ציון")
        items.append({
            "kind": "grade",
            "external_id": f"moodle:grade:{hashlib.sha1((current_course + '|' + title + '|' + score_m.group(1)).encode()).hexdigest()[:24]}"[:200],
            "title": title[:240],
            "course_title": current_course,
            "score": score,
        })
    # de-dup (same course|title|score)
    seen = set()
    out = []
    for it in items:
        if it["external_id"] in seen:
            continue
        seen.add(it["external_id"])
        out.append(it)
    return out


def main():
    ap = argparse.ArgumentParser(description="Lumio × Moodle local sync")
    ap.add_argument("--base", required=True, help="כתובת Moodle, למשל https://school.moodle.example")
    ap.add_argument("--username", default=None)
    ap.add_argument("--password", default=None)
    ap.add_argument("--sesskey", default=None, help="sesskey קיים (חלף סיסמה; יחד עם --cookie)")
    ap.add_argument("--cookie", default=None, help="מחרוזת cookie מלאה מדפדפן מחובר")
    ap.add_argument("--source", default="petel", choices=["petel", "ofek", "mashov", "classroom"],
                    help="תיוג המקור בלומיו (ברירת מחדל: petel)")
    ap.add_argument("--sync-key", default=None)
    ap.add_argument("--save-key", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-grades", action="store_true", help="לדלג על מסלול הציונים")
    ap.add_argument("--loop", type=float, default=0)
    args = ap.parse_args()

    base = args.base.rstrip("/")
    if not base.startswith("https://"):
        base = "https://" + base

    import getpass
    if not args.cookie:
        if not args.username:
            args.username = input("שם משתמש במoodle: ").strip()
        if not args.password:
            args.password = getpass.getpass("סיסמה (לא תוצג): ").strip()
    if not (args.cookie or (args.username and args.password)):
        print("נדרשים: --username + --password, או --cookie (+ --sesskey).")
        sys.exit(1)

    op, _ = make_opener(args.cookie)
    if args.username and args.password and not args.cookie:
        ok = login(op, base, args.username, args.password)
        if not ok:
            print("✗ ההתחברות נכשלה (שם משתמש/סיסמה לא נכונים, או שהאתר חוסם).")
            sys.exit(2)
    try:
        home = get(op, base + "/my/", timeout=20)
    except Exception:
        home = get(op, base + "/", timeout=20)
    sesskey = args.sesskey or extract_sesskey(home)
    if not sesskey:
        print("✗ לא נמצא sesskey — אין סשן פעיל. נסה להיכנס בדפדפן ולהעביר --cookie (וגם --sesskey).")
        sys.exit(2)

    items = []
    events = ajax_calendar(op, base, sesskey)
    for i, ev in enumerate(events or []):
        t = event_to_task(ev, i)
        if t:
            items.append(t)
    print("נלקטו {} משימות מהלוח".format(len(items)))

    if not args.no_grades:
        try:
            grade_html = get(op, base + "/grade/report/overview/index.php", timeout=25)
            g = parse_grades(grade_html)
            items.extend(g)
            print("נלקטו {} ציונים מדף הדיווח (ניתוח חישובי)".format(len(g)))
        except Exception as e:
            print("⚠ מסלול הציונים נכשל (לא קריטי): {}".format(e))

    if args.dry_run:
        print(json.dumps(items[:25], ensure_ascii=False, indent=1))
        print("(dry-run — לא נשלח כלום)")
        return
    ok, detail = lumio_push.push(items, args.source, key=args.sync_key)
    if args.save_key and args.sync_key:
        cfg = lumio_push.load_config()
        cfg["sync_key"] = args.sync_key
        lumio_push.save_config(cfg)
        print("מפתח הסנכרון נשמר ב־~/.lumio/config.json (הרשאות 600).")
    print(("✓ " if ok else "✗ ") + detail)
    if not ok:
        sys.exit(2)


if __name__ == "__main__":
    import time as _time
    _main = main
    def _looped():
        a = sys.argv
        ap = [x for x in a[1:]]
        m = re.search(r"--loop (\d+(?:\.\d+)?)", " ".join(ap))
        if m:
            hours = float(m.group(1))
            while True:
                try:
                    _main()
                except SystemExit as e:
                    if e.code not in (0, None):
                        print("✗ ריצה נכשלה, ננסה שוב בעוד {:.1f} שעות".format(hours))
                _time.sleep(hours * 3600)
    if any(re.match(r"--loop", x) for x in sys.argv[1:]):
        _looped()
    else:
        _main()
