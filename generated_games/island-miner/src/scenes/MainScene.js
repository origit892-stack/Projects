import Phaser from 'phaser';
import HUD from '../ui/HUD.js';

const TILE = 32;
const PLAYER_SPEED = 170;
const BOAR_SPEED = 82;
const HARVEST_RANGE = 54;
const WORLD_WIDTH = 1280;
const WORLD_HEIGHT = 896;

export default class MainScene extends Phaser.Scene {
  constructor() {
    super('MainScene');
  }

  create() {
    this.state = {
      maxStamina: 100,
      stamina: 100,
      inventory: { wood: 0, gold: 0, berries: 0 },
      invulnerableUntil: 0,
      craftedRaft: false,
    };

    this.resourceNodes = [];
    this.boars = [];
    this.keys = this.input.keyboard.addKeys('W,A,S,D,UP,LEFT,DOWN,RIGHT,SPACE,E,F');

    this.createWorld();
    this.createPlayer();
    this.createResources();
    this.createBoars();

    this.hud = new HUD(this);
    this.hud.update(this.state);

    this.physics.add.collider(this.player, this.blockers);
    this.physics.add.collider(this.boarGroup, this.blockers);
    this.physics.add.overlap(this.player, this.boarGroup, this.onBoarHit, null, this);

    this.cameras.main.setBounds(0, 0, WORLD_WIDTH, WORLD_HEIGHT);
    this.cameras.main.startFollow(this.player, true, 0.12, 0.12);
    this.cameras.main.setZoom(1.3);

    this.input.keyboard.on('keydown-SPACE', () => this.harvestNearest());
    this.input.keyboard.on('keydown-E', () => this.eatBerry());
    this.input.keyboard.on('keydown-F', () => this.craftRaft());

    this.hud.showMessage('SPACE harvest | E eat berries | F craft raft');
  }

  createWorld() {
    this.add.rectangle(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, WORLD_WIDTH, WORLD_HEIGHT, 0x2f8f45);
    this.add.rectangle(WORLD_WIDTH / 2, 20, WORLD_WIDTH, 40, 0x2c7fb8);
    this.add.rectangle(WORLD_WIDTH / 2, WORLD_HEIGHT - 20, WORLD_WIDTH, 40, 0x2c7fb8);
    this.add.rectangle(20, WORLD_HEIGHT / 2, 40, WORLD_HEIGHT, 0x2c7fb8);
    this.add.rectangle(WORLD_WIDTH - 20, WORLD_HEIGHT / 2, 40, WORLD_HEIGHT, 0x2c7fb8);

    for (let x = 80; x < WORLD_WIDTH - 80; x += TILE) {
      for (let y = 80; y < WORLD_HEIGHT - 80; y += TILE) {
        if ((x + y) % 96 === 0) {
          this.add.rectangle(x, y, 3, 3, 0x5fbd58, 0.55);
        }
      }
    }

    this.blockers = this.physics.add.staticGroup();
    this.blockers.add(this.add.rectangle(WORLD_WIDTH / 2, 18, WORLD_WIDTH, 36, 0x2c7fb8, 0));
    this.blockers.add(this.add.rectangle(WORLD_WIDTH / 2, WORLD_HEIGHT - 18, WORLD_WIDTH, 36, 0x2c7fb8, 0));
    this.blockers.add(this.add.rectangle(18, WORLD_HEIGHT / 2, 36, WORLD_HEIGHT, 0x2c7fb8, 0));
    this.blockers.add(this.add.rectangle(WORLD_WIDTH - 18, WORLD_HEIGHT / 2, 36, WORLD_HEIGHT, 0x2c7fb8, 0));
  }

  createPlayer() {
    this.player = this.add.container(220, 210);
    const shadow = this.add.ellipse(0, 15, 26, 8, 0x17351d, 0.45);
    const body = this.add.rectangle(0, 0, 22, 28, 0xf3d27a).setStrokeStyle(2, 0x5a3d28);
    const hat = this.add.rectangle(0, -16, 28, 8, 0xb05d34).setStrokeStyle(1, 0x5a3d28);
    this.player.add([shadow, body, hat]);

    this.physics.add.existing(this.player);
    this.player.body.setSize(22, 26).setOffset(-11, -13).setCollideWorldBounds(true);
  }

  createResources() {
    this.resourceGroup = this.add.group();
    this.addResource('tree', 360, 180, 4);
    this.addResource('tree', 500, 640, 4);
    this.addResource('tree', 960, 240, 4);
    this.addResource('tree', 1080, 690, 4);
    this.addResource('gold', 710, 250, 3);
    this.addResource('gold', 820, 600, 3);
    this.addResource('berry', 280, 600, 2);
    this.addResource('berry', 1040, 430, 2);
  }

  addResource(type, x, y, hits) {
    const container = this.add.container(x, y);
    let sprite;
    let label;

    if (type === 'tree') {
      sprite = this.add.triangle(0, -12, 0, 22, 20, -8, -20, -8, 0x216d35).setStrokeStyle(2, 0x16451f);
      const trunk = this.add.rectangle(0, 14, 8, 18, 0x8b5a2b);
      container.add([trunk, sprite]);
      label = 'tree';
    } else if (type === 'gold') {
      sprite = this.add.polygon(0, 0, '0 -20 20 -6 14 18 -12 20 -22 -4', 0xd9a441).setStrokeStyle(2, 0x7a5b22);
      container.add(sprite);
      label = 'gold vein';
    } else {
      sprite = this.add.circle(0, 0, 15, 0x8a3159).setStrokeStyle(2, 0x4a1d31);
      container.add([
        this.add.circle(-7, -3, 5, 0xe05a8a),
        this.add.circle(4, -5, 5, 0xe05a8a),
        this.add.circle(1, 6, 5, 0xe05a8a),
        sprite,
      ]);
      label = 'berry bush';
    }

    const node = { type, label, x, y, hits, maxHits: hits, container };
    this.resourceNodes.push(node);
    this.resourceGroup.add(container);
  }

  createBoars() {
    this.boarGroup = this.physics.add.group();
    [
      { x: 610, y: 430 },
      { x: 980, y: 545 },
      { x: 430, y: 420 },
    ].forEach((pos) => {
      const boar = this.add.container(pos.x, pos.y);
      boar.add([
        this.add.ellipse(0, 0, 34, 22, 0x6c3c28).setStrokeStyle(2, 0x3d2118),
        this.add.rectangle(17, -4, 9, 7, 0xe0c7a1),
        this.add.triangle(-15, -10, 0, 0, 10, -6, 2, 8, 0x4a291d),
      ]);
      this.physics.add.existing(boar);
      boar.body.setSize(34, 22).setOffset(-17, -11);
      boar.home = new Phaser.Math.Vector2(pos.x, pos.y);
      boar.wanderAngle = Phaser.Math.FloatBetween(0, Math.PI * 2);
      this.boarGroup.add(boar);
      this.boars.push(boar);
    });
  }

  update(time, deltaMs) {
    const delta = deltaMs / 1000;
    this.updatePlayer(delta);
    this.updateBoars(delta);
    this.hud.update(this.state);
  }

  updatePlayer(delta) {
    const direction = new Phaser.Math.Vector2(0, 0);
    if (this.keys.A.isDown || this.keys.LEFT.isDown) direction.x -= 1;
    if (this.keys.D.isDown || this.keys.RIGHT.isDown) direction.x += 1;
    if (this.keys.W.isDown || this.keys.UP.isDown) direction.y -= 1;
    if (this.keys.S.isDown || this.keys.DOWN.isDown) direction.y += 1;

    if (direction.lengthSq() > 0) {
      direction.normalize();
      const tiredPenalty = this.state.stamina <= 0 ? 0.45 : 1;
      this.player.body.setVelocity(direction.x * PLAYER_SPEED * tiredPenalty, direction.y * PLAYER_SPEED * tiredPenalty);
      this.state.stamina = Math.max(0, this.state.stamina - 7 * delta);
      this.player.scaleX = direction.x < 0 ? -1 : direction.x > 0 ? 1 : this.player.scaleX;
    } else {
      this.player.body.setVelocity(0, 0);
      this.state.stamina = Math.min(this.state.maxStamina, this.state.stamina + 4 * delta);
    }
  }

  updateBoars(delta) {
    this.boars.forEach((boar) => {
      const toPlayer = new Phaser.Math.Vector2(this.player.x - boar.x, this.player.y - boar.y);
      const distance = toPlayer.length();

      if (distance < 230) {
        toPlayer.normalize();
        boar.body.setVelocity(toPlayer.x * BOAR_SPEED, toPlayer.y * BOAR_SPEED);
      } else {
        boar.wanderAngle += Phaser.Math.FloatBetween(-1.4, 1.4) * delta;
        const wander = new Phaser.Math.Vector2(Math.cos(boar.wanderAngle), Math.sin(boar.wanderAngle));
        boar.body.setVelocity(wander.x * BOAR_SPEED * 0.45, wander.y * BOAR_SPEED * 0.45);
      }

      boar.scaleX = boar.body.velocity.x < 0 ? -1 : 1;
    });
  }

  harvestNearest() {
    if (this.state.stamina < 8) {
      this.hud.showMessage('Too tired. Eat berries or rest.');
      return;
    }

    const node = this.findNearestResource();
    if (!node) {
      this.hud.showMessage('Move closer to a tree, gold vein, or berry bush.');
      return;
    }

    this.state.stamina = Math.max(0, this.state.stamina - 8);
    node.hits -= 1;
    this.tweens.add({
      targets: node.container,
      scaleX: 1.12,
      scaleY: 0.88,
      yoyo: true,
      duration: 90,
      ease: 'Quad.easeOut',
    });

    if (node.type === 'tree') this.state.inventory.wood += 1;
    if (node.type === 'gold') this.state.inventory.gold += 1;
    if (node.type === 'berry') this.state.inventory.berries += 1;

    if (node.hits <= 0) {
      this.depleteResource(node);
    } else {
      this.hud.showMessage(`Harvested ${node.label}.`);
    }
  }

  findNearestResource() {
    let nearest = null;
    let nearestDistance = HARVEST_RANGE;
    this.resourceNodes.forEach((node) => {
      const distance = Phaser.Math.Distance.Between(this.player.x, this.player.y, node.x, node.y);
      if (distance < nearestDistance) {
        nearest = node;
        nearestDistance = distance;
      }
    });
    return nearest;
  }

  depleteResource(node) {
    this.resourceNodes = this.resourceNodes.filter((item) => item !== node);
    if (node.type === 'gold') {
      this.cameras.main.shake(260, 0.008);
      this.hud.showMessage('Gold vein depleted! The island rumbles.');
    } else if (node.type === 'tree') {
      this.hud.showMessage('Tree chopped down. Wood gathered.');
    } else {
      this.hud.showMessage('Berry bush picked clean.');
    }

    this.tweens.add({
      targets: node.container,
      alpha: 0,
      scale: 0.2,
      duration: 280,
      ease: 'Back.easeIn',
      onComplete: () => node.container.destroy(),
    });
  }

  eatBerry() {
    if (this.state.inventory.berries <= 0) {
      this.hud.showMessage('No berries in your pack.');
      return;
    }
    this.state.inventory.berries -= 1;
    this.state.stamina = Math.min(this.state.maxStamina, this.state.stamina + 45);
    this.hud.showMessage('Berry eaten. Stamina restored.');
  }

  craftRaft() {
    if (this.state.craftedRaft) {
      this.hud.showMessage('Raft already crafted. You own the island.');
      return;
    }
    if (this.state.inventory.wood >= 6 && this.state.inventory.gold >= 3) {
      this.state.inventory.wood -= 6;
      this.state.inventory.gold -= 3;
      this.state.craftedRaft = true;
      this.add.rectangle(this.player.x + 48, this.player.y + 20, 52, 28, 0x9b6b3d)
        .setStrokeStyle(2, 0x4d301c)
        .setDepth(4);
      this.cameras.main.flash(180, 255, 236, 145);
      this.hud.showMessage('Raft crafted! Milestone complete.');
    } else {
      this.hud.showMessage('Need 6 wood and 3 gold to craft a raft.');
    }
  }

  onBoarHit(player, boar) {
    if (this.time.now < this.state.invulnerableUntil) return;
    this.state.invulnerableUntil = this.time.now + 900;
    this.state.stamina = Math.max(0, this.state.stamina - 24);

    const knockback = new Phaser.Math.Vector2(player.x - boar.x, player.y - boar.y).normalize().scale(190);
    player.body.setVelocity(knockback.x, knockback.y);
    this.cameras.main.shake(160, 0.006);
    this.hud.showMessage('Boar charge! Stamina lost.');
  }
}
