import json
d = json.load(open('/Users/Ori/Documents/Projects/BunkerGame/default.project.json'))
t = d.get('tree', {})
print('TREE KEYS:', list(t.keys()))
ws = t.get('Workspace')
print('WORKSPACE ENTRY:')
print(json.dumps(ws, indent=2)[:1200])