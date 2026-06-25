export function createWorldBounds(scene) {
  scene.physics.world.setBounds(0, 0, 2400, 1600);
  scene.add.grid(1200, 800, 2400, 1600, 80, 80, 0x24283b, 0.32, 0x3b4261, 0.4);
}
