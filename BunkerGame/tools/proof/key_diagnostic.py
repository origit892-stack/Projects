import os
import string
import subprocess

user = os.environ.get("USER", "")


def read(svc):
    r = subprocess.run(
        ["security", "find-generic-password", "-a", user, "-s", svc, "-w"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    if r.returncode != 0:
        return None
    return r.stdout


key_raw = read("ROBLOX_OPEN_CLOUD_API_KEY")
cid_raw = read("ROBLOX_CREATOR_USER_ID")


def describe(label, raw):
    if raw is None:
        print("%s: MISSING" % label)
        return
    stripped = raw.strip()
    lead_ws = len(raw) - len(raw.lstrip())
    trail_ws = len(raw) - len(raw.rstrip())
    classes = {
        "upper": sum(c.isupper() for c in stripped),
        "lower": sum(c.islower() for c in stripped),
        "digit": sum(c.isdigit() for c in stripped),
        "symbol": sum(not c.isalnum() for c in stripped),
    }
    print("%s: raw_len=%d stripped_len=%d lead_ws=%d trail_ws=%d classes=%s" % (
        label, len(raw), len(stripped), lead_ws, trail_ws, classes,
    ))
    # first 2 / last 2 chars only (minimal, non-reversible for short keys)
    if len(stripped) >= 6:
        print("%s: head2=%r tail2=%r" % (label, stripped[:2], stripped[-2:]))
    # validity heuristics (never print the value)
    print("%s: all_alnum=%s is_digit=%s" % (
        label, stripped.isalnum(), stripped.isdigit(),
    ))


describe("API_KEY  ", key_raw)
describe("CREATOR_ID", cid_raw)
