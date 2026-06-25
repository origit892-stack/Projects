import Player from '../objects/Player.js';
import { createWorldBounds } from '../systems/world.js';

export default class GameScene extends Phaser.Scene {
  constructor() {
    super('GameScene');
  }

  create() {
    this.player = new Player(this, 640, 360);
    createWorldBounds(this);
    this.cameras.main.startFollow(this.player.sprite, true, 0.08, 0.08);
  }

  update(time, delta) {
    this.player?.update(time, delta);
  }
}
