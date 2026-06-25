/**
 * enemy.js — Enemy entities for the dungeon crawler.
 *
 * Types:
 *   slime    — small, slow, low HP, low damage
 *   skeleton — taller, faster, higher HP, higher damage
 *   archer   — ranged, keeps distance, fires arrows
 *   mage     — ranged caster, keeps distance, fires magic bolts
 *   bomber   — rushes player, primes, then explodes on contact
 *   tank     — slow, very high HP, heavy armor, AoE shockwave on attack
 *   spawner  — stationary obelisk, periodically spawns slimes until killed
 *   boss     — large, high HP, two phases (melee + ranged spread)
 *
 * AI states (unified state machine for slime, skeleton, archer, mage, tank):
 *   IDLE     — wanders randomly; transitions to ALERT when player enters aggroRadius
 *   ALERT    — brief "!" freeze (480ms) before engaging — gives player reaction time
 *   CHASE    — moves toward player
 *   ATTACK   — in attack range, executes attack pattern on cooldown
 *   RETREAT  — HP < 30%, flees away briefly before re-engaging (not tank/boss)
 *   STUNNED  — brief stagger after a heavy hit (dmg >= 18)
 *
 *   (archer-specific) BACKPEDAL — backs away when player is within minRange
 *   (mage-specific)   STRAFE_LEFT / STRAFE_RIGHT — circles the player while in range
 *   (bomber-specific) priming   — countdown before explosion (own internal state)
 *   Boss and spawner retain their own dedicated AI methods.
 *
 * Physics: each enemy gets a Phaser Arcade physics body attached to its
 * Container so it collides with the same _wallGroup as the player.
 *
 * The scene is responsible for calling enemy.update(dt, px, py) each frame
 * and for adding wall colliders after construction.
 *
 * Depth: enemies sit at depth 8 (below player at depth 10, above floor at 0–2).
 */

// ─────────────────────────────────────────────────────────────────────────────
// AI State constants — shared across all enemy types.
// Bomber and spawner use their own internal states; these apply to melee,
// archer, mage, tank, and boss types.
// ─────────────────────────────────────────────────────────────────────────────
const AI = Object.freeze({
  IDLE:    'idle',     // wandering randomly within spawn area
  ALERT:   'alert',   // spotted the player — brief "!" pause before engaging
  CHASE:   'chase',   // actively moving toward the player
  ATTACK:  'attack',  // in attack range — executing attack pattern
  RETREAT: 'retreat', // HP < RETREAT_HP_THRESHOLD — backing away to re-evaluate
  STUNNED: 'stunned', // brief stagger after taking a hit (used for heavy hits only)
  // Ranged-specific sub-states (kept as strings for backwards compat):
  BACKPEDAL:    'backpedal',
  STRAFE_LEFT:  'strafeLeft',
  STRAFE_RIGHT: 'strafeRight',
  WANDER:       'wander',
});

// Fraction of maxHp below which an enemy enters RETREAT state.
// Boss and tank ignore this — they are designed as aggressive brutes.
const RETREAT_HP_THRESHOLD = 0.30;

// How long (ms) the "!" ALERT state lasts before the enemy starts chasing.
const ALERT_DURATION = 480;

// How long (ms) the RETREAT state lasts before re-engaging.
const RETREAT_DURATION = 1400;

// How long (ms) a heavy hit stuns the enemy (≥18 dmg, matching the heavy-hit
// threshold in game.js so hit-stop and stun are synced).
const STUN_DURATION_HEAVY = 320;

// ── Drop tables ────────────────────────────────────────────────────────────
// Each entry: { id: itemId, weight: number }. Higher weight = more likely.
// Weights are relative — they are NOT probabilities.
const DROP_TABLES = {
  slime:    [
    { id: 'potion_health', weight: 60 },
    { id: 'ring_vitality', weight: 15 },
    { id: 'sword_iron',    weight: 5  },
  ],
  skeleton: [
    { id: 'sword_iron',           weight: 30 },
    { id: 'sword_warden',         weight: 15 },
    { id: 'potion_health',        weight: 25 },
    { id: 'hood_leather',         weight: 20 },
    { id: 'ring_power',           weight: 10 },
  ],
  archer: [
    { id: 'potion_health',        weight: 35 },
    { id: 'ring_swiftness',       weight: 25 },
    { id: 'chestplate_leather',   weight: 20 },
    { id: 'sword_warden',         weight: 10 },
    { id: 'pickaxe_bronze',       weight: 10 },
  ],
  mage: [
    { id: 'spell_lightning_strike', weight: 20 },
    { id: 'spell_void_ball',        weight: 20 },
    { id: 'ring_power',             weight: 30 },
    { id: 'potion_health',          weight: 20 },
    { id: 'ring_fortune',           weight: 10 },
  ],
  bomber: [
    { id: 'potion_health',        weight: 50 },
    { id: 'ring_resistance',      weight: 30 },
    { id: 'chestplate_iron',      weight: 20 },
  ],
  tank: [
    { id: 'chestplate_iron',      weight: 35 },
    { id: 'helmet_iron',          weight: 30 },
    { id: 'ring_vitality',        weight: 20 },
    { id: 'sword_warden',         weight: 15 },
  ],
  spawner: [
    { id: 'ring_power',           weight: 25 },
    { id: 'ring_fortune',         weight: 25 },
    { id: 'ring_resistance',      weight: 25 },
    { id: 'potion_health',        weight: 25 },
  ],
  boss: [
    { id: 'sword_moonsteel',      weight: 15 },
    { id: 'chest_voidplate',      weight: 15 },
    { id: 'sword_doomshard',      weight: 15 },
    { id: 'ring_vitality',        weight: 20 },
    { id: 'ring_power',           weight: 20 },
    { id: 'potion_health',        weight: 15 },
  ],
};

/**
 * Roll a random item id from the drop table for the given enemy type.
 * Returns null if no drop occurs (respects per-type drop chance).
 * @param {string} type  — enemy type key
 * @param {function():number} rng — returns [0,1)
 * @returns {string|null}
 */
function rollDrop(type, rng) {
  const table = DROP_TABLES[type];
  if (!table || table.length === 0) return null;
  // Boss almost always drops; spawner/elite more often; common enemies ~45%.
  const dropChance = type === 'boss' ? 0.95 : type === 'spawner' ? 0.60 : 0.45;
  if (rng() > dropChance) return null;
  const totalWeight = table.reduce((s, e) => s + e.weight, 0);
  let r = rng() * totalWeight;
  for (const entry of table) {
    r -= entry.weight;
    if (r <= 0) return entry.id;
  }
  return table[table.length - 1].id;
}

export class Enemy {
  /**
   * @param {Phaser.Scene}                                       scene
   * @param {number}                                             worldX
   * @param {number}                                             worldY
   * @param {'slime'|'skeleton'|'archer'|'mage'|'bomber'|'boss'} type
   */
  constructor(scene, worldX, worldY, type) {
    /** @type {'slime'|'skeleton'|'archer'|'mage'|'bomber'|'tank'|'spawner'|'boss'} */
    this.scene = scene;
    this.type  = type;
    this.dead  = false;
    this._deathHandled = false;

    // ── Stats per type ───────────────────────────────────────────────────────
    if (type === 'slime') {
      this.maxHp          = 30;
      this.damage         = 8;
      this.speed          = 62;
      this.aggroRadius    = 160;
      this.attackRange    = 38;
      this.attackCooldown = 1100;
      this.xpReward       = 15;
    } else if (type === 'skeleton') {
      this.maxHp          = 55;
      this.damage         = 15;
      this.speed          = 95;
      this.aggroRadius    = 230;
      this.attackRange    = 52;
      this.attackCooldown = 900;
      this.xpReward       = 28;
    } else if (type === 'archer') {
      this.maxHp          = 40;
      this.damage         = 14;   // arrow damage (handled by game.js)
      this.speed          = 55;
      this.aggroRadius    = 280;
      this.attackRange    = 210;  // fires when dist <= this
      this.minRange       = 95;   // backs away when dist < this
      this.attackCooldown = 2100;
      this.xpReward       = 32;
    } else if (type === 'mage') {
      this.maxHp          = 50;
      this.damage         = 20;   // bolt damage (handled by game.js)
      this.speed          = 58;
      this.aggroRadius    = 340;
      this.attackRange    = 230;  // fires when dist <= this
      this.minRange       = 90;   // backs away when dist < this
      this.attackCooldown = 2200;
      this.xpReward       = 40;
      this._charging      = 0;    // ms remaining in charge-up visual (not blocking)
    } else if (type === 'bomber') {
      this.maxHp          = 22;
      this.damage         = 42;   // explosion damage (handled by game.js)
      this.speed          = 128;
      this.aggroRadius    = 220;
      this.attackRange    = 46;
      this.attackCooldown = 0;
      this.xpReward       = 35;
      this._priming       = false;
      this._primeTimer    = 0;
      this._primeFlash    = 0;
    } else if (type === 'tank') {
      this.maxHp          = 200;
      this.damage         = 28;
      this.speed          = 44;
      this.aggroRadius    = 200;
      this.attackRange    = 62;
      this.attackCooldown = 1900;
      this.xpReward       = 60;
      this._shockwaveReady = false;
    } else if (type === 'spawner') {
      this.maxHp          = 75;
      this.damage         = 0;
      this.speed          = 0;
      this.aggroRadius    = 0;
      this.attackRange    = 0;
      this.attackCooldown = 0;
      this.xpReward       = 50;
      this._spawnTimer    = 4500 + Math.random() * 1500;
      this._wantsSpawn    = false;
    } else {                      // boss
      this.maxHp          = 320;
      this.damage         = 22;
      this.speed          = 68;
      this.aggroRadius    = 360;
      this.attackRange    = 65;
      this.attackCooldown = 1300;
      this.xpReward       = 200;
      this._phase         = 1;
      this._shootTimer    = 3200;
      this._shootAngles   = [];   // set by update before wantsShoot fires
    }
    this.hp = this.maxHp;

    // ── AI state ─────────────────────────────────────────────────────────────
    // Mage starts in a strafe state so it doesn't charge straight at the player.
    this._state        = type === 'mage' ? (Math.random() > 0.5 ? AI.STRAFE_LEFT : AI.STRAFE_RIGHT) : AI.IDLE;
    this._wanderTimer  = 600 + Math.random() * 800;
    this._wanderVx     = 0;
    this._wanderVy     = 0;
    this._attackTimer  = Math.random() * 400; // stagger so all enemies don't attack together
    this._alertTimer   = 0;   // counts down while in ALERT state
    this._retreatTimer = 0;   // counts down while in RETREAT state
    this._stunTimer    = 0;   // counts down while in STUNNED state
    this._hasAggro     = false; // true once this enemy has ever seen the player
    this._wantsAttack  = false;
    this._wantsShoot   = false;
    this._wantsExplode = false;
    if (type !== 'spawner') this._wantsSpawn = false;

    // ── Hit/knockback state ──────────────────────────────────────────────────
    this._knockbackTimer = 0;

    // ── Burn state (applied by sword_doomshard) ───────────────────────────────
    // _burning: ticks remaining (0 = not burning). _burnTimer: ms until next tick.
    this._burning   = 0;
    this._burnTimer = 0;

    // ── Flash state (red when damaged) ──────────────────────────────────────
    this._flashTimer = 0;

    // ── Draw-cache state ──────────────────────────────────────────────────────
    // For non-animated enemy types the body only needs a redraw when the flash
    // state changes. Caching the last drawn flash value skips the 8-12 Graphics
    // calls that would otherwise fire every frame for every enemy.
    this._lastFlash  = null; // null forces an initial update-path redraw (false !== null)
    this._hpDirty    = true;      // hp bar always drawn on first frame

    // ── Visuals ──────────────────────────────────────────────────────────────
    this.container = scene.add.container(worldX, worldY).setDepth(8);
    this._bodyGfx  = scene.add.graphics().setName('body');
    this._hpBarGfx = scene.add.graphics().setName('hpbar');
    this.container.add([this._bodyGfx, this._hpBarGfx]);
    this._draw(false);
    this._drawHpBar();

    // ── Physics ──────────────────────────────────────────────────────────────
    scene.physics.add.existing(this.container);
    /** @type {Phaser.Physics.Arcade.Body} */
    this._physBody = this.container.body;
    this._physBody.setDrag(200, 200).setMaxVelocity(500, 500);

    if (type === 'slime') {
      this._physBody.setSize(30, 22).setOffset(-15, -11);
    } else if (type === 'archer' || type === 'mage') {
      this._physBody.setSize(22, 30).setOffset(-11, -15);
    } else if (type === 'bomber') {
      this._physBody.setSize(26, 26).setOffset(-13, -13);
    } else if (type === 'boss') {
      this._physBody.setSize(48, 56).setOffset(-24, -28);
    } else if (type === 'tank') {
      this._physBody.setSize(36, 44).setOffset(-18, -22);
    } else if (type === 'spawner') {
      this._physBody.setSize(22, 30).setOffset(-11, -15);
      this._physBody.setImmovable(true);
    } else {
      this._physBody.setSize(24, 32).setOffset(-12, -16);
    }
  }

  // ── Public API ─────────────────────────────────────────────────────────────

  get isAlive() { return !this.dead; }

  get wantsAttack()  { return this._wantsAttack; }
  get wantsShoot()   { return this._wantsShoot; }
  get wantsExplode() { return this._wantsExplode; }
  get wantsSpawn()   { return this._wantsSpawn; }

  /**
   * Called once per frame by the scene.
   * @param {number} dt      — delta time in ms
   * @param {Array<{x:number,y:number}>} targets — all player positions; enemy picks nearest
   */
  update(dt, targets) {
    if (this.dead) return;

    // Target-lock: store index so we always use the current frame's position
    const arr = Array.isArray(targets) ? targets : [{ x: targets, y: arguments[2] }];
    let nearestIdx = 0, nearestDist = Infinity;
    for (let i = 0; i < arr.length; i++) {
      const d = Math.hypot(arr[i].x - this.container.x, arr[i].y - this.container.y);
      if (d < nearestDist) { nearestDist = d; nearestIdx = i; }
    }
    if (this._lockedTargetIdx == null || this._lockedTargetIdx >= arr.length) {
      this._lockedTargetIdx = nearestIdx;
    } else {
      const lockedDist = Math.hypot(
        arr[this._lockedTargetIdx].x - this.container.x,
        arr[this._lockedTargetIdx].y - this.container.y,
      );
      if (nearestDist < lockedDist * 0.65) this._lockedTargetIdx = nearestIdx;
    }
    const playerX = arr[this._lockedTargetIdx].x;
    const playerY = arr[this._lockedTargetIdx].y;
    this._wantsAttack  = false;
    this._wantsShoot   = false;
    this._wantsExplode = false;
    this._wantsSpawn   = false;

    // ── Burn tick (sword_doomshard) ───────────────────────────────────────────
    // Each tick fires every 600ms for _burning ticks (default 3), dealing 4 dmg.
    if (this._burning > 0) {
      this._burnTimer -= dt;
      if (this._burnTimer <= 0) {
        this._burning--;
        this._burnTimer = 600;
        this.takeDamage(4, 0, 0);
      }
    }

    // ── Flash decay ──────────────────────────────────────────────────────────
    if (this._flashTimer > 0) {
      this._flashTimer -= dt;
      if (this._flashTimer <= 0) {
        this._flashTimer = 0;
        this._lastFlash  = false; // sync cache so update()'s check doesn't double-draw
        this._draw(false);
      }
    }

    // ── Knockback: let physics drag handle deceleration ──────────────────────
    // When in knockback, skip all AI steering — physics drag will slow the enemy
    // naturally. The squash/drawHpBar calls at the bottom of update() still run.
    const inKnockback = this._knockbackTimer > 0;
    if (inKnockback) this._knockbackTimer -= dt;

    // ── Cross-type state machine ──────────────────────────────────────────────
    // Bomber and spawner have specialised logic that doesn't benefit from the
    // full state machine, so they keep their own update methods.
    // Boss uses its own phase system which overrides the standard machine.
    // All other types (melee: slime, skeleton; ranged: archer, mage; tank)
    // pass through the unified ALERT / RETREAT / STUNNED layers first, then
    // delegate to their type-specific method for CHASE / ATTACK / backpedal etc.
    if (!inKnockback) {
      if (this.type === 'bomber') {
        this._updateBomberAI(dt, playerX, playerY);
      } else if (this.type === 'spawner') {
        this._updateSpawnerAI(dt);
      } else if (this.type === 'boss') {
        this._updateBossAI(dt, playerX, playerY);
      } else {
        this._updateStateMachine(dt, playerX, playerY);
      }
    }

    // Flip sprite left/right (spawner is stationary — no flip)
    if (this.type !== 'spawner') {
      const vx = this._physBody.velocity.x;
      if (vx < -8)  this.container.setScale(-1, 1);
      if (vx >  8)  this.container.setScale( 1, 1);
    }
    const motion = Math.min(1, Math.hypot(this._physBody.velocity.x, this._physBody.velocity.y) / Math.max(this.speed, 1));
    const sx = (this.container.scaleX < 0 ? -1 : 1) * (1 + motion * 0.04);
    const sy = 1 - motion * 0.05;
    this.container.setScale(sx, sy);

    // HP bar: only redraw when hp actually changed (dirty flag set by takeDamage).
    if (this._hpDirty) { this._drawHpBar(); this._hpDirty = false; }

    // Body redraw:
    //   - mage/bomber/spawner are genuinely animated (charging aura, fuse flash,
    //     spawn-pulse) so they redraw every frame regardless of flash state.
    //   - all other types only need a redraw when the flash state changes.
    const curFlash = this._flashTimer > 0;
    if (this.type === 'mage' || this.type === 'bomber' || this.type === 'spawner') {
      this._draw(curFlash);
    } else if (curFlash !== this._lastFlash) {
      this._lastFlash = curFlash;
      this._draw(curFlash);
    }
  }

  /**
   * Apply damage; apply knockback impulse; trigger red flash.
   * Heavy hits (amount >= 18, matching game.js threshold) also trigger a brief
   * STUNNED state so the state machine pauses enemy AI for extra impact weight.
   */
  takeDamage(amount, kbVx = 0, kbVy = 0) {
    if (this.dead) return;

    this.hp = Math.max(0, this.hp - amount);

    this._flashTimer = 190;
    this._lastFlash  = true;   // keep cache coherent with the draw we're about to issue
    this._hpDirty    = true;   // hp changed — schedule bar redraw next frame
    this._draw(true);
    this.scene.tweens.add({ targets: this.container, scaleX: this.container.scaleX * 1.08, scaleY: 0.9, duration: 70, yoyo: true });

    if (Math.hypot(kbVx, kbVy) > 0) {
      this._physBody.setVelocity(kbVx, kbVy);
      this._knockbackTimer = 260;
    }

    // ── Stun on heavy hit ─────────────────────────────────────────────────────
    // Only applies to types that use the state machine (not bomber/spawner/boss).
    // Stun stacks with knockback: the enemy is first ragdolled by physics, then
    // stands still for the stun duration before AI resumes.
    if (
      amount >= 18 &&
      this.type !== 'bomber' &&
      this.type !== 'spawner' &&
      this.type !== 'boss' &&
      !this.dead
    ) {
      this._state     = AI.STUNNED;
      this._stunTimer = STUN_DURATION_HEAVY;
    }

    // Ensure the enemy has aggro after being hit — even if the player attacked
    // from outside the normal aggroRadius (e.g. ranged spell).
    if (!this.dead) this._hasAggro = true;

    // ── White hit flash — brief tint on all graphics children ────────────────
    if (this.container?.scene && this.isAlive) {
      const gfxChildren = this.container.list || [];
      for (const child of gfxChildren) {
        if (child?.setTint) child.setTint(0xffffff);
      }
      this.container.scene?.time.delayedCall(60, () => {
        if (this.container?.scene) {
          for (const child of this.container.list || []) {
            if (child?.clearTint) child.clearTint();
          }
        }
      });
    }

    if (this.hp <= 0) this._die();
  }

  // ── Private AI ─────────────────────────────────────────────────────────────

  /**
   * Unified state machine entry point for melee, archer, mage, and tank types.
   *
   * State transition graph (simplified):
   *
   *   IDLE ──(player enters aggroRadius)──> ALERT
   *   ALERT ──(alertTimer expires)────────> CHASE
   *   CHASE ──(within attackRange)─────── > ATTACK
   *   CHASE / ATTACK ──(HP < 30%)──────── > RETREAT  (non-boss, non-tank)
   *   ATTACK ──(player leaves attackRange)> CHASE
   *   CHASE ──(player leaves aggroRadius)─> IDLE
   *   RETREAT ──(retreatTimer expires)────> CHASE
   *   any ──(takeDamage heavy hit)────────> STUNNED
   *   STUNNED ──(stunTimer expires)───────> CHASE
   *
   * @param {number} dt
   * @param {number} playerX
   * @param {number} playerY
   */
  _updateStateMachine(dt, playerX, playerY) {
    const dx   = playerX - this.container.x;
    const dy   = playerY - this.container.y;
    const dist = Math.hypot(dx, dy);

    // ── STUNNED ──────────────────────────────────────────────────────────────
    // Overrides all other logic. Enemy stands still until stun expires.
    if (this._state === AI.STUNNED) {
      this._stunTimer -= dt;
      this._physBody.setVelocity(0, 0);
      if (this._stunTimer <= 0) {
        this._state = AI.CHASE;
      }
      return;
    }

    // ── ALERT ─────────────────────────────────────────────────────────────────
    // Enemy has spotted the player. It freezes briefly with a visual "!" to give
    // the player a reaction window before the chase begins.
    if (this._state === AI.ALERT) {
      this._alertTimer -= dt;
      this._physBody.setVelocity(0, 0);
      // Draw "!" indicator above the enemy for the duration of the alert
      this._drawAlertIndicator(this._alertTimer > 0);
      if (this._alertTimer <= 0) {
        this._hasAggro = true;
        this._state = AI.CHASE;
      }
      return;
    }

    // ── RETREAT ──────────────────────────────────────────────────────────────
    // Low-HP escape — enemy flees directly away from the player for RETREAT_DURATION
    // then transitions back to CHASE (angry and re-engaged).
    // Tank and boss are designed as aggressive brutes — no retreat for them.
    if (this._state === AI.RETREAT) {
      this._retreatTimer -= dt;
      const retreatSpeed = this.speed * 0.8;
      if (dist > 1) {
        // Move directly away from the player
        this._physBody.setVelocity(-(dx / dist) * retreatSpeed, -(dy / dist) * retreatSpeed);
      } else {
        this._physBody.setVelocity(0, 0);
      }
      if (this._retreatTimer <= 0) {
        this._state = AI.CHASE;
      }
      return;
    }

    // ── Transition: IDLE → ALERT ──────────────────────────────────────────────
    // First-time aggro triggers the ALERT pause. After the enemy has already
    // entered ALERT once (_hasAggro = true), re-aggro goes straight to CHASE
    // so it doesn't feel sluggish in prolonged combat.
    const inAggroRange = dist < this.aggroRadius;
    if (!this._hasAggro && inAggroRange && this._state === AI.IDLE) {
      this._state      = AI.ALERT;
      this._alertTimer = ALERT_DURATION;
      return;
    }

    // ── Transition: any → RETREAT ─────────────────────────────────────────────
    // Only trigger RETREAT once per low-HP threshold crossing. Tank and boss
    // never retreat — they are pure aggression archetypes.
    if (
      this._hasAggro &&
      this._state !== AI.RETREAT &&
      this.type !== 'tank' &&
      this.type !== 'boss' &&
      this.hp / this.maxHp < RETREAT_HP_THRESHOLD &&
      !this._retreatUsed
    ) {
      this._retreatUsed  = true; // one-shot per life — don't yo-yo endlessly
      this._state        = AI.RETREAT;
      this._retreatTimer = RETREAT_DURATION;
      return;
    }

    // ── Delegate to type-specific logic for CHASE / ATTACK / ranged states ────
    if (this.type === 'archer') {
      this._updateArcherAI(dt, playerX, playerY, dist, dx, dy);
    } else if (this.type === 'mage') {
      this._updateMageAI(dt, playerX, playerY, dist, dx, dy);
    } else if (this.type === 'tank') {
      this._updateTankAI(dt, playerX, playerY, dist, dx, dy);
    } else {
      // slime, skeleton
      this._updateMeleeAI(dt, playerX, playerY, dist, dx, dy);
    }
  }

  /**
   * Draw or hide the "!" ALERT indicator above the enemy.
   * The indicator is a small Graphics object reused per-enemy to avoid per-frame allocs.
   * @param {boolean} visible
   */
  _drawAlertIndicator(visible) {
    if (!this._alertGfx) {
      // Lazy-create once; placed in world space above the enemy's container
      this._alertGfx = this.scene.add.graphics().setDepth(12);
    }
    this._alertGfx.clear();
    if (!visible) return;

    const gx = this.container.x;
    const gy = this.container.y - 58; // above sprite head

    // White exclamation mark with a dark drop-shadow for readability
    this._alertGfx.fillStyle(0x000000, 0.4);
    this._alertGfx.fillRect(gx - 3, gy - 17, 8, 20);   // shadow
    this._alertGfx.fillStyle(0xfde68a, 1);               // yellow "!"
    this._alertGfx.fillRect(gx - 4, gy - 18, 8, 14);    // body of "!"
    this._alertGfx.fillRect(gx - 4, gy + 0,  8,  6);    // dot of "!"
  }

  _updateMeleeAI(dt, playerX, playerY, dist, dx, dy) {
    // dist/dx/dy are pre-computed by _updateStateMachine — avoid redundant hypot
    if (dist === undefined) {
      dx   = playerX - this.container.x;
      dy   = playerY - this.container.y;
      dist = Math.hypot(dx, dy);
    }

    this._attackTimer -= dt;
    if (dist <= this.attackRange) {
      this._state = AI.ATTACK;
      this._physBody.setVelocity(0, 0);
      if (this._attackTimer <= 0) {
        this._attackTimer = this.attackCooldown;
        this._wantsAttack = true;
      }
    } else if (dist < this.aggroRadius) {
      this._state = AI.CHASE;
      if (dist > 1) {
        this._physBody.setVelocity((dx / dist) * this.speed, (dy / dist) * this.speed);
      }
    } else {
      this._wander(dt);
    }
  }

  _updateArcherAI(dt, playerX, playerY, dist, dx, dy) {
    if (dist === undefined) {
      dx   = playerX - this.container.x;
      dy   = playerY - this.container.y;
      dist = Math.hypot(dx, dy);
    }

    this._attackTimer -= dt;

    if (dist < this.minRange) {
      // Too close — back away
      this._state = AI.BACKPEDAL;
      this._physBody.setVelocity(-(dx / dist) * this.speed, -(dy / dist) * this.speed);
    } else if (dist <= this.attackRange && dist < this.aggroRadius) {
      // In sweet spot — stop and shoot
      this._state = AI.ATTACK;
      this._physBody.setVelocity(0, 0);
      if (this._attackTimer <= 0) {
        this._attackTimer = this.attackCooldown;
        this._shootAngle  = Math.atan2(dy, dx);
        this._wantsShoot  = true;
      }
    } else if (dist < this.aggroRadius) {
      // Chase to get in range
      this._state = AI.CHASE;
      if (dist > 1) {
        this._physBody.setVelocity((dx / dist) * this.speed, (dy / dist) * this.speed);
      }
    } else {
      this._wander(dt);
    }
  }

  _updateMageAI(dt, playerX, playerY, dist, dx, dy) {
    if (dist === undefined) {
      dx   = playerX - this.container.x;
      dy   = playerY - this.container.y;
      dist = Math.hypot(dx, dy);
    }

    this._attackTimer -= dt;
    if (this._charging > 0) this._charging -= dt;

    if (dist < this.minRange) {
      // Too close — back away
      this._state = AI.BACKPEDAL;
      this._physBody.setVelocity(-(dx / dist) * this.speed, -(dy / dist) * this.speed);
    } else if (dist <= this.attackRange && dist < this.aggroRadius) {
      // Sweet spot — strafe sideways slightly, fire when ready.
      // If entering strafe range from CHASE (or any non-strafe state), pick a
      // starting direction randomly so mages don't all strafe the same way.
      if (this._state !== AI.STRAFE_LEFT && this._state !== AI.STRAFE_RIGHT) {
        this._state = Math.random() < 0.5 ? AI.STRAFE_LEFT : AI.STRAFE_RIGHT;
        this._wanderTimer = 900 + Math.random() * 700; // fresh timer on entry
      }
      const isStrafingLeft = this._state === AI.STRAFE_LEFT;
      const perp = isStrafingLeft ? 1 : -1;
      this._physBody.setVelocity((-dy / dist) * this.speed * 0.35 * perp, (dx / dist) * this.speed * 0.35 * perp);
      this._wanderTimer -= dt;
      if (this._wanderTimer <= 0) {
        this._state = isStrafingLeft ? AI.STRAFE_RIGHT : AI.STRAFE_LEFT;
        this._wanderTimer = 900 + Math.random() * 700;
      }
      if (this._attackTimer <= 0) {
        this._attackTimer = this.attackCooldown;
        this._shootAngle  = Math.atan2(dy, dx);
        this._wantsShoot  = true;
        this._charging    = 300;
      }
    } else if (dist < this.aggroRadius) {
      // Too far — move closer
      this._state = AI.CHASE;
      if (dist > 1) {
        this._physBody.setVelocity((dx / dist) * this.speed, (dy / dist) * this.speed);
      }
    } else {
      this._wander(dt);
    }
  }

  _updateBomberAI(dt, playerX, playerY) {
    const dx   = playerX - this.container.x;
    const dy   = playerY - this.container.y;
    const dist = Math.hypot(dx, dy);

    if (this._priming) {
      this._physBody.setVelocity(0, 0);
      this._primeTimer -= dt;
      this._primeFlash -= dt;
      if (this._primeFlash <= 0) {
        this._primeFlash = 160;
        this._draw(!this._bodyGfx._flashOn);
        this._bodyGfx._flashOn = !this._bodyGfx._flashOn;
      }
      if (this._primeTimer <= 0) {
        this._wantsExplode = true;
        this._priming = false;
      }
      return;
    }

    if (dist < this.aggroRadius) {
      if (dist <= this.attackRange) {
        // Start priming
        this._priming    = true;
        this._primeTimer = 1400;
        this._primeFlash = 0;
        this._physBody.setVelocity(0, 0);
      } else {
        this._state = 'chase';
        if (dist > 1) {
          this._physBody.setVelocity((dx / dist) * this.speed, (dy / dist) * this.speed);
        }
      }
    } else {
      this._wander(dt);
    }
  }

  _updateBossAI(dt, playerX, playerY) {
    const dx   = playerX - this.container.x;
    const dy   = playerY - this.container.y;
    const dist = Math.hypot(dx, dy);

    // Phase transition
    const newPhase = this.hp / this.maxHp <= 0.5 ? 2 : 1;
    if (newPhase !== this._phase) {
      this._phase = newPhase;
      // Enrage: speed and cooldown boost
      this.speed          = 68 * (newPhase === 2 ? 1.6 : 1);
      this.attackCooldown = 1300 * (newPhase === 2 ? 0.65 : 1);
    }

    this._attackTimer -= dt;
    this._shootTimer  -= dt;

    if (dist <= this.attackRange) {
      this._state = 'attack';
      this._physBody.setVelocity(0, 0);
      if (this._attackTimer <= 0) {
        this._attackTimer = this.attackCooldown;
        this._wantsAttack = true;
      }
    } else {
      this._state = 'chase';
      if (dist > 1) {
        this._physBody.setVelocity((dx / dist) * this.speed, (dy / dist) * this.speed);
      }
    }

    // Ranged burst — always fires regardless of distance
    const shootInterval = this._phase === 2 ? 2000 : 3200;
    if (this._shootTimer <= 0) {
      this._shootTimer = shootInterval;
      const baseAngle   = Math.atan2(dy, dx);
      const spreadCount = this._phase === 2 ? 5 : 3;
      const spreadStep  = (Math.PI * 2) / spreadCount;
      this._shootAngles = Array.from({ length: spreadCount }, (_, i) =>
        baseAngle + (i - Math.floor(spreadCount / 2)) * spreadStep * 0.38
      );
      this._wantsShoot = true;
    }
  }

  _updateTankAI(dt, playerX, playerY, dist, dx, dy) {
    if (dist === undefined) {
      dx   = playerX - this.container.x;
      dy   = playerY - this.container.y;
      dist = Math.hypot(dx, dy);
    }
    this._attackTimer -= dt;
    if (dist <= this.attackRange) {
      this._state = AI.ATTACK;
      this._physBody.setVelocity(0, 0);
      if (this._attackTimer <= 0) {
        this._attackTimer = this.attackCooldown;
        this._wantsAttack    = true;
        this._shockwaveReady = true; // game.js reads this to trigger AoE
      }
    } else if (dist < this.aggroRadius) {
      this._state = AI.CHASE;
      if (dist > 1) {
        this._physBody.setVelocity((dx / dist) * this.speed, (dy / dist) * this.speed);
      }
    } else {
      this._wander(dt);
    }
  }

  _updateSpawnerAI(dt) {
    this._physBody.setVelocity(0, 0);
    this._spawnTimer -= dt;
    if (this._spawnTimer <= 0) {
      this._spawnTimer  = 5000 + Math.random() * 2000;
      this._wantsSpawn  = true;
    }
  }

  _wander(dt) {
    this._wanderTimer -= dt;
    if (this._wanderTimer <= 0) {
      if (this._state === AI.IDLE) {
        // Transition IDLE → WANDER: pick a random direction and speed
        const angle       = Math.random() * Math.PI * 2;
        const ws          = this.speed * 0.42;
        this._wanderVx    = Math.cos(angle) * ws;
        this._wanderVy    = Math.sin(angle) * ws;
        this._wanderTimer = 900 + Math.random() * 900;
        this._state       = AI.WANDER;
      } else {
        // Transition WANDER → IDLE: stop and pause
        this._wanderVx    = 0;
        this._wanderVy    = 0;
        this._wanderTimer = 450 + Math.random() * 800;
        this._state       = AI.IDLE;
      }
    }
    this._physBody.setVelocity(this._wanderVx, this._wanderVy);
  }

  // ── Private ────────────────────────────────────────────────────────────────

  _die() {
    this.dead = true;
    if (this._physBody) this._physBody.setVelocity(0, 0);

    // Clean up the alert indicator Graphics that lives outside the container
    if (this._alertGfx) {
      this._alertGfx.destroy();
      this._alertGfx = null;
    }

    // ── Drop table roll ───────────────────────────────────────────────────────
    // Resolve the drop id now (while position is still valid) and fire the
    // optional _onDrop callback so game.js can spawn the world item.
    // game.js can also read this.droppedItemId directly during its dead-enemy
    // cleanup pass as a fallback.
    this.droppedItemId = rollDrop(this.type, Math.random.bind(Math));
    if (this.droppedItemId && typeof this._onDrop === 'function') {
      this._onDrop(this.droppedItemId, this.container.x, this.container.y);
    }

    // ── Death burst animation ─────────────────────────────────────────────────
    // Scale-pop tween drives container.destroy() in onComplete so we don't
    // destroy the container before the tween finishes.
    const scene = this.container.scene;
    if (scene) {
      const deathX = this.container.x;
      const deathY = this.container.y;

      // Per-type burst colour — matches the dominant palette of each silhouette.
      const TYPE_COLORS = {
        slime:    0x1aad3c,
        skeleton: 0xe8ecf0,
        archer:   0x064e3b,
        mage:     0xa78bfa,
        bomber:   0xf97316,
        tank:     0x374151,
        spawner:  0xa855f7,
        boss:     0x7c3aed,
      };
      const burstColor = TYPE_COLORS[this.type] || 0xffffff;

      // Scale pop then fade — container destroyed in onComplete
      scene.tweens.add({
        targets:  this.container,
        scaleX:   1.4,
        scaleY:   1.4,
        alpha:    0,
        duration: 150,
        ease:     'Quad.easeOut',
        onComplete: () => {
          if (this.container?.scene) this.container.destroy();
        },
      });

      // Six radial spark particles spawned directly in world space
      for (let i = 0; i < 6; i++) {
        const angle = (i / 6) * Math.PI * 2;
        const speed = 60 + Math.random() * 40;
        const spark = scene.add.graphics().setDepth(12);
        spark.fillStyle(burstColor, 0.9).fillCircle(0, 0, 3 + Math.random() * 3);
        spark.setPosition(deathX, deathY);
        scene.tweens.add({
          targets: spark,
          x:       deathX + Math.cos(angle) * speed,
          y:       deathY + Math.sin(angle) * speed,
          alpha:   0,
          scaleX:  0,
          scaleY:  0,
          duration: 300 + Math.random() * 100,
          ease:    'Quad.easeOut',
          onComplete: () => { if (spark?.scene) spark.destroy(); },
        });
      }
      return; // tween's onComplete handles container.destroy()
    }

    // Fallback if no scene (should not happen in normal gameplay)
    if (this.container?.scene) this.container.destroy();
  }

  /**
   * @param {boolean} flashing — true = paint red/orange (hit flash)
   */
  _draw(flashing) {
    const g = this._bodyGfx;
    g.clear();

    if (this.type === 'slime') {
      if (flashing) {
        g.fillStyle(0xff3333, 1).fillEllipse(0, 4, 32, 26);
      } else {
        g.fillStyle(0x1aad3c, 1).fillEllipse(0, 4, 32, 26);          // main body
        g.fillStyle(0x0f7a2a, 0.7).fillEllipse(0, 10, 28, 14);       // belly shadow
        g.fillStyle(0x26d648, 0.5).fillEllipse(-6, -2, 10, 8);       // highlight blob
      }
      g.fillStyle(0x0d0d1a, 1).fillCircle(-5, 2, 3);   // left eye
      g.fillStyle(0x0d0d1a, 1).fillCircle(5, 2, 3);    // right eye
      g.fillStyle(0x26d648, 0.8).fillCircle(-4, 1, 1); // eye shine L
      g.fillStyle(0x26d648, 0.8).fillCircle(6, 1, 1);  // eye shine R

    } else if (this.type === 'skeleton') {
      const bone = flashing ? 0xff3333 : 0xe8ecf0;
      // Torso (narrow)
      g.fillStyle(bone, 1).fillRect(-4, -28, 8, 18);
      // Rib lines
      g.fillStyle(0x6b7280, 0.7).lineStyle(1, 0x6b7280, 0.9);
      g.lineBetween(-4, -20, 4, -20); g.lineBetween(-4, -16, 4, -16); g.lineBetween(-4, -12, 4, -12);
      // Lower body + legs
      g.fillStyle(bone, 1).fillRect(-2, -10, 4, 10);
      g.fillStyle(bone, 1).fillRect(-6, -10, 3, 12);
      g.fillStyle(bone, 1).fillRect(3, -10, 3, 12);
      // Skull
      g.fillStyle(bone, 1).fillCircle(0, -34, 11);
      g.fillStyle(0x0d0d1a, 1).fillRect(-8, -34, 5, 3);
      g.fillStyle(0x0d0d1a, 1).fillRect(3, -34, 5, 3);
      // Eye sockets (void)
      g.fillStyle(0x0d0d1a, 1).fillCircle(-4, -36, 5);
      g.fillStyle(0x0d0d1a, 1).fillCircle(4, -36, 5);
      // Eye glow on top
      g.fillStyle(flashing ? 0xffffff : 0xef4444, 1).fillCircle(-4, -36, 3);
      g.fillStyle(flashing ? 0xffffff : 0xef4444, 1).fillCircle(4, -36, 3);
      if (!flashing) {
        g.lineStyle(1, 0xfca5a5, 0.5).strokeCircle(-4, -36, 4); // L eye bloom
        g.lineStyle(1, 0xfca5a5, 0.5).strokeCircle(4, -36, 4);  // R eye bloom
      }

    } else if (this.type === 'mage') {
      const charging = (this._charging ?? 0) > 0;
      const robe = flashing ? 0xff3333 : 0x7c3aed;
      const dark = flashing ? 0xcc0000 : 0x4c1d95;
      const glow = flashing ? 0xffffff : (charging ? 0x67e8f9 : 0xa78bfa);
      // Robe body
      g.fillStyle(robe, 1).fillRect(-9, -28, 18, 30);
      g.fillStyle(dark, 0.8).fillRect(-9, -10, 18, 12);           // bottom shadow
      g.lineStyle(1, 0x8b5cf6, 0.4).lineBetween(0, -28, 0, 2);   // center robe line
      // Pointed hood
      g.fillStyle(robe, 1).fillTriangle(0, -46, -10, -28, 10, -28);
      g.fillStyle(0x5b21b6, 0.6).fillTriangle(0, -44, -8, -30, 8, -30);
      // Face
      g.fillStyle(0xfde68a, 1).fillEllipse(0, -32, 14, 12);
      // Orb hands
      g.fillStyle(glow, 0.9).fillCircle(-14, -18, 5);
      g.fillStyle(glow, 0.9).fillCircle(14, -18, 5);
      if (!flashing) {
        g.lineStyle(2, 0xc4b5fd, 0.3).strokeCircle(-14, -18, 8);
        g.lineStyle(2, 0xc4b5fd, 0.3).strokeCircle(14, -18, 8);
      }
      // Runes on robe (lit when charging)
      if (charging) {
        g.lineStyle(1, 0x67e8f9, 0.8);
        g.lineBetween(-8, -24, -2, -24); g.lineBetween(-8, -18, -2, -18);
        g.lineBetween(2, -24, 8, -24);   g.lineBetween(2, -18, 8, -18);
      }
      // Eyes — glow when charging
      g.fillStyle(charging ? glow : 0x111111, 1).fillCircle(-4, -33, 2);
      g.fillStyle(charging ? glow : 0x111111, 1).fillCircle(4, -33, 2);
      // Charging aura
      if (charging) {
        g.lineStyle(2, 0x67e8f9, 0.4).strokeCircle(0, -32, 10);
        g.lineStyle(1, 0xa78bfa, 0.25).strokeCircle(0, -10, 18);
      }

    } else if (this.type === 'archer') {
      const cloakCol  = flashing ? 0xcc0000 : 0x064e3b;
      const cloakDark = flashing ? 0xaa0000 : 0x043a28;
      const skinCol   = flashing ? 0xff6666 : 0xfbbf24;
      // ── Cloak body (shrunk slightly so head sits above it) ────────────────
      g.fillStyle(cloakCol, 1).fillRect(-7, -16, 14, 22);     // main cloak
      g.fillStyle(cloakDark, 0.7).fillRect(-7, 2, 14, 4);     // hem shadow
      if (!flashing) {
        g.lineStyle(1, 0x0f6b4a, 0.5).lineBetween(7, -16, 7, 6); // right edge highlight
        g.lineStyle(1, 0x000000, 0.25).lineBetween(-7, -16, -7, 6); // left shadow
      }
      // Hood peak (triangular tip above head)
      g.fillStyle(cloakCol, 1).fillTriangle(0, -32, -7, -22, 7, -22);
      // ── Circular head ────────────────────────────────────────────────────
      g.fillStyle(skinCol, 1).fillCircle(0, -24, 6);
      // Eye dots
      if (!flashing) {
        g.fillStyle(0x1a1a2e, 1).fillCircle(-2, -25, 1.5);
        g.fillStyle(0x1a1a2e, 1).fillCircle(3, -25, 1.5);
      } else {
        g.fillStyle(0xffffff, 1).fillCircle(-2, -25, 1.5);
        g.fillStyle(0xffffff, 1).fillCircle(3, -25, 1.5);
      }
      // ── Bow (right side, arc) ─────────────────────────────────────────────
      g.lineStyle(3, flashing ? 0xff6600 : 0xb45309, 1);
      g.lineBetween(11, -24, 15, -18); g.lineBetween(15, -18, 17, -12); g.lineBetween(17, -12, 15, -6); g.lineBetween(15, -6, 11, 0);
      // Bowstring
      g.lineStyle(1, 0xfef9c3, 0.9).lineBetween(15, -24, 15, 0);
      // Arrow nocked
      if (!flashing) {
        g.lineStyle(1, 0x92400e, 0.8).lineBetween(4, -14, 22, -14);
        g.fillStyle(0x6b7280, 1).fillTriangle(22, -14, 18, -12, 18, -16);
      }

    } else if (this.type === 'bomber') {
      const priming = this._priming;
      const bodyCol = flashing ? 0xff3333 : 0xf97316;
      // Round body
      g.fillStyle(bodyCol, 1).fillCircle(0, 0, 15);
      // Dark stripe band (shadow wrap) — skip when flashing to keep read clear
      if (!flashing) {
        g.fillStyle(0x7c2d12, 0.8).fillRect(-15, -3, 30, 6);
      }
      // X eyes
      g.lineStyle(2, flashing ? 0xffffff : 0x1c1c1c, 1);
      g.lineBetween(-7, -6, -3, -2); g.lineBetween(-3, -6, -7, -2); // X left
      g.lineBetween(3, -6, 7, -2);   g.lineBetween(7, -6, 3, -2);   // X right
      // Fuse at top
      g.lineStyle(2, priming ? 0xfbbf24 : 0x92400e, 1);
      g.lineBetween(0, -15, 5, -21); g.lineBetween(5, -21, 5, -27); g.lineBetween(5, -27, 2, -32);
      // Fuse spark
      if (priming) {
        g.fillStyle(0xfef08a, 0.9).fillCircle(2, -32, 3);
        g.lineStyle(1, 0xfbbf24, 0.6).strokeCircle(2, -32, 5);
      } else {
        g.fillStyle(0xfef08a, 0.9).fillCircle(2, -32, 3);
      }

    } else if (this.type === 'tank') {
      const armour = flashing ? 0xff3333 : 0x374151;
      const metal  = flashing ? 0xcc0000 : 0x6b7280;
      const plate  = flashing ? 0xff6666 : 0x9ca3af;
      const eyes   = flashing ? 0xff6600 : 0xef4444;
      // Base body (wide)
      g.fillStyle(armour, 1).fillRect(-18, -22, 36, 30);
      // Chest armor plates
      g.fillStyle(metal, 0.9).fillRect(-14, -20, 12, 14); // L plate
      g.fillStyle(metal, 0.9).fillRect(2, -20, 12, 14);   // R plate
      g.fillStyle(plate, 0.5).fillRect(-13, -19, 4, 6);   // L plate highlight
      g.fillStyle(plate, 0.5).fillRect(3, -19, 4, 6);     // R plate highlight
      // Pauldrons
      g.fillStyle(0x4b5563, 1).fillRoundedRect(-22, -26, 10, 10, 2);
      g.fillStyle(0x4b5563, 1).fillRoundedRect(12, -26, 10, 10, 2);
      // Glowing eyes
      g.fillStyle(eyes, 1).fillRect(-10, -16, 6, 5);
      g.fillStyle(eyes, 1).fillRect(4, -16, 6, 5);
      if (!flashing) {
        g.lineStyle(1, 0xfca5a5, 0.4).strokeRect(-10, -16, 6, 5);
        g.lineStyle(1, 0xfca5a5, 0.4).strokeRect(4, -16, 6, 5);
      }
      // Helmet slit
      g.fillStyle(0x1f2937, 1).fillRect(-12, -22, 24, 6);

    } else if (this.type === 'spawner') {
      const pulse = this._spawnTimer < 1800 ? 0.9 : 0.4;
      const glow  = flashing ? 0xffffff : 0xa855f7;
      // Base stone plinth
      g.fillStyle(0x1a2836, 1).fillRect(-14, 0, 28, 18);
      g.lineStyle(1, 0x2a3a4e, 0.7).strokeRect(-14, 0, 28, 18);
      // Main obelisk body
      g.fillStyle(0x2a3a4e, 1).fillRect(-10, -32, 20, 32);
      // Rune lines on obelisk (always visible, dim unless about to spawn)
      g.lineStyle(1, flashing ? 0xffffff : 0x6366f1, flashing ? 0.9 : 0.4);
      g.lineBetween(-7, -28, 7, -28); g.lineBetween(-7, -20, 7, -20);
      g.lineBetween(-7, -12, 7, -12);
      // Central orb
      g.fillStyle(glow, pulse).fillCircle(0, -18, 7);
      g.lineStyle(2, 0xc084fc, flashing ? 0 : 0.3).strokeCircle(0, -18, 10);
      // Pointed top
      g.fillStyle(0x2a3a4e, 1).fillTriangle(0, -44, -10, -32, 10, -32);
      g.lineStyle(1, 0x3d4d5e, 0.5).lineBetween(-10, -32, 0, -44);
      g.lineStyle(1, 0x3d4d5e, 0.5).lineBetween(0, -44, 10, -32);

    } else {   // boss
      const primary   = flashing ? 0xff3333 : 0x7c3aed;
      const secondary = flashing ? 0xcc0000 : 0x4c1d95;
      const phase2    = this._phase === 2;
      // Rune accent: blazing gold in phase 2, amber in phase 1 (per spec)
      const runeAlpha = phase2 ? 1.0 : 0.5;
      const runeColor = phase2 ? 0xfbbf24 : 0xf59e0b;
      const accent    = flashing ? 0xff9900 : 0xfbbf24;
      // Shadow
      g.fillStyle(0x000000, 0.4); g.fillEllipse(2, 36, 52, 16);
      // Legs
      g.fillStyle(secondary, 1); g.fillRect(-22, 14, 14, 24); g.fillRect(8, 14, 14, 24);
      g.fillStyle(primary, 0.6);  g.fillRect(-22, 20, 14, 4);  g.fillRect(8, 20, 14, 4);
      // Torso
      g.fillStyle(primary, 1); g.fillRect(-22, -16, 44, 32);
      // Phase 2 halo around torso
      if (phase2 && !flashing) {
        g.lineStyle(2, 0xc084fc, 0.35).strokeRect(-22, -16, 44, 32);
      }
      // Rune lines on torso (gold, intensity scales with phase)
      g.lineStyle(2, runeColor, runeAlpha);
      g.lineBetween(-16, -8, -4, -8); g.lineBetween(-16, -1, -4, -1); g.lineBetween(-16, 6, -4, 6);
      g.lineBetween(4, -8, 16, -8);   g.lineBetween(4, -1, 16, -1);   g.lineBetween(4, 6, 16, 6);
      // Arms (big)
      g.fillStyle(secondary, 1); g.fillRect(-38, -14, 18, 28); g.fillRect(20, -14, 18, 28);
      // Claws
      g.fillStyle(accent, 1);
      g.fillTriangle(-38, 14, -42, 28, -34, 24);
      g.fillTriangle(38, 14, 34, 28, 42, 24);
      // Head — large skull with horns
      g.fillStyle(secondary, 1); g.fillRect(-20, -50, 40, 36);
      g.fillRoundedRect(-20, -56, 40, 18, { tl: 12, tr: 12, bl: 0, br: 0 });
      // Horns
      g.fillStyle(accent, 1);
      g.fillTriangle(-18, -52, -26, -68, -10, -54);
      g.fillTriangle(18, -52, 26, -68, 10, -54);
      // Eye sockets
      g.fillStyle(0x0a0010, 1); g.fillRect(-14, -46, 10, 12); g.fillRect(4, -46, 10, 12);
      // Glowing eyes
      g.fillStyle(phase2 ? 0xff0000 : accent, 1);
      g.fillCircle(-9, -41, 4); g.fillCircle(9, -41, 4);
      if (phase2) {
        g.lineStyle(2, 0xff6600, 0.7); g.strokeCircle(-9, -41, 7); g.strokeCircle(9, -41, 7);
      }
      // Mouth / teeth
      g.fillStyle(secondary, 1); g.fillRect(-14, -30, 28, 6);
      g.fillStyle(accent, 0.8);
      for (let t = 0; t < 5; t++) g.fillRect(-12 + t * 5, -28, 4, 5);
    }
  }

  /** Draw the enemy's HP bar above its sprite. */
  _drawHpBar() {
    const g = this._hpBarGfx;
    g.clear();
    if (this.hp >= this.maxHp) return;

    const isBoss = this.type === 'boss';
    const bw     = isBoss ? 56 : 34;
    const bh     = isBoss ? 6  : 4;
    const bx     = -bw / 2;
    const by     = this.type === 'slime'   ? -24
                 : this.type === 'archer'  ? -36
                 : this.type === 'mage'    ? -60
                 : this.type === 'bomber'  ? -36
                 : this.type === 'boss'    ? -70
                 : this.type === 'tank'    ? -52
                 : this.type === 'spawner' ? -42
                 : -42;
    const ratio  = this.hp / this.maxHp;
    const col    = ratio > 0.5 ? 0x22c55e : ratio > 0.25 ? 0xeab308 : 0xef4444;

    g.fillStyle(0x111111, 0.9); g.fillRect(bx - 1, by - 1, bw + 2, bh + 2);
    g.fillStyle(0x1f1f1f, 1);   g.fillRect(bx, by, bw, bh);
    g.fillStyle(col, 1);        g.fillRect(bx, by, Math.max(bw * ratio, 1), bh);
  }
}
