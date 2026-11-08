import json, glob
from collections import Counter
c = Counter()
examples = {}
for f in glob.glob('/Users/Ori/Documents/Projects/BunkerGame/.director/detached/run-*.json'):
    try:
        d = json.load(open(f))
        s = d.get('status', '?')
        c[s] += 1
        if s not in examples:
            examples[s] = f
    except Exception:
        c['ERR'] += 1
print("STATUS COUNTS:", dict(c))
for s, f in examples.items():
    print(f"EXAMPLE {s}: {f}")