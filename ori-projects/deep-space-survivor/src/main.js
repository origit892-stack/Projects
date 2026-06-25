import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js";
import { EffectComposer } from "https://unpkg.com/three@0.165.0/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "https://unpkg.com/three@0.165.0/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "https://unpkg.com/three@0.165.0/examples/jsm/postprocessing/UnrealBloomPass.js";
import { Environment } from "./environment.js";
import { Starfighter } from "./ship.js";
import { AsteroidField } from "./asteroids.js";

const canvas = document.querySelector("#game-canvas");
const scoreEl = document.querySelector("#score");
const hullEl = document.querySelector("#hull");
const waveEl = document.querySelector("#wave");
const startPanel = document.querySelector("#start-panel");
const startButton = document.querySelector("#start-button");

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: "high-performance"
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = false;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.18;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(68, window.innerWidth / window.innerHeight, 0.1, 1800);
camera.position.set(0, 5.6, 13);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.88, 0.52, 0.08);
composer.addPass(bloom);

const environment = new Environment(scene);
environment.init();

const ship = new Starfighter(scene);
const asteroidField = new AsteroidField(scene, environment.stoneTexture);
asteroidField.seedInitialField();

const cameraFill = new THREE.PointLight(0x9ed9ff, 72, 90, 2);
const engineGlow = new THREE.PointLight(0x2ab8ff, 45, 34, 2);
scene.add(cameraFill, engineGlow);

const clock = new THREE.Clock();
const input = {
  left: false,
  right: false,
  up: false,
  down: false,
  firing: false,
  x: 0,
  y: 0,
  moving: false
};

const state = {
  started: false,
  score: 0,
  hull: 100,
  elapsed: 0,
  shake: 0
};

function setKey(code, pressed) {
  if (code === "KeyA" || code === "ArrowLeft") input.left = pressed;
  if (code === "KeyD" || code === "ArrowRight") input.right = pressed;
  if (code === "KeyW" || code === "ArrowUp") input.up = pressed;
  if (code === "KeyS" || code === "ArrowDown") input.down = pressed;
}

window.addEventListener("keydown", (event) => setKey(event.code, true));
window.addEventListener("keyup", (event) => setKey(event.code, false));
window.addEventListener("pointerdown", () => {
  input.firing = true;
});
window.addEventListener("pointerup", () => {
  input.firing = false;
});
window.addEventListener("blur", () => {
  input.firing = false;
  input.left = false;
  input.right = false;
  input.up = false;
  input.down = false;
});

startButton.addEventListener("click", () => {
  state.started = true;
  startPanel.classList.add("hidden");
  canvas.focus();
});

if (new URLSearchParams(window.location.search).get("autostart") === "1") {
  state.started = true;
  startPanel.classList.add("hidden");
}

function updateInput() {
  input.x = Number(input.right) - Number(input.left);
  input.y = Number(input.up) - Number(input.down);
  if (input.x !== 0 && input.y !== 0) {
    input.x *= Math.SQRT1_2;
    input.y *= Math.SQRT1_2;
  }
  input.moving = input.x !== 0 || input.y !== 0;
}

function updateCamera(delta) {
  const cameraTarget = ship.group.position.clone().add(new THREE.Vector3(0, 4.8, 12.5));
  camera.position.lerp(cameraTarget, 1 - Math.pow(0.0008, delta));
  const lookAt = ship.group.position.clone().add(new THREE.Vector3(0, 0.6, -24));
  cameraFill.position.copy(camera.position).add(new THREE.Vector3(0, 2, -4));
  engineGlow.position.copy(ship.group.position).add(new THREE.Vector3(0, -0.2, 2.2));

  if (state.shake > 0) {
    camera.position.x += THREE.MathUtils.randFloatSpread(state.shake);
    camera.position.y += THREE.MathUtils.randFloatSpread(state.shake);
    state.shake = Math.max(0, state.shake - delta * 5.5);
  }

  camera.lookAt(lookAt);
}

function updateHUD() {
  scoreEl.textContent = state.score.toLocaleString("en-US");
  hullEl.textContent = `${Math.max(0, Math.round(state.hull))}%`;
  waveEl.textContent = String(asteroidField.wave);
}

function gameOver() {
  state.started = false;
  startPanel.classList.remove("hidden");
  startPanel.querySelector("h1").textContent = "Signal Lost";
  startPanel.querySelector("p").textContent = `Final score ${state.score.toLocaleString("en-US")}. Launch again to survive deeper.`;
  startButton.textContent = "Relaunch";
  state.score = 0;
  state.hull = 100;
  ship.group.position.set(0, 0, 0);
}

function tick() {
  requestAnimationFrame(tick);
  const delta = Math.min(clock.getDelta(), 0.033);
  state.elapsed += delta;

  updateInput();
  environment.update(delta, state.elapsed);

  if (state.started) {
    ship.update(delta, input, camera);
    asteroidField.update(delta, ship.group.position);
    asteroidField.checkLaserHits(
      ship.lasers,
      (laser) => ship.removeLaser(laser),
      (points) => {
        state.score += points;
        state.shake = Math.min(1.1, state.shake + 0.24);
      },
      (repair) => {
        state.hull = Math.min(100, state.hull + repair);
        state.shake = Math.min(0.8, state.shake + 0.18);
      }
    );

    const damage = asteroidField.checkShipCollision(ship.group.position);
    if (damage > 0) {
      ship.triggerShieldImpact();
      state.hull -= damage;
      state.shake = 1.35;
      if (state.hull <= 0) gameOver();
    }
  } else {
    ship.group.rotation.y = Math.sin(state.elapsed * 0.7) * 0.08;
    ship.group.rotation.z = Math.sin(state.elapsed * 0.9) * 0.04;
    asteroidField.update(delta, ship.group.position);
  }

  updateCamera(delta);
  updateHUD();
  composer.render();
}

window.addEventListener("resize", () => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
  composer.setSize(width, height);
  bloom.setSize(width, height);
});

tick();
