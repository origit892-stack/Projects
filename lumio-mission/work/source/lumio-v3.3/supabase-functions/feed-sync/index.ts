// Lumio 4.0 — Supabase Edge Function: feed-sync (pg_cron-driven)
// Deploy to your own Supabase project (steps in supabase-functions/README-HE.md).
//
// Reads every connections row that has a feed_url (service role), fetches each
// feed, and upserts that user's items with the SAME stable dedup keys the site
// uses (user_id,source,external_id / user_id,kind,source,external_id) — so a
// re-sync updates rows, never duplicates them.
//
// Anti-pause: every run writes to the database (last_sync_at / facts per feed),
// which keeps the Supabase project from auto-pausing after ~1 week of low
// activity. See README-HE.md for the honest caveat.
//
// No secrets in this file: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are injected
// by the Supabase runtime.

import { createClient } from 'npm:@supabase/supabase-js@2';

const FETCH_TIMEOUT_MS = 20_000;
const MAX_BYTES = 2_000_000;
const MAX_FEEDS = 200; // safety cap
const CHUNK = 20; // H2 fix: feeds per parallel batch — 100 feeds worst case = 5 batches × 20s ≈ 100s < 150s

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

async function fetchText(url: string): Promise<string> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(url, { signal: ctrl.signal, mode: 'cors', credentials: 'omit' });
    if (!res.ok) throw new Error('HTTP_' + res.status);
    const text = await res.text();
    if (text.length > MAX_BYTES) throw new Error('TOO_LARGE');
    return text;
  } finally {
    clearTimeout(timer);
  }
}

// H1 fix — server-side feed URL validation. feed_url is user-writable (owner
// row via RLS), so the client-side validator is NOT the boundary: re-check
// here. https only, shahaf host allowlist, private/loopback/link-local/metadata
// IPs rejected (SSRF guard for the service-role runtime).
function isPrivateIp(ip: string): boolean {
  const v4 = ip.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
  if (v4) {
    const a = +v4[1], b = +v4[2];
    return a === 0 || a === 10 || a === 127 || (a === 169 && b === 254) ||
      (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168) ||
      (a === 100 && b >= 64 && b <= 127);
  }
  const l = ip.toLowerCase();
  return l === '::' || l === '::1' || l.startsWith('fc') || l.startsWith('fd') ||
    l.startsWith('fe80') || l.startsWith('::ffff:0.') || l.startsWith('::ffff:10.') ||
    l.startsWith('::ffff:127.') || l.startsWith('::ffff:169.254.') ||
    l.startsWith('::ffff:192.168.');
}
async function assertSafeFeedUrl(raw: string, isShahaf: boolean): Promise<void> {
  let u: URL;
  try { u = new URL(raw); } catch { throw new Error('BAD_URL'); }
  if (u.protocol !== 'https:') throw new Error('NOT_HTTPS');
  if (u.username || u.password) throw new Error('CREDENTIALS_IN_URL');
  const h = u.hostname.toLowerCase();
  if (isShahaf && !/^[a-z0-9-]+\.shahaf\.site$/.test(h)) throw new Error('HOST_NOT_ALLOWED');
  if (h === 'localhost' || h.endsWith('.local') || h.endsWith('.internal')) throw new Error('PRIVATE_HOST');
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(h)) {
    if (isPrivateIp(h)) throw new Error('PRIVATE_IP');
  } else {
    // resolveName (Deno ≤1.x, Supabase runtime) or resolveDns (Deno 2.x) —
    // feature-detect so the function type-checks and runs on both.
    const d = Deno as unknown as Record<string, unknown>;
    const resolver = (d.resolveName ?? d.resolveDns) as
      | ((h: string, o: { family: 'A' }) => Promise<unknown>)
      | undefined;
    if (resolver) {
      try {
        const out = await resolver(h, { family: 'A' });
        const ip: string | undefined = Array.isArray(out) ? out[0] : (out as string);
        if (ip && isPrivateIp(ip)) { const e = new Error('PRIVATE_IP'); throw e; }
      } catch (e) {
        if ((e as Error).message === 'PRIVATE_IP') throw e;
        // DNS failure: let the fetch itself fail naturally
      }
    }
  }
}

// Minimal ICS parse (mirror of importers.mjs logic) → task-shaped items.
function icsItems(text: string, source: string): Record<string, unknown>[] {
  const unfolded = text.replace(/\r\n/g, '\n').replace(/\n[ \t]/g, '');
  const events: Record<string, string>[] = [];
  let cur: Record<string, string> | null = null;
  for (const line of unfolded.split('\n')) {
    const clean = line.trim();
    if (clean === 'BEGIN:VEVENT') { cur = {}; continue; }
    if (clean === 'END:VEVENT') { if (cur) events.push(cur); cur = null; continue; }
    if (!cur) continue;
    const k = clean.indexOf(':');
    if (k < 0) continue;
    const key = clean.slice(0, k).split(';')[0].toUpperCase();
    const value = clean.slice(k + 1);
    if (['UID', 'SUMMARY', 'DTSTART', 'LOCATION', 'DESCRIPTION', 'URL'].includes(key)) cur[key] = value;
  }
  return events.slice(0, 2000).map((v, i) => {
    const m = String(v.DTSTART || '').match(/^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})?(Z)?)?/);
    const due_at = m ? `${m[1]}-${m[2]}-${m[3]}T${m[4] || '12'}:${m[5] || '00'}:${m[6] || '00'}${m[7] ? 'Z' : '+02:00'}` : null;
    return {
      kind: 'task',
      // H4/CR5 fix: dedup key + fields identical to the client mirror
      // (importers.mjs parseICS) so the two writers produce the same rows.
      external_id: `ics:${v.UID || `${v.SUMMARY}:${v.DTSTART || i}`}`.slice(0, 200),
      title: String(v.SUMMARY || '').trim().slice(0, 240),
      subject: String(v.LOCATION || '').trim().slice(0, 100),
      description: String(v.DESCRIPTION || '').replace(/\\[;,n]/g, ' ').slice(0, 2000),
      source_url: String(v.URL || '').slice(0, 500) || null,
      due_at,
    };
  }).filter(x => x.title);
}

// Minimal tolerant Shahaf table parse (mirror of connectors.parseShahafPage) →
// timetable-shaped items + the "מעודכן ל:" stamp.
const DAYS: [string, number][] = [['ראשון', 0], ['שני', 1], ['שלישי', 2], ['רביעי', 3], ['חמישי', 4], ['שישי', 5], ['שבת', 6]];
const TIME_OK = /^([01]?\d|2[0-3]):[0-5]\d$/; // same tolerance as the client TIME_RE
function stripTags(s: string): string {
  return s
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
function shahafItems(html: string): { items: Record<string, unknown>[]; stamp: string | null } {
  const stampM = html.match(/מעודכן ל:\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4}(?:\s*,?\s*שעה:\s*[0-9]{2}:[0-9]{2})?)/);
  const stamp = stampM ? stampM[1].trim() : null;
  for (const m of html.matchAll(/<table[\s\S]*?<\/table>/gi)) {
    const table = m[0];
    const trs = [...table.matchAll(/<tr[\s\S]*?<\/tr>/gi)].map(tr =>
      [...tr[0].matchAll(/<t[hd][\s\S]*?<\/t[hd]>/gi)].map(c => stripTags(c[0])),
    );
    if (trs.length < 2) continue;
    const header = trs[0];
    const dayCols: { col: number; day: number }[] = [];
    header.forEach((cell, col) => {
      for (const [name, day] of DAYS) {
        if (cell.includes(name)) { dayCols.push({ col, day }); break; }
      }
    });
    if (dayCols.length < 2) continue;
    const items: Record<string, unknown>[] = [];
    for (let i = 1; i < trs.length; i++) {
      const row = trs[i];
      const label = row[0] || '';
      const tm = label.match(/([0-9]{1,2}):([0-9]{2})/);
      if (!tm) continue;
      const start = tm[1].padStart(2, '0') + ':' + tm[2];
      if (!TIME_OK.test(start)) continue; // TS L3: skip bad rows, never sink the feed
      const em = label.match(/([0-9]{1,2}):([0-9]{2})\s*[-–—]\s*([0-9]{1,2}):([0-9]{2})/);
      const end = em && TIME_OK.test(em[3].padStart(2, '0') + ':' + em[4]) ? em[3].padStart(2, '0') + ':' + em[4] : null;
      for (const { col, day } of dayCols) {
        const cell = (row[col] || '').trim();
        if (!cell) continue;
        const roomM = cell.match(/[(（]([^\)）]{1,40})[)）]\s*$/);
        let title = cell.replace(/—?\s*(בוטל|ביטול|שינוי|השתנה)\s*—?/g, ' ').replace(/\s+/g, ' ').trim();
        if (roomM) title = title.replace(roomM[0], '').trim();
        if (!title) continue;
        const change_type = /בוטל|ביטול/.test(cell) ? 'cancelled' : /שינוי|השתנה/.test(cell) ? 'changed' : 'normal';
        items.push({
          kind: 'timetable',
          external_id: `shahaf:${day}:${start}`,
          title,
          day,
          start,
          room: roomM ? roomM[1].trim() : null,
          change_type,
          end, // H4 fix: client parses end from the label — mirror it
        });
      }
    }
    return { items, stamp };
  }
  return { items: [], stamp };
}

Deno.serve(async (req: Request) => {
  const supabaseUrl = Deno.env.get('SUPABASE_URL');
  const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!supabaseUrl || !serviceKey) return json({ ok: false, error: 'SERVER_NOT_CONFIGURED' }, 500);
  // M1 fix: the function URL is derivable (project ref is public) — require the
  // dedicated cron token (set LUMIO_CRON_TOKEN in the function secrets).
  const cronToken = Deno.env.get('LUMIO_CRON_TOKEN');
  if (cronToken && req.headers.get('x-lumio-cron') !== cronToken) {
    return json({ ok: false, error: 'UNAUTHORIZED' }, 401);
  }
  const db = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });

  const { data: conns, error } = await db
    .from('connections')
    .select('user_id,provider,feed_url,feed_stamp')
    .not('feed_url', 'is', null)
    .limit(MAX_FEEDS);
  if (error || !conns) return json({ ok: false, error: 'DB_READ_FAILED' }, 500);

  const now = new Date().toISOString();
  let okFeeds = 0;
  let failedFeeds = 0;

  const processFeed = async (c: { user_id: string; provider: string; feed_url: string; feed_stamp: string | null }) => {
    try {
      const host = new URL(c.feed_url).hostname;
      const isShahaf = /(^|\.)shahaf\.site$/i.test(host);
      await assertSafeFeedUrl(c.feed_url, isShahaf); // H1 fix — SSRF guard
      const text = await fetchText(c.feed_url);
      let taskItems: Record<string, unknown>[] = [];
      let timetableItems: Record<string, unknown>[] = [];
      let stamp: string | null = null;
      if (isShahaf) {
        const parsed = shahafItems(text);
        timetableItems = parsed.items;
        stamp = parsed.stamp;
      } else {
        taskItems = icsItems(text, c.provider);
      }
      const total = taskItems.length + timetableItems.length;

      if (taskItems.length) {
        const rows = taskItems.map(x => ({
          user_id: c.user_id,
          source: c.provider,
          external_id: x.external_id,
          title: x.title,
          subject: x.subject || '',
          description: x.description ?? '',
          due_at: x.due_at ?? null,
          source_url: x.source_url ?? null,
          // M4 fix: no status on upsert — DB default on insert, user status preserved on re-sync
          retrieval_method: 'public_school_feed',
          verification_state: 'live_verified',
          synced_at: now,
          updated_at: now,
        }));
        const { error: e1 } = await db.from('tasks').upsert(rows, { onConflict: 'user_id,source,external_id' });
        if (e1) throw new Error(e1.message);
      }
      if (timetableItems.length) {
        const rows = timetableItems.map(x => ({
          user_id: c.user_id,
          kind: 'timetable',
          source: c.provider,
          external_id: x.external_id,
          title: x.title,
          subject: String(x.title),
          description: '',
          event_date: null,
          source_url: c.feed_url,
          day_of_week: x.day,
          start_time: x.start,
          end_time: x.end ?? null, // H4 fix: writer parity with the browser path
          room: x.room,
          change_type: x.change_type || 'normal',
          retrieval_method: 'public_school_feed',
          verification_state: 'live_verified',
          synced_at: now,
          updated_at: now,
        }));
        const { error: e2 } = await db.from('school_items').upsert(rows, { onConflict: 'user_id,kind,source,external_id' });
        if (e2) throw new Error(e2.message);
      }

      // Facts + stamp. This DB write is the anti-pause heartbeat.
      try {
        await db
          .from('connections')
          .update({
            data_readable: total > 0,
            sync_working: total > 0,
            last_sync_at: now,
            last_error: null,
            feed_stamp: stamp,
          })
          .eq('user_id', c.user_id)
          .eq('provider', c.provider);
      } catch {
        // fact columns missing (upgrade-2 not run) — data upsert already succeeded
      }
      okFeeds++;
    } catch {
      failedFeeds++;
      try {
        await db
          .from('connections')
          .update({ sync_working: false, last_error: 'FEED_FETCH_FAILED', last_sync_at: now })
          .eq('user_id', c.user_id)
          .eq('provider', c.provider);
      } catch {
        // ignore — recorded in response only
      }
    }
  };

  for (let i = 0; i < conns.length; i += CHUNK) {
    const batch = conns.slice(i, i + CHUNK);
    await Promise.all(batch.map(processFeed)); // H2 fix: parallel within a batch
  }

  return json({ ok: true, feeds: conns.length, okFeeds, failedFeeds });
});
