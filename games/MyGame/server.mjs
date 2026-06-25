/**
 * server.mjs — Standalone WebSocket party server.
 * Deploy this separately on Railway / Render / Fly.io.
 * The static game files stay on Vercel.
 */
import http from 'node:http';
import os   from 'node:os';
import { WebSocketServer, WebSocket } from 'ws';

const port = Number(process.env.PORT || 3001);

// ── HTTP (health-check for hosting platforms) ──────────────────
const httpServer = http.createServer((req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/plain',
    'Access-Control-Allow-Origin': '*',
  });
  res.end('Dungeon Crawler WS Server — OK\n');
});

// ── Party state ────────────────────────────────────────────────
const rooms  = new Map();  // code → { hostId, players: Map<id,ws> }
const wsInfo = new Map();  // ws  → { code, playerId }

function genCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
  let code;
  do { code = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join(''); }
  while (rooms.has(code));
  return code;
}

function genId() { return Math.random().toString(36).slice(2, 10); }

function send(ws, obj) {
  if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj));
}

function broadcast(room, obj, excludeWs = null) {
  const data = JSON.stringify(obj);
  for (const ws of room.players.values())
    if (ws !== excludeWs && ws.readyState === WebSocket.OPEN) ws.send(data);
}

// ── WebSocket server ───────────────────────────────────────────
const wss = new WebSocketServer({ server: httpServer, path: '/ws' });

// ── Heartbeat: ping every 25 s, drop unresponsive clients ──────
const PING_INTERVAL = 25_000;
setInterval(() => {
  for (const ws of wss.clients) {
    if (ws.isAlive === false) { ws.terminate(); continue; }
    ws.isAlive = false;
    ws.ping();
  }
}, PING_INTERVAL);

wss.on('connection', (ws) => {
  const playerId = genId();
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });

  ws.on('message', (raw) => {
    let msg; try { msg = JSON.parse(raw); } catch { return; }

    switch (msg.type) {
      case 'create_party': {
        const code = genCode();
        const room = { hostId: playerId, players: new Map([[playerId, ws]]), openedChests: new Set() };
        rooms.set(code, room);
        wsInfo.set(ws, { code, playerId });
        send(ws, { type: 'party_created', code, playerId, playerIndex: 0 });
        console.log(`[+] Room ${code} created`);
        break;
      }
      case 'join_party': {
        const code = msg.code?.trim().toUpperCase();
        const room = rooms.get(code);
        if (!room)               { send(ws, { type: 'error', msg: 'Party not found' }); return; }
        if (room.players.size >= 4) { send(ws, { type: 'error', msg: 'Party is full (max 4)' }); return; }
        const playerIndex = room.players.size;
        room.players.set(playerId, ws);
        wsInfo.set(ws, { code, playerId });
        send(ws, { type: 'party_joined', code, playerId, playerIndex, playerCount: room.players.size });
        broadcast(room, { type: 'player_joined', playerId, playerIndex, playerCount: room.players.size }, ws);
        console.log(`[+] ${playerId} joined ${code} (${room.players.size}/4)`);
        break;
      }
      case 'start_game': {
        const info = wsInfo.get(ws); if (!info) return;
        const room = rooms.get(info.code);
        if (!room || room.hostId !== info.playerId) return;
        const payload = { type: 'game_started', seed: msg.seed, difficulty: msg.difficulty };
        broadcast(room, payload, ws);
        send(ws, payload);
        console.log(`[>] Game started in ${info.code} seed=${msg.seed}`);
        break;
      }
      case 'player_update': {
        const info = wsInfo.get(ws); if (!info) return;
        const room = rooms.get(info.code); if (!room) return;
        // Sanity-check position to prevent spoofed/corrupt updates from
        // poisoning remote player rendering. Map bounds: 80*32=2560 x 56*32=1792.
        const state = msg.state || {};
        const x = state.x, y = state.y;
        if (typeof x !== 'number' || typeof y !== 'number' ||
            isNaN(x) || isNaN(y) ||
            x < 0 || x > 2560 || y < 0 || y > 1792) break;
        broadcast(room, { type: 'player_update', playerId: info.playerId, state: msg.state }, ws);
        break;
      }
      case 'game_event': {
        const info = wsInfo.get(ws); if (!info) return;
        const room = rooms.get(info.code); if (!room) return;
        // Deduplicate chest opens: only the first opener's event is forwarded.
        // Subsequent simultaneous requests are silently dropped so no second
        // player can receive a duplicate item grant.
        if (msg.event === 'chest_opened') {
          const chestId = msg.data?.chestId;
          if (!chestId || room.openedChests.has(chestId)) break;
          room.openedChests.add(chestId);
        }
        broadcast(room, { type: 'game_event', playerId: info.playerId, event: msg.event, data: msg.data }, ws);
        break;
      }
    }
  });

  ws.on('close', () => {
    const info = wsInfo.get(ws); if (!info) return;
    const { code, playerId: pid } = info;
    const room = rooms.get(code);
    if (room) {
      room.players.delete(pid);
      broadcast(room, { type: 'player_left', playerId: pid });
      if (room.players.size === 0) { rooms.delete(code); console.log(`[-] Room ${code} closed`); }
      else if (room.hostId === pid) {
        room.hostId = room.players.keys().next().value;
        broadcast(room, { type: 'host_changed', hostId: room.hostId });
      }
    }
    wsInfo.delete(ws);
  });
});

httpServer.listen(port, () => {
  const nets = os.networkInterfaces();
  let localIp = 'localhost';
  for (const ifaces of Object.values(nets)) {
    const hit = ifaces.find(a => a.family === 'IPv4' && !a.internal);
    if (hit) { localIp = hit.address; break; }
  }
  console.log(`\n🎮 WS Party Server`);
  console.log(`   Local:   ws://localhost:${port}/ws`);
  console.log(`   Network: ws://${localIp}:${port}/ws`);
  console.log(`   Health:  http://localhost:${port}\n`);
});
