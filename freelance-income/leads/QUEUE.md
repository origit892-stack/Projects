# Lead Queue — radar output (drafts for the user to send)
- The 09:00 daily radar cron appends new leads here (deduped by source URL).
- Status: `DRAFT` (ready to send) → `SENT` (user sent) → `REPLIED` (lead responded) → `DEAD`.
- The user's only action: copy the draft, paste into the source platform (their own logged-in account), hit send. ~30s per lead.

## 2026-11-08
*(no leads yet — radar first run 2026-11-09 09:00 IST)*

## 2026-11-09

### L-20261109-01 — FIT A — DRAFT
**Title:** n8n evaluation: autonomous Todoist + Google Calendar planning system (580 tasks, 24.5h cap, HITL)
**Source:** https://community.n8n.io/t/327481/can-n8n-reliably-automate-complex-todois (n8n community · Help me Build, posted 2026-11-08 14:47 UTC)
**Send:** reply in the thread (comment) — OP asked for technical guidance before a trial
**Draft:**
> You're evaluating n8n as plumbing for an autonomous planning system — 580 Todoist tasks, multiple calendars, a 24.5h cap, and 'never silently drop a mandatory task'. I operate exactly this class of system in production.
>
> n8n Cloud works as the orchestrator, but it is not the constraint solver — the rescheduling logic needs a small planner with a database (plan + approvals). For subtasks, recurrences and no-date items, use Todoist's REST API directly — the node drops data. Persistent state, execution logs, error alerts and a heartbeat are what make it 'reliable'.
>
> Proof: a 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state, runs verified daily — plus an unattended publishing pipeline with failure alerts.
> https://origit892-stack.github.io/agent-operator/ · github.com/origit892-stack/Projects
>
> One question: is the 24.5h a hard cap the planner must never breach, or a target it may exceed with your explicit approval? That decides the state machine.

### L-20261109-02 — FIT B — DRAFT
**Title:** [HIRING] Beyond Creator (Toronto agency, 200+ content/mo): Agency Operations & AI Systems Builder, ~15h/wk ongoing
**Source:** https://community.n8n.io/t/327583/hiring-agency-operations-ai-systems-buil (n8n community · Jobs, posted 2026-11-08 20:43 UTC)
**Send:** apply via their Notion form — https://beyondcreator.notion.site/b70000f9cb5141ef94baea3ae0d5d577?pvs=105 (thread replies closed; form is the official channel)
**Draft:**
> You need someone to keep priorities, deadlines and handoffs clear in Notion and Slack, build n8n workflows that don't fall over, and write small apps that survive production. I build and operate exactly this class of system in production.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state; scheduled runs verified OK daily.
> - 124-product store operated end-to-end via its official API — GET before write, read-back after every change.
>
> Approach: I map your content pipeline (Notion ↔ Slack ↔ n8n) and send back the plan + fixed price + done-definition in 24-48h. Ongoing part-time works as a care plan on top of the first build.
>
> https://origit892-stack.github.io/agent-operator/ · github.com/origit892-stack/Projects
>
> One question: which is the biggest leak today — deadlines slipping in Notion, n8n workflows failing silently, or the small apps? I'll build that one first.

### L-20261109-03 — FIT B — DRAFT
**Title:** r/automation: broker re-keying 6-8 carrier quotes/client into a PowerPoint proposal deck, asks where to start
**Source:** https://www.reddit.com/r/automation/comments/1xqz7p9/getting_carrier_quotes_into_a_proposal_deck_where/ (r/automation, posted 2026-11-08 14:06 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You're re-typing six to eight carrier quotes per client — the same 15 points, one slide per policy type — and Copilot is 'ok but not consistently enough to rely on'. I build exactly this class of workflow: extract from the quotes, normalize into a fixed schema, render the deck.
>
> Proof you can check today:
> - 124-product store operated end-to-end via its official API — GET before write, read-back after every change.
> - Unattended publishing pipeline running twice daily with dedupe ledger and failure alerts.
>
> Approach: I map your quote formats and the deck template, send back the plan + fixed price + done-definition in 24-48h. Built with error handling and logging — no re-typing after the first run.
>
> https://origit892-stack.github.io/agent-operator/ · github.com/origit892-stack/Projects
>
> One question: how do the carrier quotes arrive — PDFs, email bodies, or a portal export? That decides which extraction path I build first.

### L-20261109-04 — FIT B — DRAFT
**Title:** r/smallbusiness: family plumbing & heating business wants online booking to replace the hand-written schedule
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xri1wa/online_booking/ (r/smallbusiness, posted 2026-11-09 04:13 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You're hand-writing the schedule for your family's plumbing and heating business and want online booking — I build and operate exactly this class of system in production: customers book 24/7, the schedule fills itself, and follow-ups run without you.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state; scheduled runs verified daily.
> - Unattended publishing pipeline running twice daily with failure alerts.
>
> Approach: I map your job types, working hours and how customers reach you, then send back the plan + fixed price + done-definition in 24-48h. Timeline: ~5 days, with handover docs and a walkthrough video.
>
> https://origit892-stack.github.io/agent-operator/ · github.com/origit892-stack/Projects
>
> One question: how do customers reach you today — phone calls, texts, or a web form? That decides whether the first build is a phone/text AI responder or a web booking flow.

## 2026-11-10

### L-20261110-01 — FIT A — DRAFT
**Title:** r/AI_Agents: AI agent that calls insurance companies for HIPAA-compliant verification of benefits (same 15 questions every time → sheet)
**Source:** https://www.reddit.com/r/AI_Agents/comments/1xs9iai/ai_agents_using_hippa_info/ (r/AI_Agents, posted 2026-11-10 01:04 UTC) — same OP cross-posted to https://www.reddit.com/r/automation/comments/1xs9hda/ai_agent/ (reply ONCE, primary thread = r/AI_Agents)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You want an AI agent that calls insurance companies, asks the same 15 verification-of-benefits questions every time and puts the answers on a sheet — HIPAA-clean and cheap per minute. I build and operate this class of unattended agent system in production.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state; scheduled runs verified OK daily.
> - Unattended publishing pipeline running twice daily with a dedupe ledger and failure alerts.
>
> Build: a voice front that navigates hold menus, runs your 15-question script, extracts answers into a fixed schema, writes the sheet row, and escalates anything ambiguous to you. HIPAA side: BAA-covered telephony and model providers; PHI stays in your accounts.
>
> https://origit892-stack.github.io/agent-operator/ · github.com/origit892-stack/Projects
>
> One question: how do payer phone numbers and member details reach you today — a pasted spreadsheet, or a system I could pull from via API? That decides how I wire the call trigger.

### L-20261110-02 — FIT B — DRAFT
**Title:** r/smallbusiness: Estonian company automating Profit First (5/50/15/30 splits) on Revolut Business — hitting Revolut rule limits, open to integrations/alternatives
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xs3fm0/has_anyone_successfully_automated_profit_first/ (r/smallbusiness, posted 2026-11-09 20:53 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You're setting up Profit First on Revolut Business for your Estonian company and hitting the wall — one income-sorting rule per source account, and transfers between your own accounts don't trigger rules, so the 5/50/15/30 split stays manual. I build exactly this class of workflow: trigger, route, split, verify.
>
> Proof you can check today:
> - 124-product store operated end-to-end via its official API — GET before write, read-back after every change.
> - Unattended publishing pipeline running twice daily with failure alerts.
>
> Approach: I map the Revolut rules and API against your allocation flow, then send back the plan + fixed price + done-definition in 24-48h — including whether to fix it inside Revolut, automate the splits with scheduled transfers, or use a reliable alternative an Estonian company can open.
>
> https://origit892-stack.github.io/agent-operator/ · github.com/origit892-stack/Projects
>
> One question: are subcontractor costs known before the client money lands, or do they arrive after? That decides the order of the splits.

### L-20261110-03 — FIT B — DRAFT
**Title:** r/AI_Agents: wants a lookup agent — input name + postal code, agent scours the internet for property owners' phone numbers
**Source:** https://www.reddit.com/r/AI_Agents/comments/1xs52yf/ia_in_my_job/ (r/AI_Agents, posted 2026-11-09 21:57 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You're typing names and addresses into one website after another to find property owners' phone numbers, and you want to input a name + postal code and have an agent scour the internet and come back with the contact. I build exactly this class of system — a lookup pipeline that searches, extracts and verifies, instead of manual one-by-one hunting.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state; scheduled runs verified OK daily.
> - 124-product store operated end-to-end via its official API — GET before write, read-back after every change.
>
> Approach: I map the sources you check today and the output format you need, then send back the plan + fixed price + done-definition in 24-48h.
>
> https://origit892-stack.github.io/agent-operator/ · github.com/origit892-stack/Projects
>
> One question: how many lookups a day — tens or hundreds? That decides whether I build an on-demand agent or a batch pipeline.

## 2026-11-11

### L-20261111-01 — FIT C — DRAFT
**Title:** n8n [HIRING]: multi-channel marketing attribution + automated lead engine (one-time project, Indonesia)
**Source:** https://community.n8n.io/t/328000/hiring-freelancer-for-custom-ai-powered-marketing-attribution-lead-automation-pipeline-project (n8n community · Jobs, posted 2026-11-11 04:42 UTC)
**Send:** ⚠ thread replies CLOSED — OP's channel is email: oktarina.nurhayati@gratyo.id (user sends from their own account)
**Draft:**
> You're building a multi-channel attribution + lead engine — Meta/TikTok/LinkedIn/YouTube into BigQuery/Supabase via self-hosted n8n, AI schema standardization and Hot/Warm/Cold scoring, phone/email dedup with round-robin rotator, multi-touch journey logging, Mekari Qontak/WAHA WhatsApp, and a Looker Studio dashboard. That's exactly the class of system I design and operate in production.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state; scheduled runs verified daily.
> - 124-product store operated end-to-end via its official API — GET before write, read-back after every change.
>
> Approach: I map the ad APIs + your lead form, send back the plan + fixed price + done-definition in 24-48h. Timeline: ~20 days.
>
> One question: does the Bahasa Indonesia requirement apply to the customer-facing WhatsApp copy and dashboard, or to project communication? That decides how I scope the deliverable.

## 2026-11-12

### L-20261112-01 — FIT B — DRAFT
**Title:** r/zapier: home-cleaning ops — WhatsApp→CRM via Zapier: one booking = 25 tiny notes, eats tasks; wants wait-and-group note
**Source:** https://www.reddit.com/r/zapier/comments/1xtsdfe/spent_the_weekend_getting_whatsapp_chats_into_our/ (r/zapier, posted 2026-11-11 20:15 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> One booking turning into 25 tiny notes and eating your Zapier tasks — that's what you're describing: every webhook message is one action, one task. The fix has two halves: a quiet window, and extraction.
>
> I build and operate this class of pipeline in production: a small webhook service collects the chat, waits ~1 hour of silence, then an LLM writes exactly what your boss wants — quote requested?, date, booked? — as ONE structured CRM note. Runs on your infra, flat cost, no per-message tax, replayed webhooks never double-write.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents, checkpointed state; runs verified daily.
> - Unattended publishing pipeline running twice daily with a dedupe ledger and failure alerts.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which CRM are you writing the notes to — HubSpot, GoHighLevel, or something else? That decides the write path for the grouped note.

### L-20261112-02 — FIT C — DRAFT
**Title:** r/automation [HIRING]: Freelance AI Workflow Engineer (SaaS marketing agency, Delhi, India) — $15 per completed workflow
**Source:** https://www.reddit.com/r/automation/comments/1xtfpf1/hiring_freelance_ai_workflow_engineer_developer/ (r/automation, posted 2026-11-11 11:46 UTC)
**Send:** reply in the thread (post also says DMs open) — ⚠ Reddit karma gate pending (reddit/REDDIT.md); pay is $15/workflow — user decision likely reject
**Draft:**
> Custom AI workflows in Python/JS with LLM APIs and n8n, tested and delivered project-based — that's the scope I work in, day to day. One number doesn't fit: $15 per completed workflow is below my floor. My rate is $300 fixed per completed, tested, documented workflow — you get a working deliverable plus handover notes. If you batch several workflows at once, I'll quote a package price.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state; scheduled runs verified daily.
> - Unattended publishing pipeline with a dedupe ledger and failure alerts.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many workflows a week does the agency typically ship — a couple, or 20+? That decides whether a batch price is worth quoting.

### L-20261112-03 — FIT C — DRAFT
**Title:** n8n community: two weekly local-events newsletters (scraped websites + Instagram) — move from ChatGPT to n8n server?
**Source:** https://community.n8n.io/t/328205/create-newsletters-with-n8n (n8n community · Help me Build, posted 2026-11-11 17:53 UTC)
**Send:** reply in the thread (open, replies enabled)
**Draft:**
> Two weekly newsletters, and you don't want to start paying the ChatGPT API for what your subscription already does. Short answer: pennies either way (a few thousand tokens per run); for zero cost, Gemini's free tier or DeepSeek generate the HTML just as well.
>
> If I moved it: start with the website-scraping one. Cron trigger → fetch the page as text → model extracts the events and writes the HTML → push it to your email tool as a DRAFT via its API, so you still review before send. Keep the Instagram one on ChatGPT until it runs clean.
>
> I operate this class of unattended pipeline in production (twice daily, with failure alerts); I can wire the first one for you, ~$300 fixed.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which email software are you pasting into — Mailchimp, Brevo, or something else? That decides the API push node.
### L-20261112-04 — FIT C — DRAFT
**Title:** n8n [HIRING] (thread CLOSED): Founding n8n Builders for US small-business work — AutoMatch marketplace
**Source:** https://community.n8n.io/t/328131/hiring-founding-n8n-builders-for-us-small-business-client-work-freelance-remote (n8n community · Jobs, posted 2026-11-11 14:47 UTC)
**Send:** ⚠ THREAD CLOSED — draft doubles as builder application via useautomatch.com; verify platform fee cut before committing (zero-cost rule)
**Draft:**
> I'd like to join as a builder. I design and operate AI automations for small businesses in production — missed-call handling, lead follow-up, appointment booking — n8n-based, with error workflows and failure alerts, and I explain every system to non-technical owners in plain language.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents, checkpointed state; runs verified daily.
> - 124-product store operated end-to-end via its official API — GET before write, read-back after every change.
> https://origit892-stack.github.io/agent-operator/
>
> One question before I commit: what percentage does the platform hold on each completed project, and when does a builder's payout release after client approval?
