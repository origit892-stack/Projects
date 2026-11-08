from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
print('size', w, h)
px = im.load()

x = w // 2
prev = None
print('--- vertical strip at x=%d ---' % x)
for y in range(0, h, 2):
    c = px[x, y]
    if prev is None or (abs(c[0]-prev[0]) + abs(c[1]-prev[1]) + abs(c[2]-prev[2]) > 60):
        print(y, c)
        prev = c
