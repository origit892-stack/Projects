import json, sys
path = sys.argv[1]
with open(path) as f:
    data = json.load(f)
print('Valid JSON: YES')
print('Root ClassName:', data.get('ClassName'))
print('Root Name:', data.get('Name'))
children = data.get('Children', [])
print('Total children:', len(children))
mp = [c for c in children if c.get('ClassName') == 'MeshPart']
print('MeshParts:', len(mp))
missing_meshid = [c['Name'] for c in mp if not c.get('Properties', {}).get('MeshId')]
missing_pos = [c['Name'] for c in mp if not c.get('Properties', {}).get('Position')]
missing_size = [c['Name'] for c in mp if not c.get('Properties', {}).get('Size')]
missing_cframe = [c['Name'] for c in mp if c.get('Properties', {}).get('CFrame')]
print('Missing MeshId:', len(missing_meshid))
print('Missing Position:', len(missing_pos))
print('Missing Size:', len(missing_size))
print('Still have CFrame (should be 0):', len(missing_cframe))
# sample one part
if mp:
    p = mp[0]['Properties']
    print('Sample part:', mp[0]['Name'])
    print('  MeshId:', p.get('MeshId'))
    print('  Position:', p.get('Position'))
    print('  Size:', p.get('Size'))
    print('  Material:', p.get('Material'))
    print('  Color:', p.get('Color'))
    print('  Transparency:', p.get('Transparency'))