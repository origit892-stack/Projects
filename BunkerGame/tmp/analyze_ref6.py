from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
px = im.load()

def cat(r, g, b):
    mx = max(r,g,b); mn = min(r,g,b)
    if mx < 50: return '.'
    if mx - mn < 25:
        if mx > 210: return 'W'
        if mx > 130: return 'g'
        return 'd'
    if b > r and b > g: return 'B'
    if r > g and r > b: return 'R'
    if g > r and g > b: return 'G'
    if r > 110 and b > 110 and g < min(r,b): return 'P'
    return 'c'

TW = 60
TH = int(h * TW / w)
for ty in range(TH):
    row = []
    for tx in range(TW):
        x = int((tx + 0.5) * w / TW)
        y = int((ty + 0.5) * h / TH)
        row.append(cat(*px[x, y]))
    print('%3d ' % (ty*h//TH) + ''.join(row))
