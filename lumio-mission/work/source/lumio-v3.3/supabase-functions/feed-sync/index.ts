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
const CHUNK = 10; // feeds processed per batch; keeps a run well under 150s at 100 users

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
    if (['UID', 'SUMMARY', 'DTSTART', 'LOCATION'].includes(key)) cur[key] = value;
  }
  return events.slice(0, 2000).map((v, i) => {
    const m = String(v.DTSTART || '').match(/^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})?(Z)?)?/);
    const due_at = m ? `${m[1]}-${m[2]}-${m[3]}T${m[4] || '12'}:${m[5] || '00'}:${m[6] || '00'}${m[7] ? 'Z' : '+02:00'}` : null;
    return {
      kind: 'task',
      external_id: `ics:${v.UID || v.SUMMARY || i}`,
      title: String(v.SUMMARY || '').trim(),
      subject: String(v.LOCATION || '').trim(),
      due_at,
    };
  }).filter(x => x.title);
}

// Minimal tolerant Shahaf table parse (mirror of connectors.parseShahafPage) →
// timetable-shaped items + the "מעודכן ל:" stamp.
const DAYS: [string, number][] = [['ראשון', 0], ['שני', 1], ['שלישי', 2], ['רביעי', 3], ['חמישי', 4], ['שישי', 5], ['שבת', 6]];
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

  for (let i = 0; i < conns.length; i += CHUNK) {
    const batch = conns.slice(i, i + CHUNK);
    for (const c of batch) {
      try {
        const host = new URL(c.feed_url).hostname;
        const isShahaf = /(^|\.)shahaf\.site$/i.test(host);
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
            description: '',
            due_at: x.due_at ?? null,
            source_url: null,
            status: 'todo',
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
            end_time: null,
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
    }
  }

  return json({ ok: true, feeds: conns.length, okFeeds, failedFeeds });
});
