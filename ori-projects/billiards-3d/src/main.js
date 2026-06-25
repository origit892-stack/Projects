import * as THREE from "three";

const canvas = document.querySelector("#gameCanvas");
const shell = document.querySelector(".game-shell");
const startMenu = document.querySelector("#startMenu");
const startButton = document.querySelector("#startButton");
const turnLabel = document.querySelector("#turnLabel");
const scoreLabel = document.querySelector("#scoreLabel");
const messageBox = document.querySelector("#messageBox");
const controlHint = document.querySelector("#controlHint");
const powerFill = document.querySelector("#powerFill");
const ballLists = {
  solid: document.querySelector("#solidBalls"),
  stripe: document.querySelector("#stripeBalls"),
};

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x120b08);
scene.fog = new THREE.Fog(0x120b08, 9, 22);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.28;

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
camera.position.set(0, 8.1, 7.2);
camera.lookAt(0, 0, 0);

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const tablePlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -0.04);

const TABLE = {
  width: 8.4,
  depth: 4.45,
  railHeight: 0.34,
  railThickness: 0.34,
  ballRadius: 0.15,
  pocketRadius: 0.29,
};

const halfW = TABLE.width / 2;
const halfD = TABLE.depth / 2;
const playableHalfW = halfW - TABLE.railThickness - TABLE.ballRadius;
const playableHalfD = halfD - TABLE.railThickness - TABLE.ballRadius;
const cueStart = new THREE.Vector2(-2.9, 0);

const balls = [];
const pockets = [];
const keys = new Set();
const skins = {
  cueBall: "classic",
  cueStick: "wood",
};

const audio = {
  ctx: null,
  enabled: false,
  lastBallClick: 0,
  lastRailHit: 0,
};

const DEFAULT_SHOT_POWER = 5.7;
const MIN_SHOT_POWER = 2.9;
const MAX_SHOT_POWER = 8.4;

const aim = {
  angle: 0,
  turnSpeed: 2.2,
  shotPower: DEFAULT_SHOT_POWER,
  charging: false,
  chargeStart: 0,
  chargeValue: 0,
};

const game = {
  started: false,
  mode: "local",
  currentPlayer: 1,
  scores: { 1: 0, 2: 0 },
  groups: { 1: null, 2: null },
  tableOpen: true,
  ballInHand: false,
  gameOver: false,
  breakPending: true,
};

const ai = {
  player: 2,
  nextActionAt: 0,
  thinking: false,
};

let shot = createShotState();
let playerRig;
let cueStickMesh;
let predictionLine;
let lastFrameTime = performance.now();

setupLights();
createEnvironment();
createTable();
createPockets();
createBalls();
predictionLine = createPredictionLine();
playerRig = createPlayerRig();
updateHud();
setMessage("בחרו סקינים והתחילו משחק.");

document.querySelectorAll(".skin-grid").forEach((grid) => {
  grid.addEventListener("click", (event) => {
    const card = event.target.closest(".skin-card");
    if (!card) return;

    grid.querySelectorAll(".skin-card").forEach((item) => item.classList.remove("is-selected"));
    card.classList.add("is-selected");
    skins[grid.dataset.skinGroup] = card.dataset.skin;
    applySelectedSkins();
  });
});

document.querySelectorAll("[data-mode-group] .mode-card").forEach((card) => {
  card.addEventListener("click", () => {
    document.querySelectorAll("[data-mode-group] .mode-card").forEach((item) => item.classList.remove("is-selected"));
    card.classList.add("is-selected");
    game.mode = card.dataset.mode;
    updateHud();
  });
});

startButton.addEventListener("click", () => beginGame(true));

if (new URLSearchParams(window.location.search).has("autostart")) {
  window.setTimeout(() => beginGame(false), 250);
}

function beginGame(withSound) {
  if (game.started) return;
  if (withSound) ensureAudio();
  game.started = true;
  startMenu.classList.add("is-hidden");
  shell.classList.remove("is-menu-open");
  updateHud();
  setMessage(game.mode === "ai"
    ? "שחקן 1 פותח מול המחשב. החזיקו Space לעוצמה ושחררו לחבטה."
    : "שחקן 1 פותח. החזיקו Space לעוצמה ושחררו לחבטה.");
}

window.addEventListener("keydown", handleKeyDown);
window.addEventListener("keyup", handleKeyUp);
window.addEventListener("pointerdown", placeCueBallFromPointer);
window.addEventListener("resize", resize);
resize();
renderer.setAnimationLoop(animate);

function setupLights() {
  scene.add(new THREE.HemisphereLight(0x7c563b, 0x0b0705, 0.55));

  const tableLight = new THREE.SpotLight(0xffd28b, 32, 9.5, Math.PI / 4.7, 0.62, 1.15);
  tableLight.position.set(0, 5.4, 0.15);
  tableLight.target.position.set(0, 0, 0);
  tableLight.castShadow = true;
  tableLight.shadow.mapSize.set(2048, 2048);
  tableLight.shadow.camera.near = 1;
  tableLight.shadow.camera.far = 12;
  scene.add(tableLight, tableLight.target);

  const rimLight = new THREE.PointLight(0xb15f32, 1.2, 9);
  rimLight.position.set(-5.8, 2.2, -4.6);
  scene.add(rimLight);

  const barLight = new THREE.PointLight(0xffb15d, 1.6, 7);
  barLight.position.set(5.6, 2.6, -4.8);
  scene.add(barLight);

  const tableFill = new THREE.PointLight(0xffd7a0, 1.15, 7.5);
  tableFill.position.set(0, 2.4, 1.2);
  scene.add(tableFill);

  const playerFill = new THREE.PointLight(0xffc28a, 1.7, 3.2);
  playerFill.position.set(-4.35, 1.6, 0.2);
  scene.add(playerFill);
}

function createEnvironment() {
  const woodFloor = new THREE.MeshStandardMaterial({
    map: createWoodTexture(0x2d140b, 0x7d3d1f),
    roughness: 0.46,
    metalness: 0.03,
  });
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(22, 16),
    woodFloor
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.22;
  floor.receiveShadow = true;
  scene.add(floor);

  const wallMaterial = new THREE.MeshStandardMaterial({
    color: 0x2a160f,
    roughness: 0.62,
    metalness: 0.02,
  });
  [
    { size: [22, 5.2, 0.18], position: [0, 2.2, -7.2] },
    { size: [22, 5.2, 0.18], position: [0, 2.2, 7.2] },
    { size: [0.18, 5.2, 16], position: [-10.8, 2.2, 0] },
    { size: [0.18, 5.2, 16], position: [10.8, 2.2, 0] },
  ].forEach(({ size, position }) => {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(...size), wallMaterial);
    wall.position.set(...position);
    wall.receiveShadow = true;
    scene.add(wall);
  });

  createPendantLamp();
  createBackgroundTables();
  createWallSigns();
}

function createPendantLamp() {
  const cableMaterial = new THREE.MeshStandardMaterial({ color: 0x0b0b0b, roughness: 0.28, metalness: 0.55 });
  const shadeMaterial = new THREE.MeshStandardMaterial({ color: 0x16201a, roughness: 0.22, metalness: 0.46 });
  const glowMaterial = new THREE.MeshStandardMaterial({
    color: 0xffe5a8,
    emissive: 0xffd68a,
    emissiveIntensity: 1.6,
    roughness: 0.2,
  });

  [-1.25, 0, 1.25].forEach((x) => {
    const cable = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 1.2, 12), cableMaterial);
    cable.position.set(x, 4.78, 0);
    scene.add(cable);

    const shade = new THREE.Mesh(new THREE.ConeGeometry(0.44, 0.48, 48, 1, true), shadeMaterial);
    shade.position.set(x, 4.12, 0);
    shade.rotation.x = Math.PI;
    shade.castShadow = false;
    scene.add(shade);

    const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.18, 24, 16), glowMaterial);
    bulb.position.set(x, 3.91, 0);
    scene.add(bulb);
  });
}

function createBackgroundTables() {
  const wood = new THREE.MeshStandardMaterial({ map: createWoodTexture(0x34170d, 0x8b4727), roughness: 0.32, metalness: 0.05 });
  const felt = new THREE.MeshStandardMaterial({ color: 0x0f6d48, roughness: 0.82 });
  const legMaterial = new THREE.MeshStandardMaterial({ color: 0x1b0c07, roughness: 0.46 });

  [
    [-6.2, -4.9, 0.62],
    [6.1, -4.65, 0.62],
    [-6.8, 4.8, 0.54],
    [6.9, 4.7, 0.54],
  ].forEach(([x, z, scale]) => {
    const group = new THREE.Group();
    const top = new THREE.Mesh(new THREE.BoxGeometry(4.2, 0.16, 2.1), wood);
    top.position.y = 0.62;
    const cloth = new THREE.Mesh(new THREE.BoxGeometry(3.55, 0.05, 1.52), felt);
    cloth.position.y = 0.75;
    group.add(top, cloth);

    [-1.65, 1.65].forEach((lx) => {
      [-0.78, 0.78].forEach((lz) => {
        const leg = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.76, 0.18), legMaterial);
        leg.position.set(lx, 0.2, lz);
        group.add(leg);
      });
    });

    group.position.set(x, -0.04, z);
    group.scale.setScalar(scale);
    group.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    scene.add(group);
  });
}

function createWallSigns() {
  const signs = [
    { text: "HIGH STAKES", x: 5.7, y: 2.95, z: -7.08, color: "#ffd77a" },
    { text: "BILLIARDS", x: 5.7, y: 2.55, z: -7.07, color: "#55f0a1" },
    { text: "CASINO ELITE", x: -4.8, y: 2.72, z: -7.08, color: "#ff8a61" },
  ];

  signs.forEach((sign) => {
    const texture = createSignTexture(sign.text, sign.color);
    const material = new THREE.MeshStandardMaterial({
      map: texture,
      emissive: new THREE.Color(0xffffff),
      emissiveMap: texture,
      emissiveIntensity: 0.62,
      roughness: 0.45,
    });
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2.35, 0.58), material);
    mesh.position.set(sign.x, sign.y, sign.z);
    scene.add(mesh);
  });
}

function createSignTexture(text, color) {
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = 512;
  textureCanvas.height = 160;
  const ctx = textureCanvas.getContext("2d");
  ctx.fillStyle = "#140b08";
  ctx.fillRect(0, 0, 512, 160);
  ctx.strokeStyle = color;
  ctx.lineWidth = 10;
  ctx.strokeRect(18, 18, 476, 124);
  ctx.fillStyle = color;
  ctx.font = "bold 48px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 256, 82);
  const texture = new THREE.CanvasTexture(textureCanvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createWoodTexture(darkColor, lightColor) {
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = 512;
  textureCanvas.height = 512;
  const ctx = textureCanvas.getContext("2d");
  const dark = `#${darkColor.toString(16).padStart(6, "0")}`;
  const light = `#${lightColor.toString(16).padStart(6, "0")}`;
  ctx.fillStyle = dark;
  ctx.fillRect(0, 0, 512, 512);
  for (let y = 0; y < 512; y += 10) {
    const wave = Math.sin(y * 0.045) * 16 + Math.sin(y * 0.013) * 22;
    ctx.strokeStyle = y % 30 === 0 ? light : "rgba(255, 196, 122, 0.18)";
    ctx.lineWidth = y % 30 === 0 ? 3 : 1;
    ctx.beginPath();
    ctx.moveTo(0, y);
    for (let x = 0; x <= 512; x += 18) {
      ctx.lineTo(x, y + Math.sin((x + wave) * 0.035) * 8);
    }
    ctx.stroke();
  }
  const texture = new THREE.CanvasTexture(textureCanvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(3, 3);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createFeltTexture() {
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = 512;
  textureCanvas.height = 512;
  const ctx = textureCanvas.getContext("2d");
  ctx.fillStyle = "#0d6a46";
  ctx.fillRect(0, 0, 512, 512);
  const image = ctx.getImageData(0, 0, 512, 512);
  for (let i = 0; i < image.data.length; i += 4) {
    const grain = Math.random() * 24 - 12;
    image.data[i] = Math.max(0, image.data[i] + grain * 0.35);
    image.data[i + 1] = Math.max(0, image.data[i + 1] + grain);
    image.data[i + 2] = Math.max(0, image.data[i + 2] + grain * 0.45);
  }
  ctx.putImageData(image, 0, 0);
  ctx.strokeStyle = "rgba(255,255,255,0.035)";
  for (let y = 0; y < 512; y += 8) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(512, y + Math.sin(y) * 2);
    ctx.stroke();
  }
  const texture = new THREE.CanvasTexture(textureCanvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 2);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createTable() {
  const felt = new THREE.Mesh(
    new THREE.BoxGeometry(TABLE.width, 0.16, TABLE.depth),
    new THREE.MeshStandardMaterial({
      color: 0x0f6d47,
      map: createFeltTexture(),
      emissive: 0x03170d,
      emissiveIntensity: 0.14,
      roughness: 0.93,
      metalness: 0,
    })
  );
  felt.receiveShadow = true;
  felt.castShadow = true;
  scene.add(felt);

  const woodMaterial = new THREE.MeshStandardMaterial({
    color: 0x5b2514,
    map: createWoodTexture(0x2a1008, 0x9b5430),
    roughness: 0.24,
    metalness: 0.08,
  });
  const longRailGeometry = new THREE.BoxGeometry(TABLE.width + TABLE.railThickness * 2, TABLE.railHeight, TABLE.railThickness);
  const shortRailGeometry = new THREE.BoxGeometry(TABLE.railThickness, TABLE.railHeight, TABLE.depth);

  [
    { geometry: longRailGeometry, position: [0, TABLE.railHeight / 2, halfD + TABLE.railThickness / 2] },
    { geometry: longRailGeometry, position: [0, TABLE.railHeight / 2, -halfD - TABLE.railThickness / 2] },
    { geometry: shortRailGeometry, position: [halfW + TABLE.railThickness / 2, TABLE.railHeight / 2, 0] },
    { geometry: shortRailGeometry, position: [-halfW - TABLE.railThickness / 2, TABLE.railHeight / 2, 0] },
  ].forEach(({ geometry, position }) => {
    const rail = new THREE.Mesh(geometry, woodMaterial);
    rail.position.set(...position);
    rail.castShadow = true;
    rail.receiveShadow = true;
    scene.add(rail);
  });

  const metalMaterial = new THREE.MeshStandardMaterial({
    color: 0xb59466,
    roughness: 0.18,
    metalness: 0.76,
  });
  [
    [-halfW - TABLE.railThickness / 2, -halfD - TABLE.railThickness / 2],
    [halfW + TABLE.railThickness / 2, -halfD - TABLE.railThickness / 2],
    [-halfW - TABLE.railThickness / 2, halfD + TABLE.railThickness / 2],
    [halfW + TABLE.railThickness / 2, halfD + TABLE.railThickness / 2],
  ].forEach(([x, z]) => {
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.08, 40), metalMaterial);
    cap.position.set(x, TABLE.railHeight + 0.04, z);
    cap.scale.z = 0.72;
    cap.rotation.x = Math.PI / 2;
    cap.castShadow = true;
    cap.receiveShadow = true;
    scene.add(cap);
  });
}

function createPockets() {
  const pocketPositions = [
    [-playableHalfW, -playableHalfD],
    [0, -playableHalfD],
    [playableHalfW, -playableHalfD],
    [-playableHalfW, playableHalfD],
    [0, playableHalfD],
    [playableHalfW, playableHalfD],
  ];

  const material = new THREE.MeshStandardMaterial({
    color: 0x010101,
    emissive: 0x020202,
    emissiveIntensity: 0.35,
    roughness: 0.48,
    metalness: 0.05,
  });
  const rimMaterial = new THREE.MeshStandardMaterial({
    color: 0xc69a5d,
    emissive: 0x3a220d,
    emissiveIntensity: 0.32,
    roughness: 0.2,
    metalness: 0.78,
  });
  pocketPositions.forEach(([x, z]) => {
    const pocket = new THREE.Mesh(new THREE.CylinderGeometry(TABLE.pocketRadius, TABLE.pocketRadius, 0.035, 48), material);
    pocket.position.set(x, 0.085, z);
    pocket.receiveShadow = true;
    scene.add(pocket);

    const rim = new THREE.Mesh(new THREE.TorusGeometry(TABLE.pocketRadius * 1.04, 0.035, 14, 54), rimMaterial);
    rim.position.set(x, 0.125, z);
    rim.rotation.x = Math.PI / 2;
    rim.castShadow = true;
    rim.receiveShadow = true;
    scene.add(rim);

    pockets.push(new THREE.Vector2(x, z));
  });
}

function createBalls() {
  addBall({ id: "cue", number: 0, group: "cue", color: 0xffffff, x: cueStart.x, z: cueStart.y });

  const rack = [
    [1, "solid", 0xf2c232], [9, "stripe", 0xf2c232], [2, "solid", 0x2664d8],
    [10, "stripe", 0x2664d8], [8, "eight", 0x111111], [3, "solid", 0xd83232],
    [11, "stripe", 0xd83232], [4, "solid", 0x7c3fc6], [12, "stripe", 0x7c3fc6],
    [5, "solid", 0xff8b1a], [13, "stripe", 0xff8b1a], [6, "solid", 0x1f8f4f],
    [14, "stripe", 0x1f8f4f], [7, "solid", 0x7a2f18], [15, "stripe", 0x7a2f18],
  ];

  const spacing = TABLE.ballRadius * 2.08;
  const startX = 2.1;
  let index = 0;
  for (let row = 0; row < 5; row += 1) {
    for (let col = 0; col <= row; col += 1) {
      const [number, group, color] = rack[index];
      const x = startX + row * spacing;
      const z = (col - row / 2) * spacing;
      addBall({ id: `ball-${number}`, number, group, color, x, z });
      index += 1;
    }
  }
}

function addBall({ id, number, group, color, x, z }) {
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(TABLE.ballRadius, 48, 32),
    createBallMaterial({ number, group, color })
  );
  mesh.position.set(x, TABLE.ballRadius + 0.02, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  scene.add(mesh);

  const ball = {
    id,
    number,
    group,
    color,
    mesh,
    radius: TABLE.ballRadius,
    active: true,
    velocity: new THREE.Vector2(0, 0),
    start: new THREE.Vector2(x, z),
  };
  balls.push(ball);
}

function createBallMaterial({ number, group, color }) {
  if (number === 0) return createCueBallMaterial();
  if (group !== "stripe") {
    return new THREE.MeshStandardMaterial({ color, roughness: 0.045, metalness: 0.08 });
  }

  return new THREE.MeshStandardMaterial({
    map: createStripeTexture(color, number),
    roughness: 0.045,
    metalness: 0.08,
  });
}

function createCueBallMaterial() {
  if (skins.cueBall === "fire") {
    return new THREE.MeshStandardMaterial({ map: createFireTexture(), roughness: 0.045, metalness: 0.1 });
  }
  if (skins.cueBall === "gold") {
    return new THREE.MeshStandardMaterial({ color: 0xf2c14e, roughness: 0.035, metalness: 0.82 });
  }
  return new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.04, metalness: 0.06 });
}

function createStripeTexture(color, number) {
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = 256;
  textureCanvas.height = 128;
  const ctx = textureCanvas.getContext("2d");
  ctx.fillStyle = "#f8f8f0";
  ctx.fillRect(0, 0, textureCanvas.width, textureCanvas.height);
  ctx.fillStyle = `#${color.toString(16).padStart(6, "0")}`;
  ctx.fillRect(0, 44, textureCanvas.width, 40);
  ctx.fillStyle = "#ffffff";
  ctx.beginPath();
  ctx.arc(128, 64, 24, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#111111";
  ctx.font = "bold 26px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(number, 128, 64);
  const texture = new THREE.CanvasTexture(textureCanvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createFireTexture() {
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = 256;
  textureCanvas.height = 128;
  const ctx = textureCanvas.getContext("2d");
  const gradient = ctx.createRadialGradient(86, 42, 12, 128, 64, 150);
  gradient.addColorStop(0, "#fff2a6");
  gradient.addColorStop(0.25, "#ff9b23");
  gradient.addColorStop(0.62, "#c92721");
  gradient.addColorStop(1, "#4b0909");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, textureCanvas.width, textureCanvas.height);
  ctx.strokeStyle = "rgba(255,255,255,0.42)";
  ctx.lineWidth = 8;
  for (let i = 0; i < 5; i += 1) {
    ctx.beginPath();
    ctx.moveTo(i * 58, 128);
    ctx.quadraticCurveTo(36 + i * 44, 60, 18 + i * 52, 0);
    ctx.stroke();
  }
  const texture = new THREE.CanvasTexture(textureCanvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createPredictionLine() {
  const group = new THREE.Group();
  const material = new THREE.MeshStandardMaterial({
    color: 0xffdc4a,
    emissive: 0x4b3200,
    emissiveIntensity: 0.32,
    roughness: 0.36,
  });

  for (let i = 0; i < 18; i += 1) {
    const dot = new THREE.Mesh(new THREE.SphereGeometry(0.035, 16, 10), material);
    dot.position.set(0.42 + i * 0.22, TABLE.ballRadius * 2.32, 0);
    group.add(dot);
  }

  scene.add(group);
  return group;
}

function createPlayerRig() {
  const rig = new THREE.Group();
  const skin = new THREE.MeshStandardMaterial({ color: 0xd5a071, emissive: 0x2b1408, emissiveIntensity: 0.18, roughness: 0.38 });
  const shirt = new THREE.MeshStandardMaterial({ color: 0x214c62, emissive: 0x07141a, emissiveIntensity: 0.22, roughness: 0.48 });
  const vest = new THREE.MeshStandardMaterial({ color: 0x15191c, emissive: 0x050505, emissiveIntensity: 0.18, roughness: 0.32, metalness: 0.05 });
  const hair = new THREE.MeshStandardMaterial({ color: 0x2b1a10, emissive: 0x090403, emissiveIntensity: 0.12, roughness: 0.42 });

  const shoulders = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.24, 0.58), shirt);
  shoulders.position.set(-0.12, 1.0, 0);
  shoulders.rotation.z = -0.28;
  shoulders.castShadow = true;
  rig.add(shoulders);

  const chest = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.34, 0.44), vest);
  chest.position.set(-0.26, 0.78, 0);
  chest.rotation.z = -0.42;
  chest.castShadow = true;
  rig.add(chest);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 24, 18), skin);
  head.position.set(-0.48, 1.28, 0);
  head.castShadow = true;
  rig.add(head);

  const cap = new THREE.Mesh(new THREE.SphereGeometry(0.185, 24, 10, 0, Math.PI * 2, 0, Math.PI / 2), hair);
  cap.position.copy(head.position);
  cap.position.y += 0.03;
  cap.castShadow = true;
  rig.add(cap);

  const armGeometry = new THREE.CylinderGeometry(0.044, 0.044, 1.12, 16);
  [-0.16, 0.16].forEach((z) => {
    const arm = new THREE.Mesh(armGeometry, skin);
    arm.position.set(0.34, 0.78, z);
    arm.rotation.z = Math.PI / 2;
    arm.rotation.y = z > 0 ? -0.08 : 0.08;
    arm.castShadow = true;
    rig.add(arm);
  });

  [-0.16, 0.16].forEach((z) => {
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.07, 18, 12), skin);
    hand.position.set(0.9, 0.78, z);
    hand.castShadow = true;
    rig.add(hand);
  });

  cueStickMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.017, 1, 24), createCueStickMaterial());
  cueStickMesh.rotation.z = Math.PI / 2;
  cueStickMesh.position.set(1.0, 0.72, 0);
  cueStickMesh.castShadow = true;
  rig.add(cueStickMesh);

  scene.add(rig);
  return rig;
}

function createCueStickMaterial() {
  if (skins.cueStick === "carbon") {
    return new THREE.MeshStandardMaterial({ color: 0x111518, roughness: 0.18, metalness: 0.36 });
  }
  if (skins.cueStick === "gold") {
    return new THREE.MeshStandardMaterial({ color: 0xdfb546, roughness: 0.12, metalness: 0.78 });
  }
  return new THREE.MeshStandardMaterial({ color: 0x8a5528, roughness: 0.28, metalness: 0.02 });
}

function applySelectedSkins() {
  const cueBall = getCueBall();
  cueBall.mesh.material.dispose();
  cueBall.mesh.material = createCueBallMaterial();
  if (cueStickMesh) {
    cueStickMesh.material.dispose();
    cueStickMesh.material = createCueStickMaterial();
  }
}

function handleKeyDown(event) {
  const wasHeld = keys.has(event.code);
  keys.add(event.code);

  if (isStrikeKey(event.code) && !wasHeld) {
    event.preventDefault();
    if (game.ballInHand) {
      setMessage(`שחקן ${game.currentPlayer}: מקמו את הכדור הלבן, ואז לחצו Enter כדי לנעול.`);
      return;
    }
    startPowerCharge();
  }

  if (event.code === "Enter" && game.ballInHand) {
    event.preventDefault();
    confirmBallInHand();
  }
}

function handleKeyUp(event) {
  keys.delete(event.code);
  if (isStrikeKey(event.code)) {
    event.preventDefault();
    releasePowerCharge(true);
  }
}

function isStrikeKey(code) {
  if (!game.started || game.gameOver || isAiTurn()) return false;
  if (game.mode === "local" && game.currentPlayer === 2) return code === "KeyW";
  return code === "Space";
}

function startPowerCharge() {
  if (!game.started || game.gameOver || game.ballInHand || shot.striking || areBallsMoving() || aim.charging) return;
  aim.charging = true;
  aim.chargeStart = performance.now();
  aim.chargeValue = 0;
}

function releasePowerCharge(playSound = true) {
  if (!aim.charging) return;
  updatePowerCharge();
  aim.shotPower = THREE.MathUtils.lerp(MIN_SHOT_POWER, MAX_SHOT_POWER, aim.chargeValue);
  aim.charging = false;
  startCueStrike(playSound);
}

function startCueStrike(playSound = true) {
  if (!game.started || game.gameOver || game.ballInHand || shot.striking || areBallsMoving()) return;

  if (playSound) {
    ensureAudio();
    playStrikeSound();
  }
  shot = createShotState();
  shot.active = true;
  shot.isBreak = game.breakPending;
  shot.striking = true;
  shot.strikeTime = 0;
  if (shot.isBreak) aim.shotPower = Math.max(aim.shotPower, 7.6);
  updatePowerMeter(0);
}

function animate() {
  const now = performance.now();
  const delta = Math.min((now - lastFrameTime) / 1000, 0.033);
  lastFrameTime = now;

  updateAim(delta);
  updatePowerCharge();
  updateStrike(delta);
  if (game.started && !game.gameOver) stepPhysics(delta);
  updateAi(delta);
  updatePredictionLine();
  updatePlayerRig();

  renderer.render(scene, camera);
}

function updateAim(delta) {
  if (!game.started || game.gameOver || areBallsMoving() || shot.striking || isAiTurn()) return;
  if (game.ballInHand) {
    updateBallInHand(delta);
    return;
  }
  const controls = getActiveControls();
  if (keys.has(controls.left)) aim.angle += aim.turnSpeed * delta;
  if (keys.has(controls.right)) aim.angle -= aim.turnSpeed * delta;
}

function updateBallInHand(delta) {
  const cueBall = getCueBall();
  const speed = 2.15;
  let dx = 0;
  let dz = 0;
  const controls = getActiveControls();

  if (keys.has("ArrowLeft") || keys.has(controls.left)) dx -= speed * delta;
  if (keys.has("ArrowRight") || keys.has(controls.right)) dx += speed * delta;
  if (keys.has("ArrowUp") || keys.has("KeyW")) dz -= speed * delta;
  if (keys.has("ArrowDown") || keys.has("KeyS")) dz += speed * delta;
  if (dx === 0 && dz === 0) return;

  const x = THREE.MathUtils.clamp(cueBall.mesh.position.x + dx, -playableHalfW + 0.08, playableHalfW - 0.08);
  const z = THREE.MathUtils.clamp(cueBall.mesh.position.z + dz, -playableHalfD + 0.08, playableHalfD - 0.08);
  const blocked = balls.some((ball) => ball !== cueBall && ball.active && distance2D(ball.mesh.position.x, ball.mesh.position.z, x, z) < TABLE.ballRadius * 2.3);
  if (!blocked) cueBall.mesh.position.set(x, TABLE.ballRadius + 0.02, z);
}

function confirmBallInHand() {
  if (!game.ballInHand) return;
  game.ballInHand = false;
  setMessage(`שחקן ${game.currentPlayer}: כוונו וחבטו.`);
}

function updatePowerCharge() {
  if (!aim.charging) return;
  const elapsed = (performance.now() - aim.chargeStart) / 1000;
  const wave = (Math.sin(elapsed * Math.PI * 0.92 - Math.PI / 2) + 1) / 2;
  aim.chargeValue = THREE.MathUtils.clamp(wave, 0, 1);
  updatePowerMeter(aim.chargeValue);
}

function updatePowerMeter(value = aim.chargeValue) {
  if (!powerFill) return;
  powerFill.style.width = `${Math.round(THREE.MathUtils.clamp(value, 0, 1) * 100)}%`;
}

function updateAi() {
  if (!isAiTurn()) {
    ai.thinking = false;
    return;
  }

  const now = performance.now();
  if (shot.striking || areBallsMoving()) {
    ai.thinking = false;
    return;
  }

  if (!ai.thinking) {
    ai.thinking = true;
    ai.nextActionAt = now + 2000;
    setMessage("המחשב חושב על המכה הבאה...");
    return;
  }

  if (now < ai.nextActionAt) return;

  if (game.ballInHand) {
    placeCueBallForAi();
    confirmBallInHand();
    ai.nextActionAt = now + 900;
    return;
  }

  const plan = chooseAiShot();
  if (!plan) {
    switchTurn();
    ai.thinking = false;
    updateHud();
    setMessage("המחשב לא מצא מכה חוקית. התור חוזר לשחקן 1.");
    return;
  }

  aim.angle = plan.angle;
  aim.shotPower = THREE.MathUtils.clamp(plan.power + THREE.MathUtils.randFloat(-0.35, 0.45), 4.0, MAX_SHOT_POWER);
  ai.thinking = false;
  startCueStrike(audio.enabled);
}

function chooseAiShot() {
  const cueBall = getCueBall();
  if (game.breakPending) return chooseAiBreakShot(cueBall);

  const plan = chooseAiPocketPlan(cueBall);
  if (plan) return plan;

  const target = chooseAiTarget();
  if (!target) return null;
  const angle = Math.atan2(
    target.mesh.position.z - cueBall.mesh.position.z,
    target.mesh.position.x - cueBall.mesh.position.x
  );
  const distance = distance2D(cueBall.mesh.position.x, cueBall.mesh.position.z, target.mesh.position.x, target.mesh.position.z);
  const power = THREE.MathUtils.clamp(3.7 + distance * 0.52, 4.2, 6.2);
  return { angle, power, target };
}

function chooseAiBreakShot(cueBall) {
  const headBall = balls
    .filter((ball) => ball.active && ball.group !== "cue")
    .sort((a, b) => a.mesh.position.x - b.mesh.position.x)[0];
  if (!headBall) return null;

  const angle = Math.atan2(
    headBall.mesh.position.z - cueBall.mesh.position.z,
    headBall.mesh.position.x - cueBall.mesh.position.x
  );
  return { angle, power: THREE.MathUtils.randFloat(7.3, 8.2), target: headBall };
}

function chooseAiPocketPlan(cueBall) {
  const candidates = getAiLegalTargets();
  const plans = [];

  candidates.forEach((target) => {
    pockets.forEach((pocket) => {
      const targetPosition = new THREE.Vector2(target.mesh.position.x, target.mesh.position.z);
      const cuePosition = new THREE.Vector2(cueBall.mesh.position.x, cueBall.mesh.position.z);
      const toPocket = pocket.clone().sub(targetPosition);
      const targetToPocketDistance = toPocket.length();
      if (targetToPocketDistance < TABLE.ballRadius * 2.2) return;

      const pocketDirection = toPocket.normalize();
      const ghost = targetPosition.clone().sub(pocketDirection.clone().multiplyScalar(TABLE.ballRadius * 2.05));
      if (!isPointPlayable(ghost)) return;

      const cueToGhost = ghost.clone().sub(cuePosition);
      const cueDistance = cueToGhost.length();
      if (cueDistance < TABLE.ballRadius * 2) return;

      const cutAlignment = cueToGhost.clone().normalize().dot(pocketDirection);
      if (cutAlignment < 0.18) return;

      if (isPathBlocked(cuePosition, ghost, [cueBall, target], TABLE.ballRadius * 1.45)) return;
      if (isPathBlocked(targetPosition, pocket, [target], TABLE.ballRadius * 1.2)) return;

      const angle = Math.atan2(ghost.y - cuePosition.y, ghost.x - cuePosition.x);
      const power = THREE.MathUtils.clamp(3.9 + cueDistance * 0.42 + targetToPocketDistance * 0.28, 4.2, 7.2);
      const score = cueDistance * 0.72 + targetToPocketDistance + (1 - cutAlignment) * 2.8;
      plans.push({ angle, power, target, pocket, score });
    });
  });

  return plans.sort((a, b) => a.score - b.score)[0] || null;
}

function getAiLegalTargets() {
  const group = getPlayerGroup(game.currentPlayer);
  const legalGroup = group && remainingGroupBalls(group) > 0 ? group : null;
  return balls.filter((ball) => {
    if (!ball.active || ball.group === "cue") return false;
    if (legalGroup) return ball.group === legalGroup;
    if (group && remainingGroupBalls(group) === 0) return ball.group === "eight";
    return ball.group !== "eight";
  });
}

function chooseAiTarget() {
  const candidates = getAiLegalTargets();
  const cueBall = getCueBall();
  return candidates.sort((a, b) => {
    const aScore = aiTargetScore(cueBall, a);
    const bScore = aiTargetScore(cueBall, b);
    return aScore - bScore;
  })[0] || null;
}

function aiTargetScore(cueBall, target) {
  const targetPosition = new THREE.Vector2(target.mesh.position.x, target.mesh.position.z);
  const nearestPocket = pockets.reduce((best, pocket) => {
    const distance = pocket.distanceTo(targetPosition);
    return distance < best.distance ? { pocket, distance } : best;
  }, { pocket: pockets[0], distance: Infinity });
  return (
    distance2D(cueBall.mesh.position.x, cueBall.mesh.position.z, target.mesh.position.x, target.mesh.position.z) +
    nearestPocket.distance * 0.55
  );
}

function isPointPlayable(point) {
  return (
    point.x > -playableHalfW + TABLE.ballRadius &&
    point.x < playableHalfW - TABLE.ballRadius &&
    point.y > -playableHalfD + TABLE.ballRadius &&
    point.y < playableHalfD - TABLE.ballRadius
  );
}

function isPathBlocked(from, to, ignoredBalls, clearance) {
  return balls.some((ball) => {
    if (!ball.active || ignoredBalls.includes(ball)) return false;
    const center = new THREE.Vector2(ball.mesh.position.x, ball.mesh.position.z);
    return pointSegmentDistance(center, from, to) < clearance;
  });
}

function pointSegmentDistance(point, start, end) {
  const segment = end.clone().sub(start);
  const lengthSq = segment.lengthSq();
  if (lengthSq === 0) return point.distanceTo(start);
  const t = THREE.MathUtils.clamp(point.clone().sub(start).dot(segment) / lengthSq, 0, 1);
  return point.distanceTo(start.clone().add(segment.multiplyScalar(t)));
}

function placeCueBallForAi() {
  const cueBall = getCueBall();
  const target = chooseAiTarget();
  const desired = target
    ? new THREE.Vector2(target.mesh.position.x - 1.15, target.mesh.position.z)
    : cueStart.clone();

  for (let attempt = 0; attempt < 20; attempt += 1) {
    const x = THREE.MathUtils.clamp(desired.x - attempt * 0.08, -playableHalfW + 0.12, playableHalfW - 0.12);
    const z = THREE.MathUtils.clamp(desired.y + Math.sin(attempt) * 0.35, -playableHalfD + 0.12, playableHalfD - 0.12);
    const blocked = balls.some((ball) => ball !== cueBall && ball.active && distance2D(ball.mesh.position.x, ball.mesh.position.z, x, z) < TABLE.ballRadius * 2.4);
    if (!blocked) {
      cueBall.mesh.position.set(x, TABLE.ballRadius + 0.02, z);
      return;
    }
  }

  cueBall.mesh.position.set(cueStart.x, TABLE.ballRadius + 0.02, cueStart.y);
}

function updateStrike(delta) {
  if (!shot.striking) return;

  shot.strikeTime += delta;
  if (shot.strikeTime >= 0.34 && !shot.released) {
    const cueBall = getCueBall();
    cueBall.velocity.set(Math.cos(aim.angle) * aim.shotPower, Math.sin(aim.angle) * aim.shotPower);
    shot.released = true;
  }

  if (shot.strikeTime > 0.58) {
    shot.striking = false;
  }
}

function updatePredictionLine() {
  const cueBall = getCueBall();
  const visible = game.started && !game.gameOver && !game.ballInHand && !areBallsMoving() && !shot.striking && cueBall.active;
  predictionLine.visible = visible;
  if (!visible) return;

  predictionLine.position.set(cueBall.mesh.position.x, 0, cueBall.mesh.position.z);
  predictionLine.rotation.y = -aim.angle;
}

function updatePlayerRig() {
  const cueBall = getCueBall();
  const direction = new THREE.Vector2(Math.cos(aim.angle), Math.sin(aim.angle));
  const baseDistance = getOutsidePlayerDistance(cueBall, direction);
  const pullBack = shot.striking ? getStrikeOffset() : 0;
  const rigDistance = baseDistance + pullBack;

  playerRig.visible = cueBall.active && !game.gameOver;
  playerRig.position.set(
    cueBall.mesh.position.x - direction.x * rigDistance,
    0.16,
    cueBall.mesh.position.z - direction.y * rigDistance
  );
  playerRig.rotation.y = -aim.angle;

  const stickLength = Math.max(1.8, rigDistance + 0.58);
  cueStickMesh.scale.y = stickLength;
  cueStickMesh.position.x = stickLength / 2 - 0.12;
}

function getOutsidePlayerDistance(cueBall, direction) {
  const outsideHalfW = halfW + TABLE.railThickness + 0.38;
  const outsideHalfD = halfD + TABLE.railThickness + 0.38;
  const x = cueBall.mesh.position.x;
  const z = cueBall.mesh.position.z;
  const behind = new THREE.Vector2(-direction.x, -direction.y);
  const candidates = [];

  if (Math.abs(behind.x) > 0.001) {
    const boundaryX = behind.x > 0 ? outsideHalfW : -outsideHalfW;
    const t = (boundaryX - x) / behind.x;
    if (t > 0) candidates.push(t);
  }

  if (Math.abs(behind.y) > 0.001) {
    const boundaryZ = behind.y > 0 ? outsideHalfD : -outsideHalfD;
    const t = (boundaryZ - z) / behind.y;
    if (t > 0) candidates.push(t);
  }

  return Math.max(1.25, Math.min(...candidates) + 0.08);
}

function getStrikeOffset() {
  const t = shot.strikeTime;
  if (t < 0.22) return t / 0.22 * 0.34;
  if (t < 0.34) return (1 - (t - 0.22) / 0.12) * 0.34 - 0.11;
  return Math.max(0, 0.1 - (t - 0.34) * 0.4);
}

function stepPhysics(delta) {
  const friction = Math.pow(0.6, delta);

  balls.forEach((ball) => {
    if (!ball.active) return;

    ball.mesh.position.x += ball.velocity.x * delta;
    ball.mesh.position.z += ball.velocity.y * delta;
    ball.velocity.multiplyScalar(friction);

    if (ball.velocity.lengthSq() < 0.0009) ball.velocity.set(0, 0);

    bounceOffRails(ball);
    spinBall(ball, delta);
    checkPocket(ball);
  });

  for (let i = 0; i < balls.length; i += 1) {
    for (let j = i + 1; j < balls.length; j += 1) {
      resolveBallCollision(balls[i], balls[j]);
    }
  }

  if (shot.active && !shot.striking && !areBallsMoving()) {
    finishShot();
  }
}

function bounceOffRails(ball) {
  const restitution = 0.92;
  let bounced = false;
  const impactSpeed = ball.velocity.length();

  if (ball.mesh.position.x > playableHalfW) {
    ball.mesh.position.x = playableHalfW;
    ball.velocity.x = -Math.abs(ball.velocity.x) * restitution;
    bounced = true;
  } else if (ball.mesh.position.x < -playableHalfW) {
    ball.mesh.position.x = -playableHalfW;
    ball.velocity.x = Math.abs(ball.velocity.x) * restitution;
    bounced = true;
  }

  if (ball.mesh.position.z > playableHalfD) {
    ball.mesh.position.z = playableHalfD;
    ball.velocity.y = -Math.abs(ball.velocity.y) * restitution;
    bounced = true;
  } else if (ball.mesh.position.z < -playableHalfD) {
    ball.mesh.position.z = -playableHalfD;
    ball.velocity.y = Math.abs(ball.velocity.y) * restitution;
    bounced = true;
  }

  if (shot.active && bounced && shot.firstHit) {
    shot.railAfterContact = true;
  }
  if (bounced && impactSpeed > 0.24) {
    playRailSound(impactSpeed);
  }
}

function resolveBallCollision(a, b) {
  if (!a.active || !b.active) return;

  const dx = b.mesh.position.x - a.mesh.position.x;
  const dz = b.mesh.position.z - a.mesh.position.z;
  const minDistance = a.radius + b.radius;
  const distanceSq = dx * dx + dz * dz;
  if (distanceSq <= 0 || distanceSq >= minDistance * minDistance) return;

  const distance = Math.sqrt(distanceSq);
  const normal = new THREE.Vector2(dx / distance, dz / distance);
  const tangent = new THREE.Vector2(-normal.y, normal.x);
  const overlap = minDistance - distance;

  a.mesh.position.x -= normal.x * overlap * 0.5;
  a.mesh.position.z -= normal.y * overlap * 0.5;
  b.mesh.position.x += normal.x * overlap * 0.5;
  b.mesh.position.z += normal.y * overlap * 0.5;

  if (shot.active && !shot.firstHit) {
    if (a.group === "cue" && b.group !== "cue") shot.firstHit = b;
    if (b.group === "cue" && a.group !== "cue") shot.firstHit = a;
  }

  const aNormal = normal.dot(a.velocity);
  const bNormal = normal.dot(b.velocity);
  const aTangent = tangent.dot(a.velocity);
  const bTangent = tangent.dot(b.velocity);
  const impact = Math.abs(aNormal - bNormal);
  const restitution = 0.96;

  a.velocity.copy(tangent.clone().multiplyScalar(aTangent)).add(normal.clone().multiplyScalar(bNormal * restitution));
  b.velocity.copy(tangent.clone().multiplyScalar(bTangent)).add(normal.clone().multiplyScalar(aNormal * restitution));

  if (impact > 0.18) {
    playBallClick(impact);
  }
}

function checkPocket(ball) {
  if (!ball.active) return;

  const position = new THREE.Vector2(ball.mesh.position.x, ball.mesh.position.z);
  const pocket = pockets.find((item) => item.distanceTo(position) < TABLE.pocketRadius * 0.78);
  if (!pocket) return;

  playPocketSound();
  ball.active = false;
  ball.velocity.set(0, 0);
  ball.mesh.visible = false;
  if (shot.active) shot.pocketed.push(ball);

  if (ball.group === "cue") {
    shot.scratch = true;
    game.scores[game.currentPlayer] -= 50;
  } else if (ball.group === "eight") {
    shot.eightPocketed = true;
  } else {
    game.scores[game.currentPlayer] += ball.group === getPlayerGroup(game.currentPlayer) || game.tableOpen ? 100 : 25;
  }
  updateHud();
}

function finishShot() {
  const messageParts = [];
  if (shot.isBreak) {
    game.breakPending = false;
    aim.shotPower = DEFAULT_SHOT_POWER;
    messageParts.push("מכת הפתיחה הושלמה.");
  }

  const ownGroup = getPlayerGroup(game.currentPlayer);
  const targetGroup = ownGroup || "open";
  const pocketedGroups = shot.pocketed.filter((ball) => ball.group !== "cue" && ball.group !== "eight").map((ball) => ball.group);
  const madeOwnBall = game.tableOpen ? pocketedGroups.length > 0 : pocketedGroups.includes(ownGroup);
  const wrongFirstHit =
    shot.firstHit &&
    ((ownGroup && shot.firstHit.group !== ownGroup && shot.firstHit.group !== "eight") ||
      (shot.firstHit.group === "eight" && (!ownGroup || remainingGroupBalls(ownGroup) > 0)));
  const missedEverything = !shot.firstHit;
  const noRailOrPocket = !shot.railAfterContact && shot.pocketed.length === 0;
  let foul = shot.scratch || wrongFirstHit || missedEverything || noRailOrPocket;

  if (game.tableOpen && pocketedGroups.length > 0) {
    assignGroups(pocketedGroups[0]);
    messageParts.push(`הקבוצות נקבעו: שחקן ${game.currentPlayer} עם ${groupName(pocketedGroups[0])}.`);
  }

  if (shot.eightPocketed) {
    const canWin = ownGroup && remainingGroupBalls(ownGroup) === 0;
    if (canWin && !shot.scratch) {
      endGame(`שחקן ${game.currentPlayer} ניצח עם כדור 8!`);
      return;
    }
    endGame(`שחקן ${game.currentPlayer} הפסיד: כדור 8 נכנס מוקדם מדי.`);
    return;
  }

  if (shot.scratch) messageParts.push("הכדור הלבן נפל: קנס 50 נקודות וכדור ביד.");
  if (wrongFirstHit) messageParts.push(`פסילה: פגיעה ראשונה לא נכונה. המטרה היא ${groupName(targetGroup)}.`);
  if (missedEverything) messageParts.push("פסילה: הכדור הלבן לא פגע בכדור צבעוני.");
  if (noRailOrPocket) messageParts.push("פסילה: אחרי הפגיעה לא היה חור או דופן.");

  if (foul) {
    resetCueBall();
    game.ballInHand = true;
    switchTurn();
    messageParts.push(`שחקן ${game.currentPlayer}: כדור ביד. הזיזו את הלבן עם המקשים או לחצו על השולחן, ואז Enter לנעילה.`);
  } else if (madeOwnBall) {
    messageParts.push(`שחקן ${game.currentPlayer} ממשיך.`);
  } else {
    switchTurn();
    messageParts.push(`התור עובר לשחקן ${game.currentPlayer}.`);
  }

  shot = createShotState();
  updateHud();
  setMessage(messageParts.join(" "));
}

function assignGroups(firstPocketedGroup) {
  game.tableOpen = false;
  game.groups[game.currentPlayer] = firstPocketedGroup;
  game.groups[otherPlayer()] = firstPocketedGroup === "solid" ? "stripe" : "solid";
}

function remainingGroupBalls(group) {
  return balls.filter((ball) => ball.active && ball.group === group).length;
}

function resetCueBall() {
  const cueBall = getCueBall();
  cueBall.active = true;
  cueBall.mesh.visible = true;
  cueBall.mesh.position.set(cueStart.x, TABLE.ballRadius + 0.02, cueStart.y);
  cueBall.velocity.set(0, 0);
}

function placeCueBallFromPointer(event) {
  if (!game.ballInHand || game.gameOver) return;

  const rect = canvas.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);

  const hit = new THREE.Vector3();
  if (!raycaster.ray.intersectPlane(tablePlane, hit)) return;

  const cueBall = getCueBall();
  const x = THREE.MathUtils.clamp(hit.x, -playableHalfW + 0.08, playableHalfW - 0.08);
  const z = THREE.MathUtils.clamp(hit.z, -playableHalfD + 0.08, playableHalfD - 0.08);
  const blocked = balls.some((ball) => ball !== cueBall && ball.active && distance2D(ball.mesh.position.x, ball.mesh.position.z, x, z) < TABLE.ballRadius * 2.3);
  if (blocked) {
    setMessage("אי אפשר למקם את הלבן על כדור אחר.");
    return;
  }

  cueBall.mesh.position.set(x, TABLE.ballRadius + 0.02, z);
  setMessage(`שחקן ${game.currentPlayer}: הזיזו למיקום הרצוי ולחצו Enter כדי לנעול.`);
}

function ensureAudio() {
  if (!audio.ctx) {
    audio.ctx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audio.ctx.state === "suspended") audio.ctx.resume();
  audio.enabled = true;
}

function playEnvelope({ frequency, duration, gain, type = "sine", detune = 0, noise = false }) {
  if (!audio.enabled || !audio.ctx) return;

  const now = audio.ctx.currentTime;
  const output = audio.ctx.createGain();
  output.gain.setValueAtTime(0.0001, now);
  output.gain.exponentialRampToValueAtTime(Math.max(0.0002, gain), now + 0.006);
  output.gain.exponentialRampToValueAtTime(0.0001, now + duration);
  output.connect(audio.ctx.destination);

  if (noise) {
    const bufferSize = Math.max(1, Math.floor(audio.ctx.sampleRate * duration));
    const buffer = audio.ctx.createBuffer(1, bufferSize, audio.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i += 1) data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
    const source = audio.ctx.createBufferSource();
    const filter = audio.ctx.createBiquadFilter();
    filter.type = "bandpass";
    filter.frequency.setValueAtTime(frequency, now);
    filter.Q.setValueAtTime(7, now);
    source.buffer = buffer;
    source.connect(filter);
    filter.connect(output);
    source.start(now);
    source.stop(now + duration);
    return;
  }

  const oscillator = audio.ctx.createOscillator();
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, now);
  oscillator.detune.setValueAtTime(detune, now);
  oscillator.connect(output);
  oscillator.start(now);
  oscillator.stop(now + duration);
}

function playStrikeSound() {
  playEnvelope({ frequency: 155, duration: 0.09, gain: 0.16, type: "triangle" });
  playEnvelope({ frequency: 1800, duration: 0.035, gain: 0.08, noise: true });
}

function playBallClick(intensity) {
  const now = performance.now();
  if (now - audio.lastBallClick < 38) return;
  audio.lastBallClick = now;
  const gain = THREE.MathUtils.clamp(intensity * 0.028, 0.025, 0.18);
  playEnvelope({ frequency: 2400, duration: 0.032, gain, noise: true });
  playEnvelope({ frequency: 740, duration: 0.04, gain: gain * 0.35, type: "triangle" });
}

function playRailSound(intensity) {
  const now = performance.now();
  if (now - audio.lastRailHit < 55) return;
  audio.lastRailHit = now;
  const gain = THREE.MathUtils.clamp(intensity * 0.018, 0.018, 0.12);
  playEnvelope({ frequency: 260, duration: 0.09, gain, type: "sawtooth" });
  playEnvelope({ frequency: 420, duration: 0.055, gain: gain * 0.5, noise: true });
}

function playPocketSound() {
  playEnvelope({ frequency: 120, duration: 0.18, gain: 0.12, type: "sine" });
  playEnvelope({ frequency: 210, duration: 0.12, gain: 0.07, noise: true });
}

function spinBall(ball, delta) {
  const rolling = new THREE.Vector3(ball.velocity.y, 0, -ball.velocity.x);
  ball.mesh.rotation.x += rolling.x * delta / ball.radius;
  ball.mesh.rotation.z += rolling.z * delta / ball.radius;
}

function createShotState() {
  return {
    active: false,
    striking: false,
    released: false,
    strikeTime: 0,
    firstHit: null,
    pocketed: [],
    scratch: false,
    eightPocketed: false,
    railAfterContact: false,
    isBreak: false,
  };
}

function getCueBall() {
  return balls.find((ball) => ball.group === "cue");
}

function areBallsMoving() {
  return balls.some((ball) => ball.active && ball.velocity.lengthSq() > 0.012);
}

function getPlayerGroup(player) {
  return game.groups[player];
}

function otherPlayer() {
  return game.currentPlayer === 1 ? 2 : 1;
}

function isAiTurn() {
  return game.started && game.mode === "ai" && game.currentPlayer === ai.player && !game.gameOver;
}

function getActiveControls() {
  if (game.mode === "local" && game.currentPlayer === 2) {
    return { left: "KeyA", right: "KeyD", strike: "KeyW" };
  }
  return { left: "ArrowLeft", right: "ArrowRight", strike: "Space" };
}

function switchTurn() {
  game.currentPlayer = otherPlayer();
  aim.charging = false;
  aim.chargeValue = 0;
  updatePowerMeter(0);
  ai.thinking = false;
}

function groupName(group) {
  if (group === "solid") return "חלקים";
  if (group === "stripe") return "פסים";
  if (group === "eight") return "כדור 8";
  return "שולחן פתוח";
}

function distance2D(ax, az, bx, bz) {
  return Math.hypot(ax - bx, az - bz);
}

function endGame(message) {
  game.gameOver = true;
  predictionLine.visible = false;
  setMessage(`${message} לחצו רענון כדי להתחיל מחדש.`);
}

function updateHud() {
  const p1 = groupName(game.groups[1] || "open");
  const p2 = groupName(game.groups[2] || "open");
  const playerName = game.mode === "ai" && game.currentPlayer === ai.player ? "מחשב" : `שחקן ${game.currentPlayer}`;
  const modeName = game.mode === "ai" ? "נגד מחשב" : "מקומי";
  turnLabel.textContent = `${playerName} | ${p1} / ${p2}`;
  scoreLabel.textContent = `${game.scores[1]} : ${game.scores[2]}`;
  controlHint.textContent = game.mode === "ai"
    ? "← / → כיוון | החזקת Space עוצמה"
    : "שחקן 1: ←/→ + Space | שחקן 2: A/D + W";
  if (game.started) scoreLabel.title = modeName;
  renderPocketBoard();
}

function renderPocketBoard() {
  renderRemainingBalls("solid", [1, 2, 3, 4, 5, 6, 7]);
  renderRemainingBalls("stripe", [9, 10, 11, 12, 13, 14, 15]);
}

function renderRemainingBalls(group, numbers) {
  const list = ballLists[group];
  if (!list) return;

  list.replaceChildren();
  numbers.forEach((number) => {
    const ball = balls.find((item) => item.number === number);
    const dot = document.createElement("span");
    dot.className = `pocket-dot${group === "stripe" ? " pocket-dot--stripe" : ""}${ball && !ball.active ? " is-pocketed" : ""}`;
    dot.title = ball && ball.active ? `כדור ${number} נשאר` : `כדור ${number} הוטבע`;
    dot.style.background = `#${(ball?.color ?? 0x777777).toString(16).padStart(6, "0")}`;
    const label = document.createElement("span");
    label.textContent = number;
    dot.append(label);
    list.append(dot);
  });
}

function setMessage(message) {
  messageBox.textContent = message;
}

function resize() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const aspect = width / height;

  if (aspect < 0.75) {
    camera.fov = 70;
    camera.position.set(0, 15.2, 0.08);
  } else {
    camera.fov = 42;
    camera.position.set(0, 8.1, 7.2);
  }

  camera.aspect = width / height;
  camera.lookAt(0, 0, 0);
  camera.updateProjectionMatrix();
  renderer.setSize(width, height, false);
}
