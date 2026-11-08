import json
d = json.load(open('/Users/Ori/Documents/Projects/BunkerGame/.director/tasks/research-spawn-platforms.json'))
r = d.get('result') or d.get('handoff') or ''
if isinstance(r, dict):
    r = json.dumps(r)
i = r.find('RECOMMENDATION')
print(r[max(0, i - 300): i + 3000] if i >= 0 else r[-3000:])