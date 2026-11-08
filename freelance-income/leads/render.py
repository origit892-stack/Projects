#!/usr/bin/env python3
"""Render the Leads Console dashboard.
Reads STATE.json (this dir) -> writes /Users/Ori/Documents/agent-operator/leads.html
Self-contained, dark theme matching the site, auto-refresh 5 min.
"""
import json, html, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(HERE, "STATE.json")
OUT_PATH = "/Users/Ori/Documents/agent-operator/leads.html"

STATUS = {
    "new":                 ("NEW",              "#f0883e"),
    "approved":            ("APPROVED",         "#3fb950"),
    "rejected":            ("REJECTED",         "#8b949e"),
    "sent_approval":       ("APPROVAL SENT",    "#58a6ff"),
    "sent_rejection":      ("REJECTION SENT",   "#58a6ff"),
    "awaiting_channel":    ("AWAITING CHANNEL", "#f0883e"),
    "awaiting_payment":    ("AWAITING PAYMENT", "#f0883e"),
    "paid":                ("PAID",             "#3fb950"),
    "started":             ("IN WORK",          "#58a6ff"),
    "dead":                ("CLOSED",           "#8b949e"),
    "test":                ("TEST",             "#8b949e"),
}

def esc(s):
    return html.escape(str(s if s is not None else ""))

def main():
    with open(STATE_PATH) as f:
        st = json.load(f)
    cfg = st.get("config", {})
    leads = st.get("leads", [])
    site = esc(cfg.get("site_url", ""))
    payment = cfg.get("payment_link")
    pay_line = (f'<p class="muted">Payment link: <a href="{esc(payment)}">{esc(payment)}</a></p>'
                if payment else
                '<p class="muted warn">Payment link: <b>not set</b> — approved leads wait here until it is.</p>')

    rows = []
    for ld in sorted(leads, key=lambda x: x.get("updated", ""), reverse=True):
        label, color = STATUS.get(ld.get("status", "new"), (ld.get("status", "?"), "#8b949e"))
        fit = esc(ld.get("fit", "?"))
        src = ld.get("source", "#")
        title = esc(ld.get("title", "—"))
        draft = esc(ld.get("draft", ""))
        notes = esc(ld.get("notes", ""))
        draft_html = f'<details><summary>draft</summary><p class="draft">{draft}</p></details>' if draft else ""
        notes_html = f'<p class="notes">{notes}</p>' if notes else ""
        rows.append(f"""<article class="card">
  <div class="lhead">
    <span class="lid">{esc(ld.get('id','?'))}</span>
    <span class="fit fit-{fit.lower()}">FIT {fit}</span>
    <span class="badge" style="background:{color}22;color:{color};border:1px solid {color}55">{label}</span>
    <span class="lupd muted">{esc(ld.get('updated',''))}</span>
  </div>
  <h3>{title}</h3>
  <a class="src" href="{esc(src)}" target="_blank" rel="noopener">source →</a>
  {draft_html}{notes_html}
</article>""")

    body = "\n".join(rows) if rows else '<p class="empty">No leads yet — the radar runs daily at 09:00 IST.</p>'
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="300">
<title>Leads Console — The Agent Operator</title>
<style>
:root{{--bg:#0d1117;--panel:#161b22;--border:#30363d;--text:#e6edf3;--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--orange:#f0883e;--mono:SF Mono,SFMono-Regular,Menlo,Consolas,monospace}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;line-height:1.55}}
.wrap{{max-width:860px;margin:0 auto;padding:40px 24px 80px}}
h1{{font-size:26px;letter-spacing:-.3px}}
.top{{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:6px}}
.muted{{color:var(--muted)}}
.sub{{color:var(--muted);font-size:14px;margin-bottom:24px}}
.approve{{background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--green);border-radius:10px;padding:16px 20px;margin-bottom:28px;font-size:14.5px}}
.approve code{{font-family:var(--mono);background:#0d1117;border:1px solid var(--border);border-radius:5px;padding:1px 7px;color:var(--green)}}
.card{{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin-bottom:14px}}
.lhead{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}}
.lid{{font-family:var(--mono);font-size:13px;color:var(--muted)}}
.lupd{{font-family:var(--mono);font-size:12px;margin-left:auto}}
.badge{{font-family:var(--mono);font-size:12px;font-weight:700;letter-spacing:1px;padding:3px 10px;border-radius:6px}}
.fit{{font-family:var(--mono);font-size:12px;font-weight:700;padding:3px 8px;border-radius:6px;border:1px solid var(--border);color:var(--muted)}}
.fit-a{{color:var(--green);border-color:var(--green)}}
.fit-b{{color:var(--orange);border-color:var(--orange)}}
.fit-c{{color:var(--accent);border-color:var(--accent)}}
.card h3{{font-size:16.5px;margin-bottom:6px}}
.src{{font-family:var(--mono);font-size:13px;color:var(--accent)}}
details{{margin-top:10px}}
summary{{cursor:pointer;font-family:var(--mono);font-size:12.5px;color:var(--muted)}}
.draft{{margin-top:10px;font-size:14px;color:var(--muted);white-space:pre-wrap;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:12px}}
.notes{{margin-top:10px;font-size:13.5px;color:var(--orange)}}
.warn b{{color:var(--orange)}}
.empty{{color:var(--muted);padding:40px 0;text-align:center}}
footer{{margin-top:36px;color:var(--muted);font-size:12.5px;font-family:var(--mono)}}
</style>
</head>
<body>
<div class="wrap">
  <div class="top"><h1>Leads Console</h1><span class="muted" style="font-size:14px">The Agent Operator</span></div>
  <p class="sub">Auto-refreshes every 5 min · state updates within 3h of your approval · <a href="index.html" style="color:var(--accent)">← site</a></p>
  <div class="approve">
    <b>Approve / reject:</b> tell the chief in chat — <code>approve L-001</code> or <code>reject L-001</code>.
    The chief updates this page, and the 3-hour check sends the reply.
  </div>
  {pay_line}
  {body}
  <footer>state: freelance-income/leads/STATE.json · rendered by render.py</footer>
</div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(page)
    print(f"rendered {OUT_PATH} ({len(leads)} leads, {len(page)} bytes)")

if __name__ == "__main__":
    main()
