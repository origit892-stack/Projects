from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert('RGB')
w, h = im.size
px = im.load()

# The button column appears to be on the left (x ~ 0..140). 
# Find the button's left/right/top/bottom by detecting the dark outline.
def is_dark(r,g,b):
    return r < 50 and g < 50 and b < 50

# Scan a horizontal line through the middle of the first button (y~150)
for y in [150, 430, 570]:
    row = []
    for x in range(0, 160):
        r,g,b = px[x,y]
        if is_dark(r,g,b): row.append('D')
        elif b > r+40 and b > 90: row.append('B')  # blue
        elif r > g+40 and r > b+20: row.append('R')  # red
        elif max(r,g,b) > 200 and max(r,g,b)-min(r,g,b) < 30: row.append('W')  # white
        elif max(r,g,b) < 60: row.append('.')
        else: row.append('o')
    print('y=%3d: %s' % (y, ''.join(row)))

print()
# Vertical gradient sample through button center x=70
print('--- vertical gradient at x=70 (button body) ---')
for y in range(40, 240, 8):
    print('  y=%3d %s' % (y, px[70,y]))
