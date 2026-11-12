#!/usr/bin/env python3
"""Lumio × משו״ב — סנכרון מקומי (משימות + ציונים).

עובד עם ספריית pymashov הפתוחה (https://github.com/t0mer/pymashov) —
הספריה דוברת את אותו API פנימי שאתר משו״ב משתמש בו.

אבטחה:
  • הסיסמה והתעודה נכנסים במחשב שלך בלבד (ארגומנט, משתנה סביבה, או שאלה).
    הם נשמעים לעולם לא בלומיו ולא בסקריפט — רק הנתונים נשלחים.
  • מפתח הסנכרון (sync key) הוא קוד כניסה אחד־פעמי למערכת שלך בלומיו;
    אפשר לסובב/למחוק אותו בכל עת מהכרטיס.

התקנה:
  pip install pymashov

ריצות:
  python mashov_sync.py --username 123456789 --semel 123456 --student-id 987654321
  python mashov_sync.py --username ... --semel ... --student-id ... --save-key
  python mashov_sync.py --username ... --semel ... --student-id ... --dry-run
  python mashov_sync.py --username ... --semel ... --student-id ... --loop 4

--loop N: רץ כל N שעות ללא הפסקה (סגור עם Ctrl+C). בשילוב משימה מתוכננת
(Windows Task Scheduler / macOS launchd) זה נותן סנכרון אוטומטי יומי.

הערות כנות:
  • ספריית pymashov אי־רשמית — משו״ב יכול לשנות את ה־API בכל רגע; אם ריצה
    נכשלת עם שגיאת JSON/404, כנראה שהם שינו משהו. עדכן: pip install -U pymashov
  • תאימות: ספרייה בלי 2FA (הזדהות סיסמה בלבד).
  • אם לא יודע את מספר התלמיד: פתח את משו״ב בדפדפן, היכנס, בחר את התלמיד —
    המספר מופיע בכתובת/בנתוני הפרופיל. אפשר לנסות --discover.
"""
import argparse
import asyncio
import getpass
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lumio_push  # noqa: E402

YEAR_DEFAULT = "2026"


def parse_due(raw):
    """Extract a date from any Mashov due-date format → 'YYYY-MM-DDT00:00:00Z'.

    Date-only midnight-UTC matches the app convention (same as the Classroom
    DST-safe writer). Unparseable → None (the row is kept, due stays unknown).
    """
    if not raw:
        return None
    s = str(raw).strip()
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if not m:
        m = re.search(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", s)
        if not m:
            return None
        day, month, year = m.groups()
        return "{}-{:0>2}-{:0>2}T00:00:00Z".format(year, month, day)
    year, month, day = m.groups()
    return "{}-{:0>2}-{:0>2}T00:00:00Z".format(year, month, day)


def stable_id(*parts):
    return hashlib.sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:24]


def to_items(homework, grades):
    items = []
    for i, a in enumerate(homework or []):
        if not isinstance(a, dict):
            continue
        subj = str(a.get("subject") or a.get("course") or a.get("courseTitle") or "").strip()[:100]
        title = str(a.get("description") or a.get("title") or a.get("name") or "").strip()
        if not title:
            title = subj or "משימה"
        title = title[:240]
        aid = str(a.get("id") or a.get("assignmentId") or a.get("homeworkId")
                  or a.get("task_id") or a.get("taskId") or "").strip()
        ext = f"mashov:hw:{stable_id(aid or i, title[:60])}"
        items.append({
            "kind": "task",
            "external_id": ext[:200],
            "title": title,
            "course_title": subj,
            "due_at": parse_due(a.get("dueDate") or a.get("due_date") or a.get("deadline")),
            "status": "done" if str(a.get("status") or "").lower() in ("done", "completed", "submitted", "1") else "todo",
        })
    for i, g in enumerate(grades or []):
        if not isinstance(g, dict):
            continue
        subj = str(g.get("subject") or g.get("course") or g.get("courseTitle") or "").strip()[:100]
        raw = g.get("grade") if g.get("grade") is not None else g.get("score")
        try:
            score = float(raw)
        except (TypeError, ValueError):
            continue
        if score < 0 or score > 100:
            continue
        desc = str(g.get("description") or g.get("title") or g.get("assignment") or "").strip()[:120]
        items.append({
            "kind": "grade",
            "external_id": f"mashov:grade:{stable_id(subj, score, desc or i)}"[:200],
            "title": (desc or subj or "ציון")[:240],
            "course_title": subj,
            "score": score,
        })
    return items


async def fetch_all(client, student_id):
    hw = await client.get_homework(student_id)
    gr = await client.get_grades(student_id)
    return (hw if isinstance(hw, list) else hw.get("items") if isinstance(hw, dict) else []), \
           (gr if isinstance(gr, list) else gr.get("items") if isinstance(gr, dict) else [])


async def discover_student(client):
    """Best-effort: try to find the student id from the session itself."""
    for path in ("/api/students", "/api/me/students", "/api/user/students"):
        try:
            resp = await client.request("GET", path)
            data = resp.json()
        except Exception:
            continue
        cands = []
        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if re.fullmatch(r"\d{6,12}", str(v)) and re.search(r"(id|student|user)", k, re.I):
                        cands.append(str(v))
                    walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(data)
        if cands:
            return sorted(set(cands))
    return []


def main():
    ap = argparse.ArgumentParser(description="Lumio × Mashov local sync")
    ap.add_argument("--username", default=os.environ.get("MASHOV_USERNAME"), help="מספר תעודת זהות (שם משתמש במשו״ב)")
    ap.add_argument("--password", default=os.environ.get("MASHOV_PASSWORD"), help="סיסמת משו״ב (מומלץ: להשאיר ריק ולהזין בעצמך)")
    ap.add_argument("--semel", default=os.environ.get("MASHOV_SEMEL"), help="סמל מוסד")
    ap.add_argument("--year", default=YEAR_DEFAULT, help=f"שנת לימודים (ברירת מחדל {YEAR_DEFAULT})")
    ap.add_argument("--student-id", default=None, help="מספר התלמיד (ללא זה — נסה --discover)")
    ap.add_argument("--discover", action="store_true", help="נסה למצוא את מספרי התלמידים מההתחברות")
    ap.add_argument("--sync-key", default=None, help="מפתח סנכרון מלומיו (או LUMIO_SYNC_KEY / ~/.lumio/config.json)")
    ap.add_argument("--save-key", action="store_true", help="שמור את מפתח הסנכרון ב־~/.lumio/config.json (רק במחשב שלך)")
    ap.add_argument("--dry-run", action="store_true", help="הצג את הנתונים ללא שליחה")
    ap.add_argument("--loop", type=float, default=0, help="סנכרון חוזר כל N שעות (0 = ריצה בודדת)")
    args = ap.parse_args()

    try:
        from mashov import MashovClient
    except ImportError:
        print("חסרה ספריית pymashov. התקן עם:  pip install pymashov")
        sys.exit(1)

    username = args.username or input("מספר תעודת זהות (שם משתמש במשו״ב): ").strip()
    password = args.password or getpass.getpass("סיסמת משו״ב (לא תוצג): ").strip()
    semel = args.semel or input("סמל מוסד: ").strip()
    if not (username and password and semel):
        print("חסרים פרטי התחברות.")
        sys.exit(1)

    async def run_once():
        async with MashovClient(username=username, password=password, semel=semel, year=args.year) as client:
            sid = args.student_id
            if not sid and args.discover:
                found = await discover_student(client)
                if found:
                    print("נמצאו מספרי תלמיד אפשריים:", ", ".join(found))
                    if len(found) == 1:
                        sid = found[0]
                    else:
                        print("בחר אחד עם --student-id (או הקלד עכשיו): ")
                        sid = input().strip()
                else:
                    print("לא נמצאו מספרי תלמיד — ציין --student-id.")
                    sys.exit(1)
            if not sid:
                print("חסר --student-id (או --discover).")
                sys.exit(1)
            hw, gr = await fetch_all(client, sid)
            items = to_items(hw, gr)
            print("נלקטו {} פריטים ({} משימות, {} ציונים)".format(
                len(items), sum(1 for i in items if i["kind"] == "task"),
                sum(1 for i in items if i["kind"] == "grade")))
            if args.dry_run:
                import json as _json
                print(_json.dumps(items[:20], ensure_ascii=False, indent=1))
                print("(dry-run — לא נשלח כלום)")
                return
            ok, detail = lumio_push.push(items, "mashov", key=args.sync_key)
            if args.save_key and args.sync_key:
                cfg = lumio_push.load_config()
                cfg["sync_key"] = args.sync_key
                lumio_push.save_config(cfg)
                print("מפתח הסנכרון נשמר ב־~/.lumio/config.json (הרשאות 600).")
            print(("✓ " if ok else "✗ ") + detail)
            sys.exit(0 if ok else 2)

    if args.loop and args.loop > 0:
        import time
        print("מצב לולאה: סנכרון כל {:.1f} שעות (Ctrl+C לעצירה)".format(args.loop))
        while True:
            try:
                asyncio.run(run_once())
            except SystemExit:
                pass  # keep looping; next cycle re-logs in
            except Exception as e:
                print("✗ שגיאה: {}".format(e))
            time.sleep(args.loop * 3600)
    else:
        asyncio.run(run_once())


if __name__ == "__main__":
    main()
