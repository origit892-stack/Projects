/**
 * mapgen.js — Procedural dungeon layout generator.
 *
 * Produces a 28×20 tile map on floor 1 (0 = floor, 1 = wall) that grows by
 * 4 cols and 3 rows per level (capped at 80×56). Results are deterministic
 * given the same integer seed, so levels can be reproduced from a stored seed.
 *
 * Algorithm
 * ---------
 *  1. Attempt to place rooms (4-8 tiles wide, 3-6 tall, capped to map size) without
 *     overlap.  A 1-tile gap between rooms is enforced.
 *  2. Connect them in a random chain with L-shaped, 2-tile-wide corridors.
 *  3. Sort rooms by distance from the map centre so rooms[0] is the spawn
 *     (near centre) and rooms[last] is the farthest (portal destination).
 */

export const MAP_COLS = 28;
export const MAP_ROWS = 20;

// -- Seeded PRNG (Mulberry32) -------------------------------------------------
function mulberry32(seed) {
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Random integer in [min, max] inclusive. */
function ri(rng, min, max) {
  return min + Math.floor(rng() * (max - min + 1));
}

/** True if two rooms overlap (with optional cell margin on all sides). */
function overlaps(a, b, margin = 0) {
  return (
    a.x - margin < b.x + b.w + margin &&
    a.x + a.w + margin > b.x - margin &&
    a.y - margin < b.y + b.h + margin &&
    a.y + a.h + margin > b.y - margin
  );
}

/** Carve a filled rectangle into the map. Leaves a 1-tile wall border. */
function carveRect(map, x, y, w, h, cols, rows) {
  for (let r = y; r < y + h; r++) {
    for (let c = x; c < x + w; c++) {
      if (r > 0 && r < rows - 1 && c > 0 && c < cols - 1) {
        map[r][c] = 0;
      }
    }
  }
}

/**
 * Carve an L-shaped 2-tile-wide corridor between two tile positions.
 * Direction (H-then-V or V-then-H) is chosen randomly.
 */
function carveTunnel(map, x1, y1, x2, y2, rng, cols, rows) {
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const carve = (r, c) => {
    if (r >= 0 && r < rows && c >= 0 && c < cols) map[r][c] = 0;
  };

  if (rng() < 0.5) {
    // Horizontal segment (y = y1), then vertical segment (x = x2)
    const x0 = Math.min(x1, x2), x9 = Math.max(x1, x2);
    const y0 = Math.min(y1, y2), y9 = Math.max(y1, y2);
    for (let c = x0; c <= x9; c++) { carve(y1, c); carve(clamp(y1 + 1, 0, rows-1), c); }
    for (let r = y0; r <= y9; r++) { carve(r, x2); carve(r, clamp(x2 - 1, 0, cols-1)); }
  } else {
    // Vertical segment (x = x1), then horizontal segment (y = y2)
    const x0 = Math.min(x1, x2), x9 = Math.max(x1, x2);
    const y0 = Math.min(y1, y2), y9 = Math.max(y1, y2);
    for (let r = y0; r <= y9; r++) { carve(r, x1); carve(r, clamp(x1 + 1, 0, cols-1)); }
    for (let c = x0; c <= x9; c++) { carve(y2, c); carve(clamp(y2 + 1, 0, cols-1)); }
  }
}

// -- Public API ----------------------------------------------------------------

/**
 * Generate a dungeon map for the given integer seed and optional floor level.
 *
 * Map dimensions grow with floor level (capped at 80x56) so later floors feel
 * meaningfully larger and more complex. Floor 1: 28×20. Floor 10: ~64×47.
 *
 * @param   {number} seed    - integer seed (same seed + level -> same map)
 * @param   {number} [level] - dungeon floor level (default 1)
 * @returns {{ map: number[][], rooms: Room[], cols: number, rows: number }}
 *
 * Room shape: { x, y, w, h, cx, cy }
 *   (x,y) = top-left tile; (cx,cy) = approximate centre tile.
 *   rooms[0]  = spawn room (closest to map centre)
 *   rooms[last] = portal room (farthest from map centre)
 */
export function generateDungeon(seed, level = 1) {
  const rng = mulberry32(seed >>> 0);

  // Dynamic map size: floor 1 is tight and claustrophobic, grows 4 cols / 3 rows
  // per level, capped at 80x56 (floor ~14+). Floor 10: 64×47, floor 14: 80×56.
  // Grow gradually instead of jumping to the max-size map on floor 3.
  // The old step caused a huge perf spike and made early hard floors feel unreadable.
  const cols = Math.min(80, MAP_COLS + (level - 1) * 4);
  const rows = Math.min(56, MAP_ROWS + (level - 1) * 3);

  const map = Array.from({ length: rows }, () => new Array(cols).fill(1));
  const rooms = [];

  // Room count scales with map size so small floor-1 maps aren't over-stuffed.
  // Floor 1 (28 cols): min(4+3,12)=7. Floor 10 (64 cols): min(4+8,12)=12.
  let targetBase = Math.min(4 + Math.floor(cols / 8), 12);
  if (level >= 10) targetBase += 1;
  if (level >= 15) targetBase += 1;
  const target = targetBase;

  for (let attempt = 0; attempt < 1000 && rooms.length < target; attempt++) {
    const w  = ri(rng, 4, Math.min(8, Math.floor(cols / 4)));
    const h  = ri(rng, 3, Math.min(6, Math.floor(rows / 4)));
    const x  = ri(rng, 1, cols - w - 2);
    const y  = ri(rng, 1, rows - h - 2);
    const cx = x + Math.floor(w / 2);
    const cy = y + Math.floor(h / 2);
    const room = { x, y, w, h, cx, cy };

    if (!rooms.some(r => overlaps(r, room, 1))) {
      rooms.push(room);
      carveRect(map, x, y, w, h, cols, rows);
    }
  }

  // Fallback: guarantee at least one room
  if (rooms.length === 0) {
    const fw = Math.min(8, Math.floor(cols / 3)), fh = Math.min(6, Math.floor(rows / 3));
    const r = { x: Math.floor(cols / 2) - Math.floor(fw / 2), y: Math.floor(rows / 2) - Math.floor(fh / 2), w: fw, h: fh, cx: Math.floor(cols / 2), cy: Math.floor(rows / 2) };
    r.cx = r.x + Math.floor(r.w / 2);
    r.cy = r.y + Math.floor(r.h / 2);
    rooms.push(r);
    carveRect(map, r.x, r.y, r.w, r.h, cols, rows);
  }

  // Connect rooms in a chain (guarantees full reachability)
  for (let i = 1; i < rooms.length; i++) {
    carveTunnel(map, rooms[i - 1].cx, rooms[i - 1].cy,
                     rooms[i].cx,     rooms[i].cy, rng, cols, rows);
  }

  // Extra cross-connections for variety (base: 2 at 4+ and 6+ rooms)
  if (rooms.length >= 4) {
    const a = Math.floor(rng() * rooms.length);
    const b = (a + 2 + Math.floor(rng() * (rooms.length - 2))) % rooms.length;
    if (a !== b) {
      carveTunnel(map, rooms[a].cx, rooms[a].cy, rooms[b].cx, rooms[b].cy, rng, cols, rows);
    }
  }
  if (rooms.length >= 6) {
    const a = Math.floor(rng() * rooms.length);
    const b = (a + 3 + Math.floor(rng() * (rooms.length - 3))) % rooms.length;
    if (a !== b) {
      carveTunnel(map, rooms[a].cx, rooms[a].cy, rooms[b].cx, rooms[b].cy, rng, cols, rows);
    }
  }
  // Third bonus cross-connection at level 15+ for denser layouts
  if (level >= 15 && rooms.length >= 5) {
    const a = Math.floor(rng() * rooms.length);
    const b = (a + 2 + Math.floor(rng() * (rooms.length - 2))) % rooms.length;
    if (a !== b) {
      carveTunnel(map, rooms[a].cx, rooms[a].cy, rooms[b].cx, rooms[b].cy, rng, cols, rows);
    }
  }

  // Sort: rooms[0] = nearest to map centre (spawn); rooms[last] = farthest (portal)
  const midX = cols / 2, midY = rows / 2;
  rooms.sort((a, b) =>
    Math.hypot(a.cx - midX, a.cy - midY) - Math.hypot(b.cx - midX, b.cy - midY)
  );

  // Assign room types
  rooms[0].type = 'spawn';
  rooms[rooms.length - 1].type = 'portal';

  // Collect middle room indices and shuffle them (seeded) for random type assignment
  const midIndices = [];
  for (let i = 1; i < rooms.length - 1; i++) midIndices.push(i);
  for (let i = midIndices.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    const tmp = midIndices[i]; midIndices[i] = midIndices[j]; midIndices[j] = tmp;
  }
  const specialTypes = ['shop', 'treasure'];
  for (let i = 0; i < midIndices.length; i++) {
    rooms[midIndices[i]].type = specialTypes[i] || 'normal';
  }

  return { map, rooms, cols, rows };
}
