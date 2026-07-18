import http from 'node:http';
import crypto from 'node:crypto';
import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

const HOST = '127.0.0.1';
const PORT = Number(process.env.PORT || 5057);
const STATE_FILE = process.env.STATE_FILE || '/var/lib/europa-park-sync/state.json';
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '';
const clients = new Map();
let state = { schema: 2, version: 0, updatedAt: null, profiles: {} };

function cleanName(value) {
  if (typeof value !== 'string') return '';
  return value.trim().replace(/\s+/g, ' ').slice(0, 60);
}

function profileIdFor(name) {
  return crypto.createHash('sha256').update(name.toLocaleLowerCase('he-IL')).digest('hex').slice(0, 24);
}

function validRide(value) {
  return typeof value === 'string' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value) && value.length <= 120;
}

function cleanSelections(input) {
  const clean = {};
  if (!input || typeof input !== 'object') return clean;
  for (const [ride, checked] of Object.entries(input)) {
    if (validRide(ride) && typeof checked === 'boolean') clean[ride] = checked;
  }
  return clean;
}

function makeProfile(name, selections = {}) {
  const id = profileIdFor(name);
  return { id, name, version: 0, updatedAt: null, selections: cleanSelections(selections) };
}

function migrateLegacy(parsed) {
  if (parsed?.schema === 2 && parsed.profiles) return parsed;
  const migrated = { schema: 2, version: Number(parsed?.version || 0), updatedAt: parsed?.updatedAt || null, profiles: {} };
  const legacyPeople = { ori: 'אורי', roni: 'רוני', shaked: 'שקד' };
  for (const [person, name] of Object.entries(legacyPeople)) {
    const selections = {};
    for (const [ride, values] of Object.entries(parsed?.selections || {})) {
      if (typeof values?.[person] === 'boolean') selections[ride] = values[person];
    }
    if (Object.keys(selections).length) {
      const profile = makeProfile(name, selections);
      profile.version = 1;
      profile.updatedAt = parsed.updatedAt || new Date().toISOString();
      migrated.profiles[profile.id] = profile;
    }
  }
  return migrated;
}

async function loadState() {
  try {
    state = migrateLegacy(JSON.parse(await readFile(STATE_FILE, 'utf8')));
    await persist();
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
}

async function persist() {
  await mkdir(dirname(STATE_FILE), { recursive: true });
  const temporary = `${STATE_FILE}.tmp`;
  await writeFile(temporary, JSON.stringify(state), { mode: 0o600 });
  await rename(temporary, STATE_FILE);
}

function headers(type = 'application/json; charset=utf-8') {
  return { 'Content-Type': type, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' };
}

function respond(res, status, payload) {
  res.writeHead(status, headers());
  res.end(JSON.stringify(payload));
}

async function readJson(req) {
  let body = '';
  for await (const chunk of req) {
    body += chunk;
    if (body.length > 250_000) throw new Error('payload_too_large');
  }
  return JSON.parse(body || '{}');
}

function publicProfile(profile) {
  return { id: profile.id, name: profile.name, version: profile.version, updatedAt: profile.updatedAt, selections: profile.selections };
}

function bump(profile) {
  const now = new Date().toISOString();
  state.version += 1;
  state.updatedAt = now;
  profile.version += 1;
  profile.updatedAt = now;
}

function broadcast(profile) {
  const message = `data: ${JSON.stringify(publicProfile(profile))}\n\n`;
  for (const client of clients.get(profile.id) || []) client.write(message);
}

function isAdmin(req) {
  if (!ADMIN_TOKEN) return false;
  const supplied = String(req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  const a = Buffer.from(supplied), b = Buffer.from(ADMIN_TOKEN);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function adminState() {
  return {
    version: state.version,
    updatedAt: state.updatedAt,
    profiles: Object.values(state.profiles).map(publicProfile).sort((a, b) => a.name.localeCompare(b.name, 'he')),
  };
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://${req.headers.host || HOST}`);
    if (req.method === 'GET' && url.pathname === '/health') return respond(res, 200, { ok: true, version: state.version, profiles: Object.keys(state.profiles).length });

    if (req.method === 'POST' && url.pathname === '/profile') {
      const body = await readJson(req);
      const name = cleanName(body.name);
      if (name.length < 2) return respond(res, 400, { error: 'invalid_name' });
      const id = profileIdFor(name);
      let profile = state.profiles[id];
      if (!profile) {
        profile = makeProfile(name);
        state.profiles[id] = profile;
        bump(profile);
        await persist();
      }
      return respond(res, 200, publicProfile(profile));
    }

    if (req.method === 'GET' && url.pathname === '/events') {
      const id = url.searchParams.get('profile') || '';
      const profile = state.profiles[id];
      if (!profile) return respond(res, 404, { error: 'profile_not_found' });
      res.writeHead(200, { ...headers('text/event-stream; charset=utf-8'), Connection: 'keep-alive', 'X-Accel-Buffering': 'no' });
      res.write(`retry: 2500\ndata: ${JSON.stringify(publicProfile(profile))}\n\n`);
      if (!clients.has(id)) clients.set(id, new Set());
      clients.get(id).add(res);
      req.on('close', () => {
        clients.get(id)?.delete(res);
        if (!clients.get(id)?.size) clients.delete(id);
      });
      return;
    }

    if (req.method === 'POST' && url.pathname === '/select') {
      const body = await readJson(req);
      const profile = state.profiles[body.profileId];
      if (!profile || !validRide(body.ride) || typeof body.checked !== 'boolean') return respond(res, 400, { error: 'invalid_selection' });
      profile.selections[body.ride] = body.checked;
      bump(profile); await persist(); broadcast(profile);
      return respond(res, 200, publicProfile(profile));
    }

    if (req.method === 'POST' && url.pathname === '/reset') {
      const body = await readJson(req);
      const profile = state.profiles[body.profileId];
      if (!profile || body.confirm !== 'reset') return respond(res, 400, { error: 'confirmation_required' });
      profile.selections = {};
      bump(profile); await persist(); broadcast(profile);
      return respond(res, 200, publicProfile(profile));
    }

    if (req.method === 'GET' && url.pathname === '/admin/state') {
      if (!isAdmin(req)) return respond(res, 401, { error: 'unauthorized' });
      return respond(res, 200, adminState());
    }

    respond(res, 404, { error: 'not_found' });
  } catch (error) {
    console.error(error);
    respond(res, error.message === 'payload_too_large' ? 413 : 400, { error: 'bad_request' });
  }
});

await loadState();
server.listen(PORT, HOST, () => console.log(`Europa-Park profiles API listening on http://${HOST}:${PORT}`));

function shutdown() {
  for (const group of clients.values()) for (const client of group) client.end();
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(1), 5000).unref();
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
