import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js";

const canvas = document.querySelector("#game");
const startScreen = document.querySelector("#start-screen");
const gameOverScreen = document.querySelector("#game-over-screen");
const winScreen = document.querySelector("#win-screen");
const startButton = document.querySelector("#start-button");
const retryButton = document.querySelector("#retry-button");
const playAgainButton = document.querySelector("#play-again-button");
const statusText = document.querySelector("#status");

const CELL = 4;
const CEILING_HEIGHT = 4.8;
const PLAYER_HEIGHT = 1.7;
const PLAYER_RADIUS = 0.38;
const PLAYER_SPEED = 7;
const MONSTER_RADIUS = 0.92;
const MONSTER_HEIGHT = 3.2;
const MONSTER_TOUCH_DISTANCE = 1.05;
const EYE_REVEAL_DISTANCE = 6;
const MOUSE_SENSITIVITY = 0.0022;

const STAGES = [
  {
    name: "הבטון האפל",
    kind: "flesh",
    monsterColor: 0x681c26,
    monsterAccent: 0x25351e,
    fog: 0x030303,
    wallBase: [35, 34, 32],
    floorBase: [28, 27, 25],
    lightColor: 0xd8d88d,
    map: [
      "#########################",
      "#S....#.......#.....h...#",
      "#.###.#.#####.#.###.###.#",
      "#...#.#.....#...#.....#.#",
      "###.#.###.#.#####.###.#.#",
      "#...#.....#.....#...#...#",
      "#.###########.#.###.###.#",
      "#.....h.......#.....#...#",
      "#####.#####.#########.###",
      "#.....#...#.....#.......#",
      "#.#####.#.#####.#.#####.#",
      "#...#...#...M...#.....#.#",
      "###.#.###########.###.#.#",
      "#...#.....#.......#...#.#",
      "#.#######.#.#####.#.###.#",
      "#.....#...#...#...#...K.#",
      "#.###.#.#####.#.#####.###",
      "#...#.#.....#.#.....#...#",
      "###.#.#####.#.###.#.###.#",
      "#...#.....#.....#.#...#E#",
      "#.#######.#####.#.###.#.#",
      "#.........h.....#.......#",
      "#########################",
    ],
  },
  {
    name: "האקווריום התת-קרקעי",
    kind: "aquatic",
    monsterColor: 0x0d6f8f,
    monsterAccent: 0x2ce3d0,
    fog: 0x001018,
    wallBase: [12, 39, 55],
    floorBase: [8, 28, 42],
    lightColor: 0x78d5b7,
    map: [
      "#########################",
      "#S..h.....#.......#.....#",
      "#.#####.#.#.#####.#.###.#",
      "#.....#.#.#.....#.#...#.#",
      "#####.#.#.#####.#.###.#.#",
      "#.....#.#.....#.#.....#.#",
      "#.#####.#####.#.#####.#.#",
      "#.#.........#.#...h...#.#",
      "#.#.#######.#.#######.#.#",
      "#.#.#.....#.#.....#...#.#",
      "#...#.###.#.#####.#.###.#",
      "#####.#...#...M...#.....#",
      "#.....#.#####.#########.#",
      "#.#####.....#.......#...#",
      "#.....#####.#######.#.###",
      "#####.....#.....#...#...#",
      "#K..#####.#####.#.#####.#",
      "#.#.....#.....#.#.....#.#",
      "#.#####.#####.#.#####.#.#",
      "#.....h.......#.......#E#",
      "#.###################.#.#",
      "#.....................#.#",
      "#########################",
    ],
  },
];

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);
scene.fog = new THREE.FogExp2(0x020202, 0.035);

const camera = new THREE.PerspectiveCamera(72, window.innerWidth / window.innerHeight, 0.1, 140);
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;

const clock = new THREE.Clock();
const keys = new Set();
const raycaster = new THREE.Raycaster();
const eyeGlowTexture = createEyeGlowTexture();

let levelGroup = new THREE.Group();
let stageIndex = 0;
let currentStage = STAGES[0];
let currentMap = currentStage.map;
let mapWidth = currentMap[0].length;
let mapHeight = currentMap.length;
let playerColliders = [];
let monsterColliders = [];
let wallMeshes = [];
let passableCells = [];
let fluorescents = [];
let monsters = [];
let materials = {};
let key;
let keyGlow;
let door;
let hasKey = false;
let isPlaying = false;
let gameEnded = false;
let yaw = -Math.PI / 2;
let pitch = 0;
let audio = null;
let flashlight;
let lastStepTime = 0;

buildLights();
loadStage(0, false);

startButton.addEventListener("click", startGame);
retryButton.addEventListener("click", startGame);
playAgainButton.addEventListener("click", startGame);
startButton.focus();

document.addEventListener("pointerlockchange", () => {
  if (!isPlaying || gameEnded) return;
  statusText.textContent = document.pointerLockElement === canvas
    ? statusLine()
    : "המשחק רץ. לחץ על המסך כדי לנעול את העכבר.";
});

document.addEventListener("mousemove", (event) => {
  if (document.pointerLockElement !== canvas || !isPlaying || gameEnded) return;
  yaw -= event.movementX * MOUSE_SENSITIVITY;
  pitch -= event.movementY * MOUSE_SENSITIVITY;
  pitch = THREE.MathUtils.clamp(pitch, -Math.PI / 2.6, Math.PI / 2.6);
});

document.addEventListener("keydown", (event) => {
  if (event.code === "Enter" || event.code === "NumpadEnter") {
    if (!startScreen.classList.contains("hidden") || !gameOverScreen.classList.contains("hidden") || !winScreen.classList.contains("hidden")) {
      event.preventDefault();
      startGame();
      return;
    }
  }
  keys.add(event.code);
  if (["KeyW", "KeyA", "KeyS", "KeyD", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.code)) event.preventDefault();
});

document.addEventListener("keyup", (event) => keys.delete(event.code));
canvas.addEventListener("click", () => {
  if (isPlaying && !gameEnded) lockPointer();
});

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function startGame() {
  stageIndex = 0;
  loadStage(stageIndex, true);
  gameEnded = false;
  isPlaying = true;
  startScreen.classList.add("hidden");
  gameOverScreen.classList.add("hidden");
  winScreen.classList.add("hidden");
  initAudio();
  lockPointer();
}

function loadStage(index, movePlayer) {
  scene.remove(levelGroup);
  levelGroup = new THREE.Group();
  scene.add(levelGroup);

  stageIndex = index;
  currentStage = STAGES[stageIndex];
  currentMap = currentStage.map;
  mapWidth = currentMap[0].length;
  mapHeight = currentMap.length;
  playerColliders = [];
  monsterColliders = [];
  wallMeshes = [];
  passableCells = [];
  fluorescents = [];
  monsters = [];
  hasKey = false;

  scene.fog = new THREE.FogExp2(currentStage.fog, stageIndex === 0 ? 0.035 : 0.043);
  materials = makeMaterials(currentStage);
  buildMaze();
  buildArchitecture();
  buildItems();
  buildMonsters();

  if (movePlayer) {
    camera.position.copy(gridToWorld(findTile("S"), PLAYER_HEIGHT));
    yaw = -Math.PI / 2;
    pitch = 0;
    statusText.textContent = statusLine();
  }
}

function makeMaterials(stage) {
  const textures = {
    wall: createConcreteTexture({ base: stage.wallBase, stain: [4, 4, 5], lines: false }),
    floor: createConcreteTexture({ base: stage.floorBase, stain: [4, 4, 5], lines: true }),
    ceiling: createConcreteTexture({ base: stage.wallBase.map((v) => Math.max(0, v - 8)), stain: [4, 4, 5], lines: true }),
    metal: createScratchedMetalTexture(),
    flesh: createMonsterSkinTexture(stage.kind),
  };
  for (const texture of Object.values(textures)) {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
  }
  textures.floor.repeat.set(mapWidth / 2.3, mapHeight / 2.3);
  textures.ceiling.repeat.set(1.2, 1.2);

  return {
    floor: new THREE.MeshStandardMaterial({ map: textures.floor, roughness: 0.97 }),
    ceiling: new THREE.MeshStandardMaterial({ map: textures.ceiling, roughness: 0.98 }),
    wall: new THREE.MeshStandardMaterial({ map: textures.wall, roughness: 0.94 }),
    monsterSkin: new THREE.MeshStandardMaterial({ color: stage.monsterColor, map: textures.flesh, roughness: 0.62, emissive: 0x020506 }),
    monsterAccent: new THREE.MeshStandardMaterial({ color: stage.monsterAccent, map: textures.flesh, roughness: 0.72, emissive: 0x001010 }),
    monsterClaw: new THREE.MeshStandardMaterial({ color: stage.kind === "aquatic" ? 0x061c20 : 0x15100b, roughness: 0.5 }),
    monsterHorn: new THREE.MeshStandardMaterial({ color: stage.kind === "aquatic" ? 0x7be7d6 : 0x3b3025, roughness: 0.58 }),
    door: new THREE.MeshStandardMaterial({ color: stage.monsterColor, roughness: 0.72, metalness: 0.12 }),
    key: new THREE.MeshStandardMaterial({ color: 0xffc23b, map: textures.metal, emissive: 0x2b1800, metalness: 0.94, roughness: 0.16 }),
    redEye: new THREE.MeshBasicMaterial({ color: stage.kind === "aquatic" ? 0x31ffe8 : 0xff1414, transparent: true, opacity: 0 }),
  };
}

function buildMaze() {
  const worldWidth = mapWidth * CELL;
  const worldDepth = mapHeight * CELL;
  const floor = new THREE.Mesh(new THREE.BoxGeometry(worldWidth, 0.24, worldDepth), materials.floor);
  floor.position.set(0, -0.12, 0);
  floor.receiveShadow = true;
  levelGroup.add(floor);

  forEachTile((tile, x, z) => {
    const center = gridToWorld({ x, z }, 0);
    if (tile === "#") {
      addBlock(new THREE.Vector3(center.x, CEILING_HEIGHT / 2, center.z), CELL, CEILING_HEIGHT, CELL, materials.wall, true, true);
    } else {
      passableCells.push({ x, z });
      addCeilingTile(x, z, center);
    }
  });
}

function addCeilingTile(x, z, center) {
  const slab = new THREE.Mesh(new THREE.BoxGeometry(CELL, 0.18, CELL), materials.ceiling);
  slab.position.set(center.x, CEILING_HEIGHT, center.z);
  slab.receiveShadow = true;
  levelGroup.add(slab);
  if ((x + z * 3 + stageIndex * 5) % 19 === 0) addFluorescent(center.x, center.z);
}

function buildArchitecture() {
  addPillar(5, 7, 1.05);
  addPillar(16, 5, 1.15);
  addPillar(13, 16, 0.95);
  addPillar(7, 19, 1.2);
  addCrawlHole(6, 1, "x");
  addCrawlHole(6, 7, "x");
  addCrawlHole(10, 21, "z");
}

function buildItems() {
  key = createKeyModel();
  key.position.copy(gridToWorld(findTile("K"), 0.82));
  levelGroup.add(key);
  keyGlow = new THREE.PointLight(0xffbd35, 1.7, 5);
  keyGlow.position.copy(key.position);
  levelGroup.add(keyGlow);

  door = addBlock(doorPosition(), CELL * 0.95, 4.25, 0.28, materials.door, true, true);
  door.userData.open = false;
}

function buildMonsters() {
  for (let i = 0; i < 3; i += 1) {
    const monster = createMonster(gridToWorld(randomFarCell(), 0), i);
    monsters.push(monster);
  }
}

function createMonster(position, index) {
  const monster = new THREE.Group();
  monster.position.copy(position);
  monster.userData.target = null;
  monster.userData.alert = false;
  monster.userData.eyePower = 0;
  monster.userData.eyes = [];
  monster.userData.eyeLights = [];
  monster.userData.halos = [];
  monster.userData.speed = (currentStage.kind === "aquatic" ? 2.7 : 3.15) + index * 0.18;
  monster.userData.stuckTime = 0;

  if (currentStage.kind === "aquatic") buildAquaticMonster(monster);
  else buildFleshMonster(monster);

  addMonsterEye(monster, -0.32);
  addMonsterEye(monster, 0.32);
  levelGroup.add(monster);
  chooseNewMonsterTarget(monster);
  return monster;
}

function buildFleshMonster(monster) {
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.82, 24, 18), materials.monsterSkin);
  body.position.y = 1.55;
  body.scale.set(0.86, 1.65, 0.58);
  body.castShadow = true;
  monster.add(body);

  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.52, 18, 14), materials.monsterAccent);
  belly.position.set(0, 1.45, -0.22);
  belly.scale.set(0.9, 1.25, 0.32);
  belly.castShadow = true;
  monster.add(belly);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.55, 22, 16), materials.monsterSkin);
  head.position.set(0, 2.95, -0.08);
  head.scale.set(1.08, 0.78, 0.88);
  head.rotation.z = -0.16;
  head.castShadow = true;
  monster.add(head);

  const snout = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.55, 18), materials.monsterAccent);
  snout.position.set(0, 2.9, -0.58);
  snout.rotation.x = Math.PI / 2;
  snout.castShadow = true;
  monster.add(snout);

  addMonsterHorn(monster, -0.34, 3.38, -0.04, -0.28);
  addMonsterHorn(monster, 0.34, 3.38, -0.04, 0.28);
  addBackSpikes(monster);
  addMonsterLimb(monster, -0.9, 1.2, -0.28);
  addMonsterLimb(monster, 0.9, 1.18, 0.24);
  addMonsterLeg(monster, -0.36);
  addMonsterLeg(monster, 0.36);
}

function buildAquaticMonster(monster) {
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.82, 28, 18), materials.monsterSkin);
  body.position.y = 1.85;
  body.scale.set(0.95, 1.1, 0.72);
  body.castShadow = true;
  monster.add(body);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.58, 24, 16), materials.monsterAccent);
  head.position.set(0, 2.7, -0.25);
  head.scale.set(1.12, 0.72, 0.95);
  head.castShadow = true;
  monster.add(head);

  for (let i = 0; i < 6; i += 1) {
    const angle = (i / 6) * Math.PI * 2;
    const tentacle = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.16, 1.8, 12), materials.monsterSkin);
    tentacle.position.set(Math.cos(angle) * 0.42, 0.82, Math.sin(angle) * 0.35);
    tentacle.rotation.z = Math.cos(angle) * 0.35;
    tentacle.rotation.x = Math.sin(angle) * 0.35;
    tentacle.castShadow = true;
    monster.add(tentacle);
  }

  const fin = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.85, 3), materials.monsterHorn);
  fin.position.set(0, 2.15, 0.54);
  fin.rotation.x = -Math.PI / 2;
  fin.castShadow = true;
  monster.add(fin);
}

function buildLights() {
  const flashlightTarget = new THREE.Object3D();
  flashlightTarget.position.set(0, 0, -12);
  camera.add(flashlightTarget);
  flashlight = new THREE.SpotLight(0xffffff, 205, 31, Math.PI / 6.8, 0.82, 1.18);
  flashlight.position.set(0, -0.08, 0.08);
  flashlight.target = flashlightTarget;
  flashlight.castShadow = true;
  flashlight.shadow.mapSize.set(1024, 1024);
  camera.add(flashlight);
  scene.add(camera);
}

function addMonsterLimb(monster, x, y, rotation) {
  const limb = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.2, 2.25, 14), materials.monsterSkin);
  limb.position.set(x, y, 0.03);
  limb.rotation.z = rotation;
  limb.castShadow = true;
  monster.add(limb);
  const claw = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.36, 12), materials.monsterClaw);
  claw.position.set(x + Math.sign(x) * 0.32, 0.08, -0.05);
  claw.rotation.z = -rotation;
  claw.castShadow = true;
  monster.add(claw);
}

function addMonsterLeg(monster, x) {
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.26, 1.25, 14), materials.monsterAccent);
  leg.position.set(x, 0.48, 0.04);
  leg.rotation.z = x > 0 ? -0.12 : 0.12;
  leg.castShadow = true;
  monster.add(leg);
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.16, 0.75), materials.monsterClaw);
  foot.position.set(x, -0.08, -0.18);
  foot.castShadow = true;
  monster.add(foot);
}

function addMonsterHorn(monster, x, y, z, tilt) {
  const horn = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.52, 12), materials.monsterHorn);
  horn.position.set(x, y, z);
  horn.rotation.z = tilt;
  horn.castShadow = true;
  monster.add(horn);
}

function addBackSpikes(monster) {
  for (let i = 0; i < 4; i += 1) {
    const spike = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.48, 10), materials.monsterHorn);
    spike.position.set(0, 1.15 + i * 0.42, 0.48);
    spike.rotation.x = -Math.PI / 2.5;
    spike.castShadow = true;
    monster.add(spike);
  }
}

function addMonsterEye(monster, x) {
  const eye = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.13, 0.05), materials.redEye.clone());
  eye.position.set(x, currentStage.kind === "aquatic" ? 2.72 : 3.05, -0.54);
  monster.add(eye);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({
    map: eyeGlowTexture,
    color: currentStage.kind === "aquatic" ? 0x32fff0 : 0xff1b1b,
    blending: THREE.AdditiveBlending,
    depthTest: false,
    depthWrite: false,
    transparent: true,
    opacity: 0,
  }));
  halo.position.set(x, eye.position.y, -0.62);
  halo.scale.set(0.9, 0.9, 1);
  monster.add(halo);
  const light = new THREE.PointLight(currentStage.kind === "aquatic" ? 0x32fff0 : 0xff1818, 0, 8);
  light.position.copy(eye.position);
  monster.add(light);
  monster.userData.eyes.push(eye);
  monster.userData.halos.push(halo);
  monster.userData.eyeLights.push(light);
}

function addPillar(x, z, radius) {
  const center = gridToWorld({ x, z }, CEILING_HEIGHT / 2);
  const pillar = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius * 1.15, CEILING_HEIGHT, 18), materials.wall);
  pillar.position.copy(center);
  pillar.castShadow = true;
  pillar.receiveShadow = true;
  levelGroup.add(pillar);
  pillar.userData.bounds = new THREE.Box3().setFromObject(pillar);
  playerColliders.push(pillar);
  monsterColliders.push(pillar);
  wallMeshes.push(pillar);
}

function addCrawlHole(x, z, axis) {
  const center = gridToWorld({ x, z }, 0);
  const low = new THREE.Mesh(new THREE.BoxGeometry(CELL * 0.92, 0.16, CELL * 0.92), materials.ceiling);
  low.position.set(center.x, 2.15, center.z);
  low.receiveShadow = true;
  levelGroup.add(low);

  const sideSize = 1.32;
  const blockA = new THREE.Mesh(
    new THREE.BoxGeometry(axis === "x" ? CELL * 0.24 : sideSize, 2, axis === "x" ? sideSize : CELL * 0.24),
    materials.wall,
  );
  const blockB = blockA.clone();
  if (axis === "x") {
    blockA.position.set(center.x, 1, center.z - 1.25);
    blockB.position.set(center.x, 1, center.z + 1.25);
  } else {
    blockA.position.set(center.x - 1.25, 1, center.z);
    blockB.position.set(center.x + 1.25, 1, center.z);
  }
  for (const block of [blockA, blockB]) {
    block.castShadow = true;
    block.receiveShadow = true;
    levelGroup.add(block);
    block.userData.bounds = new THREE.Box3().setFromObject(block);
    playerColliders.push(block);
    monsterColliders.push(block);
    wallMeshes.push(block);
  }
  const monsterBlock = new THREE.Object3D();
  monsterBlock.userData.bounds = new THREE.Box3(
    new THREE.Vector3(center.x - 1.45, 0, center.z - 1.45),
    new THREE.Vector3(center.x + 1.45, MONSTER_HEIGHT, center.z + 1.45),
  );
  monsterColliders.push(monsterBlock);
}

function addBlock(position, width, height, depth, material, playerSolid, monsterSolid) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
  mesh.position.copy(position);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  levelGroup.add(mesh);
  mesh.userData.bounds = new THREE.Box3().setFromObject(mesh);
  if (playerSolid) playerColliders.push(mesh);
  if (monsterSolid) monsterColliders.push(mesh);
  wallMeshes.push(mesh);
  return mesh;
}

function updatePlayer(delta) {
  camera.rotation.order = "YXZ";
  camera.rotation.y = yaw;
  camera.rotation.x = pitch;
  const input = new THREE.Vector3();
  if (keys.has("KeyW") || keys.has("ArrowUp")) input.z -= 1;
  if (keys.has("KeyS") || keys.has("ArrowDown")) input.z += 1;
  if (keys.has("KeyA") || keys.has("ArrowLeft")) input.x -= 1;
  if (keys.has("KeyD") || keys.has("ArrowRight")) input.x += 1;
  if (input.lengthSq() === 0) return;
  input.normalize().applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw).multiplyScalar(PLAYER_SPEED * delta);
  moveWithCollision(camera.position, input, PLAYER_RADIUS, PLAYER_HEIGHT, playerColliders);
  updateFootsteps();
}

function updateMonsters(delta) {
  for (const monster of monsters) updateMonster(monster, delta);
}

function updateMonster(monster, delta) {
  const playerFlat = new THREE.Vector3(camera.position.x, 0, camera.position.z);
  const monsterFlat = new THREE.Vector3(monster.position.x, 0, monster.position.z);
  const distance = monsterFlat.distanceTo(playerFlat);
  const seesPlayer = lineOfSight(monster.position, camera.position);
  if (distance < 10 && seesPlayer) monster.userData.alert = true;
  if (distance > 34) monster.userData.alert = false;

  let target = monster.userData.alert ? playerFlat : monster.userData.target;
  if (!target || (!monster.userData.alert && monsterFlat.distanceTo(target) < 1.2)) {
    chooseNewMonsterTarget(monster);
    target = monster.userData.target;
  }

  const direction = target.clone().sub(monsterFlat);
  if (direction.lengthSq() > 0.01) {
    direction.normalize();
    const speed = monster.userData.speed * (monster.userData.alert ? 1.16 : 0.55);
    const moved = moveWithCollision(monster.position, direction.clone().multiplyScalar(speed * delta), MONSTER_RADIUS, MONSTER_HEIGHT, monsterColliders);
    if (!moved) chooseOpenMonsterDirection(monster, direction);
  }

  monster.lookAt(camera.position.x, monster.position.y, camera.position.z);
  monster.rotation.z = Math.sin(clock.elapsedTime * 5.2 + monster.position.x) * 0.035;
  const wantedEyePower = distance < EYE_REVEAL_DISTANCE ? THREE.MathUtils.clamp((EYE_REVEAL_DISTANCE - distance) / EYE_REVEAL_DISTANCE, 0.18, 1) : 0;
  monster.userData.eyePower = THREE.MathUtils.lerp(monster.userData.eyePower, wantedEyePower, 0.1);
  setMonsterEyes(monster, monster.userData.eyePower);
  if (distance < MONSTER_TOUCH_DISTANCE) endGame(gameOverScreen);
}

function chooseOpenMonsterDirection(monster, blockedDirection) {
  const candidates = [
    new THREE.Vector3(-blockedDirection.z, 0, blockedDirection.x),
    new THREE.Vector3(blockedDirection.z, 0, -blockedDirection.x),
    blockedDirection.clone().multiplyScalar(-1),
  ].sort(() => Math.random() - 0.5);
  for (const direction of candidates) {
    const test = monster.position.clone().add(direction.normalize().multiplyScalar(CELL * 1.5));
    if (!collides(test, MONSTER_RADIUS, MONSTER_HEIGHT, monsterColliders)) {
      monster.userData.target = test;
      return;
    }
  }
  chooseNewMonsterTarget(monster);
}

function chooseNewMonsterTarget(monster) {
  const cell = passableCells[Math.floor(Math.random() * passableCells.length)];
  monster.userData.target = gridToWorld(cell, 0);
}

function moveWithCollision(position, movement, radius, height, colliders) {
  const next = position.clone().add(new THREE.Vector3(movement.x, 0, movement.z));
  if (!collides(next, radius, height, colliders)) {
    position.copy(next);
    return true;
  }
  const slideX = position.clone().add(new THREE.Vector3(movement.x, 0, 0));
  const slideZ = position.clone().add(new THREE.Vector3(0, 0, movement.z));
  let moved = false;
  if (!collides(slideX, radius, height, colliders)) {
    position.x = slideX.x;
    moved = true;
  }
  if (!collides(slideZ, radius, height, colliders)) {
    position.z = slideZ.z;
    moved = true;
  }
  return moved;
}

function collides(position, radius, height, colliders) {
  const box = new THREE.Box3(
    new THREE.Vector3(position.x - radius, 0, position.z - radius),
    new THREE.Vector3(position.x + radius, height, position.z + radius),
  );
  return colliders.some((collider) => collider.visible !== false && box.intersectsBox(collider.userData.bounds));
}

function updateObjectives() {
  key.rotation.y += 0.035;
  key.rotation.z = Math.sin(clock.elapsedTime * 2.4) * 0.12;
  key.position.y = 0.82 + Math.sin(clock.elapsedTime * 3) * 0.1;
  keyGlow.position.copy(key.position);
  if (!hasKey && key.visible && camera.position.distanceTo(key.position) < 1.5) {
    hasKey = true;
    key.visible = false;
    keyGlow.visible = false;
    statusText.textContent = statusLine();
  }
  if (hasKey && !door.userData.open && camera.position.distanceTo(door.position) < 2.15) {
    door.userData.open = true;
    door.visible = false;
    if (stageIndex < STAGES.length - 1) {
      statusText.textContent = "הדלת נפתחה. אתה נבלע לשלב הבא...";
      setTimeout(() => {
        if (!gameEnded) loadStage(stageIndex + 1, true);
      }, 550);
    } else {
      endGame(winScreen);
    }
  }
}

function lineOfSight(from, to) {
  const origin = new THREE.Vector3(from.x, PLAYER_HEIGHT, from.z);
  const target = new THREE.Vector3(to.x, PLAYER_HEIGHT, to.z);
  const direction = target.clone().sub(origin);
  const distance = direction.length();
  raycaster.set(origin, direction.normalize());
  raycaster.far = distance;
  return raycaster.intersectObjects(wallMeshes.filter((mesh) => mesh.visible !== false), false).length === 0;
}

function setMonsterEyes(monster, power) {
  const pulse = 1 + Math.sin(clock.elapsedTime * 9) * 0.18;
  for (const eye of monster.userData.eyes) eye.material.opacity = power;
  for (const halo of monster.userData.halos) halo.material.opacity = power * 0.85;
  for (const light of monster.userData.eyeLights) light.intensity = power * 5.2 * pulse;
}

function statusLine() {
  return hasKey
    ? `שלב ${stageIndex + 1}: מפתח אצלך. מצא את הדלת.`
    : `שלב ${stageIndex + 1}: מצא מפתח. עיניים יופיעו רק כשהסכנה קרובה.`;
}

function randomFarCell() {
  const start = findTile("S");
  const candidates = passableCells.filter((cell) => {
    if (["S", "K", "E"].includes(currentMap[cell.z][cell.x])) return false;
    const dx = cell.x - start.x;
    const dz = cell.z - start.z;
    return Math.sqrt(dx * dx + dz * dz) * CELL > 24;
  });
  return candidates[Math.floor(Math.random() * candidates.length)] || findTile("M");
}

function initAudio() {
  if (!audio) {
    const context = new AudioContext();
    const master = context.createGain();
    master.gain.value = 0.13;
    master.connect(context.destination);
    const drone = context.createOscillator();
    const sub = context.createOscillator();
    const droneGain = context.createGain();
    const filter = context.createBiquadFilter();
    drone.type = "triangle";
    drone.frequency.value = 41;
    sub.type = "sine";
    sub.frequency.value = 27.5;
    droneGain.gain.value = 0.16;
    filter.type = "lowpass";
    filter.frequency.value = 160;
    filter.Q.value = 1.2;
    drone.connect(droneGain);
    sub.connect(droneGain);
    droneGain.connect(filter).connect(master);
    drone.start();
    sub.start();
    const wobble = context.createOscillator();
    const wobbleGain = context.createGain();
    wobble.frequency.value = 0.18;
    wobbleGain.gain.value = 3;
    wobble.connect(wobbleGain).connect(drone.frequency);
    wobble.start();

    const musicGain = context.createGain();
    musicGain.gain.value = 0.11;
    musicGain.connect(master);
    audio = { context, master, musicGain };
    audio.motifTimer = setInterval(() => playScaryMotif(audio), 2600);
    playScaryMotif(audio);
  }
  audio.context.resume();
}

function playScaryMotif(targetAudio) {
  if (!targetAudio) return;
  const { context, musicGain } = targetAudio;
  const now = context.currentTime;
  const notes = [55, 58.27, 41.2, 73.42, 61.74];
  notes.forEach((frequency, index) => {
    const osc = context.createOscillator();
    const gain = context.createGain();
    const filter = context.createBiquadFilter();
    osc.type = index % 2 === 0 ? "sine" : "triangle";
    osc.frequency.value = frequency;
    filter.type = "lowpass";
    filter.frequency.value = 420;
    gain.gain.setValueAtTime(0.0001, now + index * 0.22);
    gain.gain.linearRampToValueAtTime(0.13, now + index * 0.22 + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.001, now + index * 0.22 + 1.15);
    osc.connect(filter).connect(gain).connect(musicGain);
    osc.start(now + index * 0.22);
    osc.stop(now + index * 0.22 + 1.2);
  });
}

function updateFootsteps() {
  if (!audio || audio.context.currentTime - lastStepTime < 0.34) return;
  lastStepTime = audio.context.currentTime;
  const context = audio.context;
  const step = context.createOscillator();
  const click = context.createOscillator();
  const gain = context.createGain();
  const filter = context.createBiquadFilter();
  step.type = "triangle";
  click.type = "sine";
  step.frequency.setValueAtTime(82, context.currentTime);
  step.frequency.exponentialRampToValueAtTime(45, context.currentTime + 0.09);
  click.frequency.value = 150;
  filter.type = "lowpass";
  filter.frequency.value = 260;
  gain.gain.setValueAtTime(0.18, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.12);
  step.connect(filter);
  click.connect(filter);
  filter.connect(gain).connect(audio.master);
  step.start();
  click.start();
  step.stop(context.currentTime + 0.13);
  click.stop(context.currentTime + 0.06);
}

function createKeyModel() {
  const group = new THREE.Group();
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 1.8, 24), materials.key);
  shaft.rotation.z = Math.PI / 2;
  group.add(shaft);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.09, 18, 36), materials.key);
  ring.position.x = -1.05;
  ring.rotation.y = Math.PI / 2;
  group.add(ring);
  const toothA = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.45, 0.16), materials.key);
  toothA.position.set(0.78, -0.22, 0);
  group.add(toothA);
  const toothB = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.28, 0.16), materials.key);
  toothB.position.set(1.05, 0.2, 0);
  group.add(toothB);
  group.traverse((child) => {
    if (child.isMesh) child.castShadow = true;
  });
  return group;
}

function doorPosition() {
  const cell = findTile("E");
  const pos = gridToWorld(cell, 2.12);
  if (currentMap[cell.z]?.[cell.x - 1] === "#") pos.x -= CELL * 0.42;
  else if (currentMap[cell.z]?.[cell.x + 1] === "#") pos.x += CELL * 0.42;
  else if (currentMap[cell.z - 1]?.[cell.x] === "#") pos.z -= CELL * 0.42;
  else pos.z += CELL * 0.42;
  return pos;
}

function addFluorescent(x, z) {
  const fixture = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.08, 0.18), materials.ceiling);
  fixture.position.set(x, CEILING_HEIGHT - 0.12, z);
  levelGroup.add(fixture);
  const light = new THREE.PointLight(currentStage.lightColor, 0.38, 8);
  light.position.set(x, CEILING_HEIGHT - 0.35, z);
  light.userData.phase = Math.random() * Math.PI * 2;
  light.userData.base = 0.25 + Math.random() * 0.28;
  levelGroup.add(light);
  fluorescents.push(light);
}

function gridToWorld(cell, y = 0) {
  return new THREE.Vector3(
    (cell.x - mapWidth / 2 + 0.5) * CELL,
    y,
    (cell.z - mapHeight / 2 + 0.5) * CELL,
  );
}

function findTile(target) {
  for (let z = 0; z < mapHeight; z += 1) {
    const x = currentMap[z].indexOf(target);
    if (x !== -1) return { x, z };
  }
  return { x: 1, z: 1 };
}

function forEachTile(callback) {
  for (let z = 0; z < mapHeight; z += 1) {
    for (let x = 0; x < mapWidth; x += 1) callback(currentMap[z][x], x, z);
  }
}

function lockPointer() {
  const request = canvas.requestPointerLock?.();
  if (request?.catch) request.catch(() => {
    statusText.textContent = "המשחק רץ. לחץ שוב על המסך כדי לנעול את העכבר.";
  });
}

function endGame(screen) {
  gameEnded = true;
  isPlaying = false;
  document.exitPointerLock?.();
  screen.classList.remove("hidden");
  if (screen === gameOverScreen) retryButton.focus();
  if (screen === winScreen) playAgainButton.focus();
}

function createConcreteTexture({ base, stain, lines }) {
  const size = 256;
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = size;
  textureCanvas.height = size;
  const context = textureCanvas.getContext("2d");
  const image = context.createImageData(size, size);
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const i = (y * size + x) * 4;
      const noise = Math.random() * 38 - 18;
      const stainMix = Math.max(0, Math.sin(x * 0.045) + Math.cos(y * 0.032) - 1.18) * 38;
      image.data[i] = clamp(base[0] + noise - stainMix + Math.random() * stain[0] * 0.15);
      image.data[i + 1] = clamp(base[1] + noise - stainMix + Math.random() * stain[1] * 0.15);
      image.data[i + 2] = clamp(base[2] + noise - stainMix + Math.random() * stain[2] * 0.15);
      image.data[i + 3] = 255;
    }
  }
  context.putImageData(image, 0, 0);
  context.globalAlpha = 0.26;
  context.strokeStyle = "rgba(0,0,0,0.48)";
  for (let i = 0; i < 38; i += 1) {
    context.beginPath();
    context.moveTo(Math.random() * size, Math.random() * size);
    context.lineTo(Math.random() * size, Math.random() * size);
    context.stroke();
  }
  if (lines) {
    context.globalAlpha = 0.32;
    for (let i = 0; i <= size; i += 64) {
      context.beginPath();
      context.moveTo(i, 0);
      context.lineTo(i, size);
      context.moveTo(0, i);
      context.lineTo(size, i);
      context.stroke();
    }
  }
  return new THREE.CanvasTexture(textureCanvas);
}

function createScratchedMetalTexture() {
  const size = 128;
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = size;
  textureCanvas.height = size;
  const context = textureCanvas.getContext("2d");
  context.fillStyle = "#d09a2f";
  context.fillRect(0, 0, size, size);
  context.globalAlpha = 0.25;
  for (let i = 0; i < 80; i += 1) {
    context.strokeStyle = Math.random() > 0.5 ? "#ffe08a" : "#5c3308";
    context.beginPath();
    const y = Math.random() * size;
    context.moveTo(Math.random() * 20, y);
    context.lineTo(size - Math.random() * 20, y + Math.random() * 4 - 2);
    context.stroke();
  }
  return new THREE.CanvasTexture(textureCanvas);
}

function createMonsterSkinTexture(kind) {
  const size = 256;
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = size;
  textureCanvas.height = size;
  const context = textureCanvas.getContext("2d");
  const image = context.createImageData(size, size);
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const i = (y * size + x) * 4;
      const veins = Math.sin(x * 0.12 + Math.cos(y * 0.04) * 2) > 0.84 ? 38 : 0;
      const bruise = Math.max(0, Math.sin(x * 0.035) + Math.cos(y * 0.052) - 1.05) * 46;
      const noise = Math.random() * 38 - 16;
      image.data[i] = clamp((kind === "aquatic" ? 18 : 88) + noise + veins - bruise * 0.3);
      image.data[i + 1] = clamp((kind === "aquatic" ? 102 : 24) + noise * 0.35 + bruise * 0.55);
      image.data[i + 2] = clamp((kind === "aquatic" ? 120 : 32) + noise * 0.45 + bruise);
      image.data[i + 3] = 255;
    }
  }
  context.putImageData(image, 0, 0);
  context.globalAlpha = 0.28;
  context.strokeStyle = kind === "aquatic" ? "rgba(10, 240, 230, 0.55)" : "rgba(20, 4, 7, 0.8)";
  for (let i = 0; i < 28; i += 1) {
    context.beginPath();
    const startY = Math.random() * size;
    context.moveTo(Math.random() * size, startY);
    context.bezierCurveTo(Math.random() * size, startY + Math.random() * 40 - 20, Math.random() * size, startY + Math.random() * 70 - 35, Math.random() * size, startY + Math.random() * 80 - 40);
    context.stroke();
  }
  return new THREE.CanvasTexture(textureCanvas);
}

function createEyeGlowTexture() {
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = 96;
  textureCanvas.height = 96;
  const context = textureCanvas.getContext("2d");
  const gradient = context.createRadialGradient(48, 48, 4, 48, 48, 48);
  gradient.addColorStop(0, "rgba(255, 255, 255, 1)");
  gradient.addColorStop(0.2, "rgba(255, 32, 32, 0.95)");
  gradient.addColorStop(0.58, "rgba(255, 0, 0, 0.32)");
  gradient.addColorStop(1, "rgba(255, 0, 0, 0)");
  context.fillStyle = gradient;
  context.fillRect(0, 0, 96, 96);
  const texture = new THREE.CanvasTexture(textureCanvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function clamp(value) {
  return Math.max(0, Math.min(255, value));
}

function updateFluorescents() {
  for (const light of fluorescents) {
    const pulse = Math.sin(clock.elapsedTime * 2.1 + light.userData.phase);
    const twitch = Math.sin(clock.elapsedTime * 17 + light.userData.phase * 3) > 0.92 ? 0.05 : 1;
    light.intensity = light.userData.base * (0.72 + Math.max(0, pulse) * 0.28) * twitch;
  }
}

function animate() {
  const delta = Math.min(clock.getDelta(), 0.05);
  if (isPlaying && !gameEnded) {
    updatePlayer(delta);
    updateMonsters(delta);
    updateObjectives();
    updateFluorescents();
  }
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

animate();

if (new URLSearchParams(window.location.search).has("autostart")) {
  gameEnded = false;
  isPlaying = true;
  loadStage(0, true);
  startScreen.classList.add("hidden");
}
