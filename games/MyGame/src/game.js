/**
 * game.js — Dungeon Crawler, Phase 5: Procedural Dungeons & Progression
 */

import { Player } from './player.js';
import { Chest } from './chest.js';
import { Enemy } from './enemy.js';
import { MapManager, MAP_COLS, MAP_ROWS } from './map-manager.js';
import { AssetManager } from './asset-manager.js';
import { multiplayer } from './multiplayer.js';

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────
const SWING_RANGE      = 95;
const SWING_ARC_DEG    = 68;
const KNOCKBACK_FORCE  = 390;
const ATTACK_COOLDOWN  = 550;
const IFRAMES_DURATION = 850;
const CONTACT_RADIUS   = 28;
const WORLD_PICKUP_R   = 36;
const PORTAL_RADIUS    = 32;

const HOTBAR_SLOTS   = 8;
const SLOT_SIZE      = 54;
const SLOT_GAP       = 6;
const HOTBAR_PAD     = 10;

const PLAYER_SPEED   = 220;
const PLAYER_ACCEL   = 2200;
const PLAYER_DRAG    = 1800;

const TORCH_RADIUS   = 240;
const DARKNESS_ALPHA = 0.76;
const FOG_ALPHA      = 0.92; 
const FOG_START_LEVEL = 4;

const SAVE_KEY       = 'dungeon_crawler_save';
const HIGH_SCORE_KEY = 'dungeon_crawler_high_scores';
const INPUT_BUFFER_MS = 140;
const MOVE_COYOTE_MS = 90;
const FIREBALL_SPEED    = 400;
const FIREBALL_COOLDOWN = 620;
const FIREBALL_DAMAGE   = 8;
const FIREBALL_RANGE    = 230;   // px — bolts die after this distance
const FIREBALL_SPREAD   = 0.22;  // radians — angle between the 3 bolts
const LIGHTNING_RADIUS = 170;
const LIGHTNING_COOLDOWN = 2600;
const VOID_BALL_SPEED = 250;
const VOID_BALL_COOLDOWN = 3400;
const VOID_BALL_PULL_RADIUS = 94;
const VOID_BALL_PULL_FORCE = 255;
const LEVEL_INTRO_MS = 10000;

const ENEMY_ARROW_SPEED  = 280;
const ENEMY_ARROW_DAMAGE = 14;
const DASH_COOLDOWN      = 1400; // ms between dashes
const DASH_SPEED         = 820;  // velocity burst during dash
const DASH_DURATION      = 150;  // ms of iframes while dashing

// ── Game-feel constants ────────────────────────────────────────────────────
const ATTACK_LUNGE_SPEED    = 260;  // px/s burst toward cursor on swing
const ATTACK_LUNGE_DURATION = 80;   // ms the lunge velocity is applied
const HIT_STOP_DURATION     = 45;   // ms of near-freeze on a heavy hit (dmg >= 18)
const HIT_STOP_TIMESCALE    = 0.04; // physics/time scale during hit-stop
const DASH_GHOST_COUNT      = 4;    // number of afterimage ghosts spawned per dash
const DASH_GHOST_INTERVAL   = 28;   // ms between ghost spawns during dash
const STREAK_WINDOW      = 2400; // ms rapid-kill combo window
const STREAK_BONUS       = 3;    // extra gold per streak kill
const TANK_SHOCKWAVE_R   = 90;   // px radius of tank ground-slam AoE
const ENEMY_ARROW_LIFE   = 1300;
const BOMBER_EXPLODE_RADIUS = 72;
const SHOP_ITEM_COUNT    = 3;

const RARITY_COLOR = {
  common:    0x9ca3af,
  uncommon:  0x22c55e,
  rare:      0x3b82f6,
  epic:      0xa855f7,
  legendary: 0xf59e0b,
};

const STAT_LABEL = {
  attack:       'ATK',
  defense:      'DEF',
  max_hp:       'HP+',
  attack_speed: 'SPD',
  mining_power: 'PWR',
  heal:         'HEAL',
  radius:       'RAD',
  power:        'PWR',
  pull:         'PULL',
  duration:     'TIME',
};

// Returns colour palette based on floor depth
function getFloorTheme(level) {
  if (level <= 3) return {          // Stone Crypt — blue-grey stone
    wall1:   0x2a2840, wall2:   0x3a3858, wallLine: 0x5a5888,
    floor1a: 0x1a1830, floor1b: 0x161428, floor2:   0x28263e,
    moss1:   0x1a2830, moss2:   0x204038,
  };
  if (level <= 6) return {          // Overgrown Ruins — mossy green
    wall1:   0x1a3a20, wall2:   0x244e2a, wallLine: 0x3a7a48,
    floor1a: 0x0e2214, floor1b: 0x0a1a0e, floor2:   0x183a20,
    moss1:   0x1a3a1a, moss2:   0x2a6030,
  };
  if (level <= 9) return {          // Lava Depths — dark ember red
    wall1:   0x4a1800, wall2:   0x6a2200, wallLine: 0xb04400,
    floor1a: 0x2e0e00, floor1b: 0x240a00, floor2:   0x501a00,
    moss1:   0x3c1000, moss2:   0x7a2400,
  };
  return {                          // Void Realm — deep cosmic purple
    wall1:   0x1e0040, wall2:   0x2e0060, wallLine: 0x6000c0,
    floor1a: 0x120028, floor1b: 0x0c001e, floor2:   0x20004a,
    moss1:   0x16002e, moss2:   0x320070,
  };
}

function createRng(seed) {
  let s = seed >>> 0;
  return function rand() {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function readSavedGame() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (err) {
    console.warn('Failed to read save data:', err);
    localStorage.removeItem(SAVE_KEY);
    return null;
  }
}

function removeSave() {
  try {
    localStorage.removeItem(SAVE_KEY);
  } catch {}
}

function showStartupError(message) {
  const root = document.getElementById('startup-error') || document.createElement('div');
  root.id = 'startup-error';
  root.style.position = 'fixed';
  root.style.inset = '0';
  root.style.display = 'flex';
  root.style.alignItems = 'center';
  root.style.justifyContent = 'center';
  root.style.background = 'rgba(3,7,18,0.94)';
  root.style.color = '#e5e7eb';
  root.style.fontFamily = 'monospace';
  root.style.fontSize = '14px';
  root.style.textAlign = 'center';
  root.style.padding = '24px';
  root.style.zIndex = '9999';
  root.innerHTML = `<div><div style="font-size:28px;color:#ef4444;margin-bottom:12px;">Load Error</div><div>${message}</div></div>`;
  if (!root.parentNode) document.body.appendChild(root);
}

// ─────────────────────────────────────────────────────────────────────────────
// Audio System (Procedural Web Audio)
// ─────────────────────────────────────────────────────────────────────────────
let _audioCtx   = null;
let _audioReady = false; // stays false until the first user gesture

function _getAC() {
  if (!_audioCtx) _audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  if (_audioCtx.state === 'suspended') _audioCtx.resume();
  return _audioCtx;
}

// Create/resume the AudioContext only on the first user gesture.
// Sets _audioReady so that _tone() stops silently dropping sounds.
function _unlockAC() {
  _audioReady = true;
  if (!_audioCtx) {
    _audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (_audioCtx.state === 'suspended') _audioCtx.resume();
}
document.addEventListener('click',      _unlockAC, { once: true });
document.addEventListener('touchstart', _unlockAC, { once: true, passive: true });
document.addEventListener('keydown',    _unlockAC, { once: true });

function _tone(freq, type, vol, dur, freqEnd = null, delay = 0) {
  if (!_audioReady) return; // no user gesture yet — skip silently, no warning
  const ac = _getAC();
  const osc = ac.createOscillator();
  const gain = ac.createGain();
  osc.connect(gain);
  gain.connect(ac.destination);
  osc.type = type;
  osc.frequency.value = freq;
  if (freqEnd !== null) osc.frequency.linearRampToValueAtTime(freqEnd, ac.currentTime + delay + dur);
  gain.gain.setValueAtTime(vol, ac.currentTime + delay);
  gain.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + delay + dur);
  osc.start(ac.currentTime + delay);
  osc.stop(ac.currentTime + delay + dur);
}

function _soundChestOpen()    { _tone(140, 'sine', 0.25, 0.12, 90); _tone(900, 'sine', 0.12, 0.45, 1400, 0.08); _tone(1200,'sine', 0.07, 0.30, 600, 0.20); }
function _soundItemPickup()   { _tone(660, 'sine', 0.18, 0.12); _tone(880, 'sine', 0.13, 0.12, null, 0.13); _tone(1320, 'sine', 0.09, 0.22, null, 0.24); }
function _soundEquip()        { _tone(200, 'square', 0.07, 0.04); _tone(550, 'sine', 0.14, 0.22, null, 0.05); }
function _soundInventoryFull(){ _tone(220, 'sawtooth', 0.14, 0.09); _tone(190, 'sawtooth', 0.14, 0.09, null, 0.14); }
function _soundAttack()       { _tone(200, 'sawtooth', 0.09, 0.04, 80); _tone(95, 'square', 0.13, 0.07, null, 0.03); }
function _soundEnemyHit()     { _tone(260, 'square', 0.15, 0.04, 110); }
function _soundEnemyDeath()   { _tone(310, 'sawtooth', 0.16, 0.08, 70); _tone(140, 'sine', 0.10, 0.18, 55, 0.08); }
function _soundPlayerHurt()   { _tone(160, 'sawtooth', 0.20, 0.09); _tone(110, 'sawtooth', 0.15, 0.11, null, 0.07); }
function _soundPortal()       { _tone(300, 'sine', 0.2, 0.8, 800); _tone(150, 'square', 0.1, 0.8, 50, 0.1); }
function _soundLevelUp()      { _tone(440, 'square', 0.1, 0.2); _tone(554, 'square', 0.1, 0.2, null, 0.2); _tone(659, 'square', 0.1, 0.4, null, 0.4); }

class AudioManager {
  constructor() {
    this.enabled     = true;
    this.musicEvent  = null;
    this.ambientEvent= null;
    this.chordEvent  = null;
    this.dreadEvent  = null;
    this.scene       = null;
    this._chordStep  = 0;
  }

  attachScene(scene) { this.scene = scene; }

  toggleMuted() {
    this.enabled = !this.enabled;
    return this.enabled;
  }

  playSfx(name) {
    if (!this.enabled) return;
    const map = {
      chest: _soundChestOpen,
      pickup: _soundItemPickup,
      equip: _soundEquip,
      full: _soundInventoryFull,
      attack: _soundAttack,
      hit: _soundEnemyHit,
      death: _soundEnemyDeath,
      hurt: _soundPlayerHurt,
      portal: _soundPortal,
      levelup: _soundLevelUp,
      footstep_stone: () => _tone(120, 'triangle', 0.03, 0.04, 80),
      footstep_moss:  () => _tone(180, 'sine',     0.02, 0.05, 120),
    };
    map[name]?.();
  }

  startMusic(scene) {
    this.stopMusic();
    this.attachScene(scene);

    // ── Heartbeat bass: heavy double-thump every 720ms ───────────────────────
    this.musicEvent = scene.time.addEvent({
      delay: 720, loop: true,
      callback: () => {
        if (!this.enabled) return;
        _tone(58, 'sawtooth', 0.07, 0.18, 42);           // first thump
        _tone(58, 'sawtooth', 0.045, 0.13, 42, 0.22);    // echo thump
      },
    });

    // ── Tense chord cycle: dissonant minor chords every 1440ms ──────────────
    // Notes chosen for maximum unease: minor seconds, tritones, minor thirds
    const _chords = [
      [[146, 'square', 0.030, 1.1], [175, 'square', 0.018, 0.9]],   // Dm
      [[155, 'square', 0.025, 1.0], [185, 'square', 0.016, 0.8]],   // Eb (dissonant)
      [[130, 'square', 0.028, 1.2], [164, 'square', 0.018, 1.0]],   // Cm
      [[138, 'square', 0.020, 0.9], [196, 'square', 0.015, 0.7]],   // C# / tritone area
    ];
    this.chordEvent = scene.time.addEvent({
      delay: 1440, loop: true,
      callback: () => {
        if (!this.enabled) return;
        for (const [freq, type, vol, dur] of _chords[this._chordStep % _chords.length]) {
          _tone(freq, type, vol, dur);
        }
        this._chordStep++;
      },
    });

    // ── Tension sting: descending tritone + deep sustain every 3.2s ─────────
    this.ambientEvent = scene.time.addEvent({
      delay: 3200, loop: true,
      callback: () => {
        if (!this.enabled) return;
        if (Math.random() > 0.38) {
          _tone(494, 'sawtooth', 0.022, 0.22, 330);      // Bb4 → E4 tritone drop
          _tone(220, 'sine',    0.015, 1.8,  180, 0.12); // sustained low note
        } else {
          _tone(82,  'triangle', 0.025, 1.6, 62);        // deep rumble
        }
      },
    });

    // ── Dread accent: occasional high horror stab every ~8s ─────────────────
    this.dreadEvent = scene.time.addEvent({
      delay: 8200, loop: true,
      callback: () => {
        if (!this.enabled || Math.random() > 0.55) return;
        _tone(880, 'sawtooth', 0.018, 0.08, 660);        // sharp high scrape
        _tone(440, 'sine',     0.012, 0.55, 370, 0.10);  // low sustain follow
      },
    });
  }

  stopMusic() {
    this.musicEvent?.remove(false);
    this.ambientEvent?.remove(false);
    this.chordEvent?.remove(false);
    this.dreadEvent?.remove(false);
    this.musicEvent  = null;
    this.ambientEvent= null;
    this.chordEvent  = null;
    this.dreadEvent  = null;
  }
}

const audioManager = new AudioManager();

// ─────────────────────────────────────────────────────────────────────────────
// BootScene
// ─────────────────────────────────────────────────────────────────────────────
class BootScene extends Phaser.Scene {
  constructor() { super({ key: 'BootScene' }); }
  preload() {
    if (window.location.protocol === 'file:') {
      showStartupError('Open the hosted game at https://dungeon-crawler.ganz26.top/ instead of opening the HTML file directly.');
      return;
    }
    const { width, height } = this.scale;
    const cx = width / 2, cy = height / 2;
    const barBg = this.add.graphics().fillStyle(0x1a1a2e, 1).fillRect(cx - 160, cy - 16, 320, 32);
    const bar = this.add.graphics();
    this.add.text(cx, cy - 40, 'Loading...', { fontFamily: 'monospace', fontSize: '14px', color: '#a0a0c0' }).setOrigin(0.5);
    this.load.on('progress', v => { bar.clear().fillStyle(0x7c3aed, 1).fillRect(cx - 158, cy - 14, 316 * v, 28); });
    this.load.on('loaderror', (file) => {
      if (file.key === 'items') {
        showStartupError('Failed to load assets/data/items.json. Open the hosted game from https://dungeon-crawler.ganz26.top/ so the game assets can load correctly.');
      }
    });
    this.load.json('items', 'assets/data/items.json');
  }
  create() {
    if (window.location.protocol === 'file:') return;
    const raw = this.cache.json.get('items');
    if (!raw?.items) {
      showStartupError('items.json did not load correctly. Open the hosted game from https://dungeon-crawler.ganz26.top/.');
      return;
    }
    // Items are drawn procedurally with Graphics — sprite PNGs are not used
    // for rendering and the assets/sprites/ directory doesn't exist on the
    // server. Skip the load entirely to eliminate 404 console noise.
    this.scene.start('MenuScene');
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// MenuScene
// ─────────────────────────────────────────────────────────────────────────────
class MenuScene extends Phaser.Scene {
  constructor() { super({ key: 'MenuScene' }); }
  create() {
    const { width, height } = this.scale;
    const cx = width / 2, cy = height / 2;
    audioManager.startMusic(this);

    this.add.text(cx, cy - 80, 'THE DUNGEON CRAWLER', {
      fontFamily: 'monospace', fontSize: '38px', color: '#a855f7', stroke: '#000000', strokeThickness: 6
    }).setOrigin(0.5);

    const hasSave = !!readSavedGame();
    let best = null;
    try {
      best = JSON.parse(localStorage.getItem(HIGH_SCORE_KEY) || '[]')[0] || null;
    } catch {
      best = null;
    }
    if (best) {
      this.add.text(cx, cy - 24, `Best Run  Floor ${best.floor}  Lv.${best.level}  Gold ${best.gold}`, {
        fontFamily: 'monospace', fontSize: '12px', color: '#fbbf24'
      }).setOrigin(0.5);
    }

    this.add.text(cx, cy + 4, 'Choose Difficulty', {
      fontFamily: 'monospace', fontSize: '12px', color: '#a5b4fc'
    }).setOrigin(0.5);

    this._createBtn(cx - 90, cy + 44, 'Easy', true, () => {
      localStorage.removeItem(SAVE_KEY);
      this.scene.start('ClassSelectScene', { worldState: { difficulty: 'easy', openedChests: [], defeatedEnemies: [], brokenWalls: [], performanceVisible: false, godMode: false } });
    }, 140);

    this._createBtn(cx + 90, cy + 44, 'Hard', true, () => {
      localStorage.removeItem(SAVE_KEY);
      this.scene.start('ClassSelectScene', { worldState: { difficulty: 'hard', openedChests: [], defeatedEnemies: [], brokenWalls: [], performanceVisible: false, godMode: false } });
    }, 140);

    this._createBtn(cx, cy + 102, 'Continue', hasSave, () => {
      if (hasSave) {
        // Read the saved level so MainScene.init() receives it directly —
        // without this, data.level is undefined and dungeonLevel defaults to 1.
        let savedLevel = 1;
        try {
          const save = JSON.parse(localStorage.getItem(SAVE_KEY) || '{}');
          savedLevel = save.level || 1;
        } catch (e) { /* malformed save — fall back to floor 1 */ }
        this.scene.start('MainScene', { isNewGame: false, level: savedLevel });
      }
    });

    this._createBtn(cx, cy + 160, 'Instructions', true, () => {
      this.scene.start('InstructionsScene');
    }, 220);

    this._createBtn(cx, cy + 218, 'Party', true, () => {
      this.scene.start('PartyScene');
    }, 220);
  }

  _createBtn(x, y, text, active, onClick, btnW = 200) {
    const btnH = 44;
    const btnBg = this.add.graphics();
    const color = active ? 0x7c3aed : 0x333333;
    const hoverColor = active ? 0x6d28d9 : 0x333333;

    const draw = (c) => {
      btnBg.clear().fillStyle(c, 1).fillRoundedRect(x - btnW/2, y - btnH/2, btnW, btnH, 9);
    };
    draw(color);

    const txt = this.add.text(x, y, text, {
      fontFamily: 'monospace', fontSize: '18px', color: active ? '#ffffff' : '#888888'
    }).setOrigin(0.5);

    if (active) {
      txt.setInteractive({ useHandCursor: true })
         .on('pointerover', () => draw(hoverColor))
         .on('pointerout', () => draw(color))
         .on('pointerdown', () => {
           this.cameras.main.fadeOut(260, 0, 0, 0);
           this.cameras.main.once('camerafadeoutcomplete', onClick);
         });
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PartyScene
// ─────────────────────────────────────────────────────────────────────────────
class PartyScene extends Phaser.Scene {
  constructor() { super({ key: 'PartyScene' }); }

  // ─────────────────────────────────────────────────────────────
  // Bootstrap
  // ─────────────────────────────────────────────────────────────
  create() {
    const { width, height } = this.scale;
    this._cx = width / 2;
    this._W  = width;
    this._H  = height;

    this._view           = [];   // current view objects (destroyed on switch)
    this._kbListener     = null;
    this._joinInputActive = false;
    this._joinCode       = '';
    this._boxData        = [];   // { bg, x, y, w, h, txt } per letter box

    this.add.rectangle(0, 0, width, height, 0x0d0d1a).setOrigin(0);

    this._showMain();
  }

  // ─────────────────────────────────────────────────────────────
  // VIEW: Main (Choose Create / Join)
  // ─────────────────────────────────────────────────────────────
  _showMain() {
    this._clear();
    const cx = this._cx;

    this._push(this.add.text(cx, 200, 'PARTY', {
      fontFamily: 'monospace', fontSize: '42px', color: '#a855f7',
      stroke: '#000', strokeThickness: 6,
    }).setOrigin(0.5));

    this._push(this.add.text(cx, 258, 'Play online with friends on the same Wi-Fi', {
      fontFamily: 'monospace', fontSize: '12px', color: '#4c1d95',
    }).setOrigin(0.5));

    this._btn(cx - 140, 360, 'Create Party', 240, () => this._goCreate());
    this._btn(cx + 140, 360, 'Join Party',   240, () => this._goJoin());

    this._btn(cx, 460, 'Back', 140, () => {
      this.cameras.main.fadeOut(200, 0, 0, 0);
      this.cameras.main.once('camerafadeoutcomplete', () => this.scene.start('MenuScene'));
    }, 0x1a1a2e);
  }

  // ─────────────────────────────────────────────────────────────
  // VIEW: Create Party
  // ─────────────────────────────────────────────────────────────
  async _goCreate() {
    this._clear();
    const cx = this._cx;

    this._push(this.add.text(cx, 52, 'CREATE PARTY', {
      fontFamily: 'monospace', fontSize: '28px', color: '#a855f7',
      stroke: '#000', strokeThickness: 5,
    }).setOrigin(0.5));

    // live status line
    this._statusTxt = this._push(this.add.text(cx, 95, 'Connecting to server...', {
      fontFamily: 'monospace', fontSize: '11px', color: '#fbbf24',
    }).setOrigin(0.5));

    // party code
    this._push(this.add.text(cx, 135, 'Code:', {
      fontFamily: 'monospace', fontSize: '11px', color: '#4c1d95',
    }).setOrigin(0.5));
    this._codeTxt = this._push(this.add.text(cx, 182, '- - - -', {
      fontFamily: 'monospace', fontSize: '44px', color: '#fbbf24',
      stroke: '#000', strokeThickness: 4,
    }).setOrigin(0.5));

    // 4 player slots
    this._buildSlots(230);

    // player count
    this._countTxt = this._push(this.add.text(cx, 500, 'Players: 1 / 4', {
      fontFamily: 'monospace', fontSize: '12px', color: '#4c1d95',
    }).setOrigin(0.5));

    // Start Game button (inactive until someone joins)
    this._buildStartBtn(556);

    // Back
    this._btn(cx, 636, '< Back', 140, () => {
      multiplayer.disconnect();
      this._showMain();
    }, 0x1a1a2e);

    // ── Connect & request party ──
    try {
      await multiplayer.connect();
    } catch {
      this._statusTxt.setText('X Cannot connect - make sure npm run dev is running').setStyle({ color: '#ef4444' });
      return;
    }

    multiplayer.on('party_created', ({ code }) => {
      this._statusTxt.setText('Share this code with your friends ->').setStyle({ color: '#94a3b8' });
      this._codeTxt.setText(code);
      this._fillSlot(0, 'You  (Host)', '#7c3aed');
    });

    multiplayer.on('player_joined', ({ playerCount, playerIndex }) => {
      const COLORS = ['#7c3aed', '#e67e22', '#2ecc71', '#e74c3c'];
      this._fillSlot(playerIndex, `Player ${playerIndex + 1}`, COLORS[playerIndex]);
      this._countTxt.setText(`Players: ${playerCount} / 4`);
      this._setStartActive(true);
    });

    multiplayer.on('game_started', ({ seed, difficulty }) => this._launch(seed, difficulty));

    multiplayer.createParty();
  }

  // ─────────────────────────────────────────────────────────────
  // VIEW: Join Party
  // ─────────────────────────────────────────────────────────────
  _goJoin() {
    this._clear();
    const cx = this._cx;
    this._joinCode = '';
    this._joinInputActive = true;

    this._push(this.add.text(cx, 130, 'JOIN PARTY', {
      fontFamily: 'monospace', fontSize: '28px', color: '#a855f7',
      stroke: '#000', strokeThickness: 5,
    }).setOrigin(0.5));

    this._push(this.add.text(cx, 180, 'Enter the party code:', {
      fontFamily: 'monospace', fontSize: '12px', color: '#94a3b8',
    }).setOrigin(0.5));

    // ── 4 letter boxes ──────────────────────────────────────────
    const BOX_W = 78, BOX_H = 90, BOX_GAP = 18;
    const totalW = 4 * BOX_W + 3 * BOX_GAP;
    const bx0 = cx - totalW / 2;
    const bY  = 220;

    this._boxData = [];
    for (let i = 0; i < 4; i++) {
      const bx = bx0 + i * (BOX_W + BOX_GAP);
      const bg = this._push(this.add.graphics());
      const txt = this._push(this.add.text(bx + BOX_W / 2, bY + BOX_H / 2, '_', {
        fontFamily: 'monospace', fontSize: '36px', color: '#2d1b69',
      }).setOrigin(0.5));
      this._boxData.push({ bg, txt, bx, bY, BOX_W, BOX_H });
    }
    this._drawBoxes(); // initial render (first box highlighted)

    // status / error line
    this._joinStatusTxt = this._push(this.add.text(cx, 340, 'Type A-Z letters, Backspace to erase', {
      fontFamily: 'monospace', fontSize: '11px', color: '#6d28d9',
    }).setOrigin(0.5));

    // Back
    this._btn(cx, 430, '< Back', 140, () => {
      this._stopKb();
      this._showMain();
    }, 0x1a1a2e);

    this._startKb();
  }

  // ─────────────────────────────────────────────────────────────
  // VIEW: Waiting (joined successfully)
  // ─────────────────────────────────────────────────────────────
  _showWaiting(code, myIndex, playerCount) {
    this._clear();
    const cx = this._cx;
    const COLORS = ['#7c3aed', '#e67e22', '#2ecc71', '#e74c3c'];

    this._push(this.add.text(cx, 52, 'PARTY JOINED', {
      fontFamily: 'monospace', fontSize: '26px', color: '#2ecc71',
      stroke: '#000', strokeThickness: 5,
    }).setOrigin(0.5));

    this._push(this.add.text(cx, 96, `Code: ${code}`, {
      fontFamily: 'monospace', fontSize: '20px', color: '#fbbf24',
    }).setOrigin(0.5));

    // slots
    this._buildSlots(140);

    // fill slots we know about so far
    for (let i = 0; i < playerCount; i++) {
      const lbl = i === 0 ? 'Host' : i === myIndex ? 'You' : `Player ${i + 1}`;
      this._fillSlot(i, lbl, COLORS[i]);
    }

    this._countTxt = this._push(this.add.text(cx, 410, `Players: ${playerCount} / 4`, {
      fontFamily: 'monospace', fontSize: '12px', color: '#4c1d95',
    }).setOrigin(0.5));

    this._push(this.add.text(cx, 450, 'Waiting for the host to start the game...', {
      fontFamily: 'monospace', fontSize: '12px', color: '#fbbf24',
    }).setOrigin(0.5));

    // keep updating as more players join
    multiplayer.on('player_joined', ({ playerCount: cnt, playerIndex: pi }) => {
      const lbl = pi === myIndex ? 'You' : `Player ${pi + 1}`;
      this._fillSlot(pi, lbl, COLORS[pi]);
      this._countTxt?.setText(`Players: ${cnt} / 4`);
    });

    multiplayer.on('game_started', ({ seed, difficulty }) => this._launch(seed, difficulty));

    this._btn(cx, 530, '< Back', 140, () => {
      multiplayer.disconnect();
      this._showMain();
    }, 0x1a1a2e);
  }

  // ─────────────────────────────────────────────────────────────
  // Shared slot helpers
  // ─────────────────────────────────────────────────────────────
  _buildSlots(startY) {
    const cx = this._cx;
    const SW = 270, SH = 120, GAP = 14;
    const totalW = 4 * SW + 3 * GAP;
    const sx = cx - totalW / 2;

    this._slotGfxArr = [];
    this._slotNameTxts = [];

    for (let i = 0; i < 4; i++) {
      const x = sx + i * (SW + GAP);

      const bg = this._push(this.add.graphics());
      bg.fillStyle(0x0d0d1e, 1).fillRoundedRect(x, startY, SW, SH, 10);
      bg.lineStyle(2, 0x2d1b69, 1).strokeRoundedRect(x, startY, SW, SH, 10);

      this._push(this.add.text(x + SW / 2, startY + 18, `SLOT  ${i + 1}`, {
        fontFamily: 'monospace', fontSize: '9px', color: '#2d1b69',
      }).setOrigin(0.5));

      const nameTxt = this._push(this.add.text(x + SW / 2, startY + 64, '- waiting -', {
        fontFamily: 'monospace', fontSize: '13px', color: '#2d1b69',
      }).setOrigin(0.5));

      this._slotGfxArr.push({ bg, x, y: startY, w: SW, h: SH });
      this._slotNameTxts.push(nameTxt);
    }
  }

  _fillSlot(index, label, colorHex) {
    const s = this._slotGfxArr?.[index];
    if (!s) return;
    const col = parseInt(colorHex.replace('#', ''), 16);
    s.bg.clear()
      .fillStyle(0x120820, 1).fillRoundedRect(s.x, s.y, s.w, s.h, 10)
      .lineStyle(2, col, 1).strokeRoundedRect(s.x, s.y, s.w, s.h, 10);
    this._slotNameTxts[index]?.setText(label).setStyle({ color: colorHex });
  }

  // ─────────────────────────────────────────────────────────────
  // Start Game button (host)
  // ─────────────────────────────────────────────────────────────
  _buildStartBtn(y) {
    const cx = this._cx, w = 260, h = 44;
    this._startBtnBg = this._push(this.add.graphics());
    this._startBtnTxt = this._push(this.add.text(cx, y, 'Start Game  >', {
      fontFamily: 'monospace', fontSize: '19px', color: '#555566',
    }).setOrigin(0.5));
    this._setStartActive(false);
    this._startBtnY = y; this._startBtnW = w; this._startBtnH = h;
  }

  _setStartActive(active) {
    const cx = this._cx;
    const w = this._startBtnW || 260, h = this._startBtnH || 44, y = this._startBtnY || 556;
    this._startBtnBg?.clear()
      .fillStyle(active ? 0x7c3aed : 0x222233, 1)
      .fillRoundedRect(cx - w / 2, y - h / 2, w, h, 9);
    this._startBtnTxt?.setStyle({ color: active ? '#ffffff' : '#555566' });
    if (active) {
      this._startBtnTxt
        ?.setInteractive({ useHandCursor: true })
        .removeListener('pointerdown')
        .on('pointerdown', () => multiplayer.startGame(Math.floor(Math.random() * 9999999), 'easy'));
    } else {
      this._startBtnTxt?.removeInteractive();
    }
  }

  // ─────────────────────────────────────────────────────────────
  // Keyboard input for join code
  // ─────────────────────────────────────────────────────────────
  _startKb() {
    this._kbListener = (e) => {
      if (!this._joinInputActive) return;
      const k = e.key.toUpperCase();
      if (/^[A-Z]$/.test(k) && this._joinCode.length < 4) {
        this._joinCode += k;
        this._drawBoxes();
        if (this._joinCode.length === 4) this._submitJoin();
      } else if (e.key === 'Backspace' && this._joinCode.length > 0) {
        this._joinCode = this._joinCode.slice(0, -1);
        this._drawBoxes();
      }
    };
    window.addEventListener('keydown', this._kbListener);
  }

  _stopKb() {
    if (this._kbListener) { window.removeEventListener('keydown', this._kbListener); this._kbListener = null; }
    this._joinInputActive = false;
  }

  _drawBoxes() {
    for (let i = 0; i < 4; i++) {
      const d = this._boxData[i];
      if (!d) continue;
      const ch      = this._joinCode[i] || '';
      const active  = i === this._joinCode.length && this._joinInputActive;
      const filled  = !!ch;

      d.bg.clear()
        .fillStyle(active ? 0x1e1040 : 0x11112a, 1)
        .fillRoundedRect(d.bx, d.bY, d.BOX_W, d.BOX_H, 8)
        .lineStyle(2, active ? 0xa855f7 : filled ? 0x7c3aed : 0x2d1b69, 1)
        .strokeRoundedRect(d.bx, d.bY, d.BOX_W, d.BOX_H, 8);

      d.txt.setText(ch || (active ? '|' : '_'))
           .setStyle({ color: filled ? '#fbbf24' : active ? '#a855f7' : '#2d1b69' });
    }
  }

  async _submitJoin() {
    this._joinInputActive = false;
    this._joinStatusTxt?.setText('Connecting...').setStyle({ color: '#fbbf24' });

    try {
      if (!multiplayer.ws || multiplayer.ws.readyState !== WebSocket.OPEN)
        await multiplayer.connect();
    } catch {
      this._joinStatusTxt?.setText('X Cannot connect - make sure npm run dev is running').setStyle({ color: '#ef4444' });
      this._resetJoin();
      return;
    }

    multiplayer.on('party_joined', ({ code, playerCount, playerIndex }) => {
      this._stopKb();
      this._showWaiting(code, playerIndex, playerCount);
    });

    multiplayer.on('error', ({ msg }) => {
      this._joinStatusTxt?.setText(`X  ${msg}`).setStyle({ color: '#ef4444' });
      this._resetJoin();
    });

    multiplayer.joinParty(this._joinCode);
  }

  _resetJoin() {
    this._joinCode = '';
    this._joinInputActive = true;
    this._drawBoxes();
  }

  // ─────────────────────────────────────────────────────────────
  // Launch MainScene (host + all clients)
  // ─────────────────────────────────────────────────────────────
  _launch(seed, difficulty) {
    if (this._launching) return; // guard against double game_started
    this._launching = true;
    this._stopKb();
    this.cameras.main.fadeOut(300, 0, 0, 0);
    this.cameras.main.once('camerafadeoutcomplete', () => {
      this.scene.start('MainScene', {
        isNewGame: true,
        seed,
        worldState: { difficulty, openedChests: [], defeatedEnemies: [], brokenWalls: [], performanceVisible: false, godMode: false },
        mp: { code: multiplayer.partyCode, playerId: multiplayer.playerId, isHost: multiplayer.isHost, playerIndex: multiplayer.playerIndex },
      });
    });
  }

  // ─────────────────────────────────────────────────────────────
  // Generic helpers
  // ─────────────────────────────────────────────────────────────
  _push(obj) { this._view.push(obj); return obj; }

  _clear() {
    this._stopKb();
    this._view.forEach(o => { try { o.destroy(); } catch {} });
    this._view = [];
    this._slotGfxArr   = null;
    this._slotNameTxts = null;
    this._boxData      = [];
  }

  _btn(x, y, label, w, onClick, bgCol = 0x7c3aed) {
    const h = 44;
    const bg  = this._push(this.add.graphics());
    const hov = Math.max(0, bgCol - 0x111111);
    const draw = (c) => bg.clear().fillStyle(c, 1).fillRoundedRect(x - w / 2, y - h / 2, w, h, 9);
    draw(bgCol);
    this._push(
      this.add.text(x, y, label, { fontFamily: 'monospace', fontSize: '17px', color: '#ffffff' })
        .setOrigin(0.5)
        .setInteractive({ useHandCursor: true })
        .on('pointerover',  () => draw(hov))
        .on('pointerout',   () => draw(bgCol))
        .on('pointerdown',  onClick)
    );
  }

  shutdown() { this._stopKb(); }
}

class InstructionsScene extends Phaser.Scene {
  constructor() { super({ key: 'InstructionsScene' }); }

  create() {
    const { width, height } = this.scale;
    const cx = width / 2;
    this.add.rectangle(cx, height / 2, width, height, 0x070b16, 1);
    this.add.text(cx, 74, 'HOW TO PLAY', {
      fontFamily: 'monospace',
      fontSize: '30px',
      color: '#f8fafc',
      stroke: '#000000',
      strokeThickness: 4,
    }).setOrigin(0.5);

    const body = [
      'Move: WASD or Arrow Keys',
      'Mouse Click: melee attack / use hotbar slot',
      '1-8: select hotbar slots',
      'F: cast a fireball',
      'Q: clear selected hotbar slot',
      'R: lightning strike',
      'E: void ball',
      'F near a chest or shop: interact',
      'Rooms: shop (buy with Gold), trap (spikes!), treasure (better loot)',
      'Every 5 floors: boss room',
      'Esc: pause menu',
      '` : debug console',
      'Easy: fully visible map',
      'Hard: darkness + more monsters',
      'Kill every monster to unlock the next floor',
      'Multiplayer: Enter = chat bubble',
      'Classes: Warrior / Mage / Rogue (choose at new game)',
    ].join('\n');

    this.add.text(cx, height / 2 - 40, body, {
      fontFamily: 'monospace',
      fontSize: '16px',
      color: '#cbd5e1',
      align: 'center',
      lineSpacing: 8,
    }).setOrigin(0.5);

    this._createBtn(cx, height - 90, 'Back', () => this.scene.start('MenuScene'));
  }

  _createBtn(x, y, text, onClick) {
    const bg = this.add.graphics();
    const draw = (hover) => bg.clear().fillStyle(hover ? 0x6d28d9 : 0x312e81, 1).fillRoundedRect(x - 90, y - 22, 180, 44, 9);
    draw(false);
    const label = this.add.text(x, y, text, { fontFamily: 'monospace', fontSize: '18px', color: '#ffffff' }).setOrigin(0.5);
    label.setInteractive({ useHandCursor: true })
      .on('pointerover', () => draw(true))
      .on('pointerout', () => draw(false))
      .on('pointerdown', onClick);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// ClassSelectScene
// ─────────────────────────────────────────────────────────────────────────────
const CLASS_DEFS = [
  {
    id: 'warrior',
    name: 'Warrior',
    flavor: 'Born to take hits so others don\'t have to.',
    statLine: '+50 HP  |  +2 DEF',
    color: '#f59e0b',
    border: 0xf59e0b,
    startItems: ['sword_iron', 'chestplate_leather', 'potion_health'],
    equip:      ['sword_iron', 'chestplate_leather'],
    hotbar:     ['potion_health', null, null, null, null, null, null, null],
    statBonus:  { maxHp: +50, baseDefense: +2 },
    canUseSpells: false,
    perks:  ['All weapon types', 'Heavy armor proficiency', '+50 max HP and +2 DEF'],
    limits: ['Cannot pick up spells from the ground', 'Slower than the Rogue'],
  },
  {
    id: 'mage',
    name: 'Mage',
    flavor: 'Glass cannon. Every spell rewrites the battle.',
    statLine: '-25 HP  |  +50% all damage',
    color: '#a855f7',
    border: 0xa855f7,
    spellPool:  ['spell_lightning_strike', 'spell_void_ball'],
    startItems: ['potion_health', 'potion_health'],
    equip:      [],
    hotbar:     ['potion_health', null, null, null, null, null, null, null],
    statBonus:  { maxHp: -25 },
    damageMultiplier: 1.5,
    canUseSpells: true,
    perks:  ['Starts with a random spell', '+50% damage on every hit', 'Can pick up and use spells'],
    limits: ['Starts weaponless (melee is weak)', 'Only 1 random spell at start', '-25 max HP - dies easiest'],
  },
  {
    id: 'rogue',
    name: 'Rogue',
    flavor: 'Strike first, strike clean, be gone before they fall.',
    statLine: '+3 ATK  |  +60 speed',
    color: '#22c55e',
    border: 0x22c55e,
    startItems: ['sword_moonsteel', 'potion_health', 'potion_health', 'potion_health'],
    equip:      ['sword_moonsteel'],
    hotbar:     ['potion_health', 'potion_health', 'potion_health', null, null, null, null, null],
    statBonus:  { maxHp: -10, baseAttack: +3, speed: +60 },
    canUseSpells: false,
    perks:  ['Starts with Moonsteel Sword', '+3 ATK and +60 movement speed', '3 starting health potions'],
    limits: ['Cannot pick up spells from the ground', 'Less HP than Warrior'],
  },
];

class ClassSelectScene extends Phaser.Scene {
  constructor() { super({ key: 'ClassSelectScene' }); }

  init(data) { this._worldState = data.worldState || {}; }

  create() {
    const { width, height } = this.scale;
    const cx = width / 2;

    // Dark background
    this.add.rectangle(cx, height / 2, width, height, 0x060b18).setOrigin(0.5);

    // Subtle grid overlay
    const grid = this.add.graphics();
    grid.lineStyle(1, 0x1e293b, 0.35);
    for (let x = 0; x <= width; x += 48) grid.lineBetween(x, 0, x, height);
    for (let y = 0; y <= height; y += 48) grid.lineBetween(0, y, width, y);

    // Vignette
    const vig = this.add.graphics();
    vig.fillGradientStyle(0x000000, 0x000000, 0x000000, 0x000000, 0.55, 0.55, 0, 0);
    vig.fillRect(0, 0, width, height / 3);
    const vig2 = this.add.graphics();
    vig2.fillGradientStyle(0x000000, 0x000000, 0x000000, 0x000000, 0, 0, 0.55, 0.55);
    vig2.fillRect(0, height * 2 / 3, width, height / 3);

    // Title
    this.add.text(cx, 48, 'CHOOSE YOUR CLASS', {
      fontFamily: 'monospace', fontSize: '32px', color: '#f1f5f9',
      stroke: '#000000', strokeThickness: 5, letterSpacing: 8,
    }).setOrigin(0.5);

    this.add.text(cx, 90, 'Each class plays differently - choose wisely', {
      fontFamily: 'monospace', fontSize: '12px', color: '#334155', letterSpacing: 2,
    }).setOrigin(0.5);

    // Decorative line under title
    const titleLine = this.add.graphics();
    titleLine.lineStyle(1, 0x1e3a5f, 1).lineBetween(cx - 200, 106, cx + 200, 106);

    const cardW = 280, cardH = 430, gap = 38;
    const totalW = CLASS_DEFS.length * cardW + (CLASS_DEFS.length - 1) * gap;
    const startX = cx - totalW / 2;
    const cardTopY = 128;

    CLASS_DEFS.forEach((cls, i) => {
      this._buildCard(startX + i * (cardW + gap), cardTopY, cardW, cardH, cls);
    });

    this.add.text(cx, height - 22, 'Click a class to begin your descent', {
      fontFamily: 'monospace', fontSize: '11px', color: '#1e3a5f', letterSpacing: 2,
    }).setOrigin(0.5);
  }

  _buildCard(x, y, w, h, cls) {
    const cx = x + w / 2;
    const pad = 20;

    // Drop shadow
    this.add.graphics()
      .fillStyle(0x000000, 0.45)
      .fillRoundedRect(x + 5, y + 5, w, h, 14);

    const bg = this.add.graphics();
    const drawCard = (hover) => {
      bg.clear();
      // Card body
      bg.fillStyle(hover ? 0x131f36 : 0x0a1422, 1).fillRoundedRect(x, y, w, h, 14);
      // Top color strip
      bg.fillStyle(cls.border, hover ? 0.9 : 0.55).fillRoundedRect(x + pad, y + 7, w - pad * 2, 3, 2);
      // Outer glow layers when hovered
      if (hover) {
        bg.lineStyle(14, cls.border, 0.05).strokeRoundedRect(x - 5, y - 5, w + 10, h + 10, 18);
        bg.lineStyle(6,  cls.border, 0.14).strokeRoundedRect(x - 1, y - 1, w + 2,  h + 2,  15);
      }
      // Border
      bg.lineStyle(hover ? 2 : 1, cls.border, hover ? 1 : 0.35).strokeRoundedRect(x, y, w, h, 14);
    };
    drawCard(false);

    let oy = y + 26;

    // Class name
    this.add.text(cx, oy, cls.name.toUpperCase(), {
      fontFamily: 'monospace', fontSize: '22px', color: cls.color,
      stroke: '#000000', strokeThickness: 3, letterSpacing: 5,
    }).setOrigin(0.5);
    oy += 30;

    // Flavor text
    this.add.text(cx, oy, cls.flavor, {
      fontFamily: 'monospace', fontSize: '10px', color: '#475569',
      align: 'center', wordWrap: { width: w - pad * 2 },
    }).setOrigin(0.5, 0);
    oy += 28;

    // Stat line (colored)
    this.add.text(cx, oy, cls.statLine, {
      fontFamily: 'monospace', fontSize: '12px', color: cls.color, letterSpacing: 1,
    }).setOrigin(0.5);
    oy += 22;

    // Divider
    this.add.graphics().lineStyle(1, 0x1e293b, 0.9).lineBetween(x + pad, oy, x + w - pad, oy);
    oy += 14;

    // CAN section
    this.add.text(x + pad, oy, 'CAN', {
      fontFamily: 'monospace', fontSize: '10px', color: '#22c55e', letterSpacing: 3,
    });
    oy += 18;
    for (const perk of cls.perks || []) {
      this.add.text(x + pad, oy, '[+] ' + perk, {
        fontFamily: 'monospace', fontSize: '10px', color: '#86efac',
        wordWrap: { width: w - pad * 2 },
      });
      oy += 18;
    }
    oy += 6;

    // Divider
    this.add.graphics().lineStyle(1, 0x1e293b, 0.9).lineBetween(x + pad, oy, x + w - pad, oy);
    oy += 14;

    // CANNOT section
    this.add.text(x + pad, oy, 'CANNOT', {
      fontFamily: 'monospace', fontSize: '10px', color: '#ef4444', letterSpacing: 3,
    });
    oy += 18;
    for (const limit of cls.limits || []) {
      this.add.text(x + pad, oy, '[-] ' + limit, {
        fontFamily: 'monospace', fontSize: '10px', color: '#fca5a5',
        wordWrap: { width: w - pad * 2 },
      });
      oy += 18;
    }

    // SELECT button at card bottom
    const btnY = y + h - 38;
    const btnX = x + pad;
    const btnW = w - pad * 2;
    const btnH = 30;

    const btnBg = this.add.graphics();
    const btnTxt = this.add.text(cx, btnY + btnH / 2, 'SELECT', {
      fontFamily: 'monospace', fontSize: '13px', color: '#94a3b8',
      stroke: '#000000', strokeThickness: 2, letterSpacing: 4,
    }).setOrigin(0.5);

    const drawBtn = (hover) => {
      btnBg.clear();
      if (hover) {
        btnBg.fillStyle(cls.border, 1).fillRoundedRect(btnX, btnY, btnW, btnH, 6);
        btnBg.lineStyle(1, cls.border, 1).strokeRoundedRect(btnX, btnY, btnW, btnH, 6);
        btnTxt.setColor('#ffffff');
      } else {
        btnBg.fillStyle(0x0d1829, 1).fillRoundedRect(btnX, btnY, btnW, btnH, 6);
        btnBg.lineStyle(1, cls.border, 0.4).strokeRoundedRect(btnX, btnY, btnW, btnH, 6);
        btnTxt.setColor('#94a3b8');
      }
    };
    drawBtn(false);

    // Hit zone
    const zone = this.add.zone(cx, y + h / 2, w, h).setInteractive({ useHandCursor: true });
    zone.on('pointerover', () => { drawCard(true); drawBtn(true); });
    zone.on('pointerout',  () => { drawCard(false); drawBtn(false); });
    zone.on('pointerdown', () => {
      this.cameras.main.fadeOut(220, 0, 0, 0);
      this.cameras.main.once('camerafadeoutcomplete', () => {
        this.scene.start('MainScene', { isNewGame: true, worldState: this._worldState, classData: cls });
      });
    });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// MainScene
// ─────────────────────────────────────────────────────────────────────────────
class MainScene extends Phaser.Scene {
  constructor() { super({ key: 'MainScene' }); }

  init(data) {
    this.isNewGame = data.isNewGame !== false;
    this.dungeonLevel = data.level || 1;
    const urlSeed = Number(new URLSearchParams(window.location.search).get('seed'));
    this.seed = data.seed || (Number.isFinite(urlSeed) && urlSeed > 0 ? urlSeed : Math.floor(Math.random() * 9999999));
    this._incomingPlayerState = data.playerState || null;
    this._incomingWorldState = data.worldState || null;
    this._mpData = data.mp || null; // { code, playerId, isHost, playerIndex }
    this._classData = data.classData || null;
  }

  create() {
    const { width, height } = this.scale;
    audioManager.attachScene(this);

    // Item Registry
    const raw = this.cache.json.get('items');
    if (!raw?.items || !Array.isArray(raw.items)) {
      this._showFatalError('items.json failed to load or is invalid.');
      return;
    }
    this.itemRegistry = new Map(raw.items.map(item => [item.id, item]));
    this.assetManager = new AssetManager(this);
    this._worldState = {
      openedChests: [],
      defeatedEnemies: [],
      brokenWalls: [],
      difficulty: 'hard',
      performanceVisible: false,
      godMode: false,
      // Run stats (persist across floors)
      kills: 0,
      bossesKilled: 0,
      damageDealt: 0,
      damageTaken: 0,
      itemsFound: 0,
      classId: null,
      canUseSpells: false,
      runStartTime: Date.now(),
      unlockedAchievements: [],
      ...(this._incomingWorldState || {}),
    };
    // Per-floor stat (resets each floor for "no-damage" achievement check)
    this._damageTakenThisFloor = 0;
    // Reset death ward so it's usable once per floor
    if (this._worldState.relics?.deathWard) this._worldState.deathWardUsed = false;

    // Initialize Player
    this.player = new Player({ name: 'Hero', speed: PLAYER_SPEED });
    
    // Load Save or Setup New Game
    if (this._incomingPlayerState) {
      this._restorePlayerState(this._incomingPlayerState);
    } else if (this.isNewGame) {
      const cls = this._classData;
      if (cls) { this._worldState.classId = cls.id;
        // Apply class stat bonuses
        if (cls.statBonus.maxHp)       { this.player.maxHp += cls.statBonus.maxHp; this.player.hp = this.player.maxHp; }
        if (cls.statBonus.baseAttack)  this.player.baseAttack  += cls.statBonus.baseAttack;
        if (cls.statBonus.baseDefense) this.player.baseDefense += cls.statBonus.baseDefense;
        if (cls.statBonus.speed)       this.player.speed       += cls.statBonus.speed;
        // Store class flags that persist across floors
        this._worldState.damageMultiplier = cls.damageMultiplier || 1;
        this._worldState.canUseSpells = cls.canUseSpells || false;
        // Add starting items
        for (const id of cls.startItems) {
          const def = this.itemRegistry.get(id); if (def) this.player.addItem(def, 1);
        }
        // Add one random spell from pool (Mage) and auto-place on hotbar
        if (cls.spellPool && cls.spellPool.length) {
          const spellId = cls.spellPool[Math.floor(Math.random() * cls.spellPool.length)];
          const def = this.itemRegistry.get(spellId);
          if (def) {
            this.player.addItem(def, 1);
            // Reserve slot 1 for the spell so it's immediately usable
            this.player.setHotbar(1, spellId);
          }
        }
        // Equip starting gear
        for (const id of cls.equip) this.player.equip(id);
        // Set hotbar
        cls.hotbar.forEach((id, i) => { if (id) this.player.setHotbar(i, id); });
      } else {
        // Default loadout (no class selected — multiplayer / continue paths)
        this.player.addItem(this.itemRegistry.get('sword_iron'));
        this.player.addItem(this.itemRegistry.get('potion_health'), 2);
        this.player.equip('sword_iron');
        this.player.setHotbar(0, 'potion_health');
      }
    } else {
      const saved = readSavedGame();
      if (saved?.player) {
        this.dungeonLevel = saved.level || this.dungeonLevel;
        this.seed = saved.seed || this.seed;
        this._worldState = { ...this._worldState, ...(saved.world || {}) };
        this._restorePlayerState(saved.player);
      }
    }

    // Procedural Generation
    this.floorSeed = (this.seed + this.dungeonLevel * 1337) >>> 0;
    this._rng = createRng(this.floorSeed);
    this.mapManager = new MapManager(this.floorSeed, this.dungeonLevel);
    this.rooms = this.mapManager.rooms;
    this._buildTilemap(width, height, this.mapManager.map);

    // Run physics at 120 steps/sec — halves the maximum per-step displacement,
    // preventing tunneling through 32px corridors at DASH_SPEED (820px/s).
    this.physics.world.setFPS(120);

    // Player Physics & Sprite
    this._playerContainer = this._buildPlayerSprite();
    this._attachPhysics();
    // Camera follows player through the map; use dynamic size from the generator.
    const { cols: _dynCols, rows: _dynRows } = this.mapManager.getMapSize();
    const _camMapW = _dynCols * 32, _camMapH = _dynRows * 32;
    // Center small maps on screen: expand camera bounds into the black border area
    // so the map appears centred rather than anchored to the top-left corner.
    const { width: _vw, height: _vh } = this.scale;
    const _offX = Math.max(0, Math.floor((_vw - _camMapW) / 2));
    const _offY = Math.max(0, Math.floor((_vh - _camMapH) / 2));
    this._mapOffX = _offX;
    this._mapOffY = _offY;
    this.cameras.main.setBounds(-_offX, -_offY, _camMapW + _offX * 2, _camMapH + _offY * 2);
    // No zoom — camera shows the full map at 1:1. Small maps will have a border.
    this.cameras.main.startFollow(this._playerContainer, true, 0.1, 0.1);
    this._prevMainHand = this.player.equipment.main_hand?.id ?? null;
    
    // Damage multiplier (persists via _worldState across floor transitions)
    this._damageMultiplier = this._worldState.damageMultiplier || 1;

    // State Variables
    this._walkCycle = 0;
    this._flickerTime = 0;
    this._attackCooldown = 0;
    this._fireballCooldown = 0;
    this._lightningCooldown = 0;
    this._voidBallCooldown = 0;
    this._iframes = 0;
    this._lastMmPos = { x: 0, y: 0 };
    this._lastMmTime = 0;
    this._attackBuffer = null;
    this._worldItems = [];
    this._fireballs = [];
    this._voidBalls = [];
    this._enemyArrows = [];
    this._shopNpcs = [];
    this._shopUiOpen = false;
    this._optionalBosses = [];
    this._hasBossKey = false;
    this._lockedChests = [];
    this._gameOver = false;
    this._levelingUp = false;
    this._levelIntroActive = false;
    this._chatInputActive = false;
    this._visitedRooms = new Set();
    this._epicTrailTimer = 0;
    this._lastInputTimes = { left: 0, right: 0, up: 0, down: 0 };
    this._facing = 1;
    this._dashCooldown  = 0;
    this._dashActive    = false;
    this._hitStopActive = false; // game-feel: true while hit-stop freeze is in progress
    this._killStreak    = 0;
    this._lastKillTime  = 0;
    this._mmVisited     = null; // reset each floor in _buildMinimap

    // Lighting & Fog of War
    this._torchGlow = this.add.graphics().setDepth(15);
    this._torchTexKey = this._buildTorchTexture(TORCH_RADIUS);
    this._darknessRT = this.add.renderTexture(0, 0, width, height).setOrigin(0, 0).setDepth(20).setScrollFactor(0);
    // Fog of war RT disabled — full-map scaled RT caused black screens on floor 3+
    // because erase() writes in local RT pixel space while the scaled origin sits at
    // world (0,0), making the erase hole appear at the wrong position.
    // The darkness RT (screen-sized, below) provides real-time visibility around the player.
    this._fogRT = null;
    this._fogScaleX = 1;
    this._fogScaleY = 1;
    this._useDarkness = this.dungeonLevel >= FOG_START_LEVEL && this._worldState.difficulty !== 'easy';

    this._buildParticleTexture();

    // Inputs
    this.cursors = this.input.keyboard.createCursorKeys();
    this.wasd = this.input.keyboard.addKeys({ W: 'W', A: 'A', S: 'S', D: 'D' });
    this.fKey = this.input.keyboard.addKey('F');
    this.qKey = this.input.keyboard.addKey('Q');
    this.rKey = this.input.keyboard.addKey('R');
    this.eKey = this.input.keyboard.addKey('E');
    this.tKey = this.input.keyboard.addKey('T');
    this.iKey = this.input.keyboard.addKey('I');
    this.escKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ESC);
    this.backtickKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.BACKTICK);
    this.enterKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ENTER);
    this.spaceKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
    this._numKeys = Array.from({ length: HOTBAR_SLOTS }, (_, i) => this.input.keyboard.addKey(`${i + 1}`));
    this.input.on('pointerdown', ptr => this._onPointerDown(ptr.x, ptr.y));
    this.cameras.main.fadeIn(350, 0, 0, 0);

    // UI
    this.activeSlot = 0;
    this._activeGlowGfx = this.add.graphics().setDepth(92).setScrollFactor(0);
    this._buildHotbar(width, height);
    this._buildTooltip();
    this._buildHud(width, height);
    this._buildMinimap(width, height);
    this._buildPerformancePanel(width);
    this._buildVignette(width, height);
    this._paused = false;
    this._pauseUi = [];
    this._inventoryOpen = false;
    this._inventoryUi = [];
    
    this._toastText = this.add.text(width / 2, height - this._hotbarTotalH() - 20, '', {
      fontFamily: 'monospace', fontSize: '13px', color: '#fbbf24', stroke: '#000000', strokeThickness: 3,
    }).setOrigin(0.5).setDepth(200).setScrollFactor(0).setAlpha(0);

    // Auto-save at the start of the level
    this._saveGame();
    this._autosaveEvent = this.time.addEvent({
      delay: 5000,
      loop: true,
      callback: () => this._saveGame(),
    });

    this._logEvent(`Floor ${this.dungeonLevel} started`);
    this._startDust();
    this._openLevelIntro();

    this.scale.on('resize', this._handleResize, this);
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.scale.off('resize', this._handleResize, this);
      this._autosaveEvent?.remove(false);
      this._dustEvent?.remove(false);
      if (!this._gameOver) this._saveGame();
      multiplayer.stopSendingUpdates();
      clearInterval(this._enemySyncInterval);
    });

    if (this._mpData) this._setupMultiplayer();
  }

  update(time, delta) {
    if (Phaser.Input.Keyboard.JustDown(this.escKey)) this._togglePauseMenu();
    if (Phaser.Input.Keyboard.JustDown(this.backtickKey)) this._openDebugConsole();
    this._updatePerformancePanel();

    this._updateLevelIntroTimer();
    if (this._paused) return;
    if (this._levelIntroActive) return;
    if (this._levelingUp || this._gameOver) return;

    const { width, height } = this.scale;
    const playH = height - this._hotbarTotalH();

    // Movement
    const isLeft = this.cursors.left.isDown || this.wasd.A.isDown;
    const isRight = this.cursors.right.isDown || this.wasd.D.isDown;
    const isUp = this.cursors.up.isDown || this.wasd.W.isDown;
    const isDown = this.cursors.down.isDown || this.wasd.S.isDown;

    if (isLeft) this._lastInputTimes.left = time;
    if (isRight) this._lastInputTimes.right = time;
    if (isUp) this._lastInputTimes.up = time;
    if (isDown) this._lastInputTimes.down = time;

    const moveLeft = isLeft || time - this._lastInputTimes.left < MOVE_COYOTE_MS;
    const moveRight = isRight || time - this._lastInputTimes.right < MOVE_COYOTE_MS;
    const moveUp = isUp || time - this._lastInputTimes.up < MOVE_COYOTE_MS;
    const moveDown = isDown || time - this._lastInputTimes.down < MOVE_COYOTE_MS;

    let ax = 0, ay = 0;
    if (moveLeft) ax -= PLAYER_ACCEL;
    if (moveRight) ax += PLAYER_ACCEL;
    if (moveUp) ay -= PLAYER_ACCEL;
    if (moveDown) ay += PLAYER_ACCEL;
    if (ax !== 0 && ay !== 0) { ax *= 0.7071; ay *= 0.7071; }

    this._physBody.setAcceleration(ax, ay);
    // Sync max velocity with player speed every frame so speed perks/rings take effect
    if (!this._dashActive) this._physBody.setMaxVelocity(this.player.speed, this.player.speed);
    const { cols: _clampC, rows: _clampR } = this.mapManager.getMapSize();
    this.player.x = Phaser.Math.Clamp(this._playerContainer.x, 0, _clampC * 32);
    this.player.y = Phaser.Math.Clamp(this._playerContainer.y, 0, _clampR * 32);
    this._checkRoomEntry();

    // Animation
    const isMoving = moveLeft || moveRight || moveUp || moveDown;
    if (isMoving) this._walkCycle += delta * 0.007;
    if (isMoving && Math.floor(time / 280) !== this._lastFootstepBeat) {
      this._lastFootstepBeat = Math.floor(time / 280);
      audioManager.playSfx(this._getSurfaceAtPlayer() === 'moss' ? 'footstep_moss' : 'footstep_stone');
    }
    const bob = isMoving ? Math.sin(this._walkCycle) * 2.5 : 0;
    const bodyGfx = this._playerContainer.getByName('body');
    const weaponGfx = this._playerContainer.getByName('weapon');
    if (bodyGfx) bodyGfx.y = bob;
    if (weaponGfx) weaponGfx.y = bob;
    if (moveLeft) this._facing = -1;
    if (moveRight) this._facing = 1;
    const squash = isMoving ? Math.min(0.08, this._physBody.velocity.length() / PLAYER_SPEED * 0.08) : 0;
    this._playerContainer.setScale((this._facing || 1) * (1 + squash), 1 - squash);

    const curMain = this.player.equipment.main_hand?.id ?? null;
    if (curMain !== this._prevMainHand) {
      this._redrawWeapon();
      this._prevMainHand = curMain;
    }

    // Update Lighting & Fog
    this._updateTorch(delta);

    // Interaction Checks
    const px = this.player.x, py = this.player.y;
    for (const chest of this._chests) chest.setPromptVisible(chest.isNearPlayer(px, py));
    if (Phaser.Input.Keyboard.JustDown(this.fKey)) this._handleFKey();
    if (Phaser.Input.Keyboard.JustDown(this.qKey)) this._clearActiveHotbarSlot();
    if (Phaser.Input.Keyboard.JustDown(this.rKey)) this._castLightningStrike();
    if (Phaser.Input.Keyboard.JustDown(this.eKey)) this._castVoidBall();
    if (Phaser.Input.Keyboard.JustDown(this.tKey)) this._handleShopKey();
    if (Phaser.Input.Keyboard.JustDown(this.iKey) && !this._chatInputActive) this._toggleInventory();

    // Check Portal
    if (this._portal && this._portalUnlocked() && Math.hypot(px - this._portal.x, py - this._portal.y) < PORTAL_RADIUS) {
      if (!this._mpData || this._mpData.isHost) this._nextLevel();
    }

    for (let i = 0; i < HOTBAR_SLOTS; i++) {
      if (Phaser.Input.Keyboard.JustDown(this._numKeys[i])) { this._setActiveSlot(i); break; }
    }

    this._updateTooltip();
    // Dirty-flag guard: only redraw HP/XP/gold bars when the values actually change,
    // avoiding per-frame Graphics clears that waste GPU time.
    const _hudHp   = this.player.hp;
    const _hudXp   = this.player.xp;
    const _hudGold = this.player.gold;
    const _hudDash = this._dashCooldown;
    if (_hudHp !== this._lastHudHp || _hudXp !== this._lastHudXp || _hudGold !== this._lastHudGold || _hudDash !== this._lastHudDash) {
      this._lastHudHp   = _hudHp;
      this._lastHudXp   = _hudXp;
      this._lastHudGold = _hudGold;
      this._lastHudDash = _hudDash;
      this._updateHud();
    }
    this._updateMinimap();
    this._updateEpicTrail(delta);
    if (Phaser.Input.Keyboard.JustDown(this.enterKey) && !this._chatInputActive) this._openChat();

    if (this._toastText.alpha > 0) this._toastText.setAlpha(Math.max(0, this._toastText.alpha - delta / 1800));
    if (this._attackCooldown > 0) this._attackCooldown -= delta;
    if (this._fireballCooldown > 0) this._fireballCooldown -= delta;
    if (this._lightningCooldown > 0) this._lightningCooldown -= delta;
    if (this._voidBallCooldown > 0) this._voidBallCooldown -= delta;
    if (this._dashCooldown > 0) this._dashCooldown -= delta;
    if (this._iframes > 0) this._iframes -= delta;
    if (Phaser.Input.Keyboard.JustDown(this.spaceKey)) this._doDash();
    if (this._attackBuffer && time >= this._attackBuffer.executeAt && this._attackCooldown <= 0) {
      const buffered = this._attackBuffer;
      this._attackBuffer = null;
      this._doAttack(buffered.x, buffered.y, true);
    } else if (this._attackBuffer && time > this._attackBuffer.discardAt) {
      this._attackBuffer = null;
    }

    // Interpolate remote player avatars toward their last known position
    if (this._remoteGfx) {
      const lerpT = 1 - Math.pow(0.2, Math.min(delta, 100) / 16.67);
      for (const entry of this._remoteGfx.values()) {
        if (entry.targetX === undefined) continue;
        entry.x = entry.x + (entry.targetX - entry.x) * lerpT;
        entry.y = entry.y + (entry.targetY - entry.y) * lerpT;
        entry.g.setPosition(entry.x, entry.y);
        entry.hpBarGfx?.setPosition(entry.x, entry.y);
        entry.nameText.setPosition(entry.x, entry.y - 40);
      }
    }

    // Build targets array: local player + all remote players
    const _allTargets = [{ x: px, y: py }];
    if (this._mpData) {
      for (const state of multiplayer.players.values()) {
        if (Number.isFinite(state.x) && Number.isFinite(state.y))
          _allTargets.push({ x: state.x, y: state.y });
      }
    }

    // Enemies
    const allIds = Array.from(this.itemRegistry.keys());
    for (let i = this._enemies.length - 1; i >= 0; i--) {
      const enemy = this._enemies[i];
      if (enemy.dead) {
        if (!enemy._deathHandled) {
          enemy._deathHandled = true;
          if (enemy.saveId && !this._worldState.defeatedEnemies.includes(enemy.saveId)) {
            this._worldState.defeatedEnemies.push(enemy.saveId);
          }
          audioManager.playSfx('death');
          this._spawnDeathParticles(enemy.container.x, enemy.container.y, enemy.type);
          if (!enemy._mpKilled) {
            // Local kill: give rewards and broadcast death
            this._worldState.kills = (this._worldState.kills || 0) + 1;
            if (enemy.type === 'boss') this._worldState.bossesKilled = (this._worldState.bossesKilled || 0) + 1;
            // Kill streak
            const killNow = this.time.now;
            if (killNow - (this._lastKillTime || 0) < STREAK_WINDOW) {
              this._killStreak = (this._killStreak || 1) + 1;
              if (this._killStreak >= 2) {
                const bonus = this._killStreak * STREAK_BONUS;
                this.player.gold += bonus;
                this._showFloatingReward(enemy.container.x, enemy.container.y + 16, `x${this._killStreak}! +${bonus}g`, 0xfbbf24);
              }
            } else {
              this._killStreak = 1;
            }
            this._lastKillTime = killNow;
            // HP-per-kill perk
            if (this._worldState.hpPerKill) {
              this.player.hp = Math.min(this.player.hp + this._worldState.hpPerKill, this.player.effectiveMaxHp);
            }
            // Blood Pact: each kill restores 4 HP
            if (this._worldState.relics?.bloodPact) {
              this.player.hp = Math.min(this.player.hp + 4, this.player.effectiveMaxHp);
            }
            this._giveXp(enemy.xpReward);
            const goldDrop = enemy.type === 'boss'     ? this._randInt(30, 50)
                           : enemy.type === 'tank'     ? this._randInt(14, 22)
                           : enemy.type === 'spawner'  ? this._randInt(10, 18)
                           : enemy.type === 'mage'     ? this._randInt(8, 14)
                           : enemy.type === 'archer'   ? this._randInt(6, 12)
                           : enemy.type === 'bomber'   ? this._randInt(3, 7)
                           : enemy.type === 'skeleton' ? this._randInt(4, 9)
                           : this._randInt(2, 5);
            this.player.gold += goldDrop;
            this._worldState.damageDealt = (this._worldState.damageDealt || 0);
            this._updateHud();
            this._logEvent(`${enemy.type} defeated (+${enemy.xpReward} XP)`);
            this._showFloatingReward(enemy.container.x, enemy.container.y - 10, `+${goldDrop}g`, 0xfbbf24);
            this._showFloatingReward(enemy.container.x, enemy.container.y - 28, `+${enemy.xpReward}xp`, 0xa78bfa);
            this._checkAchievements();
            // Drop is already handled via enemy._onDrop callback fired in _die().
            if (this._mpData) {
              multiplayer.sendEvent('enemy_killed', { id: enemy.saveId });
              // Also broadcast enemy_dead so guests can clean up arrows from this enemy
              multiplayer.sendEvent('enemy_dead', { id: enemy.saveId });
            }
          }
        }
        if (!enemy.container.scene) this._enemies.splice(i, 1);
        continue;
      }

      if (this._mpData && !this._mpData.isHost) {
        // Guest: interpolate container toward host-synced position (no local AI/physics)
        if (Number.isFinite(enemy._syncX)) {
          const dx = enemy._syncX - enemy.container.x;
          const dy = enemy._syncY - enemy.container.y;
          const dist = Math.hypot(dx, dy);
          if (dist > 120) {
            // Too far — teleport immediately
            enemy.container.x = enemy._syncX;
            enemy.container.y = enemy._syncY;
          } else if (dist > 1) {
            // Delta-time normalized exponential lerp (~0.3 per frame at 60fps)
            const t = 1 - Math.pow(0.7, delta / 16.67);
            enemy.container.x += dx * t;
            enemy.container.y += dy * t;
          }
        }
        // Guest melee damage check against local player
        // Use the enemy's own attackRange (not a hardcoded constant) so melee enemies
        // that stop at e.g. 52px (skeleton) still register a hit on the guest side.
        // Ranged enemies (archer/mage) deal damage through projectiles, not contact.
        if (enemy._guestAtkTimer > 0) enemy._guestAtkTimer -= delta;
        const gDist = Math.hypot(enemy.container.x - px, enemy.container.y - py);
        const isRanged = enemy.type === 'archer' || enemy.type === 'mage';
        const gMeleeR  = isRanged ? (CONTACT_RADIUS + 18) : enemy.attackRange;
        if (gDist < gMeleeR && !(enemy._guestAtkTimer > 0)) {
          this._playerTakeDamage(enemy.damage, enemy);
          enemy._guestAtkTimer = enemy.attackCooldown;
        }
        enemy._drawHpBar();
      } else {
        // Host: full AI simulation
        enemy.update(delta, _allTargets);
        if (enemy.wantsAttack && enemy._knockbackTimer <= 0 && Math.hypot(enemy.container.x - px, enemy.container.y - py) < CONTACT_RADIUS + 18) {
          this._playerTakeDamage(enemy.damage, enemy);
        }
        // Tank shockwave: AoE slam that also affects player
        if (enemy.type === 'tank' && enemy._shockwaveReady) {
          enemy._shockwaveReady = false;
          const ex = enemy.container.x, ey = enemy.container.y;
          this._spawnPickupParticles(ex, ey, 0x6b7280);
          this.cameras.main.shake(200, 0.012);
          if (Math.hypot(ex - px, ey - py) < TANK_SHOCKWAVE_R) {
            this._playerTakeDamage(Math.ceil(enemy.damage * 0.6), enemy);
          }
        }
        // Spawner: emit a slime nearby
        if (enemy.type === 'spawner' && enemy.wantsSpawn) {
          const ex = enemy.container.x, ey = enemy.container.y;
          let sx, sy, _tries = 0;
          do {
            const ang = Math.random() * Math.PI * 2;
            const dist2 = 40 + Math.random() * 30;
            sx = ex + Math.cos(ang) * dist2;
            sy = ey + Math.sin(ang) * dist2;
          } while (++_tries < 10 &&
            this._wallTileMap.has(`${Math.floor(sx / this._tileW)},${Math.floor(sy / this._tileH)}`));
          if (this._wallTileMap.has(`${Math.floor(sx / this._tileW)},${Math.floor(sy / this._tileH)}`)) {
            // All candidate positions were inside walls — skip this spawn tick.
          } else {
            const minion = new Enemy(this, sx, sy, 'slime');
            minion.saveId = `spawner_minion_${this.time.now}_${Math.random()}`;
            minion.maxHp = Math.max(1, Math.floor(minion.maxHp * 0.6));
            minion.hp    = minion.maxHp;
            this.physics.add.collider(minion.container, this._wallGroup);
            this._enemies.push(minion);
            this._spawnPickupParticles(sx, sy, 0xa855f7);
          }
        }
        if (enemy.wantsShoot) {
          if (enemy.type === 'boss') {
            for (const angle of (enemy._shootAngles || [])) {
              this._spawnEnemyArrow(enemy.container.x, enemy.container.y, angle, true, enemy.saveId);
              if (this._mpData?.isHost)
                multiplayer.sendEvent('enemy_arrow', { x: Math.round(enemy.container.x), y: Math.round(enemy.container.y), angle, isBolt: true });
            }
          } else {
            const isBolt = enemy.type === 'mage';
            const angle  = enemy._shootAngle ?? 0;
            this._spawnEnemyArrow(enemy.container.x, enemy.container.y, angle, isBolt, enemy.saveId);
            if (this._mpData?.isHost)
              multiplayer.sendEvent('enemy_arrow', { x: Math.round(enemy.container.x), y: Math.round(enemy.container.y), angle, isBolt });
          }
        }
        if (enemy.wantsExplode) this._bomberExplode(enemy);
        // Burn DoT (only on host/solo)
        if (enemy._burnTimer > 0) {
          enemy._burnTimer -= delta;
          enemy._burnTickTimer = (enemy._burnTickTimer || 0) - delta;
          if (enemy._burnTickTimer <= 0) {
            enemy._burnTickTimer = 600;
            const bDmg = Math.max(1, Math.round(4 * this._damageMultiplier));
            enemy.takeDamage(bDmg, 0, 0);
            this._worldState.damageDealt = (this._worldState.damageDealt || 0) + bDmg;
            this._showDamageNumber(enemy.container.x, enemy.container.y - 22, bDmg, false, false);
          }
        }
      }
    }

    // ── Optional Boss (level 7+) — separate from portal-unlock enemies ────────
    for (let i = this._optionalBosses.length - 1; i >= 0; i--) {
      const boss = this._optionalBosses[i];
      if (boss.dead) {
        if (!boss._deathHandled) {
          boss._deathHandled = true;
          this._worldState.kills = (this._worldState.kills || 0) + 1;
          this._worldState.bossesKilled = (this._worldState.bossesKilled || 0) + 1;
          this._spawnDeathParticles(boss.container.x, boss.container.y, 'boss');
          this.cameras.main.shake(400, 0.022);
          this._giveXp(boss.xpReward * 2);
          const bossGold = this._randInt(40, 70);
          this.player.gold += bossGold;
          this._showFloatingReward(boss.container.x, boss.container.y - 10, `+${bossGold}g`, 0xfbbf24);
          this._showFloatingReward(boss.container.x, boss.container.y - 30, `+${boss.xpReward * 2}xp`, 0xa78bfa);
          this._updateHud();
          // Drop the boss key
          this._dropBossKey(boss.container.x, boss.container.y);
          this._logEvent('Optional boss defeated - key dropped!');
          this._showToast('Key obtained! Find the locked chest.');
          this._checkAchievements();
        }
        if (!boss.container.scene) this._optionalBosses.splice(i, 1);
        continue;
      }
      if (this._mpData && !this._mpData.isHost) {
        // Guest: interpolate boss position
        if (Number.isFinite(boss._syncX)) {
          const dx = boss._syncX - boss.container.x;
          const dy = boss._syncY - boss.container.y;
          const dist = Math.hypot(dx, dy);
          if (dist > 120) { boss.container.x = boss._syncX; boss.container.y = boss._syncY; }
          else if (dist > 1) {
            const t = 1 - Math.pow(0.7, delta / 16.67);
            boss.container.x += dx * t;
            boss.container.y += dy * t;
          }
        }
        boss._drawHpBar();
      } else {
        boss.update(delta, _allTargets);
        if (boss.wantsAttack && boss._knockbackTimer <= 0 && Math.hypot(boss.container.x - px, boss.container.y - py) < CONTACT_RADIUS + 24) {
          this._playerTakeDamage(boss.damage, boss);
        }
        if (boss.wantsShoot) {
          for (const angle of (boss._shootAngles || [])) {
            this._spawnEnemyArrow(boss.container.x, boss.container.y, angle, true);
            if (this._mpData?.isHost)
              multiplayer.sendEvent('enemy_arrow', { x: Math.round(boss.container.x), y: Math.round(boss.container.y), angle, isBolt: true });
          }
        }
      }
    }

    // ── Locked chest proximity ────────────────────────────────────────────────
    for (const lc of this._lockedChests) {
      if (lc.opened) continue;
      const near = Math.hypot(lc.x - px, lc.y - py) < 72;
      lc.promptText?.setAlpha(near ? 1 : 0);
    }

    // ── Boss key pickup ───────────────────────────────────────────────────────
    if (this._bossKeyPickup && !this._hasBossKey) {
      const kp = this._bossKeyPickup;
      if (Math.hypot(kp.x - px, kp.y - py) < 40) {
        this._hasBossKey = true;
        kp.g?.destroy();
        kp.label?.destroy();
        this._bossKeyPickup = null;
        this._showToast('Boss Key picked up!');
        this._logEvent('Boss Key obtained');
      }
    }

    // World Items
    for (let i = this._worldItems.length - 1; i >= 0; i--) {
      const wi = this._worldItems[i];
      if (wi.collected) { this._worldItems.splice(i, 1); continue; }
      if (Math.hypot(wi.x - px, wi.y - py) < WORLD_PICKUP_R) {
        this._collectWorldItem(wi);
        // Only remove from list if the item was actually collected
        // (rejected items stay on the ground so the player can see them)
        if (wi.collected) this._worldItems.splice(i, 1);
      }
    }

    for (let i = this._fireballs.length - 1; i >= 0; i--) {
      const fireball = this._fireballs[i];
      if (!fireball.active) {
        fireball.g.destroy();
        this._fireballs.splice(i, 1);
        continue;
      }
      const step = FIREBALL_SPEED * (delta / 1000);
      fireball.x += fireball.vx * (delta / 1000);
      fireball.y += fireball.vy * (delta / 1000);
      fireball.traveled = (fireball.traveled ?? 0) + step;
      fireball.g.setPosition(fireball.x, fireball.y);

      const col = Math.floor(fireball.x / this._tileW);
      const row = Math.floor(fireball.y / this._tileH);
      // Look-ahead: check 10px ahead to prevent phasing through thin walls
      const stepDist = 10;
      const fbAngle = Math.atan2(fireball.vy, fireball.vx);
      const stepX = fireball.x + Math.cos(fbAngle) * stepDist;
      const stepY = fireball.y + Math.sin(fbAngle) * stepDist;
      const stepCol = Math.floor(stepX / this._tileW);
      const stepRow = Math.floor(stepY / this._tileH);
      if (fireball.traveled >= FIREBALL_RANGE || this._wallTileMap.has(`${col},${row}`) || this._wallTileMap.has(`${stepCol},${stepRow}`)) {
        fireball.active = false;
        this._spawnPickupParticles(fireball.x, fireball.y, 0xf97316);
        continue;
      }

      for (const enemy of [...this._enemies, ...(this._optionalBosses ?? [])]) {
        if (!enemy.isAlive) continue;
        const dist = Math.hypot(enemy.container.x - fireball.x, enemy.container.y - fireball.y);
        if (dist > 28) continue;
        const fbDmg = Math.round(FIREBALL_DAMAGE * this._damageMultiplier);
        enemy.takeDamage(fbDmg, fireball.vx * 0.3, fireball.vy * 0.3);
        this._worldState.damageDealt = (this._worldState.damageDealt || 0) + fbDmg;
        this._showDamageNumber(enemy.container.x, enemy.container.y - 24, fbDmg, false, false);
        this._spawnPickupParticles(fireball.x, fireball.y, 0xfb923c);
        // Apply burn status effect
        enemy._burnTimer     = 2400;
        enemy._burnTickTimer = 600;
        fireball.active = false;
        break;
      }
    }

    for (let i = this._voidBalls.length - 1; i >= 0; i--) {
      const orb = this._voidBalls[i];
      if (!orb.active) {
        orb.ringInterval?.remove();
        orb.g.destroy();
        this._voidBalls.splice(i, 1);
        continue;
      }

      orb.x += orb.vx * (delta / 1000);
      orb.y += orb.vy * (delta / 1000);
      orb.life -= delta;
      orb.g.setPosition(orb.x, orb.y);

      const col = Math.floor(orb.x / this._tileW);
      const row = Math.floor(orb.y / this._tileH);
      if (orb.life <= 0 || this._wallTileMap.has(`${col},${row}`)) {
        orb.active = false;
        this._spawnPickupParticles(orb.x, orb.y, 0x67e8f9);
        continue;
      }

      for (const enemy of this._enemies) {
        if (!enemy.isAlive) continue;
        const dx = orb.x - enemy.container.x;
        const dy = orb.y - enemy.container.y;
        const dist = Math.hypot(dx, dy);
        if (dist > VOID_BALL_PULL_RADIUS || dist <= 0.001) continue;
        const pull = 1 - dist / VOID_BALL_PULL_RADIUS;
        enemy._physBody?.setVelocity(
          (dx / dist) * VOID_BALL_PULL_FORCE * pull,
          (dy / dist) * VOID_BALL_PULL_FORCE * pull,
        );
        enemy._knockbackTimer = Math.max(enemy._knockbackTimer || 0, 80);
        if (dist < 18 && !orb.hitIds.has(enemy.saveId || enemy.type)) {
          orb.hitIds.add(enemy.saveId || enemy.type);
          const vbDmg = Math.max(1, Math.round(8 * this._damageMultiplier));
          enemy.takeDamage(vbDmg, (dx / dist) * 80, (dy / dist) * 80);
          this._showDamageNumber(enemy.container.x, enemy.container.y - 24, vbDmg, false, false);
          // Void Heart: absorb life on each void ball hit
          if (this._worldState.relics?.voidHeart) {
            this.player.hp = Math.min(this.player.hp + 3, this.player.effectiveMaxHp);
            this._updateHud();
          }
        }
      }
    }

    // ── Enemy Arrows ──────────────────────────────────────────────────────────
    for (let i = this._enemyArrows.length - 1; i >= 0; i--) {
      const arrow = this._enemyArrows[i];
      if (!arrow.active) { arrow.g.destroy(); this._enemyArrows.splice(i, 1); continue; }
      arrow.x    += arrow.vx * (delta / 1000);
      arrow.y    += arrow.vy * (delta / 1000);
      arrow.life -= delta;
      arrow.g.setPosition(arrow.x, arrow.y).setRotation(Math.atan2(arrow.vy, arrow.vx));
      const col = Math.floor(arrow.x / this._tileW);
      const row = Math.floor(arrow.y / this._tileH);
      if (arrow.life <= 0 || this._wallTileMap.has(`${col},${row}`)) {
        arrow.active = false;
        continue;
      }
      if (this._iframes <= 0 && Math.hypot(arrow.x - px, arrow.y - py) < 20) {
        this._playerTakeDamage(arrow.damage);
        arrow.active = false;
      }
    }

    // ── Shop NPC prompts ──────────────────────────────────────────────────────
    if (this._shopNpcs) {
      for (const shop of this._shopNpcs) {
        shop.promptText.setAlpha(this._shopUiOpen ? 0 : 1);
      }
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Save & Load
  // ─────────────────────────────────────────────────────────────────────────────
  _saveGame() {
    const data = {
      level: this.dungeonLevel,
      seed: this.seed,
      player: this._serializePlayerState(),
      world: this._serializeWorldState(),
    };
    try {
      localStorage.setItem(SAVE_KEY, JSON.stringify(data));
    } catch (err) {
      console.warn('Failed to save game:', err);
    }
  }

  _serializePlayerState() {
    return {
      x: this.player.x,
      y: this.player.y,
      hp: this.player.hp,
      level: this.player.level,
      xp: this.player.xp,
      xpToNext: this.player.xpToNext,
      maxHp: this.player.maxHp,
      baseAttack: this.player.baseAttack,
      baseDefense: this.player.baseDefense,
      gold: this.player.gold,
      inventory: this.player.inventory.map(s => ({ id: s.item.id, qty: s.quantity })),
      hotbar: [...this.player.hotbar],
      equipment: {
        head: this.player.equipment.head?.id || null,
        chest: this.player.equipment.chest?.id || null,
        main_hand: this.player.equipment.main_hand?.id || null,
      },
    };
  }

  _restorePlayerState(state) {
    if (!state) return;

    this.player.inventory = [];
    this.player.hotbar = Array(HOTBAR_SLOTS).fill(null);
    this.player.equipment = { head: null, chest: null, main_hand: null };

    this.player.hp = state.hp ?? this.player.hp;
    this.player.x = state.x ?? this.player.x;
    this.player.y = state.y ?? this.player.y;
    this.player.level = state.level ?? this.player.level;
    this.player.xp = state.xp ?? this.player.xp;
    this.player.xpToNext = state.xpToNext ?? this.player.xpToNext;
    this.player.maxHp = state.maxHp ?? this.player.maxHp;
    this.player.baseAttack = state.baseAttack ?? this.player.baseAttack;
    this.player.baseDefense = state.baseDefense ?? this.player.baseDefense;
    this.player.gold = state.gold ?? this.player.gold;

    for (const entry of state.inventory || []) {
      const itemDef = this.itemRegistry.get(entry.id);
      if (itemDef) this.player.addItem(itemDef, entry.qty || 1);
    }

    if (Array.isArray(state.hotbar)) {
      for (let i = 0; i < HOTBAR_SLOTS; i++) this.player.hotbar[i] = state.hotbar[i] ?? null;
    }

    const equipment = state.equipment || {};
    if (equipment.head) this.player.equipment.head = this.itemRegistry.get(equipment.head) || null;
    if (equipment.chest) this.player.equipment.chest = this.itemRegistry.get(equipment.chest) || null;
    if (equipment.main_hand) this.player.equipment.main_hand = this.itemRegistry.get(equipment.main_hand) || null;

    this.player.hp = Math.min(this.player.hp, this.player.effectiveMaxHp);
  }

  _handleResize() {
    // In multiplayer the FIT scale mode handles canvas scaling automatically.
    // Restarting would drop the WebSocket connection and lose all party state.
    if (this._mpData) return;
    this.scene.restart({
      isNewGame: false,
      level: this.dungeonLevel,
      seed: this.seed,
      playerState: this._serializePlayerState(),
      worldState: this._serializeWorldState(),
    });
  }

  _serializeWorldState() {
    return {
      openedChests: [...(this._worldState?.openedChests || [])],
      defeatedEnemies: [...(this._worldState?.defeatedEnemies || [])],
      brokenWalls: [...(this._worldState?.brokenWalls || [])],
      difficulty: this._worldState?.difficulty || 'hard',
      performanceVisible: !!this._worldState?.performanceVisible,
      godMode: !!this._worldState?.godMode,
      kills: this._worldState?.kills || 0,
      bossesKilled: this._worldState?.bossesKilled || 0,
      damageDealt: this._worldState?.damageDealt || 0,
      damageTaken: this._worldState?.damageTaken || 0,
      itemsFound: this._worldState?.itemsFound || 0,
      classId: this._worldState?.classId || null,
      canUseSpells: this._worldState?.canUseSpells || false,
      damageMultiplier: this._worldState?.damageMultiplier || 1,
      runStartTime: this._worldState?.runStartTime || Date.now(),
      unlockedAchievements: [...(this._worldState?.unlockedAchievements || [])],
      lifeSteal:        this._worldState?.lifeSteal        || 0,
      hpPerKill:        this._worldState?.hpPerKill        || 0,
      atkCooldownMult:  this._worldState?.atkCooldownMult  || 1,
      absorbedPassives: [...(this._worldState?.absorbedPassives || [])],
      relics:           { ...(this._worldState?.relics || {}) },
      deathWardUsed:    this._worldState?.deathWardUsed ?? false,
    };
  }

  _getSurfaceAtPlayer() {
    const col = Math.floor(this.player.x / this._tileW);
    const row = Math.floor(this.player.y / this._tileH);
    return this._surfaceMap?.get(`${col},${row}`) || 'stone';
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Map Generation & Spawning
  // ─────────────────────────────────────────────────────────────────────────────
  _buildTilemap(width, height, map) {
    // Fixed tile size so the map is larger than the viewport and the camera scrolls
    const TILE_W = 32;
    const TILE_H = 32;
    this._tileW = TILE_W;
    this._tileH = TILE_H;
    this._mapGrid = map;

    const spawnRoom = this.rooms[0];
    const wantsSavedPosition = Number.isFinite(this._incomingPlayerState?.x) && Number.isFinite(this._incomingPlayerState?.y);
    const desiredX = wantsSavedPosition ? this._incomingPlayerState.x : (spawnRoom.cx + 0.5) * TILE_W;
    const desiredY = wantsSavedPosition ? this._incomingPlayerState.y : (spawnRoom.cy + 0.5) * TILE_H;

    if (!this.textures.exists('__wt__')) {
      const _wt = this.textures.createCanvas('__wt__', 1, 1);
      const _wtCtx = _wt.getContext();
      _wtCtx.fillStyle = '#ffffff';
      _wtCtx.fillRect(0, 0, 1, 1);
      _wt.refresh();
    }
    this._wallGroup = this.physics.add.staticGroup();
    this._floorGfx = this.add.graphics().setDepth(0);
    // Single shared Graphics object for ALL wall tiles — avoids 350-2000+ draw calls per frame
    this._wallGfx = this.add.graphics().setDepth(1);
    this._wallTileMap = new Map();
    this._surfaceMap = new Map();
    this._floorTheme = getFloorTheme(this.dungeonLevel);

    const { cols: _mapCols, rows: _mapRows } = this.mapManager.getMapSize();
    for (let row = 0; row < _mapRows; row++) {
      for (let col = 0; col < _mapCols; col++) {
        const wx = col * TILE_W, wy = row * TILE_H;
        const wallId = `floor:${this.dungeonLevel}:wall:${col}:${row}`;
        const broken = this._worldState.brokenWalls.includes(wallId);
        if (map[row][col] === 1 && !broken) {
          // make.image with add:false creates the object WITHOUT adding it to the scene
          // display list — eliminates 500-2900+ invisible items from the render batch
          // on floors 3+, which caused a first-frame freeze that presented as a black screen.
          // Physics still works because physics.world.enable registers the static body
          // independently of the display list. Body size is set explicitly after group.add()
          // to guarantee correct 32×32 bounds regardless of group createCallbackHandler.
          const img = this.make.image({ x: wx + TILE_W / 2, y: wy + TILE_H / 2, key: '__wt__', add: false });
          this.physics.world.enable(img, Phaser.Physics.Arcade.STATIC_BODY);
          this._wallGroup.add(img);
          img.body.setSize(TILE_W, TILE_H);
          img.body.reset(wx + TILE_W / 2, wy + TILE_H / 2);
          // Store as `body` so all downstream code (colliders, _breakWall) is unchanged.
          this._wallTileMap.set(`${col},${row}`, { body: img, col, row, wallId });
        } else {
          this._drawFloorTile(col, row);
        }
      }
    }

    // Draw all wall visuals in one batched pass
    this._rebuildWallGfx();
    // NOTE: _wallGroup.refresh() intentionally omitted. Each body is explicitly sized
    // and positioned via img.body.setSize()/reset() after group.add(); calling refresh()
    // would re-derive bounds from the 1×1 '__wt__' texture, resetting every body to 1×1.

    const safeSpawn = this._findSafeWorldPosition(desiredX, desiredY, spawnRoom);
    this.player.x = safeSpawn.x;
    this.player.y = safeSpawn.y;

    this._spawnChests();
    this._spawnEnemies();
    this._spawnPortal();
    this._spawnShops();
    if (this.dungeonLevel >= 7) this._spawnOptionalBossLair();
  }

  _findSafeWorldPosition(worldX, worldY, preferredRoom = null) {
    const { cols: _fc, rows: _fr } = this.mapManager.getMapSize();
    const preferredCol = Phaser.Math.Clamp(Math.floor(worldX / this._tileW), 0, _fc - 1);
    const preferredRow = Phaser.Math.Clamp(Math.floor(worldY / this._tileH), 0, _fr - 1);
    const isFloor = (col, row) => {
      if (row < 0 || row >= _fr || col < 0 || col >= _fc) return false;
      return this._mapGrid?.[row]?.[col] === 0 && !this._wallTileMap.has(`${col},${row}`);
    };

    if (isFloor(preferredCol, preferredRow)) {
      return { x: (preferredCol + 0.5) * this._tileW, y: (preferredRow + 0.5) * this._tileH };
    }

    for (let radius = 1; radius <= Math.max(_fc, _fr); radius++) {
      for (let dy = -radius; dy <= radius; dy++) {
        for (let dx = -radius; dx <= radius; dx++) {
          const col = preferredCol + dx;
          const row = preferredRow + dy;
          if (!isFloor(col, row)) continue;
          return { x: (col + 0.5) * this._tileW, y: (row + 0.5) * this._tileH };
        }
      }
    }

    if (preferredRoom) {
      return { x: (preferredRoom.cx + 0.5) * this._tileW, y: (preferredRoom.cy + 0.5) * this._tileH };
    }
    return { x: this._tileW * 1.5, y: this._tileH * 1.5 };
  }

  _drawFloorTile(col, row) {
    const wx = col * this._tileW;
    const wy = row * this._tileH;
    const th = this._floorTheme || getFloorTheme(this.dungeonLevel);
    const moss = (row * 11 + col * 7 + this.dungeonLevel) % 9 === 0;
    const base = moss ? th.moss1 : ((row + col) % 2 === 0 ? th.floor1a : th.floor1b);
    // Moss tiles use moss2 for accent; stone tiles use floor2
    const accent = moss ? th.moss2 : th.floor2;
    this._surfaceMap.set(`${col},${row}`, moss ? 'moss' : 'stone');
    this._floorGfx.fillStyle(base, 1).fillRect(wx, wy, this._tileW - 1, this._tileH - 1);
    this._floorGfx.fillStyle(accent, 0.12).fillRect(wx + 4, wy + 4, this._tileW - 8, this._tileH - 8);
    // Faint cross-hatch variation on every 7th tile for visual texture
    if ((row * 13 + col * 7) % 7 === 0) {
      this._floorGfx.lineStyle(1, th.floor2, 0.08).lineBetween(wx + 8, wy + 8, wx + this._tileW - 8, wy + this._tileH - 8);
    }
  }

  // Redraws all non-broken wall tiles onto the single shared _wallGfx object.
  // Called once on map build and again whenever a wall is carved/broken.
  _rebuildWallGfx() {
    const th = this._floorTheme || getFloorTheme(this.dungeonLevel);
    const TW = this._tileW, TH = this._tileH;
    this._wallGfx.clear();
    for (const entry of this._wallTileMap.values()) {
      const wx = entry.col * TW;
      const wy = entry.row * TH;
      // Draw order matches original per-tile order: base → inner → outline → bottom highlight → left shadow
      this._wallGfx
        .fillStyle(th.wall1, 1).fillRect(wx, wy, TW, TH)
        .fillStyle(th.wall2, 0.6).fillRect(wx + 2, wy + 2, TW - 4, TH - 4)
        .lineStyle(1, th.wallLine, 0.4).strokeRect(wx, wy, TW, TH)
        .fillStyle(th.wallLine, 0.45).fillRect(wx, wy + TH - 3, TW, 3)
        .fillStyle(0x000000, 0.25).fillRect(wx, wy, 2, TH);
    }
  }

  _spawnChests() {
    this._chests = [];
    const MIN_CHEST_DIST = 72; // px — minimum separation between any two chests
    const allIds = Array.from(this.itemRegistry.keys()).filter(id => !id.startsWith('spell_'));
    const spellIds = this._worldState.canUseSpells
      ? Array.from(this.itemRegistry.keys()).filter(id => id.startsWith('spell_') && !this._playerOwnsItem(id))
      : [];
    for (let i = 1; i < this.rooms.length - 1; i++) {
      const r = this.rooms[i];
      // Only shop rooms have no chest (they have a merchant instead)
      if (r.type === 'shop') continue;
      const chestId = `floor:${this.dungeonLevel}:chest:${i}`;
      if (this._worldState.openedChests.includes(chestId)) continue;
      const cx = (r.cx + 0.5) * this._tileW, cy = (r.cy + 0.5) * this._tileH;
      // Treasure rooms: offset chest slightly + guaranteed rare loot + more choices
      const isTreasure = r.type === 'treasure';
      const loot = [allIds[this._randInt(0, allIds.length - 1)], 'potion_health'];
      if (isTreasure) {
        // Add 2 extra items to the loot pool for more interesting picks
        loot.push(allIds[this._randInt(0, allIds.length - 1)]);
        if (spellIds.length > 0) loot.push(spellIds[this._randInt(0, spellIds.length - 1)]);
      } else if (spellIds.length > 0 && this._randFloat() < 0.28) {
        loot.push(spellIds[this._randInt(0, spellIds.length - 1)]);
      }
      // Cross-room dedup: two adjacent rooms can have near-identical cx/cy.
      // Skip placement rather than stacking chests visually on top of each other.
      if (this._chests.some(c => Math.hypot(c.x - cx, c.y - cy) < MIN_CHEST_DIST)) continue;
      const chest = new Chest(this, cx, cy, loot);
      chest.saveId    = chestId;
      chest.rollIndex = this._randInt(0, loot.length - 1);
      chest.isTreasure = isTreasure;
      this._chests.push(chest);
      // Visual marker for treasure room: gold ring on floor
      if (isTreasure) this._drawTreasureRoomMarker(r);
    }

    // Guarantee at least 2 chests in treasure rooms (reuses allIds from above)
    for (const r of this.rooms) {
      if (r.type !== 'treasure') continue;
      // Skip rooms too small to physically fit a second chest without overlap.
      // w<5 or h<4 leaves only 1-2 valid tile positions — 8 retries can't avoid the first chest.
      if (r.w < 5 || r.h < 4) continue;
      const chestsInRoom = this._chests.filter(c => {
        const cc = Math.floor(c.x / this._tileW);
        const cr = Math.floor(c.y / this._tileH);
        return cc >= r.x && cc < r.x + r.w && cr >= r.y && cr < r.y + r.h;
      }).length;
      for (let add = chestsInRoom; add < 2; add++) {
        const extraChestId = `floor:${this.dungeonLevel}:treasure:${r.x}:${r.y}:${add}`;
        if (this._worldState.openedChests.includes(extraChestId)) continue;
        // Find a position that doesn't overlap existing chests (up to 8 attempts).
        let tcx, tcy, attempts = 0;
        do {
          tcx = (r.x + 1 + Math.floor(this._randFloat() * (r.w - 2)) + 0.5) * this._tileW;
          tcy = (r.y + 1 + Math.floor(this._randFloat() * (r.h - 2)) + 0.5) * this._tileH;
          attempts++;
        } while (attempts < 8 && this._chests.some(c => Math.hypot(c.x - tcx, c.y - tcy) < MIN_CHEST_DIST));
        // Final dedup: if we exhausted retries and still overlap, skip rather than place
        if (this._chests.some(c => Math.hypot(c.x - tcx, c.y - tcy) < MIN_CHEST_DIST)) continue;
        const extraLoot = [
          allIds[this._randInt(0, allIds.length - 1)],
          allIds[this._randInt(0, allIds.length - 1)],
          'potion_health',
        ];
        const extraChest = new Chest(this, tcx, tcy, extraLoot);
        extraChest.saveId    = extraChestId;
        extraChest.rollIndex = this._randInt(0, extraLoot.length - 1);
        extraChest.isTreasure = true;
        this._chests.push(extraChest);
      }
    }

    // Final dedup: remove any chest too close to another (handles edge cases from both loops)
    this._chests = this._chests.filter((c, i) =>
      !this._chests.slice(0, i).some(other => Math.hypot(other.x - c.x, other.y - c.y) < 64)
    );
  }

  _spawnEnemies() {
    this._enemies = [];
    const isBossFloor = this.dungeonLevel % 5 === 0;
    for (let i = 1; i < this.rooms.length; i++) {
      const r = this.rooms[i];
      // No enemies in shop rooms — safe zone for buying
      if (r.type === 'shop') continue;
      // Boss floor: portal room gets the boss instead of regular enemies
      if (isBossFloor && r.type === 'portal') {
        this._spawnBoss(r, i);
        continue;
      }
      const isEasy = this._worldState.difficulty === 'easy';
      const bonus  = isEasy ? -1 : 2;  // easy: -1 (fewer), hard: +2 (more)
      const cap    = isEasy ? 2  : 5;  // easy: max 2/room, hard: max 5/room
      // Trap rooms have fewer enemies (traps are the main hazard)
      const roomCap = r.type === 'trap' ? Math.min(cap, 2) : cap;
      // Extra enemies scale with floor progression — easy scales slowly, hard quickly
      const extraCount = isEasy
        ? Math.min(1, Math.floor((this.dungeonLevel - 1) / 5))  // easy: +1 every 5 floors
        : Math.min(3, Math.floor((this.dungeonLevel - 1) / 3)); // hard: +1 every 3 floors
      const base  = Math.ceil(this.dungeonLevel / 2) + this._randInt(0, 1);
      const count = Math.max(1, Math.min(roomCap + extraCount, base + bonus + extraCount));
      for (let e = 0; e < count; e++) {
        const enemyId = `floor:${this.dungeonLevel}:enemy:${i}:${e}`;
        if (this._worldState.defeatedEnemies.includes(enemyId)) continue;
        // Snap to tile centers so the enemy body never straddles a wall edge.
        const col = r.x + 1 + Math.floor(this._randFloat() * (r.w - 2));
        const row = r.y + 1 + Math.floor(this._randFloat() * (r.h - 2));
        const x = (col + 0.5) * this._tileW;
        const y = (row + 0.5) * this._tileH;
        // Enemy type variety scales with dungeon level
        const roll = this._randFloat();
        let type;
        if (this.dungeonLevel >= 5 && e === 0 && roll > 0.88) {
          type = 'spawner';   // ~12% chance for first enemy to be a spawner (floor 5+)
        } else if (this.dungeonLevel >= 4 && roll > 0.88) {
          type = 'tank';      // ~12% tanks from floor 4+
        } else if (this.dungeonLevel >= 3 && roll > 0.78) {
          type = 'bomber';    // ~10%
        } else if (roll > 0.58) {
          type = 'mage';      // ~20%
        } else if (roll > 0.36) {
          type = 'archer';    // ~22%
        } else if (roll > 0.16) {
          type = 'skeleton';  // ~20%
        } else {
          type = 'slime';     // ~16%
        }
        // Treasure room: first enemy is always a mage guardian
        if (r.type === 'treasure' && e === 0) type = 'mage';
        const enemy = new Enemy(this, x, y, type);
        enemy.saveId = enemyId;
        // Scale enemy stats based on dungeon level via _floorScale.
        // Easy mode further reduces stats by 30% to maintain a meaningful difficulty gap.
        const scaleMult = this._worldState.difficulty === 'easy' ? 0.7 : 1.0;
        const baseHp  = enemy.maxHp;
        const baseAtk = enemy.damage;
        enemy.maxHp  = Math.round(baseHp  * this._floorScale(this.dungeonLevel) * scaleMult);
        enemy.hp     = enemy.maxHp;
        enemy.damage = Math.round(baseAtk * this._floorScale(this.dungeonLevel) * scaleMult);
        enemy._onDrop = (id, ex, ey) => { const def = this.itemRegistry.get(id); if (def) this._spawnWorldItem(ex, ey, def); };
        this.physics.add.collider(enemy.container, this._wallGroup);
        this._enemies.push(enemy);
      }
    }
  }

  _checkRoomEntry() {
    if (this._levelIntroActive || this._gameOver || this._levelingUp) return;
    const px = this.player.x, py = this.player.y;
    for (let i = 0; i < this.rooms.length; i++) {
      if (this._visitedRooms.has(i)) continue;
      const r = this.rooms[i];
      const rLeft = r.x * this._tileW, rTop = r.y * this._tileH;
      const rRight = (r.x + r.w) * this._tileW, rBottom = (r.y + r.h) * this._tileH;
      if (px >= rLeft && px <= rRight && py >= rTop && py <= rBottom) {
        this._visitedRooms.add(i);
        // Camera shake for notable rooms (no zoom)
        if (r.type === 'boss' || r.type === 'treasure' || r.type === 'portal' || r.type === 'trap') {
          if (r.type === 'boss') this.cameras.main.shake(120, 0.006);
          else this.cameras.main.shake(60, 0.003);
        }
      }
    }
  }

  _spawnBoss(room, roomIndex) {
    const bossId = `floor:${this.dungeonLevel}:boss:${roomIndex}`;
    if (this._worldState.defeatedEnemies.includes(bossId)) return;
    const x = (room.cx + 0.5) * this._tileW;
    const y = (room.cy + 0.5) * this._tileH;
    const boss = new Enemy(this, x, y, 'boss');
    boss.saveId = bossId;
    boss.maxHp  = Math.floor(boss.maxHp * (1 + (this.dungeonLevel - 1) * 0.15));
    boss.hp     = boss.maxHp;
    boss.damage = Math.floor(boss.damage * (1 + (this.dungeonLevel - 1) * 0.1));
    boss._onDrop = (id, bx2, by2) => { const def = this.itemRegistry.get(id); if (def) this._spawnWorldItem(bx2, by2, def); };
    this.physics.add.collider(boss.container, this._wallGroup);
    this._enemies.push(boss);
    // Show boss warning toast
    this.time.delayedCall(800, () => {
      this._showToast('!! BOSS FLOOR !!');
      this._logEvent(`Boss awakens on floor ${this.dungeonLevel}!`);
    });
  }

  _spawnPortal() {
    const portalRoom = this.rooms[this.rooms.length - 1];
    const px = (portalRoom.cx + 0.5) * this._tileW;
    const py = (portalRoom.cy + 0.5) * this._tileH;

    this._portal = { x: px, y: py };
    this._portalLabel = null;

    // Static base: outer ring drawn once — never redrawn per-frame.
    // Depth 22 — above fog (depth 21) so the portal glows through darkness as a beacon.
    const pgStatic = this.add.graphics().setDepth(22).setPosition(px, py);
    pgStatic.fillStyle(0x1e1b4b, 0.2).fillCircle(0, 0, PORTAL_RADIUS);

    // Animated overlay: only the 2 moving elements are redrawn each frame.
    const pg = this.add.graphics().setDepth(22).setPosition(px, py);
    this._portalGfx = pg; // store reference to prevent GC and allow cleanup

    this.tweens.addCounter({
      from: 0, to: 360, duration: 3000, repeat: -1,
      onUpdate: tween => {
        // Guard: if the graphics object has been destroyed (scene restart), bail out.
        if (!pg?.scene) return;
        pg.clear();
        const a = Phaser.Math.DegToRad(tween.getValue());
        const unlocked = this._portalUnlocked();
        // Spinning mid-ring (colour shifts on unlock)
        pg.fillStyle(unlocked ? 0x7c3aed : 0x2e2b6e, 0.4)
          .fillCircle(Math.cos(a)*5, Math.sin(a)*5, PORTAL_RADIUS * 0.7);
        // Counter-rotating inner white dot
        pg.fillStyle(0xffffff, 0.8)
          .fillCircle(Math.cos(-a)*2, Math.sin(-a)*2, PORTAL_RADIUS * 0.3);
      }
    });
  }

  _portalUnlocked() {
    return this._enemies?.every(enemy => enemy.dead || !enemy.container.scene) ?? false;
  }

  // ── Enemy projectiles ─────────────────────────────────────────────────────

  _spawnEnemyArrow(originX, originY, angle, isBolt = false, enemyId = null) {
    const g = this.add.graphics().setDepth(9).setPosition(originX, originY);
    if (isBolt) {
      // Magic bolt: glowing orb
      g.fillStyle(0x7c3aed, 0.4); g.fillCircle(0, 0, 10);
      g.fillStyle(0xa855f7, 0.8); g.fillCircle(0, 0, 7);
      g.fillStyle(0xe9d5ff, 1);   g.fillCircle(0, 0, 4);
    } else {
      // Arrow: thin elongated shape pointing in travel direction
      g.fillStyle(0xfcd34d, 1); g.fillRect(-8, -2, 16, 4);
      g.fillStyle(0x92400e, 1); g.fillTriangle(8, -3, 14, 0, 8, 3);
      g.setRotation(angle);
    }
    const speed = isBolt ? 190 : ENEMY_ARROW_SPEED;
    this._enemyArrows.push({
      g,
      x: originX, y: originY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      damage: isBolt ? 20 : ENEMY_ARROW_DAMAGE,
      life: ENEMY_ARROW_LIFE,
      active: true,
      isBolt,
      enemyId, // for multiplayer ghost-arrow cleanup
    });
  }

  _bomberExplode(enemy) {
    const ex = enemy.container.x;
    const ey = enemy.container.y;
    // Visual explosion burst
    this._spawnPickupParticles(ex, ey, 0xf97316);
    this._spawnPickupParticles(ex, ey, 0xfbbf24);
    // Camera shake
    this.cameras.main.shake(350, 0.02);
    // Area damage to player
    if (Math.hypot(ex - this.player.x, ey - this.player.y) < BOMBER_EXPLODE_RADIUS) {
      this._playerTakeDamage(enemy.damage, enemy);
    }
    // Kill the bomber
    enemy.takeDamage(9999);
  }

  // ── Room special features ─────────────────────────────────────────────────

  _spawnShops() {
    this._shopNpcs = [];
    const allIds  = Array.from(this.itemRegistry.keys());
    for (const room of this.rooms) {
      if (room.type !== 'shop') continue;
      const nx = (room.cx + 0.5) * this._tileW;
      const ny = (room.cy + 0.5) * this._tileH;
      // Pick 3 random items for sale; price in gold
      const items = Array.from({ length: SHOP_ITEM_COUNT }, () => {
        const id  = allIds[this._randInt(0, allIds.length - 1)];
        const def = this.itemRegistry.get(id);
        return { id, def, goldCost: def ? Math.max(15, Math.floor((def.value || 40) * 0.8)) : 15 };
      });
      // NPC graphic — clickable hitbox
      const g = this.add.graphics().setDepth(6).setPosition(nx, ny);
      this._drawShopNpc(g);
      // Invisible click zone on top of the NPC
      const hitZone = this.add.zone(nx, ny, 64, 64)
        .setDepth(7)
        .setInteractive({ useHandCursor: true });
      hitZone.on('pointerdown', () => this._openShopUi(npcEntry));
      // Prompt text — always visible so player knows what it is
      const promptText = this.add.text(nx, ny - 54, '[click] Shop', {
        fontFamily: 'monospace', fontSize: '12px', color: '#fbbf24',
        stroke: '#000000', strokeThickness: 3,
      }).setOrigin(0.5).setDepth(32).setAlpha(1);
      const npcEntry = { x: nx, y: ny, items, g, hitZone, promptText };
      this._shopNpcs.push(npcEntry);
    }
  }

  _drawShopNpc(g) {
    g.clear();
    // Shadow
    g.fillStyle(0x000000, 0.28); g.fillEllipse(2, 30, 36, 12);
    // Legs
    g.fillStyle(0x78350f, 1); g.fillRect(-10, 10, 9, 20); g.fillRect(1, 10, 9, 20);
    // Apron (front)
    g.fillStyle(0xfef3c7, 1); g.fillRect(-10, -4, 20, 16);
    // Stocky body
    g.fillStyle(0x92400e, 1); g.fillRect(-13, -16, 26, 28);
    // Arms (holding something)
    g.fillStyle(0x92400e, 1); g.fillRect(-22, -14, 11, 18); g.fillRect(11, -14, 11, 18);
    // Bag of gold in left hand
    g.fillStyle(0xfbbf24, 1); g.fillCircle(-18, 6, 7);
    g.lineStyle(2, 0xca8a04, 1); g.strokeCircle(-18, 6, 7);
    g.fillStyle(0xfef08a, 0.8); g.fillCircle(-18, 6, 4);
    // Head (round, friendly)
    g.fillStyle(0xfde68a, 1); g.fillEllipse(0, -24, 22, 20);
    // Merchant cap (flat brim, not pointed)
    g.fillStyle(0x78350f, 1); g.fillRect(-14, -34, 28, 6); g.fillRect(-10, -40, 20, 8);
    g.fillStyle(0xca8a04, 1); g.fillRect(-14, -36, 28, 3);
    // Eyes (friendly, smiling)
    g.fillStyle(0x111111, 1); g.fillCircle(-5, -25, 2); g.fillCircle(5, -25, 2);
    // Smile
    g.lineStyle(2, 0x78350f, 1);
    g.strokeEllipse(0, -19, 10, 6);
    // Apron tie
    g.lineStyle(2, 0xca8a04, 1); g.lineBetween(-4, -4, -4, 12); g.lineBetween(4, -4, 4, 12);
  }

  _openShopUi(shop) {
    if (this._shopUiOpen) return;
    this._shopUiOpen = true;
    this._paused = true;
    this.physics.pause();

    // Re-roll items every time the shop is opened (filter spells for non-mages)
    const allIds = Array.from(this.itemRegistry.keys())
      .filter(id => this._worldState.canUseSpells || this.itemRegistry.get(id)?.type !== 'spell');
    shop.items = Array.from({ length: SHOP_ITEM_COUNT }, () => {
      const id  = allIds[this._randInt(0, allIds.length - 1)];
      const def = this.itemRegistry.get(id);
      return { id, def, goldCost: def ? Math.max(15, Math.floor((def.value || 40) * 0.8)) : 15 };
    });

    const { width, height } = this.scale;
    const cx = width / 2, cy = height / 2;
    const elements = [];

    const overlay = this.add.graphics().setDepth(500).setScrollFactor(0);
    overlay.fillStyle(0x000000, 0.82).fillRect(0, 0, width, height);
    elements.push(overlay);

    const title = this.add.text(cx, cy - 160, 'MERCHANT', {
      fontFamily: 'monospace', fontSize: '26px', color: '#fbbf24',
      stroke: '#000000', strokeThickness: 4,
    }).setOrigin(0.5).setDepth(501).setScrollFactor(0);
    elements.push(title);

    const sub = this.add.text(cx, cy - 128, 'Spend Gold to buy items', {
      fontFamily: 'monospace', fontSize: '13px', color: '#94a3b8',
    }).setOrigin(0.5).setDepth(501).setScrollFactor(0);
    elements.push(sub);

    const closeAll = () => {
      elements.forEach(e => e.destroy());
      this._shopUiOpen = false;
      this._paused = false;
      this.physics.resume();
    };

    shop.items.forEach((shopItem, idx) => {
      const iy = cy - 70 + idx * 68;
      const def = shopItem.def;
      if (!def) return;
      const rarityCol = { common: '#9ca3af', uncommon: '#22c55e', rare: '#3b82f6', epic: '#a855f7', legendary: '#f59e0b' }[def.rarity] || '#9ca3af';
      const bg = this.add.graphics().setDepth(501).setScrollFactor(0);
      const drawBg = (hover) => {
        bg.clear();
        bg.fillStyle(hover ? 0x1e293b : 0x0f172a, 0.95).fillRoundedRect(cx - 200, iy - 24, 400, 52, 8);
        bg.lineStyle(2, hover ? 0x3b82f6 : 0x334155, 1).strokeRoundedRect(cx - 200, iy - 24, 400, 52, 8);
      };
      drawBg(false);
      elements.push(bg);

      const nameText = this.add.text(cx - 180, iy - 10, def.name, {
        fontFamily: 'monospace', fontSize: '14px', color: rarityCol, stroke: '#000', strokeThickness: 2,
      }).setDepth(502).setScrollFactor(0);
      elements.push(nameText);

      const descText = this.add.text(cx - 180, iy + 8, def.description?.slice(0, 45) ?? '', {
        fontFamily: 'monospace', fontSize: '10px', color: '#64748b',
      }).setDepth(502).setScrollFactor(0);
      elements.push(descText);

      const priceText = this.add.text(cx + 190, iy, `${shopItem.goldCost} gold`, {
        fontFamily: 'monospace', fontSize: '13px', color: '#fbbf24',
      }).setOrigin(1, 0.5).setDepth(502).setScrollFactor(0);
      elements.push(priceText);

      // Invisible hit zone
      const hitZone = this.add.zone(cx, iy, 400, 52).setDepth(503).setScrollFactor(0).setInteractive();
      elements.push(hitZone);
      hitZone.on('pointerover', () => drawBg(true));
      hitZone.on('pointerout',  () => drawBg(false));
      hitZone.on('pointerdown', () => {
        if (this.player.gold < shopItem.goldCost) {
          this._showToast('Not enough gold!');
          return;
        }
        const added = this.player.addItem(def, 1);
        if (!added) { this._showToast('Inventory full!'); return; }
        this.player.gold -= shopItem.goldCost;
        // Also place in an empty hotbar slot so it's immediately visible
        const emptySlot = this.player.hotbar.findIndex(s => s === null);
        if (emptySlot !== -1) this.player.setHotbar(emptySlot, def.id);
        this._refreshHotbar();
        this._updateHud();
        this._saveGame();
        this._logEvent(`Bought ${def.name} for ${shopItem.goldCost} gold`);
        this._showToast(`Bought: ${def.name}!`);
        closeAll();
      });
    });

    const closeBtn = this.add.text(cx, cy + 140, '[ESC or click] Close', {
      fontFamily: 'monospace', fontSize: '12px', color: '#64748b',
    }).setOrigin(0.5).setDepth(502).setScrollFactor(0).setInteractive();
    elements.push(closeBtn);
    closeBtn.on('pointerdown', closeAll);

    // Close on ESC
    const escHandler = this.input.keyboard.once('keydown-ESC', closeAll);
    elements.push({ destroy: () => { /* escHandler cleanup handled by once */ } });
  }

  _drawTreasureRoomMarker(room) {
    const g = this.add.graphics().setDepth(1);
    const tileW = this._tileW, tileH = this._tileH;
    // Gold-tinted overlay on floor tiles
    for (let row = room.y; row < room.y + room.h; row++) {
      for (let col = room.x; col < room.x + room.w; col++) {
        g.fillStyle(0xfbbf24, 0.07).fillRect(col * tileW, row * tileH, tileW - 1, tileH - 1);
      }
    }
    // Corner gems
    const corners = [
      [room.x, room.y], [room.x + room.w - 1, room.y],
      [room.x, room.y + room.h - 1], [room.x + room.w - 1, room.y + room.h - 1],
    ];
    for (const [c, r] of corners) {
      const wx = (c + 0.5) * tileW, wy = (r + 0.5) * tileH;
      g.fillStyle(0xfbbf24, 0.6).fillRect(wx - 4, wy - 4, 8, 8);
      g.fillStyle(0xfef08a, 0.8).fillRect(wx - 2, wy - 2, 4, 4);
    }
  }

  // ── Optional Boss Lair (level 7+) ──────────────────────────────────────────

  _spawnOptionalBossLair() {
    this._optionalBosses = [];
    this._lockedChests   = [];
    this._hasBossKey     = false;
    this._bossKeyPickup  = null;

    // Pick a room that isn't spawn or portal for the boss lair
    const candidates = this.rooms.filter(r => r.type !== 'spawn' && r.type !== 'portal');
    if (candidates.length === 0) return;
    const lairRoom = candidates[Math.floor(this._randFloat() * candidates.length)];

    // Dark-red floor tint for the lair
    const g = this.add.graphics().setDepth(1);
    for (let row = lairRoom.y; row < lairRoom.y + lairRoom.h; row++) {
      for (let col = lairRoom.x; col < lairRoom.x + lairRoom.w; col++) {
        g.fillStyle(0x7c3aed, 0.12).fillRect(col * this._tileW, row * this._tileH, this._tileW - 1, this._tileH - 1);
      }
    }

    // Spawn optional boss
    const bx = (lairRoom.cx + 0.5) * this._tileW;
    const by = (lairRoom.cy + 0.5) * this._tileH;
    const boss = new Enemy(this, bx, by, 'boss');
    boss.saveId = `floor:${this.dungeonLevel}:optboss`;
    boss.maxHp  = Math.floor(320 * (1 + (this.dungeonLevel - 7) * 0.18));
    boss.hp     = boss.maxHp;
    boss.damage = Math.floor(22  * (1 + (this.dungeonLevel - 7) * 0.12));
    boss._onDrop = (id, bx2, by2) => { const def = this.itemRegistry.get(id); if (def) this._spawnWorldItem(bx2, by2, def); };
    this.physics.add.collider(boss.container, this._wallGroup);
    this._optionalBosses.push(boss);

    // Skull marker above boss spawn
    const label = this.add.text(bx, by - 80, '[OPTIONAL BOSS]', {
      fontFamily: 'monospace', fontSize: '11px', color: '#a855f7',
      stroke: '#000000', strokeThickness: 3,
    }).setOrigin(0.5).setDepth(30);
    this.tweens.add({ targets: label, alpha: 0.3, duration: 900, yoyo: true, repeat: -1 });

    // Locked chest — placed offset from the boss so it's reachable after the fight
    const lcx = bx + (lairRoom.w > 3 ? this._tileW * 1.5 : 0);
    const lcy = by + this._tileH;
    this._spawnLockedChest(lcx, lcy);

    this._logEvent(`Optional boss lair on floor ${this.dungeonLevel}!`);
  }

  _spawnLockedChest(x, y) {
    const g = this.add.graphics().setDepth(5).setPosition(x, y);
    this._drawLockedChest(g, false);

    const promptText = this.add.text(x, y - 52, '[F] Locked - need Boss Key', {
      fontFamily: 'monospace', fontSize: '11px', color: '#a855f7',
      stroke: '#000000', strokeThickness: 3,
    }).setOrigin(0.5).setDepth(32).setAlpha(0);

    const lc = { x, y, g, promptText, opened: false };
    this._lockedChests.push(lc);
  }

  _drawLockedChest(g, opened) {
    g.clear();
    if (!opened) {
      // Dark purple chest with glowing lock
      g.fillStyle(0x000000, 0.3); g.fillEllipse(2, 28, 46, 12);
      g.fillStyle(0x4c1d95, 1);   g.fillRect(-22, 2, 44, 20);
      g.fillStyle(0x6d28d9, 1);   g.fillRect(-22, -16, 44, 20);
      g.lineStyle(2, 0xa855f7, 1); g.strokeRect(-22, -16, 44, 38);
      g.lineStyle(1, 0xa855f7, 0.5); g.lineBetween(-22, 2, 22, 2);
      for (const [cx, cy] of [[-18, -14], [16, -14], [-18, 18], [16, 18]]) {
        g.fillStyle(0xa855f7, 1); g.fillCircle(cx, cy, 3);
      }
      // Glowing lock
      g.fillStyle(0xa855f7, 1);   g.fillRect(-6, -5, 12, 11);
      g.lineStyle(3, 0xe9d5ff, 1); g.strokeArc(0, -5, 5, Math.PI, 0, false);
      g.fillStyle(0x0a0010, 1);   g.fillRect(-2, -2, 4, 6);
    } else {
      g.fillStyle(0x1a0830, 1); g.fillRect(-22, -2, 44, 24);
      g.fillStyle(0x0a0010, 1); g.fillRect(-17, 0, 34, 16);
      g.fillStyle(0x2e1065, 1); g.fillRect(-22, -20, 44, 12);
      g.lineStyle(2, 0x4c1d95, 1); g.strokeRect(-22, -20, 44, 46);
    }
  }

  _dropBossKey(x, y) {
    const g = this.add.graphics().setDepth(6).setPosition(x, y);
    // Key visual
    g.fillStyle(0xfbbf24, 1); g.fillCircle(0, 0, 8);
    g.fillStyle(0xfef08a, 0.8); g.fillCircle(0, 0, 5);
    g.fillStyle(0xfbbf24, 1); g.fillRect(4, -3, 14, 6);
    g.fillRect(14, -3, 4, 8); g.fillRect(10, -3, 4, 8);
    g.lineStyle(2, 0xf59e0b, 1); g.strokeCircle(0, 0, 8);
    const label = this.add.text(x, y - 22, '[BOSS KEY]', {
      fontFamily: 'monospace', fontSize: '11px', color: '#fbbf24',
      stroke: '#000000', strokeThickness: 3,
    }).setOrigin(0.5).setDepth(32);
    this.tweens.add({ targets: [g, label], y: `-=4`, duration: 600, yoyo: true, repeat: -1 });
    this._bossKeyPickup = { x, y, g, label };
  }

  _tryOpenLockedChest(lc) {
    if (!this._hasBossKey) {
      this._showToast('Need Boss Key to open this!');
      return;
    }
    this._hasBossKey = false;
    lc.opened = true;
    lc.promptText?.setAlpha(0);
    this._drawLockedChest(lc.g, true);

    // Give 3 high-quality random items.
    // Chest loot can include spells for every class; only floor pickups stay mage-locked.
    const allIds   = Array.from(this.itemRegistry.keys())
      .filter(id => this.itemRegistry.get(id)?.type !== 'spell');
    const spellIds = Array.from(this.itemRegistry.keys())
      .filter(id => id.startsWith('spell_') && !this._playerOwnsItem(id));
    const lootPool = spellIds.length > 0 ? [...allIds, ...spellIds, ...spellIds] : allIds;
    let given = 0;
    for (let attempt = 0; attempt < 20 && given < 3; attempt++) {
      const id  = lootPool[this._randInt(0, lootPool.length - 1)];
      const def = this.itemRegistry.get(id);
      if (!def) continue;
      if (this.player.addItem(def, 1)) {
        const slot = this.player.hotbar.findIndex(s => s === null);
        if (slot !== -1) this.player.setHotbar(slot, def.id);
        this._spawnPickupParticles(lc.x, lc.y, 0xa855f7);
        this._logEvent(`Locked chest: found ${def.name}`);
        given++;
      }
    }
    this._refreshHotbar();
    this._updateHud();
    this._saveGame();
    this._showToast(`Treasure! Found ${given} items!`);
    this.cameras.main.flash(200, 168, 85, 247, true);
  }

  _nextLevel() {
    if (this._levelingUp || this._gameOver) return;
    this._levelingUp = true; // Block input
    this._checkAchievements();
    this._saveGame();
    if (this._mpData?.isHost) multiplayer.sendEvent('next_level', {});
    audioManager.playSfx('portal');
    this._logEvent(`Descending to floor ${this.dungeonLevel + 1}`);
    this.cameras.main.fadeOut(800, 0, 0, 0);
    this.cameras.main.once('camerafadeoutcomplete', () => {
      const nextPlayerState = this._serializePlayerState();
      nextPlayerState.x = null;
      nextPlayerState.y = null;
      this.scene.restart({
        isNewGame: false,
        level: this.dungeonLevel + 1,
        seed: this.seed,
        playerState: nextPlayerState,
        worldState: this._serializeWorldState(),
        mp: this._mpData,  // preserve multiplayer session across floors
      });
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Multiplayer
  // ─────────────────────────────────────────────────────────────────────────────
  _setupMultiplayer() {
    const COLORS = [0x7c3aed, 0xe67e22, 0x2ecc71, 0xe74c3c];
    this._remoteGfx = new Map(); // playerId → { g, nameText }

    multiplayer.on('player_update', ({ playerId, state }) => {
      let entry = this._remoteGfx.get(playerId);
      if (!entry) {
        const g = this.add.graphics().setDepth(22);
        const hpBarGfx = this.add.graphics().setDepth(23);
        const nameText = this.add.text(0, -40, `P${(state.playerIndex ?? 1) + 1}`, {
          fontFamily: 'monospace', fontSize: '9px', color: '#ffffff',
          stroke: '#000000', strokeThickness: 2,
        }).setOrigin(0.5).setDepth(24);
        // snap to first known position
        g.setPosition(state.x, state.y);
        hpBarGfx.setPosition(state.x, state.y);
        nameText.setPosition(state.x, state.y - 40);
        // use undefined so the first update always triggers a draw (null === null would skip it)
        entry = { pid: playerId, g, hpBarGfx, nameText, x: state.x, y: state.y, hp: state.hp, maxHp: state.maxHp, color: COLORS[state.playerIndex ?? 1], prevHead: undefined, prevChest: undefined, prevMain: undefined };
        this._remoteGfx.set(playerId, entry);
      }
      // store target; interpolation happens in update()
      entry.targetX = state.x;
      entry.targetY = state.y;
      entry.hp    = state.hp ?? entry.hp;
      entry.maxHp = state.maxHp ?? entry.maxHp;
      // redraw only when equipment changes
      const changed = entry.prevHead !== state.head || entry.prevChest !== state.chest || entry.prevMain !== state.main;
      if (changed) {
        entry.prevHead  = state.head;
        entry.prevChest = state.chest;
        entry.prevMain  = state.main;
        this._drawRemotePlayer(entry, state);
      }
      // Update HP bar
      if (entry.hpBarGfx && Number.isFinite(entry.hp) && Number.isFinite(entry.maxHp) && entry.maxHp > 0) {
        const ratio = Math.max(0, entry.hp / entry.maxHp);
        const col = ratio > 0.5 ? 0x16a34a : ratio > 0.25 ? 0xca8a04 : 0xdc2626;
        entry.hpBarGfx.clear()
          .fillStyle(0x0f172a, 0.8).fillRect(-20, 24, 40, 5)
          .fillStyle(col, 1).fillRect(-20, 24, Math.max(0, 40 * ratio), 5);
      }
    });

    multiplayer.on('player_left', ({ playerId }) => {
      const e = this._remoteGfx.get(playerId);
      if (e) { e.g.destroy(); e.hpBarGfx?.destroy(); e.nameText.destroy(); this._remoteGfx.delete(playerId); }
    });

    multiplayer.on('game_event', ({ playerId, event, data }) => {
      if (event === 'next_level' && !this._mpData.isHost) this._nextLevel();
      if (event === 'enemy_killed') this._applyRemoteEnemyKill(data?.id);
      if (event === 'enemy_sync' && !this._mpData.isHost) this._applyEnemySync(data?.enemies);
      if (event === 'boss_sync'  && !this._mpData.isHost) this._applyBossSync(data?.bosses);
      if (event === 'enemy_arrow' && !this._mpData.isHost)
        this._spawnEnemyArrow(data.x, data.y, data.angle, data.isBolt);
      if (event === 'chat' && data?.text)
        this._showChatBubble(data.text, playerId);
      if (event === 'enemy_dead') {
        // Deactivate arrows from this enemy so they don't become ghosts
        for (const a of (this._enemyArrows || [])) {
          if (a.enemyId === data.id) a.active = false;
        }
      }
      if (event === 'chest_opened') {
        // A remote player opened this chest — apply visual-only state so we
        // don't grant a duplicate item but the world stays consistent.
        const c = this._chests?.find(ch => ch.saveId === data?.chestId);
        if (c && !c.opened) { c.markOpened(); }
      }
      if (event === 'revive_player' && data?.targetPid === multiplayer.playerId) {
        // This player is being revived by a teammate
        const reviveHp = data.hp || 30;
        this.player.hp = Math.min(this.player.effectiveMaxHp, this.player.hp + reviveHp);
        this._updateHud();
        this._saveGame();
        this._showToast(`Revived! +${reviveHp} HP`);
        audioManager.playSfx('levelup');
      }
    });

    // HOST: broadcast enemy positions every 33 ms (~30fps sync)
    if (this._mpData.isHost) {
      this._enemySyncInterval = setInterval(() => {
        const enemies = this._enemies
          .filter(e => !e.dead)
          .map((e, i) => [i, Math.round(e.container.x), Math.round(e.container.y), e.hp]);
        multiplayer.sendEvent('enemy_sync', { enemies });
        if (this._optionalBosses?.length) {
          const bosses = this._optionalBosses
            .filter(b => !b.dead)
            .map((b, i) => [i, Math.round(b.container.x), Math.round(b.container.y), b.hp]);
          multiplayer.sendEvent('boss_sync', { bosses });
        }
      }, 33);
    }

    // Send own position + equipment + HP state at 30/sec
    multiplayer.startSendingUpdates(() => ({
      x: Math.round(this._playerContainer.x),
      y: Math.round(this._playerContainer.y),
      playerIndex: this._mpData.playerIndex,
      head:  this.player.equipment.head?.id  ?? null,
      chest: this.player.equipment.chest?.id ?? null,
      main:  this.player.equipment.main_hand?.id ?? null,
      hp:    this.player.hp,
      maxHp: this.player.effectiveMaxHp,
    }));
  }

  // Draw a remote player's avatar with their current equipment
  _drawRemotePlayer(entry, state) {
    const g = entry.g;
    const color = entry.color;
    g.clear();
    // shadow
    g.fillStyle(0x000000, 0.3); g.fillEllipse(0, 14, 28, 9);
    // legs
    g.fillStyle(color, 1); g.fillRect(-10, -14, 20, 28);
    // helmet (head slot)
    const hasHelmet = state.head && state.head.includes('helmet');
    if (hasHelmet) {
      g.fillStyle(0x94a3b8, 1); g.fillRect(-11, -38, 22, 14);
    }
    // head
    g.fillStyle(0xfbbf24, 1); g.fillCircle(0, -28, 11);
    // eyes
    g.fillStyle(0x1e1b4b, 1); g.fillCircle(-4, -28, 2.5); g.fillCircle(4, -28, 2.5);
    // chest armor overlay
    if (state.chest) {
      const chestCol = state.chest.includes('warden') ? 0x7c3aed : 0x64748b;
      g.fillStyle(chestCol, 0.85); g.fillRect(-11, -16, 22, 18);
    }
    // weapon in hand
    if (state.main) {
      const isSpell = state.main.startsWith('spell_');
      const isSword = state.main.includes('sword') || state.main.includes('pickaxe');
      if (isSpell) {
        g.fillStyle(0xa855f7, 0.8); g.fillCircle(13, -14, 5);
        g.fillStyle(0xe9d5ff, 1);   g.fillCircle(13, -14, 2.5);
      } else if (isSword) {
        g.lineStyle(3, 0xd1d5db, 1); g.lineBetween(10, -6, 22, -22);
        g.lineStyle(2, 0x9ca3af, 1); g.lineBetween(8, -16, 16, -8);
      }
    }
  }

  // Apply enemy position/HP snapshot received from host
  _applyEnemySync(snapshots) {
    if (!snapshots) return;
    // Format: [index, x, y, hp]
    for (const [idx, x, y, hp] of snapshots) {
      const enemy = this._enemies[idx];
      if (!enemy || enemy.dead) continue;
      enemy._syncX = x;
      enemy._syncY = y;
      enemy.hp = hp;
    }
  }

  _applyBossSync(snapshots) {
    if (!snapshots || !this._optionalBosses) return;
    for (const [idx, x, y, hp] of snapshots) {
      const boss = this._optionalBosses[idx];
      if (!boss || boss.dead) continue;
      boss._syncX = x;
      boss._syncY = y;
      boss.hp = hp;
    }
  }

  // Kill a remote enemy without awarding XP/gold/loot
  _applyRemoteEnemyKill(id) {
    if (!id) return;
    const enemy = [...this._enemies, ...(this._optionalBosses || [])]
      .find(e => e.saveId === id);
    if (!enemy || enemy.dead) return;
    enemy._mpKilled = true;
    enemy.takeDamage(99999);
  }

  _randFloat() {
    return this._rng ? this._rng() : Math.random();
  }

  _randInt(min, max) {
    return min + Math.floor(this._randFloat() * (max - min + 1));
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Core Systems (Player, Physics, Lighting)
  // ─────────────────────────────────────────────────────────────────────────────
  _hotbarTotalH() { return SLOT_SIZE + HOTBAR_PAD * 2 + 24; }

  // Enemies get progressively stronger each floor
  _floorScale(level) {
    return 1 + (level - 1) * 0.18;
  }

  _buildPlayerSprite() {
    const c = this.add.container(this.player.x, this.player.y).setDepth(10);
    const classId = this._worldState?.classId;
    const body = this.add.graphics().setName('body');

    // Shadow ellipse — same for all classes
    body.fillStyle(0x000000, 0.35).fillEllipse(0, 30, 36, 12);

    if (classId === 'warrior') {
      // Blue steel warrior
      body.fillStyle(0x1e40af, 1).fillRect(-10, 12, 8, 18).fillRect(2, 12, 8, 18); // legs
      body.fillStyle(0x1d4ed8, 1).fillRect(-13, -14, 26, 28);                       // torso
      body.fillStyle(0x1e3a5f, 1).fillRect(-13, 6, 26, 5);                          // belt
      body.fillStyle(0x3b82f6, 1).fillRect(-17, -14, 8, 8).fillRect(9, -14, 8, 8); // pauldrons
    } else if (classId === 'rogue') {
      // Dark hunter green rogue
      body.fillStyle(0x047857, 1).fillRect(-10, 12, 8, 18).fillRect(2, 12, 8, 18); // legs
      body.fillStyle(0x065f46, 1).fillRect(-13, -14, 26, 28);                       // torso
      body.fillStyle(0x064e3b, 1).fillRect(-13, 6, 26, 5);                          // belt
      body.fillStyle(0x10b981, 1).fillRect(-17, -14, 8, 8).fillRect(9, -14, 8, 8); // pauldrons
    } else {
      // Default / mage — original purple
      body.fillStyle(0x3b1473, 1).fillRect(-10, 12, 8, 18).fillRect(2, 12, 8, 18);
      body.fillStyle(0x5b21b6, 1).fillRect(-13, -14, 26, 28);
      body.fillStyle(0x2e1065, 1).fillRect(-13, 6, 26, 5);
      body.fillStyle(0x7c3aed, 1).fillRect(-17, -14, 8, 8).fillRect(9, -14, 8, 8);
    }

    // Head — shared across classes
    body.fillStyle(0xfbbf24, 1).fillCircle(0, -26, 14);
    body.fillStyle(0x1e1b4b, 1).fillCircle(-5, -26, 3).fillCircle(5, -26, 3);

    const armor = this.add.graphics().setName('armor');
    const helmet = this.add.graphics().setName('helmet');
    const weapon = this.add.graphics().setName('weapon');
    const rings = this.add.graphics().setName('rings');
    this._drawArmorGfx(armor, helmet);
    this._drawWeaponGfx(weapon);
    this._drawRingGfx(rings);

    // Class-specific visual overlays
    const extraGfx = [];
    if (classId === 'warrior') {
      const shield = this.add.graphics().setName('shield');
      shield.fillStyle(0x1e40af, 1).fillRoundedRect(-24, -10, 10, 22, 3);
      shield.lineStyle(2, 0x60a5fa, 0.9).strokeRoundedRect(-24, -10, 10, 22, 3);
      shield.fillStyle(0x60a5fa, 0.5).fillRect(-21, -4, 4, 8);
      extraGfx.push(shield);
    } else if (classId === 'mage') {
      const staffOrb = this.add.graphics().setName('staffOrb');
      staffOrb.fillStyle(0xa78bfa, 0.85).fillCircle(18, -24, 5);
      staffOrb.fillStyle(0xffffff, 0.6).fillCircle(16, -26, 2);
      staffOrb.lineStyle(1, 0xc4b5fd, 0.4);
      staffOrb.strokeCircle(18, -24, 8);
      extraGfx.push(staffOrb);
    } else if (classId === 'rogue') {
      const dagger = this.add.graphics().setName('dagger');
      dagger.fillStyle(0xd1d5db, 0.8).fillRect(11, -6, 3, 14);
      dagger.fillStyle(0x6b7280, 1).fillRect(10, -10, 5, 5);
      extraGfx.push(dagger);
    }

    c.add([body, armor, helmet, rings, weapon, ...extraGfx]);
    return c;
  }

  _attachPhysics() {
    this.physics.add.existing(this._playerContainer);
    this._physBody = this._playerContainer.body;
    this._physBody.setDrag(PLAYER_DRAG, PLAYER_DRAG).setMaxVelocity(this.player.speed, this.player.speed).setSize(22, 28).setOffset(-11, -10);
    this.physics.add.collider(this._playerContainer, this._wallGroup);
  }

  _drawWeaponGfx(g) {
    g.clear();
    const item = this.player.equipment.main_hand;
    if (!item) return;
    if (item.type === 'weapon') {
      const col   = parseInt((item.particle_color || '#d1d5db').replace('#', ''), 16);
      const guard = item.rarity === 'epic'   ? 0xc084fc
                  : item.rarity === 'rare'   ? 0x60a5fa
                  : item.rarity === 'uncommon' ? 0x94a3b8
                  : 0xca8a04;
      if (item.id.startsWith('dagger_')) {
        // Short thin blade
        g.fillStyle(col, 1).fillRect(19, -18, 4, 24);
        g.fillStyle(guard, 1).fillRect(13, 6, 14, 4);
      } else if (item.id.startsWith('axe_')) {
        // Axe: handle + wide head
        g.fillStyle(0x92400e, 1).fillRect(18, -28, 4, 42);
        g.fillStyle(col, 1).fillTriangle(10, -28, 26, -22, 10, -6);
        g.fillStyle(guard, 1).fillRect(12, -8, 16, 4);
      } else {
        // Standard sword
        g.fillStyle(col, 1).fillRect(16, -32, 5, 42);
        g.fillStyle(guard, 1).fillRect(9, -12, 18, 6);
      }
    } else if (item.type === 'tool') {
      g.fillStyle(0x92400e, 1).fillRect(15, -10, 5, 38);
      g.fillStyle(0x64748b, 1).fillRect(6, -28, 24, 10);
    }
  }

  _redrawWeapon() {
    const w = this._playerContainer.getByName('weapon');
    if (w) this._drawWeaponGfx(w);
    const armor = this._playerContainer.getByName('armor');
    const helmet = this._playerContainer.getByName('helmet');
    if (armor && helmet) this._drawArmorGfx(armor, helmet);
    const rings = this._playerContainer.getByName('rings');
    if (rings) this._drawRingGfx(rings);
  }

  _drawRingGfx(rings) {
    rings.clear();
    const passives = this._worldState?.absorbedPassives;
    if (!passives || passives.length === 0) return;
    // Draw small colored dots along the player's neck/collar as ring indicators
    const RING_COLORS = [0x86efac, 0xfca5a5, 0x7dd3fc, 0xc4b5fd, 0xfde047];
    const count = Math.min(passives.length, 5);
    const spacing = 7;
    const startX = -((count - 1) * spacing) / 2;
    for (let i = 0; i < count; i++) {
      const col = RING_COLORS[i % RING_COLORS.length];
      rings.fillStyle(col, 0.9).fillCircle(startX + i * spacing, -6, 3);
      rings.lineStyle(1, 0xffffff, 0.5).strokeCircle(startX + i * spacing, -6, 3);
    }
  }

  _drawArmorGfx(armor, helmet) {
    armor.clear();
    helmet.clear();
    if (this.player.equipment.chest) {
      const RARITY_CHEST_COLORS = { common: 0x78716c, uncommon: 0x6ee7b7, rare: 0x60a5fa, epic: 0xa855f7, legendary: 0xf59e0b };
      const chestCol = RARITY_CHEST_COLORS[this.player.equipment.chest.rarity] ?? 0x8b5cf6;
      armor.fillStyle(chestCol, 0.9).fillRect(-14, -8, 28, 18);
      armor.lineStyle(2, 0xe9d5ff, 0.45).strokeRect(-14, -8, 28, 18);
    }
    if (this.player.equipment.head) {
      const RARITY_HELM_COLORS = { common: 0x9ca3af, uncommon: 0x4ade80, rare: 0x60a5fa, epic: 0xa855f7, legendary: 0xf59e0b };
      const col = RARITY_HELM_COLORS[this.player.equipment.head.rarity] ?? 0x9ca3af;
      helmet.fillStyle(col, 0.95).fillRect(-12, -38, 24, 10);
      helmet.fillStyle(0x1f2937, 0.7).fillRect(-10, -31, 20, 4);
    }
  }

  _buildTorchTexture(radius) {
    const key = '__torch__';
    // Reuse existing texture — radius is constant (TORCH_RADIUS never changes at
    // runtime), and removing a canvas texture that may still be referenced by the
    // active _fogRT or _darknessRT can crash WebGL on scene restart (floor 3+).
    if (this.textures.exists(key)) return key;
    const tex = this.textures.createCanvas(key, radius * 2, radius * 2);
    const ctx = tex.getContext();
    const grad = ctx.createRadialGradient(radius, radius, 0, radius, radius, radius);
    grad.addColorStop(0, 'rgba(255,255,255,1.00)');
    grad.addColorStop(0.5, 'rgba(255,255,255,0.95)');
    grad.addColorStop(0.8, 'rgba(255,255,255,0.3)');
    grad.addColorStop(1, 'rgba(255,255,255,0.00)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, radius * 2, radius * 2);
    tex.refresh();
    return key;
  }

  _updateTorch(delta) {
    this._torchUpdateAccum = (this._torchUpdateAccum || 0) + delta;
    if (this._torchUpdateAccum < 33) return;
    this._torchUpdateAccum = 0;

    if (!this._useDarkness) {
      this._torchGlow.clear();
      this._darknessRT.clear();
      return;
    }
    this._flickerTime += delta;
    const px = this._playerContainer.x, py = this._playerContainer.y;

    // Sine wave flicker
    const flicker = Math.sin(this._flickerTime * 0.005) * 6 + Math.sin(this._flickerTime * 0.012) * 3;
    const currentRad = TORCH_RADIUS + flicker;

    this._torchGlow.clear()
      .fillStyle(0xff8c00, 0.07).fillCircle(px, py, currentRad * 1.15)
      .fillStyle(0xff7700, 0.04).fillCircle(px, py, currentRad * 0.6);

    // Darkness RT must be rebuilt every frame — it tracks the camera and flickers.
    this._darknessRT.clear().fill(0x000000, DARKNESS_ALPHA);

    // Darkness RT is screen-space (scrollFactor 0) — convert world coords to screen
    const camScrollX = this.cameras.main.scrollX;
    const camScrollY = this.cameras.main.scrollY;
    const screenPx = px - camScrollX;
    const screenPy = py - camScrollY;
    this._darknessRT.erase(this._torchTexKey, screenPx - TORCH_RADIUS, screenPy - TORCH_RADIUS);

    // Fog RT is null (disabled) — darkness RT alone handles visibility.
    // If a fog RT is ever re-enabled, this block will punch persistent explored holes.
    if (this._fogRT) {
      if (!this._lastFogPos) this._lastFogPos = { x: -9999, y: -9999 };
      if (Math.hypot(px - this._lastFogPos.x, py - this._lastFogPos.y) > 10) {
        this._fogRT.erase(
          this._torchTexKey,
          (px - TORCH_RADIUS) * this._fogScaleX,
          (py - TORCH_RADIUS) * this._fogScaleY
        );
        this._lastFogPos.x = px;
        this._lastFogPos.y = py;
      }
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // UI & Interaction
  // ─────────────────────────────────────────────────────────────────────────────
  _tryOpenNearbyChest() {
    const px = this.player.x, py = this.player.y;
    const chest = this._chests.find(c => !c.opened && c.isNearPlayer(px, py));
    if (!chest) return;
    const previewItem = chest.peekLoot(this.itemRegistry);
    if (this._isDuplicatePickup(previewItem)) {
      const msg = this._hasBetterItemFor(previewItem) ? 'Already have better gear' : `Already carrying ${previewItem.name}`;
      this._showToast(msg);
      audioManager.playSfx('full');
      return;
    }
    const itemDef = chest.tryOpen(this.player, this.itemRegistry);
    if (!itemDef) { this._showToast('Inventory full!'); audioManager.playSfx('full'); return; }

    // Notify other players so they see the chest as opened and the server can
    // deduplicate simultaneous open attempts (race condition guard).
    if (this._mpData) {
      multiplayer.sendEvent('chest_opened', { chestId: chest.saveId });
    }

    this.player.gold += this._randInt(4, 12);
    if (chest.saveId && !this._worldState.openedChests.includes(chest.saveId)) this._worldState.openedChests.push(chest.saveId);
    this._spawnPickupParticles(chest.x, chest.y, RARITY_COLOR[itemDef.rarity] || RARITY_COLOR.common);
    audioManager.playSfx('chest');

    // Passive items (rings, relics) are always absorbed instantly — never linger in inventory/hotbar
    if (itemDef.type === 'passive') {
      this._applyPassiveItem(itemDef);
      this._updateHud();
      this._saveGame();
      this._logEvent(`Absorbed ${itemDef.name} from chest`);
      this._showToast(`Absorbed: ${itemDef.name}!`);
      return;
    }

    const emptyHotbar = this.player.hotbar.findIndex(s => s === null);
    if (emptyHotbar !== -1) this.player.setHotbar(emptyHotbar, itemDef.id);
    this._playLootReveal(chest.x, chest.y, itemDef, emptyHotbar !== -1 ? emptyHotbar : this.activeSlot);
    this._refreshHotbar();
    this._updateHud();
    this._saveGame();
    this._logEvent(`You found a ${itemDef.rarity} ${itemDef.name}`);
    this._showToast(`Found: ${itemDef.name}!`);
  }

  _playerOwnsItem(itemId) {
    if (this.player.inventory.some(slot => slot.item.id === itemId)) return true;
    return Object.values(this.player.equipment).some(item => item?.id === itemId);
  }

  _playerHasSpell(itemId) {
    return this._playerOwnsItem(itemId) || this.player.hotbar.includes(itemId);
  }

  _hasBetterItemFor(itemDef) {
    if (!itemDef?.slot) return false;
    const newScore = this._itemScore(itemDef);
    // Only compare items of the same type — a sword must NOT block a pickaxe pickup
    const equipped = this.player.equipment[itemDef.slot];
    if (equipped && equipped.type === itemDef.type && this._itemScore(equipped) >= newScore) return true;
    return this.player.inventory.some(
      s => s.item.slot === itemDef.slot && s.item.type === itemDef.type && this._itemScore(s.item) >= newScore
    );
  }

  _itemScore(itemDef) {
    const s = itemDef.stats || {};
    // Weapons/tools: score by attack; armor: score by defense; fallback to value
    if (itemDef.slot === 'main_hand') return (s.attack ?? 0) + (s.mining_power ?? 0) * 0.3;
    if (itemDef.slot === 'head' || itemDef.slot === 'chest') return (s.defense ?? 0) + (s.max_hp ?? 0) * 0.2;
    return itemDef.value ?? 0;
  }

  _isDuplicatePickup(itemDef) {
    if (!itemDef) return false;
    if (itemDef.stackable) {
      if (itemDef.max_stack) {
        const slot = this.player.inventory.find(s => s.item.id === itemDef.id);
        return slot ? slot.quantity >= itemDef.max_stack : false;
      }
      return false;
    }
    return this._playerOwnsItem(itemDef.id);
  }

  _clearActiveHotbarSlot() {
    if (this._levelIntroActive || this._paused || this._gameOver || this._levelingUp) return;
    if (!this.player.hotbar[this.activeSlot]) return;
    this.player.hotbar[this.activeSlot] = null;
    this._refreshHotbar();
    this._hideTooltip();
    this._saveGame();
    this._showToast(`Cleared slot ${this.activeSlot + 1}`);
  }

  _handleFKey() {
    const px = this.player.x;
    const py = this.player.y;
    // Locked chest (boss key required)
    const lockedChest = this._lockedChests?.find(lc => !lc.opened && Math.hypot(lc.x - px, lc.y - py) < 72);
    if (lockedChest) {
      this._tryOpenLockedChest(lockedChest);
      return;
    }
    const chestNearby = this._chests.find(c => !c.opened && c.isNearPlayer(px, py));
    if (chestNearby) {
      this._tryOpenNearbyChest();
      return;
    }
    this._castFireball();
  }

  _handleShopKey() {
    const px = this.player.x;
    const py = this.player.y;
    const shopNearby = this._shopNpcs?.find(s => Math.hypot(s.x - px, s.y - py) < 200);
    if (shopNearby) this._openShopUi(shopNearby);
  }

  _castFireball() {
    if (this._fireballCooldown > 0) return;
    this._fireballCooldown = FIREBALL_COOLDOWN;
    const ptr = this.input.activePointer;
    const targetX = ptr.worldX ?? ptr.x;
    const targetY = ptr.worldY ?? ptr.y;
    const baseAngle = Math.atan2(targetY - this.player.y, targetX - this.player.x);

    // Fire 3 rectangular bolts in a spread
    for (let i = -1; i <= 1; i++) {
      const angle = baseAngle + i * FIREBALL_SPREAD;
      const g = this.add.graphics().setDepth(12).setPosition(this.player.x, this.player.y);
      // Elongated rectangle pointing in travel direction
      g.fillStyle(0xfb923c, 1).fillRect(-12, -4, 24, 8);
      g.fillStyle(0xfef08a, 0.9).fillRect(-8, -2, 14, 4);
      g.fillStyle(0xffffff, 0.5).fillRect(-6, -1, 6, 2);
      g.setRotation(angle);
      this._fireballs.push({
        g,
        x: this.player.x, y: this.player.y,
        vx: Math.cos(angle) * FIREBALL_SPEED,
        vy: Math.sin(angle) * FIREBALL_SPEED,
        traveled: 0,
        active: true,
      });
    }
    this._spawnPickupParticles(this.player.x, this.player.y, 0xfb923c);
  }

  _castLightningStrike() {
    if (!this._playerHasSpell('spell_lightning_strike') || this._lightningCooldown > 0) return;
    this._lightningCooldown = LIGHTNING_COOLDOWN;
    const originX = this.player.x;
    const originY = this.player.y;
    let hitAny = false;

    for (const enemy of this._enemies) {
      if (!enemy.isAlive) continue;
      const dist = Math.hypot(enemy.container.x - originX, enemy.container.y - originY);
      if (dist > LIGHTNING_RADIUS) continue;
      const dmg = Math.max(1, Math.ceil(enemy.hp * 0.5 * this._damageMultiplier));
      hitAny = true;
      // Jagged lightning — 5 random offset segments from sky to target
      const startX = enemy.container.x + (Math.random() - 0.5) * 10;
      const startY = enemy.container.y - 160;
      const endX = enemy.container.x;
      const endY = enemy.container.y - 10;
      const segments = 5;
      const pts = [{ x: startX, y: startY }];
      for (let s = 1; s < segments; s++) {
        pts.push({
          x: startX + (endX - startX) * (s / segments) + (Math.random() - 0.5) * 28,
          y: startY + (endY - startY) * (s / segments),
        });
      }
      pts.push({ x: endX, y: endY });

      const boltG = this.add.graphics().setDepth(18);
      // Core bolt
      boltG.lineStyle(2, 0xfde047, 1.0);
      boltG.beginPath(); boltG.moveTo(pts[0].x, pts[0].y);
      for (const p of pts.slice(1)) boltG.lineTo(p.x, p.y);
      boltG.strokePath();
      // Glow bloom
      boltG.lineStyle(6, 0xfde047, 0.18);
      boltG.beginPath(); boltG.moveTo(pts[0].x, pts[0].y);
      for (const p of pts.slice(1)) boltG.lineTo(p.x, p.y);
      boltG.strokePath();
      // Impact flash at bottom
      boltG.fillStyle(0xfef08a, 0.6).fillCircle(endX, endY, 10);
      this.time.delayedCall(200, () => { if (boltG?.scene) boltG.destroy(); });
      enemy.takeDamage(dmg, 0, 0);
      this._showDamageNumber(enemy.container.x, enemy.container.y - 30, dmg, false, true);
      this._spawnPickupParticles(enemy.container.x, enemy.container.y, 0xfde047);
    }

    // Storm Crown: chain to 2 additional enemies outside the primary radius
    if (hitAny && this._worldState.relics?.stormCrown) {
      const chainTargets = this._enemies.filter(e => e.isAlive &&
        Math.hypot(e.container.x - originX, e.container.y - originY) > LIGHTNING_RADIUS &&
        Math.hypot(e.container.x - originX, e.container.y - originY) < LIGHTNING_RADIUS * 2.2
      ).slice(0, 2);
      for (const ce of chainTargets) {
        const chainDmg = Math.max(1, Math.ceil(ce.hp * 0.25 * this._damageMultiplier));
        const cBoltG = this.add.graphics().setDepth(18);
        cBoltG.lineStyle(1.5, 0xfde047, 0.7).lineBetween(originX, originY - 60, ce.container.x, ce.container.y - 10);
        cBoltG.fillStyle(0xfef08a, 0.4).fillCircle(ce.container.x, ce.container.y - 10, 7);
        this.time.delayedCall(200, () => { if (cBoltG?.scene) cBoltG.destroy(); });
        ce.takeDamage(chainDmg, 0, 0);
        this._showDamageNumber(ce.container.x, ce.container.y - 30, chainDmg, false, true);
      }
    }

    if (hitAny) {
      audioManager.playSfx('hit');
      this._showToast('Lightning Strike');
      this.cameras.main.flash(130, 255, 245, 180, true);
    } else {
      this._showToast('No enemies nearby');
    }
  }

  _castVoidBall() {
    if (!this._playerHasSpell('spell_void_ball') || this._voidBallCooldown > 0) return;
    this._voidBallCooldown = VOID_BALL_COOLDOWN;
    const ptr = this.input.activePointer;
    const targetX = ptr.worldX ?? ptr.x;
    const targetY = ptr.worldY ?? ptr.y;
    const angle = Math.atan2(targetY - this.player.y, targetX - this.player.x);
    const g = this.add.graphics().setDepth(12).setPosition(this.player.x, this.player.y);
    g.fillStyle(0x0f172a, 1).fillCircle(0, 0, 14);
    g.lineStyle(2, 0x67e8f9, 0.95).strokeCircle(0, 0, 14);
    g.fillStyle(0x67e8f9, 0.35).fillCircle(0, 0, 7);
    const vb = {
      g,
      x: this.player.x,
      y: this.player.y,
      vx: Math.cos(angle) * VOID_BALL_SPEED,
      vy: Math.sin(angle) * VOID_BALL_SPEED,
      life: 1400,
      active: true,
      hitIds: new Set(),
    };
    // Gravity distortion ring — pulses every 300ms while ball is alive
    const ringInterval = this.time.addEvent({
      delay: 300, loop: true,
      callback: () => {
        if (!vb.active) { ringInterval.remove(); return; }
        const ring = this.add.graphics().setDepth(17);
        ring.lineStyle(1.5, 0x67e8f9, 0.6);
        ring.strokeCircle(vb.x, vb.y, 8);
        this.tweens.add({
          targets: ring, scaleX: 3, scaleY: 3, alpha: 0,
          duration: 280, ease: 'Quad.easeOut',
          onComplete: () => { if (ring?.scene) ring.destroy(); },
        });
      },
    });
    vb.ringInterval = ringInterval;
    this._voidBalls.push(vb);
    this._spawnPickupParticles(this.player.x, this.player.y, 0x67e8f9);
    this._showToast('Void Ball');
  }

  _buildHotbar(width, height) {
    const totalW = HOTBAR_SLOTS * SLOT_SIZE + (HOTBAR_SLOTS - 1) * SLOT_GAP + HOTBAR_PAD * 2;
    const totalH = SLOT_SIZE + HOTBAR_PAD * 2;
    this._hotbarStartX = (width - totalW) / 2;
    this._hotbarStartY = height - totalH - 14;

    const panel = this.add.graphics().setDepth(90).setScrollFactor(0);
    panel.fillStyle(0x060614, 0.93).fillRoundedRect(this._hotbarStartX - 4, this._hotbarStartY - 4, totalW + 8, totalH + 8, 14);
    panel.lineStyle(1, 0x1e1b4b, 1).strokeRoundedRect(this._hotbarStartX - 4, this._hotbarStartY - 4, totalW + 8, totalH + 8, 14);

    this._hotbarSlotData = [];
    for (let i = 0; i < HOTBAR_SLOTS; i++) {
      const sx = this._hotbarStartX + HOTBAR_PAD + i * (SLOT_SIZE + SLOT_GAP), sy = this._hotbarStartY + HOTBAR_PAD;
      const bg = this.add.graphics().setDepth(91).setScrollFactor(0);
      const icon = this.add.image(sx + SLOT_SIZE / 2, sy + SLOT_SIZE / 2 - 10, '__spark__').setDepth(93).setScrollFactor(0).setDisplaySize(24, 24).setVisible(false);
      const numLabel = this.add.text(sx + 6, sy + 5, `${i + 1}`, { fontFamily: 'monospace', fontSize: '10px', color: '#4b5563' }).setDepth(93).setScrollFactor(0);
      const itemLabel = this.add.text(sx + SLOT_SIZE / 2, sy + SLOT_SIZE / 2 + 4, '', { fontFamily: 'monospace', fontSize: '10px', color: '#e2e8f0', align: 'center', wordWrap: { width: SLOT_SIZE - 8 } }).setOrigin(0.5).setDepth(93).setScrollFactor(0);
      this._hotbarSlotData.push({ bg, icon, numLabel, itemLabel, sx, sy });
    }
    this._refreshHotbar();
  }

  _drawSlotBg(g, sx, sy, slotIndex) {
    g.clear();
    const itemId = this.player.hotbar[slotIndex];
    const item = itemId ? this.itemRegistry.get(itemId) : null;
    if (item) {
      const col = RARITY_COLOR[item.rarity] ?? RARITY_COLOR.common;
      if (item.rarity === 'rare' || item.rarity === 'epic') {
        g.fillStyle(col, item.rarity === 'epic' ? 0.16 : 0.1).fillRoundedRect(sx - 3, sy - 3, SLOT_SIZE + 6, SLOT_SIZE + 6, 10);
      }
      g.fillStyle(0x1a0f3a, 1).fillRoundedRect(sx, sy, SLOT_SIZE, SLOT_SIZE, 8);
      g.fillStyle(col, 0.28).fillRoundedRect(sx + 1, sy + SLOT_SIZE - 12, SLOT_SIZE - 2, 11, { tl: 0, tr: 0, bl: 7, br: 7 });
      g.lineStyle(1.5, col, 0.6).strokeRoundedRect(sx, sy, SLOT_SIZE, SLOT_SIZE, 8);
    } else {
      g.fillStyle(0x0c0c1e, 1).fillRoundedRect(sx, sy, SLOT_SIZE, SLOT_SIZE, 8);
      g.lineStyle(1, 0x1c1c3a, 1).strokeRoundedRect(sx, sy, SLOT_SIZE, SLOT_SIZE, 8);
    }
  }

  _refreshSlotLabel(labelText, i) {
    const itemId = this.player.hotbar[i];
    const item = itemId ? this.itemRegistry.get(itemId) : null;
    labelText.setText(item ? item.name : '');
  }

  _setActiveSlot(index, force = false) {
    if (index === this.activeSlot && !force) return;
    this.activeSlot = index;
    const g = this._activeGlowGfx.clear();
    const slot = this._hotbarSlotData[index];
    const { sx, sy } = slot;
    g.lineStyle(3, 0xffffff, 0.1).strokeRoundedRect(sx - 4, sy - 4, SLOT_SIZE + 8, SLOT_SIZE + 8, 10);
    g.lineStyle(2, 0xffffff, 1.0).strokeRoundedRect(sx, sy, SLOT_SIZE, SLOT_SIZE, 8);
    this.tweens.add({
      targets: [slot.icon, slot.itemLabel],
      scaleX: 1.12,
      scaleY: 1.12,
      duration: 90,
      yoyo: true,
    });
  }

  _refreshHotbar() {
    for (let i = 0; i < HOTBAR_SLOTS; i++) {
      this._drawSlotBg(this._hotbarSlotData[i].bg, this._hotbarSlotData[i].sx, this._hotbarSlotData[i].sy, i);
      this._refreshSlotLabel(this._hotbarSlotData[i].itemLabel, i);
      const itemId = this.player.hotbar[i];
      const item = itemId ? this.itemRegistry.get(itemId) : null;
      const icon = this._hotbarSlotData[i].icon;
      if (item) {
        const key = this.assetManager.ensureItemTexture(item, 36);
        // setTexture resets displayWidth/Height to the native canvas size, so
        // re-apply the fixed display size after every texture swap.
        icon.setTexture(key).setDisplaySize(34, 34).setVisible(true);
      } else {
        icon.setVisible(false);
      }
    }
    this._setActiveSlot(this.activeSlot, true);
  }

  _onPointerDown(mx, my) {
    if (this._gameOver || this._levelingUp) return;
    for (let i = 0; i < HOTBAR_SLOTS; i++) {
      const { sx, sy } = this._hotbarSlotData[i];
      if (mx >= sx && mx <= sx + SLOT_SIZE && my >= sy && my <= sy + SLOT_SIZE) return this._equipFromHotbar(i);
    }
    if (this._attackCooldown > 0) {
      const now = this.time.now;
      this._attackBuffer = {
        x: mx,
        y: my,
        executeAt: now + Math.min(this._attackCooldown, INPUT_BUFFER_MS),
        discardAt: now + INPUT_BUFFER_MS,
      };
      return;
    }
    this._doAttack(mx, my);
  }

  _equipFromHotbar(slotIdx) {
    const itemId = this.player.hotbar[slotIdx];
    if (!itemId) return;
    const itemDef = this.itemRegistry.get(itemId);
    if (!itemDef) return;

    if (itemDef.type === 'spell') {
      this._setActiveSlot(slotIdx);
      if (itemDef.id === 'spell_lightning_strike') this._castLightningStrike();
      else if (itemDef.id === 'spell_void_ball') this._castVoidBall();
      return;
    }

    // Passive relics that ended up on the hotbar are absorbed immediately.
    if (itemDef.type === 'passive') {
      this._applyPassiveItem(itemDef);
      this.player.removeItem(itemDef.id, 1);
      this.player.hotbar[slotIdx] = null;
      this._refreshHotbar();
      this._updateHud();
      audioManager.playSfx('equip');
      return;
    }

    if (!itemDef.slot) {
      this._useConsumable(slotIdx, itemDef);
      return;
    }

    const displaced = this.player.equip(itemId);
    if (displaced === null && this.player.equipment[itemDef.slot]?.id !== itemId) return;
    this.player.hotbar[slotIdx] = displaced?.id ?? null;
    this._refreshHotbar();
    this._redrawWeapon();
    this._updateHud();
    this._saveGame();
    audioManager.playSfx('equip');
  }

  _useConsumable(slotIdx, itemDef) {
    if (itemDef.type !== 'consumable') return;

    const heal = itemDef.stats?.heal || 0;
    if (heal > 0) {
      // In a party: if a nearby teammate is downed, revive them instead of healing self
      if (this._mpData && this._remoteGfx) {
        const px = this.player.x, py = this.player.y;
        let reviveTarget = null;
        for (const entry of this._remoteGfx.values()) {
          if ((entry.hp ?? 1) <= 0 && Math.hypot(entry.x - px, entry.y - py) < 90) {
            reviveTarget = entry;
            break;
          }
        }
        if (reviveTarget) {
          const reviveHp = Math.min(30, heal);
          multiplayer.sendEvent('revive_player', { targetPid: reviveTarget.pid, hp: reviveHp });
          this.player.removeItem(itemDef.id, 1);
          const remaining = this.player.inventory.find(s => s.item.id === itemDef.id);
          if (!remaining) this.player.hotbar[slotIdx] = null;
          this._refreshHotbar();
          this._updateHud();
          this._saveGame();
          audioManager.playSfx('levelup');
          this._showToast(`Revived teammate!`);
          return;
        }
      }
      this.player.hp = Math.min(this.player.effectiveMaxHp, this.player.hp + heal);
      this._showToast(`Recovered ${heal} HP`);
    }

    this.player.removeItem(itemDef.id, 1);
    const remaining = this.player.inventory.find(s => s.item.id === itemDef.id);
    if (!remaining) this.player.hotbar[slotIdx] = null;

    this._refreshHotbar();
    this._updateHud();
    this._saveGame();
    audioManager.playSfx('pickup');
  }

  _buildTooltip() {
    this._ttPanel = this.add.graphics().setDepth(95).setScrollFactor(0).setVisible(false);
    this._ttNameTxt = this.add.text(0, 0, '', { fontFamily: 'monospace', fontSize: '12px', color: '#ffffff' }).setDepth(96).setScrollFactor(0).setVisible(false);
    this._ttBodyTxt = this.add.text(0, 0, '', { fontFamily: 'monospace', fontSize: '10px', color: '#94a3b8', wordWrap: { width: 180 } }).setDepth(96).setScrollFactor(0).setVisible(false);
    this._ttLoreTxt = this.add.text(0, 0, '', { fontFamily: 'monospace', fontSize: '10px', color: '#c4b5fd', fontStyle: 'italic', wordWrap: { width: 180 } }).setDepth(96).setScrollFactor(0).setVisible(false);
    this._ttHoveredSlot = -1;
  }

  _updateTooltip() {
    const ptr = this.input.activePointer;
    let hovered = -1;
    for (let i = 0; i < HOTBAR_SLOTS; i++) {
      const { sx, sy } = this._hotbarSlotData[i];
      if (ptr.x >= sx && ptr.x <= sx + SLOT_SIZE && ptr.y >= sy && ptr.y <= sy + SLOT_SIZE && this.player.hotbar[i]) { hovered = i; break; }
    }
    if (hovered !== this._ttHoveredSlot) {
      this._ttHoveredSlot = hovered;
      hovered >= 0 ? this._showTooltip(hovered) : this._hideTooltip();
    }
  }

  _showTooltip(slotIdx) {
    const item = this.itemRegistry.get(this.player.hotbar[slotIdx]);
    if (!item) return;
    const { sx, sy } = this._hotbarSlotData[slotIdx];
    const colHex = '#' + (RARITY_COLOR[item.rarity] ?? RARITY_COLOR.common).toString(16).padStart(6, '0');
    
    this._ttNameTxt.setText(item.name).setColor(colHex);
    const statLines = Object.entries(item.stats || {}).map(([k, v]) => `  ${(STAT_LABEL[k]||k).padEnd(5)}  ${v>=0?'+':''}${v}`).join('\n');
    const spellHint = item.type === 'spell' ? `\nUse Key: ${item.use_key || '?'}` : '';
    this._ttBodyTxt.setText(`${item.type.toUpperCase()} - ${item.rarity}${spellHint}\n\n${item.description}\n${statLines ? '\n'+statLines : ''}`);
    this._ttLoreTxt.setText(item.lore ? item.lore : '');
    
    const loreH = item.lore ? this._ttLoreTxt.height + 14 : 0;
    const w = 210, h = 18 + this._ttBodyTxt.height + 28 + loreH;
    const tx = Phaser.Math.Clamp(sx + SLOT_SIZE/2 - w/2, 4, this.scale.width - w - 4), ty = sy - h - 8;
    
    this._ttPanel.clear().fillStyle(0x04040f, 0.97).fillRoundedRect(tx, ty, w, h, 8).lineStyle(1.5, RARITY_COLOR[item.rarity] || RARITY_COLOR.common, 0.85).strokeRoundedRect(tx, ty, w, h, 8);
    this._ttNameTxt.setPosition(tx + 10, ty + 8).setVisible(true);
    this._ttBodyTxt.setPosition(tx + 10, ty + 32).setVisible(true);
    this._ttLoreTxt.setPosition(tx + 10, ty + 38 + this._ttBodyTxt.height).setVisible(!!item.lore);
    this._ttPanel.setVisible(true);
  }

  _hideTooltip() { this._ttPanel.setVisible(false); this._ttNameTxt.setVisible(false); this._ttBodyTxt.setVisible(false); this._ttLoreTxt.setVisible(false); }

  _buildHud(width, height) {
    const pad = 14;
    this._hpBarContainer = this.add.container(0, 0).setDepth(110).setScrollFactor(0);
    // HP bar track — darker background, 14px tall with radius 7
    // Explicit setScrollFactor(0) on each child: Phaser 3 containers do NOT
    // propagate scrollFactor to children, so graphics added to the container
    // would still scroll with the camera unless explicitly fixed here.
    this._hpTrack = this.add.graphics().setScrollFactor(0).setDepth(110).fillStyle(0x06060f, 1).fillRoundedRect(pad, pad, 200, 14, 7).lineStyle(1, 0x1a1a38, 1).strokeRoundedRect(pad, pad, 200, 14, 7);
    this._hpFill = this.add.graphics().setScrollFactor(0).setDepth(110);
    this._hpText = this.add.text(pad + 202, pad + 2, '', { fontFamily: 'monospace', fontSize: '10px', color: '#94a3b8' }).setScrollFactor(0).setDepth(110);
    this._hpBarContainer.add([this._hpTrack, this._hpFill, this._hpText]);

    // XP bar — thin indigo bar below HP bar
    this._xpTrack = this.add.graphics().setDepth(110).setScrollFactor(0);
    this._xpTrack.fillStyle(0x06060f, 1).fillRoundedRect(pad, pad + 18, 200, 6, 3).lineStyle(1, 0x1a1a38, 0.8).strokeRoundedRect(pad, pad + 18, 200, 6, 3);
    this._xpFill = this.add.graphics().setDepth(111).setScrollFactor(0);

    this._lvlText = this.add.text(pad, pad + 26, '', { fontFamily: 'monospace', fontSize: '12px', color: '#a78bfa' }).setDepth(112).setScrollFactor(0);
    this._statText = this.add.text(pad, pad + 44, '', { fontFamily: 'monospace', fontSize: '10px', color: '#94a3b8' }).setDepth(112).setScrollFactor(0);

    // Floor indicator — compact "F-01" format, subdued color
    const floorLabel = `F-${String(this.dungeonLevel).padStart(2, '0')}`;
    this._floorText = this.add.text(width / 2, 14, floorLabel, { fontFamily: 'monospace', fontSize: '18px', color: '#6d6d9e', stroke: '#000000', strokeThickness: 3 }).setOrigin(0.5, 0).setDepth(112).setScrollFactor(0);

    this._equipTxt = this.add.text(width - pad, pad, '', { fontFamily: 'monospace', fontSize: '11px', color: '#9ca3af', align: 'right' }).setOrigin(1, 0).setDepth(112).setScrollFactor(0);

    // Dash cooldown indicator — shorter label, 11px
    this._dashText = this.add.text(pad, pad + 62, 'DASH', {
      fontFamily: 'monospace', fontSize: '11px', color: '#38bdf8',
    }).setDepth(112).setScrollFactor(0);

    // Sound toggle button
    this._soundBtn = this.add.text(pad, pad + 78, audioManager.enabled ? '[SND ON ]' : '[SND OFF]', {
      fontFamily: 'monospace', fontSize: '10px',
      color: audioManager.enabled ? '#4ade80' : '#dc2626',
    }).setDepth(112).setScrollFactor(0).setInteractive({ useHandCursor: true });
    this._soundBtn.on('pointerdown', () => {
      audioManager.toggleMuted();
      this._soundBtn.setText(audioManager.enabled ? '[SND ON ]' : '[SND OFF]');
      this._soundBtn.setStyle({ color: audioManager.enabled ? '#4ade80' : '#dc2626' });
    });

    this._updateHud();
  }

  _updateHud() {
    const p = this.player;
    const ratio = p.hp / p.effectiveMaxHp;
    const col = ratio > 0.5 ? 0x16a34a : ratio > 0.25 ? 0xca8a04 : 0xdc2626;
    this._hpFill.clear().fillStyle(col, 1);
    // HP bar is now 14px tall with radius 7
    if (ratio > 0) this._hpFill.fillRoundedRect(14, 14, Math.max(200 * ratio, 4), 14, 7);

    // HP number displayed to the right of the bar
    this._hpText.setText(`${p.hp}/${p.effectiveMaxHp}`);
    // XP bar fill — indigo
    if (this._xpFill) {
      const xpRatio = p.xpToNext > 0 ? Math.min(p.xp / p.xpToNext, 1) : 0;
      this._xpFill.clear().fillStyle(0x4f46e5, 1);
      if (xpRatio > 0) this._xpFill.fillRoundedRect(14, 14 + 18, Math.max(200 * xpRatio, 3), 6, 3);
    }
    this._lvlText.setText(`Lv.${p.level}  ${p.xp}/${p.xpToNext} XP`);
    // Compact stat format: gold first, then atk/def
    this._statText.setText(`${p.gold}g  ATK${p.attack}  DEF${p.defense}`);
    const equipLines = Object.entries(p.equipment).map(([k, v]) => `${k.padEnd(10)}  ${v?.name ?? '-'}`);
    const passives = this._worldState?.absorbedPassives || [];
    if (passives.length) equipLines.push(`passives    ${passives.join(', ')}`);
    this._equipTxt.setText(equipLines.join('\n'));
    // Dash cooldown display — compact, no [SPACE] prefix
    if (this._dashText) {
      if ((this._dashCooldown || 0) > 0) {
        this._dashText.setText(`${(this._dashCooldown / 1000).toFixed(1)}s`).setStyle({ color: '#1e4060' });
      } else {
        this._dashText.setText('DASH').setStyle({ color: '#38bdf8' });
      }
    }
  }

  // ── Inventory UI ──────────────────────────────────────────────────────────
  _toggleInventory() {
    if (this._inventoryOpen) {
      this._closeInventory();
    } else {
      this._openInventory();
    }
  }

  _openInventory() {
    if (this._inventoryOpen) return;
    this._inventoryOpen = true;
    this._paused = true;
    const { width, height } = this.scale;
    const pw = 580, ph = 420;
    const px = (width - pw) / 2, py = (height - ph) / 2;

    const overlay = this.add.graphics().setDepth(600).setScrollFactor(0);
    overlay.fillStyle(0x000000, 0.75).fillRect(0, 0, width, height);

    const panel = this.add.graphics().setDepth(601).setScrollFactor(0);
    panel.fillStyle(0x060610, 0.98).fillRoundedRect(px, py, pw, ph, 12);
    panel.lineStyle(1, 0x1a1a38, 1).strokeRoundedRect(px, py, pw, ph, 12);
    panel.lineStyle(1, 0x2a2a5a, 0.3).strokeRoundedRect(px + 2, py + 2, pw - 4, ph - 4, 10);

    const title = this.add.text(px + pw / 2, py + 18, 'INVENTORY  [I] to close', {
      fontFamily: 'monospace', fontSize: '13px', color: '#6366f1',
    }).setOrigin(0.5, 0).setDepth(602).setScrollFactor(0);

    const COLS = 8, ROWS = 4, SLOT = 54, GAP = 6;
    const gridX = px + (pw - (COLS * SLOT + (COLS - 1) * GAP)) / 2;
    const gridY = py + 52;
    const slotObjs = [];

    for (let row = 0; row < ROWS; row++) {
      for (let col = 0; col < COLS; col++) {
        const idx = row * COLS + col;
        const sx = gridX + col * (SLOT + GAP);
        const sy = gridY + row * (SLOT + GAP);
        const slotGfx = this.add.graphics().setDepth(602).setScrollFactor(0);
        slotGfx.fillStyle(0x0e0e20, 1).fillRoundedRect(sx, sy, SLOT, SLOT, 6);
        slotGfx.lineStyle(1, 0x151528, 1).strokeRoundedRect(sx, sy, SLOT, SLOT, 6);

        const invSlot = this.player.inventory[idx];
        if (invSlot) {
          const item = invSlot.item;
          const RARITY_BORDER = { common: 0xcbd5e1, uncommon: 0x4ade80, rare: 0x60a5fa, epic: 0xc084fc, legendary: 0xfbbf24 };
          const borderCol = RARITY_BORDER[item.rarity] || 0xcbd5e1;
          slotGfx.lineStyle(1.5, borderCol, 0.8).strokeRoundedRect(sx, sy, SLOT, SLOT, 6);
          const texKey = this.assetManager.ensureItemTexture(item, SLOT - 8);
          const icon = this.add.image(sx + SLOT / 2, sy + SLOT / 2 - 4, texKey).setDepth(603).setScrollFactor(0);
          const nameText = this.add.text(sx + SLOT / 2, sy + SLOT - 8, item.name.length > 8 ? item.name.substring(0, 7) + '..' : item.name, {
            fontFamily: 'monospace', fontSize: '8px', color: '#94a3b8',
          }).setOrigin(0.5, 1).setDepth(603).setScrollFactor(0);
          slotObjs.push(icon, nameText);
          // Highlight equipped items
          const equipped = Object.values(this.player.equipment).some(e => e?.id === item.id);
          if (equipped) {
            slotGfx.fillStyle(borderCol, 0.1).fillRoundedRect(sx, sy, SLOT, SLOT, 6);
          }
        }
        slotObjs.push(slotGfx);
      }
    }

    // Equipment section header
    const eqLabel = this.add.text(px + 16, gridY + ROWS * (SLOT + GAP) + 12, 'EQUIPPED:', {
      fontFamily: 'monospace', fontSize: '10px', color: '#475569',
    }).setDepth(602).setScrollFactor(0);

    const eqLine = this.add.text(px + 16, gridY + ROWS * (SLOT + GAP) + 26,
      Object.entries(this.player.equipment).filter(([, v]) => v).map(([k, v]) => `${k}: ${v.name}`).join('   ') || 'Nothing equipped',
      { fontFamily: 'monospace', fontSize: '10px', color: '#6d6d9e' },
    ).setDepth(602).setScrollFactor(0);

    this._inventoryUi = [overlay, panel, title, eqLabel, eqLine, ...slotObjs];

    // Close on ESC
    this.input.keyboard.once('keydown-ESC', () => this._closeInventory());
  }

  _closeInventory() {
    if (!this._inventoryOpen) return;
    this._inventoryOpen = false;
    this._paused = false;
    for (const obj of this._inventoryUi || []) obj?.destroy?.();
    this._inventoryUi = [];
  }

  _buildLootLog(width, height) {
    // Loot log removed — no-op kept so any stale call sites don't throw.
  }

  // Silent no-op — call sites preserved throughout codebase.
  _logEvent(msg) {}

  // ── Minimap ───────────────────────────────────────────────────────────────
  _buildMinimap(width, height) {
    const { cols: _mmCols, rows: _mmRows } = this.mapManager.getMapSize();
    // Scale minimap tile size down on large maps so it always fits in ~80x60 pixels.
    const T = Math.max(1, Math.floor(Math.min(80 / _mmCols, 60 / _mmRows)));
    const mw = _mmCols * T, mh = _mmRows * T;
    const hotbarH = this._hotbarTotalH();
    const ox = width  - mw - 10;
    const oy = height - hotbarH - mh - 10;
    this._mmX = ox; this._mmY = oy; this._mmT = T;

    // Fog of war: always fresh per floor — room indices are per-floor so old data is invalid
    this._mmVisited = new Set([0]); // spawn room always starts visible

    const bg = this.add.graphics().setDepth(113).setScrollFactor(0);
    bg.fillStyle(0x050814, 0.88).fillRoundedRect(ox - 4, oy - 4, mw + 8, mh + 8, 5);
    bg.lineStyle(1, 0x22304d, 1).strokeRoundedRect(ox - 4, oy - 4, mw + 8, mh + 8, 5);

    this._mmStaticGfx = this.add.graphics().setDepth(114).setScrollFactor(0);
    this._mmDotGfx    = this.add.graphics().setDepth(115).setScrollFactor(0);
    this._drawMinimapStatic();
  }

  _drawMinimapStatic() {
    const gfx = this._mmStaticGfx, map = this.mapManager.map;
    const T = this._mmT, ox = this._mmX, oy = this._mmY;
    const visited = this._mmVisited || new Set();
    const { cols: _mmC, rows: _mmR } = this.mapManager.getMapSize();
    gfx.clear();
    // Corridors — always dim grey
    for (let r = 0; r < _mmR; r++) {
      for (let c = 0; c < _mmC; c++) {
        if (map[r][c] === 0) { gfx.fillStyle(0x1e293b, 1); gfx.fillRect(ox + c*T, oy + r*T, T-1, T-1); }
      }
    }
    const roomColors = { spawn: 0x16a34a, portal: 0xa855f7, shop: 0xfbbf24, trap: 0xdc2626, treasure: 0x3b82f6 };
    for (let ri = 0; ri < this.rooms.length; ri++) {
      const room = this.rooms[ri];
      const isVisited = visited.has(ri);
      const col = isVisited ? (roomColors[room.type] ?? 0x475569) : 0x1e2d40;
      gfx.fillStyle(col, isVisited ? 0.75 : 0.45);
      for (let r = room.y; r < room.y + room.h; r++)
        for (let c = room.x; c < room.x + room.w; c++)
          if (map[r]?.[c] === 0) gfx.fillRect(ox + c*T, oy + r*T, T-1, T-1);
    }
  }

  _updateMinimap() {
    if (!this._mmDotGfx) return;
    const T = this._mmT, ox = this._mmX, oy = this._mmY;
    const tw = this._tileW, th = this._tileH;

    // Fog of war: detect which room the player is in and mark as visited.
    // This check is cheap (set ops) so it runs every frame.
    const playerTileC = Math.floor(this._playerContainer.x / tw);
    const playerTileR = Math.floor(this._playerContainer.y / th);
    const prevSize = this._mmVisited.size;
    for (let ri = 0; ri < this.rooms.length; ri++) {
      const room = this.rooms[ri];
      if (playerTileC >= room.x && playerTileC < room.x + room.w &&
          playerTileR >= room.y && playerTileR < room.y + room.h) {
        this._mmVisited.add(ri);
      }
    }
    if (this._mmVisited.size !== prevSize) this._drawMinimapStatic();

    // Dot redraw is throttled: only redraw when the player moves >2px or every 100ms.
    // Graphics.clear() + fillCircle every frame is wasteful when the player stands still.
    const wx = this._playerContainer.x, wy = this._playerContainer.y;
    const now = this.time.now;
    const moved = Math.hypot(wx - this._lastMmPos.x, wy - this._lastMmPos.y) > 2;
    const elapsed = now - this._lastMmTime > 100;
    if (!moved && !elapsed) return;
    this._lastMmPos.x = wx;
    this._lastMmPos.y = wy;
    this._lastMmTime = now;

    this._mmDotGfx.clear();
    // Remote players
    if (this._mpData && this._remoteGfx) {
      for (const [, entry] of this._remoteGfx) {
        if (entry.targetX === undefined) continue;
        const rx = (entry.x / tw) * T, ry = (entry.y / th) * T;
        this._mmDotGfx.fillStyle(0xe67e22, 1).fillCircle(ox + rx, oy + ry, 2);
      }
    }
    // Local player dot
    const px = (this._playerContainer.x / tw) * T;
    const py = (this._playerContainer.y / th) * T;
    this._mmDotGfx.fillStyle(0xffffff, 1).fillCircle(ox + px, oy + py, 2.5);
  }

  // ── Multiplayer chat ──────────────────────────────────────────────────────
  _openChat() {
    if (this._chatInputActive) return;
    this._chatInputActive = true;
    this._chatBuffer = '';
    const { width, height } = this.scale;
    const cy = height - this._hotbarTotalH() - 56;

    const elements = [];
    const bg = this.add.graphics().setDepth(600).setScrollFactor(0);
    bg.fillStyle(0x000000, 0.80).fillRoundedRect(width/2 - 210, cy - 4, 420, 36, 6);
    bg.lineStyle(1, 0x334155, 1).strokeRoundedRect(width/2 - 210, cy - 4, 420, 36, 6);
    elements.push(bg);

    const chatTxt = this.add.text(width/2 - 198, cy + 5, 'Say: _', {
      fontFamily: 'monospace', fontSize: '13px', color: '#f8fafc',
    }).setDepth(601).setScrollFactor(0).setOrigin(0, 0.5);
    elements.push(chatTxt);

    const close = () => {
      elements.forEach(e => e.destroy());
      this.input.keyboard.off('keydown', onKey);
      this._chatInputActive = false;
    };

    const onKey = (ev) => {
      if (ev.key === 'Escape') { close(); return; }
      if (ev.key === 'Enter') {
        const txt = this._chatBuffer.trim();
        if (txt) {
          this._showChatBubble(txt, null); // always show locally
          if (this._mpData) multiplayer.sendEvent('chat', { text: txt }); // broadcast if in party
        }
        close();
        return;
      }
      if (ev.key === 'Backspace') this._chatBuffer = this._chatBuffer.slice(0, -1);
      else if (ev.key.length === 1 && this._chatBuffer.length < 36) this._chatBuffer += ev.key;
      chatTxt.setText(`Say: ${this._chatBuffer}_`);
    };
    this.input.keyboard.on('keydown', onKey);
  }

  _showChatBubble(text, playerId) {
    // Determine world-space anchor
    const isLocal = playerId === null;
    let wx, wy;
    if (isLocal) {
      wx = this._playerContainer.x; wy = this._playerContainer.y;
    } else {
      const entry = this._remoteGfx?.get(playerId);
      if (!entry) return;
      wx = entry.x; wy = entry.y;
    }
    const bubble = this.add.text(wx, wy - 60, text, {
      fontFamily: 'monospace', fontSize: '11px', color: '#f8fafc',
      backgroundColor: '#1e293b', padding: { x: 6, y: 4 },
      stroke: '#000000', strokeThickness: 1,
    }).setOrigin(0.5, 1).setDepth(201).setAlpha(1);

    // Fade out after 3 s
    this.time.delayedCall(2400, () => {
      this.tweens.add({ targets: bubble, alpha: 0, duration: 600, onComplete: () => { try { bubble.destroy(); } catch {} } });
    });

    // Follow moving objects (update each frame for 3 s)
    const followTimer = this.time.addEvent({
      delay: 16, loop: true, callback: () => {
        if (!bubble.scene) { followTimer.remove(); return; }
        if (isLocal) {
          bubble.setPosition(this._playerContainer.x, this._playerContainer.y - 60);
        } else {
          const e = this._remoteGfx?.get(playerId);
          if (e) bubble.setPosition(e.x, e.y - 60);
        }
      },
    });
    this.time.delayedCall(3000, () => followTimer.remove());
  }

  _buildPerformancePanel(width) {
    this._perfText = this.add.text(width - 16, 12, '', {
      fontFamily: 'monospace',
      fontSize: '10px',
      color: '#86efac',
      align: 'right',
    }).setOrigin(1, 0).setDepth(150).setScrollFactor(0).setVisible(!!this._worldState.performanceVisible);
  }

  _updatePerformancePanel() {
    if (!this._perfText) return;
    this._perfText.setVisible(!!this._worldState.performanceVisible);
    if (!this._worldState.performanceVisible) return;
    const fps = this.game.loop.actualFps?.toFixed(0) || '0';
    const heap = performance?.memory?.usedJSHeapSize ? `${Math.round(performance.memory.usedJSHeapSize / 1048576)} MB` : 'n/a';
    this._perfText.setText(`FPS ${fps}\nMEM ${heap}`);
  }

  _updateEpicTrail(delta) {
    this._epicTrailTimer += delta;
    const epicEquipped = Object.values(this.player.equipment).some(item => item?.rarity === 'epic');
    if (!epicEquipped || this._epicTrailTimer < 240) return;
    this._epicTrailTimer = 0;
    this._spawnPickupParticles(this.player.x + this._randInt(-8, 8), this.player.y + this._randInt(-10, 10), 0xa855f7);
  }

  _togglePauseMenu() {
    if (this._gameOver || this._levelingUp || this._levelIntroActive) return;
    this._paused ? this._closePauseMenu() : this._openPauseMenu();
  }

  _openPauseMenu() {
    this._paused = true;
    this.physics.world.pause();
    const { width, height } = this.scale;
    const cx = width / 2;
    const panelY = height / 2 - 150;
    const overlay = this.add.graphics().setDepth(500).setScrollFactor(0);
    overlay.fillStyle(0x000000, 0.72).fillRect(0, 0, width, height);
    const panel = this.add.graphics().setDepth(501).setScrollFactor(0);
    panel.fillStyle(0x090b16, 0.96).fillRoundedRect(cx - 170, panelY, 340, 320, 16).lineStyle(2, 0x7c3aed, 0.9).strokeRoundedRect(cx - 170, panelY, 340, 320, 16);
    const title = this.add.text(cx, panelY + 28, 'PAUSED', { fontFamily: 'monospace', fontSize: '28px', color: '#f8fafc' }).setOrigin(0.5).setDepth(502).setScrollFactor(0);
    const sub = this.add.text(cx, panelY + 58, `Seed ${this.seed}  Floor ${this.dungeonLevel}`, { fontFamily: 'monospace', fontSize: '11px', color: '#a5b4fc' }).setOrigin(0.5).setDepth(502).setScrollFactor(0);

    const buttons = [
      { label: 'Resume', onClick: () => this._closePauseMenu() },
      { label: audioManager.enabled ? 'Sound: On' : 'Sound: Off', onClick: () => { audioManager.toggleMuted(); this._closePauseMenu(); this._openPauseMenu(); } },
      { label: this._worldState.performanceVisible ? 'Performance: On' : 'Performance: Off', onClick: () => { this._worldState.performanceVisible = !this._worldState.performanceVisible; this._closePauseMenu(); this._openPauseMenu(); } },
      { label: 'Share Seed', onClick: () => this._shareSeed() },
      { label: 'Quit To Menu', onClick: () => { this._saveGame(); this.scene.start('MenuScene'); } },
    ];
    this._pauseUi = [overlay, panel, title, sub];
    buttons.forEach((button, idx) => {
      const y = panelY + 112 + idx * 42;
      const bg = this.add.graphics().setDepth(502).setScrollFactor(0);
      const draw = (hover) => bg.clear().fillStyle(hover ? 0x6d28d9 : 0x312e81, 1).fillRoundedRect(cx - 120, y, 240, 32, 8);
      draw(false);
      const txt = this.add.text(cx, y + 16, button.label, { fontFamily: 'monospace', fontSize: '14px', color: '#ffffff' }).setOrigin(0.5).setDepth(503).setScrollFactor(0);
      txt.setInteractive({ useHandCursor: true }).on('pointerover', () => draw(true)).on('pointerout', () => draw(false)).on('pointerdown', button.onClick);
      this._pauseUi.push(bg, txt);
    });
  }

  _closePauseMenu() {
    this._paused = false;
    this.physics.world.resume();
    for (const node of this._pauseUi) node?.destroy?.();
    this._pauseUi = [];
  }

  _shareSeed() {
    const url = `${window.location.origin}${window.location.pathname}?seed=${this.seed}`;
    navigator.clipboard?.writeText(url);
    this._showToast('Seed URL copied');
    this._logEvent(`Share seed copied: ${this.seed}`);
  }

  _openDebugConsole() {
    const input = window.prompt('Debug command', '/spawn potion_health');
    if (!input) return;
    const [command, arg] = input.trim().split(/\s+/);
    if (command === '/spawn' && arg) {
      const item = this.itemRegistry.get(arg);
      if (!item) return this._showToast(`Unknown item: ${arg}`);
      this.player.addItem(item, 1);
      const emptySlot = this.player.hotbar.findIndex(s => s === null);
      if (emptySlot !== -1) this.player.setHotbar(emptySlot, item.id);
      this._refreshHotbar();
      this._saveGame();
      this._logEvent(`Debug spawned ${item.name}`);
      return this._showToast(`Spawned ${item.name}`);
    }
    if (command === '/god') {
      this._worldState.godMode = !this._worldState.godMode;
      this._saveGame();
      this._logEvent(`God mode ${this._worldState.godMode ? 'enabled' : 'disabled'}`);
      return this._showToast(`God mode ${this._worldState.godMode ? 'ON' : 'OFF'}`);
    }
    if (command === '/next') {
      this._nextLevel();
      return;
    }
    this._showToast('Unknown debug command');
  }

  _showFatalError(message) {
    const { width, height } = this.scale;
    this.add.rectangle(width / 2, height / 2, width, height, 0x040404, 1);
    this.add.text(width / 2, height / 2 - 18, 'LOAD ERROR', {
      fontFamily: 'monospace',
      fontSize: '26px',
      color: '#ef4444',
    }).setOrigin(0.5);
    this.add.text(width / 2, height / 2 + 18, message, {
      fontFamily: 'monospace',
      fontSize: '12px',
      color: '#e5e7eb',
      wordWrap: { width: width - 80 },
      align: 'center',
    }).setOrigin(0.5);
  }

  _buildVignette(width, height) {
    this._vignette = this.add.graphics().setDepth(140).setScrollFactor(0);
    for (let i = 0; i < 7; i++) {
      this._vignette.lineStyle(24, 0x000000, 0.05);
      this._vignette.strokeRect(i * 2, i * 2, width - i * 4, height - i * 4);
    }
  }

  _startDust() {
    this._dustEvent = this.time.addEvent({
      delay: 1400,
      loop: true,
      callback: () => {
        const y = this._randInt(24, this.scale.height - this._hotbarTotalH() - 24);
        const x = this._randFloat() > 0.5 ? -20 : this.scale.width + 20;
        const txt = this.add.text(x, y, '.', {
          fontFamily: 'monospace',
          fontSize: '18px',
          color: '#cbd5e1',
        }).setDepth(19).setAlpha(0.12);
        this.tweens.add({
          targets: txt,
          x: x < 0 ? this.scale.width + 24 : -24,
          alpha: 0,
          duration: 7000 + this._randInt(0, 2000),
          onComplete: () => txt.destroy(),
        });
      },
    });
  }

  _saveHighScore() {
    const current = {
      floor: this.dungeonLevel,
      level: this.player.level,
      gold: this.player.gold,
      kills: this._worldState?.kills || 0,
      damageDealt: this._worldState?.damageDealt || 0,
      classId: this._worldState?.classId || null,
      runMs: Date.now() - (this._worldState?.runStartTime || Date.now()),
      timestamp: Date.now(),
    };
    let scores = [];
    try {
      scores = JSON.parse(localStorage.getItem(HIGH_SCORE_KEY) || '[]');
    } catch {
      scores = [];
    }
    scores.push(current);
    scores.sort((a, b) => b.floor - a.floor || b.level - a.level || b.gold - a.gold);
    localStorage.setItem(HIGH_SCORE_KEY, JSON.stringify(scores.slice(0, 5)));
    return scores[0];
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Combat & Experience
  // ─────────────────────────────────────────────────────────────────────────────
  _doDash() {
    if (this._dashCooldown > 0 || this._paused || this._gameOver || this._levelingUp || this._levelIntroActive || this._chatInputActive) return;
    // Allow dashing in any direction; if standing still, dash in last-faced direction
    let vx = this._physBody.velocity.x;
    let vy = this._physBody.velocity.y;
    let len = Math.hypot(vx, vy);
    if (len < 10) {
      // Use last facing direction
      vx = this._facing || 1;
      vy = 0;
      len = 1;
    }
    this._dashCooldown = DASH_COOLDOWN;
    this._dashActive = true;
    const nx = vx / len, ny = vy / len;
    // Zero drag so the burst isn't eaten, raise max velocity cap
    this._physBody.setDrag(0, 0);
    this._physBody.setAcceleration(0, 0);
    this._physBody.setMaxVelocity(DASH_SPEED, DASH_SPEED);
    this._physBody.setVelocity(nx * DASH_SPEED, ny * DASH_SPEED);
    this._iframes = Math.max(this._iframes, DASH_DURATION + 80);
    // Restore physics after dash window
    this.time.delayedCall(DASH_DURATION, () => {
      this._dashActive = false;
      this._physBody.setDrag(PLAYER_DRAG, PLAYER_DRAG);
    });
    // ── Dash ghost trail: spawn DASH_GHOST_COUNT afterimage copies of the player ──
    // Each ghost is a plain Graphics snapshot drawn at staggered delays so they
    // trail behind naturally. They fade to alpha 0 and self-destroy. No heap alloc
    // per frame — all cleanup is handled by the tween's onComplete.
    this._spawnDashGhosts();
    // Shadow Step: leave a shadow clone that damages nearby enemies
    if (this._worldState.relics?.shadowStep) {
      const cloneX = this.player.x, cloneY = this.player.y;
      const cloneG = this.add.graphics().setDepth(9);
      cloneG.setPosition(cloneX, cloneY);
      cloneG.fillStyle(0x312e81, 0.7).fillRect(-13, -14, 26, 28).fillCircle(0, -26, 13);
      this.tweens.add({ targets: cloneG, alpha: 0, duration: 380, ease: 'Quad.easeIn', onComplete: () => { if (cloneG?.scene) cloneG.destroy(); } });
      // Deal 8 damage to all enemies within 60px of clone
      for (const e of this._enemies) {
        if (!e.isAlive) continue;
        if (Math.hypot(e.container.x - cloneX, e.container.y - cloneY) < 60) {
          e.takeDamage(8, 0, 0);
          this._showDamageNumber(e.container.x, e.container.y - 20, 8, false, false);
        }
      }
    }
    audioManager.playSfx('pickup');
    this._updateHud();
  }

  _spawnDashGhosts() {
    for (let i = 0; i < DASH_GHOST_COUNT; i++) {
      // Capture position at the moment each ghost is "born" via delayedCall.
      // The stagger spreads the ghosts over the first half of the dash duration.
      this.time.delayedCall(i * DASH_GHOST_INTERVAL, () => {
        if (!this._dashActive && i > 0) return; // dash ended early — skip late ghosts
        const gx = this.player.x;
        const gy = this.player.y;
        const scaleX = this._playerContainer.scaleX;
        const scaleY = this._playerContainer.scaleY;

        // Draw a simplified silhouette matching the player's body shape
        const ghost = this.add.graphics().setDepth(9); // below player (depth 10)
        ghost.setPosition(gx, gy);
        ghost.setScale(scaleX, scaleY);

        // Silhouette: torso + head circles in the dash accent colour
        const col = 0xc4b5fd; // lavender — matches existing dash particle colour
        ghost.fillStyle(col, 0.55);
        ghost.fillRect(-13, -14, 26, 28); // body
        ghost.fillCircle(0, -26, 13);     // head

        // Alpha fade and destroy — ghost lifetime decreases for older copies so
        // the farthest-back ghost vanishes first, creating a natural trail taper.
        const lifetime = 160 - i * 22;
        this.tweens.add({
          targets: ghost,
          alpha: 0,
          duration: lifetime,
          ease: 'Quad.easeIn',
          onComplete: () => ghost.destroy(),
        });
      });
    }
  }

  _doAttack(mx, my, fromBuffer = false) {
    if (this._attackCooldown > 0 && !fromBuffer) return;
    const weapon = this.player.equipment.main_hand;
    if (!weapon) { this._showToast('Equip a weapon first!'); return; }

    this._attackCooldown = ATTACK_COOLDOWN * (this._worldState.atkCooldownMult || 1);
    audioManager.playSfx('attack');

    const worldX = mx + this.cameras.main.scrollX, worldY = my + this.cameras.main.scrollY;
    const px = this.player.x, py = this.player.y;
    const atkAngle = Math.atan2(worldY - py, worldX - px);
    this._drawSwingArc(px, py, atkAngle);

    // ── Attack lunge: brief velocity burst toward cursor for snappy game feel ──
    // Only lunge when not already dashing; lunge respects wall collisions via physics.
    if (!this._dashActive) {
      this._physBody.setAcceleration(0, 0);
      this._physBody.setVelocity(
        Math.cos(atkAngle) * ATTACK_LUNGE_SPEED,
        Math.sin(atkAngle) * ATTACK_LUNGE_SPEED,
      );
      // Restore normal drag-based deceleration after the lunge window
      this.time.delayedCall(ATTACK_LUNGE_DURATION, () => {
        if (!this._dashActive) this._physBody.setDrag(PLAYER_DRAG, PLAYER_DRAG);
      });
    }

    if (weapon.type === 'tool') this._tryMineWall(worldX, worldY, weapon);

    let dmg = Math.max(1, Math.round(((weapon.stats?.attack || 0) + this.player.baseAttack * 0.4) * this._damageMultiplier));
    // Berserker Core: damage scales with missing HP
    if (this._worldState.relics?.berserker) {
      const hpRatio = this.player.hp / this.player.effectiveMaxHp;
      if (hpRatio < 0.25) dmg = Math.round(dmg * 1.8);
      else if (hpRatio < 0.5) dmg = Math.round(dmg * 1.4);
    }
    let didHit = false;
    let heavyHit = false;

    for (const enemy of this._enemies) {
      if (!enemy.isAlive) continue;
      const ex = enemy.container.x, ey = enemy.container.y;
      const dist = Math.hypot(ex - px, ey - py);
      if (dist > SWING_RANGE) continue;

      let diff = Math.abs(Math.atan2(ey - py, ex - px) - atkAngle);
      if (diff > Math.PI) diff = Math.PI * 2 - diff;
      if (diff > (SWING_ARC_DEG * Math.PI) / 180) continue;

      enemy.takeDamage(dmg, ((ex - px)/dist) * KNOCKBACK_FORCE, ((ey - py)/dist) * KNOCKBACK_FORCE);
      this._showDamageNumber(ex, ey - 24, dmg, false, dmg >= 18);
      this._worldState.damageDealt = (this._worldState.damageDealt || 0) + dmg;
      // Vampiric lifesteal
      if (this._worldState.lifeSteal) {
        this.player.hp = Math.min(this.player.hp + this._worldState.lifeSteal, this.player.effectiveMaxHp);
      }
      // Doomshard: apply burn debuff on each melee hit (3 ticks, 4 dmg per tick, 600ms interval)
      if (this.player.equipment.main_hand?.id === 'sword_doomshard') {
        enemy._burning   = 3;
        enemy._burnTimer = 600;
      }
      audioManager.playSfx('hit');
      didHit = true;
      if (dmg >= 18) heavyHit = true;
    }

    if (didHit) {
      this.cameras.main.shake(heavyHit ? 180 : 120, heavyHit ? 0.009 : 0.005);
      // ── Hit-stop: freeze physics/time briefly on a heavy hit for impact weight ──
      // Sets time.timeScale and physics.world.timeScale to near-zero for
      // HIT_STOP_DURATION real milliseconds, then restores both.
      //
      // IMPORTANT: we use window.setTimeout (real wall-clock time) rather than
      // this.time.delayedCall because delayedCall is scaled by time.timeScale —
      // at scale 0.04 a 45ms delay would take ~1125ms of real time to fire.
      if (heavyHit && !this._hitStopActive) {
        this._hitStopActive = true;
        // Arcade physics uses inverse timeScale (higher = slower world)
        this.physics.world.timeScale = 1 / HIT_STOP_TIMESCALE;
        this.time.timeScale = HIT_STOP_TIMESCALE;
        window.setTimeout(() => {
          if (this.scene?.isActive()) {   // guard: scene may have shut down
            this.physics.world.timeScale = 1;
            this.time.timeScale = 1;
          }
          this._hitStopActive = false;
        }, HIT_STOP_DURATION);
      }
    }
  }

  _drawSwingArc(px, py, angle) {
    const arcRad = (SWING_ARC_DEG * Math.PI) / 180;
    const weapon = this.player.equipment.main_hand;
    const color = weapon?.particle_color ? Number(`0x${weapon.particle_color.replace('#', '')}`) : 0xffffff;
    const g = this.add.graphics().setDepth(11);
    g.fillStyle(color, 0.16).beginPath().moveTo(px, py).arc(px, py, SWING_RANGE, angle - arcRad, angle + arcRad, false).closePath().fillPath();
    this.tweens.add({ targets: g, alpha: 0, duration: 230, onComplete: () => g.destroy() });
  }

  _tryMineWall(worldX, worldY, tool) {
    const miningPower = tool.stats?.mining_power || 0;
    if (miningPower <= 0) return;
    const col = Math.floor(worldX / this._tileW);
    const row = Math.floor(worldY / this._tileH);
    const key = `${col},${row}`;
    const wall = this._wallTileMap.get(key);
    if (!wall) return;
    const dist = Math.hypot(worldX - this.player.x, worldY - this.player.y);
    if (dist > this._tileW * 1.7) return;
    if (!this.mapManager.carve(col, row)) return;

    if (wall.wallId && !this._worldState.brokenWalls.includes(wall.wallId)) {
      this._worldState.brokenWalls.push(wall.wallId);
    }
    // wall.body is a display-list-free Image (make.image add:false); remove its static
    // body from the broadphase first, then destroy the object so nothing lingers.
    this.physics.world.remove(wall.body.body);
    wall.body.destroy();
    this._wallTileMap.delete(key);
    this._drawFloorTile(col, row);
    // Redraw the merged wall graphics to exclude the newly broken tile
    this._rebuildWallGfx();
    this._saveGame();
    this._logEvent(`Wall broken with ${tool.name}`);
    this._showToast('Wall broken');
  }

  _playerTakeDamage(amount, attacker = null) {
    if (this._iframes > 0 || this._gameOver || this._worldState?.godMode) return;
    const mitigated = Math.max(1, amount - Math.floor(this.player.defense * 0.6));
    this.player.hp = Math.max(0, this.player.hp - mitigated);
    this._worldState.damageTaken = (this._worldState.damageTaken || 0) + mitigated;
    this._damageTakenThisFloor = (this._damageTakenThisFloor || 0) + mitigated;
    this._iframes = IFRAMES_DURATION;
    this._killStreak = 0; // reset combo on taking damage

    // Voidplate: reflect 15% of mitigated damage back to the attacker.
    // Uses the passed attacker reference; falls back to the nearest alive enemy.
    if (this.player.equipment.chest?.id === 'chest_voidplate') {
      const reflectDmg = Math.max(1, Math.round(mitigated * 0.15));
      let reflectTarget = attacker ?? null;
      if (!reflectTarget && this._enemies) {
        // Find nearest alive enemy without mutating enemy objects
        let bestDist = Infinity;
        for (const e of this._enemies) {
          if (!e.isAlive) continue;
          const d = Math.hypot(e.container.x - this.player.x, e.container.y - this.player.y);
          if (d < bestDist) { bestDist = d; reflectTarget = e; }
        }
      }
      if (reflectTarget?.isAlive) {
        reflectTarget.takeDamage(reflectDmg, 0, 0);
        this._showDamageNumber(reflectTarget.container.x, reflectTarget.container.y - 20, reflectDmg, false, false);
      }
    }
    
    audioManager.playSfx('hurt');
    this.cameras.main.flash(90, 255, 0, 0, true);
    this.cameras.main.shake(220, 0.011);
    this._showDamageNumber(this.player.x, this.player.y - 38, mitigated, true);
    this._updateHud();

    if (this.player.hp <= 0) {
      if (this._worldState.relics?.deathWard && !this._worldState.deathWardUsed) {
        this._worldState.deathWardUsed = true;
        this.player.hp = 1;
        this._showToast('Death Ward activated!');
        this.cameras.main.flash(200, 148, 0, 211, true);
      } else {
        this._triggerGameOver();
        return;
      }
    }
    this._saveGame();
  }

  _giveXp(amount) {
    const oldLevel = this.player.level;
    this.player.gainXp(amount);
    this._updateHud();
    
    if (this.player.level > oldLevel) {
      this._saveGame();
      this._showLevelUpChoice();
    }
  }

  _showLevelUpChoice() {
    this._levelingUp = true;
    audioManager.playSfx('levelup');
    this._logEvent(`Level ${this.player.level} reached`);
    
    const { width, height } = this.scale;
    const cx = width / 2, cy = height / 2;

    const overlay = this.add.graphics().setDepth(400).setScrollFactor(0);
    overlay.fillStyle(0x000000, 0.85).fillRect(0, 0, width, height);
    
    const title = this.add.text(cx, cy - 80, 'LEVEL UP!', { fontFamily: 'monospace', fontSize: '32px', color: '#fbbf24', stroke: '#000000', strokeThickness: 4 }).setOrigin(0.5).setDepth(401).setScrollFactor(0);
    const subtitle = this.add.text(cx, cy - 40, 'Choose a perk:', { fontFamily: 'monospace', fontSize: '14px', color: '#e2e8f0' }).setOrigin(0.5).setDepth(401).setScrollFactor(0);

    const PERK_POOL = [
      { text: '+8 Max HP',           apply: () => { this.player.maxHp += 8;  this.player.hp += 8; } },
      { text: '+15 Max HP',          apply: () => { this.player.maxHp += 15; this.player.hp = Math.min(this.player.hp + 15, this.player.maxHp); } },
      { text: '+3 Attack',           apply: () => { this.player.baseAttack += 3; } },
      { text: '+5 Attack',           apply: () => { this.player.baseAttack += 5; } },
      { text: '+2 Defense',          apply: () => { this.player.baseDefense += 2; } },
      { text: '+3 Defense',          apply: () => { this.player.baseDefense += 3; } },
      { text: '+30 Move Speed',      apply: () => { this.player.speed += 30; } },
      { text: '+25 Gold',            apply: () => { this.player.gold += 25; } },
      { text: 'Full Heal',           apply: () => { this.player.hp = this.player.effectiveMaxHp; } },
      { text: 'Vampiric (1 HP/hit)', apply: () => { this._worldState.lifeSteal = (this._worldState.lifeSteal || 0) + 1; } },
      { text: '+1 HP per kill',      apply: () => { this._worldState.hpPerKill = (this._worldState.hpPerKill || 0) + 1; } },
      { text: '-15% Atk Cooldown',   apply: () => { this._worldState.atkCooldownMult = (this._worldState.atkCooldownMult || 1) * 0.85; } },
    ];
    // Shuffle and pick 3 unique perks
    const choices = [...PERK_POOL].sort(() => Math.random() - 0.5).slice(0, 3);

    const btns = [];
    choices.forEach((c, i) => {
      const y = cy + i * 50;
      const btnBg = this.add.graphics().setDepth(401).setScrollFactor(0);
      
      const drawBtn = (hover) => {
        btnBg.clear().fillStyle(hover ? 0x6d28d9 : 0x7c3aed, 1).fillRoundedRect(cx - 100, y - 20, 200, 40, 8);
      };
      drawBtn(false);

      const txt = this.add.text(cx, y, c.text, { fontFamily: 'monospace', fontSize: '16px', color: '#ffffff' }).setOrigin(0.5).setDepth(402).setScrollFactor(0);
      txt.setInteractive({ useHandCursor: true })
         .on('pointerover', () => drawBtn(true))
         .on('pointerout', () => drawBtn(false))
         .on('pointerdown', () => {
           c.apply();
           overlay.destroy();
           btns.forEach(b => { b.bg.destroy(); b.txt.destroy(); });
           title.destroy();
           subtitle.destroy();
           this._levelingUp = false;
           this._updateHud();
           this._saveGame();
         });
         
      btns.push({ bg: btnBg, txt: txt });
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Visuals & Game Over
  // ─────────────────────────────────────────────────────────────────────────────
  _buildParticleTexture() {
    const key = '__spark__';
    if (this.textures.exists(key)) this.textures.remove(key);
    const tex = this.textures.createCanvas(key, 8, 8);
    const ctx = tex.getContext();
    const grad = ctx.createRadialGradient(4, 4, 0, 4, 4, 4);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = grad; ctx.fillRect(0, 0, 8, 8);
    tex.refresh();
  }

  _spawnPickupParticles(x, y, rarityHex) {
    const emitter = this.add.particles(x, y, '__spark__', {
      speed: { min: 55, max: 195 }, angle: { min: 0, max: 360 }, scale: { start: 0.9, end: 0 },
      alpha: { start: 1, end: 0 }, lifespan: 650, gravityY: 90, tint: rarityHex, emitting: false,
    }).setDepth(18);
    emitter.explode(22, x, y);
    this.time.delayedCall(750, () => emitter.destroy());
  }

  _spawnDeathParticles(x, y, type) {
    const col = type === 'slime'    ? 0x22cc44
              : type === 'mage'     ? 0xa855f7
              : type === 'archer'   ? 0xd97706
              : type === 'bomber'   ? 0xf97316
              : type === 'boss'     ? 0x7c3aed
              : type === 'tank'     ? 0x6b7280
              : type === 'spawner'  ? 0xa855f7
              : 0xe2e8f0;
    this._spawnPickupParticles(x, y, col);
    if (type === 'bomber' || type === 'boss') {
      // Extra burst
      this._spawnPickupParticles(x, y, 0xfbbf24);
    }
  }

  _showDamageNumber(x, y, amount, isPlayer, isCrit = false) {
    const txt = this.add.text(x, y, `${isPlayer ? '-' : ''}${amount}`, {
      fontFamily: 'monospace', fontSize: isPlayer ? '16px' : '13px', color: isPlayer ? '#ef4444' : (isCrit ? '#fbbf24' : '#fde68a'), stroke: '#000000', strokeThickness: 3
    }).setOrigin(0.5).setDepth(22);
    this.tweens.add({ targets: txt, y: y - 44, alpha: 0, duration: 870, onComplete: () => txt.destroy() });
  }

  _showFloatingReward(x, y, label, color) {
    const hexCol = '#' + color.toString(16).padStart(6, '0');
    const txt = this.add.text(x, y, label, {
      fontFamily: 'monospace', fontSize: '12px', color: hexCol, stroke: '#000000', strokeThickness: 3,
    }).setOrigin(0.5).setDepth(23);
    this.tweens.add({ targets: txt, y: y - 36, alpha: 0, duration: 1100, onComplete: () => txt.destroy() });
  }

  // ── Achievement system ────────────────────────────────────────────────────
  _checkAchievements() {
    const s = this._worldState;
    const p = this.player;
    const ACHIEVEMENTS = [
      { id: 'first_kill',   name: 'First Blood',      desc: 'Kill your first enemy',       check: () => s.kills >= 1 },
      { id: 'kill_10',      name: 'Slayer',            desc: 'Kill 10 enemies',              check: () => s.kills >= 10 },
      { id: 'kill_50',      name: 'Dungeon Veteran',   desc: 'Kill 50 enemies',              check: () => s.kills >= 50 },
      { id: 'floor_5',      name: 'Deep Diver',        desc: 'Reach floor 5',                check: () => this.dungeonLevel >= 5 },
      { id: 'floor_10',     name: 'Abyss Walker',      desc: 'Reach floor 10',               check: () => this.dungeonLevel >= 10 },
      { id: 'rich',         name: 'Hoarder',           desc: 'Accumulate 200 gold',          check: () => p.gold >= 200 },
      { id: 'level_5',      name: 'Seasoned',          desc: 'Reach player level 5',         check: () => p.level >= 5 },
      { id: 'boss_slayer',  name: 'Boss Slayer',       desc: 'Defeat a boss',                check: () => s.bossesKilled >= 1 },
      { id: 'glass_cannon', name: 'Glass Cannon',      desc: 'Deal 500 total damage',        check: () => s.damageDealt >= 500 },
      { id: 'survivor',     name: 'Untouchable',       desc: 'Clear a floor without damage', check: () => this._damageTakenThisFloor === 0 && s.kills >= 1 },
      { id: 'collector',    name: 'Collector',         desc: 'Find 10 items',                check: () => s.itemsFound >= 10 },
    ];
    const unlocked = s.unlockedAchievements || [];
    const newlyUnlocked = [];
    for (const ach of ACHIEVEMENTS) {
      if (unlocked.includes(ach.id)) continue;
      if (ach.check()) {
        unlocked.push(ach.id);
        newlyUnlocked.push(ach);
        try {
          const saved = JSON.parse(localStorage.getItem('dungeon_achievements') || '[]');
          if (!saved.includes(ach.id)) { saved.push(ach.id); localStorage.setItem('dungeon_achievements', JSON.stringify(saved)); }
        } catch {}
      }
    }
    s.unlockedAchievements = unlocked;
    // Queue toasts so they don't all stack at once
    newlyUnlocked.forEach((ach, i) => {
      this.time.delayedCall(i * 3400, () => { if (this.scene.isActive()) this._showAchievementToast(ach.name, ach.desc); });
    });
  }

  _showAchievementToast(name, desc) {
    const { width } = this.scale;
    const x = width - 14, y = 300;
    const bg = this.add.graphics().setDepth(500).setScrollFactor(0).setAlpha(0);
    bg.fillStyle(0x0f172a, 0.95).fillRoundedRect(x - 224, y - 32, 220, 60, 10);
    bg.lineStyle(2, 0xf59e0b, 1).strokeRoundedRect(x - 224, y - 32, 220, 60, 10);
    const titleTxt = this.add.text(x - 114, y - 18, `[ACH] ${name}`, {
      fontFamily: 'monospace', fontSize: '13px', color: '#f59e0b',
    }).setOrigin(0.5, 0).setDepth(501).setScrollFactor(0).setAlpha(0);
    const descTxt = this.add.text(x - 114, y + 4, desc, {
      fontFamily: 'monospace', fontSize: '10px', color: '#94a3b8',
    }).setOrigin(0.5, 0).setDepth(501).setScrollFactor(0).setAlpha(0);
    this.tweens.add({ targets: [bg, titleTxt, descTxt], alpha: 1, duration: 300 });
    this.time.delayedCall(2800, () => {
      this.tweens.add({ targets: [bg, titleTxt, descTxt], alpha: 0, duration: 400, onComplete: () => {
        try { bg.destroy(); titleTxt.destroy(); descTxt.destroy(); } catch {}
      }});
    });
  }

  _spawnWorldItem(x, y, itemDef) {
    if (this._isDuplicatePickup(itemDef)) return;
    const col = RARITY_COLOR[itemDef.rarity] ?? RARITY_COLOR.common;
    const iconKey = this.assetManager.ensureItemTexture(itemDef, 28);
    const g = this.add.graphics().setDepth(6).fillStyle(col, 0.1).fillCircle(x, y, 22).fillStyle(col, 0.45).fillCircle(x, y, 9).fillStyle(0xffffff, 0.85).fillCircle(x, y, 4);
    const icon = this.add.image(x, y, iconKey).setDepth(7).setDisplaySize(18, 18);
    const label = this.add.text(x, y - 20, itemDef.name, { fontFamily: 'monospace', fontSize: '9px', color: '#' + col.toString(16).padStart(6, '0'), stroke: '#000000', strokeThickness: 2 }).setOrigin(0.5).setDepth(32);
    this.tweens.add({ targets: label, y: y - 30, duration: 1100, yoyo: true, repeat: -1 });
    this.tweens.add({ targets: g, alpha: { from: 0.7, to: 1 }, duration: 700, yoyo: true, repeat: -1 });
    this._worldItems.push({ x, y, itemDef, g, icon, label, collected: false });
  }

  _collectWorldItem(wi) {
    // Reject before destroying so item stays on the ground
    if (wi.itemDef.type === 'spell' && !this._worldState.canUseSpells) {
      this._showToast('Only Mages can use spells');
      return;
    }
    // Passive items: absorbed immediately, no hotbar slot needed
    if (wi.itemDef.type === 'passive') {
      wi.collected = true;
      this.tweens.killTweensOf(wi.g); this.tweens.killTweensOf(wi.label);
      wi.g.destroy(); wi.icon?.destroy(); wi.label.destroy();
      this._applyPassiveItem(wi.itemDef);
      this._worldState.itemsFound = (this._worldState.itemsFound || 0) + 1;
      this._spawnPickupParticles(wi.x, wi.y, RARITY_COLOR[wi.itemDef.rarity] || RARITY_COLOR.uncommon);
      audioManager.playSfx('pickup');
      this._logEvent(`Absorbed ${wi.itemDef.name}`);
      this._showToast(`Absorbed: ${wi.itemDef.name}!`);
      this._updateHud();
      this._checkAchievements();
      return;
    }
    // Block picking up weaker slotted gear before destroying graphics
    if (wi.itemDef.slot && this._hasBetterItemFor(wi.itemDef)) {
      this._showToast('Already have better gear equipped');
      return;
    }
    if (this._isDuplicatePickup(wi.itemDef)) {
      const msg = wi.itemDef.type === 'spell' ? `Already know ${wi.itemDef.name}` : `Already carrying ${wi.itemDef.name}`;
      this._showToast(msg);
      return;
    }
    wi.collected = true;
    this.tweens.killTweensOf(wi.g); this.tweens.killTweensOf(wi.label);
    wi.g.destroy(); wi.icon?.destroy(); wi.label.destroy();
    if (!this.player.addItem(wi.itemDef, 1)) return this._showToast('Inventory full!');
    const emptySlot = this.player.hotbar.findIndex(s => s === null);
    if (emptySlot !== -1) this.player.setHotbar(emptySlot, wi.itemDef.id);
    this._worldState.itemsFound = (this._worldState.itemsFound || 0) + 1;
    this._refreshHotbar();
    this._saveGame();
    this._spawnPickupParticles(wi.x, wi.y, RARITY_COLOR[wi.itemDef.rarity] || RARITY_COLOR.common);
    audioManager.playSfx('pickup');
    this._logEvent(`Picked up ${wi.itemDef.name}`);
    this._showToast(`Picked up: ${wi.itemDef.name}`);
    this._checkAchievements();
  }

  _applyPassiveItem(itemDef) {
    const s = itemDef.stats || {};
    if (s.max_hp)  { this.player.maxHp += s.max_hp;  this.player.hp += s.max_hp; }
    if (s.attack)  { this.player.baseAttack  += s.attack; }
    if (s.defense) { this.player.baseDefense += s.defense; }
    if (s.speed)   { this.player.speed       += s.speed; }
    if (s.gold)    { this.player.gold        += s.gold; }
    // Track absorbed rings so they show in HUD and on player sprite
    if (!this._worldState.absorbedPassives) this._worldState.absorbedPassives = [];
    this._worldState.absorbedPassives.push(itemDef.name);

    // ── Legendary relic effect hooks ──────────────────────────────────────────
    if (!this._worldState.relics) this._worldState.relics = {};
    if (itemDef.id === 'relic_berserker_core') this._worldState.relics.berserker = true;
    if (itemDef.id === 'relic_storm_crown')    this._worldState.relics.stormCrown = true;
    if (itemDef.id === 'relic_shadow_step')    this._worldState.relics.shadowStep = true;
    if (itemDef.id === 'relic_void_heart')     this._worldState.relics.voidHeart  = true;
    if (itemDef.id === 'relic_death_ward')     { this._worldState.relics.deathWard = true; this._worldState.deathWardUsed = false; }
    if (itemDef.id === 'relic_blood_pact')     this._worldState.relics.bloodPact  = true;

    this._updateHud();
    this._redrawWeapon(); // refresh ring dots on player neck
  }

  _showToast(msg) {
    if (this._levelIntroActive) return;
    this._toastText.setPosition(this.scale.width / 2, this.scale.height - this._hotbarTotalH() - 20).setText(msg).setAlpha(1);
    // Cancel any pending clear so rapid toasts don't expire prematurely.
    if (this._toastClearEvent) { this._toastClearEvent.remove(false); this._toastClearEvent = null; }
    this._toastClearEvent = this.time.delayedCall(2200, () => {
      this._toastText.setAlpha(0);
      this._toastClearEvent = null;
    });
  }

  _openLevelIntro() {
    const { width, height } = this.scale;
    const cx = width / 2;
    const cy = height / 2 + 28;
    this._levelIntroActive = true;
    this._levelIntroEndsAt = this.time.now + LEVEL_INTRO_MS;

    const spellSummary = ['Fireball [F]'];
    if (this._playerHasSpell('spell_lightning_strike')) spellSummary.push('Lightning Strike [R]');
    if (this._playerHasSpell('spell_void_ball')) spellSummary.push('Void Ball [E]');

    const loadout = [
      `Weapon: ${this.player.equipment.main_hand?.name ?? 'None'}`,
      `Chest: ${this.player.equipment.chest?.name ?? 'None'}`,
      `Head: ${this.player.equipment.head?.name ?? 'None'}`,
      `Spells: ${spellSummary.join(', ')}`,
      `Hotbar: ${this.player.hotbar.map(id => this.itemRegistry.get(id)?.name || 'Empty').join(' | ')}`,
    ].join('\n');

    const overlay = this.add.graphics().setDepth(450).setScrollFactor(0);
    overlay.fillStyle(0x000000, 0.94).fillRect(0, 0, width, height);
    const panel = this.add.graphics().setDepth(451).setScrollFactor(0);
    panel.fillStyle(0x070b16, 0.98).fillRoundedRect(cx - 270, cy - 168, 540, 336, 14).lineStyle(2, 0x7c3aed, 0.9).strokeRoundedRect(cx - 270, cy - 168, 540, 336, 14);
    const THEME_NAMES = ['Stone Dungeon','Stone Dungeon','Stone Dungeon','Overgrown Cave','Overgrown Cave','Overgrown Cave','Lava Depths','Lava Depths','Lava Depths','Void Realm'];
    const themeName = THEME_NAMES[Math.min(this.dungeonLevel - 1, THEME_NAMES.length - 1)] || 'Void Realm';
    const themeColors = ['#a78bfa','#a78bfa','#a78bfa','#4ade80','#4ade80','#4ade80','#f87171','#f87171','#f87171','#c4b5fd'];
    const themeCol = themeColors[Math.min(this.dungeonLevel - 1, themeColors.length - 1)] || '#c4b5fd';
    const title = this.add.text(cx, cy - 132, `FLOOR ${this.dungeonLevel}`, { fontFamily: 'monospace', fontSize: '30px', color: '#f8fafc' }).setOrigin(0.5).setDepth(452).setScrollFactor(0);
    const themeText = this.add.text(cx, cy - 98, themeName, { fontFamily: 'monospace', fontSize: '13px', color: themeCol, letterSpacing: 4 }).setOrigin(0.5).setDepth(452).setScrollFactor(0);
    const sub = this.add.text(cx, cy - 76, 'Look over your loadout before the floor goes live.', { fontFamily: 'monospace', fontSize: '12px', color: '#c4b5fd' }).setOrigin(0.5).setDepth(452).setScrollFactor(0);
    const body = this.add.text(cx, cy - 8, loadout, {
      fontFamily: 'monospace',
      fontSize: '14px',
      color: '#cbd5e1',
      align: 'center',
      lineSpacing: 8,
      wordWrap: { width: 470 },
    }).setOrigin(0.5).setDepth(452).setScrollFactor(0);
    const timerText = this.add.text(cx, cy + 108, '', { fontFamily: 'monospace', fontSize: '16px', color: '#fde68a' }).setOrigin(0.5).setDepth(452).setScrollFactor(0);
    const skipBg = this.add.graphics().setDepth(452).setScrollFactor(0);
    const drawSkip = (hover) => skipBg.clear().fillStyle(hover ? 0x6d28d9 : 0x312e81, 1).fillRoundedRect(cx - 90, cy + 130, 180, 40, 8);
    drawSkip(false);
    const skipLabel = this.add.text(cx, cy + 150, 'Skip Countdown', { fontFamily: 'monospace', fontSize: '15px', color: '#ffffff' }).setOrigin(0.5).setDepth(453).setScrollFactor(0);
    skipLabel.setInteractive({ useHandCursor: true })
      .on('pointerover', () => drawSkip(true))
      .on('pointerout', () => drawSkip(false))
      .on('pointerdown', () => this._closeLevelIntro());

    this._levelIntroUi = [overlay, panel, title, themeText, sub, body, timerText, skipBg, skipLabel];
    this._levelIntroTimerText = timerText;
    this._hideTooltip();
    this._toastText.setAlpha(0);
    this._updateLevelIntroTimer();
  }

  _updateLevelIntroTimer() {
    if (!this._levelIntroActive || !this._levelIntroTimerText) return;
    const remainingMs = Math.max(0, this._levelIntroEndsAt - this.time.now);
    const seconds = Math.ceil(remainingMs / 1000);
    this._levelIntroTimerText.setText(`Starting in ${seconds}s`);
    if (remainingMs <= 0) this._closeLevelIntro();
  }

  _closeLevelIntro() {
    if (!this._levelIntroActive) return;
    this._levelIntroActive = false;
    this._levelIntroEndsAt = 0;
    for (const node of this._levelIntroUi || []) node?.destroy?.();
    this._levelIntroUi = [];
    this._levelIntroTimerText = null;
  }

  _playLootReveal(x, y, itemDef, slotIndex) {
    const key = this.assetManager.ensureItemTexture(itemDef, 32);
    const beam = this.add.graphics().setDepth(40);
    beam.fillStyle(0xffffff, 0.18).fillRect(x - 8, y - 64, 16, 60);
    const icon = this.add.image(x, y - 22, key).setDisplaySize(26, 26).setDepth(41);
    const target = this._hotbarSlotData?.[Math.max(0, slotIndex)] || this._hotbarSlotData?.[0];
    this.tweens.add({
      targets: icon,
      y: y - 56,
      duration: 180,
      yoyo: true,
      onComplete: () => {
        this.tweens.add({
          targets: icon,
          x: target.sx + SLOT_SIZE / 2,
          y: target.sy + SLOT_SIZE / 2 - 10,
          scaleX: 0.5,
          scaleY: 0.5,
          alpha: 0.2,
          duration: 320,
          onComplete: () => icon.destroy(),
        });
      },
    });
    this.tweens.add({ targets: beam, alpha: 0, duration: 520, onComplete: () => beam.destroy() });
  }

  _triggerGameOver() {
    if (this._gameOver) return;
    this._gameOver = true;
    this._autosaveEvent?.remove(false);
    this._dustEvent?.remove(false);
    for (const e of this._enemies) if (!e.dead && e._physBody) e._physBody.setVelocity(0, 0);
    this._physBody.setVelocity(0, 0).setAcceleration(0, 0);
    this.cameras.main.flash(600, 220, 0, 0, false);
    const bestScore = this._saveHighScore();
    
    // Clear save on death
    removeSave();
    
    this.time.delayedCall(700, () => {
      const { width, height } = this.scale;
      const cx = width / 2, cy = height / 2;
      this.add.graphics().setDepth(300).setScrollFactor(0).fillStyle(0x000000, 0.82).fillRect(0, 0, width, height);

      const s = this._worldState || {};
      const runMs   = Date.now() - (s.runStartTime || Date.now());
      const runMins = Math.floor(runMs / 60000);
      const runSecs = Math.floor((runMs % 60000) / 1000);
      const className = s.classId ? (s.classId.charAt(0).toUpperCase() + s.classId.slice(1)) : 'Hero';

      const pW = 400, pH = 360, pX = cx - pW/2, pY = cy - pH/2;
      this.add.graphics().setDepth(301).setScrollFactor(0)
        .fillStyle(0x080817, 0.98).fillRoundedRect(pX, pY, pW, pH, 16)
        .lineStyle(2, 0xdc2626, 0.85).strokeRoundedRect(pX, pY, pW, pH, 16);

      this.add.text(cx, pY + 38, 'GAME OVER', {
        fontFamily: 'monospace', fontSize: '34px', color: '#dc2626', stroke: '#000000', strokeThickness: 4,
      }).setOrigin(0.5).setDepth(302).setScrollFactor(0);

      // Class line
      this.add.text(cx, pY + 82, className, {
        fontFamily: 'monospace', fontSize: '15px', color: '#a78bfa',
      }).setOrigin(0.5).setDepth(302).setScrollFactor(0);

      // Stats block
      const stats = [
        [`Floor`,    `${this.dungeonLevel}`],
        [`Level`,    `${this.player.level}`],
        [`Gold`,     `${this.player.gold}`],
        [`Kills`,    `${s.kills || 0}`],
        [`Bosses`,   `${s.bossesKilled || 0}`],
        [`Dmg dealt`,`${s.damageDealt || 0}`],
        [`Dmg taken`,`${s.damageTaken || 0}`],
        [`Items`,    `${s.itemsFound || 0}`],
        [`Run time`, `${runMins}m ${runSecs}s`],
      ];
      stats.forEach(([label, val], i) => {
        const row = pY + 116 + Math.floor(i / 2) * 26;
        const col = i % 2 === 0 ? pX + 28 : cx + 10;
        this.add.text(col, row, label, { fontFamily: 'monospace', fontSize: '11px', color: '#64748b' }).setDepth(302).setScrollFactor(0);
        this.add.text(col + 80, row, val, { fontFamily: 'monospace', fontSize: '11px', color: '#f1f5f9' }).setDepth(302).setScrollFactor(0);
      });

      // Best run
      if (bestScore) {
        this.add.text(cx, pY + pH - 106, `Best: Floor ${bestScore.floor}  Lv.${bestScore.level}  ${bestScore.kills || 0} kills`, {
          fontFamily: 'monospace', fontSize: '11px', color: '#fbbf24',
        }).setOrigin(0.5).setDepth(302).setScrollFactor(0);
      }

      const btnW = 160, btnH = 44, btnX = cx - btnW/2, btnY = pY + pH - 62;
      const btnBg = this.add.graphics().setDepth(302).setScrollFactor(0);
      const drawBtn = (hover) => { btnBg.clear().fillStyle(hover ? 0x6d28d9 : 0x7c3aed, 1).fillRoundedRect(btnX, btnY, btnW, btnH, 9); };
      drawBtn(false);
      const btnTxt = this.add.text(cx, btnY + btnH/2, 'Main Menu', { fontFamily: 'monospace', fontSize: '16px', color: '#ffffff' }).setOrigin(0.5).setDepth(303).setScrollFactor(0);
      btnTxt.setInteractive({ useHandCursor: true }).on('pointerover', () => drawBtn(true)).on('pointerout', () => drawBtn(false)).on('pointerdown', () => this.scene.start('MenuScene'));
    });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Init
// ─────────────────────────────────────────────────────────────────────────────
const config = {
  type: Phaser.AUTO,
  parent: 'game-container',
  width: 1280,
  height: 720,
  backgroundColor: '#0d0d1a',
  pixelArt: true,
  roundPixels: true,
  physics: { default: 'arcade', arcade: { gravity: { y: 0 }, debug: false, fps: 60 } },
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [BootScene, MenuScene, PartyScene, InstructionsScene, ClassSelectScene, MainScene],
};

new Phaser.Game(config);
