#!/usr/bin/env python3
import csv, hashlib, os, pathlib, sys
backup_root = pathlib.Path(__file__).resolve().parents[1]
source_root = backup_root / "source"
manifest = pathlib.Path(__file__).resolve().parent / "FILE_MANIFEST.tsv"
def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(4 * 1024 * 1024)
            if not b: break
            h.update(b)
    return h.hexdigest()
failures = []
with manifest.open(encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        path = source_root / row["relative_path"]
        if row["entry_type"] == "file":
            if not path.is_file() or path.stat().st_size != int(row["bytes"]) or digest(path) != row["sha256"]:
                failures.append(row["relative_path"])
        elif row["entry_type"] == "symlink":
            payload = ("SYMLINK\0" + os.readlink(path)).encode("utf-8", errors="surrogateescape") if path.is_symlink() else b""
            if hashlib.sha256(payload).hexdigest() != row["sha256"]: failures.append(row["relative_path"])
        else:
            failures.append(row["relative_path"] + ": unsupported special entry")
if failures:
    print("FULL_GAME_BACKUP_VERIFY=FAIL")
    print("\n".join(failures[:100]))
    sys.exit(1)
print("FULL_GAME_BACKUP_VERIFY=PASS")
