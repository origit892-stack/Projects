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
