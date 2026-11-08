# BunkerGame Full-Game Recovery Backup Manifest

- **Timestamp:** `20260826_174739`
- **Reason:** Immutable recovery boundary immediately before the Director-authorized full greenfield rebuild of all current game content/implementation.
- **Source root:** `/Users/Ori/Documents/Projects/BunkerGame`
- **Backup root:** `/Users/Ori/Documents/Projects/BunkerGame/backups/full_game/20260826_174739_pre_full_greenfield_rebuild`
- **Source copy:** `/Users/Ori/Documents/Projects/BunkerGame/backups/full_game/20260826_174739_pre_full_greenfield_rebuild/source`
- **File count:** `1043`
- **Total source bytes:** `6179507194`
- **Special entries:** `0`
- **File manifest SHA-256:** `303f38b96f6411acddd19b878b17ca1396700847d67099872f3dcdcd44b51068`
- **Verification:** Every regular file was readable and SHA-256/size-identical in source-before, backup, and source-after inventories. Source did not change during capture.

## Included

Every file and symlink below `/Users/Ori/Documents/Projects/BunkerGame` at backup time, including source, Rojo configuration, docs, tools, Asset Factory/production registry, Environment Director, visual-QA evidence/workflows, historical place files, and prior `backups/new_bunker` recovery evidence.

## Exclusions

1. `/Users/Ori/Documents/Projects/BunkerGame/backups/full_game/**` only, to prevent recursive self-inclusion. No pre-existing valid full-game backup existed.
2. `/Users/Ori/Documents/Projects/.git/**` is outside the project root and is shared by unrelated sibling projects. It was not copied or modified. BunkerGame was an untracked subtree (`git ls-files -- BunkerGame` returned zero entries); exact Git root/HEAD/status/log evidence is retained in `evidence/GIT_EVIDENCE.txt`.
3. Volatile application process memory is not filesystem project content. Studio and OBS state at the boundary are recorded in `evidence/STUDIO_EVIDENCE.txt` and `evidence/OBS_EVIDENCE.txt`.

No other project-root content was excluded.

## Integrity evidence

- Per-entry relative/source/backup paths, byte sizes, source modes, types, and SHA-256 values: `evidence/FILE_MANIFEST.tsv`
- Re-verifier: `evidence/verify_backup.py`
- Copy method: `evidence/COPY_METHOD.txt`
- Git boundary: `evidence/GIT_EVIDENCE.txt`
- Studio boundary: `evidence/STUDIO_EVIDENCE.txt`
- OBS boundary: `evidence/OBS_EVIDENCE.txt`

## Exact restoration procedure

1. Stop Roblox Play, stop any active OBS recording, stop Rojo serving, and close or disconnect Studio from live synchronization.
2. Preserve this immutable backup directory. If desired, copy it to separate storage before restoration.
3. Clear macOS immutable flags on the *copy destination only if required*; do not unlock this recovery evidence in place.
4. Restore the snapshot while preserving `backups/full_game`:

   ```bash
   /usr/bin/rsync -a --delete --exclude='/backups/full_game/' --chmod=Du+w '/Users/Ori/Documents/Projects/BunkerGame/backups/full_game/20260826_174739_pre_full_greenfield_rebuild/source/' '/Users/Ori/Documents/Projects/BunkerGame/'
   ```

5. Reapply exact source modes from the `source_mode` column in `evidence/FILE_MANIFEST.tsv` if byte-for-byte forensic restoration is required. All game/source hashes are independent of the read-only backup flag.
6. Verify restored regular-file hashes against `evidence/FILE_MANIFEST.tsv` (the `source_path` column names restored locations), and independently verify this backup at any time with:

   ```bash
   python3 '/Users/Ori/Documents/Projects/BunkerGame/backups/full_game/20260826_174739_pre_full_greenfield_rebuild/evidence/verify_backup.py'
   ```

7. Run `/Users/Ori/.aftman/bin/rojo sourcemap default.project.json --output sourcemap.json` and `/Users/Ori/.aftman/bin/rojo build default.project.json --output <recovery-check>.rbxlx`.
8. Reconnect the correct Bunker Game place (`placeId 129695090105158`), inspect mapped hierarchy, run controlled Play QA, stop Play, and verify Studio returns to Edit-only.

## Acceptance marker

`FULL_GAME_BACKUP=PASS`
