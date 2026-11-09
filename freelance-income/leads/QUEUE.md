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
