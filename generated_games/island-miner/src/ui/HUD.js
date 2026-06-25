import Phaser from 'phaser';

export default class HUD {
  constructor(scene) {
    this.scene = scene;
    this.width = scene.scale.width;
    this.height = scene.scale.height;
    this.container = scene.add.container(0, 0).setScrollFactor(0).setDepth(1000);

    this.panel = scene.add.rectangle(12, 12, this.width - 24, 58, 0x17251a, 0.88)
      .setOrigin(0, 0)
      .setStrokeStyle(2, 0x5f7f4f);

    this.title = scene.add.text(24, 24, 'ISLAND MINER', {
      fontFamily: 'monospace',
      fontSize: '18px',
      color: '#f8f0b0',
      fontStyle: 'bold',
    });

    this.staminaLabel = scene.add.text(210, 22, 'STAMINA', {
      fontFamily: 'monospace',
      fontSize: '13px',
      color: '#d7e894',
    });

    this.staminaBack = scene.add.rectangle(210, 42, 180, 14, 0x263321, 1)
      .setOrigin(0, 0.5)
      .setStrokeStyle(1, 0x8ab060);
    this.staminaFill = scene.add.rectangle(212, 42, 176, 10, 0xa8e65a, 1)
      .setOrigin(0, 0.5);

    this.inventoryText = scene.add.text(420, 23, '', {
      fontFamily: 'monospace',
      fontSize: '15px',
      color: '#ffffff',
    });

    this.messageText = scene.add.text(this.width / 2, 84, '', {
      fontFamily: 'monospace',
      fontSize: '16px',
      color: '#ffe48a',
      backgroundColor: '#17251a',
      padding: { x: 10, y: 5 },
    }).setOrigin(0.5, 0).setAlpha(0);

    this.container.add([
      this.panel,
      this.title,
      this.staminaLabel,
      this.staminaBack,
      this.staminaFill,
      this.inventoryText,
      this.messageText,
    ]);

    scene.scale.on('resize', this.resize, this);
  }

  resize(gameSize) {
    this.width = gameSize.width;
    this.height = gameSize.height;
    this.panel.setSize(this.width - 24, 58);
    this.messageText.setX(this.width / 2);
  }

  update(state) {
    const staminaRatio = Phaser.Math.Clamp(state.stamina / state.maxStamina, 0, 1);
    this.staminaFill.width = 176 * staminaRatio;

    const staminaColor = staminaRatio > 0.55 ? 0xa8e65a : staminaRatio > 0.25 ? 0xf2c94c : 0xff6b5a;
    this.staminaFill.setFillStyle(staminaColor);

    const raftReady = state.inventory.wood >= 6 && state.inventory.gold >= 3;
    this.inventoryText.setText(
      `WOOD ${state.inventory.wood}  GOLD ${state.inventory.gold}  BERRIES ${state.inventory.berries}  ${raftReady ? 'RAFT READY' : 'RAFT: 6W 3G'}`
    );
  }

  showMessage(message) {
    this.scene.tweens.killTweensOf(this.messageText);
    this.messageText.setText(message).setAlpha(1);
    this.scene.tweens.add({
      targets: this.messageText,
      alpha: 0,
      delay: 1100,
      duration: 450,
      ease: 'Sine.easeOut',
    });
  }

  destroy() {
    this.scene.scale.off('resize', this.resize, this);
    this.container.destroy();
  }
}
