# Freelance Income Kit — "AI employee in 2 weeks"

**Status (2026-11-08):** KIT COMPLETE + STRATEGY SHIFT — user DROPPED Fiverr/Upwork ("תמצא תחליף חינמי"). Active channels = `channels/FREE_CHANNELS.md` (Braintrust 0% + direct $0 stack). Fiverr/Upwork files → `archive/`.
**Not done:** accounts (user action), Telegram bot token, payment link, channel name confirmation, 12:00 YT + 09:00 Reddit crons.

## What this is
An inbound sales machine for selling AI-agent/automation builds.
No cold DMs. Demand comes from: (a) the $0 channel stack in `channels/FREE_CHANNELS.md` (Braintrust, Google Business, FB groups, LinkedIn, Discord, Reddit, build-in-public), (b) public proof (storefront, GitHub, demo video, content).

## Architecture rule — where client systems run (2026-11-08, user capacity concern resolved)
**Delivered client systems NEVER run on the operator's home machine / local models.** Per client, runtime is one of:
1. **Client's own LLM API keys** (DeepSeek/Groq/etc., pay-per-use — client's cost, cents per conversation) — default; scales to any concurrency.
2. **Client's own VPS/server** ($5-40/mo, client's cost) — self-hosted option.
3. **Operator-hosted** (care plan, client pays the server) — shared hosted model.
Local Qwen/vLLM = build/test/dev environment + operator's own pipelines ONLY. "40 concurrent clients" is a non-issue: load lands on client-side / client-paid infra.

## Files
| File | What |
|---|---|
| `OFFER.md` | The offer + pricing, EN + HE |
| `channels/FREE_CHANNELS.md` | **CURRENT CHANNEL STRATEGY** — free-marketplace research (Braintrust in; Contra/Malt out) + the $0 direct stack |
| `proposals/TEMPLATE.md` | Master proposal template + rules (any lead source) |
| `demos/DEMO_PLAN.md` | 3 demo clips — shot list, captions, ffmpeg recipe |
| `demos/PIPELINE_REPURPOSE.md` | DAILY 12:00 B2B demo channel — decided plan, needs user go (new channel, automated production) |
| `reddit/REDDIT.md` | Reddit play — verified subs + rules + 21-day timeline + monitoring-cron proposal |
| `site/SITE.md` | Site + messaging + payment decisions — live on GitHub Pages (agent-operator repo); NO fake case studies; inbound Telegram bot only; Stripe/PayPal links ($0 out-of-pocket) |
| `demos/clip1-agent-ops.mp4` | Ready demo video (27.5s vertical) — "demo link" for any lead source |
| `archive/` | Upwork/Fiverr profile + watchlist + 3 proposal drafts — OFF, kept paste-ready |

## Proof assets (all verified 2026-11-08, public or user-owned)
- Storefront I operate: https://openshelf.1st4offers.com (124 products, run via official API)
- Public code portfolio: https://github.com/origit892-stack/Projects
- Live cron (24/7 unattended jobs): `hermes cron list` — shorts pipeline 2x daily, last run ok 2026-11-08 16:32; daily 08:00 research brief (tesla-researcher profile)
- Live Roblox game in production state (14+ scripts, DataStore) — use verbally, not as a public link
- Full RE of a commercial obfuscated app (554/554 files decoded) — use verbally / as a written case study

## USER ACTION CHECKLIST (~40 min total, once)
1. **Braintrust** — apply at usebraintrust.com: profile from `OFFER.md` + site + the 4 proof systems; pass the AI interview. 0% talent fee. (~20 min)
2. **Google Business Profile** — claim free listing "The Agent Operator — AI Automation", Tel Aviv; link the site. (~10 min)
3. **LinkedIn** — free profile with the same copy. (~10 min)
4. **Telegram bot** — @BotFather, send token to the chief. (2 min)
5. **Payment** — PayPal.Me or Stripe Payment Link → chief pastes into the site. (10 min)
6. **Confirm** channel name "The Agent Operator" + go on the two crons (YT 12:00, Reddit 09:00).
7. (Optional, strong) Record a 2-min proof video with **Cmd+Shift+5** (free, no watermark): `hermes cron list` + storefront + GitHub repo.
8. Tell the chief "done" → it wires the bot, payment button, and site placeholders.

## ZERO-COST RULES (user mandates: אפס הוצאות + no Fiverr/Upwork)
- **Out-of-pocket: $0, forever.** The only money that ever moves: Stripe/PayPal per-transaction fees on a closed sale, and client-side platform fees (client pays). **Any channel taking a cut of OUR revenue is off the list** (Fiverr 20% and the Upwork model rejected by user 2026-11-08 — files archived, not deleted).
- **No pre-payment, no subscription, no "verification fee", no boosters, no paid tools, no third-party profile services.**
- **Recording:** macOS built-in screen recorder Cmd+Shift+5 (free, no watermark). Never Loom or paid tools.
- **Free content channels (the inbound engine):** existing Shorts pipeline + new 12:00 B2B channel + X + LinkedIn + Telegram + public GitHub (already live).

## Rules (honesty)
- Every claim in copy = verifiable system the user actually runs. NO invented client names, NO "12 client projects".
- No cold outreach of any kind (user explicitly rejected; platforms ban it).
- If a lead asks for client portfolio: the honest answer is "my production evidence is the systems I run — verifiable today" + links.
