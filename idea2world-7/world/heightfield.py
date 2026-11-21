"""Deterministic heightfield shared by the Python planner and the generated Luau build.

The planner computes the field once, validates it (slopes, clearance, water), and bakes it
into `WorldLayout.lua`. Studio therefore builds exactly the terrain that was validated --
there is no second, silently different noise implementation inside Roblox.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence


def _hash2(ix: int, iz: int, seed: int) -> float:
    n = math.sin(ix * 127.1 + iz * 311.7 + seed * 0.013) * 43758.5453
    return n - math.floor(n)


def _smooth_noise(x: float, z: float, seed: int) -> float:
    ix, iz = math.floor(x), math.floor(z)
    fx, fz = x - ix, z - iz
    fx = fx * fx * (3 - 2 * fx)
    fz = fz * fz * (3 - 2 * fz)
    a = _hash2(ix, iz, seed)
    b = _hash2(ix + 1, iz, seed)
    c = _hash2(ix, iz + 1, seed)
    d = _hash2(ix + 1, iz + 1, seed)
    ab = a + (b - a) * fx
    cd = c + (d - c) * fx
    return ab + (cd - ab) * fz


def fbm(x: float, z: float, seed: int, octaves: int = 4, lacunarity: float = 2.0, gain: float = 0.5) -> float:
    """Fractal value noise in 0..1."""
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        total += _smooth_noise(x * (lacunarity ** o), z * (lacunarity ** o), seed + o * 977) * amp
        norm += amp
        amp *= gain
    return total / norm if norm else 0.0


def ridged(x: float, z: float, seed: int, octaves: int = 4) -> float:
    """Ridge silhouette used for mountain chains (0..1)."""
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        n = _smooth_noise(x * (2.0 ** o), z * (2.0 ** o), seed + o * 613)
        total += (1.0 - abs(2.0 * n - 1.0)) * amp
        norm += amp
        amp *= 0.5
    return total / norm if norm else 0.0


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge1 == edge0:
        return 1.0 if value >= edge1 else 0.0
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3 - 2 * t)


class Heightfield:
    """Square, centered heightfield. `at()` is bilinear; `slope_deg()` uses a 2x2 sample."""

    def __init__(self, size: float, res: int, rows: Sequence[Sequence[float]], water: float | None = None):
        if res < 2:
            raise ValueError("res must be >= 2")
        self.size = float(size)
        self.res = int(res)
        self.rows = [[float(v) for v in row] for row in rows]
        if len(self.rows) != self.res or any(len(r) != self.res for r in self.rows):
            raise ValueError("heightfield rows must be res x res")
        self.cell = self.size / (self.res - 1)
        self.water = float(water if water is not None else self.min_height())
        self.min = self.min_height()
        self.max = self.max_height()

    # -- construction -----------------------------------------------------------------
    @classmethod
    def generate(cls, size: float, res: int, seed: int, relief: float = 1.0,
                 base: float = 6.0, mountain_mask: bool = True,
                 region_shapes: Iterable[dict] = ()) -> "Heightfield":
        """Generate a natural field, then apply planner-authored region shapes.

        region_shapes: dicts with keys center (x,z), radius, raise (m), flatten (0..1),
        style in {"plateau", "basin", "hill", "cliff", "flat"}.
        """
        size = float(size)
        rows = []
        for j in range(res):
            z = -size / 2 + j * size / (res - 1)
            row = []
            for i in range(res):
                x = -size / 2 + i * size / (res - 1)
                nx, nz = x / size, z / size
                broad = fbm(nx * 4.5 + 11.0, nz * 4.5 - 8.0, seed, 4)
                detail = fbm(nx * 15.0 - 3.0, nz * 15.0 + 9.0, seed + 91, 3)
                h = base + (broad * 26.0 + detail * 6.0) * relief
                if mountain_mask:
                    mask = max(0.0, min(1.0, (fbm(nx * 2.4 + 30.0, nz * 2.4 + 20.0, seed + 17, 3) - 0.42) * 2.6))
                    h += ridged(nx * 7.0 + 2.0, nz * 7.0 - 5.0, seed + 53, 4) ** 2 * 110.0 * relief * mask
                row.append(h)
            rows.append(row)

        field = cls(size, res, rows)
        for shape in region_shapes:
            field.apply_region(shape)
        return field

    def apply_region(self, shape: dict) -> None:
        cx, cz = shape["center"]
        radius = max(1.0, float(shape["radius"]))
        style = shape.get("style", "flat")
        raise_by = float(shape.get("raise", 0.0))
        flatten = max(0.0, min(1.0, float(shape.get("flatten", 0.0))))
        target = shape.get("target")
        for j in range(self.res):
            z = -self.size / 2 + j * self.cell
            for i in range(self.res):
                x = -self.size / 2 + i * self.cell
                d = math.hypot(x - cx, z - cz)
                if d > radius * 1.6:
                    continue
                t = 1.0 - smoothstep(radius * 0.55, radius * 1.6, d)
                if t <= 0.0:
                    continue
                if style == "basin":
                    delta = -raise_by * t
                elif style == "plateau":
                    delta = raise_by * t
                elif style == "hill":
                    delta = raise_by * (t ** 2)
                elif style == "cliff":
                    delta = raise_by * smoothstep(0.15, 0.85, t)
                else:
                    delta = raise_by * t
                self.rows[j][i] += delta
                if target is not None:
                    toward = (float(target) - self.rows[j][i]) * t
                    self.rows[j][i] += toward * flatten

    def merge_water_basin(self, water_level: float, depth: float = 4.0) -> None:
        """Clamp terrain that sits just under the water line so lakes read as lakes."""
        for j in range(self.res):
            for i in range(self.res):
                h = self.rows[j][i]
                if h < water_level + depth:
                    self.rows[j][i] = min(self.rows[j][i], water_level - depth * 0.5)

    # -- queries ----------------------------------------------------------------------
    def index_of(self, value: float) -> float:
        return (value + self.size / 2) / self.cell

    def position_of(self, index: float) -> float:
        return -self.size / 2 + index * self.cell

    def at(self, x: float, z: float) -> float:
        fx = max(0.0, min(self.res - 1.0, self.index_of(x)))
        fz = max(0.0, min(self.res - 1.0, self.index_of(z)))
        x0, z0 = int(math.floor(fx)), int(math.floor(fz))
        x1, z1 = min(x0 + 1, self.res - 1), min(z0 + 1, self.res - 1)
        tx, tz = fx - x0, fz - z0
        a = self.rows[z0][x0]
        b = self.rows[z0][x1]
        c = self.rows[z1][x0]
        d = self.rows[z1][x1]
        ab = a + (b - a) * tx
        cd = c + (d - c) * tx
        return ab + (cd - ab) * tz

    def slope_deg(self, x: float, z: float) -> float:
        d = max(self.cell, 1.0)
        hx = self.at(x + d, z) - self.at(x - d, z)
        hz = self.at(x, z + d) - self.at(x, z - d)
        grad = math.hypot(hx, hz) / (2 * d)
        return math.degrees(math.atan(grad))

    def min_height(self) -> float:
        return min(min(r) for r in self.rows)

    def max_height(self) -> float:
        return max(max(r) for r in self.rows)

    def rows_int(self) -> list[list[int]]:
        """Rounded integers keep the baked Luau table small."""
        return [[int(round(v)) for v in row] for row in self.rows]

    def stats(self) -> dict:
        return {"size": self.size, "res": self.res, "cell": round(self.cell, 3),
                "min": round(self.min, 2), "max": round(self.max, 2), "water": round(self.water, 2)}
