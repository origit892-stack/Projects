import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

const canvas = document.querySelector("#game");
const scoreEl = document.querySelector("#score");
const veil = document.querySelector("#veil");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x120c0a);
scene.fog = new THREE.FogExp2(0x1a1412, 0.018);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
renderer.shadowMap.enabled = false;
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.7));

const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 1200);
camera.position.set(0, 5, 10);

const lavaGlow = new THREE.PointLight(0xff5522, 12, 850, 1.15);
lavaGlow.position.set(0, -5, 0);
scene.add(lavaGlow);

const atmosphereLight = new THREE.DirectionalLight(0x9999aa, 0.4);
atmosphereLight.position.set(100, 200, 100);
scene.add(atmosphereLight);
scene.add(new THREE.HemisphereLight(0xa4a0a0, 0xa23b18, 1.05));
scene.add(new THREE.AmbientLight(0x655a52, 0.82));

const templeKey = new THREE.DirectionalLight(0xb8b1a8, 1.35);
templeKey.position.set(0, 38, 58);
scene.add(templeKey);

const playerRim = new THREE.PointLight(0xffb36d, 7.5, 42, 1.55);
scene.add(playerRim);

const clock = new THREE.Clock();
const pillarTargets = [];
const tmpMatrix = new THREE.Matrix4();
const tmpObject = new THREE.Object3D();
const tmpVec = new THREE.Vector3();

const state = {
  index: 0,
  jumping: false,
  falling: false,
  jumpTime: 0,
  from: new THREE.Vector3(),
  to: new THREE.Vector3(),
  miss: false,
  gameOverShown: false,
};

function makeNoiseTexture(size = 256, style = "stone") {
  const c = document.createElement("canvas");
  c.width = size;
  c.height = size;
  const ctx = c.getContext("2d");
  const img = ctx.createImageData(size, size);
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const i = (y * size + x) * 4;
      const grain = Math.random();
      const crack = Math.abs(Math.sin(x * 0.075 + Math.sin(y * 0.04) * 8)) < 0.035 || Math.random() > 0.992;
      let v = style === "normal" ? 128 + (grain - 0.5) * 92 : 128 + grain * 84;
      if (crack) v *= style === "normal" ? 0.55 : 0.18;
      img.data[i] = style === "normal" ? 128 + (v - 128) * 0.7 : v;
      img.data[i + 1] = style === "normal" ? 128 + (Math.random() - 0.5) * 80 : v * 0.92;
      img.data[i + 2] = style === "normal" ? 210 : v * 0.86;
      img.data[i + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  const texture = new THREE.CanvasTexture(c);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(3, 3);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

const basaltMap = makeNoiseTexture(512, "stone");
const basaltNormal = makeNoiseTexture(512, "normal");
const basalt = new THREE.MeshStandardMaterial({
  color: 0x82786d,
  emissive: 0x35150a,
  emissiveIntensity: 0.32,
  roughness: 1,
  metalness: 0,
  map: basaltMap,
  normalMap: basaltNormal,
  normalScale: new THREE.Vector2(1.5, 1.5),
});

const lavaTexture = makeNoiseTexture(512, "stone");
lavaTexture.repeat.set(38, 38);
const lava = new THREE.Mesh(
  new THREE.PlaneGeometry(10000, 10000, 260, 260),
  new THREE.MeshStandardMaterial({
    color: 0x2b0502,
    emissive: 0xff3c13,
    emissiveIntensity: 4,
    roughness: 0.82,
    metalness: 0,
    map: lavaTexture,
  }),
);
lava.rotation.x = -Math.PI / 2;
lava.position.y = -10;
lava.material.onBeforeCompile = (shader) => {
  shader.uniforms.uTime = { value: 0 };
  lava.material.userData.shader = shader;
  shader.vertexShader = shader.vertexShader.replace(
    "#include <common>",
    `#include <common>
    uniform float uTime;
    float wave(vec2 p) {
      return sin(p.x * 0.025 + uTime * 0.55) * cos(p.y * 0.021 - uTime * 0.42);
    }`,
  );
  shader.vertexShader = shader.vertexShader.replace(
    "#include <begin_vertex>",
    `#include <begin_vertex>
    transformed.z += wave(position.xy) * 0.35;`,
  );
};
scene.add(lava);

function buildPillars() {
  const geometry = new THREE.BoxGeometry(8, 1, 8, 8, 1, 8);
  const count = 72;
  const mesh = new THREE.InstancedMesh(geometry, basalt, count - 1);
  mesh.instanceMatrix.setUsage(THREE.StaticDrawUsage);
  scene.add(mesh);

  pillarTargets.push(new THREE.Vector3(0, 0.55, 8));
  for (let i = 1; i < count; i += 1) {
    const previous = pillarTargets[i - 1];
    const drift = Math.sin(i * 1.17) * 2.9 + (Math.random() - 0.5) * 2.3;
    const gap = 12 + Math.random() * 4.5;
    pillarTargets.push(new THREE.Vector3(previous.x + drift, 0.55 + Math.sin(i * 0.45) * 0.7, previous.z - gap));
  }

  for (let i = 0; i < count; i += 1) {
    if (i === 0) continue;
    const p = pillarTargets[i];
    const height = 20 + Math.random() * 15;
    tmpObject.position.set(p.x, p.y - height / 2, p.z);
    tmpObject.rotation.y = Math.random() * Math.PI;
    tmpObject.scale.set(1 + Math.random() * 0.18, height, 1 + Math.random() * 0.18);
    tmpObject.updateMatrix();
    mesh.setMatrixAt(i - 1, tmpObject.matrix);
  }

  return mesh;
}

const pillarMesh = buildPillars();

function makePlatform() {
  const group = new THREE.Group();
  const slab = new THREE.Mesh(new THREE.BoxGeometry(32, 3.2, 28, 10, 2, 10), basalt);
  slab.position.set(0, -1.05, 8);
  group.add(slab);

  for (let i = 0; i < 12; i += 1) {
    const block = new THREE.Mesh(new THREE.BoxGeometry(2.7 + Math.random() * 3, 1.2, 2.2 + Math.random() * 3), basalt);
    block.position.set(-16 + Math.random() * 32, 0.7, -4 + Math.random() * 23);
    block.rotation.y = Math.random() * Math.PI;
    group.add(block);
  }
  scene.add(group);
}
makePlatform();

function buildDistantRuins() {
  const archMat = new THREE.MeshStandardMaterial({ color: 0x201c1a, roughness: 1, metalness: 0, normalMap: basaltNormal });
  const pillarGeo = new THREE.CylinderGeometry(1.4, 1.8, 34, 10);
  const topGeo = new THREE.BoxGeometry(21, 3, 3.6);
  const statueGeo = new THREE.CapsuleGeometry(3.3, 14, 8, 14);
  const chainGeo = new THREE.TorusGeometry(1.1, 0.14, 6, 12);
  const archColumns = new THREE.InstancedMesh(pillarGeo, archMat, 48);
  const archTops = new THREE.InstancedMesh(topGeo, archMat, 24);
  const statues = new THREE.InstancedMesh(statueGeo, archMat, 10);
  const chains = new THREE.InstancedMesh(chainGeo, archMat, 80);

  for (let i = 0; i < 24; i += 1) {
    const z = -90 - i * 30 - Math.random() * 25;
    const side = i % 2 === 0 ? -1 : 1;
    const x = side * (38 + Math.random() * 85);
    const rotY = side * 0.45 + (Math.random() - 0.5) * 0.4;
    const scale = 1.4 + Math.random() * 1.8;

    for (let column = 0; column < 2; column += 1) {
      const localX = column === 0 ? -8 : 8;
      const localY = column === 0 ? 2 : -2 + Math.random() * 3;
      tmpObject.position.set(x + Math.cos(rotY) * localX * scale, -11 + localY * scale, z - Math.sin(rotY) * localX * scale);
      tmpObject.rotation.set(0, rotY, 0);
      tmpObject.scale.setScalar(scale);
      tmpObject.updateMatrix();
      archColumns.setMatrixAt(i * 2 + column, tmpObject.matrix);
    }

    tmpObject.position.set(x, -11 + 19 * scale, z);
    tmpObject.rotation.set(0, rotY, (Math.random() - 0.5) * 0.25);
    tmpObject.scale.setScalar(scale);
    tmpObject.updateMatrix();
    archTops.setMatrixAt(i, tmpObject.matrix);
  }

  for (let i = 0; i < 10; i += 1) {
    tmpObject.position.set((i % 2 ? -1 : 1) * (60 + Math.random() * 135), -7, -130 - i * 58);
    tmpObject.rotation.set(0, Math.PI + (Math.random() - 0.5) * 0.7, 0);
    tmpObject.scale.set(1, 1.8 + Math.random() * 1.5, 0.72);
    tmpObject.updateMatrix();
    statues.setMatrixAt(i, tmpObject.matrix);
  }

  for (let i = 0; i < 80; i += 1) {
    tmpObject.position.set(-70 + (i % 20) * 7.5, 22 - Math.floor(i / 20) * 6, -155 - Math.floor(i / 20) * 88);
    tmpObject.rotation.set(Math.PI / 2, i % 2 ? Math.PI / 2 : 0, 0.2);
    tmpObject.scale.setScalar(1.4);
    tmpObject.updateMatrix();
    chains.setMatrixAt(i, tmpObject.matrix);
  }

  scene.add(archColumns, archTops, statues, chains);
}
buildDistantRuins();

function makeKnight() {
  const group = new THREE.Group();
  const armor = new THREE.MeshStandardMaterial({ color: 0xa6a093, emissive: 0x1b120c, emissiveIntensity: 0.18, roughness: 0.72, metalness: 0.42 });
  const cloth = new THREE.MeshStandardMaterial({ color: 0x5c2119, emissive: 0x1b0704, emissiveIntensity: 0.2, roughness: 0.95, metalness: 0 });
  const leather = new THREE.MeshStandardMaterial({ color: 0x4a2a1c, roughness: 1, metalness: 0 });

  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.35, 0.78, 8, 16), armor);
  body.position.y = 1.08;
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.26, 18, 12), armor);
  head.position.y = 1.78;
  const helm = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.22, 18), armor);
  helm.position.y = 2.02;
  const cape = new THREE.Mesh(new THREE.PlaneGeometry(0.95, 1.25, 5, 5), cloth);
  cape.position.set(0, 1.05, 0.29);
  cape.rotation.x = -0.18;
  const sword = new THREE.Mesh(new THREE.BoxGeometry(0.05, 1.15, 0.05), armor);
  sword.position.set(0.54, 0.95, 0.08);
  sword.rotation.z = -0.45;

  for (const x of [-0.27, 0.27]) {
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.55, 6, 10), leather);
    leg.position.set(x, 0.38, 0);
    group.add(leg);
    const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.08, 0.55, 6, 10), armor);
    arm.position.set(x * 1.75, 1.17, 0.02);
    arm.rotation.z = -x * 1.2;
    group.add(arm);
  }
  group.add(body, head, helm, cape, sword);
  group.position.copy(pillarTargets[0]);
  group.position.y += 0.08;
  group.rotation.y = Math.PI;
  scene.add(group);
  return group;
}

const player = makeKnight();

function makeParticles() {
  const count = 1800;
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  for (let i = 0; i < count; i += 1) {
    positions[i * 3] = (Math.random() - 0.5) * 260;
    positions[i * 3 + 1] = -4 + Math.random() * 40;
    positions[i * 3 + 2] = 35 - Math.random() * 520;
    const ember = Math.random() > 0.72;
    colors[i * 3] = ember ? 1 : 0.45;
    colors[i * 3 + 1] = ember ? 0.28 : 0.34;
    colors[i * 3 + 2] = ember ? 0.08 : 0.31;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  const material = new THREE.PointsMaterial({
    size: 0.075,
    transparent: true,
    opacity: 0.72,
    vertexColors: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const points = new THREE.Points(geometry, material);
  scene.add(points);
  return { points, positions };
}

const particles = makeParticles();

const ChromaticVignetteShader = {
  uniforms: {
    tDiffuse: { value: null },
    resolution: { value: new THREE.Vector2(1, 1) },
    amount: { value: 0.0016 },
    vignette: { value: 0.48 },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform vec2 resolution;
    uniform float amount;
    uniform float vignette;
    varying vec2 vUv;
    void main() {
      vec2 center = vUv - 0.5;
      vec2 offset = center * amount;
      float r = texture2D(tDiffuse, vUv + offset).r;
      float g = texture2D(tDiffuse, vUv).g;
      float b = texture2D(tDiffuse, vUv - offset).b;
      float shade = 1.0 - smoothstep(vignette, 0.92, dot(center, center) * 1.55);
      gl_FragColor = vec4(vec3(r, g, b) * shade, 1.0);
    }
  `,
};

const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(scene, camera);
const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.4, 0.55, 0.58);
const grade = new ShaderPass(ChromaticVignetteShader);
composer.addPass(renderPass);
composer.addPass(bloom);
composer.addPass(grade);

function startJump() {
  if (state.jumping || state.falling || state.index >= pillarTargets.length - 1) return;
  state.jumping = true;
  state.jumpTime = 0;
  state.from.copy(player.position);
  const target = pillarTargets[state.index + 1].clone();
  target.y += 0.08;
  const missChance = state.index > 2 ? 0.08 + Math.min(0.13, state.index * 0.004) : 0;
  state.miss = Math.random() < missChance;
  if (state.miss) target.x += Math.sign(Math.random() - 0.5 || 1) * (5.2 + Math.random() * 2.8);
  state.to.copy(target);
}

function restart() {
  state.index = 0;
  state.jumping = false;
  state.falling = false;
  state.jumpTime = 0;
  state.miss = false;
  state.gameOverShown = false;
  player.position.copy(pillarTargets[0]).add(new THREE.Vector3(0, 0.08, 0));
  veil.classList.remove("visible");
  scoreEl.textContent = "PILLAR 1";
}

window.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    event.preventDefault();
    startJump();
  }
  if (event.code === "KeyR") restart();
});

function updateJump(dt) {
  if (state.jumping) {
    state.jumpTime += dt;
    const p = Math.min(state.jumpTime / 0.7, 1);
    player.position.lerpVectors(state.from, state.to, p);
    player.position.y += Math.sin(p * Math.PI) * 4;
    const dir = tmpVec.subVectors(state.to, state.from);
    player.rotation.y = Math.atan2(dir.x, dir.z);

    if (p >= 1) {
      state.jumping = false;
      if (state.miss) {
        state.falling = true;
      } else {
        state.index += 1;
        scoreEl.textContent = `PILLAR ${state.index + 1}`;
      }
    }
  }

  if (state.falling) {
    player.position.y -= dt * 16;
    player.rotation.x += dt * 2.4;
    if (player.position.y < -7 && !state.gameOverShown) {
      state.gameOverShown = true;
      veil.classList.add("visible");
    }
  }
}

function updateCamera(dt) {
  const follow = player.position.clone().add(new THREE.Vector3(0, 5.35, 13.2));
  camera.position.lerp(follow, 1 - Math.pow(0.002, dt));
  const look = player.position.clone().add(new THREE.Vector3(0, 1.05, -8.5));
  camera.lookAt(look);
}

function animate() {
  const dt = Math.min(clock.getDelta(), 0.033);
  const t = clock.elapsedTime;

  lavaTexture.offset.x = t * 0.015;
  lavaTexture.offset.y = t * -0.009;
  if (lava.material.userData.shader) lava.material.userData.shader.uniforms.uTime.value = t;
  playerRim.position.copy(player.position).add(new THREE.Vector3(0, 2.2, 2.8));

  const pos = particles.positions;
  for (let i = 0; i < pos.length / 3; i += 1) {
    pos[i * 3 + 1] += dt * (0.35 + (i % 7) * 0.035);
    pos[i * 3] += Math.sin(t * 0.4 + i) * dt * 0.12;
    if (pos[i * 3 + 1] > 38) {
      pos[i * 3 + 1] = -5;
      pos[i * 3 + 2] = player.position.z + 40 - Math.random() * 520;
    }
  }
  particles.points.geometry.attributes.position.needsUpdate = true;

  updateJump(dt);
  updateCamera(dt);
  composer.render();
  requestAnimationFrame(animate);
}

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setSize(w, h, false);
  composer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  grade.uniforms.resolution.value.set(w, h);
}

window.addEventListener("resize", resize);
resize();
animate();
