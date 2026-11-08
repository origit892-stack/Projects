import re
import subprocess

out = subprocess.run(
    ["security", "dump-keychain"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
).stdout

items = []
cur = None
for line in out.splitlines():
    if line.startswith("keychain:"):
        if cur:
            items.append(cur)
        cur = {"keychain": line.split('"')[1], "svc": None, "acct": None, "cdat": None, "mdat": None, "cls": None}
        continue
    if cur is None:
        continue
    m = re.search(r'0x00000007 <blob>="([^"]*)"', line)
    if m:
        cur["svc"] = m.group(1)
        continue
    m = re.search(r'"acct"<blob>="([^"]*)"', line)
    if m:
        cur["acct"] = m.group(1)
        continue
    m = re.search(r'"cdat"<timedate>=0x[0-9A-Fa-f]+ +\"([^\"]*)', line)
    if m:
        cur["cdat"] = m.group(1)
        continue
    m = re.search(r'"mdat"<timedate>=0x[0-9A-Fa-f]+ +\"([^\"]*)', line)
    if m:
        cur["mdat"] = m.group(1)
        continue
    m = re.search(r'^class: "(.*)"$', line.strip())
    if m:
        cur["cls"] = m.group(1)
if cur:
    items.append(cur)

# sort by mdat desc
def keyf(it):
    return it.get("mdat") or it.get("cdat") or ""

items.sort(key=keyf, reverse=True)
print("TOTAL_ITEMS=%d" % len(items))
for it in items[:25]:
    print("%s | kc=%s | svc=%s | acct=%s" % (
        it.get("mdat") or it.get("cdat"),
        it["keychain"].split("/")[-1],
        (it.get("svc") or "")[:60],
        (it.get("acct") or "")[:40],
    ))
PY = None