# Lumio Mission — MoE Identity/Data Ecosystem + 0-ILS Free-Tier Analysis

- **Date of research:** 2026-11-11
- **Method:** `web_search` + `web_extract` only. No logins. Official government/vendor sources outrank community.
- **Labels:** `VERIFIED` (official source retrieved/read) · `NOT VERIFIED` (no official confirmation found; evidence cited as such) · `UNLIKELY` (strong negative or contradictory evidence)
- **Pages without a printed date:** labeled "page date not printed; accessed 2026-11-11".

---

# PART A — Ministry of Education (MoE) identity & data ecosystem

## A1. IDM — is there a PUBLIC path for a third-party app to register as SAML/OIDC SP?

### VERDICT: YES, an official public path exists — but it is a **vendor-approval-gated process**, not self-service, and it is designed for vendors with MoE-approved products, not for private individuals.

**The key official page** (found via search, full text extracted):
`sapakim.education.gov.il/tech/idm` — title: *"הזדהות אחידה - חיבור ספקים חיצוניים למערכת ההזדהות המרכזית של משרד החינוך (IDM)"* (VERIFIED, official MoE vendor-portal domain, page date not printed; accessed 2026-11-11).

Evidence from that page:

| Claim | Label | Quote (≤20 words) |
|---|---|---|
| MoE extended central authentication to external vendors | VERIFIED | "החליט המשרד להרחיב את שירותי הגישה וההזדהות המרכזיים גם לספקים חיצוניים" |
| SSO between systems is the explicit goal | VERIFIED | "יתאפשר מעבר בין מערכות שונות ללא צורך בהזדהות נוספת. (SSO)" |
| Student credentials are issued at school enrolment | VERIFIED | "פרטי הזיהוי והסיסמה מופקים עבור כל תלמיד במסגרת תהליך קליטתו בבית הספר" |
| Protocols: OPENID, SAML, FEDERATION — vendor's choice | VERIFIED | "ניתן להתחבר למערכת הזדהות אחידה באמצעות כל הפרוטוקולים הנפוצים – OPENID, SAML, FEDERATION לבחירת הספק" |
| SSO connection is a condition of product approval in the MoE educational catalog | VERIFIED | "אישור מוצר בקטלוג החינוכי מותנה בהשלמת תהליך החיבור של המוצר למערכת ההזדהות האחידה" |
| Vendor products must first obtain MoE approval | VERIFIED | (sapakim.education.gov.il/tech/) "ספקים וגופים מפתחים... נדרשים לקבל אישור של משרד החינוך" |

**The connection process ("תהליך החיבור")** is documented with public download links on the same page (VERIFIED — links listed on the official page; documents not individually opened):
1. "מאפייני טוקן בפרוטוקולים השונים" (token attributes per protocol) — PDF, `meyda.education.gov.il/files/anan_chinuchi/meda_lspakim/tfasim/teud-sugey-token.pdf`
2. **"ספק שירות - טופס פרטי חיבור שירות להזדהות אחידה"** (Service Provider — connection-details form) — DOCX form, `meyda.education.gov.il/files/anan_chinuchi/meda_lspakim/tfasim/sapak-sherut-tofes-pirtey-chibur-sherut.docx`
3. "מסמך הנחיות לחיבור ספק במערכת החינוך למערכת ההזדהות של המשרד" (connection instructions) — PDF, `meyda.education.gov.il/files/anan_chinuchi/meda_lspakim/anchayot_drishot_lechibur_sapak_chistoni.pdf`
4. "טופס פתיחת תקלה במערכת ספק חיצוני" (vendor fault-report form) — DOCX, sent with fault reports to **GR_IDM_Team@education.gov.il**

**Answers to the specific A1 questions:**

| Question | Answer | Label |
|---|---|---|
| Who approves? | The MoE "GR_IDM_Team" (central authentication team), operated under the vendor-services portal `sapakim.education.gov.il` (ספקים ושירותים משרד החינוך). Historically this function sits with the ministry's digitization management (מינהל תקשוב ומערכת מידע). | VERIFIED (contact + portal); unit naming `NOT VERIFIED` |
| Required forms / security / accessibility? | The DOCX connection-details form + connection-instructions PDF (links above). Broader vendor requirements that apply to any MoE product: "תקן אבטחת מידע - לספקי משרד החינוך", "נוהל פרטיות למוצרים טכנולוגיים במשרד החינוך", "נוהל התאמות נגישות... – מאי 2025" (all listed in the sapakim portal navigation, VERIFIED as listed; contents not read). | VERIFIED (existence of the requirement set) |
| Sandbox existence? | **NOT mentioned anywhere on the public pages.** No public documentation of a sandbox/staging IdP environment. | NOT VERIFIED |
| Cost (if documented)? | **No cost is documented** anywhere in the public pages. The process appears administrative, but this is not confirmed. | NOT VERIFIED |
| Can a private individual / student request registration? | No self-service portal for individuals exists. The process targets "ספקים טכנולוגיים" (tech vendors) whose product has MoE catalog approval; the connection is *conditional on* that approval. A student cannot self-register. | UNLIKELY (process is explicitly vendor/product-approval-based; no public individual path found) |
| Realistic pilot path via a school principal? | The only realistic near-term path: (1) principal + school digitization coordinator (רכז תקשוב) sponsor the app as a school-level pilot; (2) contact GR_IDM_Team@education.gov.il with the A5 inquiry, attaching the principal's letter of intent and offering to fill the official connection form; (3) request a sandbox/exception for a single-school pilot. No published SLA or timeline. | UNLIKELY to be fast; path is inferred from the official process docs (the pilot route itself is a recommendation, not a published procedure) |

**Supporting official evidence that MoE SAML federation is real and operational (not just policy):**
- `lgn.edu.gov.il/nidp/saml2/sso?id=EduCombinedAuthUidPwd&option=credential` — the live MoE SAML 2.0 SSO endpoint, offering username/password + one-time SMS code ("כניסה עם קוד משתמש וסיסמה", "כניסה עם קוד חד-פעמי לנייד"). VERIFIED (official domain, page date not printed).
- Government procurement document (mr.gov.il attachment "מסמכי הזמנה" for משרד החינוך, unified-identity project): "התאמת המערכת לעבודה עם מנגנון הזדהות והרשאות מבוסס SAML ובהתאם למבנה ה CLAIM של משרד החינוך. הגדרת קישור מוגן למערכת... Protected Resource". VERIFIED as a government procurement document via search snippet; the full tender page could not be opened (crawl timeout) — tender number/date NOT VERIFIED.
- Schools portal (`mosdot.education.gov.il/personal/identification`, VERIFIED): "הזדהות אחידה מאפשרת להיכנס באמצעות סיסמה אחת לכלל מערכות משרד החינוך ולסביבות הדיגיטליות המאושרות" — i.e., external ("סביבות... מאושרות") approved digital environments are an existing, normal category.

**Searches run for A1 (all performed 2026-11-11):**
1. `משרד החינוך מערכת אימות מרכזית SAML הרשמת מערכת חיצונית`
2. `"lgn.edu.gov.il" SAML metadata service provider integration`
3. `מינהל תקשוב משרד החינוך הזדהות מרכזית SAML אבטחה יישומים חיצוניים`
4. `"edu.gov.il" אינטגרציה SSO OAuth אפליקציה חיצונית תלמידים`
5. `mashov.gov.il התחברות אימות מרכזי משרד החינוך`
6. `משרד החינוך הזדהות אחידה סביבות תוכן חיצוניות אישור הרשמה תהליך`
7. `mr.gov.il משרד החינוך מכרז הזדהות אחידה SAML יישומי מערכת החינוך`

→ **Conclusion: a public path DOES exist (the sapakim IDM page + forms). It is not open self-registration; it is a vendor process requiring MoE product approval, and sandbox/cost are undocumented. An individual student cannot request it; the school-principal pilot route is the practical entry.**

---

## A2. ED-DATA — can a NEW app PULL student learning data?

### VERDICT: There is **no official MoE system named "ED-DATA"**. The name belongs to an **independent private project** (`eddata.live`). The official MoE data-sharing mechanisms that do exist are **push-based and vendor-gated** — none lets a new arbitrary app pull per-student tasks/grades.

| Finding | Label | Source |
|---|---|---|
| `eddata.live` explicitly states it is not an official MoE site: "ED-DATA אינו אתר ממשלתי ואינו מייצג גוף ציבורי" | VERIFIED (self-declaration) | eddata.live/about, eddata.live/terms (page date not printed; accessed 2026-11-11) |
| `eddata.live` aggregates public MoE/statistical sources; it is a data-access layer, not an MoE API | VERIFIED | eddata.live/about (accessed 2026-11-11) |
| Official MoE vendor data channel "מפרט ממשקים (כספת)" is MoE→approved-software direction: "נספק בעמוד זה עבורכם את הנתונים שקיבלתם בעבר מהמנב"ס" (data the vendor previously received from the Manbas school system), "כחלק מתוכנית המשרד להחלפת תוכנת המנב"ס" | VERIFIED | `sapakim.education.gov.il/tech/interfaces/` (title + snippet, page date not printed) |
| Official MoE LRS channel is vendor→MoE push of **usage** data (see A3) — not a pull API for grades | VERIFIED | `sapakim.education.gov.il/tech/lrs/` |
| Research data (identified or anonymized) is only obtainable via the national research authority RAMA through its data-request process; identified data is processed in a secure room (Central Bureau of Statistics) | VERIFIED | rama.gov.il/questions/data-request (official MoE authority domain, page date not printed) |
| Per-student grades/tasks live in מנב"סנט (MoE school-management) and vendor systems (e.g., Mashov); **no public API for a new app to pull them was found** | NOT VERIFIED (absence finding from searches listed in A1 + the searches below) | — |

**Searches run for A2:** `ED-DATA משרד החינוך שיתוף נתונים חינוכיים`, plus the A1 search set. No official MoE page using "ED-DATA" for a data platform was found on gov.il / education.gov.il.

**Answer to the literal question:** as far as official sources show, a NEW app **cannot** pull student learning data (tasks/grades) from the MoE. The official flows are (a) MoE → approved software (כספת/interfaces, replacement of Manbas feeds) and (b) approved vendors → MoE (LRS usage data). Both are gated by MoE product/vendor approval.

---

## A3. LRS / xAPI — who writes, who reads, statement types, consumer authorization, do grades flow?

### VERDICT: The MoE LRS is real and xAPI-based (official, `sapakim.education.gov.il/tech/lrs/`), but it is a **vendor→MoE push of *usage* telemetry for approved digital-content vendors**. It is **not** a public store of grades/assignments, and there is **no documented read access for new external consumers**.

Official page: "חיבור ספקי חומרי למידה דיגיטליים למאגר נתוני השימוש המרכזי של משרד החינוך (LRS)". Evidence (all VERIFIED, page date not printed; accessed 2026-11-11):

| Question | Answer | Quote (≤20 words) |
|---|---|---|
| What is it? | A platform to collect & aggregate **usage data of students and teaching staff in digital learning content** | "פיתח משרד החינוך פלטפורמה לאיסוף ואיגום נתוני השימוש של התלמידים ועובדי ההוראה" |
| Standard | ADL Initiative xAPI is officially adopted | "המשרד אימץ את תקן xAPI של ADL Initiative" |
| Who writes statements? | **Digital-content vendors** (LRPs). Vendors in the central digital-content tender are **obligated**; other approved digital-content vendors may opt in; development-tender vendors are obligated per tender | "כל הספקים המאושרים ב-מכרז... מחוייבים להעביר את נתוני השימוש, בהתאם לתנאי המכרז" |
| Cadence | Near real-time streaming + **monthly cumulative reconciliation report**; vendor must fix discrepancies | "באופן שוטף, near real-time" |
| Identity in statements | MoE supplies **hashed** IDs; delivered via the IDM **token** (post-authentication) and via learning-group feeds from the NMM system ("כספת"); statement must use `exidentifier` in `homepage`, not `idnumber` | "משרד החינוך מחזיק ומספק תעודות זהות מעורבלות (hashed)" |
| Statement types | Usage statements per digital-content type, per the MoE "usage monitoring" metadata spec (linked instructions, not read in full) | "בהתאם למטה-דאטה המוגדר במערכת ניטור שימושים לסוג חומר הלמידה הדיגיטלי" |
| Who can READ the statements? | Only the **MoE side** is described (the platform aggregates *to* the ministry). **No public consumer authorization, no read API for new apps is documented.** | NOT VERIFIED (no read path found on the official page) |
| Do grades/assignments flow there? | **No.** The scope is *usage of digital content* (activity in content), not grades or assignments. No mention of grades anywhere on the page. | UNLIKELY (scope language on the official page is usage-only) |
| Connection form | Public Monday.com initial-connection form + integration guide ("מדריך ההתממשקות") | VERIFIED (link on the page: forms.monday.com/forms/224be31131bfaddd3fb1fbc4a953c419) |

**Note on "Mashov" (common confusion):** Mashov (משו"ב) is **not** the MoE LRS and not an MoE system — it is operated by a private company: App Store listing "Developer: MASHOV - IMMEDIACY TRANSPARENCY & CONTROL LTD" (by Priority Software) (VERIFIED via Apple App Store listing, accessed 2026-11-11). Its teacher login page shows a "הזדהות משרד החינוך" (MoE identity) option (VERIFIED via web.mashov.info snippet — vendor page, not MoE).

**Searches run for A3:** `מאגם LRS xAPI משרד החינוך הצהרות לומדים`, `"מאגם" משרד החינוך מערכת`, `education.gov.il LRS "מאגם" xAPI learning records`, `sapakim.education.gov.il LRS "מאגר נתוני שימוש" ספקים`. (The term "מאגם" as a MoE LRS returned **no** official results; the official LRS is named "מאגר נתוני השימוש המרכזי (LRS)".)

---

## A4. Core distinction: does the MoE SSO session belong exclusively to the origin systems, or can a NEW registered client obtain its own identity token? Identity federation ≠ data federation.

### VERDICT: **Identity federation is open (in principle) to registered clients; data federation is closed to approved vendors only.** A student logging into Mashov (or any origin system) via the MoE SSO button obtains a session **scoped to that system only** — it does **not** transfer to another app. A *new* client that completes the MoE's IDM connection process **can** obtain its own identity token — but that is an identity assertion, **not** a delegated data grant.

Reasoning with sources:

1. **The MoE IdP is a SAML 2.0 identity provider issuing tokens per registered SP.** The live endpoint `lgn.edu.gov.il/nidp/saml2/sso` exists (VERIFIED), and the MoE's own vendor documentation defines "token attributes per protocol" (מאפייני טוקן בפרוטוקולים השונים) for connected services (VERIFIED, link on the IDM page). In standard SAML, an assertion issued to SP-A is signed and addressed to SP-A; SP-B cannot present or consume it. This is a property of the SAML standard, not merely MoE policy. `VERIFIED` (endpoint + MoE token-attributes doc); the "no cross-SP transfer" mechanism is `VERIFIED` as SAML 2.0 behavior.
2. **A new registered client CAN obtain its own token.** The IDM page explicitly extends central authentication to external vendors and says the protocol is the vendor's choice (OPENID/SAML/FEDERATION) (VERIFIED, quotes in A1). Community evidence that third-party, non-MoE domains are in fact federated through this IdP: third-party education portals (e.g., Ofek at cet.ac.il, Galim at galim.org.il) log in by redirecting to `lgn.edu.gov.il` SSO and returning with a full session (source: skillhub.360.com/skills/ofek-galim — **community documentation, NOT VERIFIED officially**; no student data or credentials reproduced here).
3. **The SSO session does NOT transfer between apps.** There is no MoE-documented mechanism by which a Mashov/MoE session could be presented to another service. The MoE's own description of SSO is scoped: "מעבר בין מערכות שונות ללא צורך בהזדהות נוספת (SSO)" for services connected to the central IdP (VERIFIED, IDM page). Each connected system authenticates the student itself against the IdP. So: *a student logging into Mashov via MoE SSO does NOT hand Lumio (or anyone) that session* — `VERIFIED` as a property of the federation design (per-SP tokens; no delegation mechanism documented).
4. **Data federation is a separate, closed layer.** Even with its own identity token, a new app gets **no** grades/tasks: grades live in מנב"ס and vendor systems (A2), the LRS is usage-push only (A3), and the MoE's data feeds (כספת/interfaces) are provided "לתוכנות המורשות" (to authorized software) under the Manbas-replacement plan (VERIFIED, interfaces page snippet). OAuth-style delegated authorization ("student grants app access to MY grades") is **not documented anywhere** in official sources. `NOT VERIFIED` / `UNLIKELY` for such a mechanism today.

**One-line summary for Lumio:** *Identity via SSO = obtainable after SP registration (gated, vendor process). Student learning data via the same login = NOT obtainable today by any new app; it requires a separate, separate-approval data arrangement that no public channel provides.*

---

## A5. Draft inquiry message (Hebrew) — SP registration request to MoE / school support

> **נושא:** בקשה לחיבור לאימות אחיד (IDM) — פילוט אפליקציית התלמידים "Lumio" במוסד חינוכי

> לרשות ההזדהות האחידה (GR_IDM_Team@education.gov.il), שלום רב,
>
> אנו מפתחים את **Lumio** — אפליקציית תלמידים חינמית (יישום רשת) לניהול לימודי אישי (תצוגת משימות, מעקב התקדמות). במסגרת פילוט בית-ספרי אנו מעוניינים לאפשר לתלמידים התחברות באמצעות **הזדהות משרד החינוך (SSO)**, כדי להימנע מניהול סיסמה נוספת.
>
> לפי המידע באתר "ספקים ושירותים משרד החינוך" (דף "הזדהות אחידה (IDM)"), אנו פונים בבקשה הבאות:
>
> 1. **רישום SP (מתחם שירות) לאימות אחיד:**
>    - שם היישום: **Lumio**
>    - פרוטוקולים נדרשים: **SAML 2.0 / OpenID Connect** — נגלם כמקובל על משרד החינוך (כמפורסם: OPENID, SAML, FEDERATION לבחירת הספק)
>    - כתובת Callback / ACS (נקודת החזרה): **[למלא — תסופק לאחר קבלת סביבת אימות/מטא-דאטה של המשרד]**
>    - קטגוריות נתונים המבוקשות: **זהות בלבד** — מאפייני הטוקן הסטנדרטיים המוגדרים על-ידי המשרד; לא נבקש כל נתון נוסף בשלב זה
> 2. **בקשה לסאנדבוקס:** האם קיימת סביבת אימות (sandbox/staging) לבדיקת חיבור SSO לפני העלאה לייצור? אם כן — מה הליך הקבלה והמשך הצפוי?
> 3. **שאלה נפרדת הנתונים (לא כחלק מההזדהות):** האם קיים מנגנון המאפשר למוצר מאושר קבלת נתוני לימוד של תלמיד (משימות/ציונים) — למשל דרך ממשקי "כספת" או דרך LRS — ואילו התנאים וההליך לחיבור כזה?
> 4. **הקשר הפילוט:** הפילוט מתוכנן במוסד החינוכי **[שם המוסד — למלא]**, בהסכמת ומימון כוונת המנהל/ת, להיקף של כיתה אחת (עד N תלמידים). לא תאוחסן שום מידע אישי מעבר לתוכן הלימודי וההתקדמות, והמוצר יתאים לתקני המשרד (אבטחת מידע, נגישות, פרטיות).
>
> מצורפים: תיאור היישום, פרטי חיבור, וכן **מכתב כוונה של מנהל/ת בית הספר**. נמלא מיד כל טופס שיידרש, לרבות "טופס פרטי חיבור שירות להזדהות אחידה" הנמצא באתר הספקים.
>
> מראש תודה,
> [שם מלא, תפקיד, טלפון, דוא"ל]
> [קשר בית-ספרי: שם המנהל/ת, מוסד, טלפון]

*No student personal data appears in this draft by design; placeholders are marked.*

---

# PART B — 0 ILS/month operation (free tiers as of 2026-11-11)

## B1. Supabase Free plan — verified limits

Sources: `supabase.com/pricing` (page date not printed; accessed 2026-11-11), `supabase.com/docs/guides/platform/billing-on-supabase` (**Updated Sep 17, 2026**), `supabase.com/docs/guides/functions/limits` (accessed 2026-11-11), `supabase.com/docs/guides/platform/free-project-pausing` (accessed 2026-11-11), `supabase.com/docs/guides/functions/schedule-functions` + `supabase.com/docs/guides/cron` (accessed 2026-11-11). All VERIFIED.

| Item | Free-plan limit | Note |
|---|---|---|
| Price | $0/month | "Free: $0/month" (pricing page) |
| Projects | **2 active** free projects per org; unlimited *paused* projects | Paused projects don't count toward the limit |
| Database size | **500 MB per project** | Hard cap |
| Auth users | **50,000 monthly active users (MAU)** | "Monthly Active Users: 50,000" |
| Bandwidth (egress) | **5 GB** egress (+ 5 GB cached egress) | Org-wide, monthly |
| File storage | **1 GB** (max file 50 MB) | |
| **Edge Function invocations** | **500,000 / month** (org-wide, per billing period) | Exceeding on Free → notification + grace period (Fair Use); **no overage billing on Free** — you lose service headroom, not get an invoice |
| Edge Function **max runtime** | **150 s** wall clock per worker (paid: 400 s); **2 s CPU** per request; 256 MB memory | "Free plan: 150s" |
| Edge Function **concurrency** | **No published per-plan concurrency number found** | NOT VERIFIED — docs publish memory/CPU/wall-clock, not a concurrency cap |
| Edge Function **secrets** | **100 per project** | |
| Functions per project | 100 (Free) | |
| Realtime | 200 peak connections, 2M messages/month | Not used by Lumio's core flow |
| **Auto-pause** | Free projects paused after **~1 week of low DB activity** | See analysis below |

### Auto-pause — the CRITICAL sync-while-PC-off question (all VERIFIED unless noted)

- "Supabase pauses Free Plan projects that show low activity over a 7-day period." (`free-project-pausing`)
- Inactivity = DB activity: "A Free plan project is considered inactive if it does not receive sufficient user database activity over the past week."
- Practical threshold: "Typically a few user requests to the database each day over the previous week is enough to keep the project from being paused."
- Warning: "A warning email roughly one week before the pause takes effect", then a confirmation email.
- After warning, pause is avoidable by: visiting the dashboard, or "making API calls to your project or sending requests via your connected application."
- **Does pausing kill scheduled sync? YES.** A paused project's database is offline; `pg_cron` runs *inside* Postgres, so **a paused project cannot fire its cron jobs**.
- **Does cron self-resume a paused project? NO (NOT VERIFIED as a feature; the only documented restore path is manual: "Click Resume project" in the Dashboard, valid for 1 year).** Conservative design assumption: **cron prevents pausing; it does not cure it.**
- **Does any traffic reset it?** DB-touching traffic (API calls that reach the database) is the documented counter to inactivity. Whether a pure Edge-Function invocation that never touches the DB counts is **NOT VERIFIED** — treat DB activity as the requirement.
- **Does a pg_cron job itself count as the activity?** Official docs do not state it explicitly. Community evidence is strong and consistent (e.g., r/Supabase: "28 pg_cron jobs on free tier… the free tier has held up"; a widely-used keep-alive pattern is a daily `cron.schedule('…', 'SELECT …')` job). Label: **NOT VERIFIED officially / UNLIKELY to be a problem** — plan for it, but watch the warning email.

### Scheduled Functions (cron) on Free plan

- Official: "The hosted Supabase Platform supports the pg_cron extension… In combination with pg_net… invoke Edge Functions periodically." (`schedule-functions`)
- Official Cron guide: jobs "can run anywhere from every second to once a year"; "recommend no more than 8 Jobs run concurrently. Each Job should run no more than 10 minutes." (`supabase.com/docs/guides/cron`)
- Plan availability: **no official statement restricting pg_cron to paid plans**; the docs are plan-neutral. Community: multiple reports of pg_cron running on free tier (see above). Label: **NOT VERIFIED officially / UNLIKELY to be restricted** — verify empirically (one SQL command on a free project settles it).
- **Exact free quota for cron:** there is **no separate cron quota**. Cron jobs consume (a) DB compute (included in the free project) and (b) any Edge-Function invocations they trigger, which draw down the **500,000/month** invocation quota. Practical cap: 1 job/day = 30 invocations/month ≈ 0.006% of quota.

## B2. Cloudflare Pages free — verified limits

Sources: `developers.cloudflare.com/pages/platform/limits/` (**Last updated Sep 5, 2026**), `developers.cloudflare.com/workers/platform/pricing/` (**Last updated Oct 2, 2026**), `developers.cloudflare.com/pages/get-started/direct-upload/` (accessed 2026-11-11). All VERIFIED.

| Item | Free-plan limit | Note |
|---|---|---|
| Builds | **500 builds/month** (not minutes); 1 concurrent build; 20-minute build timeout | "Builds per month: 500" |
| Requests | **Unlimited static requests** — "Requests to static assets are free and unlimited" (Workers pricing footnote) | A Pages **Function** counts against the Workers free quota (100,000 requests/day, 10 ms CPU/invocation) — avoid Pages Functions; Lumio's backend is Supabase |
| Egress / bandwidth | **Unlimited** — "There are no additional charges for data transfer (egress) or throughput (bandwidth)" (Workers pricing, all plans) | |
| Files per deployment | **20,000 files** (free; 100,000 paid) | |
| File size | **25 MiB** per asset | |
| **Direct Upload** | **Available** — "Direct Upload enables you to upload your prebuilt assets to Pages… Wrangler CLI or drag & drop"; no Git required. Caveat: a Direct Upload project cannot later switch to Git integration (create a new project then) | No plan restriction stated → usable on Free |
| Custom domain | **100 custom domains per project** (free); free SSL via Pages | Add your own domain at 0 ILS (domain itself is the only possible cost) |
| Projects per account | 100 | |
| Redirects/headers | `_redirects`: 2,000 static + 100 dynamic; `_headers`: 100 rules | |
| Static hosting notes | Free subdomain `<project>.pages.dev` included; preview deployments unlimited | |

## B3. Conservative cost estimate — 10 / 100 / 1000 students

**Assumptions (stated, adjustable):** 22 school days/month; each student: **1 manual sync + 3 page-loads/day**, each of which triggers exactly **1 Supabase Edge Function invocation**; the app runs **1 cron poll/day (30/month)**; each data response ≈ **100 KB** (conservative, full grades+tasks JSON); 1 DB row ≈ 1 KB with ~2× index/overhead; static assets served by Cloudflare (not counted against Supabase egress).

### Monthly Supabase Edge-Function invocations

Per student/month: 22 syncs + 66 loads = **88 invocations**.

| Scale | Student invocations | + Cron | Total/month | % of 500,000 quota |
|---|---|---|---|---|
| 10 | 880 | 30 | **≈ 910** | 0.2% |
| 100 | 8,800 | 30 | **≈ 8,830** | 1.8% |
| 1000 | 88,000 | 30 | **≈ 88,030** | 17.6% |

(Invocation quota would first be exhausted at ~5,600 students at these rates.)

### DB growth (tasks + school_items; 200 rows/student/year)

| Scale | Rows/year | Size/year (1 KB×2 overhead) | Time to 500 MB cap |
|---|---|---|---|
| 10 | 2,000 | ~4 MB | ~100+ years (not a constraint) |
| 100 | 20,000 | ~40 MB | ~10+ years |
| 1000 | 200,000 | ~400 MB | **~1–1.5 years** (first hard cap candidate) |

### Supabase egress (API responses only)

Per student/month: 88 × 100 KB ≈ **8.8 MB**.

| Scale | Egress/month | % of 5 GB quota |
|---|---|---|
| 10 | ~0.09 GB | <2% |
| 100 | ~0.9 GB | ~18% |
| 1000 | **~8.8 GB** | **~176% → exceeds the free cap** |

(Egress would first be exhausted at ~570 students at these assumptions. Mitigations if relevant: response compression, caching at the client, smaller payloads, or moving sync to a once-a-week cadence.)

### Verdict per scale — does 0 ILS hold TODAY?

| Scale | 0 ILS today? | First hard cap | Operational risk |
|---|---|---|---|
| **10** | **YES — comfortably** (all quotas <20% for years) | None in quota terms | **Project auto-pause** during long idle periods (summer break, zero syncs >7 days) — mitigated by daily cron keep-alive + monitoring the warning email |
| **100** | **YES — comfortably** for ~3–5 years | DB size (~10 yrs) | Same pause risk; otherwise negligible |
| **1000** | **NO at peak usage** — egress (5 GB) breached from month 1 if all students sync daily; DB (500 MB) breached within ~1–1.5 years | **Egress first, then DB** | On the Free plan exceeding a quota = grace period/fair-use throttling, not an invoice — i.e., service degradation, still 0 ILS but not reliable at this scale |

> **0 ILS is NOT a permanent guarantee.** Free tiers are a policy choice of the vendors: Supabase has changed Edge-Function caps before (e.g., July 2024 change to invocation quotas — documented in third-party tracking; Supabase's own pricing page is undated and current as of 2026-11-11), and Cloudflare's limits page is explicitly "limits observed… refer to Cloudflare plans for details". Re-verify both pages before each major milestone.

## B4. Verdicts per research question

**(1) Public SP registration path?** → **YES, with a gate.** Official MoE page `sapakim.education.gov.il/tech/idm` + public connection forms + GR_IDM_Team@education.gov.il; protocols OPENID/SAML/FEDERATION at vendor choice; **conditional on MoE product approval in the educational catalog**; no self-service for individuals; sandbox and cost undocumented (NOT VERIFIED). `VERIFIED` for the page/forms; pilot-via-principal is the practical route.

**(2) Does MoE SSO include delegated data authorization, or identity only?** → **Identity only.** SSO issues a per-SP identity token. Data federation is a separate, closed layer (LRS = vendor→MoE usage push; כספת = MoE→authorized software). No OAuth-style delegated student-data grant exists in any official source. `VERIFIED` (identity) / `NOT VERIFIED→UNLIKELY` (delegated data).

**(3) Free + legal way to get Mashov grades via SSO without a separate password — known today?** → **NO.** Nothing verified and known today. Mashov is a private vendor (Priority); grades originate in מנב"ס and are shown through vendor systems. Community scrapers (pymashov, Home Assistant integration, etc.) all use **Mashov's own web API with username/password + school code (semel)** — undocumented, unofficial, and each carries the school's issued credentials; none uses an SSO-issued token, and none is an approved data channel. Mashov's login page does offer "הזדהות משרד החינוך", but that authenticates *inside Mashov* — the session cannot be transferred to Lumio (per A4). Legal routes to grades data today: (a) MoE vendor approval + interfaces (multi-year horizon), (b) RAMA research data room (research purposes, not a product), (c) student/teacher-initiated manual import. `NOT VERIFIED` for any faster legal path.

**(9) Free server-side sync mechanism that runs while the user's PC is off + exact free quota?** → **Supabase pg_cron (+pg_net) invoking an Edge Function** (official pattern, `schedule-functions`). Quota: **no dedicated cron quota** — it shares the free project's DB compute and the **500,000 Edge-Function invocations/month**; guidance ≤8 concurrent jobs, ≤10 min/job, min interval 1 min (Cron docs). Available on Free: NOT VERIFIED officially, UNLIKELY to be restricted (docs plan-neutral; multiple community free-tier reports). **Caveat:** a *paused* project does not run cron, and a paused project does not auto-resume — so the cron must *prevent* pausing (DB activity), and the warning email must be monitored with manual resume as fallback. **Backup 0-ILS mechanism:** GitHub Actions scheduled workflow — Free plan includes $12/month compute on private repos (~2,000 ubuntu-latest minutes; **free & unlimited on public repos**) (`docs.github.com`, VERIFIED) — e.g., a daily ping to the app to keep the Supabase project active even if the DB cron ever fails.

**(11) What can be live_verified RIGHT NOW vs requires_vendor_approval?**

| Can be live-verified NOW (0 ILS, no MoE approval) | Requires vendor/MoE approval |
|---|---|
| Supabase Free quotas exactly as in B1 (docs verified 2026-11-11; empirically: create project, enable `pg_cron`, schedule a job, watch invocation counter) | Actual **SP registration / IDM connection** (GR_IDM_Team + catalog approval) |
| **pg_cron + pg_net** cron → Edge Function pattern on a Free project (community + docs) | **IDM sandbox** (existence not even confirmed) |
| Cloudflare Pages Free: Direct Upload, 500 builds/mo, unlimited static requests (docs verified 2026-11-11) | **LRS read/write access** (vendor connection via the Monday form; usage data, not grades) |
| Auto-pause behavior: reproduce with an idle Free project (warning email ≈1 week before) | **כספת/interfaces** data feeds (authorized software only; grades/tasks live in מנב"ס) |
| Existence of the MoE SAML endpoint `lgn.edu.gov.il/nidp/saml2/sso` (public) | Any **real student data** (grades, tasks) — all channels gated |
| GitHub Actions scheduled keep-alive (public repo = free) | MoE **privacy/security/accessibility standards** compliance sign-off (required before any MoE-connected product) |

---

# Combined Sources list

**Official MoE / government (education.gov.il, gov.il, mr.gov.il):**
1. `sapakim.education.gov.il/tech/idm` — "הזדהות אחידה - חיבור ספקים חיצוניים... (IDM)" — full text extracted 2026-11-11 (page date not printed). Includes form PDF/DOCX links + GR_IDM_Team@education.gov.il.
2. `sapakim.education.gov.il/tech/lrs/` — "חיבור ספקי חומרי למידה דיגיטליים למאגר נתוני השימוש המרכזי (LRS)" — full text extracted 2026-11-11. xAPI adoption, obligated-vendor rules, hashed-IDs FAQ, Monday.com connection form.
3. `sapakim.education.gov.il/tech/interfaces/` — "שליחת וקבלת מידע מהמשרד לספקים מאושרים - מפרט ממשקים (כספת)" — title + snippet (page date not printed).
4. `sapakim.education.gov.il/tech/` — "ספקים וגופים מפתחים... נדרשים לקבל אישור של משרד החינוך" — snippet (page date not printed).
5. `lgn.edu.gov.il/nidp/saml2/sso?id=EduCombinedAuthUidPwd&option=credential` — live MoE SAML SSO endpoint (page date not printed).
6. `mosdot.education.gov.il/personal/identification` — "הזדהות אחידה" schools-portal page (page date not printed).
7. `mosdotold.education.gov.il/messages/passwords` — password management for "סביבות חיצוניות מאושרות" (page date not printed).
8. `rama.gov.il/questions/data-request` — RAMA data-request process (page date not printed).
9. `mr.gov.il/ilgstorefront/.../attachment/005056BF4DAB1EDB809505726EDCC123` — MoE procurement "מסמכי הזמנה" quoting SAML claims/Protected-Resource requirements (snippet only; full doc unreadable — crawl timeout; tender date NOT VERIFIED).
10. `meyda.education.gov.il/files/edu/accessibility/tech-accessibility-adjustments-1-21.pdf` — MoE accessibility procedure for tech vendors (Jan 2021, references the "tקנים והנחיות טכנולוגיות לספקים" site).
11. `www.gov.il/he/departments/ministry-of-education` — MoE contact/units page (accessed 2026-11-11).

**Vendor / platform docs (supabase.com, developers.cloudflare.com, docs.github.com):**
12. `supabase.com/pricing` — Free plan: 500 MB DB, 50k MAU, 5 GB egress, 1 GB storage, 500k Edge invocations, pause after 1 week inactivity, 2 active projects (accessed 2026-11-11).
13. `supabase.com/docs/guides/platform/billing-on-supabase` — quota table, **Updated Sep 17, 2026**.
14. `supabase.com/docs/guides/functions/limits` — Edge Functions: 150 s wall-clock (Free), 2 s CPU, 256 MB, 100 functions, 100 secrets (accessed 2026-11-11).
15. `supabase.com/docs/guides/platform/free-project-pausing` — 7-day low-activity pause, "few user requests to the database each day", warning+confirmation emails, 1-yr manual restore (accessed 2026-11-11).
16. `supabase.com/docs/guides/functions/schedule-functions` — pg_cron + pg_net → Edge Functions (accessed 2026-11-11).
17. `supabase.com/docs/guides/cron` — "every second to once a year"; ≤8 concurrent jobs, ≤10 min each (search snippet, accessed 2026-11-11).
18. `developers.cloudflare.com/pages/platform/limits/` — **Last updated Sep 5, 2026**: 500 builds/mo, 20k files, 25 MiB, 100 custom domains, functions count against Workers quota.
19. `developers.cloudflare.com/workers/platform/pricing/` — **Last updated Oct 2, 2026**: Free = 100,000 requests/day, 10 ms CPU; "Requests to static assets are free and unlimited"; no egress/bandwidth charges.
20. `developers.cloudflare.com/pages/get-started/direct-upload/` — Direct Upload via Wrangler/drag-drop; no Git; cannot switch to Git later (accessed 2026-11-11).
21. `docs.github.com/en/billing/concepts/product-billing/github-actions` — GitHub Free: $12/month compute private repos; free on public repos (accessed 2026-11-11).

**Community / third-party (lower weight; labeled in text):**
22. `skillhub.360.com/skills/ofek-galim` — third-party portals federating via `lgn.edu.gov.il` SSO (NOT VERIFIED officially; contains leaked credentials — **do not use or reproduce any data from this page**).
23. `github.com/t0mer/pymashov`, `github.com/NirBY/ha-mashov`, `pypi.org/project/pymashov` — unofficial Mashov scrapers using username/password+semel (NOT an approved channel).
24. `apps.apple.com/il/.../id683777271` — Mashov app developer = "MASHOV - IMMEDIACY TRANSPARENCY & CONTROL LTD" (Priority Software).
25. `eddata.live/about`, `eddata.live/terms` — self-declared independent, non-governmental data project.
26. `reddit.com/r/Supabase` (2 threads), `github.com/orgs/supabase/discussions/37405` — pg_cron on free tier in practice (NOT VERIFIED officially).

---

# Blockers & exact next actions

| # | What is missing | Who holds it | One precise request |
|---|---|---|---|
| 1 | **IDM SP registration + sandbox for Lumio** (no public self-service; sandbox unconfirmed) | MoE — GR_IDM_Team (GR_IDM_Team@education.gov.il) | Send the A5 Hebrew inquiry: request SP registration (SAML 2.0/OIDC, ACS placeholder), **explicit sandbox question**, and the school-pilot context with the principal's letter of intent attached. |
| 2 | **MoE product-approval route** (SSO connection is conditional on catalog approval; standards for security/privacy/accessibility apply) | MoE — sapakim vendor-portal process | In the same email, ask: "מה המסלול המינימלי לאישור מוצר לצורך פילוט בית-ספרי בודד, ומהם התקנים החלים (אבטחה, פרטיות, נגישות)?" |
| 3 | **Delegated student-data access** (grades/tasks) — no public channel; only MoE→approved-software or vendor→MoE flows | MoE (IDM/כספת) + RAMA for research | In the same email (A5 item 3), ask whether any mechanism exists for an approved pilot product to receive per-student task/grade data, and what the conditions are. |
| 4 | **Principal sponsorship** for the pilot (required to make the MoE inquiry concrete) | User + the school principal | Obtain a 1-page letter of intent (school name, class size, no student-data storage beyond study content) to attach to the email. |
| 5 | **Official confirmation: pg_cron counts as anti-pause activity on Free; cron available on Free** | Supabase (support / docs) | Empirical check first (user action, 0 ILS): on a Free project run `create extension pg_cron; select cron.schedule('keepalive','* * * * *','select 1');` and observe `cron.job_run_details` + the pause-warning email behavior; if inconclusive, open a Supabase support ticket citing `docs/guides/platform/free-project-pausing` and `docs/guides/cron`. |
| 6 | **Pause-survival design** (paused project ≠ cron running; no auto-resume) | User (architecture) | Implement: daily DB-touching keep-alive (pg_cron), warning-email monitoring, and a GitHub Actions scheduled ping (public repo = free) as the external fallback; document manual-resume runbook. |
| 7 | **Scale guardrails for 1000-student scenario** (egress 5 GB + DB 500 MB) | User (architecture) | Add payload compression + client-side caching and a weekly (not daily) sync option; monitor the Supabase usage page weekly; re-verify free-tier pages at each scale milestone (tiers change). |

**Bottom line:** 0 ILS is achievable today at 10–100 students (verified quotas, pause risk managed). MoE SSO login is reachable via a real, public-but-gated vendor process (IDM forms + GR_IDM_Team) — no sandbox/cost documented. MoE SSO is identity-only: no student data comes with it, and no free/legal SSO-based grades path exists today; the legal grades path is MoE vendor approval (multi-month, minimum) or manual import.
