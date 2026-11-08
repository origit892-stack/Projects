# Draft 03 — n8n Automation Specialist for Business Workflow Automation & API Integrations
**Job:** https://www.upwork.com/freelance-jobs/apply/n8n-Automation-Specialist-for-Business-Workflow-Automation-API-Integrations_~022105779109331591343/
**Their ask:** $30-60/hr, 6+ mo, contract-to-hire; when applying include: a workflow you automated, the manual process it replaced, apps integrated, how you handled errors/edge cases.

---

**A workflow I automated (and run daily):**
Before: an ops loop of finding licensed source material, cutting vertical video, writing attribution lines, uploading — all manual, twice a day, easy to duplicate or forget.
Now: scheduled jobs run the full chain unattended. A dedup ledger means nothing is ever processed twice (idempotency by design), failures raise an alert with the exact run id, and I verify the last run's result on read-back — not by trusting the log. Last run this morning: verified OK.

**Second system — a 124-product e-commerce store I operate via its official API:**
Before: GUI clicking in a panel, one field at a time. Now: GET before every write, read-back verification after, explicit URL rules so a rename never 404s a live product page. Same discipline I'd bring to your CRM syncs: count-asserted failsafes on any bulk operation — if the numbers don't match, the operation aborts instead of "mostly succeeding."

**Apps I integrate routinely:** Gmail/Google APIs, Airtable/Sheets, Slack, webhooks (REST, OAuth, API-key), LLM APIs (OpenAI/Claude/Gemini) inside workflow nodes, Airtable/HubSpot-class CRMs. n8n is my primary canvas; custom Python/JS nodes where n8n alone isn't enough.

**Error handling (your priority #1, mine too):** retry with backoff, failure alerts with execution context, idempotent steps (replayed webhook never double-charges/double-tags), per-system checkpoint/recovery docs, and monitoring that pages me before your customer notices.

**Rate:** $35/hr for our first project — after you've seen a delivery, $45+. Timezone Israel (UTC+2): full European overlap, US Eastern afternoons.

**One question:** of your manual processes, which one is the ugliest right now — the one your team dreads doing every day? Start there and we'll both see the win fast.

---
