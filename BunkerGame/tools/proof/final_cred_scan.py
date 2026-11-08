import os
import subprocess

# 1) All keychain items mentioning roblox (svc/acct only, values never printed)
out = subprocess.run(
    ["security", "dump-keychain"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
).stdout
lines = out.splitlines()
hits = []
for i, l in enumerate(lines):
    low = l.lower()
    if "roblox" in low and ("svce" in low or "acct" in low):
        # print the attribute line with value masked
        masked = l.split("blob>=")[0] + "blob>=<masked>"
        hits.append(masked)
print("KEYCHAIN_ROBLOX_HITS=%d" % len(hits))
for h in hits:
    print("  " + h)

# 2) Shell profiles containing ROBLOX (masked values)
profile_files = [
    ".zshenv", ".zprofile", ".zshrc", ".zlogin",
    ".bash_profile", ".bashrc", ".profile",
]
found = []
for name in profile_files:
    p = os.path.expanduser("~" + name)
    if not os.path.isfile(p):
        continue
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                if "ROBLOX" in line:
                    masked = line.strip().split("=")[0] + "=<masked>"
                    found.append((name, n, masked))
    except Exception as e:
        found.append((name, -1, "ERR " + str(e)))
print("SHELL_PROFILE_ROBLOX_HITS=%d" % len(found))
for name, n, masked in found:
    print("  %s:%d %s" % (name, n, masked))
