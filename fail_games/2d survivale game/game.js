const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const statusLabel = document.getElementById("status");
const inventoryLabel = document.getElementById("inventory");
const toolLabel = document.getElementById("tool");
const bannerText = document.getElementById("banner-text");

ctx.imageSmoothingEnabled = false;

const TILE_SIZE = 48;
const WORLD_WIDTH = 72;
const WORLD_HEIGHT = 72;
const TREE_DENSITY = 0.085;
const PLAYER_SPEED = 245;
const ACTION_DURATION = 0.34;
const ARROW_SPEED = 680;
const DAY_LENGTH = 95;
const HOUSE_WIDTH = 360;
const HOUSE_HEIGHT = 250;

const ASSET_SOURCES = {
  playerIdle: [
    "./Tiny RPG Character Asset Pack v1.03 -Free Soldier&Orc/Characters(100x100)/Soldier/Soldier/Soldier-Idle.png",
  ],
  playerWalk: [
    "./Tiny RPG Character Asset Pack v1.03 -Free Soldier&Orc/Characters(100x100)/Soldier/Soldier/Soldier-Walk.png",
  ],
  playerAxe: [
    "./Tiny RPG Character Asset Pack v1.03 -Free Soldier&Orc/Characters(100x100)/Soldier/Soldier/Soldier-Attack02.png",
  ],
  playerBow: [
    "./Tiny RPG Character Asset Pack v1.03 -Free Soldier&Orc/Characters(100x100)/Soldier/Soldier/Soldier-Attack03.png",
  ],
  arrow: [
    "./Tiny RPG Character Asset Pack v1.03 -Free Soldier&Orc/Arrow(Projectile)/Arrow01(32x32).png",
    "./Tiny RPG Character Asset Pack v1.03 -Free Soldier&Orc/Characters(100x100)/Soldier/Arrow(projectile)/Arrow01(32x32).png",
  ],
  toolSheet: [
    "./Screenshot 2026-04-16 at 19.33.59.png",
  ],
};

const keys = new Set();
const pressedKeys = new Set();
const mouse = {
  screenX: 0,
  screenY: 0,
  worldX: 0,
  worldY: 0,
  down: false,
};

const rng = createMulberry32(0x51a2d3f);
const noiseSeedA = rng() * 1000;
const noiseSeedB = rng() * 1000;

const assets = {};
const world = {
  tiles: [],
  trees: [],
  arrows: [],
  woodDrops: [],
  house: null,
  insideDoor: null,
};

const player = {
  x: WORLD_WIDTH * TILE_SIZE * 0.5,
  y: WORLD_HEIGHT * TILE_SIZE * 0.5,
  radius: 20,
  drawWidth: 214,
  drawHeight: 214,
  facing: 0,
  moveX: 0,
  moveY: 1,
  bob: 0,
  action: null,
  equipped: "axe",
  wood: 0,
  arrows: 12,
  inHouse: false,
};

const camera = {
  x: player.x,
  y: player.y,
};

const gameState = {
  time: 0,
  prompt: "Cut trees for wood, press 2 for bow, and reach the house door with E to enter.",
};

function createMulberry32(seed) {
  return function next() {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function smoothstep(edge0, edge1, value) {
  const t = clamp((value - edge0) / (edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
}

function resizeCanvas() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.floor(window.innerWidth * dpr);
  canvas.height = Math.floor(window.innerHeight * dpr);
  canvas.style.width = `${window.innerWidth}px`;
  canvas.style.height = `${window.innerHeight}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.imageSmoothingEnabled = false;
}

window.addEventListener("resize", resizeCanvas);

window.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (!keys.has(key)) {
    pressedKeys.add(key);
  }
  keys.add(key);
});

window.addEventListener("keyup", (event) => {
  const key = event.key.toLowerCase();
  keys.delete(key);
});

canvas.addEventListener("mousemove", (event) => {
  const rect = canvas.getBoundingClientRect();
  mouse.screenX = event.clientX - rect.left;
  mouse.screenY = event.clientY - rect.top;
});

canvas.addEventListener("mousedown", () => {
  mouse.down = true;
  useCurrentTool();
});

window.addEventListener("mouseup", () => {
  mouse.down = false;
});

canvas.addEventListener("contextmenu", (event) => {
  event.preventDefault();
});

async function loadImageFromCandidates(paths) {
  for (const path of paths) {
    try {
      const image = await loadImage(path);
      return image;
    } catch {
      continue;
    }
  }

  return null;
}

function loadImage(path) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Failed to load ${path}`));
    image.src = path;
  });
}

function makeCanvas(width, height) {
  const buffer = document.createElement("canvas");
  buffer.width = width;
  buffer.height = height;
  return buffer;
}

function drawPixelRect(context, x, y, width, height, color) {
  context.fillStyle = color;
  context.fillRect(x, y, width, height);
}

function createGrassTexture() {
  const buffer = makeCanvas(TILE_SIZE * 4, TILE_SIZE);
  const bctx = buffer.getContext("2d");
  bctx.imageSmoothingEnabled = false;

  const palettes = [
    ["#b9ec8d", "#9dd96f", "#7ec058", "#5f9e46"],
    ["#c8f3a0", "#ace37b", "#86c95e", "#679f46"],
    ["#c7e88c", "#aad46d", "#88be56", "#5e9445"],
    ["#d4f0a8", "#b3dd80", "#8ec165", "#6aa14c"],
  ];

  palettes.forEach((palette, index) => {
    const offsetX = index * TILE_SIZE;
    for (let y = 0; y < TILE_SIZE; y += 4) {
      for (let x = 0; x < TILE_SIZE; x += 4) {
        const tone = palette[(x / 4 + y / 4 + index) % palette.length];
        drawPixelRect(bctx, offsetX + x, y, 4, 4, tone);
      }
    }

    bctx.fillStyle = "rgba(255,255,255,0.18)";
    for (let i = 0; i < 6; i += 1) {
      bctx.fillRect(offsetX + 4 + i * 7, 6 + (i % 3) * 9, 2, 6);
    }

    bctx.fillStyle = "rgba(71,109,39,0.25)";
    for (let i = 0; i < 10; i += 1) {
      bctx.fillRect(offsetX + ((i * 9) % TILE_SIZE), 28 + ((i * 5) % 14), 3, 3);
    }
  });

  return buffer;
}

function createTreeTexture(theme) {
  const palettes = {
    green: {
      leaves: ["#7eb94e", "#5b963a", "#48752d", "#33511f"],
      trunk: ["#7d5433", "#5d3f24", "#402912"],
    },
    gold: {
      leaves: ["#e5c25c", "#c49535", "#9d6b23", "#6b4619"],
      trunk: ["#7b5537", "#5d4127", "#3d2812"],
    },
    teal: {
      leaves: ["#8de3a3", "#5dc786", "#3a9664", "#286348"],
      trunk: ["#74533b", "#593f2b", "#382518"],
    },
  };

  const palette = palettes[theme];
  const buffer = makeCanvas(124, 156);
  const bctx = buffer.getContext("2d");
  bctx.imageSmoothingEnabled = false;

  for (let y = 0; y < 72; y += 4) {
    for (let x = 0; x < 82; x += 4) {
      const dx = x - 41;
      const dy = y - 34;
      const distance = Math.sqrt(dx * dx + dy * dy);
      if (distance < 40 + ((x + y) % 7) - 2) {
        const colorIndex = clamp(Math.floor(distance / 12), 0, palette.leaves.length - 1);
        drawPixelRect(bctx, 20 + x, 6 + y, 4, 4, palette.leaves[colorIndex]);
      }
    }
  }

  drawPixelRect(bctx, 54, 70, 18, 64, palette.trunk[1]);
  drawPixelRect(bctx, 58, 64, 10, 70, palette.trunk[0]);
  drawPixelRect(bctx, 51, 84, 6, 36, palette.trunk[2]);
  drawPixelRect(bctx, 69, 88, 5, 30, palette.trunk[2]);

  const trunk = makeCanvas(buffer.width, buffer.height);
  const canopy = makeCanvas(buffer.width, buffer.height);
  const trunkCtx = trunk.getContext("2d");
  const canopyCtx = canopy.getContext("2d");
  trunkCtx.imageSmoothingEnabled = false;
  canopyCtx.imageSmoothingEnabled = false;

  trunkCtx.drawImage(buffer, 0, 70, buffer.width, buffer.height - 70, 0, 70, buffer.width, buffer.height - 70);
  canopyCtx.drawImage(buffer, 0, 0, buffer.width, 100, 0, 0, buffer.width, 100);

  return { full: buffer, trunk, canopy };
}

function createToolSheetFallback() {
  const buffer = makeCanvas(324, 239);
  const bctx = buffer.getContext("2d");
  bctx.imageSmoothingEnabled = false;
  bctx.fillStyle = "#a8d7e4";
  bctx.fillRect(0, 0, buffer.width, buffer.height);

  drawPixelRect(bctx, 42, 20, 18, 6, "#6b6b6b");
  drawPixelRect(bctx, 36, 26, 8, 22, "#77512f");
  drawPixelRect(bctx, 47, 27, 9, 15, "#9d9d9d");

  drawPixelRect(bctx, 172, 20, 6, 22, "#6a4329");
  drawPixelRect(bctx, 180, 18, 12, 12, "#765536");
  drawPixelRect(bctx, 194, 20, 4, 22, "#765536");

  drawPixelRect(bctx, 83, 82, 24, 16, "#8f6031");
  drawPixelRect(bctx, 98, 78, 9, 6, "#b48046");

  return buffer;
}

function cropToolSprite(sheet, sx, sy, sw, sh, scale = 2) {
  const buffer = makeCanvas(sw * scale, sh * scale);
  const bctx = buffer.getContext("2d");
  bctx.imageSmoothingEnabled = false;
  bctx.drawImage(sheet, sx, sy, sw, sh, 0, 0, buffer.width, buffer.height);
  return buffer;
}

function createHouseTexture() {
  const buffer = makeCanvas(240, 190);
  const bctx = buffer.getContext("2d");
  bctx.imageSmoothingEnabled = false;

  drawPixelRect(bctx, 0, 74, 240, 116, "#e6d0a3");
  drawPixelRect(bctx, 12, 74, 216, 104, "#c28a4d");
  drawPixelRect(bctx, 20, 82, 200, 88, "#d79a58");
  drawPixelRect(bctx, 86, 110, 68, 60, "#6c4528");
  drawPixelRect(bctx, 94, 118, 52, 52, "#845332");
  drawPixelRect(bctx, 115, 134, 8, 8, "#d7b97d");
  drawPixelRect(bctx, 40, 104, 34, 32, "#85cae8");
  drawPixelRect(bctx, 166, 104, 34, 32, "#85cae8");

  for (let i = 0; i < 7; i += 1) {
    drawPixelRect(bctx, 20 + i * 30, 54 - i * 4, 24, 28 + i * 4, "#8b4d2d");
  }
  drawPixelRect(bctx, 0, 50, 240, 16, "#6d321e");
  drawPixelRect(bctx, 12, 66, 216, 8, "#96512d");

  return buffer;
}

function createHouseInteriorTexture() {
  const buffer = makeCanvas(420, 300);
  const bctx = buffer.getContext("2d");
  bctx.imageSmoothingEnabled = false;

  drawPixelRect(bctx, 0, 0, 420, 300, "#d3b07a");
  for (let y = 0; y < 300; y += 20) {
    for (let x = 0; x < 420; x += 20) {
      bctx.fillStyle = (x + y) % 40 === 0 ? "#ca9f63" : "#deb882";
      bctx.fillRect(x, y, 20, 20);
    }
  }

  drawPixelRect(bctx, 0, 0, 420, 30, "#8a613f");
  drawPixelRect(bctx, 0, 270, 420, 30, "#8a613f");
  drawPixelRect(bctx, 0, 0, 24, 300, "#8a613f");
  drawPixelRect(bctx, 396, 0, 24, 300, "#8a613f");
  drawPixelRect(bctx, 152, 18, 116, 46, "#8a5c30");
  drawPixelRect(bctx, 272, 82, 90, 42, "#8d5a38");
  drawPixelRect(bctx, 52, 194, 96, 44, "#93663d");
  drawPixelRect(bctx, 180, 260, 60, 40, "#6d4528");
  return buffer;
}

function createCampfireTexture() {
  const buffer = makeCanvas(44, 40);
  const bctx = buffer.getContext("2d");
  bctx.imageSmoothingEnabled = false;
  drawPixelRect(bctx, 10, 24, 8, 4, "#6f4b2a");
  drawPixelRect(bctx, 24, 24, 8, 4, "#6f4b2a");
  drawPixelRect(bctx, 14, 22, 16, 4, "#8b5a31");
  drawPixelRect(bctx, 16, 10, 12, 12, "#ffb347");
  drawPixelRect(bctx, 18, 6, 8, 10, "#ffd86e");
  drawPixelRect(bctx, 20, 12, 4, 7, "#fff2b8");
  return buffer;
}

function createArrowFallback() {
  const buffer = makeCanvas(32, 32);
  const bctx = buffer.getContext("2d");
  bctx.imageSmoothingEnabled = false;
  drawPixelRect(bctx, 5, 15, 18, 2, "#6b4628");
  drawPixelRect(bctx, 21, 13, 7, 6, "#bcbcbc");
  drawPixelRect(bctx, 3, 12, 4, 8, "#ded8c9");
  return buffer;
}

async function loadAssets() {
  statusLabel.textContent = "Loading assets...";

  assets.playerIdle = await loadImageFromCandidates(ASSET_SOURCES.playerIdle);
  assets.playerWalk = await loadImageFromCandidates(ASSET_SOURCES.playerWalk);
  assets.playerAxe = await loadImageFromCandidates(ASSET_SOURCES.playerAxe);
  assets.playerBow = await loadImageFromCandidates(ASSET_SOURCES.playerBow);
  assets.arrow = (await loadImageFromCandidates(ASSET_SOURCES.arrow)) || createArrowFallback();

  const toolSheet = (await loadImageFromCandidates(ASSET_SOURCES.toolSheet)) || createToolSheetFallback();
  assets.icons = {
    axe: cropToolSprite(toolSheet, 39, 17, 26, 30, 2),
    bow: cropToolSprite(toolSheet, 165, 15, 40, 30, 2),
    wood: cropToolSprite(toolSheet, 78, 74, 34, 28, 2),
  };

  assets.grass = createGrassTexture();
  assets.trees = {
    green: createTreeTexture("green"),
    gold: createTreeTexture("gold"),
    teal: createTreeTexture("teal"),
  };
  assets.house = createHouseTexture();
  assets.houseInterior = createHouseInteriorTexture();
  assets.campfire = createCampfireTexture();
}

function getAnimationFrame(sheet, time, fps) {
  const frameHeight = sheet.height;
  const frameWidth = frameHeight;
  const frameCount = Math.max(1, Math.floor(sheet.width / frameWidth));
  const frameIndex = Math.floor(time * fps) % frameCount;
  return {
    frameWidth,
    frameHeight,
    frameCount,
    sx: frameIndex * frameWidth,
  };
}

function sampleNoise(x, y, offset) {
  const waveA = Math.sin(x + offset) * 0.5 + 0.5;
  const waveB = Math.cos(y * 1.13 + offset * 0.7) * 0.5 + 0.5;
  const waveC = Math.sin((x + y) * 0.69 + offset * 1.9) * 0.5 + 0.5;
  return (waveA + waveB + waveC) / 3;
}

function chooseGroundTile(x, y) {
  const a = sampleNoise(x * 0.12, y * 0.12, noiseSeedA);
  const b = sampleNoise(x * 0.18, y * 0.18, noiseSeedB);
  if (b > 0.72) return 3;
  if (a > 0.62) return 2;
  if (a < 0.35) return 1;
  return 0;
}

function countNearbyTrees(tileX, tileY) {
  let count = 0;
  for (const tree of world.trees) {
    if (Math.abs(tree.tileX - tileX) <= 1 && Math.abs(tree.tileY - tileY) <= 1 && tree.health > 0) {
      count += 1;
    }
  }
  return count;
}

function createTree(tileX, tileY, theme) {
  const sway = sampleNoise(tileX * 0.2, tileY * 0.2, noiseSeedB);
  return {
    id: `${tileX}-${tileY}`,
    tileX,
    tileY,
    x: tileX * TILE_SIZE + TILE_SIZE / 2 + (sway - 0.5) * 12,
    y: tileY * TILE_SIZE + TILE_SIZE / 2 + 12 + (sway - 0.5) * 8,
    theme,
    health: 4,
    maxHealth: 4,
    trunkRadius: 14,
    shadowScale: 1 + sway * 0.25,
  };
}

function createWorld() {
  world.tiles = Array.from({ length: WORLD_HEIGHT }, (_, y) =>
    Array.from({ length: WORLD_WIDTH }, (_, x) => chooseGroundTile(x, y)),
  );
  world.trees = [];
  world.arrows = [];
  world.woodDrops = [];

  const spawnRadius = 8;
  const centerTileX = Math.floor(WORLD_WIDTH / 2);
  const centerTileY = Math.floor(WORLD_HEIGHT / 2);
  const themes = ["green", "gold", "teal"];

  world.house = {
    x: centerTileX * TILE_SIZE + 460,
    y: centerTileY * TILE_SIZE - 140,
    width: HOUSE_WIDTH,
    height: HOUSE_HEIGHT,
    doorWidth: 58,
    doorHeight: 36,
  };

  for (let y = 2; y < WORLD_HEIGHT - 2; y += 1) {
    for (let x = 2; x < WORLD_WIDTH - 2; x += 1) {
      const dx = x - centerTileX;
      const dy = y - centerTileY;
      const nearHouse = Math.abs(x * TILE_SIZE - world.house.x) < 230 && Math.abs(y * TILE_SIZE - world.house.y) < 210;
      if (Math.sqrt(dx * dx + dy * dy) < spawnRadius || nearHouse) {
        continue;
      }

      const placementNoise = sampleNoise(x * 0.31, y * 0.31, noiseSeedA);
      if (placementNoise < 0.56 || rng() > TREE_DENSITY + placementNoise * 0.12) {
        continue;
      }
      if (countNearbyTrees(x, y) > 2) {
        continue;
      }

      const theme = themes[Math.floor(sampleNoise(x * 0.16, y * 0.16, noiseSeedB) * themes.length)];
      world.trees.push(createTree(x, y, theme));
    }
  }

  world.insideDoor = {
    x: 210,
    y: HOUSE_HEIGHT + 34,
  };

  player.x = centerTileX * TILE_SIZE;
  player.y = centerTileY * TILE_SIZE;
  player.inHouse = false;
}

function getHouseDoorWorldPosition() {
  return {
    x: world.house.x,
    y: world.house.y + world.house.height * 0.5 - 8,
  };
}

function update(deltaTime) {
  gameState.time = (gameState.time + deltaTime / DAY_LENGTH) % 1;
  updateMouseWorldPosition();
  updateInputs();
  updatePlayer(deltaTime);
  updateArrows(deltaTime);
  collectWoodDrops();
  updateCamera(deltaTime);
  updateUi();
  pressedKeys.clear();
}

function updateInputs() {
  if (pressedKeys.has("1")) {
    player.equipped = "axe";
  }
  if (pressedKeys.has("2")) {
    player.equipped = "bow";
  }

  if (pressedKeys.has("e")) {
    tryToggleHouse();
  }
}

function updateMouseWorldPosition() {
  mouse.worldX = mouse.screenX + camera.x - window.innerWidth / 2;
  mouse.worldY = mouse.screenY + camera.y - window.innerHeight / 2;
}

function useCurrentTool() {
  if (player.action) {
    return;
  }

  if (player.equipped === "bow") {
    if (player.arrows <= 0) {
      gameState.prompt = "No arrows left. Switch back to the axe with 1 and cut more trees.";
      return;
    }

    player.action = { type: "bow", timer: ACTION_DURATION * 0.9, hitDone: false };
    return;
  }

  player.action = { type: "axe", timer: ACTION_DURATION, hitDone: false };
}

function updatePlayer(deltaTime) {
  let inputX = 0;
  let inputY = 0;

  if (keys.has("w")) inputY -= 1;
  if (keys.has("s")) inputY += 1;
  if (keys.has("a")) inputX -= 1;
  if (keys.has("d")) inputX += 1;

  const length = Math.hypot(inputX, inputY) || 1;
  inputX /= length;
  inputY /= length;

  player.moveX = inputX;
  player.moveY = inputY;

  if (Math.abs(inputX) > 0.001 || Math.abs(inputY) > 0.001) {
    player.facing = Math.atan2(inputY, inputX);
    player.bob += deltaTime * 9;
  } else {
    const dx = mouse.worldX - player.x;
    const dy = mouse.worldY - player.y;
    if (Math.abs(dx) + Math.abs(dy) > 0.01) {
      player.facing = Math.atan2(dy, dx);
    }
  }

  movePlayer(inputX * PLAYER_SPEED * deltaTime, 0);
  movePlayer(0, inputY * PLAYER_SPEED * deltaTime);

  if (player.inHouse) {
    player.x = clamp(player.x, 54, HOUSE_WIDTH - 54);
    player.y = clamp(player.y, 56, HOUSE_HEIGHT + 42);
  } else {
    player.x = clamp(player.x, player.radius, WORLD_WIDTH * TILE_SIZE - player.radius);
    player.y = clamp(player.y, player.radius, WORLD_HEIGHT * TILE_SIZE - player.radius);
  }

  if (player.action) {
    player.action.timer = Math.max(0, player.action.timer - deltaTime);
    const progress = 1 - player.action.timer / ACTION_DURATION;

    if (!player.action.hitDone && progress > 0.38) {
      if (player.action.type === "axe") {
        applyAxeHit();
      } else if (player.action.type === "bow") {
        shootArrow();
      }
      player.action.hitDone = true;
    }

    if (player.action.timer <= 0) {
      player.action = null;
    }
  }
}

function movePlayer(dx, dy) {
  player.x += dx;
  player.y += dy;

  if (player.inHouse) {
    return;
  }

  for (const tree of world.trees) {
    if (tree.health <= 0) {
      continue;
    }

    const distance = Math.hypot(player.x - tree.x, player.y - tree.y);
    const minDistance = player.radius + tree.trunkRadius;
    if (distance > 0 && distance < minDistance) {
      const angle = Math.atan2(player.y - tree.y, player.x - tree.x);
      player.x = tree.x + Math.cos(angle) * minDistance;
      player.y = tree.y + Math.sin(angle) * minDistance;
    }
  }

  const houseDistanceX = Math.abs(player.x - world.house.x);
  const houseDistanceY = Math.abs(player.y - world.house.y);
  if (houseDistanceX < world.house.width * 0.5 + player.radius && houseDistanceY < world.house.height * 0.5 + player.radius) {
    const door = getHouseDoorWorldPosition();
    const withinDoor = Math.abs(player.x - door.x) < world.house.doorWidth * 0.5 && player.y > door.y;
    if (!withinDoor) {
      const overlapX = world.house.width * 0.5 + player.radius - houseDistanceX;
      const overlapY = world.house.height * 0.5 + player.radius - houseDistanceY;
      if (overlapX < overlapY) {
        player.x += player.x < world.house.x ? -overlapX : overlapX;
      } else {
        player.y += player.y < world.house.y ? -overlapY : overlapY;
      }
    }
  }
}

function applyAxeHit() {
  if (player.inHouse) {
    return;
  }

  const hitAngle = player.facing;
  const hitX = player.x + Math.cos(hitAngle) * 54;
  const hitY = player.y + Math.sin(hitAngle) * 54;

  for (const tree of world.trees) {
    if (tree.health <= 0) {
      continue;
    }

    const distance = Math.hypot(hitX - tree.x, hitY - tree.y);
    if (distance <= tree.trunkRadius + 26) {
      tree.health -= 1;
      if (tree.health <= 0) {
        dropWood(tree);
        gameState.prompt = "Tree down. Walk over the wood to collect it for campfires later.";
      } else {
        gameState.prompt = "The axe is working. Keep chopping to bring the tree down.";
      }
      return;
    }
  }

  gameState.prompt = "Swing the axe closer to a tree trunk to collect wood.";
}

function dropWood(tree) {
  const pieceCount = 2 + Math.floor(rng() * 2);
  for (let i = 0; i < pieceCount; i += 1) {
    world.woodDrops.push({
      x: tree.x + (rng() - 0.5) * 28,
      y: tree.y + 12 + (rng() - 0.5) * 18,
      radius: 14,
    });
  }
}

function collectWoodDrops() {
  world.woodDrops = world.woodDrops.filter((drop) => {
    const keep = Math.hypot(player.x - drop.x, player.y - drop.y) > player.radius + drop.radius;
    if (!keep) {
      player.wood += 1;
    }
    return keep;
  });
}

function shootArrow() {
  const angle = player.facing;
  world.arrows.push({
    x: player.x + Math.cos(angle) * 42,
    y: player.y + Math.sin(angle) * 42 - 4,
    dx: Math.cos(angle) * ARROW_SPEED,
    dy: Math.sin(angle) * ARROW_SPEED,
    angle,
    life: 1.5,
  });
  player.arrows -= 1;
  gameState.prompt = "Arrow fired. Use 1 to swap back to the axe when you need more wood.";
}

function updateArrows(deltaTime) {
  world.arrows = world.arrows.filter((arrow) => {
    arrow.x += arrow.dx * deltaTime;
    arrow.y += arrow.dy * deltaTime;
    arrow.life -= deltaTime;

    if (
      arrow.x < 0 ||
      arrow.y < 0 ||
      arrow.x > WORLD_WIDTH * TILE_SIZE ||
      arrow.y > WORLD_HEIGHT * TILE_SIZE ||
      arrow.life <= 0
    ) {
      return false;
    }

    for (const tree of world.trees) {
      if (tree.health <= 0) {
        continue;
      }
      if (Math.hypot(arrow.x - tree.x, arrow.y - tree.y) <= tree.trunkRadius + 10) {
        return false;
      }
    }

    return true;
  });
}

function tryToggleHouse() {
  if (player.inHouse) {
    player.inHouse = false;
    const door = getHouseDoorWorldPosition();
    player.x = door.x;
    player.y = door.y + 56;
    gameState.prompt = "Back outside. Chop more wood before the night gets darker.";
    return;
  }

  const door = getHouseDoorWorldPosition();
  const distance = Math.hypot(player.x - door.x, player.y - door.y);
  if (distance <= 70) {
    player.inHouse = true;
    player.x = world.insideDoor.x;
    player.y = world.insideDoor.y;
    gameState.prompt = "Inside the house. Press E by the doorway again when you want to go back out.";
  }
}

function updateCamera(deltaTime) {
  const targetX = player.inHouse
    ? HOUSE_WIDTH * 0.5
    : clamp(player.x, window.innerWidth / 2, WORLD_WIDTH * TILE_SIZE - window.innerWidth / 2);
  const targetY = player.inHouse
    ? HOUSE_HEIGHT * 0.5
    : clamp(player.y, window.innerHeight / 2, WORLD_HEIGHT * TILE_SIZE - window.innerHeight / 2);
  const softness = 1 - Math.pow(0.0018, deltaTime);
  camera.x = lerp(camera.x, targetX, softness);
  camera.y = lerp(camera.y, targetY, softness);
}

function worldToScreenX(x) {
  return x - camera.x + window.innerWidth / 2;
}

function worldToScreenY(y) {
  return y - camera.y + window.innerHeight / 2;
}

function isNight() {
  return gameState.time >= 0.58;
}

function getNightAlpha() {
  return smoothstep(0.58, 0.82, gameState.time);
}

function render(elapsedTime) {
  ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

  if (player.inHouse) {
    drawHouseInterior();
    drawPlayer(elapsedTime);
    drawInteriorPrompt();
  } else {
    drawSky();
    drawGround();
    drawHouse();
    drawShadows();
    drawTreeTrunks();
    drawWoodDrops();
    drawArrows();
    drawPlayer(elapsedTime);
    drawTreeCanopies();
    drawOutdoorPrompt();
    drawNightOverlay();
  }
}

function drawSky() {
  const dayMix = getNightAlpha();
  const gradient = ctx.createLinearGradient(0, 0, 0, window.innerHeight);
  gradient.addColorStop(0, dayMix > 0.5 ? "#34567f" : "#d7f4ff");
  gradient.addColorStop(1, dayMix > 0.5 ? "#6b8750" : "#9bd772");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);
}

function drawGround() {
  const startTileX = Math.max(0, Math.floor((camera.x - window.innerWidth / 2) / TILE_SIZE) - 1);
  const endTileX = Math.min(WORLD_WIDTH, Math.ceil((camera.x + window.innerWidth / 2) / TILE_SIZE) + 1);
  const startTileY = Math.max(0, Math.floor((camera.y - window.innerHeight / 2) / TILE_SIZE) - 1);
  const endTileY = Math.min(WORLD_HEIGHT, Math.ceil((camera.y + window.innerHeight / 2) / TILE_SIZE) + 1);
  const sourceTileSize = assets.grass.height;

  for (let y = startTileY; y < endTileY; y += 1) {
    for (let x = startTileX; x < endTileX; x += 1) {
      const variant = world.tiles[y][x];
      const screenX = Math.floor(worldToScreenX(x * TILE_SIZE));
      const screenY = Math.floor(worldToScreenY(y * TILE_SIZE));
      ctx.drawImage(
        assets.grass,
        variant * sourceTileSize,
        0,
        sourceTileSize,
        sourceTileSize,
        screenX,
        screenY,
        TILE_SIZE,
        TILE_SIZE,
      );
    }
  }
}

function drawHouse() {
  const screenX = Math.floor(worldToScreenX(world.house.x - assets.house.width / 2));
  const screenY = Math.floor(worldToScreenY(world.house.y - assets.house.height / 2));
  ctx.drawImage(assets.house, screenX, screenY);
}

function drawHouseInterior() {
  const screenX = Math.floor(worldToScreenX(0));
  const screenY = Math.floor(worldToScreenY(0));
  ctx.drawImage(assets.houseInterior, screenX, screenY);
}

function drawShadowAt(x, y, radiusX, radiusY, skew) {
  const screenX = worldToScreenX(x);
  const screenY = worldToScreenY(y);
  ctx.save();
  ctx.translate(screenX + skew, screenY);
  ctx.rotate(-0.15);
  ctx.fillStyle = "rgba(38, 55, 27, 0.22)";
  ctx.beginPath();
  ctx.ellipse(0, 0, radiusX, radiusY, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawShadows() {
  for (const tree of world.trees) {
    if (tree.health <= 0) {
      continue;
    }
    drawShadowAt(tree.x + 8, tree.y + 16, 22 * tree.shadowScale, 9 * tree.shadowScale, 10);
  }

  drawShadowAt(world.house.x + 20, world.house.y + 92, 90, 22, 18);
  drawShadowAt(player.x + 4, player.y + 22, 18, 8, 10);
}

function drawTreeTrunks() {
  for (const tree of world.trees) {
    if (tree.health <= 0) {
      continue;
    }

    const texture = assets.trees[tree.theme];
    const screenX = Math.floor(worldToScreenX(tree.x - texture.trunk.width / 2));
    const screenY = Math.floor(worldToScreenY(tree.y - texture.trunk.height + 42));
    ctx.drawImage(texture.trunk, screenX, screenY);

    if (tree.health < tree.maxHealth) {
      const ratio = tree.health / tree.maxHealth;
      ctx.fillStyle = "rgba(27, 20, 10, 0.75)";
      ctx.fillRect(screenX + 38, screenY + 84, 48, 6);
      ctx.fillStyle = ratio > 0.45 ? "#6fd55b" : "#f08f51";
      ctx.fillRect(screenX + 39, screenY + 85, 46 * ratio, 4);
    }
  }
}

function drawTreeCanopies() {
  for (const tree of world.trees) {
    if (tree.health <= 0) {
      continue;
    }
    const texture = assets.trees[tree.theme];
    const screenX = Math.floor(worldToScreenX(tree.x - texture.canopy.width / 2));
    const screenY = Math.floor(worldToScreenY(tree.y - texture.canopy.height + 42));
    ctx.drawImage(texture.canopy, screenX, screenY);
  }
}

function drawWoodDrops() {
  for (const drop of world.woodDrops) {
    const x = Math.floor(worldToScreenX(drop.x - assets.icons.wood.width / 2));
    const y = Math.floor(worldToScreenY(drop.y - assets.icons.wood.height / 2));
    ctx.drawImage(assets.icons.wood, x, y);
  }
}

function drawArrows() {
  for (const arrow of world.arrows) {
    ctx.save();
    ctx.translate(worldToScreenX(arrow.x), worldToScreenY(arrow.y));
    ctx.rotate(arrow.angle);
    ctx.drawImage(assets.arrow, -18, -10, 36, 20);
    ctx.restore();
  }
}

function drawPlayer(elapsedTime) {
  const moving = Math.abs(player.moveX) > 0.01 || Math.abs(player.moveY) > 0.01;
  const activeAction = player.action?.type;
  const sprite = activeAction === "bow"
    ? assets.playerBow
    : activeAction === "axe"
      ? assets.playerAxe
      : moving
        ? assets.playerWalk
        : assets.playerIdle;
  const fps = activeAction ? 14 : moving ? 9 : 4;
  const animation = getAnimationFrame(sprite, elapsedTime, fps);
  const bob = moving ? Math.sin(player.bob) * 2 : 0;
  const screenX = Math.floor(worldToScreenX(player.x - player.drawWidth / 2));
  const screenY = Math.floor(worldToScreenY(player.y - player.drawHeight / 2 + bob - 22));

  ctx.save();
  if (Math.cos(player.facing) < -0.15) {
    ctx.translate(screenX + player.drawWidth, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(sprite, animation.sx, 0, animation.frameWidth, animation.frameHeight, 0, screenY, player.drawWidth, player.drawHeight);
  } else {
    ctx.drawImage(sprite, animation.sx, 0, animation.frameWidth, animation.frameHeight, screenX, screenY, player.drawWidth, player.drawHeight);
  }
  ctx.restore();

  drawHeldTool();
}

function drawHeldTool() {
  const icon = assets.icons[player.equipped];
  const pulse = player.action ? Math.sin((1 - player.action.timer / ACTION_DURATION) * Math.PI) : 0.2;
  const distance = player.equipped === "bow" ? 40 : 34 + pulse * 10;
  const handleX = worldToScreenX(player.x + Math.cos(player.facing) * distance);
  const handleY = worldToScreenY(player.y - 8 + Math.sin(player.facing) * distance);

  ctx.save();
  ctx.translate(handleX, handleY);
  ctx.rotate(player.facing + (player.equipped === "bow" ? 0.15 : Math.PI / 2));
  if (player.equipped === "bow") {
    ctx.drawImage(icon, -26, -18, 52, 36);
  } else {
    ctx.drawImage(icon, -18, -30, 36, 60);
  }
  ctx.restore();
}

function drawNightOverlay() {
  const alpha = getNightAlpha();
  if (alpha <= 0.01) {
    return;
  }

  ctx.fillStyle = `rgba(17, 33, 58, ${0.56 * alpha})`;
  ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

  if (player.wood >= 5) {
    const fireX = worldToScreenX(player.x + 84);
    const fireY = worldToScreenY(player.y + 8);
    ctx.drawImage(assets.campfire, fireX - 22, fireY - 20);
  }
}

function drawOutdoorPrompt() {
  const door = getHouseDoorWorldPosition();
  if (Math.hypot(player.x - door.x, player.y - door.y) <= 78) {
    drawPromptBubble(worldToScreenX(door.x), worldToScreenY(door.y - 94), "Press E to enter the house");
  } else if (player.woodDrops && world.woodDrops.length > 0) {
    const drop = world.woodDrops[0];
    drawPromptBubble(worldToScreenX(drop.x), worldToScreenY(drop.y - 34), "Walk over wood to collect it");
  }
}

function drawInteriorPrompt() {
  drawPromptBubble(worldToScreenX(world.insideDoor.x), worldToScreenY(HOUSE_HEIGHT + 8), "Press E at the door to leave");
}

function drawPromptBubble(x, y, text) {
  ctx.save();
  ctx.font = "16px Georgia";
  const width = ctx.measureText(text).width + 24;
  ctx.fillStyle = "rgba(255, 248, 232, 0.94)";
  ctx.strokeStyle = "rgba(91, 70, 32, 0.35)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  roundRect(ctx, x - width / 2, y - 18, width, 30, 10);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#3c2a18";
  ctx.fillText(text, x - width / 2 + 12, y + 2);
  ctx.restore();
}

function roundRect(context, x, y, width, height, radius) {
  context.moveTo(x + radius, y);
  context.lineTo(x + width - radius, y);
  context.quadraticCurveTo(x + width, y, x + width, y + radius);
  context.lineTo(x + width, y + height - radius);
  context.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  context.lineTo(x + radius, y + height);
  context.quadraticCurveTo(x, y + height, x, y + height - radius);
  context.lineTo(x, y + radius);
  context.quadraticCurveTo(x, y, x + radius, y);
}

function updateUi() {
  const tileX = Math.floor(player.x / TILE_SIZE);
  const tileY = Math.floor(player.y / TILE_SIZE);
  const phase = isNight() ? "Night" : "Day";
  const nextCampfireNote = isNight()
    ? player.wood >= 5
      ? "You have enough wood for a campfire once build controls are added."
      : "Collect 5 wood before campfires become available."
    : "Gather wood before night. Campfire building will be added next.";

  inventoryLabel.innerHTML = `Wood: <span>${player.wood}</span> | Arrows: <span>${player.arrows}</span>`;
  toolLabel.innerHTML = `Tool: <span>${player.equipped === "axe" ? "Axe" : "Bow"}</span> | Time: <span>${phase}</span>`;
  statusLabel.textContent = `Tile ${tileX},${tileY} | Trees left ${world.trees.filter((tree) => tree.health > 0).length}`;
  bannerText.textContent = player.inHouse ? "Shelter found. Press E near the doorway to go back outside." : `${gameState.prompt} ${nextCampfireNote}`;
}

let lastTimestamp = 0;

function frame(timestamp) {
  const elapsedSeconds = timestamp / 1000;
  const deltaTime = Math.min(0.033, (timestamp - lastTimestamp) / 1000 || 0.016);
  lastTimestamp = timestamp;

  update(deltaTime);
  render(elapsedSeconds);
  requestAnimationFrame(frame);
}

async function boot() {
  resizeCanvas();
  await loadAssets();
  createWorld();
  requestAnimationFrame(frame);
}

boot().catch((error) => {
  console.error(error);
  statusLabel.textContent = "Failed to start the game.";
});
