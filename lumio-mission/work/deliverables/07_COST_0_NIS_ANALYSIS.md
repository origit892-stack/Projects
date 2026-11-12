# 07 — 0₪/Month Cost Analysis (Lumio 4.0)

All figures verified from official docs during this mission (2026-11-11/12; see 02 for URLs). "0₪ today" ≠ "free forever" — each row notes the first cap that breaks at scale.

## Fixed stack (0₪ within free tiers)
| component | provider | free tier (verified) | Lumio usage at 100 students (conservative) | first cap that breaks |
|---|---|---|---|---|
| Static hosting + PWA | Cloudflare Pages | 500 builds/mo, unlimited bandwidth (free plan) | a handful of deploys/mo | none at school scale (1000s of students) |
| Database + Auth + RLS | Supabase Free | 500MB DB, 2GB file storage, **auto-pause after ~1 week low activity**, 50k MAU auth | ~20-50MB at 100 students; 10-100 users | **auto-pause** (mitigated: DB traffic = heartbeat — see 06 R2); 500MB at ~10+ years |
| Background sync (Classroom) | Google Apps Script (consumer accounts) | 20 triggers/user, 90 min/day runtime, 20k URLFetch/day, 6 min/run, **$0 for gmail.com accounts** | 1 trigger + 1 daily run per student (~1% of quota) | none at any school scale |
| Background sync (ICS/public feeds) | Supabase Edge Functions + pg_cron | **500k invocations/mo**, 150s runtime, 100 functions, 100 secrets | ~1 invocation/day (cron fan-out in one function) ≈ 30/mo ≈ 0.006% | 150s runtime at ~1000+ users (chunking in code); 5GB egress |
| Egress | Supabase Free | **5GB/mo** | ~18% at 100 students (JSON syncs + page loads) | **~1000 students at peak** → upgrade or CDN-cache the static site |
| Domain | Cloudflare (user's existing) | DNS free; **domain renewal is NOT free** — user's registrar charges apply yearly | — | renewal fee (not a monthly cost; never claimed "free forever") |

## Conservative per-scale estimate (monthly, ₪)
| scale | Supabase | Cloudflare | Apps Script | total |
|---|---|---|---|---|
| 10 students (1 class) | 0₪ | 0₪ | 0₪ | **0₪** |
| 100 students (1 school) | 0₪ | 0₪ | 0₪ | **0₪** (watch: egress ~18%) |
| 1000 students (district) | 0₪ at typical use; egress breach risk at peak | 0₪ | 0₪ | **0₪ typical / ~$25-50 if Supabase Pro becomes necessary** |

## What is NOT 0₪ (stated honestly)
1. **Domain renewal** — yearly, at the user's registrar (existing obligation, not added by this project).
2. **Classroom in-app flow production use** — the OAuth client itself is free; if the school requires Google's verification of the app for non-test users, Google's process is free but time-costly (forms, possibly a SOC2 for sensitive scopes — classroom.readonly scopes are *sensitive*, not *restricted*; testing mode covers a pilot).
3. **Maintenance labor** — code maintenance is on the user (0₪ cash, non-zero time).
4. If Supabase free auto-pause becomes a problem: the documented mitigation is DB-heartbeat traffic (already in feed-sync); a paid tier ($25/mo) is the fallback, not a requirement at school scale.

## Verification trail
- Supabase free limits: official docs pages fetched 2026-11-11 (moe-cost.md §B, URLs in 02).
- Apps Script consumer quotas: official quotas page fetched 2026-11-12 (automation-engines.md E1, "Triggers 20/user/script", "90 min/day", "20,000/day URL Fetch").
- Cloudflare Pages free plan: official docs (DEPLOY.md + 02).
- 5GB egress / 500MB DB / auto-pause: Supabase free-tier page, 2026-11-11.
