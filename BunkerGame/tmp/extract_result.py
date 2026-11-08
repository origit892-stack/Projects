import json
d = json.load(open('.director/results/research-obj-to-studio2.json'))
r = d.get('result','')
idx = r.find('ITEM 3')
print(r[idx:] if idx != -1 else r[-4000:])
