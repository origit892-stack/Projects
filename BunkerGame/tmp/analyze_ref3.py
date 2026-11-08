from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
px = im.load()

# Strong saturated blue mask (button gradient: cyan-blue top to royal blue bottom)
def is_blue(r, g, b):
    return b > 100 and b > r + 50 and b > g + 10 and (b - r) > 60

mask = [[is_blue(*px[x, y]) for x in range(0, w, 4)] for y in range(0, h, 4)]
H = len(mask); W = len(mask[0])

# connected components (4-neighbor)
seen = [[False]*W for _ in range(H)]
comps = []
for y in range(H):
    for x in range(W):
        if mask[y][x] and not seen[y][x]:
            # BFS
            stack = [(x, y)]
            seen[y][x] = True
            cells = []
            while stack:
                cx, cy = stack.pop()
                cells.append((cx, cy))
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = cx+dx, cy+dy
                    if 0 <= nx < W and 0 <= ny < H and mask[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            if len(cells) > 200:  # big enough to be a button
                xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
                comps.append((min(xs)*4, min(ys)*4, max(xs)*4, max(ys)*4, len(cells)*16))

comps.sort(key=lambda c: -c[4])
print('large blue components (x0,y0,x1,y1,area):')
for c in comps[:15]:
    print('  %d,%d -> %d,%d  (w=%d h=%d area=%d)' % (c[0], c[1], c[2], c[3], c[2]-c[0], c[3]-c[1], c[4]))
