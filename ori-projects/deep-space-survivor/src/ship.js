import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js";

function hullMaterial(color, metalness = 0.82) {
  return new THREE.MeshStandardMaterial({
    color,
    metalness,
    roughness: 0.32,
    emissive: new THREE.Color(0x070d14),
    emissiveIntensity: 0.18,
    envMapIntensity: 0.8
  });
}

function addPanelLines(parent, width, z, y) {
  const material = new THREE.MeshBasicMaterial({ color: 0x83cfff, transparent: true, opacity: 0.28 });
  for (let i = -2; i <= 2; i += 1) {
    const line = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.018, 1.35), material);
    line.position.set((i * width) / 5, y, z);
    parent.add(line);
  }
}

export class Starfighter {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.velocity = new THREE.Vector3();
    this.targetOffset = new THREE.Vector3();
    this.state = "idle";
    this.lasers = [];
    this.muzzleCooldown = 0;
    this.fireInterval = 0.105;
    this.engineTrails = [];
    this.shield = null;
    this.shieldTimer = 0;
    this.scene.add(this.group);
    this.createMesh();
  }

  createMesh() {
    const darkMetal = hullMaterial(0x1b242b);
    const graphite = hullMaterial(0x303943, 0.72);
    const brightEdge = hullMaterial(0x8ba5b5, 0.9);
    const glowBlue = new THREE.MeshBasicMaterial({ color: 0x28b8ff });
    const glowOrange = new THREE.MeshBasicMaterial({ color: 0xff7b28 });

    const nose = new THREE.Mesh(new THREE.ConeGeometry(0.58, 3.1, 8, 1), darkMetal);
    nose.rotation.x = Math.PI / 2;
    nose.position.z = -1.6;
    this.group.add(nose);

    const body = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.55, 2.4), graphite);
    body.position.z = -0.15;
    this.group.add(body);

    const cockpit = new THREE.Mesh(
      new THREE.SphereGeometry(0.42, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.55),
      new THREE.MeshStandardMaterial({
        color: 0x092239,
        metalness: 0.15,
        roughness: 0.08,
        emissive: 0x0d68a2,
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.86
      })
    );
    cockpit.scale.set(0.78, 0.42, 1.05);
    cockpit.position.set(0, 0.38, -0.72);
    this.group.add(cockpit);

    const wingGeometry = new THREE.BufferGeometry();
    wingGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(
        new Float32Array([
          0, 0, -1.2, 3.1, -0.08, 0.45, 0.4, 0.04, 0.85,
          0, 0, -1.2, 0.4, 0.04, 0.85, 2.45, -0.18, 1.35
        ]),
        3
      )
    );
    wingGeometry.computeVertexNormals();

    const leftWing = new THREE.Mesh(wingGeometry, darkMetal);
    const rightWing = leftWing.clone();
    rightWing.scale.x = -1;
    this.group.add(leftWing, rightWing);

    for (const side of [-1, 1]) {
      const rail = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 2.35), brightEdge);
      rail.position.set(side * 1.28, 0.03, -0.08);
      rail.rotation.z = side * 0.16;
      this.group.add(rail);

      const cannon = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.08, 1.35, 14), brightEdge);
      cannon.rotation.x = Math.PI / 2;
      cannon.position.set(side * 0.54, -0.08, -1.88);
      this.group.add(cannon);

      const fin = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.78, 1.1), darkMetal);
      fin.position.set(side * 0.72, 0.42, 0.9);
      fin.rotation.z = side * 0.18;
      this.group.add(fin);

      const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.24, 0.45, 24), graphite);
      nozzle.rotation.x = Math.PI / 2;
      nozzle.position.set(side * 0.42, -0.03, 1.22);
      this.group.add(nozzle);

      const core = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.08, 0.24, 24), side < 0 ? glowBlue : glowOrange);
      core.rotation.x = Math.PI / 2;
      core.position.set(side * 0.42, -0.03, 1.48);
      this.group.add(core);

      const trail = new THREE.Mesh(
        new THREE.ConeGeometry(0.16, 2.2, 24, 1, true),
        new THREE.MeshBasicMaterial({
          color: side < 0 ? 0x21a9ff : 0xff742b,
          transparent: true,
          opacity: 0.5,
          blending: THREE.AdditiveBlending,
          depthWrite: false
        })
      );
      trail.rotation.x = -Math.PI / 2;
      trail.position.set(side * 0.42, -0.03, 2.45);
      this.engineTrails.push(trail);
      this.group.add(trail);
    }

    addPanelLines(this.group, 0.8, -0.7, 0.3);
    this.shield = new THREE.Mesh(
      new THREE.SphereGeometry(2.05, 48, 24),
      new THREE.MeshBasicMaterial({
        color: 0x76ddff,
        transparent: true,
        opacity: 0,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        wireframe: true
      })
    );
    this.shield.visible = false;
    this.group.add(this.shield);

    this.group.scale.setScalar(1.05);
    this.group.position.set(0, 0, 0);
  }

  update(delta, input, camera) {
    this.state = input.firing ? "firing" : input.moving ? "movement" : "idle";
    const speed = 15.5;
    this.targetOffset.set(input.x * 8.5, input.y * 5.5, 0);

    const desired = new THREE.Vector3(this.targetOffset.x, this.targetOffset.y, 0);
    this.group.position.lerp(desired, 1 - Math.pow(0.001, delta));

    this.velocity.x = input.x * speed;
    this.velocity.y = input.y * speed;
    this.group.rotation.z = THREE.MathUtils.lerp(this.group.rotation.z, -input.x * 0.42, 1 - Math.pow(0.005, delta));
    this.group.rotation.x = THREE.MathUtils.lerp(this.group.rotation.x, input.y * 0.18, 1 - Math.pow(0.005, delta));
    this.group.rotation.y = THREE.MathUtils.lerp(this.group.rotation.y, input.x * 0.15, 1 - Math.pow(0.005, delta));

    for (const trail of this.engineTrails) {
      trail.scale.setScalar(0.82 + Math.random() * 0.22 + Math.abs(input.x + input.y) * 0.06);
      trail.material.opacity = 0.33 + Math.random() * 0.26;
    }
    this.updateShield(delta);

    this.muzzleCooldown -= delta;
    if (input.firing && this.muzzleCooldown <= 0) {
      this.fire(camera);
      this.muzzleCooldown = this.fireInterval;
    }

    this.updateLasers(delta);
  }

  triggerShieldImpact() {
    this.shieldTimer = 0.42;
    if (this.shield) {
      this.shield.visible = true;
      this.shield.scale.setScalar(0.78);
      this.shield.material.opacity = 0.72;
    }
  }

  updateShield(delta) {
    if (!this.shield || this.shieldTimer <= 0) {
      if (this.shield) this.shield.visible = false;
      return;
    }

    this.shieldTimer -= delta;
    const t = Math.max(0, this.shieldTimer / 0.42);
    this.shield.visible = true;
    this.shield.scale.setScalar(0.9 + (1 - t) * 0.42);
    this.shield.material.opacity = t * 0.58;
    this.shield.rotation.y += delta * 2.5;
    this.shield.rotation.z -= delta * 1.9;
  }

  fire() {
    const laserMaterial = new THREE.MeshBasicMaterial({
      color: 0x49d5ff,
      transparent: true,
      opacity: 0.95,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    for (const side of [-1, 1]) {
      const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 3.6, 12), laserMaterial.clone());
      beam.rotation.x = Math.PI / 2;
      beam.position.copy(this.group.position).add(new THREE.Vector3(side * 0.58, -0.08, -2.6));
      beam.userData.velocity = new THREE.Vector3(0, 0, -155);
      beam.userData.life = 1.55;
      beam.userData.damage = 1;
      this.scene.add(beam);
      this.lasers.push(beam);
    }
  }

  updateLasers(delta) {
    for (let i = this.lasers.length - 1; i >= 0; i -= 1) {
      const laser = this.lasers[i];
      laser.position.addScaledVector(laser.userData.velocity, delta);
      laser.userData.life -= delta;
      laser.material.opacity = Math.max(0, laser.userData.life / 1.55);
      if (laser.userData.life <= 0 || laser.position.z < -250) {
        this.scene.remove(laser);
        laser.geometry.dispose();
        laser.material.dispose();
        this.lasers.splice(i, 1);
      }
    }
  }

  removeLaser(laser) {
    const index = this.lasers.indexOf(laser);
    if (index >= 0) this.lasers.splice(index, 1);
    this.scene.remove(laser);
    laser.geometry.dispose();
    laser.material.dispose();
  }
}
