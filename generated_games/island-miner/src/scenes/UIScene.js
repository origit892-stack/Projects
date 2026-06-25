export default class UIScene extends Phaser.Scene {
  constructor() {
    super('UIScene');
  }

  create() {
    this.add.text(24, 20, 'HP 100  |  Score 0', {
      fontFamily: 'Inter, system-ui, sans-serif',
      fontSize: '20px',
      color: '#f5f7fb'
    }).setScrollFactor(0);
  }
}
