import * as THREE from "./vendor/three.module.js";

const DEG = Math.PI / 180;

function canvasTexture(draw, width = 512, height = 256) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  draw(context, width, height);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

function makeGrimeTexture(base = "#4a504b", fleck = "#171b19", size = 512) {
  const texture = canvasTexture((ctx, width, height) => {
    ctx.fillStyle = base;
    ctx.fillRect(0, 0, width, height);
    for (let i = 0; i < 1500; i += 1) {
      const alpha = 0.015 + Math.random() * 0.11;
      ctx.fillStyle = `${fleck}${Math.floor(alpha * 255).toString(16).padStart(2, "0")}`;
      const radius = Math.random() * 5 + 0.2;
      ctx.beginPath();
      ctx.arc(Math.random() * width, Math.random() * height, radius, 0, Math.PI * 2);
      ctx.fill();
    }
    for (let i = 0; i < 28; i += 1) {
      const x = Math.random() * width;
      const gradient = ctx.createLinearGradient(x, 0, x + Math.random() * 20 - 10, height);
      gradient.addColorStop(0, "rgba(0,0,0,0)");
      gradient.addColorStop(0.25, "rgba(10,13,12,.10)");
      gradient.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = gradient;
      ctx.fillRect(x, 0, 3 + Math.random() * 13, height);
    }
    ctx.strokeStyle = "rgba(230,225,210,.04)";
    for (let i = 0; i < 18; i += 1) {
      ctx.beginPath();
      ctx.moveTo(Math.random() * width, Math.random() * height);
      ctx.lineTo(Math.random() * width, Math.random() * height);
      ctx.stroke();
    }
  }, size, size);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(2.2, 3.5);
  return texture;
}

function makeTextTexture({
  title,
  subtitle = "",
  footer = "",
  background = "#101713",
  color = "#9ed8ad",
  accent = "#5e8f6d",
  border = true,
  width = 768,
  height = 256,
}) {
  return canvasTexture((ctx, w, h) => {
    ctx.fillStyle = background;
    ctx.fillRect(0, 0, w, h);
    const gradient = ctx.createLinearGradient(0, 0, w, h);
    gradient.addColorStop(0, "rgba(255,255,255,.045)");
    gradient.addColorStop(0.5, "rgba(255,255,255,0)");
    gradient.addColorStop(1, "rgba(0,0,0,.24)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, w, h);

    if (border) {
      ctx.strokeStyle = accent;
      ctx.lineWidth = 5;
      ctx.strokeRect(12, 12, w - 24, h - 24);
      ctx.strokeStyle = `${accent}66`;
      ctx.lineWidth = 1;
      for (let x = 28; x < w; x += 34) {
        ctx.beginPath();
        ctx.moveTo(x, 22);
        ctx.lineTo(x, h - 22);
        ctx.stroke();
      }
    }

    ctx.direction = "rtl";
    ctx.textAlign = "center";
    ctx.fillStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 12;
    ctx.font = `700 ${Math.round(h * 0.25)}px Assistant, Arial`;
    ctx.fillText(title, w / 2, h * 0.43);
    ctx.shadowBlur = 5;
    ctx.fillStyle = `${color}cc`;
    ctx.font = `500 ${Math.round(h * 0.105)}px Assistant, Arial`;
    ctx.fillText(subtitle, w / 2, h * 0.63);
    ctx.shadowBlur = 0;
    ctx.fillStyle = `${color}88`;
    ctx.font = `500 ${Math.round(h * 0.065)}px monospace`;
    ctx.fillText(footer, w / 2, h * 0.82);
  }, width, height);
}

function makeWarningTexture() {
  return canvasTexture((ctx, width, height) => {
    ctx.fillStyle = "#351714";
    ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = "#bd3e34";
    ctx.lineWidth = 10;
    ctx.strokeRect(10, 10, width - 20, height - 20);
    ctx.direction = "rtl";
    ctx.textAlign = "center";
    ctx.fillStyle = "#f0d5c3";
    ctx.font = "700 42px Assistant, Arial";
    ctx.fillText("חירום", width / 2, 64);
    ctx.fillStyle = "#d7b5a4";
    ctx.font = "600 21px Assistant, Arial";
    ctx.fillText("במקרה של חריגה בלבד", width / 2, 112);
    ctx.fillText("משכו בידית בחוזקה", width / 2, 144);
    ctx.fillStyle = "#a97c70";
    ctx.font = "500 15px Assistant, Arial";
    ctx.fillText("אין למשוך בזמן נסיעה", width / 2, 181);
    ctx.fillStyle = "#d34c3e";
    ctx.fillRect(36, 202, width - 72, 5);
    ctx.font = "12px monospace";
    ctx.fillText("EMERGENCY SYSTEM · 13-A", width / 2, 232);
  }, 512, 256);
}

function meshBox(width, height, depth, material, position, parent, name = "") {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
  mesh.position.set(...position);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.name = name;
  parent.add(mesh);
  return mesh;
}

function panel(width, height, texture, position, parent, options = {}) {
  const material = new THREE.MeshBasicMaterial({
    map: texture,
    transparent: options.transparent ?? false,
    opacity: options.opacity ?? 1,
    side: THREE.DoubleSide,
    depthWrite: options.depthWrite ?? true,
    blending: options.blending ?? THREE.NormalBlending,
  });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, height), material);
  mesh.position.set(...position);
  if (options.rotation) mesh.rotation.set(...options.rotation);
  parent.add(mesh);
  return mesh;
}

function addAction(object, action) {
  object.traverse((child) => {
    if (child.isMesh) child.userData.action = action;
  });
}

export class TrainScene3D {
  constructor(canvas) {
    this.canvas = canvas;
    this.container = canvas.parentElement;
    this.clock = new THREE.Clock();
    this.pointer = new THREE.Vector2(2, 2);
    this.targetLook = new THREE.Vector2();
    this.currentLook = new THREE.Vector2();
    this.raycaster = new THREE.Raycaster();
    this.clickables = [];
    this.objects = {};
    this.flickerMode = false;
    this.doorAmount = 0;
    this.leverAmount = 0;
    this.shakeAmount = 0;
    this.onDecision = null;
    this.disposed = false;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x050707);
    this.scene.fog = new THREE.FogExp2(0x070908, 0.016);

    this.camera = new THREE.PerspectiveCamera(58, 1, 0.1, 70);
    this.camera.position.set(0, 2.05, 4.4);
    this.camera.lookAt(0, 2.05, -10);

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: "high-performance" });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.34;

    this.buildMaterials();
    this.buildCarriage();
    this.buildLights();
    this.buildInteractives();
    this.buildAnomalyObjects();
    this.bindEvents();
    this.resize();
    this.renderer.setAnimationLoop(() => this.render());
  }

  buildMaterials() {
    const metalMap = makeGrimeTexture("#4a504c", "#101412");
    const floorMap = makeGrimeTexture("#2a2e2b", "#070908");
    const leatherMap = makeGrimeTexture("#4d3c2d", "#160f0a", 256);
    const greenMap = makeGrimeTexture("#28443a", "#0b1c17", 256);

    this.materials = {
      metal: new THREE.MeshStandardMaterial({ map: metalMap, color: 0xb7bbb5, metalness: 0.72, roughness: 0.68 }),
      darkMetal: new THREE.MeshStandardMaterial({ color: 0x181d1b, metalness: 0.86, roughness: 0.48 }),
      edge: new THREE.MeshStandardMaterial({ color: 0x090b0a, metalness: 0.9, roughness: 0.34 }),
      floor: new THREE.MeshStandardMaterial({ map: floorMap, color: 0x9a9c96, metalness: 0.27, roughness: 0.92 }),
      seat: new THREE.MeshStandardMaterial({ map: greenMap, color: 0x78a08c, roughness: 0.86, metalness: 0.08 }),
      leather: new THREE.MeshStandardMaterial({ map: leatherMap, color: 0xb58b65, roughness: 0.82, metalness: 0.04 }),
      brass: new THREE.MeshStandardMaterial({ color: 0x8a7244, metalness: 0.88, roughness: 0.34 }),
      glass: new THREE.MeshPhysicalMaterial({ color: 0x263633, metalness: 0.08, roughness: 0.18, transmission: 0.15, transparent: true, opacity: 0.56 }),
      blackGlass: new THREE.MeshStandardMaterial({ color: 0x020404, metalness: 0.25, roughness: 0.16 }),
      red: new THREE.MeshStandardMaterial({ color: 0x8d211c, emissive: 0x5c0b08, emissiveIntensity: 0.65, metalness: 0.56, roughness: 0.42 }),
      rubber: new THREE.MeshStandardMaterial({ color: 0x090b0a, roughness: 0.95 }),
      pale: new THREE.MeshStandardMaterial({ color: 0xc5bbaa, roughness: 0.94 }),
    };
  }

  buildCarriage() {
    const root = new THREE.Group();
    root.name = "NightTrainCabin";
    this.scene.add(root);
    this.root = root;

    meshBox(10, 0.18, 29, this.materials.floor, [0, -0.08, -3], root, "worn-floor");
    meshBox(10, 0.18, 29, this.materials.metal, [0, 5.5, -3], root, "ceiling");
    meshBox(0.18, 5.6, 29, this.materials.metal, [-5, 2.7, -3], root, "left-wall");
    meshBox(0.18, 5.6, 29, this.materials.metal, [5, 2.7, -3], root, "right-wall");
    meshBox(10, 5.6, 0.26, this.materials.metal, [0, 2.7, -13.25], root, "end-wall");

    for (let z = 9; z > -13; z -= 2.1) {
      const seam = meshBox(9.85, 0.015, 0.035, this.materials.edge, [0, 0.025, z], root);
      seam.receiveShadow = false;
    }

    this.buildWindows(root);
    this.buildSeats(root);
    this.buildDoorMechanism(root);
    this.buildDetails(root);
  }

  buildWindows(root) {
    this.outsideStreaks = [];
    const windowZ = [2.3, -3.1, -8.2];
    for (const side of [-1, 1]) {
      for (const z of windowZ) {
        meshBox(0.22, 2.55, 3.9, this.materials.edge, [side * 4.91, 3.05, z], root);
        const glass = meshBox(0.13, 2.18, 3.52, this.materials.blackGlass, [side * 4.79, 3.05, z], root, "dirty-window");

        for (let i = 0; i < 5; i += 1) {
          const streakMat = new THREE.MeshBasicMaterial({
            color: i % 2 ? 0xb0996c : 0x6d806f,
            transparent: true,
            opacity: 0.08 + Math.random() * 0.18,
          });
          const streak = meshBox(0.035, 0.018, 0.65 + Math.random() * 1.4, streakMat, [side * 4.7, 2.4 + Math.random() * 1.7, z + Math.random() * 2.8 - 1.4], root);
          this.outsideStreaks.push({ mesh: streak, side, speed: 6 + Math.random() * 10 });
        }

        for (let drip = 0; drip < 9; drip += 1) {
          const line = meshBox(0.015, 0.2 + Math.random() * 0.65, 0.018, this.materials.glass, [side * 4.68, 2.3 + Math.random() * 1.5, z + Math.random() * 2.9 - 1.45], root);
          line.rotation.z = (Math.random() - 0.5) * 4 * DEG;
        }
        glass.material = this.materials.blackGlass;
      }
    }
  }

  buildSeats(root) {
    for (const side of [-1, 1]) {
      for (let z = 5; z > -11; z -= 2.4) {
        const seat = new THREE.Group();
        seat.position.set(side * 4.15, 0.2, z);
        root.add(seat);
        const cushion = meshBox(1.45, 0.38, 1.8, this.materials.seat, [0, 0.45, 0], seat);
        cushion.rotation.z = side * -2 * DEG;
        const back = meshBox(0.36, 1.55, 1.8, this.materials.seat, [side * 0.54, 1.18, 0], seat);
        back.rotation.z = side * -7 * DEG;
        for (const y of [0.68, 1.05, 1.42]) {
          meshBox(0.38, 0.025, 1.6, this.materials.edge, [side * 0.35, y, 0], seat).material = new THREE.MeshStandardMaterial({ color: 0x16231e, roughness: 0.9 });
        }
      }
    }

    for (const side of [-1, 1]) {
      for (const z of [4.2, -2.3, -8.4]) {
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 5.2, 12), this.materials.brass);
        pole.position.set(side * 3.05, 2.6, z);
        pole.castShadow = true;
        root.add(pole);
        const ring = new THREE.Mesh(new THREE.TorusGeometry(0.29, 0.025, 8, 20), this.materials.brass);
        ring.position.set(side * 3.05, 4.6, z);
        ring.rotation.y = 90 * DEG;
        root.add(ring);
      }
    }
  }

  buildDoorMechanism(root) {
    const frame = new THREE.Group();
    frame.position.set(0, 0, -12.95);
    root.add(frame);
    meshBox(5.25, 5.1, 0.3, this.materials.edge, [0, 2.55, 0], frame);
    meshBox(4.75, 4.72, 0.36, this.materials.blackGlass, [0, 2.36, 0.06], frame);

    const doorMaterial = this.materials.metal.clone();
    doorMaterial.roughness = 0.52;
    this.objects.leftDoor = meshBox(2.28, 4.58, 0.28, doorMaterial, [-1.17, 2.29, 0.27], frame, "door-left");
    this.objects.rightDoor = meshBox(2.28, 4.58, 0.28, doorMaterial, [1.17, 2.29, 0.27], frame, "door-right");
    this.objects.leftDoor.userData.closedX = -1.17;
    this.objects.rightDoor.userData.closedX = 1.17;

    for (const door of [this.objects.leftDoor, this.objects.rightDoor]) {
      for (let y = 0.35; y < 4.2; y += 0.6) {
        meshBox(2.05, 0.022, 0.035, this.materials.edge, [0, y - 2.29, 0.17], door);
      }
    }

    const gearWindowMaterial = new THREE.MeshStandardMaterial({ color: 0x111514, metalness: 0.8, roughness: 0.25 });
    for (const x of [-1.15, 1.15]) {
      meshBox(1.42, 1.44, 0.14, this.materials.edge, [x, 3.05, 0.49], frame);
      meshBox(1.18, 1.19, 0.11, gearWindowMaterial, [x, 3.05, 0.57], frame);
    }

    this.objects.gears = [];
    for (const [x, y, radius] of [[-1.18, 3.05, 0.39], [1.12, 3.05, 0.42], [0, 3.18, 0.25]]) {
      const gear = new THREE.Mesh(new THREE.TorusGeometry(radius, 0.095, 8, 18), this.materials.brass);
      gear.position.set(x, y, 0.67);
      frame.add(gear);
      for (let tooth = 0; tooth < 12; tooth += 1) {
        const angle = (tooth / 12) * Math.PI * 2;
        const cube = meshBox(0.11, 0.19, 0.08, this.materials.brass, [x + Math.cos(angle) * radius, y + Math.sin(angle) * radius, 0.68], frame);
        cube.rotation.z = angle;
      }
      this.objects.gears.push(gear);
    }

    for (const x of [-2.25, 2.25]) {
      for (const y of [0.25, 1.2, 2.1, 3, 4.25]) {
        const bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.06, 10), this.materials.brass);
        bolt.rotation.x = 90 * DEG;
        bolt.position.set(x, y, 0.5);
        frame.add(bolt);
      }
    }
    addAction(this.objects.leftDoor, "door");
    addAction(this.objects.rightDoor, "door");
    this.clickables.push(this.objects.leftDoor, this.objects.rightDoor);
  }

  buildDetails(root) {
    const vfdTexture = makeTextTexture({ title: "התחנה הבאה · אין מידע", subtitle: "נא להישאר בקרון", footer: "NIGHT SERVICE / LINE 13", background: "#07130c", color: "#80c48c" });
    this.objects.vfd = panel(5.8, 1.22, vfdTexture, [0, 4.65, -12.72], root);
    meshBox(6.15, 1.5, 0.28, this.materials.edge, [0, 4.65, -12.88], root);
    this.objects.vfd.position.z = -12.69;

    const hologramTexture = makeTextTexture({
      title: "האם הכל תקין?",
      subtitle: "סריקת חריגות בתהליך...",
      footer: "CAR_SCAN 01 · MOTION 00.4 · TEMP 16.3° · SIGNAL LOST",
      background: "rgba(3,18,18,.82)",
      color: "#8bd5c4",
      accent: "#477c74",
    });
    this.objects.hologram = panel(5.2, 1.72, hologramTexture, [0, 3.15, -10.8], root, {
      transparent: true,
      opacity: 0.82,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    this.objects.hologram.renderOrder = 3;

    const clockTexture = makeTextTexture({ title: "00:13", footer: "SYSTEM TIME", background: "#080606", color: "#e54c42", accent: "#5c1814", width: 384, height: 180 });
    this.objects.clock = panel(1.28, 0.6, clockTexture, [-3.72, 4.4, -12.66], root);

    const numberTexture = makeTextTexture({ title: "13", subtitle: "NIGHT LINE", background: "#160a09", color: "#df4b40", accent: "#7d211c", width: 320, height: 320 });
    this.objects.number = panel(1.02, 1.02, numberTexture, [-4.12, 4.55, -12.62], root);

    const routeTexture = makeTextTexture({ title: "מרכז  •  הגשר  •  הביתה", subtitle: "הנקודה האדומה מציינת את מיקומכם", footer: "ROUTE 13 / DO NOT LEAVE BETWEEN STATIONS", background: "#d0cbbd", color: "#6f2722", accent: "#8f3a32" });
    this.objects.route = panel(3.6, 1.15, routeTexture, [4.84, 3.7, -3.6], root, { rotation: [0, -90 * DEG, 0] });

    const posterTexture = makeTextTexture({ title: "אל תירדמו.", subtitle: "הדרך הבטוחה הביתה", footer: "METRO NIGHT AUTHORITY", background: "#c7c0ac", color: "#45251f", accent: "#9e4138" });
    this.objects.poster = panel(3.3, 1.35, posterTexture, [-4.84, 3.75, -3.3], root, { rotation: [0, 90 * DEG, 0] });

    this.buildSuitcase(root);
    this.buildIntercom(root);
  }

  buildSuitcase(root) {
    const suitcase = new THREE.Group();
    suitcase.position.set(3.25, 0.72, -5.9);
    suitcase.scale.setScalar(1.12);
    suitcase.rotation.y = -8 * DEG;
    root.add(suitcase);
    meshBox(1.2, 1.25, 0.48, this.materials.leather, [0, 0, 0], suitcase);
    meshBox(1.13, 0.045, 0.5, this.materials.brass, [0, 0.23, 0], suitcase);
    for (const x of [-0.5, 0.5]) meshBox(0.07, 1.12, 0.52, this.materials.brass, [x, 0, 0], suitcase);
    const handle = new THREE.Mesh(new THREE.TorusGeometry(0.27, 0.045, 8, 18, Math.PI), this.materials.leather);
    handle.position.set(0, 0.7, 0);
    handle.rotation.z = Math.PI;
    suitcase.add(handle);
    this.objects.suitcase = suitcase;
  }

  buildIntercom(root) {
    const group = new THREE.Group();
    group.position.set(3.8, 3.7, -12.67);
    root.add(group);
    meshBox(1.15, 1.35, 0.25, this.materials.darkMetal, [0, 0, 0], group);
    for (let y = -0.42; y <= 0.43; y += 0.21) {
      for (let x = -0.35; x <= 0.36; x += 0.18) {
        const hole = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.08, 8), this.materials.rubber);
        hole.rotation.x = 90 * DEG;
        hole.position.set(x, y, 0.17);
        group.add(hole);
      }
    }
    this.objects.intercom = group;
  }

  buildLights() {
    this.scene.add(new THREE.HemisphereLight(0x8ca69d, 0x18110d, 1.35));
    this.scene.add(new THREE.AmbientLight(0x58645f, 0.72));
    const cameraFill = new THREE.PointLight(0xb7d6cc, 58, 28, 1.55);
    cameraFill.position.set(0, 3.6, 3.7);
    this.scene.add(cameraFill);
    const sideFill = new THREE.PointLight(0xff9a58, 38, 18, 1.7);
    sideFill.position.set(-4.2, 2.5, -3.5);
    this.scene.add(sideFill);
    this.objects.fluorescents = [];
    for (const [index, z] of [3.6, -2.5, -8.5].entries()) {
      const fixture = new THREE.Group();
      fixture.position.set(0, 5.27, z);
      this.root.add(fixture);
      meshBox(0.88, 0.18, 3.5, this.materials.edge, [0, 0, 0], fixture);
      const tubeMaterial = new THREE.MeshStandardMaterial({
        color: index === 1 ? 0x574a38 : 0xd5dfd5,
        emissive: index === 1 ? 0xa45b27 : 0xb8d5ce,
        emissiveIntensity: index === 2 ? 0.05 : 3.2,
        roughness: 0.3,
      });
      const tube = meshBox(0.48, 0.08, 3.05, tubeMaterial, [0, -0.13, 0], fixture);
      const light = new THREE.PointLight(index === 1 ? 0xff9c52 : 0xc9fff1, index === 2 ? 0 : index === 1 ? 105 : 82, 14, 1.65);
      light.position.set(0, -0.35, 0);
      light.castShadow = index < 2;
      light.shadow.mapSize.set(512, 512);
      light.shadow.bias = -0.001;
      fixture.add(light);
      this.objects.fluorescents.push({ fixture, tube, light, baseIntensity: light.intensity });
    }

    const redFill = new THREE.PointLight(0xd12820, 24, 7, 1.8);
    redFill.position.set(3.5, 2.2, -10.5);
    this.scene.add(redFill);
    this.objects.redFill = redFill;

    const coneMaterial = new THREE.MeshBasicMaterial({ color: 0xffc07c, transparent: true, opacity: 0.018, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
    const cone = new THREE.Mesh(new THREE.ConeGeometry(2.2, 5.2, 20, 1, true), coneMaterial);
    cone.position.set(0, 2.7, -2.5);
    cone.rotation.z = Math.PI;
    this.scene.add(cone);
  }

  buildInteractives() {
    const emergency = new THREE.Group();
    emergency.position.set(3.72, 1.78, -12.5);
    this.root.add(emergency);
    meshBox(1.62, 2.55, 0.42, this.materials.darkMetal, [0, 0, 0], emergency);
    const warning = panel(1.43, 0.72, makeWarningTexture(), [0, 0.75, 0.24], emergency);
    warning.material.map.anisotropy = 8;
    meshBox(1.2, 1.15, 0.35, this.materials.red, [0, -0.42, 0.25], emergency);
    const leverPivot = new THREE.Group();
    leverPivot.position.set(0, -0.13, 0.55);
    emergency.add(leverPivot);
    const leverStem = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.13, 0.85, 16), this.materials.brass);
    leverStem.position.y = -0.38;
    leverPivot.add(leverStem);
    const grip = meshBox(0.58, 0.25, 0.28, this.materials.red, [0, -0.82, 0], leverPivot, "emergency-grip");
    this.objects.leverPivot = leverPivot;
    addAction(emergency, "alarm");
    this.clickables.push(emergency);

    const keyhole = new THREE.Group();
    keyhole.position.set(-3.72, 1.68, -12.55);
    this.root.add(keyhole);
    meshBox(1.25, 2.2, 0.34, this.materials.darkMetal, [0, 0, 0], keyhole);
    meshBox(0.88, 1.72, 0.18, this.materials.brass, [0, 0, 0.25], keyhole);
    for (const [x, y] of [[-0.35, 0.68], [0.35, 0.68], [-0.35, -0.68], [0.35, -0.68]]) {
      const screw = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.06, 10), this.materials.edge);
      screw.rotation.x = 90 * DEG;
      screw.position.set(x, y, 0.4);
      keyhole.add(screw);
    }
    const lock = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.16, 20), this.materials.darkMetal);
    lock.rotation.x = 90 * DEG;
    lock.position.z = 0.42;
    keyhole.add(lock);
    meshBox(0.08, 0.34, 0.1, this.materials.rubber, [0, -0.1, 0.52], keyhole);

    this.buildDecisionSwitch(-1.22, "alarm", "ראיתם חריגה?", 0xa52f28);
    this.buildDecisionSwitch(1.22, "door", "הכל רגיל", 0x486e5a);
  }

  buildDecisionSwitch(x, action, label, color) {
    const group = new THREE.Group();
    group.position.set(x, 0.42, -9.75);
    group.rotation.x = -18 * DEG;
    this.root.add(group);
    meshBox(1.95, 0.46, 1.18, this.materials.darkMetal, [0, 0, 0], group);
    const switchMaterial = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.32, metalness: 0.67, roughness: 0.35 });
    const button = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.39, 0.25, 20), switchMaterial);
    button.position.set(0, 0.35, 0.08);
    group.add(button);
    const labelTexture = makeTextTexture({ title: label, footer: action === "door" ? "CONFIRM / E" : "REPORT / R", background: "#171a18", color: "#d8d2c2", accent: color === 0xa52f28 ? "#9b332c" : "#496c59", width: 512, height: 180 });
    const labelPlane = panel(1.46, 0.5, labelTexture, [0, 0.24, 0.53], group, { rotation: [-72 * DEG, 0, 0] });
    addAction(group, action);
    this.clickables.push(group);
    group.userData.button = button;
    group.userData.label = labelPlane;
  }

  buildAnomalyObjects() {
    const passenger = new THREE.Group();
    passenger.position.set(-3.9, 0.42, -5.5);
    this.root.add(passenger);
    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.45, 1.15, 8, 14), this.materials.rubber);
    torso.position.y = 1.1;
    torso.rotation.z = -8 * DEG;
    passenger.add(torso);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.34, 24, 16), this.materials.pale);
    head.scale.set(0.83, 1.15, 0.84);
    head.position.set(0.05, 2.08, 0.03);
    passenger.add(head);
    for (const x of [-0.12, 0.17]) {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.035, 10, 8), this.materials.rubber);
      eye.position.set(x, 2.15, 0.3);
      passenger.add(eye);
    }
    passenger.visible = false;
    this.objects.passenger = passenger;

    const face = new THREE.Group();
    face.position.set(4.67, 3.1, -2.3);
    face.rotation.y = -90 * DEG;
    this.root.add(face);
    const faceHead = new THREE.Mesh(new THREE.SphereGeometry(0.43, 26, 18), this.materials.pale);
    faceHead.scale.set(0.72, 1.2, 0.72);
    face.add(faceHead);
    for (const x of [-0.14, 0.14]) {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.055, 12, 8), this.materials.rubber);
      eye.position.set(x, 0.08, 0.34);
      face.add(eye);
    }
    face.visible = false;
    this.objects.face = face;

    const handTexture = canvasTexture((ctx, w, h) => {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "rgba(116,15,12,.68)";
      ctx.beginPath();
      ctx.ellipse(w * 0.52, h * 0.58, w * 0.18, h * 0.25, -0.18, 0, Math.PI * 2);
      ctx.fill();
      for (let i = 0; i < 5; i += 1) {
        ctx.save();
        ctx.translate(w * (0.34 + i * 0.085), h * 0.39);
        ctx.rotate((i - 2) * 0.11);
        ctx.fillRect(-w * 0.025, -h * (0.18 + (i % 2) * 0.03), w * 0.05, h * 0.24);
        ctx.restore();
      }
    }, 256, 256);
    this.objects.handprint = panel(0.9, 1.2, handTexture, [4.65, 3.2, -7.4], this.root, { rotation: [0, -90 * DEG, -12 * DEG], transparent: true, depthWrite: false });
    this.objects.handprint.visible = false;

    const footprints = new THREE.Group();
    this.root.add(footprints);
    for (let i = 0; i < 7; i += 1) {
      const printMaterial = new THREE.MeshBasicMaterial({ color: 0x050706, transparent: true, opacity: 0.74, side: THREE.DoubleSide });
      const print = new THREE.Mesh(new THREE.CircleGeometry(0.18, 15), printMaterial);
      print.scale.set(0.62, 1.35, 1);
      print.rotation.x = -90 * DEG;
      print.rotation.z = (i % 2 ? -12 : 12) * DEG;
      print.position.set(i % 2 ? 0.23 : -0.23, 0.025, 2.3 - i * 1.55);
      footprints.add(print);
    }
    footprints.visible = false;
    this.objects.footprints = footprints;

    const eyes = new THREE.Group();
    this.root.add(eyes);
    for (const x of [-4.68, 4.68]) {
      for (const offset of [-0.14, 0.14]) {
        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), new THREE.MeshBasicMaterial({ color: 0xe7a451 }));
        eye.position.set(x, 3.25, -0.4 + offset);
        eyes.add(eye);
      }
    }
    eyes.visible = false;
    this.objects.eyes = eyes;

    const extraSeat = new THREE.Group();
    extraSeat.position.set(3.95, 0.2, 6.4);
    this.root.add(extraSeat);
    meshBox(1.45, 0.38, 1.7, this.materials.seat, [0, 0.45, 0], extraSeat);
    meshBox(0.36, 1.55, 1.7, this.materials.seat, [0.54, 1.18, 0], extraSeat);
    extraSeat.visible = false;
    this.objects.extraSeat = extraSeat;
  }

  bindEvents() {
    this.resizeHandler = () => this.resize();
    window.addEventListener("resize", this.resizeHandler);
    this.canvas.addEventListener("pointermove", (event) => this.handlePointerMove(event));
    this.canvas.addEventListener("pointerleave", () => {
      this.pointer.set(2, 2);
      this.canvas.style.cursor = "crosshair";
    });
    this.canvas.addEventListener("click", (event) => this.handleClick(event));
  }

  handlePointerMove(event) {
    const rect = this.canvas.getBoundingClientRect();
    this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const hits = this.raycaster.intersectObjects(this.clickables, true);
    this.canvas.style.cursor = hits.length ? "pointer" : "crosshair";
  }

  handleClick(event) {
    this.handlePointerMove(event);
    const hits = this.raycaster.intersectObjects(this.clickables, true);
    const hit = hits.find((entry) => entry.object.userData.action);
    if (hit && this.onDecision) this.onDecision(hit.object.userData.action);
  }

  setLook(x, y) {
    this.targetLook.set(x, y);
  }

  setProgress(progress) {
    if (!this.objects.hologram) return;
    const texture = makeTextTexture({
      title: "האם הכל תקין?",
      subtitle: "סריקת חריגות בתהליך...",
      footer: `CAR_SCAN ${String(progress + 1).padStart(2, "0")} · MOTION 00.4 · TEMP 16.3° · SIGNAL LOST`,
      background: "rgba(3,18,18,.82)",
      color: "#8bd5c4",
      accent: "#477c74",
    });
    this.objects.hologram.material.map.dispose();
    this.objects.hologram.material.map = texture;
    this.objects.hologram.material.needsUpdate = true;
  }

  resetAnomaly() {
    for (const object of [this.objects.passenger, this.objects.face, this.objects.handprint, this.objects.footprints, this.objects.eyes, this.objects.extraSeat]) {
      if (object) object.visible = false;
    }
    if (this.objects.suitcase) this.objects.suitcase.visible = true;
    this.flickerMode = false;
    this.objects.vfd.material.map = makeTextTexture({ title: "התחנה הבאה · אין מידע", subtitle: "נא להישאר בקרון", footer: "NIGHT SERVICE / LINE 13", background: "#07130c", color: "#80c48c" });
    this.objects.clock.material.map = makeTextTexture({ title: "00:13", footer: "SYSTEM TIME", background: "#080606", color: "#e54c42", accent: "#5c1814", width: 384, height: 180 });
    this.objects.route.material.map = makeTextTexture({ title: "מרכז  •  הגשר  •  הביתה", subtitle: "הנקודה האדומה מציינת את מיקומכם", footer: "ROUTE 13 / DO NOT LEAVE BETWEEN STATIONS", background: "#d0cbbd", color: "#6f2722", accent: "#8f3a32" });
    this.objects.poster.material.map = makeTextTexture({ title: "אל תירדמו.", subtitle: "הדרך הבטוחה הביתה", footer: "METRO NIGHT AUTHORITY", background: "#c7c0ac", color: "#45251f", accent: "#9e4138" });
    this.objects.number.material.map = makeTextTexture({ title: "13", subtitle: "NIGHT LINE", background: "#160a09", color: "#df4b40", accent: "#7d211c", width: 320, height: 320 });
    for (const object of [this.objects.vfd, this.objects.clock, this.objects.route, this.objects.poster, this.objects.number]) object.material.needsUpdate = true;
    this.objects.intercom.scale.setScalar(1);
  }

  setAnomaly(id) {
    this.resetAnomaly();
    if (!id) return;
    if (id === "face") this.objects.face.visible = true;
    if (id === "handprint") this.objects.handprint.visible = true;
    if (id === "passenger") this.objects.passenger.visible = true;
    if (id === "bag") this.objects.suitcase.visible = false;
    if (id === "footprints") this.objects.footprints.visible = true;
    if (id === "eyes") this.objects.eyes.visible = true;
    if (id === "extra-seat") this.objects.extraSeat.visible = true;
    if (id === "lights") this.flickerMode = true;
    if (id === "intercom") this.objects.intercom.userData.pulsing = true;
    else this.objects.intercom.userData.pulsing = false;

    if (id === "clock") {
      this.objects.clock.material.map = makeTextTexture({ title: "03:33", footer: "TIME ERROR", background: "#080606", color: "#f1dbb6", accent: "#71332b", width: 384, height: 180 });
      this.objects.clock.material.needsUpdate = true;
    }
    if (id === "route") {
      this.objects.route.material.map = makeTextTexture({ title: "מרכז  •  הגשר  •  אין יציאה", subtitle: "התחנה האחרונה נמחקה", footer: "ROUTE UNKNOWN / PASSENGER NOT FOUND", background: "#c7c0b2", color: "#9c211b", accent: "#9c211b" });
      this.objects.route.material.needsUpdate = true;
    }
    if (id === "sign") {
      this.objects.vfd.material.map = makeTextTexture({ title: "אל תפתחו את הדלת", subtitle: "היא מחכה בצד השני", footer: "DOOR INTERLOCK FAILURE", background: "#210706", color: "#e64c40", accent: "#8b1d18" });
      this.objects.vfd.material.needsUpdate = true;
    }
    if (id === "number") {
      this.objects.number.material.map = makeTextTexture({ title: "1313", subtitle: "NO SERVICE", background: "#160a09", color: "#df4b40", accent: "#7d211c", width: 320, height: 320 });
      this.objects.number.material.needsUpdate = true;
    }
    if (id === "poster") {
      this.objects.poster.material.map = makeTextTexture({ title: "היא יושבת מאחוריך.", subtitle: "אל תסתובבו", footer: "THIS MESSAGE IS FOR YOU", background: "#bcb4a1", color: "#861b17", accent: "#861b17" });
      this.objects.poster.material.needsUpdate = true;
    }
  }

  openDoors() {
    this.doorAmount = 1;
    this.shake(0.12);
  }

  pullAlarm() {
    this.leverAmount = 1;
    this.objects.redFill.intensity = 95;
    this.shake(0.22);
  }

  resetActions() {
    this.doorAmount = 0;
    this.leverAmount = 0;
    this.objects.redFill.intensity = 24;
  }

  shake(amount = 0.15) {
    this.shakeAmount = Math.max(this.shakeAmount, amount);
  }

  resize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    if (!width || !height) return;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height, false);
  }

  render() {
    if (this.disposed) return;
    const delta = Math.min(this.clock.getDelta(), 0.04);
    const elapsed = this.clock.elapsedTime;

    this.currentLook.lerp(this.targetLook, 0.045);
    const swayX = Math.sin(elapsed * 1.7) * 0.018 + Math.sin(elapsed * 8.1) * 0.005;
    const swayY = Math.sin(elapsed * 2.15) * 0.012;
    const shakeX = (Math.random() - 0.5) * this.shakeAmount;
    const shakeY = (Math.random() - 0.5) * this.shakeAmount;
    this.shakeAmount *= 0.89;
    this.camera.position.x = this.currentLook.x * 0.52 + swayX + shakeX;
    this.camera.position.y = 2.05 + this.currentLook.y * 0.28 + swayY + shakeY;
    this.camera.lookAt(this.currentLook.x * 2.2, 2.05 + this.currentLook.y * 1.25, -11.5);

    this.objects.leftDoor.position.x = THREE.MathUtils.lerp(this.objects.leftDoor.position.x, -1.17 - this.doorAmount * 2.05, 0.055);
    this.objects.rightDoor.position.x = THREE.MathUtils.lerp(this.objects.rightDoor.position.x, 1.17 + this.doorAmount * 2.05, 0.055);
    this.objects.leverPivot.rotation.x = THREE.MathUtils.lerp(this.objects.leverPivot.rotation.x, this.leverAmount * -68 * DEG, 0.09);

    this.objects.gears.forEach((gear, index) => {
      gear.rotation.z += (index % 2 ? -1 : 1) * delta * (0.35 + index * 0.14);
    });
    this.outsideStreaks.forEach((item) => {
      item.mesh.position.z += item.speed * delta;
      if (item.mesh.position.z > 5.2) item.mesh.position.z = -11.8;
    });

    this.objects.hologram.material.opacity = 0.74 + Math.sin(elapsed * 3.2) * 0.07 + (Math.random() > 0.985 ? -0.28 : 0);
    const warm = this.objects.fluorescents[1];
    warm.light.intensity = warm.baseIntensity * (0.78 + Math.sin(elapsed * 17) * 0.08 + (Math.random() > 0.96 ? -0.72 : 0));
    warm.tube.material.emissiveIntensity = Math.max(0.15, warm.light.intensity / 7);

    if (this.flickerMode) {
      const cold = this.objects.fluorescents[0];
      const on = Math.random() > 0.32;
      cold.light.intensity = on ? cold.baseIntensity : 0;
      cold.tube.material.emissiveIntensity = on ? 3.2 : 0.02;
    } else {
      this.objects.fluorescents[0].light.intensity = this.objects.fluorescents[0].baseIntensity;
      this.objects.fluorescents[0].tube.material.emissiveIntensity = 3.2;
    }

    if (this.objects.intercom.userData.pulsing) {
      const scale = 1 + Math.sin(elapsed * 12) * 0.035;
      this.objects.intercom.scale.setScalar(scale);
    }

    this.renderer.render(this.scene, this.camera);
  }
}
