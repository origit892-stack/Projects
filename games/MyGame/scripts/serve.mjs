/**
 * serve.mjs — Dev server with WebSocket support for online multiplayer.
 * Run: npm run dev
 */
import http  from 'node:http';
import { readFile } from 'node:fs/promises';
import path  from 'node:path';
import { fileURLToPath } from 'node:url';
import { WebSocketServer, WebSocket } from 'ws';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root      = path.resolve(__dirname, '..');
const port      = Number(process.env.PORT || 4173);

const mime = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
};

// ── HTTP server (file serving) ─────────────────────────────────────────────
const server = http.createServer(async (req, res) => {
  const urlPath = req.url === '/' ? '/index.html' : req.url.split('?')[0];
  const filePath = path.join(root, urlPath);
  try {
    const data = await readFile(filePath);
    const ext  = path.extname(filePath);
    res.writeHead(200, { 'Content-Type': mime[ext] || 'application/octet-stream' });
    res.end(data);
  } catch {
    res.writeHead(404);
    res.end('Not found');
  }
});

// ── Party state ────────────────────────────────────────────────────────────
// rooms: Map<code, { hostId: string, players: Map<playerId, ws> }>
const rooms     = new Map();
const wsInfo    = new Map(); // ws → { code, playerId }

function genCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
  let code;
  do {
    code = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
  } while (rooms.has(code));
  return code;
}

function genId() {
  return Math.random().toString(36).slice(2, 10);
}

function send(ws, obj) {
  if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj));
}

function broadcast(room, obj, excludeWs = null) {
  const data = JSON.stringify(obj);
  for (const ws of room.players.values()) {
    if (ws !== excludeWs && ws.readyState === WebSocket.OPEN) ws.send(data);
  }
}

// ── WebSocket server ───────────────────────────────────────────────────────
const wss = new WebSocketServer({ server, path: '/ws' });

wss.on('connection', (ws) => {
  const playerId = genId();

  ws.on('message', (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }

    switch (msg.type) {

      case 'create_party': {
        const code = genCode();
        const room = { hostId: playerId, players: new Map([[playerId, ws]]) };
        rooms.set(code, room);
        wsInfo.set(ws, { code, playerId });
        send(ws, { type: 'party_created', code, playerId, playerIndex: 0 });
        console.log(`[Party] Created ${code} by ${playerId}`);
        break;
      }

      case 'join_party': {
        const code = msg.code?.trim().toUpperCase();
        const room = rooms.get(code);
        if (!room) {
          send(ws, { type: 'error', msg: 'Party not found' });
          return;
        }
        if (room.players.size >= 4) {
          send(ws, { type: 'error', msg: 'Party is full (max 4)' });
          return;
        }
        const playerIndex = room.players.size;
        room.players.set(playerId, ws);
        wsInfo.set(ws, { code, playerId });
        send(ws, { type: 'party_joined', code, playerId, playerIndex, playerCount: room.players.size });
        broadcast(room, { type: 'player_joined', playerId, playerIndex, playerCount: room.players.size }, ws);
        console.log(`[Party] ${playerId} joined ${code} (${room.players.size}/4)`);
        break;
      }

      case 'start_game': {
        const info = wsInfo.get(ws);
        if (!info) return;
        const room = rooms.get(info.code);
        if (!room || room.hostId !== info.playerId) return;
        const payload = { type: 'game_started', seed: msg.seed, difficulty: msg.difficulty };
        broadcast(room, payload);        // non-host players
        send(ws, payload);              // host too
        console.log(`[Party] Game started in ${info.code} — seed ${msg.seed}`);
        break;
      }

      case 'player_update': {
        const info = wsInfo.get(ws);
        if (!info) return;
        const room = rooms.get(info.code);
        if (!room) return;
        broadcast(room, { type: 'player_update', playerId: info.playerId, state: msg.state }, ws);
        break;
      }

      case 'game_event': {
        const info = wsInfo.get(ws);
        if (!info) return;
        const room = rooms.get(info.code);
        if (!room) return;
        broadcast(room, { type: 'game_event', playerId: info.playerId, event: msg.event, data: msg.data }, ws);
        break;
      }
    }
  });

  ws.on('close', () => {
    const info = wsInfo.get(ws);
    if (!info) return;
    const { code, playerId: pid } = info;
    const room = rooms.get(code);
    if (room) {
      room.players.delete(pid);
      broadcast(room, { type: 'player_left', playerId: pid });
      if (room.players.size === 0) {
        rooms.delete(code);
        console.log(`[Party] Room ${code} closed`);
      } else if (room.hostId === pid) {
        room.hostId = room.players.keys().next().value;
        broadcast(room, { type: 'host_changed', hostId: room.hostId });
        console.log(`[Party] Host transferred in ${code} to ${room.hostId}`);
      }
    }
    wsInfo.delete(ws);
  });
});

// ── Start ──────────────────────────────────────────────────────────────────
import os from 'node:os';

function getLocalIp() {
  for (const ifaces of Object.values(os.networkInterfaces())) {
    const hit = ifaces.find(a => a.family === 'IPv4' && !a.internal);
    if (hit) return hit.address;
  }
  return 'localhost';
}

server.listen(port, '0.0.0.0', () => {
  const localIp = getLocalIp();
  console.log(`\n🎮 Dungeon Crawler server running`);
  console.log(`   Local:   http://localhost:${port}`);
  console.log(`   Network: http://${localIp}:${port}  ← share with friends on same Wi-Fi\n`);
});
