/**
 * multiplayer.js — WebSocket client for party-based online play.
 * Singleton: import { multiplayer } from './multiplayer.js'
 */

export class MultiplayerManager {
  constructor() {
    this.ws          = null;
    this.partyCode   = null;
    this.playerId    = null;
    this.playerIndex = 0;
    this.isHost      = false;
    this.players     = new Map();   // playerId → last state
    this._cbs        = {};
    this._interval   = null;
  }

  // ── Event emitter ──────────────────────────────────────────────
  on(event, cb) { this._cbs[event] = cb; }
  _emit(event, data) { this._cbs[event]?.(data); }

  // ── Connect to server WebSocket ────────────────────────────────
  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host  = window.MP_SERVER_HOST || window.location.host;
      const url   = `${proto}//${host}/ws`;
      this.ws = new WebSocket(url);
      this.ws.onopen    = () => resolve();
      this.ws.onerror   = () => reject(new Error('WebSocket connection failed'));
      this.ws.onclose   = () => this._emit('disconnect', {});
      this.ws.onmessage = (e) => this._handle(JSON.parse(e.data));
    });
  }

  // ── Send helpers ───────────────────────────────────────────────
  _send(type, payload = {}) {
    if (this.ws?.readyState === WebSocket.OPEN)
      this.ws.send(JSON.stringify({ type, ...payload }));
  }

  createParty()              { this._send('create_party'); }
  joinParty(code)            { this._send('join_party', { code }); }
  startGame(seed, difficulty){ this._send('start_game', { seed, difficulty }); }
  sendEvent(event, data = {}) { this._send('game_event', { event, data }); }

  // ── Position broadcasting (30 ticks/sec) ──────────────────────
  startSendingUpdates(getStateFn) {
    clearInterval(this._interval);
    this._interval = setInterval(() => {
      this._send('player_update', { state: getStateFn() });
    }, 33);
  }

  stopSendingUpdates() {
    clearInterval(this._interval);
    this._interval = null;
  }

  disconnect() {
    this.stopSendingUpdates();
    this.ws?.close();
    this.ws        = null;
    this.partyCode = null;
    this.playerId  = null;
    this.isHost    = false;
    this.players.clear();
  }

  // ── Message router ─────────────────────────────────────────────
  _handle(msg) {
    switch (msg.type) {
      case 'party_created':
        this.partyCode   = msg.code;
        this.playerId    = msg.playerId;
        this.playerIndex = 0;
        this.isHost      = true;
        this._emit('party_created', msg);
        break;

      case 'party_joined':
        this.partyCode   = msg.code;
        this.playerId    = msg.playerId;
        this.playerIndex = msg.playerIndex;
        this.isHost      = false;
        this._emit('party_joined', msg);
        break;

      case 'player_joined':
        this._emit('player_joined', msg);
        break;

      case 'player_left':
        this.players.delete(msg.playerId);
        this._emit('player_left', msg);
        break;

      case 'host_changed':
        if (msg.hostId === this.playerId) this.isHost = true;
        this._emit('host_changed', msg);
        break;

      case 'game_started':
        this._emit('game_started', msg);
        break;

      case 'player_update':
        this.players.set(msg.playerId, msg.state);
        this._emit('player_update', msg);
        break;

      case 'game_event':
        this._emit('game_event', msg);
        break;

      case 'error':
        this._emit('error', msg);
        break;
    }
  }
}

export const multiplayer = new MultiplayerManager();
