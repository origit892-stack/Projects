import * as THREE from "three";
import "./styles.css";

const FLOOR_Y = -1.72;
const PLAYER_SIZE = 0.62;
const OBSTACLE_SIZE = 0.72;
const TRACK_WIDTH = 4.4;
const TRACK_LENGTH = 42;
const SEGMENT_COUNT = 7;
const LANE_X = 1.18;
const BASE_SPEED = 11.4;
const LANE_SWITCH_SPEED = 13.5;
const OBSTACLE_POOL_SIZE = 52;
const OBSTACLE_GAP_MIN = 6.4;
const OBSTACLE_GAP_RANDOM = 7.2;
const STAR_COUNT = 3600;
const TRAIL_POOL_SIZE = 24;
const TRAIL_INTERVAL = 0.035;
const BOOST_POOL_SIZE = 5;
const COIN_POOL_SIZE = 34;
const BOOST_DURATION = 3;
const BOOST_COOLDOWN = 8.5;
const SHIELD_COST = 6;

const scoreEl = document.querySelector("#score");
const coinsEl = document.querySelector("#coins");
const turboEl = document.querySelector("#turbo");
const startScreenEl = document.querySelector("#start-screen");
const startButton = document.querySelector("#start-button");
const damageFlashEl = document.querySelector("#damage-flash");
const gameOverEl = document.querySelector("#game-over");
const finalScoreEl = document.querySelector("#final-score");
const retryButton = document.querySelector("#retry-button");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x03060d);
scene.fog = new THREE.FogExp2(0x03060d, 0.027);

const camera = new THREE.PerspectiveCamera(
  58,
  window.innerWidth / window.innerHeight,
  0.1,
  260,
);
const renderer = new THREE.WebGLRenderer({
  antialias: true,
  preserveDrawingBuffer: true,
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.82;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
document.body.appendChild(renderer.domElement);

let lastFrameTime = performance.now();
const playerBox = new THREE.Box3();
const obstacleBox = new THREE.Box3();
const boostBox = new THREE.Box3();
const coinBox = new THREE.Box3();
const trackSegments = [];
const obstacles = [];
const boostPads = [];
const coins = [];
const trailPieces = [];
const starField = createStarField();
const audioEngine = createAudioEngine();
const surfaceTexture = createSurfaceTexture();

const state = {
  running: true,
  started: false,
  distance: 0,
  score: 0,
  coins: 0,
  currentLane: 1,
  targetX: LANE_X,
  nextObstacleZ: 16,
  nextBoostZ: 72,
  nextCoinZ: 22,
  turboTime: 0,
  boostCooldown: 0,
  trailTimer: 0,
  shakeTime: 0,
  shakePower: 0,
  switchingLane: false,
  ending: false,
};

const floorMaterial = new THREE.MeshStandardMaterial({
  color: 0x171b20,
  roughness: 0.82,
  metalness: 0.2,
  emissive: 0x06222a,
  emissiveIntensity: 0.12,
  roughnessMap: surfaceTexture,
  bumpMap: surfaceTexture,
  bumpScale: 0.035,
});
const wallMaterial = new THREE.MeshStandardMaterial({
  color: 0x10151c,
  roughness: 0.76,
  metalness: 0.28,
  emissive: 0x11172c,
  emissiveIntensity: 0.14,
  roughnessMap: surfaceTexture,
  bumpMap: surfaceTexture,
  bumpScale: 0.025,
});
const panelMaterial = new THREE.MeshStandardMaterial({
  color: 0x0d1117,
  roughness: 0.88,
  metalness: 0.16,
  roughnessMap: surfaceTexture,
});
const ribMaterial = new THREE.MeshStandardMaterial({
  color: 0x070a0f,
  roughness: 0.92,
  metalness: 0.22,
});
const railMaterial = new THREE.MeshStandardMaterial({
  color: 0x102027,
  emissive: 0x0f8090,
  emissiveIntensity: 0.34,
  roughness: 0.58,
  metalness: 0.36,
});
const laneMaterial = new THREE.MeshStandardMaterial({
  color: 0x101e23,
  emissive: 0x18d3e5,
  emissiveIntensity: 0.18,
  roughness: 0.66,
  metalness: 0.24,
});
const speedLineMaterial = new THREE.MeshBasicMaterial({
  color: 0x25e8ff,
  transparent: true,
  opacity: 0.42,
});
const playerMaterial = new THREE.MeshStandardMaterial({
  color: 0x8eefff,
  emissive: 0x10b9d2,
  emissiveIntensity: 1.9,
  roughness: 0.38,
  metalness: 0.34,
});
const obstacleMaterial = new THREE.MeshStandardMaterial({
  color: 0xd8394a,
  emissive: 0xff1634,
  emissiveIntensity: 1.15,
  roughness: 0.46,
  metalness: 0.24,
});
const boostMaterial = new THREE.MeshStandardMaterial({
  color: 0x67e68a,
  emissive: 0x24d35c,
  emissiveIntensity: 1.3,
  roughness: 0.5,
  metalness: 0.18,
});
const coinMaterial = new THREE.MeshStandardMaterial({
  color: 0xffd34d,
  emissive: 0xffb000,
  emissiveIntensity: 1.05,
  roughness: 0.34,
  metalness: 0.62,
});

setupLights();
createTrack();

const player = new THREE.Mesh(
  new THREE.BoxGeometry(PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE),
  playerMaterial,
);
player.position.set(state.targetX, FLOOR_Y + PLAYER_SIZE / 2, 0);
player.castShadow = true;
scene.add(player);

for (let i = 0; i < TRAIL_POOL_SIZE; i += 1) {
  const material = new THREE.MeshBasicMaterial({
    color: 0x55f6ff,
    transparent: true,
    opacity: 0,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const trail = new THREE.Mesh(
    new THREE.BoxGeometry(PLAYER_SIZE * 0.9, PLAYER_SIZE * 0.9, 0.18),
    material,
  );
  trail.visible = false;
  trail.userData.life = 0;
  trail.userData.maxLife = 0.34;
  scene.add(trail);
  trailPieces.push(trail);
}

for (let i = 0; i < OBSTACLE_POOL_SIZE; i += 1) {
  const obstacle = new THREE.Mesh(
    new THREE.BoxGeometry(OBSTACLE_SIZE, OBSTACLE_SIZE, OBSTACLE_SIZE),
    obstacleMaterial,
  );
  obstacle.castShadow = true;
  obstacle.visible = false;
  obstacle.userData.active = false;
  scene.add(obstacle);
  obstacles.push(obstacle);
}

for (let i = 0; i < BOOST_POOL_SIZE; i += 1) {
  const boost = new THREE.Mesh(
    new THREE.BoxGeometry(0.72, 0.055, 0.92),
    boostMaterial,
  );
  boost.visible = false;
  boost.userData.active = false;
  boost.receiveShadow = true;
  scene.add(boost);
  boostPads.push(boost);
}

for (let i = 0; i < COIN_POOL_SIZE; i += 1) {
  const coin = new THREE.Mesh(
    new THREE.BoxGeometry(0.26, 0.26, 0.09),
    coinMaterial,
  );
  coin.castShadow = true;
  coin.visible = false;
  coin.userData.active = false;
  scene.add(coin);
  coins.push(coin);
}

resetGame();
window.addEventListener("resize", onResize);
window.addEventListener("keydown", onKeyDown);
window.addEventListener("pointerdown", () => audioEngine.start(), { once: true });
startButton.addEventListener("click", startGame);
retryButton.addEventListener("click", resetGame);
renderer.setAnimationLoop(animate);

function setupLights() {
  scene.add(new THREE.AmbientLight(0x8aa3b4, 0.26));

  const cyanLight = new THREE.PointLight(0x25e8ff, 48, 28);
  cyanLight.position.set(-3.8, 2.1, -4.2);
  scene.add(cyanLight);

  const redLight = new THREE.PointLight(0xff3157, 18, 21);
  redLight.position.set(3.4, 0.2, 9);
  scene.add(redLight);

  const keyLight = new THREE.DirectionalLight(0xd8f0ff, 2.05);
  keyLight.position.set(4.2, 7.4, -6.8);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(1024, 1024);
  keyLight.shadow.camera.near = 1;
  keyLight.shadow.camera.far = 38;
  keyLight.shadow.camera.left = -8;
  keyLight.shadow.camera.right = 8;
  keyLight.shadow.camera.top = 8;
  keyLight.shadow.camera.bottom = -8;
  scene.add(keyLight);
}

function createTrack() {
  for (let i = 0; i < SEGMENT_COUNT; i += 1) {
    const segment = new THREE.Group();
    segment.position.z = i * TRACK_LENGTH - TRACK_LENGTH;

    segment.add(makeBox(TRACK_WIDTH, 0.18, TRACK_LENGTH, 0, FLOOR_Y, 0, floorMaterial));
    segment.add(makeBox(0.14, 0.72, TRACK_LENGTH, -TRACK_WIDTH / 2, FLOOR_Y + 0.36, 0, wallMaterial));
    segment.add(makeBox(0.14, 0.72, TRACK_LENGTH, TRACK_WIDTH / 2, FLOOR_Y + 0.36, 0, wallMaterial));
    segment.add(makeBox(0.06, 0.06, TRACK_LENGTH, -0.18, FLOOR_Y + 0.11, 0, laneMaterial));
    segment.add(makeBox(0.06, 0.06, TRACK_LENGTH, 0.18, FLOOR_Y + 0.11, 0, laneMaterial));
    segment.add(makeBox(0.09, 0.09, TRACK_LENGTH, -TRACK_WIDTH / 2 + 0.09, FLOOR_Y + 0.78, 0, railMaterial));
    segment.add(makeBox(0.09, 0.09, TRACK_LENGTH, TRACK_WIDTH / 2 - 0.09, FLOOR_Y + 0.78, 0, railMaterial));

    for (let j = 0; j < 7; j += 1) {
      const localZ = -TRACK_LENGTH / 2 + j * (TRACK_LENGTH / 7);
      segment.add(makeBox(TRACK_WIDTH * 0.88, 0.024, 0.08, 0, FLOOR_Y + 0.104, localZ, panelMaterial));
    }

    for (let j = 0; j < 5; j += 1) {
      const localZ = -TRACK_LENGTH / 2 + j * (TRACK_LENGTH / 5) + 2.4;
      segment.add(makeBox(TRACK_WIDTH + 0.16, 0.055, 0.16, 0, FLOOR_Y + 0.13, localZ, ribMaterial));
      segment.add(makeBox(0.12, 0.46, 0.18, -TRACK_WIDTH / 2 + 0.24, FLOOR_Y + 0.46, localZ + 0.05, ribMaterial));
      segment.add(makeBox(0.12, 0.46, 0.18, TRACK_WIDTH / 2 - 0.24, FLOOR_Y + 0.46, localZ + 0.05, ribMaterial));
    }

    for (let j = 0; j < 10; j += 1) {
      const localZ = -TRACK_LENGTH / 2 + j * (TRACK_LENGTH / 10) + 1.2;
      const leftLine = makeBox(0.045, 0.045, 1.65, -TRACK_WIDTH / 2 + 0.08, FLOOR_Y + 0.83, localZ, speedLineMaterial);
      const rightLine = makeBox(0.045, 0.045, 1.65, TRACK_WIDTH / 2 - 0.08, FLOOR_Y + 0.83, localZ, speedLineMaterial);
      leftLine.userData.speedLine = true;
      rightLine.userData.speedLine = true;
      segment.add(leftLine, rightLine);
    }

    trackSegments.push(segment);
    scene.add(segment);
  }
}

function makeBox(width, height, depth, x, y, z, material) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
  mesh.position.set(x, y, z);
  mesh.castShadow = height > 0.05 && depth < TRACK_LENGTH * 0.8;
  mesh.receiveShadow = true;
  return mesh;
}

function createSurfaceTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const context = canvas.getContext("2d");
  const imageData = context.createImageData(canvas.width, canvas.height);

  for (let i = 0; i < imageData.data.length; i += 4) {
    const value = 88 + Math.random() * 72;
    imageData.data[i] = value;
    imageData.data[i + 1] = value;
    imageData.data[i + 2] = value;
    imageData.data[i + 3] = 255;
  }

  context.putImageData(imageData, 0, 0);
  context.globalAlpha = 0.18;
  context.strokeStyle = "#ffffff";
  for (let y = 0; y < canvas.height; y += 16) {
    context.beginPath();
    context.moveTo(0, y + 0.5);
    context.lineTo(canvas.width, y + 0.5);
    context.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(10, 18);
  return texture;
}

function createStarField() {
  const positions = [];
  const speeds = [];
  for (let i = 0; i < STAR_COUNT; i += 1) {
    positions.push(
      THREE.MathUtils.randFloatSpread(96),
      THREE.MathUtils.randFloatSpread(56),
      THREE.MathUtils.randFloat(-18, 180),
    );
    speeds.push(THREE.MathUtils.randFloat(0.55, 1.9));
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("speed", new THREE.Float32BufferAttribute(speeds, 1));
  const material = new THREE.PointsMaterial({
    color: 0x9cecff,
    size: 0.082,
    transparent: true,
    opacity: 0.82,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });
  const points = new THREE.Points(geometry, material);
  scene.add(points);
  return points;
}

function animate() {
  const now = performance.now();
  const dt = Math.min((now - lastFrameTime) / 1000, 0.033);
  lastFrameTime = now;
  if (state.running) {
    updateGame(dt);
  }
  renderer.render(scene, camera);
}

function updateGame(dt) {
  if (state.turboTime > 0) {
    state.turboTime = Math.max(state.turboTime - dt, 0);
    if (state.turboTime === 0) {
      audioEngine.setTurbo(false);
      turboEl.classList.add("hidden");
    }
  }
  if (state.boostCooldown > 0) {
    state.boostCooldown = Math.max(state.boostCooldown - dt, 0);
  }

  const speedMultiplier = state.turboTime > 0 ? 2 : 1;
  const speed = (BASE_SPEED + Math.min(state.score / 820, 5.2)) * speedMultiplier;
  state.distance += speed * dt;
  state.score = Math.floor(state.distance * 10);

  const smooth = 1 - Math.exp(-LANE_SWITCH_SPEED * dt);
  player.position.x = THREE.MathUtils.lerp(player.position.x, state.targetX, smooth);
  player.rotation.z = THREE.MathUtils.lerp(
    player.rotation.z,
    -state.currentLane * 0.2,
    smooth,
  );
  player.rotation.x += dt * 4.1;
  player.rotation.y += dt * 1.2 * -state.currentLane;

  const laneDelta = Math.abs(player.position.x - state.targetX);
  if (state.switchingLane && laneDelta < 0.035) {
    state.switchingLane = false;
    triggerShake(0.105, 0.035);
  }

  recycleTrack(dt, speed);
  updateObstacles(dt, speed);
  updateBoostPads(dt, speed);
  updateCoins(dt, speed);
  updateTrail(dt, speed);
  updateNeon(dt);
  updateCamera(dt);
  updateBackground(dt, speed);
  checkPickups();
  checkCollisions();

  scoreEl.textContent = `Score: ${state.score}`;
  coinsEl.textContent = `Coins: ${state.coins}`;
  if (state.turboTime > 0) {
    turboEl.textContent = `TURBO ${state.turboTime.toFixed(1)}`;
  }
}

function recycleTrack(dt, speed) {
  for (const segment of trackSegments) {
    segment.position.z -= speed * dt;
  }

  let farthestZ = Math.max(...trackSegments.map((segment) => segment.position.z));
  for (const segment of trackSegments) {
    if (segment.position.z < -TRACK_LENGTH * 1.5) {
      segment.position.z = farthestZ + TRACK_LENGTH;
      farthestZ = segment.position.z;
    }
  }
}

function updateObstacles(dt, speed) {
  for (const obstacle of obstacles) {
    if (!obstacle.userData.active) {
      continue;
    }

    obstacle.position.z -= speed * dt;
    if (obstacle.userData.mover) {
      obstacle.userData.movePhase += dt * obstacle.userData.moveSpeed;
      obstacle.position.x = Math.sin(obstacle.userData.movePhase) * LANE_X;
    }
    const pulse = 1 + Math.sin(state.distance * 0.22 + obstacle.userData.phase) * 0.045;
    obstacle.rotation.y += dt * (2.6 + state.score * 0.0009);
    obstacle.rotation.x += dt * 1.15;
    obstacle.rotation.z += dt * obstacle.userData.spin;
    obstacle.scale.setScalar(pulse);

    if (obstacle.position.z < -11) {
      obstacle.visible = false;
      obstacle.userData.active = false;
    }
  }

  while (state.nextObstacleZ < 118) {
    spawnObstacle(state.nextObstacleZ);
    state.nextObstacleZ += OBSTACLE_GAP_MIN + Math.random() * OBSTACLE_GAP_RANDOM;
  }
  state.nextObstacleZ -= speed * dt;
}

function spawnObstacle(z) {
  const obstacle = obstacles.find((item) => !item.userData.active);
  if (!obstacle) {
    return;
  }

  const lane = Math.random() > 0.5 ? 1 : -1;
  obstacle.position.set(
    lane * LANE_X,
    FLOOR_Y + 0.09 + OBSTACLE_SIZE / 2,
    z,
  );
  obstacle.rotation.set(0, Math.random() * Math.PI, 0);
  obstacle.visible = true;
  obstacle.userData.active = true;
  obstacle.userData.lane = lane;
  obstacle.userData.phase = Math.random() * Math.PI * 2;
  obstacle.userData.spin = THREE.MathUtils.randFloat(-1.7, 1.7);
  obstacle.userData.mover = state.score > 350 && Math.random() < Math.min(0.18 + state.score / 4200, 0.48);
  obstacle.userData.movePhase = lane * Math.PI * 0.5;
  obstacle.userData.moveSpeed = THREE.MathUtils.randFloat(0.75, 1.25);
}

function updateBoostPads(dt, speed) {
  for (const boost of boostPads) {
    if (!boost.userData.active) {
      continue;
    }

    boost.position.z -= speed * dt;
    boost.material.emissiveIntensity = 1.05 + Math.sin(state.distance * 0.5 + boost.userData.phase) * 0.32;
    boost.rotation.y = Math.sin(state.distance * 0.05 + boost.userData.phase) * 0.08;

    if (boost.position.z < -11) {
      boost.visible = false;
      boost.userData.active = false;
    }
  }

  while (state.nextBoostZ < 150) {
    if (state.turboTime > 0 || state.boostCooldown > 0) {
      return;
    }
    spawnBoostPad(state.nextBoostZ);
    state.nextBoostZ += THREE.MathUtils.randFloat(86, 126);
  }
  state.nextBoostZ -= speed * dt;
}

function spawnBoostPad(z) {
  const boost = boostPads.find((item) => !item.userData.active);
  if (!boost) {
    return;
  }

  const lane = Math.random() > 0.5 ? 1 : -1;
  boost.position.set(lane * LANE_X, FLOOR_Y + 0.145, z);
  boost.rotation.set(0, 0, 0);
  boost.visible = true;
  boost.userData.active = true;
  boost.userData.phase = Math.random() * Math.PI * 2;
}

function updateCoins(dt, speed) {
  for (const coin of coins) {
    if (!coin.userData.active) {
      continue;
    }

    coin.position.z -= speed * dt;
    coin.rotation.y += dt * 5.8;
    coin.rotation.z += dt * 1.4;
    coin.position.y = coin.userData.baseY + Math.sin(state.distance * 0.18 + coin.userData.phase) * 0.045;

    if (coin.position.z < -11) {
      coin.visible = false;
      coin.userData.active = false;
    }
  }

  while (state.nextCoinZ < 132) {
    spawnCoinCluster(state.nextCoinZ);
    state.nextCoinZ += THREE.MathUtils.randFloat(18, 29);
  }
  state.nextCoinZ -= speed * dt;
}

function spawnCoinCluster(z) {
  const lane = Math.random() > 0.5 ? 1 : -1;
  const amount = Math.random() > 0.72 ? 2 : 1;
  for (let i = 0; i < amount; i += 1) {
    const coin = coins.find((item) => !item.userData.active);
    if (!coin) {
      return;
    }

    coin.position.set(lane * LANE_X, FLOOR_Y + 0.72, z + i * 1.08);
    coin.rotation.set(0, Math.random() * Math.PI, 0);
    coin.visible = true;
    coin.userData.active = true;
    coin.userData.baseY = FLOOR_Y + 0.72;
    coin.userData.phase = Math.random() * Math.PI * 2;
  }
}

function updateCamera(dt) {
  const desiredPosition = new THREE.Vector3(3.55, 2.35, -6.05);
  const lookTarget = new THREE.Vector3(player.position.x * 0.2, FLOOR_Y + 0.34, 5.7);
  camera.position.lerp(desiredPosition, 1 - Math.exp(-7.5 * dt));

  if (state.shakeTime > 0) {
    state.shakeTime = Math.max(state.shakeTime - dt, 0);
    const amount = state.shakePower * (state.shakeTime / Math.max(state.shakeDuration, 0.001));
    camera.position.x += THREE.MathUtils.randFloatSpread(amount);
    camera.position.y += THREE.MathUtils.randFloatSpread(amount * 0.65);
  }

  camera.lookAt(lookTarget);
}

function updateBackground(dt, speed) {
  const positions = starField.geometry.attributes.position;
  const speeds = starField.geometry.attributes.speed;
  for (let i = 0; i < STAR_COUNT; i += 1) {
    const offset = i * 3;
    positions.array[offset + 2] -= speed * dt * speeds.array[i] * 2.8;
    positions.array[offset] += Math.sign(positions.array[offset] || 1) * dt * speeds.array[i] * 1.4;

    if (positions.array[offset + 2] < -22) {
      positions.array[offset] = THREE.MathUtils.randFloatSpread(82);
      positions.array[offset + 1] = THREE.MathUtils.randFloatSpread(48);
      positions.array[offset + 2] = THREE.MathUtils.randFloat(120, 190);
    }
    if (Math.abs(positions.array[offset]) > 56) {
      positions.array[offset] *= -0.55;
    }
  }
  positions.needsUpdate = true;
}

function updateNeon(dt) {
  const galaxyColor = getGalaxyColor();
  const pulse = 0.62 + Math.sin(state.distance * 0.34) * 0.18;
  const turboLift = state.turboTime > 0 ? 0.28 : 0;

  railMaterial.emissive.lerp(galaxyColor, 1 - Math.exp(-2.4 * dt));
  laneMaterial.emissive.lerp(galaxyColor, 1 - Math.exp(-2.4 * dt));
  speedLineMaterial.color.lerp(galaxyColor, 1 - Math.exp(-3.2 * dt));
  speedLineMaterial.opacity = THREE.MathUtils.clamp(0.34 + pulse * 0.22 + turboLift, 0.28, 0.72);
  railMaterial.emissiveIntensity = 0.34 + pulse * 0.34 + turboLift;
  laneMaterial.emissiveIntensity = 0.16 + pulse * 0.18 + turboLift * 0.55;
  playerMaterial.emissiveIntensity = state.turboTime > 0 ? 2.85 : 1.85;
  starField.material.color.lerp(galaxyColor, 1 - Math.exp(-1.2 * dt));
}

function getGalaxyColor() {
  const palette = [
    new THREE.Color(0x20e8ff),
    new THREE.Color(0x884dff),
    new THREE.Color(0xff43b0),
    new THREE.Color(0xff8a24),
  ];
  const progress = (state.score / 520) % (palette.length - 1);
  const index = Math.floor(progress);
  const mix = progress - index;
  return palette[index].clone().lerp(palette[index + 1], mix);
}

function updateTrail(dt, speed) {
  state.trailTimer += dt;
  const laneDelta = Math.abs(player.position.x - state.targetX);
  if (state.trailTimer > TRAIL_INTERVAL || laneDelta > 0.12) {
    emitTrail();
    state.trailTimer = 0;
  }

  for (const trail of trailPieces) {
    if (!trail.visible) {
      continue;
    }

    trail.userData.life -= dt;
    trail.position.z -= speed * dt;
    trail.scale.multiplyScalar(1 + dt * 1.9);
    const alpha = Math.max(trail.userData.life / trail.userData.maxLife, 0);
    trail.material.opacity = alpha * 0.45;

    if (trail.userData.life <= 0) {
      trail.visible = false;
    }
  }
}

function emitTrail() {
  const trail = trailPieces.find((item) => !item.visible) ?? trailPieces[0];
  trail.position.copy(player.position);
  trail.position.z -= 0.28;
  trail.rotation.copy(player.rotation);
  trail.scale.setScalar(1);
  trail.material.color.copy(playerMaterial.emissive);
  trail.material.opacity = 0.45;
  trail.userData.life = trail.userData.maxLife;
  trail.visible = true;
}

function checkPickups() {
  playerBox.setFromObject(player);
  playerBox.expandByScalar(0.05);

  for (const boost of boostPads) {
    if (!boost.userData.active) {
      continue;
    }

    boostBox.setFromObject(boost);
    if (playerBox.intersectsBox(boostBox)) {
      boost.visible = false;
      boost.userData.active = false;
      activateTurbo();
    }
  }

  for (const coin of coins) {
    if (!coin.userData.active) {
      continue;
    }

    coinBox.setFromObject(coin);
    if (playerBox.intersectsBox(coinBox)) {
      coin.visible = false;
      coin.userData.active = false;
      state.coins += 1;
      coinsEl.textContent = `Coins: ${state.coins}`;
      audioEngine.playCoin();
    }
  }
}

function activateTurbo() {
  state.turboTime = BOOST_DURATION;
  state.boostCooldown = BOOST_DURATION + BOOST_COOLDOWN;
  state.nextBoostZ = 185;
  turboEl.classList.remove("hidden");
  turboEl.textContent = `TURBO ${BOOST_DURATION.toFixed(1)}`;
  for (const boost of boostPads) {
    boost.visible = false;
    boost.userData.active = false;
  }
  triggerShake(0.18, 0.055);
  audioEngine.setTurbo(true);
  audioEngine.playBoost();
}

function checkCollisions() {
  if (state.ending) {
    return;
  }

  playerBox.setFromObject(player);
  playerBox.expandByScalar(-0.08);

  for (const obstacle of obstacles) {
    if (!obstacle.userData.active) {
      continue;
    }

    obstacleBox.setFromObject(obstacle);
    obstacleBox.expandByScalar(-0.06);
    if (playerBox.intersectsBox(obstacleBox)) {
      hitObstacle(obstacle);
      break;
    }
  }
}

function hitObstacle(obstacle) {
  obstacle.visible = false;
  obstacle.userData.active = false;
  obstacle.scale.setScalar(1);

  if (state.turboTime > 0) {
    state.coins += 1;
    coinsEl.textContent = `Coins: ${state.coins}`;
    triggerShake(0.12, 0.045);
    audioEngine.playCrash();
    return;
  }

  if (state.coins >= SHIELD_COST) {
    state.coins -= SHIELD_COST;
    coinsEl.textContent = `Coins: ${state.coins}`;
    showDamageFlash();
    triggerShake(0.24, 0.075);
    audioEngine.playCrash();
    return;
  }

  showDamageFlash();
  triggerShake(0.34, 0.095);
  state.ending = true;
  state.running = false;
  window.setTimeout(endGame, 170);
}

function onKeyDown(event) {
  if (event.code !== "Space") {
    return;
  }

  event.preventDefault();
  audioEngine.start();
  if (!state.started) {
    startGame();
    return;
  }
  if (!state.running) {
    resetGame();
    return;
  }

  state.currentLane *= -1;
  state.targetX = state.currentLane * LANE_X;
  state.switchingLane = true;
  audioEngine.playSwitch();
}

function endGame() {
  if (!state.started || !gameOverEl.classList.contains("hidden")) {
    return;
  }
  state.running = false;
  audioEngine.setIntensity(0.42);
  audioEngine.setTurbo(false);
  audioEngine.playCrash();
  finalScoreEl.textContent = `Score: ${state.score}`;
  gameOverEl.classList.remove("hidden");
}

function startGame() {
  state.started = true;
  resetGame(true);
}

function triggerShake(duration, power) {
  state.shakeTime = duration;
  state.shakeDuration = duration;
  state.shakePower = power;
}

function showDamageFlash() {
  damageFlashEl.classList.add("active");
  window.setTimeout(() => damageFlashEl.classList.remove("active"), 90);
}

function resetGame(playNow = state.started) {
  state.running = playNow;
  state.distance = 0;
  state.score = 0;
  state.coins = 0;
  state.currentLane = 1;
  state.targetX = LANE_X;
  state.nextObstacleZ = 18;
  state.nextBoostZ = 72;
  state.nextCoinZ = 22;
  state.turboTime = 0;
  state.boostCooldown = 0;
  state.trailTimer = 0;
  state.shakeTime = 0;
  state.shakePower = 0;
  state.switchingLane = false;
  state.ending = false;
  audioEngine.setIntensity(1);
  audioEngine.setTurbo(false);
  gameOverEl.classList.add("hidden");
  turboEl.classList.add("hidden");
  startScreenEl.classList.toggle("hidden", state.started);
  damageFlashEl.classList.remove("active");

  player.position.set(state.targetX, FLOOR_Y + PLAYER_SIZE / 2, 0);
  player.rotation.set(0, 0, 0);
  camera.position.set(3.55, 2.35, -6.05);
  camera.lookAt(0, FLOOR_Y + 0.34, 5.7);

  trackSegments.forEach((segment, index) => {
    segment.position.z = index * TRACK_LENGTH - TRACK_LENGTH;
  });

  for (const trail of trailPieces) {
    trail.visible = false;
    trail.userData.life = 0;
    trail.material.opacity = 0;
  }

  for (const obstacle of obstacles) {
    obstacle.visible = false;
    obstacle.userData.active = false;
    obstacle.scale.setScalar(1);
  }

  for (const boost of boostPads) {
    boost.visible = false;
    boost.userData.active = false;
  }

  for (const coin of coins) {
    coin.visible = false;
    coin.userData.active = false;
  }

  for (let i = 0; i < 13; i += 1) {
    spawnObstacle(state.nextObstacleZ);
    state.nextObstacleZ += OBSTACLE_GAP_MIN + Math.random() * OBSTACLE_GAP_RANDOM;
  }

  for (let i = 0; i < 5; i += 1) {
    spawnCoinCluster(state.nextCoinZ);
    state.nextCoinZ += THREE.MathUtils.randFloat(18, 29);
  }

  for (let i = 0; i < 1; i += 1) {
    spawnBoostPad(state.nextBoostZ);
    state.nextBoostZ += THREE.MathUtils.randFloat(86, 126);
  }

  scoreEl.textContent = "Score: 0";
  coinsEl.textContent = "Coins: 0";
  lastFrameTime = performance.now();
}

function createAudioEngine() {
  let context;
  let master;
  let filter;
  let delay;
  let feedback;
  let started = false;
  let stepTimer;
  let bassOsc;
  let bassGain;
  let padOscA;
  let padOscB;
  let padGain;
  let intensity = 1;
  let step = 0;
  let turbo = false;

  const tempo = 128;
  const beat = 60 / tempo;
  let currentBeat = beat;
  const bassNotes = [55, 55, 82.41, 65.41, 55, 73.42, 82.41, 98];
  const leadNotes = [220, 246.94, 293.66, 329.63, 293.66, 246.94, 220, 196];

  function start() {
    if (started) {
      context.resume();
      return;
    }

    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) {
      return;
    }

    context = new AudioContext();
    master = context.createGain();
    master.gain.value = 0.0001;

    filter = context.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 4200;
    filter.Q.value = 0.7;

    delay = context.createDelay(0.5);
    delay.delayTime.value = beat * 0.75;

    feedback = context.createGain();
    feedback.gain.value = 0.22;

    delay.connect(feedback);
    feedback.connect(delay);
    delay.connect(filter);
    filter.connect(master);
    master.connect(context.destination);

    bassOsc = context.createOscillator();
    bassOsc.type = "sawtooth";
    bassGain = context.createGain();
    bassGain.gain.value = 0.0001;
    bassOsc.connect(bassGain);
    bassGain.connect(filter);
    bassOsc.start();

    padOscA = context.createOscillator();
    padOscB = context.createOscillator();
    padOscA.type = "triangle";
    padOscB.type = "sine";
    padOscA.frequency.value = 110;
    padOscB.frequency.value = 164.82;
    padGain = context.createGain();
    padGain.gain.value = 0.0001;
    padOscA.connect(padGain);
    padOscB.connect(padGain);
    padGain.connect(filter);
    padOscA.start();
    padOscB.start();

    master.gain.exponentialRampToValueAtTime(0.23, context.currentTime + 0.7);
    padGain.gain.exponentialRampToValueAtTime(0.035, context.currentTime + 1.4);

    started = true;
    scheduleStep();
    stepTimer = window.setInterval(scheduleStep, currentBeat * 1000);
  }

  function scheduleStep() {
    if (!context) {
      return;
    }

    const now = context.currentTime;
    const bassFreq = bassNotes[step % bassNotes.length];
    const leadFreq = leadNotes[step % leadNotes.length];

    bassOsc.frequency.setTargetAtTime(bassFreq, now, 0.035);
    bassGain.gain.cancelScheduledValues(now);
    bassGain.gain.setValueAtTime(0.0001, now);
    bassGain.gain.exponentialRampToValueAtTime(0.065 * intensity, now + 0.025);
    bassGain.gain.exponentialRampToValueAtTime(0.0001, now + currentBeat * 0.72);

    if (step % 2 === 0) {
      playTone(leadFreq, "square", 0.022 * intensity, 0.11, now + 0.02, delay);
    }

    if (step % 4 === 2) {
      playTone(440, "triangle", 0.018 * intensity, 0.06, now + 0.01, filter);
    }

    step += 1;
  }

  function playTone(frequency, type, volume, duration, when, destination = filter) {
    if (!context) {
      return;
    }

    const osc = context.createOscillator();
    const gain = context.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(frequency, when);
    gain.gain.setValueAtTime(0.0001, when);
    gain.gain.exponentialRampToValueAtTime(Math.max(volume, 0.0002), when + 0.012);
    gain.gain.exponentialRampToValueAtTime(0.0001, when + duration);
    osc.connect(gain);
    gain.connect(destination);
    osc.start(when);
    osc.stop(when + duration + 0.03);
  }

  function playSwitch() {
    if (!context) {
      return;
    }
    const now = context.currentTime;
    playTone(523.25, "triangle", 0.04, 0.1, now, delay);
    playTone(783.99, "sine", 0.026, 0.14, now + 0.045, delay);
  }

  function playCrash() {
    if (!context) {
      return;
    }
    const now = context.currentTime;
    playTone(130.81, "sawtooth", 0.08, 0.22, now, filter);
    playTone(65.41, "triangle", 0.08, 0.34, now + 0.04, filter);
  }

  function playCoin() {
    if (!context) {
      return;
    }
    const now = context.currentTime;
    playTone(987.77, "sine", 0.025, 0.075, now, delay);
    playTone(1318.51, "triangle", 0.018, 0.08, now + 0.045, delay);
  }

  function playBoost() {
    if (!context) {
      return;
    }
    const now = context.currentTime;
    playTone(196, "sawtooth", 0.055, 0.18, now, filter);
    playTone(392, "square", 0.04, 0.16, now + 0.07, delay);
    playTone(784, "triangle", 0.035, 0.22, now + 0.14, delay);
  }

  function setTurbo(active) {
    turbo = active;
    currentBeat = turbo ? beat * 0.58 : beat;
    if (filter && context) {
      filter.frequency.setTargetAtTime(turbo ? 6500 : 4200, context.currentTime, 0.09);
      feedback.gain.setTargetAtTime(turbo ? 0.32 : 0.22, context.currentTime, 0.08);
    }
    if (stepTimer) {
      window.clearInterval(stepTimer);
      stepTimer = window.setInterval(scheduleStep, currentBeat * 1000);
    }
  }

  function setIntensity(value) {
    intensity = value;
    if (!context || !master) {
      return;
    }
    const target = state.running ? 0.23 * value : 0.12;
    master.gain.cancelScheduledValues(context.currentTime);
    master.gain.setTargetAtTime(target, context.currentTime, 0.12);
  }

  return { start, playSwitch, playCrash, playCoin, playBoost, setIntensity, setTurbo };
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
