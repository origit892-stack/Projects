import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js";

function asteroidGeometry(radius, detail = 2) {
  const geometry = new THREE.IcosahedronGeometry(radius, detail);
  const position = geometry.attributes.position;
  const vertex = new THREE.Vector3();

  for (let i = 0; i < position.count; i += 1) {
    vertex.fromBufferAttribute(position, i);
    const n =
      1 +
      Math.sin(vertex.x * 2.7 + vertex.y * 1.4) * 0.18 +
      Math.cos(vertex.z * 3.1 - vertex.x) * 0.14 +
      THREE.MathUtils.randFloatSpread(0.22);
    vertex.multiplyScalar(n);
    position.setXYZ(i, vertex.x, vertex.y, vertex.z);
  }

  geometry.computeVertexNormals();
  return geometry;
}

export class AsteroidField {
  constructor(scene, stoneTexture) {
    this.scene = scene;
    this.stoneTexture = stoneTexture;
    this.asteroids = [];
    this.fragments = [];
    this.wave = 1;
    this.spawnTimer = 0;
    this.poolMaterial = new THREE.MeshStandardMaterial({
      map: this.stoneTexture,
      color: 0x9b9488,
      roughness: 0.96,
      metalness: 0.04,
      emissive: 0x15110d,
      emissiveIntensity: 0.18
    });
    this.crystalMaterial = new THREE.MeshStandardMaterial({
      color: 0x7d36ff,
      roughness: 0.2,
      metalness: 0.08,
      emissive: 0x8f3dff,
      emissiveIntensity: 1.8,
      transparent: true,
      opacity: 0.92
    });
    this.hotRockMaterial = new THREE.MeshBasicMaterial({
      color: 0xff8d3a,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
  }

  seedInitialField() {
    for (let i = 0; i < 95; i += 1) {
      const z = THREE.MathUtils.randFloat(-260, -30);
      const size = THREE.MathUtils.randFloat(0.8, 7.5);
      this.spawnAsteroid(size, new THREE.Vector3(THREE.MathUtils.randFloatSpread(95), THREE.MathUtils.randFloatSpread(58), z), true);
    }
  }

  spawnWave() {
    const count = 9 + this.wave * 2;
    for (let i = 0; i < count; i += 1) {
      const size = THREE.MathUtils.randFloat(1.4, 5.8 + this.wave * 0.45);
      const isCrystal = Math.random() < 0.075;
      this.spawnAsteroid(
        isCrystal ? THREE.MathUtils.randFloat(1.3, 2.25) : size,
        new THREE.Vector3(THREE.MathUtils.randFloatSpread(46), THREE.MathUtils.randFloatSpread(30), THREE.MathUtils.randFloat(-235, -170)),
        false,
        { type: isCrystal ? "crystal" : "rock" }
      );
    }
    this.wave += 1;
  }

  spawnAsteroid(size, position, ambient, options = {}) {
    const type = options.type || "rock";
    const geometry =
      type === "crystal"
        ? new THREE.OctahedronGeometry(size, 1)
        : asteroidGeometry(size, size > 3 ? 3 : 2);
    const mesh = new THREE.Mesh(geometry, type === "crystal" ? this.crystalMaterial : this.poolMaterial);
    mesh.position.copy(position);
    mesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    mesh.scale.set(
      type === "crystal" ? 0.72 : 1 + THREE.MathUtils.randFloatSpread(0.3),
      type === "crystal" ? 1.55 : 0.82 + Math.random() * 0.5,
      type === "crystal" ? 0.72 : 1 + THREE.MathUtils.randFloatSpread(0.34)
    );
    mesh.frustumCulled = true;
    mesh.userData = {
      type,
      radius: size * (type === "crystal" ? 1.25 : 1.15),
      health: type === "crystal" ? 1 : Math.ceil(size * 0.8),
      velocity: options.velocity || new THREE.Vector3(
        THREE.MathUtils.randFloatSpread(ambient ? 2.2 : 6),
        THREE.MathUtils.randFloatSpread(ambient ? 1.6 : 4),
        THREE.MathUtils.randFloat(ambient ? 1.8 : 8, ambient ? 10 : 23)
      ),
      spin: new THREE.Vector3(
        THREE.MathUtils.randFloatSpread(type === "crystal" ? 2.1 : 1.1),
        THREE.MathUtils.randFloatSpread(type === "crystal" ? 2.1 : 1.1),
        THREE.MathUtils.randFloatSpread(type === "crystal" ? 2.1 : 1.1)
      ),
      size
    };
    this.scene.add(mesh);
    this.asteroids.push(mesh);
  }

  update(delta, shipPosition) {
    this.spawnTimer -= delta;
    if (this.spawnTimer <= 0) {
      this.spawnWave();
      this.spawnTimer = Math.max(2.6, 7.2 - this.wave * 0.18);
    }

    for (let i = this.asteroids.length - 1; i >= 0; i -= 1) {
      const asteroid = this.asteroids[i];
      asteroid.position.addScaledVector(asteroid.userData.velocity, delta);
      asteroid.rotation.x += asteroid.userData.spin.x * delta;
      asteroid.rotation.y += asteroid.userData.spin.y * delta;
      asteroid.rotation.z += asteroid.userData.spin.z * delta;
      if (asteroid.userData.type === "crystal") {
        const pulse = 1 + Math.sin(performance.now() * 0.006 + asteroid.position.x) * 0.08;
        asteroid.scale.set(0.72 * pulse, 1.55 * pulse, 0.72 * pulse);
      }

      const farBehind = asteroid.position.z > 40;
      const farSide = Math.abs(asteroid.position.x - shipPosition.x) > 140 || Math.abs(asteroid.position.y - shipPosition.y) > 95;
      if (farBehind || farSide) {
        this.disposeAsteroid(i);
      }
    }

    this.updateFragments(delta);
  }

  checkLaserHits(lasers, onHit, onScore, onRepair) {
    for (let a = this.asteroids.length - 1; a >= 0; a -= 1) {
      const asteroid = this.asteroids[a];
      for (let l = lasers.length - 1; l >= 0; l -= 1) {
        const laser = lasers[l];
        if (asteroid.position.distanceTo(laser.position) < asteroid.userData.radius + 0.5) {
          asteroid.userData.health -= laser.userData.damage;
          onHit(laser);
          this.spark(asteroid.position, 18, 0.7);
          if (asteroid.userData.health <= 0) {
            const score = Math.round(asteroid.userData.size * (asteroid.userData.type === "crystal" ? 260 : 100));
            if (asteroid.userData.type === "crystal") {
              this.repairFlash(asteroid.position);
              onRepair(20);
            } else {
              this.explode(asteroid);
              if (asteroid.userData.size > 3) this.split(asteroid);
            }
            this.disposeAsteroid(a);
            onScore(score);
          }
          break;
        }
      }
    }
  }

  checkShipCollision(shipPosition) {
    for (let i = this.asteroids.length - 1; i >= 0; i -= 1) {
      const asteroid = this.asteroids[i];
      if (asteroid.position.distanceTo(shipPosition) < asteroid.userData.radius + 1.2) {
        this.explode(asteroid);
        this.disposeAsteroid(i);
        return Math.round(asteroid.userData.size * 6);
      }
    }
    return 0;
  }

  split(asteroid) {
    const pieces = THREE.MathUtils.randInt(2, 3);
    const newSize = asteroid.userData.size * 0.42;
    for (let i = 0; i < pieces; i += 1) {
      const direction = new THREE.Vector3(
        THREE.MathUtils.randFloatSpread(1.6),
        THREE.MathUtils.randFloatSpread(1.2),
        THREE.MathUtils.randFloat(0.25, 1)
      ).normalize();
      const offset = direction.clone().multiplyScalar(asteroid.userData.size * 1.25);
      const velocity = direction
        .clone()
        .multiplyScalar(18 + Math.random() * 18)
        .add(new THREE.Vector3(0, 0, 16 + Math.random() * 12));
      this.spawnAsteroid(newSize, asteroid.position.clone().add(offset), false, { velocity, type: "rock" });
    }
  }

  explode(asteroid) {
    this.spark(asteroid.position, Math.min(900, 190 + asteroid.userData.size * 95), asteroid.userData.size);
  }

  spark(position, count, power) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = [];

    for (let i = 0; i < count; i += 1) {
      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;
      velocities.push(new THREE.Vector3().randomDirection().multiplyScalar(8 + Math.random() * 28 * power));
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const points = new THREE.Points(
      geometry,
      new THREE.PointsMaterial({
        color: 0xff8d3a,
        size: 0.12 + power * 0.08,
        transparent: true,
        opacity: 1,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      })
    );
    points.userData = { life: 1.25, maxLife: 1.25, velocities };
    this.scene.add(points);
    this.fragments.push(points);

    const flash = new THREE.Mesh(
      new THREE.SphereGeometry(1.4 + power, 24, 12),
      this.hotRockMaterial.clone()
    );
    flash.position.copy(position);
    flash.userData = { life: 0.38, maxLife: 0.38, velocities: [] };
    this.scene.add(flash);
    this.fragments.push(flash);
  }

  repairFlash(position) {
    this.spark(position, 150, 1.1);
    const flash = new THREE.Mesh(
      new THREE.SphereGeometry(2.8, 24, 12),
      new THREE.MeshBasicMaterial({
        color: 0x35ff7a,
        transparent: true,
        opacity: 0.95,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      })
    );
    flash.position.copy(position);
    flash.userData = { life: 0.55, maxLife: 0.55, velocities: [] };
    this.scene.add(flash);
    this.fragments.push(flash);
  }

  updateFragments(delta) {
    for (let i = this.fragments.length - 1; i >= 0; i -= 1) {
      const fragment = this.fragments[i];
      fragment.userData.life -= delta;
      const t = Math.max(0, fragment.userData.life / fragment.userData.maxLife);

      if (fragment.isPoints) {
        const position = fragment.geometry.attributes.position;
        for (let p = 0; p < position.count; p += 1) {
          const velocity = fragment.userData.velocities[p];
          position.array[p * 3] += velocity.x * delta;
          position.array[p * 3 + 1] += velocity.y * delta;
          position.array[p * 3 + 2] += velocity.z * delta;
        }
        position.needsUpdate = true;
        fragment.material.opacity = t;
      } else {
        fragment.scale.multiplyScalar(1 + delta * 8);
        fragment.material.opacity = t * 0.82;
      }

      if (fragment.userData.life <= 0) {
        this.scene.remove(fragment);
        fragment.geometry.dispose();
        fragment.material.dispose();
        this.fragments.splice(i, 1);
      }
    }
  }

  disposeAsteroid(index) {
    const asteroid = this.asteroids[index];
    this.scene.remove(asteroid);
    asteroid.geometry.dispose();
    this.asteroids.splice(index, 1);
  }
}
