import re, sys
path = sys.argv[1]
data = open(path).read()
blocks = re.findall(r'<CoordinateFrame name="CFrame">(.*?)</CoordinateFrame>', data, re.S)
print('Total CFrame blocks:', len(blocks))
non_identity = 0
for b in blocks:
    def g(tag):
        m = re.search(r'<'+tag+r'>([-0-9.eE+]+)</'+tag+r'>', b)
        return float(m.group(1)) if m else None
    r00,r01,r02 = g('R00'),g('R01'),g('R02')
    r10,r11,r12 = g('R10'),g('R11'),g('R12')
    r20,r21,r22 = g('R20'),g('R21'),g('R22')
    ident = (r00==1 and r01==0 and r02==0 and r10==0 and r11==1 and r12==0 and r20==0 and r21==0 and r22==1)
    if not ident:
        non_identity += 1
        if non_identity <= 5:
            print('NON-IDENTITY:', r00,r01,r02,r10,r11,r12,r20,r21,r22)
print('Non-identity count:', non_identity)