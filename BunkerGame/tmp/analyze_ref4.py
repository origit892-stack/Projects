from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
px = im.load()

def sat(r, g, b):
    mx = max(r, g, b); mn = min(r, g, b)
    return (mx - mn)

# saturated + not too dark/bright
step = 4
mask = [[ (sat(*px[x,y]) > 70 and max(px[x,y]) > 90) for x in range(0, w, step)] for y in range(0, h, step)]
H = len(mask); W = len(mask[0])
seen = [[False]*W for _ in range(H)]
comps = []
for y in range(H):
    for x in range(W):
        if mask[y][x] and not seen[y][x]:
            stack = [(x, y)]; seen[y][x] = True; cells = []
            while stack:
                cx, cy = stack.pop(); cells.append((cx, cy))
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = cx+dx, cy+dy
                    if 0 <= nx < W and 0 <= ny < H and mask[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True; stack.append((nx, ny))
            if len(cells) > 400:
                xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
                x0,y0,x1,y1 = min(xs)*step, min(ys)*step, max(xs)*step, max(ys)*step
                comps.append((x0,y0,x1,y1,(x1-x0),(y1-y0),len(cells)*step*step))

comps.sort(key=lambda c: -c[6])
print('saturated blocks (x0,y0,x1,y1,w,h,area):')
for c in comps[:25]:
    print('  %4d,%4d -> %4d,%4d  w=%4d h=%4d area=%d' % c)
