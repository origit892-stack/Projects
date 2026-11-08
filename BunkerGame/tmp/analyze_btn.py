from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
px = im.load()
print('size', w, h)

# Find dark outline pixels (near-black) to locate button borders
def is_dark(r,g,b):
    return r < 45 and g < 45 and b < 45

# For each row, count dark pixels and find leftmost/rightmost
dark_rows = []
for y in range(h):
    xs = [x for x in range(w) if is_dark(*px[x,y])]
    if len(xs) > 5:
        dark_rows.append((y, min(xs), max(xs), len(xs)))

# Group consecutive dark rows into horizontal bands (top/bottom outlines)
print('--- dark horizontal bands (y, xmin, xmax, count) ---')
if dark_rows:
    bands = []
    cur = [dark_rows[0]]
    for r in dark_rows[1:]:
        if r[0] - cur[-1][0] <= 3:
            cur.append(r)
        else:
            bands.append(cur); cur=[r]
    bands.append(cur)
    for b in bands:
        ys=[r[0] for r in b]
        xmins=[r[1] for r in b]; xmaxs=[r[2] for r in b]
        print('  y %d..%d  x %d..%d  (thickness~%d)' % (min(ys),max(ys),min(xmins),max(xmaxs),max(ys)-min(ys)))
