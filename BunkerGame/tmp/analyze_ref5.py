from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
px = im.load()

def cat(r, g, b):
    mx = max(r,g,b); mn = min(r,g,b)
    if mx < 60: return '.'          # near black
    if mx - mn < 30:
        if mx > 200: return 'W'     # white
        if mx > 120: return 'g'     # gray
        return 'd'                  # dark gray
    # colored
    if b > r and b > g: return 'B'  # blue
    if r > g and r > b: return 'R'  # red
    if g > r and g > b: return 'G'  # green
    if r > 120 and b > 120 and g < r: return 'P'  # purple
    return 'c'

# downsample to ~150 wide
TW = 150
TH = int(h * TW / w)
for ty in range(TH):
    row = []
    for tx in range(TW):
        x = int((tx + 0.5) * w / TW)
        y = int((ty + 0.5) * h / TH)
        row.append(cat(*px[x, y]))
    print(''.join(row))
