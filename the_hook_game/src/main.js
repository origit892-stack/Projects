import * as THREE from "three";
import "./styles.css";

const canvas = document.querySelector("#game");
const scoreEl = document.querySelector("#score");
const coinsEl = document.querySelector("#coins");
const menuCoinsEl = document.querySelector("#menuCoins");
const destroyedEl = document.querySelector("#destroyed");
const dodgedEl = document.querySelector("#dodged");
const comboEl = document.querySelector("#combo");
const feverEl = document.querySelector("#fever");
const statusEl = document.querySelector("#status");
const hudEl = document.querySelector(".hud");
const missionsEl = document.querySelector("#missions");
const bossWarningEl = document.querySelector("#bossWarning");
const introEl = document.querySelector("#intro");
const startButtonEl = document.querySelector("#startButton");
const ropeCostEl = document.querySelector("#ropeCost");
const shopButtons = [...document.querySelectorAll(".shop-item")];

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x090a0d);
scene.fog = new THREE.FogExp2(0x090a0d, 0.017);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;

const camera = new THREE.PerspectiveCamera(46, window.innerWidth / window.innerHeight, 0.1, 240);
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const timer = new THREE.Timer();
timer.connect(document);

const world = {
  laneHalfWidth: 7.4,
  runSpeed: 14,
  enemySpeed: 7,
  spawnEvery: 0.92,
  spawnTimer: 0,
  started: false,
  runTime: 0,
  comboBoostTime: 0,
  gameOver: false,
  distance: 0,
  speedEffect: 0,
  shake: 0,
  environmentIndex: 0,
  environmentTimer: 0,
  combo: 0,
  comboTimer: 0,
  destroyStreak: 0,
  bulletTime: 0,
  feverMeter: 0,
  feverTime: 0,
  timeScale: 1,
  hazardTimer: 2.4,
  beatTimer: 0,
  audioStarted: false,
  nextBossScore: 500,
  bossActive: false,
  bossHits: 0,
  bossAttackTimer: 0,
  bossWarningTimer: 0,
  biomeIndex: 0,
  biomeTimer: 0,
  coinTimer: 1.1,
  noDestroyDistance: 0,
};

const score = {
  destroyed: 0,
  dodged: 0,
  total: 0,
  coins: 0,
};

const save = {
  coins: Number(localStorage.getItem("hookRunnerCoins") ?? 0),
  ropeLevel: Number(localStorage.getItem("hookRunnerRope") ?? 0),
  skin: localStorage.getItem("hookRunnerSkin") ?? "default",
  ownedSkins: JSON.parse(localStorage.getItem("hookRunnerSkins") ?? "[\"default\"]"),
};

const keys = new Set();
const enemies = [];
const fragments = [];
const particleBursts = [];
const runwaySegments = [];
const stars = [];
const speedLines = [];
const asteroids = [];
const nebulaClouds = [];
const trailSegments = [];
const hazards = [];
const crystals = [];
let boss = null;

const tmpVec = new THREE.Vector3();
const tmpVecB = new THREE.Vector3();
let audioContext = null;

const materials = {
  runway: new THREE.MeshStandardMaterial({
    color: 0x303435,
    roughness: 0.58,
    metalness: 0.22,
  }),
  runwaySide: new THREE.MeshStandardMaterial({
    color: 0x171b1e,
    roughness: 0.34,
    metalness: 0.72,
  }),
  player: new THREE.MeshStandardMaterial({
    color: 0xe8e1d2,
    roughness: 0.38,
    metalness: 0.38,
  }),
  playerAccent: new THREE.MeshStandardMaterial({
    color: 0x2a9fb0,
    roughness: 0.32,
    metalness: 0.56,
    emissive: 0x0b4351,
    emissiveIntensity: 0.7,
  }),
  playerDark: new THREE.MeshStandardMaterial({
    color: 0x191d22,
    roughness: 0.28,
    metalness: 0.82,
  }),
  playerGlow: new THREE.MeshStandardMaterial({
    color: 0x7fd8ff,
    roughness: 0.2,
    metalness: 0.45,
    emissive: 0x1479ad,
    emissiveIntensity: 1.9,
  }),
  enemy: new THREE.MeshStandardMaterial({
    color: 0xd4473f,
    roughness: 0.25,
    metalness: 0.22,
    emissive: 0x5c0b08,
    emissiveIntensity: 0.8,
    transparent: true,
    opacity: 0.86,
  }),
  enemyEdge: new THREE.MeshStandardMaterial({
    color: 0xffb0a4,
    roughness: 0.22,
    metalness: 0.72,
    emissive: 0xa62117,
    emissiveIntensity: 1.15,
  }),
  fragment: new THREE.MeshStandardMaterial({
    color: 0xbf5a48,
    roughness: 0.52,
    metalness: 0.16,
  }),
  shieldEnemy: new THREE.MeshStandardMaterial({
    color: 0x2f8bd8,
    roughness: 0.18,
    metalness: 0.58,
    emissive: 0x0a4c86,
    emissiveIntensity: 1.0,
    transparent: true,
    opacity: 0.82,
  }),
  bombEnemy: new THREE.MeshStandardMaterial({
    color: 0xf0c83d,
    roughness: 0.2,
    metalness: 0.35,
    emissive: 0x8a4b05,
    emissiveIntensity: 1.05,
    transparent: true,
    opacity: 0.88,
  }),
  laser: new THREE.MeshBasicMaterial({
    color: 0xffe58a,
    transparent: true,
    opacity: 0.78,
  }),
  gapWarning: new THREE.MeshBasicMaterial({
    color: 0x12161a,
    transparent: true,
    opacity: 0.86,
  }),
};

const environments = [
  {
    background: new THREE.Color(0x0b0712),
    fog: new THREE.Color(0x100815),
    accent: new THREE.Color(0x8b5ac8),
    name: "violet",
  },
  {
    background: new THREE.Color(0x06100e),
    fog: new THREE.Color(0x071814),
    accent: new THREE.Color(0x47c88f),
    name: "green",
  },
  {
    background: new THREE.Color(0x07090d),
    fog: new THREE.Color(0x090a0d),
    accent: new THREE.Color(0xb7c8da),
    name: "open",
  },
];

const skins = {
  default: { accent: 0x2a9fb0, glow: 0x7fd8ff, dark: 0x191d22 },
  ninja: { accent: 0x14181f, glow: 0xfff2df, dark: 0x050608 },
  gold: { accent: 0xc99b2e, glow: 0xffe58a, dark: 0x2a2113 },
  astro: { accent: 0xe8e1d2, glow: 0x9fd7ff, dark: 0x2a3038 },
};

const shopPrices = {
  ninja: 60,
  gold: 90,
  astro: 120,
};

const biomes = [
  { name: "Void", laneHalfWidth: 7.4, deck: 0x303435, rail: 0x171b1e, speed: 1 },
  { name: "Lava", laneHalfWidth: 5.7, deck: 0x3a2723, rail: 0x2b1110, speed: 1.08 },
  { name: "Cyber", laneHalfWidth: 7.2, deck: 0x111817, rail: 0x05140e, speed: 1.5 },
];

const missions = [
  { id: "jumps", text: "בצע 5 קפיצות חבל ברצף", target: 5, reward: 45, value: 0, complete: false },
  { id: "bombs", text: "השמד 3 קוביות צהובות", target: 3, reward: 70, value: 0, complete: false },
  { id: "pacifist", text: "עבור 200 מטר בלי להשמיד קוביה", target: 200, reward: 55, value: 0, complete: false },
];

function getProgression() {
  const warmup = THREE.MathUtils.clamp(world.runTime / 20, 0, 1);
  const scoreFactor = THREE.MathUtils.clamp(score.total / 2500, 0, 1);
  const curve = warmup * 0.55 + scoreFactor * 0.45;
  const comboBonus = world.comboBoostTime > 0 ? 1.16 : 1;
  const feverBonus = world.feverTime > 0 ? 1.45 : 1;
  return {
    runSpeed: THREE.MathUtils.lerp(9.2, 18.5, curve) * comboBonus * feverBonus * biomes[world.biomeIndex].speed,
    enemySpeed: THREE.MathUtils.lerp(4.8, 10.2, curve) * comboBonus * biomes[world.biomeIndex].speed,
    spawnEvery: THREE.MathUtils.lerp(2.15, 0.72, curve),
    hazardEvery: THREE.MathUtils.lerp(6.6, 3.3, curve),
    inputSpeed: THREE.MathUtils.lerp(7.6, 10.2, curve),
  };
}

function persistShop() {
  localStorage.setItem("hookRunnerCoins", String(save.coins));
  localStorage.setItem("hookRunnerRope", String(save.ropeLevel));
  localStorage.setItem("hookRunnerSkin", save.skin);
  localStorage.setItem("hookRunnerSkins", JSON.stringify(save.ownedSkins));
}

function applySkin() {
  const skin = skins[save.skin] ?? skins.default;
  materials.playerAccent.color.setHex(skin.accent);
  materials.playerAccent.emissive.setHex(skin.glow);
  materials.playerGlow.color.setHex(skin.glow);
  materials.playerGlow.emissive.setHex(skin.glow);
  materials.playerDark.color.setHex(skin.dark);
}

function updateShopUi() {
  menuCoinsEl.textContent = String(save.coins);
  ropeCostEl.textContent = String(getRopeCost());
  for (const button of shopButtons) {
    const skin = button.dataset.skin;
    button.classList.toggle("owned", skin ? save.ownedSkins.includes(skin) : false);
    if (skin && save.skin === skin) button.classList.add("owned");
  }
}

function getRopeCost() {
  return 80 + save.ropeLevel * 65;
}

function addCoins(amount) {
  save.coins += amount;
  score.coins += amount;
  persistShop();
  updateShopUi();
  updateHud();
}

function buySkin(skin) {
  if (save.ownedSkins.includes(skin)) {
    save.skin = skin;
  } else if (save.coins >= shopPrices[skin]) {
    save.coins -= shopPrices[skin];
    save.ownedSkins.push(skin);
    save.skin = skin;
  }
  persistShop();
  applySkin();
  updateShopUi();
}

function buyRope() {
  const cost = getRopeCost();
  if (save.coins < cost) return;
  save.coins -= cost;
  save.ropeLevel += 1;
  persistShop();
  updateShopUi();
}

function updateMissionsUi() {
  missionsEl.innerHTML = missions
    .map((mission) => {
      const value = Math.min(mission.target, Math.floor(mission.value));
      return `<div class="mission ${mission.complete ? "complete" : ""}"><strong>${value}/${mission.target}</strong> ${mission.text}</div>`;
    })
    .join("");
}

function progressMission(id, amount) {
  const mission = missions.find((item) => item.id === id);
  if (!mission || mission.complete) return;
  mission.value = Math.min(mission.target, mission.value + amount);
  if (mission.value >= mission.target) {
    mission.complete = true;
    addCoins(mission.reward);
    flashComboHud();
  }
  updateMissionsUi();
}

function addLights() {
  const hemi = new THREE.HemisphereLight(0xa7c7cf, 0x16110d, 1.5);
  scene.add(hemi);

  const key = new THREE.DirectionalLight(0xfff2df, 4.6);
  key.position.set(-7, 12, 8);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.left = -24;
  key.shadow.camera.right = 24;
  key.shadow.camera.top = 24;
  key.shadow.camera.bottom = -24;
  key.shadow.camera.near = 1;
  key.shadow.camera.far = 60;
  scene.add(key);

  const rim = new THREE.DirectionalLight(0x8fb8c5, 2.1);
  rim.position.set(9, 7, -16);
  scene.add(rim);

  const low = new THREE.PointLight(0xcaa889, 55, 34, 2);
  low.position.set(0, 3, 7);
  scene.add(low);
}

function makeRunway() {
  const deckGeometry = new THREE.BoxGeometry(17, 0.55, 42);
  const sideGeometry = new THREE.BoxGeometry(0.35, 0.8, 42);
  const stripeGeometry = new THREE.BoxGeometry(0.08, 0.04, 4.5);
  const stripeMaterial = new THREE.MeshStandardMaterial({
    color: 0xbfc7bf,
    roughness: 0.44,
    metalness: 0.24,
  });

  for (let i = 0; i < 8; i += 1) {
    const segment = new THREE.Group();
    const deck = new THREE.Mesh(deckGeometry, materials.runway);
    deck.receiveShadow = true;
    deck.castShadow = true;
    segment.add(deck);

    for (const x of [-8.7, 8.7]) {
      const rail = new THREE.Mesh(sideGeometry, materials.runwaySide);
      rail.position.set(x, 0.25, 0);
      rail.castShadow = true;
      rail.receiveShadow = true;
      segment.add(rail);
    }

    for (let s = -16; s <= 16; s += 8) {
      const stripe = new THREE.Mesh(stripeGeometry, stripeMaterial);
      stripe.position.set(0, 0.32, s);
      stripe.castShadow = true;
      segment.add(stripe);
    }

    segment.position.z = -i * 42;
    scene.add(segment);
    runwaySegments.push(segment);
  }
}

function makeSpace() {
  const starGeometry = new THREE.IcosahedronGeometry(0.035, 0);
  const starMaterial = new THREE.MeshBasicMaterial({ color: 0xd4d0c7 });
  for (let i = 0; i < 180; i += 1) {
    const star = new THREE.Mesh(starGeometry, starMaterial);
    const side = Math.random() < 0.5 ? -1 : 1;
    star.position.set(
      side * (14 + Math.random() * 38),
      3 + Math.random() * 24,
      22 - Math.random() * 160,
    );
    star.scale.setScalar(0.6 + Math.random() * 2.2);
    scene.add(star);
    stars.push(star);
  }

  const lineGeometry = new THREE.BoxGeometry(0.035, 0.035, 5.8);
  const lineMaterial = new THREE.MeshBasicMaterial({
    color: 0x8cc8ff,
    transparent: true,
    opacity: 0.36,
  });
  for (let i = 0; i < 80; i += 1) {
    const line = new THREE.Mesh(lineGeometry, lineMaterial.clone());
    line.position.set(
      THREE.MathUtils.randFloatSpread(52),
      THREE.MathUtils.randFloat(1.5, 18),
      16 - Math.random() * 150,
    );
    line.rotation.x = THREE.MathUtils.randFloat(-0.18, 0.18);
    line.rotation.y = THREE.MathUtils.randFloat(-0.08, 0.08);
    line.scale.z = THREE.MathUtils.randFloat(0.5, 1.8);
    scene.add(line);
    speedLines.push(line);
  }

  const cloudGeometry = new THREE.PlaneGeometry(18, 11);
  for (let i = 0; i < 18; i += 1) {
    const cloud = new THREE.Mesh(
      cloudGeometry,
      new THREE.MeshBasicMaterial({
        color: environments[i % environments.length].accent,
        transparent: true,
        opacity: 0.08,
        depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    cloud.position.set(
      THREE.MathUtils.randFloatSpread(64),
      THREE.MathUtils.randFloat(5, 24),
      4 - Math.random() * 170,
    );
    cloud.rotation.set(
      THREE.MathUtils.randFloat(-0.8, 0.8),
      THREE.MathUtils.randFloat(-0.5, 0.5),
      THREE.MathUtils.randFloat(0, Math.PI),
    );
    cloud.scale.setScalar(THREE.MathUtils.randFloat(0.8, 2.4));
    scene.add(cloud);
    nebulaClouds.push(cloud);
  }

  const rockGeometry = new THREE.DodecahedronGeometry(0.75, 0);
  const rockMaterial = new THREE.MeshStandardMaterial({
    color: 0x383836,
    roughness: 0.82,
    metalness: 0.08,
  });
  for (let i = 0; i < 30; i += 1) {
    const rock = new THREE.Mesh(rockGeometry, rockMaterial);
    rock.position.set(
      (Math.random() < 0.5 ? -1 : 1) * THREE.MathUtils.randFloat(15, 46),
      THREE.MathUtils.randFloat(0, 16),
      0 - Math.random() * 170,
    );
    rock.scale.setScalar(THREE.MathUtils.randFloat(0.35, 1.8));
    rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    rock.castShadow = true;
    scene.add(rock);
    asteroids.push(rock);
  }
}

function makePlayer() {
  const group = new THREE.Group();
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.42, 0.92, 8, 16), materials.playerDark);
  torso.position.y = 1.24;
  torso.rotation.x = 0.12;
  torso.scale.set(0.86, 1, 0.62);
  torso.castShadow = true;
  torso.receiveShadow = true;
  group.add(torso);

  const chest = new THREE.Mesh(new THREE.BoxGeometry(0.78, 0.74, 0.28), materials.player);
  chest.position.set(0, 1.34, -0.12);
  chest.rotation.x = 0.08;
  chest.castShadow = true;
  group.add(chest);

  const core = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.44, 0.05), materials.playerGlow);
  core.position.set(0, 1.35, -0.29);
  group.add(core);

  const head = new THREE.Mesh(new THREE.BoxGeometry(0.58, 0.45, 0.52), materials.playerDark);
  head.position.y = 2.06;
  head.castShadow = true;
  group.add(head);

  const visor = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.08, 0.06), materials.playerGlow);
  visor.position.set(0, 2.1, -0.28);
  group.add(visor);

  const shoulderGeometry = new THREE.BoxGeometry(0.34, 0.2, 0.5);
  const armGeometry = new THREE.CapsuleGeometry(0.13, 0.62, 6, 10);
  for (const side of [-1, 1]) {
    const shoulder = new THREE.Mesh(shoulderGeometry, materials.playerAccent);
    shoulder.position.set(side * 0.62, 1.62, -0.04);
    shoulder.castShadow = true;
    group.add(shoulder);

    const arm = new THREE.Mesh(armGeometry, materials.playerDark);
    arm.position.set(side * 0.74, 1.1, -0.06);
    arm.rotation.z = side * 0.28;
    arm.castShadow = true;
    group.add(arm);

    const forearm = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.54, 0.22), materials.playerGlow);
    forearm.position.set(side * 0.82, 0.82, -0.12);
    forearm.rotation.z = side * 0.18;
    forearm.castShadow = true;
    group.add(forearm);
  }

  const legGeometry = new THREE.CapsuleGeometry(0.15, 0.7, 6, 10);
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(legGeometry, materials.playerDark);
    leg.position.set(side * 0.24, 0.56, 0.02);
    leg.rotation.z = side * 0.12;
    leg.castShadow = true;
    group.add(leg);

    const boot = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.18, 0.72), materials.playerAccent);
    boot.position.set(side * 0.26, 0.22, -0.16);
    boot.castShadow = true;
    group.add(boot);
  }

  const backpack = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.8, 0.22), materials.playerAccent);
  backpack.position.set(0, 1.26, 0.32);
  backpack.castShadow = true;
  group.add(backpack);

  const thrusterGeometry = new THREE.CylinderGeometry(0.08, 0.12, 0.28, 12);
  for (const x of [-0.16, 0.16]) {
    const thruster = new THREE.Mesh(thrusterGeometry, materials.playerGlow);
    thruster.position.set(x, 1.03, 0.48);
    thruster.rotation.x = Math.PI / 2;
    group.add(thruster);
  }

  const body = torso;

  group.position.set(0, 0, 0);
  group.userData = {
    velocityY: 0,
    grounded: true,
    state: "run",
    stateTime: 0,
    stateDuration: 0,
    start: new THREE.Vector3(),
    target: new THREE.Vector3(),
    targetEnemy: null,
    shotProgress: 0,
    model: body,
  };
  scene.add(group);
  return group;
}

const player = makePlayer();

function makePlayerTrail() {
  const geometry = new THREE.BoxGeometry(0.08, 0.08, 1);
  for (let i = 0; i < 28; i += 1) {
    const segment = new THREE.Mesh(
      geometry,
      new THREE.MeshBasicMaterial({
        color: i % 2 === 0 ? 0x47c8ff : 0x95ecff,
        transparent: true,
        opacity: 0,
        depthWrite: false,
      }),
    );
    segment.position.copy(player.position);
    scene.add(segment);
    trailSegments.push({
      mesh: segment,
      age: 1,
      life: 0.36 + i * 0.01,
      side: i % 2 === 0 ? -1 : 1,
    });
  }
}

const hookMaterial = new THREE.LineBasicMaterial({
  color: 0x8ee7ff,
  transparent: true,
  opacity: 0,
});
const hookGlowMaterial = new THREE.LineBasicMaterial({
  color: 0x2f9cff,
  transparent: true,
  opacity: 0,
});
const hookGeometry = new THREE.BufferGeometry().setFromPoints([
  new THREE.Vector3(),
  new THREE.Vector3(),
]);
const hookLine = new THREE.Line(hookGeometry, hookMaterial);
const hookGlowLine = new THREE.Line(hookGeometry.clone(), hookGlowMaterial);
scene.add(hookLine);
scene.add(hookGlowLine);

function makeEnemy(options = {}) {
  const group = new THREE.Group();
  const roll = Math.random();
  const type = options.type ?? (roll < 0.18 ? "shield" : roll < 0.34 ? "bomb" : "normal");
  const coreMaterial = type === "shield" ? materials.shieldEnemy : type === "bomb" ? materials.bombEnemy : materials.enemy;
  const core = new THREE.Mesh(new THREE.OctahedronGeometry(1.25, 1), coreMaterial);
  core.castShadow = true;
  core.receiveShadow = true;
  core.userData.enemyRoot = group;
  group.add(core);

  const inner = new THREE.Mesh(
    new THREE.BoxGeometry(1.15, 1.15, 1.15),
    type === "shield" ? materials.shieldEnemy : type === "bomb" ? materials.bombEnemy : materials.enemy,
  );
  inner.rotation.set(0.4, 0.7, 0.2);
  inner.scale.set(0.7, 0.7, 0.7);
  inner.userData.enemyRoot = group;
  group.add(inner);

  const bevel = new THREE.Mesh(
    new THREE.TorusGeometry(1.28, 0.055, 8, 4),
    type === "shield" ? materials.playerGlow : type === "bomb" ? materials.bombEnemy : materials.enemyEdge,
  );
  bevel.rotation.x = Math.PI / 2;
  bevel.castShadow = true;
  bevel.userData.enemyRoot = group;
  group.add(bevel);

  const frameMaterial = type === "shield" ? materials.playerGlow : type === "bomb" ? materials.bombEnemy : materials.enemyEdge;
  for (const axis of ["x", "y", "z"]) {
    const frame = new THREE.Mesh(new THREE.BoxGeometry(0.1, 2.05, 0.1), frameMaterial);
    if (axis === "x") frame.rotation.z = Math.PI / 2;
    if (axis === "z") frame.rotation.x = Math.PI / 2;
    frame.castShadow = true;
    frame.userData.enemyRoot = group;
    group.add(frame);
  }

  if (type === "shield") {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.55, 0.045, 8, 32), materials.playerGlow);
    ring.rotation.x = Math.PI / 2;
    ring.userData.enemyRoot = group;
    group.add(ring);
  }

  if (type === "bomb") {
    const fuse = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 1.45, 10), materials.playerGlow);
    fuse.position.set(0, 0, 0);
    fuse.rotation.x = Math.PI / 2;
    fuse.userData.enemyRoot = group;
    group.add(fuse);
  }

  group.position.set(
    options.x ?? THREE.MathUtils.randFloatSpread(world.laneHalfWidth * 1.6),
    options.y ?? 1.05,
    options.z ?? player.position.z - 64 - Math.random() * 18,
  );
  group.rotation.set(
    THREE.MathUtils.randFloat(-0.14, 0.14),
    THREE.MathUtils.randFloat(0, Math.PI),
    THREE.MathUtils.randFloat(-0.14, 0.14),
  );
  group.userData = {
    destroyed: false,
    dodged: false,
    type,
    hitPulse: 0,
    spinner: Math.random() < 0.55,
    spinAxis: new THREE.Vector3(
      THREE.MathUtils.randFloatSpread(1),
      THREE.MathUtils.randFloat(0.35, 1),
      THREE.MathUtils.randFloatSpread(1),
    ).normalize(),
    spinSpeed: THREE.MathUtils.randFloat(1.4, 3.8),
    baseX: group.position.x,
    sway: world.biomeIndex === 1 || options.sway,
  };
  scene.add(group);
  enemies.push(group);
}

function makeHazard() {
  const type = Math.random() < 0.5 ? "gap" : "laser";
  const group = new THREE.Group();
  if (type === "gap") {
    const pit = new THREE.Mesh(new THREE.BoxGeometry(16.2, 0.08, 7.4), materials.gapWarning);
    pit.position.y = 0.36;
    pit.receiveShadow = true;
    group.add(pit);
    for (const x of [-5.2, 0, 5.2]) {
      const strip = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.06, 0.16), materials.laser);
      strip.position.set(x, 0.46, -3.45);
      group.add(strip);
    }
  } else {
    const beam = new THREE.Mesh(new THREE.BoxGeometry(16.5, 0.16, 0.16), materials.laser);
    beam.position.y = 1.55;
    group.add(beam);
    const topBeam = beam.clone();
    topBeam.position.y = 2.25;
    topBeam.material = materials.laser.clone();
    topBeam.material.opacity = 0.44;
    group.add(topBeam);
    for (const x of [-8.1, 8.1]) {
      const post = new THREE.Mesh(new THREE.BoxGeometry(0.22, 2.8, 0.22), materials.enemyEdge);
      post.position.set(x, 1.2, 0);
      post.castShadow = true;
      group.add(post);
    }
  }
  group.position.set(0, 0, player.position.z - 82 - Math.random() * 18);
  group.userData = { type, cleared: false };
  scene.add(group);
  hazards.push(group);
  if (type === "gap") {
    makeEnemy({
      type: "normal",
      x: THREE.MathUtils.randFloatSpread(world.laneHalfWidth * 1.25),
      y: 2.25,
      z: group.position.z - 2.2,
    });
  }
}

function makeCrystal() {
  const crystal = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.42, 1),
    new THREE.MeshStandardMaterial({
      color: 0x7fd8ff,
      emissive: 0x1b8cc2,
      emissiveIntensity: 1.6,
      roughness: 0.18,
      metalness: 0.35,
      transparent: true,
      opacity: 0.9,
    }),
  );
  crystal.position.set(
    THREE.MathUtils.randFloatSpread(world.laneHalfWidth * 1.55),
    1.05,
    player.position.z - 34 - Math.random() * 38,
  );
  crystal.castShadow = true;
  scene.add(crystal);
  crystals.push(crystal);
}

function spawnFragments(position) {
  const fragmentGeometry = new THREE.BoxGeometry(0.32, 0.32, 0.32);
  for (let i = 0; i < 22; i += 1) {
    const mesh = new THREE.Mesh(fragmentGeometry, materials.fragment);
    mesh.position.copy(position);
    mesh.position.add(new THREE.Vector3(
      THREE.MathUtils.randFloatSpread(0.9),
      THREE.MathUtils.randFloatSpread(0.7),
      THREE.MathUtils.randFloatSpread(0.9),
    ));
    mesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    mesh.castShadow = true;
    scene.add(mesh);
    fragments.push({
      mesh,
      velocity: new THREE.Vector3(
        THREE.MathUtils.randFloatSpread(8),
        THREE.MathUtils.randFloat(4, 11),
        THREE.MathUtils.randFloatSpread(8),
      ),
      spin: new THREE.Vector3(
        THREE.MathUtils.randFloatSpread(9),
        THREE.MathUtils.randFloatSpread(9),
        THREE.MathUtils.randFloatSpread(9),
      ),
      life: 1.4,
    });
  }
}

function spawnParticles(position) {
  const count = 90;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const velocities = [];

  for (let i = 0; i < count; i += 1) {
    positions[i * 3] = position.x;
    positions[i * 3 + 1] = position.y;
    positions[i * 3 + 2] = position.z;
    velocities.push(new THREE.Vector3(
      THREE.MathUtils.randFloatSpread(13),
      THREE.MathUtils.randFloat(1, 12),
      THREE.MathUtils.randFloatSpread(13),
    ));
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({
    color: 0xf0c486,
    size: 0.07,
    transparent: true,
    opacity: 1,
    depthWrite: false,
  });
  const points = new THREE.Points(geometry, material);
  scene.add(points);
  particleBursts.push({ points, velocities, life: 0.8 });
}

function scoreAction(kind, basePoints) {
  const wasBelowComboBoost = world.destroyStreak < 3;
  world.combo += 1;
  world.comboTimer = 1.25;
  const multiplier = world.feverTime > 0 ? Math.max(2, world.combo) : Math.max(1, world.combo);
  score.total += basePoints * multiplier;
  if (kind === "destroy" || kind === "bomb") {
    score.destroyed += 1;
    world.destroyStreak += 1;
    world.noDestroyDistance = 0;
    missions.find((mission) => mission.id === "pacifist").value = 0;
  } else {
    world.destroyStreak = 0;
    progressMission("jumps", 1);
  }
  if (kind === "bomb") progressMission("bombs", 1);
  if (kind === "dodge") score.dodged += 1;
  world.feverMeter = Math.min(100, world.feverMeter + (kind === "bomb" ? 28 : 14 + Math.min(world.combo, 8)));
  if (world.feverMeter >= 100 && world.feverTime <= 0) {
    world.feverTime = 10;
    world.feverMeter = 0;
    world.speedEffect = 2.4;
  }
  if (wasBelowComboBoost && world.destroyStreak >= 3) {
    world.comboBoostTime = 4.2;
    world.speedEffect = Math.max(world.speedEffect, 1.75);
    flashComboHud();
  }
  updateHud();
}

function flashComboHud() {
  for (const element of [hudEl, scoreEl, comboEl]) {
    element.classList.remove("combo-pop", "combo-score");
    void element.offsetWidth;
  }
  hudEl.classList.add("combo-pop");
  scoreEl.classList.add("combo-score");
  comboEl.classList.add("combo-score");
}

function openChainWindow() {
  if (enemies.filter((enemy) => !enemy.userData.destroyed).length < 2) {
    const roll = Math.random();
    makeEnemy({
      type: roll < 0.18 ? "shield" : roll < 0.36 ? "bomb" : "normal",
      x: THREE.MathUtils.randFloatSpread(world.laneHalfWidth * 1.35),
      y: THREE.MathUtils.randFloat(1.4, 2.6),
      z: player.position.z - THREE.MathUtils.randFloat(36, 54),
    });
  }
  player.userData.state = "chain";
  player.userData.stateTime = 0;
  player.userData.stateDuration = 0.5;
  player.userData.targetEnemy = null;
  player.userData.shotProgress = 0;
  player.position.y = Math.max(player.position.y, 2.7);
  world.bulletTime = 0.5;
  world.speedEffect = Math.max(world.speedEffect, 1.4);
}

function shatterEnemy(enemy, options = {}) {
  if (!enemy || enemy.userData.destroyed) return;
  enemy.userData.destroyed = true;
  const pos = enemy.position.clone();
  scene.remove(enemy);
  spawnFragments(pos);
  spawnParticles(pos);
  if (options.score !== false) scoreAction(enemy.userData.type === "bomb" ? "bomb" : "destroy", 10);
  if (enemy.userData.type === "bomb") detonateBomb(pos, enemy);
}

function detonateBomb(position, sourceEnemy) {
  world.shake = Math.max(world.shake, 0.75);
  spawnParticles(position);
  for (const enemy of [...enemies]) {
    if (enemy === sourceEnemy || enemy.userData.destroyed) continue;
    if (enemy.position.distanceTo(position) < 8.5) {
      shatterEnemy(enemy, { score: false });
      score.total += 80 * Math.max(1, world.combo);
    }
  }
  updateHud();
}

function updateHud() {
  scoreEl.textContent = String(score.total);
  coinsEl.textContent = String(score.coins);
  menuCoinsEl.textContent = String(save.coins);
  destroyedEl.textContent = String(score.destroyed);
  dodgedEl.textContent = String(score.dodged);
  comboEl.textContent = `x${Math.max(1, world.combo)}`;
  feverEl.textContent = world.feverTime > 0 ? `${Math.ceil(world.feverTime)}s` : `${Math.floor(world.feverMeter)}%`;
}

function startAttack(enemy) {
  if (enemy.userData.type === "shield" && world.feverTime <= 0) {
    endRun();
    return;
  }
  const target = enemy.position.clone();
  target.y = world.combo > 0 || player.position.y > 1 ? 2.6 : 0;
  player.userData.state = "hookAttack";
  player.userData.stateTime = 0;
  player.userData.stateDuration = 0.14;
  player.userData.start.copy(player.position);
  player.userData.target.copy(target);
  player.userData.targetEnemy = enemy;
  player.userData.shotProgress = 0;
  world.speedEffect = 1;
  hookMaterial.opacity = 1;
  hookGlowMaterial.opacity = 0.55;
}

function startDodge(enemy) {
  enemy.userData.dodged = true;
  const target = enemy.position.clone();
  target.z -= 2.8;
  target.y = 2.8;
  player.userData.state = "hookDodge";
  player.userData.stateTime = 0;
  player.userData.stateDuration = 0.15;
  player.userData.start.copy(player.position);
  player.userData.target.copy(target);
  player.userData.targetEnemy = enemy;
  player.userData.shotProgress = 0;
  world.speedEffect = 1;
  hookMaterial.opacity = 1;
  hookGlowMaterial.opacity = 0.55;
  scoreAction("dodge", 100);
}

function pickEnemy(event) {
  ensureAudio();
  if (!world.started || world.gameOver) return;
  if (!["run", "chain"].includes(player.userData.state)) return;
  pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
  pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  if (boss) {
    const bossHits = raycaster.intersectObjects(boss.children, false);
    if (bossHits.length || findNearestScreenBoss(event.clientX, event.clientY)) {
      hitBoss();
      return;
    }
  }
  const meshes = enemies.flatMap((enemy) => enemy.children);
  const hits = raycaster.intersectObjects(meshes, false);
  let enemy = hits[0]?.object.userData.enemyRoot;
  if (!enemy) enemy = findNearestScreenEnemy(event.clientX, event.clientY);
  if (!enemy || enemy.userData.destroyed) return;
  if (keys.has("Space")) startDodge(enemy);
  else startAttack(enemy);
}

function findNearestScreenEnemy(clientX, clientY) {
  let nearest = null;
  let nearestDistance = (player.userData.state === "chain" ? 180 : 115) + save.ropeLevel * 36;
  for (const enemy of enemies) {
    if (enemy.userData.destroyed) continue;
    const projected = enemy.position.clone().project(camera);
    if (projected.z < -1 || projected.z > 1) continue;
    const x = (projected.x * 0.5 + 0.5) * window.innerWidth;
    const y = (-projected.y * 0.5 + 0.5) * window.innerHeight;
    if (x < -120 || x > window.innerWidth + 120 || y < -120 || y > window.innerHeight + 120) continue;
    const distance = Math.hypot(x - clientX, y - clientY);
    if (distance < nearestDistance) {
      nearestDistance = distance;
      nearest = enemy;
    }
  }
  return nearest;
}

function findNearestScreenBoss(clientX, clientY) {
  if (!boss) return false;
  const projected = boss.position.clone().project(camera);
  if (projected.z < -1 || projected.z > 1) return false;
  const x = (projected.x * 0.5 + 0.5) * window.innerWidth;
  const y = (-projected.y * 0.5 + 0.5) * window.innerHeight;
  return Math.hypot(x - clientX, y - clientY) < 190 + save.ropeLevel * 40;
}

function updatePlayer(dt) {
  const progression = getProgression();
  const input = tmpVec.set(0, 0, 0);
  if (keys.has("KeyA")) input.x -= 1;
  if (keys.has("KeyD")) input.x += 1;
  if (keys.has("KeyW")) input.z -= 1;
  if (keys.has("KeyS")) input.z += 1;

  if (player.userData.state === "run") {
    if (world.comboTimer <= 0 && world.feverTime <= 0) world.combo = 0;
    if (input.lengthSq() > 0) input.normalize();
    player.position.x += input.x * progression.inputSpeed * dt;
    player.position.z += input.z * progression.inputSpeed * dt;
    player.position.z -= progression.runSpeed * dt;
    player.position.x = THREE.MathUtils.clamp(player.position.x, -world.laneHalfWidth, world.laneHalfWidth);
    player.position.y = 0;
    player.rotation.y = THREE.MathUtils.lerp(player.rotation.y, input.x * -0.28, 0.12);
    player.rotation.x = Math.sin(timer.getElapsed() * 10) * 0.025;
  } else if (player.userData.state === "chain") {
    player.userData.stateTime += dt / Math.max(world.timeScale, 0.35);
    player.position.z -= progression.runSpeed * dt * 0.35;
    player.position.y = THREE.MathUtils.lerp(player.position.y, 2.8 + Math.sin(timer.getElapsed() * 10) * 0.18, dt * 8);
    player.rotation.x = Math.sin(timer.getElapsed() * 8) * 0.22;
    player.rotation.z = Math.sin(timer.getElapsed() * 6) * 0.18;
    if (player.userData.stateTime >= player.userData.stateDuration) {
      player.userData.state = "run";
      player.position.y = 0;
      player.rotation.set(0, player.rotation.y, 0);
    }
  } else if (player.userData.state === "hookAttack" || player.userData.state === "hookDodge") {
    player.userData.stateTime += dt;
    player.userData.shotProgress = Math.min(1, player.userData.stateTime / player.userData.stateDuration);
    player.rotation.z = Math.sin(player.userData.shotProgress * Math.PI) * 0.22;
    player.rotation.x = -Math.sin(player.userData.shotProgress * Math.PI) * 0.12;
    if (player.userData.shotProgress >= 1) {
      player.userData.state = player.userData.state === "hookAttack" ? "attack" : "dodge";
      player.userData.stateTime = 0;
      player.userData.stateDuration = player.userData.state === "attack" ? 0.34 : 0.84;
      player.userData.start.copy(player.position);
    }
  } else {
    player.userData.stateTime += dt;
    const t = Math.min(player.userData.stateTime / player.userData.stateDuration, 1);
    const eased = 1 - (1 - t) ** 3;
    player.position.lerpVectors(player.userData.start, player.userData.target, eased);

    if (player.userData.state === "dodge") {
      player.position.y = Math.sin(t * Math.PI) * 5.1;
      player.rotation.x = -Math.sin(t * Math.PI) * 1.15;
      player.rotation.y += 11 * dt;
      player.rotation.z = Math.sin(t * Math.PI * 2) * 0.42;
    } else {
      player.position.y = Math.sin(t * Math.PI) * 0.55;
      player.rotation.y += 32 * dt;
      player.rotation.x = Math.sin(t * Math.PI * 2) * 0.45;
      player.rotation.z = -Math.sin(t * Math.PI) * 1.2;
    }

    if (t >= 1) {
      if (player.userData.state === "attack") shatterEnemy(player.userData.targetEnemy);
      openChainWindow();
      player.userData.shotProgress = 0;
    }
  }
}

function updateHook() {
  const activeEnemy = player.userData.targetEnemy;
  if (player.userData.state === "run" || !activeEnemy || activeEnemy.userData.destroyed) {
    hookMaterial.opacity = Math.max(0, hookMaterial.opacity - 0.08);
    hookGlowMaterial.opacity = Math.max(0, hookGlowMaterial.opacity - 0.08);
  } else {
    hookMaterial.opacity = 1;
    hookGlowMaterial.opacity = player.userData.state.startsWith("hook") ? 0.8 : 0.48;
  }

  if (hookMaterial.opacity <= 0) return;
  const positions = hookLine.geometry.attributes.position;
  const glowPositions = hookGlowLine.geometry.attributes.position;
  const from = player.localToWorld(tmpVec.set(0, 1.45, -0.2));
  const target = activeEnemy ? tmpVecB.copy(activeEnemy.position).setY(activeEnemy.position.y + 0.2) : player.position;
  const draw = player.userData.state.startsWith("hook") ? player.userData.shotProgress : 1;
  const to = new THREE.Vector3().lerpVectors(from, target, draw);
  positions.setXYZ(0, from.x, from.y, from.z);
  positions.setXYZ(1, to.x, to.y, to.z);
  glowPositions.setXYZ(0, from.x, from.y, from.z);
  glowPositions.setXYZ(1, to.x, to.y, to.z);
  positions.needsUpdate = true;
  glowPositions.needsUpdate = true;
}

function updateEnemies(dt) {
  const progression = getProgression();
  world.spawnTimer -= dt;
  if (world.spawnTimer <= 0) {
    makeEnemy();
    world.spawnEvery = progression.spawnEvery;
    world.spawnTimer = progression.spawnEvery;
  }

  world.hazardTimer -= dt;
  if (world.hazardTimer <= 0) {
    makeHazard();
    world.hazardTimer = THREE.MathUtils.randFloat(progression.hazardEvery, progression.hazardEvery + 1.8);
  }

  for (let i = enemies.length - 1; i >= 0; i -= 1) {
    const enemy = enemies[i];
    if (enemy.userData.destroyed) {
      enemies.splice(i, 1);
      continue;
    }
    enemy.position.z += progression.enemySpeed * dt;
    if (enemy.userData.sway) {
      enemy.position.x = THREE.MathUtils.clamp(
        enemy.userData.baseX + Math.sin(timer.getElapsed() * 2.4 + enemy.position.z * 0.08) * 2.1,
        -world.laneHalfWidth,
        world.laneHalfWidth,
      );
    }
    if (enemy.userData.spinner) {
      enemy.rotateOnAxis(enemy.userData.spinAxis, enemy.userData.spinSpeed * dt);
      enemy.rotation.z += dt * 1.2;
    } else {
      enemy.rotation.x += dt * 0.55;
      enemy.rotation.y += dt * 0.75;
    }
    enemy.userData.hitPulse = Math.max(0, enemy.userData.hitPulse - dt);

    const dx = Math.abs(enemy.position.x - player.position.x);
    const dz = Math.abs(enemy.position.z - player.position.z);
    const dy = Math.abs((enemy.position.y - 1) - player.position.y);
    if (
      world.feverTime <= 0 &&
      !enemy.userData.dodged &&
      dx < 1.35 &&
      dz < 1.35 &&
      dy < 1.75 &&
      player.userData.state === "run"
    ) {
      endRun();
    }

    if (enemy.position.z > player.position.z + 24) {
      if (!enemy.userData.dodged && !enemy.userData.destroyed) {
        world.combo = 0;
        world.destroyStreak = 0;
        world.comboTimer = 0;
      }
      scene.remove(enemy);
      enemies.splice(i, 1);
    }
  }
}

function updateHazards(dt) {
  const progression = getProgression();
  for (let i = hazards.length - 1; i >= 0; i -= 1) {
    const hazard = hazards[i];
    hazard.position.z += progression.enemySpeed * dt;
    for (const child of hazard.children) {
      if (hazard.userData.type === "laser") child.scale.x = 1 + Math.sin(timer.getElapsed() * 16) * 0.025;
    }

    const dz = Math.abs(hazard.position.z - player.position.z);
    if (world.feverTime <= 0 && dz < 2.2 && !hazard.userData.cleared) {
      const airborne = player.position.y > (hazard.userData.type === "laser" ? 2.75 : 1.7);
      const grappling = player.userData.state !== "run";
      if (!airborne && !grappling) endRun();
      else hazard.userData.cleared = true;
    }

    if (hazard.position.z > player.position.z + 24) {
      scene.remove(hazard);
      hazards.splice(i, 1);
    }
  }
}

function updateCrystals(dt) {
  const progression = getProgression();
  world.coinTimer -= dt;
  if (world.coinTimer <= 0) {
    makeCrystal();
    world.coinTimer = THREE.MathUtils.randFloat(0.75, 1.45);
  }

  for (let i = crystals.length - 1; i >= 0; i -= 1) {
    const crystal = crystals[i];
    crystal.position.z += progression.enemySpeed * dt;
    crystal.rotation.y += dt * 2.8;
    crystal.rotation.x += dt * 1.4;
    if (crystal.position.distanceTo(player.position) < 1.45) {
      scene.remove(crystal);
      crystals.splice(i, 1);
      addCoins(1);
      continue;
    }
    if (crystal.position.z > player.position.z + 22) {
      scene.remove(crystal);
      crystals.splice(i, 1);
    }
  }
}

function spawnBoss() {
  world.bossActive = true;
  world.bossHits = 0;
  world.bossAttackTimer = 1.2;
  world.bossWarningTimer = 1.4;
  bossWarningEl.hidden = false;
  boss = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(5.2, 5.2, 2.8),
    new THREE.MeshStandardMaterial({
      color: 0x681516,
      emissive: 0x7a0909,
      emissiveIntensity: 1.3,
      roughness: 0.28,
      metalness: 0.45,
    }),
  );
  body.castShadow = true;
  body.userData.bossRoot = boss;
  boss.add(body);
  for (const x of [-1.2, 1.2]) {
    const eye = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.36, 0.08), materials.laser);
    eye.position.set(x, 0.65, -1.45);
    eye.userData.bossRoot = boss;
    boss.add(eye);
  }
  boss.position.set(0, 3.2, player.position.z - 44);
  boss.userData = { destroyed: false };
  scene.add(boss);
}

function hitBoss() {
  if (!boss || boss.userData.destroyed) return;
  world.bossHits += 1;
  world.speedEffect = 1.9;
  spawnParticles(boss.position);
  if (world.bossHits >= 3) {
    boss.userData.destroyed = true;
    scene.remove(boss);
    boss = null;
    world.bossActive = false;
    world.nextBossScore += 500;
    score.total += 250;
    addCoins(35);
    flashComboHud();
  }
}

function updateBoss(dt) {
  if (!world.bossActive && score.total >= world.nextBossScore) spawnBoss();
  if (world.bossWarningTimer > 0) {
    world.bossWarningTimer -= dt;
    if (world.bossWarningTimer <= 0) bossWarningEl.hidden = true;
  }
  if (!boss) return;
  boss.position.z = THREE.MathUtils.lerp(boss.position.z, player.position.z - 42, dt * 1.6);
  boss.position.x = Math.sin(timer.getElapsed() * 1.2) * 2.8;
  boss.rotation.y = Math.sin(timer.getElapsed() * 1.7) * 0.18;
  world.bossAttackTimer -= dt;
  if (world.bossAttackTimer <= 0) {
    world.bossAttackTimer = THREE.MathUtils.randFloat(1.1, 1.9);
    if (Math.random() < 0.55) makeEnemy({ type: "normal", x: THREE.MathUtils.randFloatSpread(world.laneHalfWidth * 1.4), z: player.position.z - 46 });
    else makeHazard();
  }
}

function updateBiomes(dt) {
  if (!world.started) return;
  world.biomeTimer += dt;
  if (world.biomeTimer >= 30) {
    world.biomeTimer = 0;
    world.biomeIndex = (world.biomeIndex + 1) % biomes.length;
  }
  const biome = biomes[world.biomeIndex];
  world.laneHalfWidth = THREE.MathUtils.lerp(world.laneHalfWidth, biome.laneHalfWidth, dt * 0.45);
  materials.runway.color.lerp(new THREE.Color(biome.deck), dt * 0.45);
  materials.runwaySide.color.lerp(new THREE.Color(biome.rail), dt * 0.45);
}

function updateRunway() {
  const segmentLength = 42;
  for (const segment of runwaySegments) {
    while (segment.position.z > player.position.z + segmentLength) {
      segment.position.z -= segmentLength * runwaySegments.length;
    }
    while (segment.position.z < player.position.z - segmentLength * (runwaySegments.length - 1)) {
      segment.position.z += segmentLength * runwaySegments.length;
    }
  }
}

function updateFragments(dt) {
  for (let i = fragments.length - 1; i >= 0; i -= 1) {
    const item = fragments[i];
    item.life -= dt;
    item.velocity.y -= 16 * dt;
    item.mesh.position.addScaledVector(item.velocity, dt);
    item.mesh.rotation.x += item.spin.x * dt;
    item.mesh.rotation.y += item.spin.y * dt;
    item.mesh.rotation.z += item.spin.z * dt;
    item.mesh.scale.setScalar(Math.max(0.05, item.life / 1.4));
    if (item.life <= 0) {
      scene.remove(item.mesh);
      fragments.splice(i, 1);
    }
  }
}

function updateParticles(dt) {
  for (let b = particleBursts.length - 1; b >= 0; b -= 1) {
    const burst = particleBursts[b];
    burst.life -= dt;
    const positions = burst.points.geometry.attributes.position;
    for (let i = 0; i < burst.velocities.length; i += 1) {
      const velocity = burst.velocities[i];
      velocity.y -= 10 * dt;
      positions.array[i * 3] += velocity.x * dt;
      positions.array[i * 3 + 1] += velocity.y * dt;
      positions.array[i * 3 + 2] += velocity.z * dt;
    }
    positions.needsUpdate = true;
    burst.points.material.opacity = Math.max(0, burst.life / 0.8);
    if (burst.life <= 0) {
      scene.remove(burst.points);
      particleBursts.splice(b, 1);
    }
  }
}

function updateStars(dt) {
  const speedBoost = 1 + world.speedEffect * 4.5;
  for (const star of stars) {
    star.position.z += dt * 3.4 * speedBoost;
    if (star.position.z > player.position.z + 34) {
      star.position.z = player.position.z - 130 - Math.random() * 40;
      star.position.x = (Math.random() < 0.5 ? -1 : 1) * (14 + Math.random() * 38);
      star.position.y = 3 + Math.random() * 24;
    }
  }
}

function updateSpaceScenery(dt) {
  world.environmentTimer += dt;
  if (world.environmentTimer > 18) {
    world.environmentTimer = 0;
    world.environmentIndex = (world.environmentIndex + 1) % environments.length;
  }

  const env = environments[world.environmentIndex];
  scene.background.lerp(env.background, dt * 0.12);
  scene.fog.color.lerp(env.fog, dt * 0.16);
  scene.fog.density = THREE.MathUtils.lerp(scene.fog.density, 0.018 + world.speedEffect * 0.008, dt * 2.2);

  const speedBoost = 1 + world.speedEffect * 7;
  for (const line of speedLines) {
    line.position.z += dt * (26 + world.runSpeed) * speedBoost;
    line.scale.z = THREE.MathUtils.lerp(line.scale.z, 1.2 + world.speedEffect * 3.8, dt * 8);
    line.material.opacity = THREE.MathUtils.lerp(line.material.opacity, 0.22 + world.speedEffect * 0.44, dt * 7);
    if (line.position.z > player.position.z + 32) {
      line.position.z = player.position.z - 135 - Math.random() * 50;
      line.position.x = THREE.MathUtils.randFloatSpread(56);
      line.position.y = THREE.MathUtils.randFloat(1.5, 19);
    }
  }

  for (let i = 0; i < nebulaClouds.length; i += 1) {
    const cloud = nebulaClouds[i];
    cloud.position.z += dt * 5.5 * speedBoost;
    cloud.material.color.lerp(environments[(world.environmentIndex + i) % environments.length].accent, dt * 0.2);
    cloud.material.opacity = 0.05 + (i % 3) * 0.02;
    cloud.rotation.z += dt * 0.025;
    if (cloud.position.z > player.position.z + 24) {
      cloud.position.z = player.position.z - 150 - Math.random() * 70;
      cloud.position.x = THREE.MathUtils.randFloatSpread(66);
      cloud.position.y = THREE.MathUtils.randFloat(5, 24);
    }
  }

  for (const rock of asteroids) {
    rock.position.z += dt * 8.5 * speedBoost;
    rock.rotation.x += dt * 0.35;
    rock.rotation.y += dt * 0.27;
    if (rock.position.z > player.position.z + 30) {
      rock.position.z = player.position.z - 155 - Math.random() * 55;
      rock.position.x = (Math.random() < 0.5 ? -1 : 1) * THREE.MathUtils.randFloat(15, 48);
      rock.position.y = THREE.MathUtils.randFloat(0, 17);
    }
  }
}

function updatePlayerTrail(dt) {
  const stateBoost = player.userData.state === "run" ? 1 : 2.6;
  const spawnRate = 0.065 / stateBoost;
  world.distance += dt;
  if (world.distance > spawnRate) {
    world.distance = 0;
    const segment = trailSegments.shift();
    const side = segment.side;
    const offset = tmpVec.set(side * 0.26, 1.08, 0.58);
    player.localToWorld(offset);
    segment.mesh.position.copy(offset);
    segment.mesh.rotation.copy(player.rotation);
    segment.mesh.scale.set(1 + world.speedEffect * 1.8, 1, 2.3 + world.speedEffect * 5.2);
    segment.age = 0;
    trailSegments.push(segment);
  }

  for (const segment of trailSegments) {
    segment.age += dt;
    const p = Math.min(1, segment.age / segment.life);
    segment.mesh.position.z += dt * (10 + world.speedEffect * 35);
    segment.mesh.position.y -= dt * 0.18;
    segment.mesh.material.opacity = (1 - p) * (0.58 + world.speedEffect * 0.28);
    segment.mesh.scale.x = THREE.MathUtils.lerp(segment.mesh.scale.x, 0.18, dt * 5);
  }
}

function updateScreenEffects(dt) {
  world.comboBoostTime = Math.max(0, world.comboBoostTime - dt);
  world.comboTimer = Math.max(0, world.comboTimer - dt);
  world.bulletTime = Math.max(0, world.bulletTime - dt);
  world.feverTime = Math.max(0, world.feverTime - dt);
  world.timeScale = world.bulletTime > 0 ? 0.42 : 1;
  if (world.feverTime > 0) {
    world.speedEffect = Math.max(world.speedEffect, 2.2);
  } else {
    world.speedEffect = Math.max(0, world.speedEffect - dt * 1.7);
  }
  if (world.started && !world.gameOver) {
    const progression = getProgression();
    world.noDestroyDistance += progression.runSpeed * dt;
    progressMission("pacifist", progression.runSpeed * dt);
  }
  world.shake = Math.max(0, world.shake - dt * 2.8);
  if (world.comboTimer <= 0 && player.userData.state === "run" && world.feverTime <= 0) world.combo = 0;
  updateHud();
  updateBeat(dt);
}

function ensureAudio() {
  if (world.audioStarted) return;
  audioContext = new AudioContext();
  world.audioStarted = true;
}

function updateBeat(dt) {
  if (!audioContext) return;
  const bpm = world.feverTime > 0 ? 176 : 92 + Math.min(world.combo, 8) * 7;
  world.beatTimer -= dt;
  if (world.beatTimer > 0) return;
  world.beatTimer = 60 / bpm;
  const now = audioContext.currentTime;
  const osc = audioContext.createOscillator();
  const gain = audioContext.createGain();
  osc.type = world.feverTime > 0 ? "sawtooth" : "triangle";
  osc.frequency.setValueAtTime(world.feverTime > 0 ? 150 : 92 + world.combo * 8, now);
  gain.gain.setValueAtTime(0.0001, now);
  gain.gain.exponentialRampToValueAtTime(world.feverTime > 0 ? 0.06 : 0.025, now + 0.015);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.09);
  osc.connect(gain).connect(audioContext.destination);
  osc.start(now);
  osc.stop(now + 0.1);
}

function updateCamera(dt) {
  const pullBoost = player.userData.state === "attack" || player.userData.state === "dodge" ? 1 : world.speedEffect;
  const cameraTarget = tmpVec.set(player.position.x * 0.38, 1.6 + pullBoost * 0.8, player.position.z - 6 - pullBoost * 2.4);
  const cameraPosition = tmpVecB.set(
    player.position.x + 10.5 + pullBoost * 1.6,
    player.position.y + 13.5 + pullBoost * 1.2,
    player.position.z + 15 + pullBoost * 3.5,
  );
  camera.position.lerp(cameraPosition, 1 - Math.exp(-dt * 5.5));
  if (world.shake > 0) {
    const shake = world.shake * world.shake;
    camera.position.x += THREE.MathUtils.randFloatSpread(shake * 1.25);
    camera.position.y += THREE.MathUtils.randFloatSpread(shake * 0.9);
    camera.position.z += THREE.MathUtils.randFloatSpread(shake * 1.25);
  }
  camera.lookAt(cameraTarget);
}

function endRun() {
  if (world.feverTime > 0) return;
  world.gameOver = true;
  world.destroyStreak = 0;
  world.shake = 1.8;
  statusEl.hidden = false;
}

function resetGame() {
  world.gameOver = false;
  world.runTime = 0;
  score.destroyed = 0;
  score.dodged = 0;
  score.total = 0;
  score.coins = 0;
  world.spawnEvery = getProgression().spawnEvery;
  world.spawnTimer = 1.2;
  player.position.set(0, 0, 0);
  player.rotation.set(0, 0, 0);
  player.userData.state = "run";
  player.userData.targetEnemy = null;
  player.userData.shotProgress = 0;
  world.speedEffect = 0;
  world.shake = 0;
  world.distance = 0;
  world.combo = 0;
  world.comboTimer = 0;
  world.destroyStreak = 0;
  world.comboBoostTime = 0;
  world.bulletTime = 0;
  world.feverMeter = 0;
  world.feverTime = 0;
  world.timeScale = 1;
  world.hazardTimer = 2.4;
  world.coinTimer = 1.1;
  world.bossActive = false;
  world.bossHits = 0;
  world.bossAttackTimer = 0;
  world.bossWarningTimer = 0;
  world.biomeIndex = 0;
  world.biomeTimer = 0;
  world.nextBossScore = 500;
  world.noDestroyDistance = 0;
  bossWarningEl.hidden = true;
  materials.runway.color.setHex(biomes[0].deck);
  materials.runwaySide.color.setHex(biomes[0].rail);
  hookMaterial.opacity = 0;
  hookGlowMaterial.opacity = 0;
  statusEl.hidden = true;
  for (const enemy of enemies) scene.remove(enemy);
  for (const hazard of hazards) scene.remove(hazard);
  for (const crystal of crystals) scene.remove(crystal);
  for (const item of fragments) scene.remove(item.mesh);
  for (const burst of particleBursts) scene.remove(burst.points);
  if (boss) scene.remove(boss);
  boss = null;
  enemies.length = 0;
  hazards.length = 0;
  crystals.length = 0;
  fragments.length = 0;
  particleBursts.length = 0;
  for (const mission of missions) {
    mission.value = 0;
    mission.complete = false;
  }
  updateMissionsUi();
  updateHud();
}

function startGame() {
  introEl.hidden = true;
  world.started = true;
  resetGame();
}

function animate(timestamp) {
  requestAnimationFrame(animate);
  timer.update(timestamp);
  const rawDt = Math.min(timer.getDelta(), 0.033);
  world.timeScale = world.bulletTime > 0 ? 0.42 : 1;
  const dt = rawDt * world.timeScale * (world.feverTime > 0 ? 1.55 : 1);

  if (!world.started) {
    updateStars(rawDt * 0.35);
    updateSpaceScenery(rawDt * 0.35);
    updatePlayerTrail(rawDt * 0.25);
  } else if (!world.gameOver) {
    world.runTime += rawDt;
    updateBiomes(rawDt);
    updatePlayer(dt);
    updateEnemies(dt);
    updateHazards(dt);
    updateCrystals(dt);
    updateBoss(dt);
    updateRunway();
    updateFragments(dt);
    updateParticles(dt);
    updateStars(dt);
    updateSpaceScenery(dt);
    updatePlayerTrail(dt);
    updateHook();
  } else {
    updateBoss(dt);
    updateFragments(dt);
    updateParticles(dt);
    updateStars(dt);
    updateSpaceScenery(dt);
    updatePlayerTrail(dt);
    hookMaterial.opacity = Math.max(0, hookMaterial.opacity - 0.06);
    hookGlowMaterial.opacity = Math.max(0, hookGlowMaterial.opacity - 0.06);
  }

  updateScreenEffects(rawDt);
  updateCamera(dt);
  renderer.render(scene, camera);
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

if (import.meta.env.DEV) {
  window.__HOOK_RUNNER__ = {
    targets() {
      return enemies
        .filter((enemy) => !enemy.userData.destroyed)
        .map((enemy) => {
          const projected = enemy.position.clone().project(camera);
          return {
            x: (projected.x * 0.5 + 0.5) * window.innerWidth,
            y: (-projected.y * 0.5 + 0.5) * window.innerHeight,
            z: projected.z,
            type: enemy.userData.type,
            world: enemy.position.toArray(),
            visible:
              projected.z >= -1 &&
              projected.z <= 1 &&
              (projected.x * 0.5 + 0.5) * window.innerWidth >= 0 &&
              (projected.x * 0.5 + 0.5) * window.innerWidth <= window.innerWidth &&
              (-projected.y * 0.5 + 0.5) * window.innerHeight >= 0 &&
              (-projected.y * 0.5 + 0.5) * window.innerHeight <= window.innerHeight,
          };
        });
    },
    state() {
      return {
        playerState: player.userData.state,
        player: player.position.toArray(),
        enemyCount: enemies.length,
        score: { ...score },
        combo: world.combo,
        feverMeter: world.feverMeter,
        feverTime: world.feverTime,
        hazardCount: hazards.length,
        started: world.started,
        runTime: world.runTime,
        spawnEvery: world.spawnEvery,
        comboBoostTime: world.comboBoostTime,
        bossActive: world.bossActive,
        biomeIndex: world.biomeIndex,
        coins: score.coins,
        wallet: save.coins,
        ropeLevel: save.ropeLevel,
        gameOver: world.gameOver,
      };
    },
  };
}

window.addEventListener("keydown", (event) => {
  keys.add(event.code);
  if (event.code === "KeyR" && world.gameOver) {
    world.started = true;
    resetGame();
  }
});
window.addEventListener("keyup", (event) => keys.delete(event.code));
window.addEventListener("pointerdown", pickEnemy);
window.addEventListener("resize", onResize);
startButtonEl.addEventListener("click", () => {
  ensureAudio();
  startGame();
});
for (const button of shopButtons) {
  button.addEventListener("click", () => {
    const skin = button.dataset.skin;
    if (skin) buySkin(skin);
    if (button.dataset.upgrade === "rope") buyRope();
  });
}

addLights();
makeRunway();
makeSpace();
makePlayerTrail();
applySkin();
updateShopUi();
updateMissionsUi();
resetGame();
animate();
