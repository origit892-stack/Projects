import os
import subprocess

def mask(v):
    v = (v or "").strip()
    return "len=%d" % len(v)

# 1) current shell environment
env_hits = []
for k, v in os.environ.items():
    if "ROBLOX" in k.upper() or "OPEN_CLOUD" in k.upper():
        env_hits.append("%s=<%s>" % (k, mask(v)))
print("ENV_HITS=%d" % len(env_hits))
for h in env_hits:
    print("  " + h)

# 2) .env / credential files in likely roots (names only + presence of key vars)
roots = [
    "/Users/Ori/Documents/Projects/BunkerGame",
    "/Users/Ori/Developer/roblox-assets",
    "/Users/Ori/Developer/roblox-cube",
    os.path.expanduser("~"),
]
seen = set()
candidates = []
for root in roots:
    for base, dirs, files in os.walk(root):
        # keep walk shallow in home
        if base.startswith(os.path.expanduser("~")) and base.count(os.sep) - os.path.expanduser("~").count(os.sep) > 2:
            dirs[:] = []
            continue
        if any(part in base for part in ("/.git/", "/node_modules/", "/backups/", "/.venv/", "/Library/")):
            continue
        for f in files:
            low = f.lower()
            if low == ".env" or low.startswith(".env.") or "credential" in low or ("roblox" in low and low.endswith((".json", ".txt", ".env", ".key", ".yaml", ".yml", ".toml"))):
                p = os.path.join(base, f)
                if p in seen:
                    continue
                seen.add(p)
                candidates.append(p)

print("CANDIDATE_FILES=%d" % len(candidates))
key_var_names = ("ROBLOX_OPEN_CLOUD_API_KEY", "ROBLOX_CREATOR_USER_ID", "api_key", "apikey")
for p in candidates:
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read(200000)
    except Exception:
        print("  %s (unreadable)" % p)
        continue
    hits = []
    for line in content.splitlines():
        up = line.upper()
        if any(kv.upper() in up for kv in key_var_names) and "=" in line:
            val = line.split("=", 1)[1].strip().strip('"').strip("'")
            hits.append(mask(val))
    if hits:
        print("  %s -> %s" % (p, ",".join(hits)))
    else:
        print("  %s (no roblox key vars)" % p)

# 3) keychain: ALL accounts under the two service names (values masked)
for svc in ("ROBLOX_OPEN_CLOUD_API_KEY", "ROBLOX_CREATOR_USER_ID",
            "roblox-assets-open-cloud", "roblox-assets-creator-user-id"):
    r = subprocess.run(["security", "find-generic-password", "-s", svc, "-g"],
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if r.returncode != 0:
        continue
    # parse acct + length of secret (never print the secret)
    import re
    accts = re.findall(r'"acct"<blob>="([^"]*)"', r.stdout)
    print("KEYCHAIN svc=%s accounts=%s" % (svc, accts if accts else ["<none>"]))

# 4) config dirs
for d in ("~/.roblox-assets", "~/.config/roblox-assets", "~/.argon", "~/.roblox"):
    p = os.path.expanduser(d)
    if os.path.isdir(p):
        try:
            entries = os.listdir(p)
            print("DIR %s -> %s" % (d, ",".join(entries)[:200]))
        except Exception as e:
            print("DIR %s ERR %s" % (d, e))
print("DILIGENCE_DONE")