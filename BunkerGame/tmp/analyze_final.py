from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
px = im.load()
print('size', w, h)

# 1. Background color (sample far-right column which is pure background)
print('--- background samples (right edge x=290) ---')
for y in [10, 100, 300, 500, 670]:
    print('  y=%3d %s' % (y, px[290, y]))

# 2. Blue button background gradient - sample left blue strip (x=20) through button rows
print('--- button blue bg gradient (x=20) ---')
for y in range(95, 200, 10):
    print('  y=%3d %s' % (y, px[20, y]))

# 3. Button 1 exact horizontal bounds at y=150 (find dark outline)
def is_dark(r,g,b): return r<50 and g<50 and b<50
y=150
xs=[x for x in range(w) if is_dark(*px[x,y])]
print('--- button1 dark outline x at y=150:', xs[:5], '...', xs[-5:] if len(xs)>5 else '')

# 4. Corner radius: check top-left corner of button1 (around x=11,y=90)
print('--- top-left corner region (x 8-30, y 88-110) ---')
for y in range(88, 112, 2):
    row=[]
    for x in range(8, 32):
        r,g,b=px[x,y]
        if is_dark(r,g,b): row.append('#')
        elif b>r+40 and b>90: row.append('B')
        else: row.append('.')
    print('  y=%3d %s' % (y, ''.join(row)))

# 5. Label text: find white text rows and sample
print('--- white label region (y 200-235) sample ---')
for y in range(200, 236, 4):
    whites=[x for x in range(w) if min(px[x,y])>180]
    if whites:
        print('  y=%3d white x %d..%d (n=%d)' % (y, min(whites), max(whites), len(whites)))
