import json, re

files = [
    '/Users/Ori/.continue/sessions/1cacee3b-5522-47a4-81dd-1599f27e64e4.json',
    '/Users/Ori/.continue/sessions/227a071d-74cb-4cc9-84bb-d4b7f9e97768.json',
]

for f in files:
    try:
        data = open(f).read()
    except Exception as e:
        print(f, 'ERR', e)
        continue
    count = data.count('3:313')
    print(f, 'occurrences:', count, 'size:', len(data))

# Try to find the detailed node tree for 3:313 in the session logs
# Look for JSON structures containing "3:313" as a node id with children
for f in files:
    try:
        data = open(f).read()
    except Exception:
        continue
    # Find tool outputs that contain 3:313 and look like figma node data
    # The figma_get_nodes response has structure: {"nodes":{"3:313":{"document":{...}}}}
    # Search for "3:313" followed by document structure
    for m in re.finditer(r'3:313', data):
        start = max(0, m.start() - 200)
        end = min(len(data), m.end() + 5000)
        chunk = data[start:end]
        if 'document' in chunk and ('children' in chunk or 'fills' in chunk):
            print('=== FOUND 3:313 node data in', f, 'at offset', m.start(), '===')
            print(chunk[:4000])
            print('=== END CHUNK ===')
            break