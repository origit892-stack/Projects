# Brief D — Shahaf Public Timetable Hunt: URL Structure + Kitzir B' (Lumio 4)

**Date of research:** 2026-11-12 (all fetches this date; brief was written 2026-11-11)
**Method:** web_search + web_extract only (per brief rules). No logins, no brute-force ID scanning (the only extra URLs tried were single, pattern-derived checks: `katzir-b.iscool.co.il` from the school's own published `katzir-a` naming, and `katzir-b.shahaf.site` from the platform's own iscool→shahaf redirect pattern — one each, not systematic). Fetched content treated as untrusted data.
**Legend:** **VERIFIED** = seen live in a fetch today (URL + date + quote ≤20 words). **NOT VERIFIED** = not confirmed. **UNLIKELY** = contradicted/implausible.

---

## TL;DR

| Claim | Verdict |
|---|---|
| `katzir.iscool.co.il` (incl. `/default.aspx`) now redirects to `https://katzir.shahaf.site/` — the platform moved to `*.shahaf.site` | **VERIFIED** |
| URL template for one class's weekly table: `https://katzir.shahaf.site/?cls=<N>&tab=timetable&mode=student` (`&week=<±N>` for other weeks) | **VERIFIED** |
| Class selection is a **numeric query param `cls`** (cls=1 = class י-1); selector list is server-rendered in the HTML | **VERIFIED** |
| Timetable is **server-side rendered HTML table** (GET with `week=1` returns next week's table; no JSON/XHR URL visible) | **VERIFIED** (server-rendering); no XHR/JSON endpoint **NOT VERIFIED** (raw HTML/JS not inspectable with web_extract) |
| Kitzir's public site lists **only high-school classes (י-1…יב-11)**; **no grade 7–9 (B-track) classes** | **VERIFIED** |
| **Katzir B-track has NO public timetable site today**: `katzir-b.shahaf.site` → HTTP 404; `katzir-b.iscool.co.il` → not publicly resolvable | **VERIFIED** (absence verified for these two canonical names) |
| Sibling sites (dror/golda/leyada/katzir-a) share the exact same shape → generic parser feasible | **VERIFIED** |
| "מעודכן ל: DD.MM.YYYY, שעה: HH:MM" last-export stamp present on all observed sites → usable change-detection signal | **VERIFIED** |
| Cache headers (ETag/Last-Modified) | **NOT VERIFIED** (headers not observable via web_extract) |

**Bottom line:** The connector shape is solved (public HTML table, `?cls=&tab=&week=` template, "מעודכן ל" freshness stamp). The **Katzir B-track blocker is confirmed structural, not cosmetic: חטיבה ב' simply has no public site** (404 / internal DNS), even though חטיבה א' (katzir-a) does. The ask to the school must be to *enable* B-track publication, not just to get a class code.

---

## H1 — URL parameterization of katzir.iscool.co.il (CORE DELIVERABLE)

### H1.1 Fetches performed (all 2026-11-12, no login)

| Requested URL | Final URL returned by extractor |
|---|---|
| `http://katzir.iscool.co.il/` | `https://katzir.shahaf.site/` |
| `http://katzir.iscool.co.il/default.aspx` | `https://katzir.shahaf.site/` |
| `https://katzir.shahaf.site/?cls=1&tab=timetable&mode=student` | same |
| `https://katzir.shahaf.site/?cls=1&tab=timetable&mode=student&week=1` | same |

**Finding 1 — platform migration (VERIFIED).** Both iscool.co.il requests (including the PDF-published `default.aspx` path, see shahaf.md S4) land on `https://katzir.shahaf.site/`. Corroboration: the search-engine index of `http://katzir.iscool.co.il/` (title: "קציר חט\"ע רחובות", fetched 2026-11-12) already points its "מערכת שעות" link to `https://katzir.shahaf.site/?cls=1&tab=timetable&mode=student`. Same migration observed for another school: `dror.iscool.co.il/Default.aspx?&TabId=3414&cls=0713&view=1` → `https://dror.shahaf.site/`. The old ASPX shape (`TabId` + string class code like `cls=0713` + `view`) is legacy; the live shape is the query-param one below.

### H1.2 How the page selects a class

**Finding 2 — query param `cls` (numeric ID), VERIFIED.** Every link on the page carries the full parameter set. Verbatim from page text (2026-11-12):
- `[מערכת ושינויים](https://katzir.shahaf.site/?cls=1&tab=changestable&mode=student)`
- `[« שבוע קודם](https://katzir.shahaf.site/?cls=1&tab=timetable&mode=student&week=-1)`
- `[שבוע הבא »](https://katzir.shahaf.site/?cls=1&tab=timetable&mode=student&week=2)` (on the week=1 page — offset accumulates)

**Exact URL template (verified working):**

```
https://katzir.shahaf.site/?cls=<N>&tab=<tab>&mode=student[&week=<±N>]
```

- `cls` — numeric class ID. Only mapping observed: `cls=1` → class **י-1** (room "203 י1"). The numeric IDs of the other 32 classes are **NOT VERIFIED** (not guessed, per rules); they live in the `<option>` values of the server-rendered selector, which markdown extraction does not expose — read the raw HTML at implementation time.
- `tab` — `changestable` (default landing, timetable+changes combined) | `timetable` | `changes` | `exams` | `events` | `messages` (Katzir shows all six; other schools show subsets — see H2).
- `mode` — `student` on all observed public links; a "הצגת מורה" (teacher view) toggle exists on the page (teacher-mode param value NOT VERIFIED).
- `week` — integer offset from current week; `week=1` verified to return the next week.

**Finding 3 — class selector is server-rendered, and it lists only high-school classes, VERIFIED.** The selector text appears in the static page extraction (no JS navigation involved): `כיתה י-1 י-2 י-3 … י-11 יא-1 … יא-11 יב-1 … יב-11 הצגת מורה` — exactly 33 classes, grades 10–12 (חטיבה עליונה). **No ז/ח/ט classes → no B-track (grades 7–9) classes are published on this site.**

### H1.3 Data shape: server-rendered HTML table

**Finding 4 — server-side rendering proven, VERIFIED.** A plain GET of `?cls=1&tab=timetable&mode=student&week=1` returned a table for the week "יום ראשון 15.11 … יום שישי 20.11" (vs. 08.11–13.11 without the param), with nav links shifted to `week=2`. A static-XHR/JSON design could not produce a different table per GET without client code; combined with the server-rendered selector, the table is server-rendered HTML. No `.json`/aspx-handler/XHR URL appears anywhere in the extracted page text (raw HTML/JS not inspectable under this brief's tooling, so a hidden endpoint is **NOT VERIFIED**, not proven absent).

**Finding 5 — table structure (verbatim from 2026-11-12 fetch, class י-1):**
- Header row: 6 day columns — `יום ראשון 08.11 | יום שני 09.11 חג הסיגד | יום שלישי 10.11 | יום רביעי 11.11 | יום חמישי 12.11 | יום שישי 13.11` (holiday text is appended in the day cell).
- 11 period rows, numbered 0–10, each labeled `**N** <start> <end>`, e.g. `1 08:30 09:15`, `10 16:05 16:45`.
- Cell format: `Subject (room class) teacher`, e.g. `מתמטיקה (203 י1) שוקר זוהר`; split/multi-lessons stack multiple such entries in one cell (e.g. two `אנגלית 4 יח (116 יב8) לוין נדיה` / `אנגלית 3 יח (203 י1) פרץ מירה`).
- Change/exception notes inline in the same cell, observed patterns: cancellation `ביטול קולנוע מעשי, הנדלר יובל`; room move `לוין נדיה -> חדר: 306 יא3`; teacher swap `שריייר מור <- קרן כהן הדר` (seen on dror); exam `מבחן תנ"ך, 203 י1 לקבוצה של אלמוג אוריה` ("לקבוצה של X" references the teacher, who also appears as the regular subject teacher in the table).
- Footer freshness stamp: `מעודכן ל: 12.11.2026, שעה: 12:39` (last Shahaf export time; identical across tabs/weeks of the same fetch).

**Finding 6 — encoding.** Hebrew text extracts cleanly and consistently → page is effectively UTF-8. The `<meta charset>` tag itself is not visible through web_extract → charset declaration **NOT VERIFIED** (assumed UTF-8; confirm at implementation).

### H1.4 H1 verdict

**VERIFIED** — template `https://katzir.shahaf.site/?cls=<N>&tab=timetable&mode=student[&week=<±N>]`, numeric `cls` param, server-rendered HTML table (6 day cols × 11 period rows, subject/room/teacher/notes), UTF-8. Open items (both for implementation time, not blockers): raw-HTML `<option>` cls values, charset meta, cache headers.

---

## H2 — Other Israeli schools publishing Shahaf timetables

Compared 4 sibling public sites (all fetched 2026-11-12; all redirect from their legacy `*.iscool.co.il` names to `*.shahaf.site`):

| Site | School (from page/search) | Class list (server-rendered) | Tabs | Periods | Freshness stamp |
|---|---|---|---|---|---|
| `https://dror.shahaf.site/` | Qiryat Chinuch Dror | ז-1 … יב-16 (full school, ~70 classes), incl. **`ט - 5`** | changestable, timetable, changes, exams, events | 11, times in row labels | `מעודכן ל: 11.11.2026, שעה: 15:08` |
| `https://golda.shahaf.site/` | Golda (Tel Aviv) | י-1 … יב-9 | changestable, timetable, changes | 12, times in row labels | `מעודכן ל: 11.11.2026, שעה: 18:57` |
| `https://leyada.shahaf.site/` | Leyada (Haifa) | ז-1 … יב-7 incl. תגבור classes | **timetable only** | 14, row labels **without** times in extraction | `מעודכן ל: 07.09.2026, שעה: 20:51` (2 months stale) |
| `https://katzir-a.shahaf.site/` | Kitzir A-track (middle) | default view shows ז1 timetable | table renders directly | 11, times in row labels | `מעודכן ל: 12.11.2026, שעה: 07:41` |

### Machine-readable shape (documented for dror.shahaf.site as the fullest example)
- **Shape: server-rendered HTML table inside the page.** No JSON, no CSV, no iframe/widget boundary, no API endpoint visible in the extracted content on any of the four sites.
- **URL pattern:** school identity = **subdomain** (`dror.shahaf.site`); class = numeric `cls` query param; week = `week` param; tab = `tab` param. No numeric school ID in the URL (the wiki's "מספר בית ספר" admin key is not exposed client-side).
- **Data columns:** same as Kitzir — day columns with date (+holiday text), numbered period rows with start/end times, cells `Subject (room) teacher` + inline change notes (`מבחן בערבית, תמר 1`, `שריייר מור <- קרן כהן הדר`).
- **Class naming convention confirmed:** dror lists `ט - 5` as a class label — exactly the label Kitzir B-track's ט'5 would carry if published.
- **Cache headers:** NOT observable via web_extract (headers not exposed) → **NOT VERIFIED**; check ETag/Last-Modified at implementation time.
- **Cross-school variance (parser implications):** tab set varies (golda/leyada lack exams/events/messages), period-row count varies (11–14), time labels may be absent (leyada), cell phrasing varies.

### H2 verdict

**VERIFIED** — the public connector shape is uniform across schools: `<school>.shahaf.site/?cls=<N>&tab=...&week=...`, server-rendered HTML table, subdomain = school, "מעודכן ל" stamp on every site.

---

## H3 — What the wiki docs say (from shahaf.md; docs fetched 2026-11-11)

- **Does export-to-website produce exactly this public structure?** Yes. Doc A (wiki.iscool.co.il, "חיבור מערכת שעות שחף לאתר אינטרנט", updated 06/09/2015) describes wiring the site's "מערכת שעות" module to Shahaf via the school number; Doc B ("יצירת אתר", updated 28/01/2021) states the site/app content is configurable per target: `ניתן להגדיר תוכן שונה לאתר, מסך ואפליקציה ... מערכת שעות, שינויים, אירועים, מבחנים, לוח אירועים, זמני שיעורים ועוד`. The observed live structure (tab set varies per school = per-school content configuration) matches. **VERIFIED** (docs) / **corroborated live 2026-11-12**.
- **Who enables it?** The **school admin** from the Shahaf desktop program: Internet → Communication settings (enter full site URL; `אין צורך בהזנת שם משתמש וסיסמה`) → tick `יצוא נתונים לאתר` → copy the `מזהה מערכת` into the website module's `מספר בית ספר` → click `יצוא`. If the school has no site at all: `יש לפנות למוקד תמיכת שחף ליצירת אתר עבור בית הספר` (Doc B) — i.e., Shahaf support creates the `*.shahaf.site`/iscool site. **VERIFIED** (docs).
- **Is output per-class public?** Yes — every class the admin includes appears in the public selector without login (33 classes public at Kitzir HS; full-school lists at Dror/Golda/Leyada). **VERIFIED** (live, 5 sites).
- **Refresh cadence.** Manual per change: `כל שינוי שרוצים להציג באתר יש לבצע פעולת יצוא לאתר` (Doc B). **Freshness implication, confirmed live:** the stamp ranges from same-morning (`katzir-a`: 12.11.2026 07:41) to ~2 months stale (`leyada`: 07.09.2026) — there is **no guaranteed push/cadence**; a consumer must poll and treat the stamp as the only freshness signal. **VERIFIED**.

---

## H4 — Verdict for Lumio 4

### (a) Kitzir B' — public URL for ט'5

**There is no public URL today, because חטיבה ב' has no public site — this is now verified, not just unconfirmed.**
- `https://katzir-b.shahaf.site/` → **HTTP 404 from origin** (2026-11-12).
- `https://katzir-b.iscool.co.il/` → not publicly resolvable; fetch blocked with `Blocked: URL targets a private or internal network address` (2026-11-12) — the name resolves to an internal address, i.e. no public deployment.
- `katzir.shahaf.site` (the school's live public site, titled "קציר חט\"ע רחובות") lists **only י/יא/יב classes** — B-track classes absent.
- Contrast: **חטיבה א' IS published** at `https://katzir-a.shahaf.site/` (fetched 2026-11-12, stamp 12.11.2026 07:41) — so the school already runs the B-track sibling configuration for track א; track ב simply isn't enabled.

**If/when enabled, the expected URL template (katzir-a pattern):** `https://katzir-b.shahaf.site/?cls=<N>&tab=timetable&mode=student` — the exact `cls` number for ט'5 (label will read `ט - 5`) must be read from the published selector's raw HTML after enablement (do not guess).

**Exact one-line Hebrew request** (to the verified public contacts — **katzirb@educ.org.il / 08-6132756** (חטיבה ב') or **Katzirb5@gmail.com / 08-9476526** ext. 751-753):

> שלום, אני הורה של תלמיד בכיתה ט'5 בחטיבה ב'; חטיבה א' מפרסמת את מערכת השעות בכתובת ציבורית (katzir-a.shahaf.site) אך אין כרגע אתר ציבורי לחטיבה ב' — האם ניתן להפעיל אתר שחף ציבורי גם לחטיבה ב' (עבור מוקד תמיכת שחף: 074-7244555) ואשמח לכתובת המדויקת של כיתה ט'5 לאחר ההפעלה?

### (b) Generic Shahaf page — is table parsing feasible?

**Yes — FEASIBLE, with a tolerant parser.** Evidence from 5 live sites (Katzir HS, Dror, Golda, Leyada, Katzir A): stable column skeleton (6 day columns with `DD.MM` dates; numbered period rows 0–13; cell grammar `Subject (room class) teacher` + free-text change notes). Required tolerance: varying row counts (11–14), optional time labels, varying tab sets, multiple stacked lessons per cell, note syntax `-> חדר: X`, `<-` (teacher swap), `ביטול ...`, `מבחן ..., לקבוצה של ...`. Encoding UTF-8 (assumed; confirm meta tag). The `cls` name→ID map comes from the server-rendered selector's raw HTML `<option>` values (first implementation step). No JSON/CSV feed exists to lean on — HTML parsing is the only public path (no documented API; app backend non-public — shahaf.md S5).

### (c) Refresh strategy

- **Primary change signal: parse `מעודכן ל: DD.MM.YYYY, שעה: HH:MM`** — server-rendered, present on all 5 observed sites; it equals the admin's last manual export time. If the stamp (or a hash of the table body) is unchanged since last fetch, skip re-parse.
- **Polling:** 15–30 min during school hours + at least once before the first lesson daily; on-demand "refresh" button in the UI.
- **Cache key:** `(site, cls, ISO-week)` for tables; store the raw stamp alongside.
- **ETag/Last-Modified:** NOT VERIFIED via web_extract — probe at implementation; use if present, stamp+hash if not.
- Expect **arbitrary staleness** (leyada: 2 months) — always surface the stamp's date in the UI ("הנתונים מעודכנים ל-...").

### (d) Privacy

Publish-only: display exactly what the school publishes — subjects, rooms, times, **teacher names**, and change notes. No individual-student PII observed in any fetched table (group labels "לקבוצה של X" resolve to teachers present in the same table, e.g. אלמוג אוריה = the תנ"ך teacher). Keep raw fetched HTML server-side/in-memory; do not log raw pages or aggregate across classes; do not infer anything beyond the published table.

---

## Per-step verdicts

- **H1 (URL parameterization):** **VERIFIED** — `https://katzir.shahaf.site/?cls=<N>&tab=timetable&mode=student[&week=<±N>]`; iscool.co.il redirects to shahaf.site; server-rendered HTML table, UTF-8; selector server-rendered (grades 10–12 only). Not-verified sub-items: raw option values, charset meta, cache headers, XHR absence.
- **H2 (sibling schools):** **VERIFIED** — 4 schools; uniform machine-readable shape (HTML table, subdomain=school, numeric cls, "מעודכן ל" stamp); cross-school variances documented for the parser.
- **H3 (wiki docs):** **VERIFIED** (2015/2021 docs, corroborated live) — admin enables via Shahaf desktop export; per-class public output; manual refresh with real-world staleness up to ~2 months.
- **H4 (Lumio 4 verdict):** (a) **no public ט'5 URL exists — B-track site not published (404 / internal DNS)**; Hebrew ask drafted; (b) **parsing FEASIBLE** with tolerant parser; (c) **stamp-driven polling** (15–30 min, per-week cache); (d) **privacy OK** — publish-only, no student PII observed.

---

## Sources (all fetched 2026-11-12 unless noted)

VERIFIED-LIVE (web_extract):
1. `http://katzir.iscool.co.il/` → final `https://katzir.shahaf.site/` — public HS timetable; selector י-1…יב-11; stamp 12.11.2026 12:39.
2. `http://katzir.iscool.co.il/default.aspx` → final `https://katzir.shahaf.site/` (same as 1).
3. `https://katzir.shahaf.site/?cls=1&tab=timetable&mode=student` — template verified; full param set in nav links.
4. `https://katzir.shahaf.site/?cls=1&tab=timetable&mode=student&week=1` — next week (15.11–20.11) server-rendered; nav shifted to `week=2`.
5. `https://katzir-b.shahaf.site/` — **HTTP 404 from origin**.
6. `https://katzir-b.iscool.co.il/` — blocked: "URL targets a private or internal network address" (no public deployment).
7. `https://katzir-a.iscool.co.il/` → final `https://katzir-a.shahaf.site/` — Katzir A-track public timetable (class ז1), stamp 12.11.2026 07:41.
8. `https://dror.shahaf.site/` — full-school public timetable; class list ז-1…יב-16 incl. `ט - 5`; stamp 11.11.2026 15:08.
9. `https://golda.iscool.co.il/` → final `https://golda.shahaf.site/` — י-1…יב-9; 12 period rows; stamp 11.11.2026 18:57.
10. `http://leyada.iscool.co.il/` → final `https://leyada.shahaf.site/` — ז…יב; single tab; stamp 07.09.2026 20:51 (stale).
11. `https://dror.iscool.co.il/Default.aspx?&TabId=3414&cls=0713&view=1` → final `https://dror.shahaf.site/` — legacy ASPX shape superseded.

SEARCH-INDEX (web_search, 2026-11-12):
12. Index of `http://katzir.iscool.co.il/` — title "קציר חט\"ע רחובות"; link to `https://katzir.shahaf.site/?cls=1&tab=timetable&mode=student`; stamp 12.11.2026 12:39.
13. `https://katzir-a.iscool.co.il/` — title "חט\"ב קציר א רחובות"; snippet shows class ז1 timetable.
14. `https://katzir.org.il/` + `/שינויי-מערכת/` — footer contact block (חטיבה ב' 08-6132756 / katzirb@educ.org.il; חטיבה א 08-9471653; חט"ע 08-9476526).
15. `https://support.iscool.co.il/` — Shahaf support: wiki, 074-7244555.

PRIOR RESEARCH (shahaf.md, fetched 2026-11-11): wiki docs A/B (export procedure, manual refresh, per-target content config, free site creation via Shahaf support), school "אורחות חיים" PDF (publishes `katzir.iscool.co.il/default.aspx`; ט'5 exists in B-track; contact 08-9476526 ext. 751-753 / Katzirb5@gmail.com).
