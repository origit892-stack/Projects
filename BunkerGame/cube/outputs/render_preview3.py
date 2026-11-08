#!/usr/bin/env python3
import numpy as np
from PIL import Image

OBJ = "/Users/Ori/Documents/Projects/BunkerGame/cube/outputs/output.obj"
OUT = "/Users/Ori/Documents/Projects/BunkerGame/cube/outputs/preview_4view.png"
W, H = 560, 420
BG = np.array([24, 26, 30], dtype=np.uint8)
BASE = np.array([122, 130, 140], dtype=np.float64)

verts, faces = [], []
with open(OBJ) as fh:
    for line in fh:
        if line.startswith("v "):
            p = line.split()
            verts.append([float(p[1]), float(p[2]), float(p[3])])
        elif line.startswith("f "):
            idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
            for k in range(1, len(idx) - 1):
                faces.append((idx[0], idx[k], idx[k + 1]))

V = np.array(verts, dtype=np.float64)
F = np.array(faces, dtype=np.int64)
V -= V.mean(0)
V /= (V.max(0) - V.min(0)).max()

def render(elev_deg, azim_deg):
    e, a = np.deg2rad(elev_deg), np.deg2rad(azim_deg)
    cy, sy = np.cos(a), np.sin(a)
    ce, se = np.cos(e), np.sin(e)
    R = np.array([[cy, 0, -sy], [sy*se, ce, cy*se], [-sy*ce, se, -cy*ce]])
    P = V @ R.T
    zbuf = np.full((H, W), np.inf)
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:] = BG
    scale = 0.80 * min(W, H)
    cx = (P[:, 0] + 0.02) * scale + W / 2
    cyy = (0.88 - P[:, 1]) * scale + H / 2
    tri_v = V[F]
    tri_p = P[F]
    order = np.argsort(-tri_p[:, 0, 2], kind="stable")
    for fi in order:
        x = cx[F[fi]]
        y = cyy[F[fi]]
        z = tri_p[fi][:, 2]
        ax, ay, bx, by, cx2, cy2 = x[0], y[0], x[1], y[1], x[2], y[2]
        x0, x1 = max(int(np.floor(x.min())), 0), min(int(np.ceil(x.max())), W - 1)
        y0, y1 = max(int(np.floor(y.min())), 0), min(int(np.ceil(y.max())), H - 1)
        if x0 > x1 or y0 > y1:
            continue
        area2 = (bx - ax) * (cy2 - ay) - (by - ay) * (cx2 - ax)
        if abs(area2) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        w0 = ((bx - gx) * (cy2 - gy) - (cx2 - gx) * (by - gy)) / area2
        w1 = ((cx2 - gx) * (ay - gy) - (ax - gx) * (cy2 - gy)) / area2
        w2 = 1.0 - w0 - w1
        if area2 > 0:
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        else:
            inside = (w0 <= 1e-6) & (w1 <= 1e-6) & (w2 <= 1e-6)
        if not inside.any():
            continue
        zpix = w0 * z[0] + w1 * z[1] + w2 * z[2]
        n = np.cross(tri_v[fi, 1] - tri_v[fi, 0], tri_v[fi, 2] - tri_v[fi, 0])
        nl = np.linalg.norm(n)
        if nl < 1e-12:
            continue
        n = (n / nl) @ R.T
        if n[2] < 0:
            n = -n
        diff = np.clip(n[2], 0.0, 1.0) * 0.6 + 0.35
        col = (BASE * diff).clip(0, 255).astype(np.uint8)
        mask = inside & (zpix < zbuf[y0:y1 + 1, x0:x1 + 1])
        if mask.any():
            zbuf[y0:y1 + 1, x0:x1 + 1][mask] = zpix[mask]
            img[y0:y1 + 1, x0:x1 + 1][mask] = col
    return img

tiles = [render(18, az) for az in (15, 105, 195, 285)]
pad = 10
full = np.full((H + 2 * pad, W * 4 + 5 * pad, 3), BG, dtype=np.uint8)
for i, t in enumerate(tiles):
    full[pad:pad + H, pad + i * (W + pad):pad + i * (W + pad) + W] = t
Image.fromarray(full).save(OUT)
print("saved", OUT)
