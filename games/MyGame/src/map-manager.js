import { generateDungeon, MAP_COLS, MAP_ROWS } from './mapgen.js';

export class MapManager {
  constructor(seed, dungeonLevel = 1) {
    this.seed = seed >>> 0;
    this.layout = generateDungeon(this.seed, dungeonLevel);
    // Dynamic map dimensions returned by the generator for this floor
    this.cols = this.layout.cols;
    this.rows = this.layout.rows;
  }

  get map() {
    return this.layout.map;
  }

  get rooms() {
    return this.layout.rooms;
  }

  /** Returns the dynamic tile dimensions for this floor. */
  getMapSize() {
    return { cols: this.cols, rows: this.rows };
  }

  isWall(col, row) {
    if (row < 0 || row >= this.rows || col < 0 || col >= this.cols) return true;
    return this.layout.map[row][col] === 1;
  }

  carve(col, row) {
    if (row < 0 || row >= this.rows || col < 0 || col >= this.cols) return false;
    if (this.layout.map[row][col] !== 1) return false;
    this.layout.map[row][col] = 0;
    return true;
  }
}

export { MAP_COLS, MAP_ROWS };
