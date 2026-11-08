from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
print('size', w, h)
px = im.load()

# Scan for saturated blue regions (button family): blue dominant, high saturation
import collections
blue_cells = []
for y in range(0, h, 8):
    for x in range(0, w, 8):
        r, g, b = px[x, y]
        if b > 120 and b > r + 40 and b > g + 20:
            blue_cells.append((x, y, (r, g, b)))

if not blue_cells:
    print('no blue cells found')
else:
    xs = [c[0] for c in blue_cells]
    ys = [c[1] for c in blue_cells]
    print('blue bbox: x[%d..%d] y[%d..%d] count=%d' % (min(xs), max(xs), min(ys), max(ys), len(blue_cells)))
    # cluster by y to find individual buttons
    ys_sorted = sorted(set(ys))
    clusters = []
    cur = [ys_sorted[0]]
    for y in ys_sorted[1:]:
        if y - cur[-1] <= 16:
            cur.append(y)
        else:
            clusters.append((cur[0], cur[-1]))
            cur = [y]
    clusters.append((cur[0], cur[-1]))
    print('y-clusters (button rows):')
    for c in clusters:
        print('  y %d..%d (h~%d)' % (c[0], c[1], c[1]-c[0]))
