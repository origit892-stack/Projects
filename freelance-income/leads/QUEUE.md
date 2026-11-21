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

## 2026-11-13

### L-20261113-01 — FIT B — DRAFT
**Title:** n8n Telegram bot for a fitness studio — class scheduling, booking/reschedule/cancel, multi-room, double-booking prevention, reminders, roles
**Source:** https://community.n8n.io/t/328331/looking-for-an-n8n-telegram-bot-workflow-for-class-scheduling-booking (n8n community · Help me Build, posted 2026-11-12 12:01 UTC)
**Send:** reply in the thread (open, replies enabled) — OP asked for a template / GitHub / architecture
**Draft:**
> Your Telegram bot for a fitness studio — schedule, book/reschedule/cancel, multiple rooms, double-booking prevention, reminders, role-based access — is exactly the class of n8n system I build and operate in production.
>
> Architecture I'd use: all state (classes, rooms, bookings, users+roles) in PostgreSQL, not Google Calendar — Calendar can't hold room+role+booking metadata. Double-booking guard: one SQL transaction with a unique (slot, room) constraint — the database rejects the conflict, the bot never has to. Reminders: a scheduled check 24h/1h before class → Telegram to booked members + trainers. Roles enforced per command in the DB.
>
> Proof you can check today: a 24/7 multi-agent ops desk — 71 specialized agents, checkpointed state, runs verified daily. A 124-product store operated end-to-end via its official API.
> https://origit892-stack.github.io/agent-operator/
>
> One question: who enters the class schedules — the trainers, or are they already in Google Calendar? That decides which one is the source of truth.

### L-20261113-02 — FIT B — DRAFT
**Title:** r/AI_Agents: AI that watches saved Instagram Reels and ranks business ideas 1–10 with explanation + one concrete action
**Source:** https://www.reddit.com/r/AI_Agents/comments/1xv0v97/is_there_an_ai_that_watches_my_saved_instagram/ (r/AI_Agents, posted 2026-11-13 06:46 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You save loads of Reels on marketing, AI tools and business ideas — you want each rated 1-10 against the projects you actually run, the score explained, plus one concrete action. I build exactly this class of pipeline in production.
>
> Honest constraint first: Instagram has no API for saved Reels. The setup that works: share the Reel link into a Sheet or Notion (one tap); the pipeline transcribes it (Whisper), scores it against your goals and constraints with a fixed rubric — relevance, feasibility, cost, impact — and writes back score, reasoning, one next action. Not a summary.
>
> Proof: an unattended publishing pipeline running twice daily with a dedupe ledger and failure alerts; a 24/7 multi-agent ops desk — 71 agents, checkpointed state.
> https://origit892-stack.github.io/agent-operator/
>
> One question: should it score everything you save, or only the Reels you explicitly flag? That decides whether it's a nightly batch or a per-Reel trigger.

### L-20261113-03 — FIT C — DRAFT
**Title:** r/automation: automating small purchases — agent finds item + checkout works, payment is the blocker (Oobit "Agent Pay" one-time virtual cards)
**Source:** https://www.reddit.com/r/automation/comments/1xuuj3d/anyone_managed_to_get_an_ai_agent_to_actually/ (r/automation, posted 2026-11-13 01:16 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> The payment part is where this breaks, and your instinct is right: a single-use virtual card with a hard spend cap is the right shape — worst case is one bad order. The part nobody mentions is 3DS: many merchants throw a one-time-code challenge at checkout, and the agent stalls there before the card even matters.
>
> The sequence that works: pre-test the exact checkout in a dry run to find which merchants throw 3DS; the agent picks the item and reaches checkout, then stops and pings you for one-tap approval; it pays with the capped one-time card, verifies the order confirmation, logs it.
>
> I build and operate this class of HITL agent system in production. If you want it built: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which merchant do you buy from most — that's the one to 3DS-test first.

## 2026-11-14

### L-20261114-01 — FIT B — DRAFT
**Title:** n8n runtime-based HVAC maintenance reminders — per-customer runtime totals from smart thermostats (Ecobee/Honeywell), 300-400h triggers, reset via technician webhook, PSEG rebate nudges
**Source:** https://community.n8n.io/t/328494/hvac-company-question-high-efficiency-rebates-n8n-workflow-to-remind-pseg-customers-about-upgrades-and-service (n8n community · Help me Build, posted 2026-11-13 12:27 UTC)
**Send:** reply in the thread (open, replies enabled — verified 2026-11-14)
**Draft:**
> Runtime-based reminders is the right design — your three questions have clean answers:
>
> 1. Per-customer total: a database table, one row per customer (counter + last reset). Static data can't survive overlapping runs, and a webhook workflow elsewhere can't touch it. On n8n Cloud: Data Tables.
> 2. Reset: the scheduling-form webhook -> one transaction: zero the counter, log the visit, timestamp it. Idempotent on job ID so a resubmitted form can't double-reset.
> 3. Token refresh: keep Ecobee/Honeywell credentials in n8n's credential store; a small scheduled workflow refreshes ahead of expiry.
>
> I build and operate this class of n8n system in production — 24/7 multi-agent ops desk (71 agents, checkpointed, verified daily), unattended pipeline with failure alerts. Happy to build this one; fixed quote after a quick mapping.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which brand do most customers actually run — Ecobee or Honeywell? That decides which runtime API I test first.

### L-20261114-02 — FIT C — DRAFT
**Title:** r/n8n: family 'tech person' asked to pick a voice AI for sister's home-services company drowning in phone calls
**Source:** https://www.reddit.com/r/n8n/comments/1xvd98e/how_do_you_even_pick_a_voice_ai_for_a_small/ (r/n8n, posted 2026-11-13 17:00 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Your sister's home-services company drowning in phone calls — what actually matters when picking a voice AI:
>
> 1. Answer rate — does it pick up on the 2nd-3rd ring after hours? Test on real missed calls, not a demo.
> 2. The 2-3 outcomes a call must achieve: book? callback? emergency dispatch? The system is built around those.
> 3. Human escalation — upset caller: live transfer, or a flagged text to her phone?
> 4. Cost — per-minute; a busy line burns hundreds of minutes a month.
>
> I operate this class of unattended agent system in production: a 24/7 multi-agent ops desk (verified daily) and a publishing pipeline with failure alerts. If she wants it set up: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many calls a day is she missing, and what do callers need most on the line — booking, pricing, or a callback?

### L-20261114-03 — FIT C — DRAFT
**Title:** r/automation: insurer's test-automation lead — which AI testing tools give auditable step-by-step run reports (screenshots + failure analysis) that internal audit accepts
**Source:** https://www.reddit.com/r/automation/comments/1xvibii/which_ai_testing_tools_give_auditable_step_by/ (r/automation, posted 2026-11-13 20:10 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You've hit the core issue: auditors don't accept the agent's explanation — they accept a deterministic record. My rule in production: every step logged before the model's commentary — exact input, tool call, expected vs actual, screenshot hash, timestamp; the LLM's 'reasoning' is an attachment, never the evidence.
>
> The pattern that passes audit: an append-only run log (one signed/timestamped line per step), screenshots keyed to step IDs, PASS/FAIL from assertions, not the model. AskUI's report is closest — what to demand from any vendor is the deterministic core under it.
>
> I run this in production: a 24/7 multi-agent ops desk (71 agents, checkpointed state, execution logs verified daily) plus an unattended pipeline with failure alerts. I can build that evidence layer for your agent runs.
> https://origit892-stack.github.io/agent-operator/
>
> One question: does your audit side require an immutable run log (append-only/signed), or is a timestamped archive with access control enough?

### L-20261114-04 — FIT C — DRAFT
**Title:** r/AI_Agents: planning a team of 7 AI agents to automate the entire software QA lifecycle (BRD/SDD analysis, test generation, execution, automation) — looking for suggestions
**Source:** https://www.reddit.com/r/AI_Agents/comments/1xvhhm6/i_want_to_build_a_team_of_7_ai_agents_to_automate/ (r/AI_Agents, posted 2026-11-13 19:38 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Your 7-agent QA split (BRD -> SDD -> strategy -> execution -> automation) is solid. From running similar systems in production:
>
> 1. Give every agent a contract: fixed input/output schemas + a done-definition. Multi-agent systems die at the seams, not the models — prose between agents.
> 2. One shared artifact store, not message passing: each agent reads/writes structured artifacts (traceability table, test-case JSON, execution reports); the orchestrator only routes.
> 3. Traceability is what clients pay for: requirement ID -> test case ID -> execution result, in a table from agent 3 onward.
>
> I operate this class of system in production: a 24/7 multi-agent ops desk — 71 specialized agents, checkpointed state, runs verified daily. Happy to review the spec and send back plan + fixed price.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what's the source of truth for your BRDs/SDDs — Confluence, SharePoint, or PDF drops? That decides the intake design.

## 2026-11-15

### L-20261115-01 — FIT A — DRAFT
**Title:** r/n8n: n8n Cloud (no VM) — extract SLAs, penalties + tech requirements from 30-page tenders with messy tables; Textract/LlamaParse/vision API? cost + security approval
**Source:** https://www.reddit.com/r/n8n/comments/1xwox45/can_n8n_handle_tender_documents_on_its_own_with/ (r/n8n, posted 2026-11-15 06:58 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> n8n Cloud, no VM, pulling SLAs, penalties and tech requirements out of 30-page tenders — the realistic route is a parse/vision API from an HTTP Request node: Textract handles clean tables but struggles with messy merged cells; LlamaParse has the best messy-table accuracy; a plain vision LLM fed the page as an image is cheapest to start and fine if you need structured fields, not perfect layout. Per-tender cost is cents to ~$0.50 — trivial vs the analyst time it replaces. Security usually asks: data classification, DPA with the provider, no-retention/no-training, access logs, redaction before storage.
>
> I build and operate this class of document pipeline in production: a 24/7 multi-agent ops desk (71 agents, checkpointed state, verified daily) and an unattended pipeline with a dedupe ledger + failure alerts. If you want it wired end-to-end — intake → parse → structured schema → gap alerts: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what does the output have to look like — a structured JSON per tender, or a filled comparison sheet for humans? That decides which parse path I'd build first.

### L-20261115-02 — FIT B — DRAFT
**Title:** r/automation: 17-person startup, non-technical — wants recurring ops handled "without babysitting or a complicated setup"; asks what people actually used
**Source:** https://www.reddit.com/r/automation/comments/1xw53g3/how_to_create_an_ai_agent_that_actually_does/ (r/automation, posted 2026-11-14 15:27 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> A 17-person startup that just wants recurring ops handled without babysitting — skip the tool tour; that rabbit hole is real. The pattern that actually holds: pick the single most-recurring ops process (not three) and build it as one workflow with three guarantees — persistent state so nothing is dropped, error alerts when something fails, and a human-approval queue for anything customer-facing. Everything else is decoration until that one runs for two unattended weeks.
>
> I operate exactly this class of system in production: a 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state, scheduled runs verified daily — plus an unattended pipeline with a dedupe ledger and failure alerts.
>
> If you'd rather have it built than figured out: I map the process and send back the plan + fixed price + done-definition in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what's the single most-recurring ops task right now — invoice chasing, onboarding, status updates, data entry? I'd start there.

### L-20261115-03 — FIT B — DRAFT
**Title:** r/smallbusiness: retail business (POS) with inventory off + manual EOD low-stock email lists, items getting missed before the holidays
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xwm1yu/advice_needed_inventorylow_stock_monitoring/ (r/smallbusiness, posted 2026-11-15 04:13 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Inventory off the POS, manual EOD lists, items getting missed before the holidays — the fix is to stop making lists and start getting alerts. The setup: pull inventory levels from the POS daily (API or its nightly export), compare against a per-item low-stock threshold, and send one digest — what's low, what's out, suggested reorder counts. A scheduled cycle count on your 10 most-moved items catches the receiving errors while they're still small.
>
> I build and operate this class of unattended pipeline in production: a 24/7 multi-agent ops desk (71 agents, checkpointed state, verified daily) and a publishing pipeline with failure alerts — the same shape: scheduled pull, check, alert, log.
>
> I can build this for you: plan + fixed price + done-definition in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which POS are you on, and does it have an API or a nightly CSV export? That decides whether the pull is live or once-a-day.

### L-20261115-04 — FIT B — DRAFT
**Title:** r/smallbusiness: painting business — leads get quoted fast but are ghosted after slow follow-ups; "what are you using to help follow up on estimates?"
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xwjfic/estimate_follow_ups/ (r/smallbusiness, posted 2026-11-15 01:54 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You give quotes fast but the follow-up drags and leads ghost — on painting jobs, timing is the whole game: the first follow-up wins most of the "we're thinking about it" pile, and a second touch at 3-5 days wins more. The system: every estimate gets logged with a date; day-1 "any questions?" touch; day-4 value-add ("here's a start timeline for this week"); day-9 close-the-loop; anything still silent goes to a short call list for you.
>
> I build and operate this class of follow-up system in production — a 24/7 multi-agent ops desk (71 agents, checkpointed state, runs verified daily) and an unattended pipeline with failure alerts. I can wire it to how you actually quote: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: where do your estimates live today — paper, texts, or a CRM? That decides whether the first build starts with logging or with the follow-up sequence alone.

### L-20261115-05 — FIT C — DRAFT
**Title:** r/smallbusiness (Canada): "Help with receipts, I'm drowning" — too many random paper receipts, needs a system
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xwivhu/help_with_receipts_im_drowning/ (r/smallbusiness, posted 2026-11-15 01:26 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Drowning in paper receipts — the system is simple: photograph them as they come in (camera roll works), and a nightly job extracts date, merchant, amount and category into one sheet or your bookkeeping tool. Nothing is "random" anymore — the sheet is the system, and month-end becomes one export instead of a shoebox.
>
> I build and operate this class of extraction pipeline in production: a 24/7 multi-agent ops desk (71 agents, checkpointed state, verified daily) and an unattended pipeline with a dedupe ledger and failure alerts — same pattern: collect, extract, verify, log.
>
> I can build the full receipt-to-sheets/bookkeeping flow: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what do the receipts end up feeding — a bookkeeper, QuickBooks, or a personal ledger? That decides the output format.

## 2026-11-16

### L-20261116-01 — FIT B — DRAFT
**Title:** r/smallbusiness: online tutoring company — parents message evenings/weekends about the software; site chatbot helps a bit but reschedule requests go unanswered; can't justify a support hire at low unpredictable volume
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xx93xv/question_about_support_queries/ (r/smallbusiness, posted 2026-11-15 22:46 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Parents messaging evenings and weekends — most questions quick, but they still need answering, and reschedules are exactly what your site chatbot misses. When volume is low and unpredictable, the answer is rarely a hire: one message endpoint (WhatsApp, where they already write) that answers your software FAQ from your help docs, plus a 'move lesson' flow — parent picks a new slot, the agent checks it against the calendar, updates the booking, both sides get a confirmation. Low-confidence messages land in one morning inbox for you. You never cover a shift again.
>
> I build and operate this class of unattended system in production — a 24/7 multi-agent ops desk (71 agents, checkpointed state, runs verified daily) and an unattended pipeline with failure alerts.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what runs your lesson scheduling today — a calendar, a SaaS, or a spreadsheet? That decides whether reschedules update automatically or come back for your confirmation.

### L-20261116-02 — FIT C — DRAFT
**Title:** r/LLMDevs: perfume-comparison app — can't reliably extract BHD prices from local Bahrain store sites; tried 7 scraping stacks + LLM fallback, still misses
**Source:** https://www.reddit.com/r/LLMDevs/comments/1xx1uxv/cant_reliably_get_local_store_prices_in_bahrain/ (r/LLMDevs, posted 2026-11-15 17:50 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Prices are where it falls apart — and you've already tried the generic pipeline the hard way: JSON-LD/OpenGraph/microdata, Shopify/Woo JSON, LLM fallback, plus seven scraping stacks. The pattern that actually holds when the store set is small (and Bahrain's is): stop detecting, start specializing. One hand-written extractor per store — twenty stores = twenty tiny functions that beat a hundred generic detectors — each with a price-change canary that alerts you the day a store redesigns. For pasted links or bottle photos: match the input against your own catalog first, then run that SKU's extractors — no open-web search at runtime. LLM stays the last resort, with a strict schema and a confidence threshold; every miss gets logged as the next canary's training data.
>
> I operate this class of unattended extraction pipeline in production — publishing twice daily with a dedupe ledger and failure alerts. Happy to build the store-adapter layer for you.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many distinct store sites are in the corpus — under 20, or hundreds? That decides per-store adapters vs a generic detector.

### L-20261116-03 — FIT C — DRAFT
**Title:** r/smallbusiness: traveling makeup artist, first business — missed a Zoom with a potential client; tracking clients/calls/payments across planner + notebook + Google Docs
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xxf4lv/tips_on_keeping_all_info_organized/ (r/smallbusiness, posted 2026-11-16 03:34 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You missed a Zoom call with a potential client because the planner + notebook + Google Docs mix can't keep up — the fix isn't more discipline, it's one source of truth. One sheet (or Notion) with three small tables: clients (who, service, how they want to be reached), calls (date, link, what they wanted), payments (paid vs owed). Then two automations: a reminder fires before every scheduled call, and a weekly digest tells you who owes what and who hasn't been followed up with. The planner stays as backup; the sheet is the system.
>
> I build and operate this class of unattended pipeline in production — a 24/7 multi-agent ops desk (71 agents, checkpointed state, verified daily) and a publishing pipeline with failure alerts. I can set this up for you end-to-end: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how do clients pay you today — Zelle, PayPal, card, or a mix? That decides which payment ledger I build first.

### L-20261116-04 — FIT C — DRAFT
**Title:** r/n8n: experimenting with Meta Muse, wants to pair it with a phone agent that handles calls (not just chat) — asks what's actually working
**Source:** https://www.reddit.com/r/n8n/comments/1xwzyma/what_are_the_most_useful_phone_agents_to_use_with/ (r/n8n, posted 2026-11-15 16:36 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Pairing Muse with something that actually takes calls — what matters when picking the phone-agent layer:
>
> 1. Pickup — does it answer on the 2nd-3rd ring, or bounce to voicemail mid-test?
> 2. Barge-in — can a caller interrupt, or does the agent monologue? On real calls this is make-or-break.
> 3. Handoff — human needed: live transfer, or a flagged message with full context?
> 4. Per-minute cost — a busy line burns hundreds of minutes a month.
>
> Purpose-built voice platforms win on 1-3; a general AI agent only holds up on 4.
>
> I operate this class of unattended agent system in production (24/7 multi-agent ops desk, verified daily). If you want the whole thing wired — Muse + voice front + handoff: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what should a successful call end in — a booking, a callback request, or a message to a human? That decides which layer is worth testing first.

## 2026-11-17

### L-20261117-01 — FIT B — DRAFT
**Title:** r/AI_Agents: supplier ordering — 7 suppliers, 500+ SKUs, days-of-supply floor → full truckloads → order forms; "would an AI agent make quick work of this?"
**Source:** https://www.reddit.com/r/AI_Agents/comments/1xy86e3/supplier_ordering/ (r/AI_Agents, posted 2026-11-17 02:04 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> You want Excel to take over ordering from your 7 suppliers — 500+ SKUs, days-of-supply floors, full semi truckloads, order forms. Honest answer: an AI agent is overkill here — a deterministic pipeline does it faster and never drifts.
>
> The build: your inventory report in → rules engine computes per-SKU reorder quantities from each supplier's lead time and your days-of-supply floor → bin-packs into full truckloads per supplier → writes the order forms in your exact layout → flags the near-empty trucks for a human look.
>
> Proof you can check today:
> - 24/7 multi-agent ops desk — 71 specialized agents, checkpointed state, runs verified daily.
> - Unattended pipeline publishing twice daily with a dedupe ledger and failure alerts.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how does the inventory report arrive today — an export from your system, or a sheet someone maintains? That decides where the pull starts.

### L-20261117-02 — FIT B — DRAFT
**Title:** r/smallbusiness: 15-person ecommerce — order checks, invoice matching, ticket follow-ups eat the week; tried Codex + others, syncs break; maintenance + cost worries
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xyahsx/running_a_business_is_starting_to_feel_like_a/ (r/smallbusiness, posted 2026-11-17 03:58 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Orders, supplier payments, invoices — "there's always something to check, match or follow up on," and the tools you've tried stop halfway and still need manual checking. The fix is to stop automating three things at once:
>
> 1. One flow first: invoice matching is usually the cleanest win — pull the supplier invoice, match it against order and receipt, flag only the mismatches. Your team stops checking everything and only checks what doesn't match.
> 2. Maintenance is the product: every system I ship runs unattended in my own 24/7 production first — error alerts, checkpointed recovery, written runbook — and the ongoing care is a small fixed monthly plan, not an in-house tech team.
> 3. Cost: it runs on your own API keys, pay-per-use — for this volume, low dollars per day, no per-seat subscription.
>
> Proof: a 24/7 multi-agent ops desk (71 agents, checkpointed, verified daily); an unattended pipeline with failure alerts.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which of the three — order checks, invoice matching, or ticket follow-ups — eats the most hours per week? I'd build that one first.

### L-20261117-03 — FIT B — DRAFT
**Title:** r/smallbusiness: solo mobile mechanic — separate advertising phone line + after-hours "robo secretary" that screens calls and gathers customer info
**Source:** https://www.reddit.com/r/smallbusiness/comments/1xy5vin/small_business_phone_line/ (r/smallbusiness, posted 2026-11-17 00:16 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> A separate advertising line plus "a robo secretary to screen calls and gather customer information" — for a one-man mobile mechanic that's the right shape, and the robo part is what stops after-hours customers going to whoever answers.
>
> The phone: keep it simple — one VoIP business number on your existing phone. Skip the dumb phone: customers will want to text a photo of the leak or the engine.
>
> The robo: after hours (or while you're under the hood), an AI receptionist answers on the 2nd–3rd ring, confirms the job — vehicle, what's wrong, address, urgency — books a slot or a morning callback, and texts you the summary. Anything urgent or unclear goes straight to your phone.
>
> Proof you can check today: a 24/7 multi-agent ops desk (71 agents, checkpointed state, runs verified daily); an unattended pipeline with failure alerts.
> https://origit892-stack.github.io/agent-operator/
>
> One question: when a customer calls after hours, what's the ideal outcome — a booked service slot, a morning callback, or just the details captured? That decides how much the booking flow has to do.

### L-20261117-04 — FIT B — DRAFT
**Title:** r/automation: recruiting sourcing agent — needs structured people data (title, past employers + dates, location, work email) at thousands of lookups/day; Exa too weak
**Source:** https://www.reddit.com/r/automation/comments/1xximwz/whats_a_good_exa_alternative_for_people_data/ (r/automation, posted 2026-11-16 06:52 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Filtering "past company with dates" by stuffing it into a semantic query string is the failure mode you've hit — Exa's work-history fields are sparse, so the search returns current Stripe people and people who merely wrote about Stripe. At a few thousand lookups a day, don't let the search layer do structured filtering:
>
> The build: a fixed source stack, each with a hand-written extractor into one schema — current title, past companies with dates, location, work email. Your agent then filters the schema in code (deterministic, cheap, testable); the LLM only touches the ambiguous rows. Rate-limit per source, cache by person, and log which source provided each field — weak sources get swapped out on evidence, not guesswork.
>
> Proof: an unattended extraction pipeline running twice daily with a dedupe ledger and failure alerts; a 24/7 multi-agent ops desk (71 agents, checkpointed state).
> https://origit892-stack.github.io/agent-operator/
>
> One question: is the few-thousand-a-day a one-time list or a rolling pool — and which source does your team currently hand-verify against? That decides the schema's ground truth.

### L-20261117-05 — FIT C — DRAFT
**Title:** r/AI_Agents: production voice agent — 15 metrics all green, customers still complain, hundreds of calls/day; how to find failure modes no metric covers
**Source:** https://www.reddit.com/r/AI_Agents/comments/1xydhou/our_voice_agent_passes_every_metric_we_wrote_and/ (r/AI_Agents, posted 2026-11-17 06:44 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> All-green metrics with live complaints means you're measuring what you wrote, not what confuses the customer. For hundreds of calls a day, the layer that scales past listening one-by-one:
>
> 1. Sample both directions: a few random "green" calls plus every call tied to a complaint, daily.
> 2. Transcribe, then run an open-ended critic — not a rubric: "what in this call could have frustrated the caller?"
> 3. Cluster the free-text notes nightly; a recurring new phrase becomes a metric candidate — you discover failure modes from the language of complaints instead of guessing them.
> 4. Weekly: the top-5 confusion patterns with timestamps into the recordings, so your team listens to five clips, not five hundred calls.
>
> I run this class of audit layer in production (checkpointed multi-agent desk, execution logs verified daily). Happy to wire it against your call data — plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: do your recordings and your complaint tickets already share a call ID, or is matching them manual today? That decides how much of step 1 is plumbing.

### L-20261117-06 — FIT C — DRAFT
**Title:** r/AI_Agents: voice customer queries → end-of-day top-10 common points summary ("can we create a customer based ai system")
**Source:** https://www.reddit.com/r/AI_Agents/comments/1xy6vxs/solve_customer_problem/ (r/AI_Agents, posted 2026-11-17 01:03 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Customers send their problems by voice, and at end of day you get the top 10 common points — yes, buildable, and as your thread's comments say: a pipeline, not a full agent.
>
> The shape: each call → transcription → one short structured note per call (topic tag + two-line summary) → a nightly job clusters the tags and counts distinct customers per topic, so one frustrated caller reporting the same issue five times counts once → your top-10 sheet with a redacted example quote per row.
>
> The trap: if the model "summarizes the day" directly, it echoes the loudest complaints. Tag-then-count is what makes the top-10 honest.
>
> Proof: an unattended pipeline running twice daily with a dedupe ledger and failure alerts; a 24/7 multi-agent ops desk (71 agents, checkpointed state).
> https://origit892-stack.github.io/agent-operator/
>
> One question: how do the calls arrive today — a phone line, WhatsApp voice notes, or a ticketing system? That decides the ingestion step.

### L-20261117-07 — FIT C — DRAFT
**Title:** r/n8n (cross-posted r/nocode): building voice agents — how to handle call-drop / bad-network scenarios, dry-running them
**Source:** https://www.reddit.com/r/n8n/comments/1xxrp0c/if_you_are_building_automation_with_voice_agents/ (r/n8n, posted 2026-11-16 15:06 UTC; same OP cross-posted r/nocode: https://www.reddit.com/r/nocode/comments/1xxrnr4/if_you_are_building_automation_with_voice_agents/ — reply ONCE, primary = r/n8n)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> For call drops and bad-network runs, you can't dry-run every failure — but you can make each class of drop do the right thing automatically:
>
> 1. Drop before the caller confirms → the downstream action must not fire (commit only after confirmation).
> 2. Drop after the action but before they hear the confirmation → store the result keyed to the call; on reconnect, look it up and tell them what happened instead of re-running.
> 3. The silent drop — provider sends no end event at all (this is the one that bites): a watchdog timer per call; no status in the window = treat as dropped, same recovery path.
>
> Plus a small nightly dry-run of the two real disconnect scenarios against a test number, so regressions show up before customers do.
>
> I build and operate this class of unattended agent system in production (24/7 multi-agent desk, verified daily). If you want it wired into your flow: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which voice provider are you on — does it webhook mid-call drops, or only end-of-call? That decides whether the watchdog is the safety net or the primary detector.

### L-20261117-08 — FIT C — DRAFT
**Title:** r/automation: cross-portal RPA without APIs (login-gated partner portals) — Viktor vs n8n+Claude+Playwright, token-vs-speed trade-off
**Source:** https://www.reddit.com/r/automation/comments/1xxlfng/how_do_you_make_rpa_faster_when_there_is_no_api/ (r/automation, posted 2026-11-16 09:50 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Your token-vs-speed trade-off has a standard resolution: stop paying model tokens for data that is already structured.
>
> The pattern: per partner portal, one hand-written extractor (deterministic fields — the layout is stable per portal even when the values aren't), Playwright only for the login-gated navigation, and the LLM only the rows the extractor can't parse with high confidence. Batch: one model call per page, not per record. And split extraction from submission at the page level, not the record level — your split idea is right, it just needs the right seam.
>
> Result: Viktor-level speed with N8n-level visibility, and a logged decision trail per record.
>
> Proof: an unattended extraction pipeline running twice daily with a dedupe ledger and failure alerts; a 24/7 multi-agent ops desk (71 agents, checkpointed state).
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many distinct partner portals are in the loop — under 5, or 10+? That decides whether per-portal extractors pay off immediately or you need a generic-parser-first approach.

### L-20261117-09 — FIT C — DRAFT
**Title:** r/AI_Agents: "10 agents running, half waiting on me" — managing agent escalations is a full-time job
**Source:** https://www.reddit.com/r/AI_Agents/comments/1xy1quh/im_the_bottleneck_of_my_own_company/ (r/AI_Agents, posted 2026-11-16 21:24 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> "10 agents and half are waiting on me" — the problem isn't the count, it's that all 10 escalate to you the same way, no matter what's at stake. What I run in production (a 71-agent desk, higher stakes):
>
> 1. Split by reversibility. Anything an agent can undo, or that costs nothing if wrong, proceeds and just logs — only irreversible or customer-facing actions hit your queue.
> 2. One inbox, not 10 threads: each escalation is one structured line — decision needed, what's pending, cost of waiting — so triage takes minutes.
> 3. Timeouts: nothing waits forever. An unanswered approval auto-escalates (or auto-approves, for the low-risk tier) after a set window. A 48-hour stuck loop is a missing timeout, not a missing person.
>
> I operate this class of multi-agent system in production — checkpointed state, runs verified daily. Happy to review your escalation design and send back a plan + fixed price.
> https://origit892-stack.github.io/agent-operator/
>
> One question: of the 10, how many would lose nothing by proceeding without you for a full day? That's your reversible tier — its size decides the queue design.

### L-20261117-10 — FIT C — DRAFT
**Title:** r/n8n: seeking technical co-founder for B2B sales/GTM automation (equity partnership, not a paid build)
**Source:** https://www.reddit.com/r/n8n/comments/1xxi884/looking_for_a_technical_cofounder_partner_to/ (r/n8n, posted 2026-11-16 06:26 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Your technical side reads exactly like what I build and operate in production — n8n-scale workflow systems, Python/JS data pipelines, enrichment and LLM orchestration: a 24/7 multi-agent ops desk (71 agents, checkpointed state, verified daily), an unattended pipeline with failure alerts.
>
> One honest note first: I work as an operator, not an equity co-founder — fixed-price builds and care plans, where you keep 100% of the business and I'm paid for systems that run. If that shape works — you own the GTM vision and the customers, I build and operate the prospecting/enrichment engine — we can start on working software instead of promises: a paid discovery build for one ICP (account research + enrichment + scoring), plan + fixed price in 24-48h.
>
> Proof: github.com/origit892-stack/Projects · https://origit892-stack.github.io/agent-operator/
>
> One question: what's the first industry + size band you'd target? That decides whether the first build is a prospecting engine or a buying-signal monitor.

## 2026-11-18

### L-20261118-02 — FIT C — DRAFT
**Title:** n8n [HIRING] (thread CLOSED): commission-based BD / AI-implementation consultant + unpaid portfolio AI engineers — Meridian AI LLC (water utilities, pre-revenue, Tempe AZ)
**Source:** https://community.n8n.io/t/329316/ (n8n community · Jobs, posted 2026-11-18 03:15 UTC)
**Send:** ⚠ THREAD CLOSED — channel = the interest form (Google Form) linked in the post; user decision likely reject (no guaranteed pay — commission on pre-revenue + unpaid work)
**Draft:**
> Straight from me: I work as an operator on fixed-price builds and care plans — not commission, and I don't take unpaid builds. So the BD half isn't a fit.
>
> If you're still looking for the prototype work (public water-system data), here's what I run in production: a 24/7 multi-agent ops desk — 71 specialized agents with checkpointed state, execution verified daily — plus unattended pipelines with failure alerts. For one clearly scoped deliverable I can send a fixed quote — e.g. the follow-up-provenance loop (alert → who owns it → what proves it's done) as an n8n workflow + database, with execution logs.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what does "done" look like for the first deliverable — the full alert→assignment→proof loop for one utility, or just the tracking table behind it?

## 2026-11-19

### L-20261119-01 — FIT C — DRAFT
**Title:** n8n: automate supermarket cart from a Google Sheet (product/qty/brand -> add to cart) — beginner asking which nodes
**Source:** https://community.n8n.io/t/329458/ (n8n community · Help me Build, posted 2026-11-18 15:59 UTC)
**Send:** reply in the thread (open, replies enabled — verified 2026-11-19)
**Draft:**
> "Automate the purchase of products at a supermarket" — a Google Sheet in, the cart out — is the class of workflow I build and run in production.
> 
> Honest constraint first: a headless run starts logged out, and most supermarket sites block headless Chrome or throw a CAPTCHA once requests repeat. So the robust shape:
> 1. Google Sheets node (From Sheet) -> Loop Over Items, one product per row.
> 2. Browser Tool node navigates to the product page, sets quantity from the row, clicks Add to cart — drive React/Vue quantity fields from the node's JS action, not plain typing.
> 3. If the chain exposes a commerce API, an HTTP Request node with Header Auth outlives every CSS selector — that's the version I'd build.
> 
> Proof you can check today: a 124-product store I run end-to-end via its official API — GET before write, read-back after every change — plus an unattended pipeline with failure alerts. I can wire the first one for you, ~$300 fixed.
> https://origit892-stack.github.io/agent-operator/
> 
> One question: which supermarket, and does it expose any commerce/partner API, or is it website-only? That decides the API path vs the browser path.

### L-20261119-02 — FIT B — DRAFT
**Title:** n8n [HIRING] (thread CLOSED): Gumroad sales data -> Airtable (email/date/amount/product id) — $1,000 budget, was scammed before
**Source:** https://community.n8n.io/t/329131/ (n8n community · Jobs, posted 2026-11-17 02:14 UTC — ~52h gap-miss, still live)
**Send:** ⚠ THREAD CLOSED — channel = Airtable form: https://airtable.com/appkK1MZ2cLhJYQlR/pagE4pCmCjCzloG9u/form (user applies from their own account)
**Draft:**
> You're opening a Gumroad store and want to "export sales data from Gumroad to Airtable" to follow up with customers — email, transaction date, amount, product id. That's a clean, well-scoped data-sync workflow I build and run in production.
> 
> You've been burned by a workflow that "looked like it worked" but didn't — so this one is built to prove it actually works:
> 1. Gumroad webhook on each new sale (API poll as the fallback) -> one row per transaction.
> 2. Map to your Airtable fields -> write.
> 3. Read-back verification: after every write, GET the row and confirm it landed, plus a daily recount of Gumroad vs Airtable so a missed event can't hide. Idempotent on transaction id — replayed webhooks never double-write.
> 
> Proof you can check today: I run a 124-product store end-to-end via its official API — GET before write, read-back after every change. Read-back is exactly what rules out a workflow that "looks like it worked."
> https://origit892-stack.github.io/agent-operator/ · github.com/origit892-stack/Projects
> 
> Your $1,000 budget covers this with room — I'll send the exact fixed price after a quick mapping. Timeline: ~3 days.
> 
> One question: is the Gumroad store already live with API/webhook access, or still pre-launch? That decides whether I wire the webhook now or start from the API poll.

## 2026-11-21

### L-20261121-01 — FIT B — DRAFT
**Title:** r/AI_Agents: healthcare system (Michigan, IT Governance) mandated audit of every AI agent/app/automation — 2,000+ Power Apps est., needs accurate inventory (owners, assets, data sources, live permissions, orphaned flows)
**Source:** https://www.reddit.com/r/AI_Agents/comments/1y12z0c/trying_to_get_an_accurate_inventory_of_every_ai/ (r/AI_Agents, posted 2026-11-20 13:05 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Leadership mandated an audit of every automation and employee-built tool, and the real count already blew past your 2,000-Power-Apps estimate — a "superficial environment count" won't hold up. I build and operate exactly this class of pipeline in production: pull from the platform APIs (Power Platform admin / Dataverse), normalize into one inventory table — owner, asset, connected data sources, live permissions, orphaned flows — with read-back verification, so no row is written blind.
>
> Proof you can check today: a 24/7 multi-agent ops desk (71 agents, checkpointed state, runs verified daily); a 124-product store run end-to-end via its official API — GET before write, read-back after every change.
>
> If you want it built: plan + fixed price in 24-48h. Timeline: ~10 days for a first full sweep plus the audit report.
> https://origit892-stack.github.io/agent-operator/
>
> One question: does the audit also have to cover non-Microsoft builds — custom scripts, apps on employee machines, Zapier/n8n/Make accounts? That decides how much of the inventory comes from discovery instead of APIs.

### L-20261121-02 — FIT B — DRAFT
**Title:** r/automation: client onboarding pipeline (Jotform → Zapier → Google Docs template → DocuSign → HubSpot) — "when it breaks nobody knows which piece did it"; wants one tool for form + docs
**Source:** https://www.reddit.com/r/automation/comments/1y1pw8a/zapier_alternative/ (r/automation, posted 2026-11-21 06:13 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Your client onboarding — Jotform, Zapier, a Google Docs template, DocuSign, then back into HubSpot — has the classic failure mode: five handoffs, zero ownership when something breaks. The fix is collapsing form + document + signature into one place, and making the rest observable — not swapping one five-tool chain for another.
>
> The build: one intake form → document set generated from your template with the client data → e-signature → completed packet synced to HubSpot — with one run log per client, so any failure names the exact stage. I operate this class of unattended pipeline in production: a 24/7 multi-agent ops desk with execution logs verified daily, and a store run via its official API with read-back after every write.
>
> I can map your five tools and send back the plan + fixed price + done-definition in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what's in the "document part" — a fixed set of templates, or does the document set change per client type? That decides whether I build the generator around templates or a data-driven document spec.

### L-20261121-03 — FIT B — DRAFT
**Title:** r/n8n: landscaping company (OP = same user as L-20261116-04) — 15-20 calls/wk, misses most while on jobs; voice AI pricing "is wild"; what's worth paying vs fluff
**Source:** https://www.reddit.com/r/n8n/comments/1y17rrw/is_voice_ai_actually_worth_the_cost_for_small/ (r/n8n, posted 2026-11-20 16:25 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> 15-20 calls a week, most of them missed because you're out on jobs — the math is simple: one missed call that was a 20% chance at a $500 job is already paying for the voice line. On the "wild pricing": you only need three things — a number that answers on the 2nd-3rd ring, a script that takes name, phone, job type and address, and a text to you with the lead. Everything else (dashboards, CRM integrations, custom branding) is the fluff you're right to skip. That three-piece core is per-minute telephony plus one LLM call per call — low single-digit dollars a month at your volume.
>
> I build and operate this class of unattended system in production: a 24/7 multi-agent ops desk, runs verified daily; an unattended pipeline with failure alerts. I can wire the whole thing: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: what should a missed call end in — an auto-booked slot, a scheduled callback, or just the lead details texted to you? That decides how much the booking flow has to do.

### L-20261121-04 — FIT C — DRAFT
**Title:** r/AI_Agents: invoice-reminder agent silently dead for 9 days (expired API token, no alert); current fix = 6 "I ran" messages a day, too noisy; asks about heartbeats/dashboards/dead man's switch
**Source:** https://www.reddit.com/r/AI_Agents/comments/1y0x7r1/how_do_you_find_out_your_agent_silently_failed/ (r/AI_Agents, posted 2026-11-20 07:23 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> The expired-token-silent-for-9-days failure has a name: no dead man's switch. Your "I ran, did X" message is the right primitive — you just need to stop delivering it as six messages. The pattern I run in production (71-agent desk, verified daily):
>
> 1. Each agent pings a heartbeat store — one row: run id, status, count, duration — not your inbox.
> 2. One monitor job checks every hour: no fresh heartbeat in the window → one alert, with a retry. For the token-expiry class specifically: wrap the API calls so an auth-class error alerts on the FIRST failed call, not after the window.
> 3. Your inbox gets at most one digest — "X agents ran, 0 exceptions" — or silence, plus one alert per real failure.
>
> Proof: the ops desk runs exactly this — scheduled runs, execution logs verified daily. I can wire the same layer around your agents: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: where do your agents run — n8n, cron scripts, or something else? That decides whether the heartbeat store is a table, a file, or the platform's own logs.

### L-20261121-05 — FIT C — DRAFT
**Title:** r/automation: Fyxer alternatives — wants AI email management: sort/prioritize, email→tasks, replies + follow-ups, calendar connect, less manual checking
**Source:** https://www.reddit.com/r/automation/comments/1y1g0jm/what_are_some_good_fyxer_alternatives_for/ (r/automation, posted 2026-11-20 21:56 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Sort, prioritize, turn into tasks, handle replies and follow-ups, connect to the calendar — that's five jobs, and each tool you've shortlisted (Fyxer, Shortwave, Lindy) covers two or three of them, which is exactly why manual work survives. The honest comparison:
>
> 1. Inbox triage tools (Fyxer, Shortwave) — zero follow-up automation.
> 2. AI-staff tools (Lindy) — closest to your list, but per-action pricing adds up, and it's only as good as your prompts.
> 3. A thin custom layer — one LLM pass over your new mail against your fixed rules (what's urgent, what's a task, what needs a reply) writing ONE structured row per email: action, due date, draft reply. You approve, it executes. Runs on your own API keys, no per-seat SaaS.
>
> Proof: I operate unattended pipelines in production — a 24/7 multi-agent ops desk with runs verified daily; a store run via its official API with read-back after every change. If you want option 3 built: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which mail backend do you run — Gmail, Microsoft 365, or something else? That decides the ingestion path.

### L-20261121-06 — FIT C — DRAFT
**Title:** r/smallbusiness: nearly double-paid a $2,400 vendor bill ($800 deposit paid earlier "vanished into the checkbook"); asks where to put deposits so the payer sees them when the final bill lands (Ramp Bill Pay)
**Source:** https://www.reddit.com/r/smallbusiness/comments/1y1ce2b/how_do_i_keep_from_paying_the_same_deposit_twice/ (r/smallbusiness, posted 2026-11-20 19:25 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> The $800 you paid while the installer was still on site vanished into the checkbook — the fix is a deposit ledger that shows up at payment time, not better memory. The build: one table (vendor, deposit date, amount, reference, what it applies to); every final invoice in Ramp's Bill Pay gets matched against open deposits before the check is cut — match found → the net amount shows ($1,600, not $2,400); no match but the vendor has history → one nudge to you. Ten minutes a week instead of a checkbook archaeology dig.
>
> Proof: I run this class of unattended reconciliation pipeline in production — scheduled pull, match, alert, log (a 24/7 multi-agent ops desk, verified daily; a store run via its official API with read-back after every change). I can build the ledger + the match: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how do the deposits actually get paid today — checks, ACH through Ramp, or a mix? That decides where the deposit record gets written.

### L-20261121-07 — FIT B — DRAFT (gap-miss: 11-20 radar run missing)
**Title:** r/n8n: Google Calendar → Sheets/Docs → NotebookLM pipeline — ICS handling is the blocker; "tell me if there is anything wrong in my thinking"
**Source:** https://www.reddit.com/r/n8n/comments/1y0tll3/need_help_with_creating_a_google_calendar_sheets/ (r/n8n, posted 2026-11-20 03:54 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> The hard part you named is the right one: NotebookLM doesn't care about your calendar, it cares about a file it can read. The clean shape:
>
> 1. A scheduled n8n trigger pulls your Google Calendar (Calendar API node) for the window you care about.
> 2. Convert to plain text in a Code node — one line per event: date, time, title, location, description. Skip the binary-ics round-trip; text is what NotebookLM reads best.
> 3. Write it into the Sheet cell / Doc you import (your "easy" step), let NotebookLM ingest. Refresh on a schedule and the source is always current.
>
> Proof: I run this class of unattended pipeline in production — a 24/7 multi-agent ops desk (71 agents, checkpointed, verified daily) plus a store run via its official API with read-back after every change. Happy to wire the full calendar→NotebookLM flow: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: which window does NotebookLM need — today + tomorrow, the week, or the full month? That decides how often the refresh has to run.

### L-20261121-08 — FIT B — DRAFT (gap-miss)
**Title:** r/automation: enterprise QA — evaluating agentic test platforms; demo agent "marked a step passed when it typed into the wrong panel"; needs forensics, Windows client, runtime at hundreds of cases (AskUI in production, replacing Tosca/Ranorex)
**Source:** https://www.reddit.com/r/automation/comments/1y0vcnx/best_agentic_test_automation_platforms_for/ (r/automation, posted 2026-11-20 05:30 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> The panel thing is the tell — "marked a step passed when it typed into the wrong panel" is exactly where a forensic layer earns its keep. From operating this class of system in production (71-agent desk, execution logs verified daily), the three criteria I'd judge any platform on:
>
> 1. Reconstructability — every step stores exact input, the action taken, the field actually hit, expected vs actual, so a pass is re-derivable, not just asserted.
> 2. Out-of-UI verification for money/critical steps — query the backend after the run (payment API, order status), not just the screen.
> 3. Bounded behavior — hard caps on retries and runtime; an agent that tries six paths until one looks green is unbounded retry, not intelligence.
>
> I run this evidence pattern daily and can build it around your AskUI/Playwright setup — including the Windows client side. Plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many of your hundreds of cases touch the Windows client vs the browser? That decides whether the evidence layer instruments the desktop automation or just the Playwright side.

### L-20261121-09 — FIT B — DRAFT (gap-miss)
**Title:** r/AI_Agents: QuickBooks DESKTOP bank-upload automation — multiple entities, "not interested in moving to QB Online"; manually downloading + reloading each account file, "very time consuming"
**Source:** https://www.reddit.com/r/AI_Agents/comments/1y06qye/quickbooks_desktop_bank_upload_automation/ (r/AI_Agents, posted 2026-11-19 11:10 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Manually downloading and reloading bank files for every entity is exactly the kind of deterministic, no-LLM-needed automation I build in production:
>
> 1. A scheduled job per entity pulls the bank feed (your bank's file/API, read-only credentials per entity).
> 2. Normalize into QuickBooks Desktop's import format — one mapping table per bank, so a new account is a row, not a rebuild.
> 3. Push into QB Desktop's import path, then read back: transaction count in QB must match the file, or the run alerts instead of logging success. Idempotent on transaction ID — a re-run can't double-import. No QB Online migration required.
>
> Proof: an unattended pipeline publishing twice daily with a dedupe ledger and failure alerts; a 124-product store run via its official API — GET before write, read-back after every change. Same pattern, applied to your banks.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many entities and bank accounts total, and does each bank give you a file export (CSV/QFX) or only online banking? That decides whether the pull is a file drop or a browser step.

### L-20261121-10 — FIT B — DRAFT (gap-miss)
**Title:** r/n8n: internal app on n8n Cloud (webhook → HTML → SQL via Power Automate) on email + shared password — "anyone with the password can sign in as a colleague and approve things in their name"; wants Microsoft Entra ID login
**Source:** https://www.reddit.com/r/n8n/comments/1y09pcq/microsoft_login_for_an_app_hosted_in_n8n/ (r/n8n, posted 2026-11-19 13:45 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> "Anyone with the password can sign in as a colleague and approve things in their name" — that's the real bug, and it has a clean fix: the HTML page authenticates against Microsoft Entra ID, and n8n learns the identity from the token, not from a form field.
>
> 1. The page signs in via MSAL (Entra ID) — no n8n credentials involved.
> 2. The page carries the ID token to your webhooks; a small auth middleware (an n8n Code node, or a tiny service in front) validates it against Entra and extracts the verified email.
> 3. Your existing security-table lookup keys off the validated identity — approvals now carry a name that can't be spoofed by a shared password.
>
> I build and operate this class of system in production — a 24/7 multi-agent ops desk with checkpointed, verified runs; a store run via its official API with read-back after every change. I can wire the Entra layer for you: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: is the app on a single Entra tenant with everyone in one work/school account, or are guest/external accounts involved? That decides which MSAL flow I set up.

### L-20261121-11 — FIT C — DRAFT (gap-miss)
**Title:** r/AI_Agents: agent-based UI regression passed a checkout that never charged the card (payment timeout, agent saw an order number and called it done); OP enumerating fixes; asks what makes a pass trustworthy
**Source:** https://www.reddit.com/r/AI_Agents/comments/1y0oxf9/how_do_ai_testing_agents_prevent_false_passes_and/ (r/AI_Agents, posted 2026-11-20 00:04 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> "The run log said 'checkout completed successfully' — that's the agent telling us what it thinks happened, not proof that it happened." Your four changes are the right ones; the pattern behind them is what I run in production (checkpointed 71-agent desk, execution logs verified daily):
>
> 1. A pass is an assertion, not a narrative — every step carries an expected result and the verdict comes from checking it; the model's summary is an attachment, never the evidence.
> 2. Out-of-UI checks for anything that moves money — query the payment API after the run. A green screen is not proof the charge landed.
> 3. Bounded attempts — hard caps on retries and paths; an agent that wanders six routes until one looks green is hiding the failure, not finding it.
> 4. One artifact per step — screenshot keyed to the step ID plus expected/actual — so a reviewer of a green run sees exactly what the agent saw.
>
> I can build that evidence layer around your agent: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many of your regression cases touch payment or other money steps? That decides how much of the out-of-UI verification layer I'd build first.

### L-20261121-12 — FIT C — DRAFT (gap-miss)
**Title:** r/smallbusiness: launching a local scrap (paper/cardboard) pickup service, "zero budget to build a custom app"; wants a cheap no-app way for families to book pickups without phone tag / messy text threads
**Source:** https://www.reddit.com/r/smallbusiness/comments/1y0tih1/need_a_cheap_noapp_way_for_local_families_to/ (r/smallbusiness, posted 2026-11-20 03:49 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> "Zero budget" + "no phone tag, no messy text threads" — the honest answer: a booking app is not the first step. The cheapest thing that kills phone tag is a two-step free setup:
>
> 1. A free Google Form with three fields: name, phone, what you're picking up (paper / cardboard / both).
> 2. A free Google Calendar with a published "pickups this week" view — the form auto-creates the event (one ~20-line Apps Script), so every request lands in one place with an address and a slot.
>
> That's $0 today and it ends the text threads. If it outgrows that — which it will — the paid step is a real booking page: customer picks a slot, you get a notification, no app store, no per-booking fee. I build and operate that class of unattended pipeline in production (24/7 ops desk, verified daily; a store run via its official API). Paid version when you want it: fixed quote after a quick mapping.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many pickups a week are you expecting at launch — a handful, or 50+? That decides whether the free setup holds or you should skip straight to the booking page.

### L-20261121-13 — FIT C — DRAFT (gap-miss)
**Title:** r/smallbusiness: messy supplier Excel sheets — merged cells, 3-row headers, dimensions in descriptions, prices change monthly; "is everyone still stuck doing copy-paste / hiring VAs?"
**Source:** https://www.reddit.com/r/smallbusiness/comments/1y0ck2p/how_do_you_actually_handle_messy_supplier_excel/ (r/smallbusiness, posted 2026-11-19 15:44 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> Merged cells, 3-row headers, dimensions buried in descriptions — that's not a spreadsheet problem, it's a normalization problem, and the clean-it-manually-every-month loop is the bottleneck to kill. The pattern that works:
>
> 1. Per supplier, one hand-written parser (their layout is stable even when the values aren't) into one fixed schema: SKU, description, dimensions, unit, price, currency, effective date.
> 2. Price changes become dated rows, not overwrites — you keep history, and "what changed this month" is a query, not a memory.
> 3. Two outputs fall out for free: the store price update (a diff vs current — you approve the deltas) and the clean PDF catalog / quote (template + data).
>
> The LLM only touches rows the parser can't place with high confidence; everything else is deterministic and logged.
>
> Proof: I run unattended extraction pipelines in production — a 24/7 multi-agent ops desk (verified daily), a store run via its official API with read-back after every change. I can build your supplier-normalization layer: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many suppliers send these sheets, and does every supplier use a different layout? That decides whether it's N small parsers or one generic one with per-supplier overrides.

### L-20261121-14 — FIT C — DRAFT (gap-miss)
**Title:** r/smallbusiness: invoicing is easy but "following up afterwards is where things fall apart — it's manual, it's uncomfortable, and the first thing to slip when I'm busy"
**Source:** https://www.reddit.com/r/smallbusiness/comments/1y0i410/whats_your_process_for_following_up_on_overdue/ (r/smallbusiness, posted 2026-11-19 19:16 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> "Following up is where things fall apart — manual, uncomfortable, the first thing to slip" — that's a system problem, not a willpower problem, and the uncomfortable part is exactly why manual follow-up fails: it depends on you feeling like it. The setup that actually works:
>
> 1. Every invoice gets a dated touch plan at creation: day 1 (thanks / received?), day 7 (friendly nudge), day 14 (firm, with the next step), day 21 (final + what happens next).
> 2. The sequence runs itself — personal-sounding email from your name (not "billing@"), each step references the invoice and amount, replies route to you, and a paid invoice stops the chain immediately.
> 3. One morning digest: who's late, by how much, what's queued next.
>
> I build and operate this class of unattended system in production — a 24/7 multi-agent ops desk with execution logs verified daily, and an unattended pipeline with failure alerts. I can wire it to your invoicing tool: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: where do your invoices live today — an accounting tool (which one), spreadsheets, or invoiced by hand? That decides where the touch plan hooks in.

### L-20261121-15 — FIT C — DRAFT (gap-miss)
**Title:** r/AI_Agents: gym chatbot invented a free 3-month membership pause → screenshot went viral in the town's Facebook group; now running an Orq-AI terms guardrail that's "either too strict or too loose"; considering checking only yes-answers
**Source:** https://www.reddit.com/r/AI_Agents/comments/1y0akr8/how_do_teams_catch_ai_chatbots_giving_customers/ (r/AI_Agents, posted 2026-11-19 14:22 UTC)
**Send:** reply in the thread — ⚠ user's Reddit account still on the 21-day karma plan (reddit/REDDIT.md); parks until the account passes the gate
**Draft:**
> A bot inventing a free 3-month pause and the town Facebook group getting the screenshot — your calibration problem (too strict blocks "bring a friend on Saturday," too loose lets "free locker" through) has a standard resolution: stop checking every answer, check the risk class.
>
> 1. A cheap first pass classifies each answer: does it grant, waive, extend, or promise anything — a yes to a request, a price, a policy, an exception? No → it ships. Yes → it goes to the guardrail.
> 2. The guardrail checks that specific claim against the terms with a narrow question — "is this exact offer in the terms, and where?" — not "does this answer match the terms." That kills both failure modes: normal questions never reach the strictness, invented offers get checked precisely. Your yes-only instinct is the right one, formalized.
> 3. Every guardrail decision logs the terms section it cited — when the bot is wrong, you see why in one line.
>
> I run this class of verification layer in production (71-agent desk, execution logs verified daily; a store run via its official API with read-back after every change). I can build the two-stage guardrail for your Orq setup: plan + fixed price in 24-48h.
> https://origit892-stack.github.io/agent-operator/
>
> One question: how many distinct offers or policies in your terms doc are "yes"-granting — a dozen, or hundreds? That decides how the guardrail indexes the terms.
