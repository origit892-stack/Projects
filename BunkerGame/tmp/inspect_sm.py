import json
d = json.load(open('/tmp/sm.json'))

def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if 'ArgonProof' in str(k):
                print('KEY:', path + '/' + str(k))
            walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + '[' + str(i) + ']')

walk(d)
print('--- top keys ---', list(d.keys())[:20])

# Find the MeshPart node specifically
def find_meshpart(o, path=''):
    if isinstance(o, dict):
        if o.get('Name') == 'ArgonProofMeshPart01' or o.get('name') == 'ArgonProofMeshPart01':
            print('=== MESH PART NODE ===')
            print(json.dumps(o, indent=2)[:1500])
            return True
        for k, v in o.items():
            if find_meshpart(v, path + '/' + str(k)):
                return True
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if find_meshpart(v, path + '[' + str(i) + ']'):
                return True
    return False

find_meshpart(d)