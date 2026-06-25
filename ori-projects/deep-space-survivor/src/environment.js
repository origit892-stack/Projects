import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js";

function makeCanvasTexture(draw, size = 512) {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  draw(ctx, size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.anisotropy = 4;
  return texture;
}

export function createStoneTexture() {
  return makeCanvasTexture((ctx, size) => {
    const base = ctx.createLinearGradient(0, 0, size, size);
    base.addColorStop(0, "#35342f");
    base.addColorStop(0.45, "#171815");
    base.addColorStop(1, "#595347");
    ctx.fillStyle = base;
    ctx.fillRect(0, 0, size, size);

    for (let i = 0; i < 6800; i += 1) {
      const shade = Math.floor(35 + Math.random() * 95);
      ctx.fillStyle = `rgba(${shade}, ${shade - 4}, ${shade - 12}, ${Math.random() * 0.18})`;
      ctx.fillRect(Math.random() * size, Math.random() * size, 1 + Math.random() * 3, 1 + Math.random() * 3);
    }

    for (let i = 0; i < 95; i += 1) {
      ctx.strokeStyle = `rgba(0, 0, 0, ${0.16 + Math.random() * 0.2})`;
      ctx.lineWidth = 1 + Math.random() * 3;
      ctx.beginPath();
      ctx.moveTo(Math.random() * size, Math.random() * size);
      for (let p = 0; p < 7; p += 1) {
        ctx.lineTo(Math.random() * size, Math.random() * size);
      }
      ctx.stroke();
    }
  });
}

function createGasGiantTexture() {
  return makeCanvasTexture((ctx, size) => {
    const g = ctx.createLinearGradient(0, 0, size, 0);
    g.addColorStop(0, "#2f1b17");
    g.addColorStop(0.2, "#8c5134");
    g.addColorStop(0.42, "#d8ae74");
    g.addColorStop(0.6, "#69513d");
    g.addColorStop(0.82, "#b57a45");
    g.addColorStop(1, "#241513");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, size, size);

    for (let y = 0; y < size; y += 12) {
      const alpha = 0.08 + Math.random() * 0.12;
      ctx.fillStyle = y % 36 === 0 ? `rgba(255, 226, 168, ${alpha})` : `rgba(42, 18, 18, ${alpha})`;
      ctx.fillRect(0, y + Math.sin(y * 0.08) * 6, size, 4 + Math.random() * 14);
    }
  }, 1024);
}

function createNebulaTexture() {
  return makeCanvasTexture((ctx, size) => {
    ctx.clearRect(0, 0, size, size);
    const colors = [
      "rgba(32, 118, 255, 0.34)",
      "rgba(121, 62, 226, 0.3)",
      "rgba(255, 188, 73, 0.22)",
      "rgba(15, 49, 119, 0.28)"
    ];
    for (let i = 0; i < 120; i += 1) {
      const sweep = i / 120;
      const x = size * (0.12 + sweep * 0.74 + Math.sin(sweep * Math.PI * 6) * 0.08);
      const y = size * (0.28 + Math.sin(sweep * Math.PI * 3.2) * 0.22 + Math.random() * 0.22);
      const r = size * (0.055 + Math.random() * 0.2);
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, r);
      gradient.addColorStop(0, colors[i % colors.length]);
      gradient.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
  }, 1024);
}

function createRingTexture() {
  return makeCanvasTexture((ctx, size) => {
    ctx.clearRect(0, 0, size, size);
    const center = size / 2;
    for (let y = 0; y < size; y += 1) {
      const distance = Math.abs(y - center) / center;
      const band = Math.sin(distance * 70) * 0.5 + 0.5;
      const dust = Math.random() * 0.18;
      const alpha = Math.max(0, 1 - distance * 1.35) * (0.28 + band * 0.34 + dust);
      ctx.fillStyle = `rgba(255, 219, 166, ${alpha})`;
      ctx.fillRect(0, y, size, 1);
    }
  }, 1024);
}

function createStarField(count, radius, color, size, depthBias = 0) {
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const c = new THREE.Color();

  for (let i = 0; i < count; i += 1) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(THREE.MathUtils.randFloatSpread(2));
    const r = radius * (0.52 + depthBias + Math.random() * 0.32);
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.cos(phi);
    positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
    c.set(color).offsetHSL(THREE.MathUtils.randFloatSpread(0.04), 0, THREE.MathUtils.randFloatSpread(0.18));
    colors.set([c.r, c.g, c.b], i * 3);
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  return new THREE.Points(
    geometry,
    new THREE.PointsMaterial({
      size,
      vertexColors: true,
      transparent: true,
      opacity: 0.78,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    })
  );
}

export class Environment {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.nebulaLayers = [];
    this.starLayers = [];
    this.scene.add(this.group);
    this.stoneTexture = createStoneTexture();
  }

  init() {
    this.scene.background = new THREE.Color(0x030712);
    this.scene.fog = new THREE.FogExp2(0x071128, 0.0022);

    const nebulaTint = new THREE.AmbientLight(0x6677b8, 1.55);
    this.scene.add(nebulaTint);

    const sun = new THREE.DirectionalLight(0xffd49a, 3.1);
    sun.position.set(0.72, 0.36, 0.58).normalize();
    this.scene.add(sun);

    const rimLight = new THREE.DirectionalLight(0x6da9ff, 1.2);
    rimLight.position.set(-0.7, -0.15, 0.45).normalize();
    this.scene.add(rimLight);

    const farStars = createStarField(5200, 1800, 0xffffff, 1.05, 0.34);
    const midStars = createStarField(2400, 1100, 0xdbeaff, 1.35, 0.12);
    const goldStars = createStarField(900, 760, 0xffdeb3, 1.65, 0.04);
    this.starLayers.push(farStars, midStars, goldStars);
    this.group.add(farStars, midStars, goldStars);
    this.createGasGiant();
    this.createNebula();
    this.createDistantDust();
  }

  createGasGiant() {
    const planet = new THREE.Mesh(
      new THREE.SphereGeometry(150, 28, 18),
      new THREE.MeshStandardMaterial({
        map: createGasGiantTexture(),
        roughness: 0.9,
        metalness: 0,
        emissive: new THREE.Color(0x5a2a17),
        emissiveIntensity: 0.48
      })
    );
    planet.position.set(440, 62, -780);
    planet.rotation.set(0.18, -0.38, 0.05);
    planet.frustumCulled = true;
    this.group.add(planet);

    const rings = new THREE.Mesh(
      new THREE.RingGeometry(190, 345, 128),
      new THREE.MeshBasicMaterial({
        map: createRingTexture(),
        color: 0xffd69b,
        transparent: true,
        opacity: 0.9,
        side: THREE.DoubleSide,
        depthWrite: false
      })
    );
    rings.position.copy(planet.position);
    rings.rotation.set(0.48, 0.12, -0.38);
    rings.frustumCulled = true;
    this.group.add(rings);

    const torusMaterial = new THREE.MeshBasicMaterial({
      color: 0xffd69b,
      transparent: true,
      opacity: 0.72,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    for (const radius of [215, 258, 316]) {
      const band = new THREE.Mesh(new THREE.TorusGeometry(radius, radius === 258 ? 3.6 : 2.2, 8, 192), torusMaterial.clone());
      band.position.copy(planet.position);
      band.rotation.copy(rings.rotation);
      band.frustumCulled = true;
      this.group.add(band);
    }
  }

  createNebula() {
    const nebulaTexture = createNebulaTexture();
    for (let i = 0; i < 5; i += 1) {
      const layer = new THREE.Mesh(
        new THREE.PlaneGeometry(820 + i * 115, 530 + i * 76, 1, 1),
        new THREE.MeshBasicMaterial({
          map: nebulaTexture,
          transparent: true,
          opacity: 0.42 - i * 0.045,
          blending: THREE.AdditiveBlending,
          depthWrite: false
        })
      );
      layer.position.set(-430 - i * 28, 80 + i * 18, -650 - i * 72);
      layer.rotation.set(0.03, 0.38, -0.28 + i * 0.13);
      this.nebulaLayers.push(layer);
      this.group.add(layer);
    }

    const accentColors = [0x8d58ff, 0xffc56f];
    for (let i = 0; i < 2; i += 1) {
      const accent = new THREE.Mesh(
        new THREE.PlaneGeometry(640 + i * 180, 390 + i * 90, 1, 1),
        new THREE.MeshBasicMaterial({
          map: nebulaTexture,
          color: accentColors[i],
          transparent: true,
          opacity: 0.28,
          blending: THREE.AdditiveBlending,
          depthWrite: false
        })
      );
      accent.position.set(20 + i * 270, 110 - i * 42, -940 - i * 70);
      accent.rotation.set(-0.04, -0.22, 0.42 - i * 0.58);
      this.nebulaLayers.push(accent);
      this.group.add(accent);
    }
  }

  createDistantDust() {
    const dust = createStarField(900, 420, 0x4da9ff, 2.5);
    dust.material.opacity = 0.2;
    dust.position.z = -220;
    this.group.add(dust);
  }

  update(delta, elapsed) {
    this.nebulaLayers.forEach((layer, index) => {
      layer.material.opacity = 0.38 + Math.sin(elapsed * 0.22 + index) * 0.065;
      layer.rotation.z += delta * (0.004 + index * 0.002);
    });
    this.starLayers.forEach((layer, index) => {
      layer.material.opacity = 0.58 + Math.sin(elapsed * (0.7 + index * 0.23) + index * 1.7) * 0.22;
      layer.rotation.y += delta * (0.0015 + index * 0.0007);
    });
  }
}
