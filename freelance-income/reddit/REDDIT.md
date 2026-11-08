# Reddit plan — rules verified 2026-11-08 (r/forhire sidebar + live auto-removal posts + 2026 guides)

## Why Reddit
Requests are ALREADY posted there (inbound, same model as Upwork) — free, and it compounds: an account with history is a trust asset platforms can't fake.

## The two layers
### Layer 1 — Request boards (paid requests posted publicly)
| Sub | Size/activity | Gate (verified) | Verdict |
|---|---|---|---|
| **r/forhire** | 672K members, ~40 posts/day | Comment on [Hiring] posts: account ≥20 days old + recent regular activity + undisclosed karma (auto-removed if under — no error message). [For Hire] post: ≥1 month old | **THE main one.** [Hiring] posts = clients with budgets. Apply via PM (private message), never in comments. |
| r/slavelabour | 200K+ | low barrier | **Skip for work** — tasks are <$30, below our $300 floor. Karma source only. |
| r/B2BForHire | ~37K visits/wk | 2-month-old account | Revisit in month 2. |

### Layer 2 — Expertise communities (inbound reputation — answer, don't pitch)
r/n8n · r/LangChain · r/ChatGPTCoding · r/ClaudeAI · r/LocalLLaMA · r/smallbusiness · r/Entrepreneur · r/webdev
Play: answer real questions with substance (9 helpful answers : 1 self-reference max), no link-bombing, no copy-paste across subs. Builds karma (unlocks Layer 1) + occasional "DM me" + profile traffic.

## Hard rules (breaking = ban, and several are unappealable)
1. **NO bots / automated contact — ever.** Monitoring (reading posts) is fine; every reply must be sent by a human hand. (I draft; user clicks send.)
2. **No karma farming** (low-effort posts for karma) — bannable.
3. **1 [For Hire] post per 7 days**, max. Rate + portfolio required in the post body. Currency only, no free/spec work.
4. Apply to [Hiring] posts by **PM only**; never comment "sent you a PM".
5. Rate floor: < $15/hr is auto-removed (we're $300+ — fine).
6. Read the LIVE sidebar before every post — rules change without notice.
7. Never ask mods for the karma number — that itself is a ban.

## Timeline (starts when user creates the account)
- **Day 0:** create account (real email; name can reflect the business — it's a real account of a real person). Profile: one line + links to github.com/origit892-stack/Projects + openshelf.1st4offers.com.
- **Days 0-21 (karma phase):** 15-30 min/day answering real questions in Layer 2 (I prepare 2-3 drafts daily; user pastes + edits in their voice). No self-promo.
- **Day 21+:** eligible to comment on r/forhire [Hiring]. Start replying to matching posts (agent/automation/n8n/chatbot/CRM/LLM) — via PM.
- **Day 30+:** first [For Hire] post (below).
- **Month 2:** add r/B2BForHire.

## [For Hire] post template (day 30)
**Title:** [For Hire] AI Agent & Automation Engineer — agents that run 24/7 · fixed $300-$2,000
**Body:**
One-line offer. 3 proof bullets: (1) 24/7 multi-agent ops fleet I operate daily, (2) 124-product store run end-to-end via API, (3) unattended publishing pipeline 2x/day. Links: GitHub + storefront + YT channel. Rate: $300/$900/$2,000 fixed packages, $35/hr for retainers. Timezone UTC+2. "PM me the task you want gone."

## Monitoring cron (PROPOSED — needs user OK)
Daily 09:00 IST, read-only: fetch public RSS of r/forhire, r/n8n, r/B2BForHire → filter last 24h for keywords (agent, automation, n8n, chatbot, whatsapp, crm, llm, "build", "need someone") → deliver top 3-5 with a 2-3 line PM draft each. Cost: $0. Useless until day 21, but it keeps a 21-day deep list so day 21 starts hot.
