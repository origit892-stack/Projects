export default class Player {
  constructor(scene, x, y) {
    this.scene = scene;
    this.speed = 260;
    this.sprite = scene.add.rectangle(x, y, 34, 42, 0x6ee7b7);
    scene.physics.add.existing(this.sprite);
    this.sprite.body.setCollideWorldBounds(true);
    this.cursors = scene.input.keyboard.createCursorKeys();
    this.keys = scene.input.keyboard.addKeys('W,A,S,D,SPACE');
  }

  update() {
    const body = this.sprite.body;
    const left = this.cursors.left.isDown || this.keys.A.isDown;
    const right = this.cursors.right.isDown || this.keys.D.isDown;
    const up = this.cursors.up.isDown || this.keys.W.isDown;
    const down = this.cursors.down.isDown || this.keys.S.isDown;

    body.setVelocity(0);
    if (left) body.setVelocityX(-this.speed);
    if (right) body.setVelocityX(this.speed);
    if (up) body.setVelocityY(-this.speed);
    if (down) body.setVelocityY(this.speed);
    body.velocity.normalize().scale(this.speed);
  }
}
