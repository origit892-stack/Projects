// Lumio 4.0 — Supabase Edge Function: apps-script-ingest
// Deploy to your own Supabase project (steps in supabase-functions/README-HE.md).
//
// Receives POST {key, items[]} from the student-owned Apps Script.
// The user_id is ALWAYS taken from the connections row matched by apps_script_key
// (unique) — a client-supplied user_id is never trusted.
// No secrets in this file: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY come from the
// function environment, which the Supabase runtime injects (service role).

import { createClient } from 'npm:@supabase/supabase-js@2';

const MAX_ITEMS = 500;
const ALLOWED_ITEM_KINDS = new Set(['task', 'grade']);
// Sources this endpoint accepts. 'classroom' is the Apps Script template
// (official API). The rest are student-local sync scripts pushing with the
// student's own account — labeled honestly as local_sync downstream.
const ALLOWED_SOURCES = new Set(['classroom', 'mashov', 'ofek', 'petel']);

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

Deno.serve(async (req: Request) => {
  if (req.method !== 'POST') return json({ ok: false, error: 'METHOD_NOT_ALLOWED' }, 405);

  const supabaseUrl = Deno.env.get('SUPABASE_URL');
  const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!supabaseUrl || !serviceKey) return json({ ok: false, error: 'SERVER_NOT_CONFIGURED' }, 500);
  const db = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });

  // L3 fix: size-cap the raw body before parsing (self-DoS guard).
  const MAX_BODY_BYTES = 1_500_000;
  const cl = Number(req.headers.get('content-length') || 0);
  if (cl > MAX_BODY_BYTES) return json({ ok: false, error: 'BODY_TOO_LARGE' }, 413);
  let rawBody = '';
  try {
    rawBody = await req.text();
  } catch {
    return json({ ok: false, error: 'BAD_BODY' }, 400);
  }
  if (rawBody.length > MAX_BODY_BYTES) return json({ ok: false, error: 'BODY_TOO_LARGE' }, 413);
  let body: any;
  try {
    body = JSON.parse(rawBody);
  } catch {
    return json({ ok: false, error: 'BAD_BODY' }, 400);
  }

  const syncKey = typeof body?.key === 'string' ? body.key.trim() : '';
  const rawItems: unknown[] = Array.isArray(body?.items) ? body.items : [];
  const partial = rawItems.length > MAX_ITEMS;
  const items = rawItems.slice(0, MAX_ITEMS);
  // Source: who is pushing. Untrusted — whitelist, default 'classroom'
  // (backward compatible with the Apps Script template).
  const source = ALLOWED_SOURCES.has(typeof body?.source === 'string' ? body.source : '')
    ? body.source as string
    : 'classroom';
  const retrievalMethod = source === 'classroom' ? 'official_api' : 'local_sync';

  // Binding lookup: the key identifies the connection row; its user_id is the only
  // user this function may write to. Missing key or a disconnected source → 401.
  const { data: conn, error: connErr } = await db
    .from('connections')
    .select('user_id,provider,state')
    .eq('apps_script_key', syncKey)
    .maybeSingle();
  if (connErr || !conn || conn.state === 'not_connected') {
    return json({ ok: false, error: 'LUMIO_BINDING_INVALID' }, 401);
  }

  const userId: string = conn.user_id; // never from the client
  const now = new Date().toISOString();
  const taskRows: Record<string, unknown>[] = [];
  const gradeRows: Record<string, unknown>[] = [];

  for (const it of items) {
    if (!it || typeof it !== 'object') continue;
    const item = it as Record<string, unknown>;
    const kind = typeof item.kind === 'string' ? item.kind : 'task';
    if (!ALLOWED_ITEM_KINDS.has(kind)) continue;
    const external_id =
      typeof item.external_id === 'string' && item.external_id.trim() ? item.external_id.trim().slice(0, 200) : null;
    const title = typeof item.title === 'string' ? item.title.trim().slice(0, 240) : '';
    if (!external_id || !title) continue;
    const subject = typeof item.course_title === 'string' ? item.course_title.trim().slice(0, 100) : '';

    if (kind === 'grade') {
      const score = Number(item.score ?? item.assignedGrade);
      if (!Number.isFinite(score) || score < 0 || score > 100) continue;
      gradeRows.push({
        user_id: userId,
        kind: 'grade',
        source,
        external_id,
        title,
        subject,
        description: '',
        event_date: null,
        score,
        source_url: null,
        retrieval_method: retrievalMethod,
        verification_state: 'live_verified',
        synced_at: now,
        updated_at: now,
      });
    } else {
      taskRows.push({
        user_id: userId,
        source,
        external_id,
        title,
        subject,
        description: '',
        // L2 fix: validate/normalize due_at — garbage must not sink the batch.
        due_at: (() => { const d = new Date(item.due_at as string); return item.due_at && !Number.isNaN(d.getTime()) ? d.toISOString() : null; })(),
        source_url: null,
        status: item.status === 'done' ? 'done' : 'todo',
        retrieval_method: retrievalMethod,
        verification_state: 'live_verified',
        synced_at: now,
        updated_at: now,
      });
    }
  }

  if (taskRows.length) {
    const { error } = await db.from('tasks').upsert(taskRows, { onConflict: 'user_id,source,external_id' });
    if (error) return json({ ok: false, error: 'DB_TASKS_FAILED' }, 500);
  }
  if (gradeRows.length) {
    const { error } = await db.from('school_items').upsert(gradeRows, { onConflict: 'user_id,kind,source,external_id' });
    if (error) return json({ ok: false, error: 'DB_GRADES_FAILED' }, 500);
  }

  // Facts + last_sync. Wrapped: if the fact columns are not there yet
  // (upgrade-2 not run) the data was already saved — do not fail the run.
  try {
    await db
      .from('connections')
      .update({
        // MAJOR-2 fix: the daily sync succeeded — the state must say so,
        // otherwise the card shows "awaiting consent" next to four ✓ facts.
        state: 'synced',
        identity_authenticated: true,
        permission_granted: true,
        data_readable: true,
        sync_working: true,
        last_sync_at: now,
        last_error: null,
      })
      .eq('user_id', userId)
      .eq('provider', source);
  } catch {
    // fact columns missing — data upsert above already succeeded
  }

  return json({ ok: true, saved: { tasks: taskRows.length, grades: gradeRows.length }, partial });
});
