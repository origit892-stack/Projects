# Objective: File Smoke — 4 Artifacts in Isolated Sandbox

## Source of request
User request file (treated as the user's execution request):
/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/user-request.md

## Objective
Perform a full implementation, autonomously until verified completion, creating exactly four artifacts inside this sandbox directory ONLY:

/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work

Create the `work` directory if it does not exist.

## Required artifacts (exact contents, no extra characters)
1. `backend.txt` — exact content: `BACKEND=READY`
2. `frontend.txt` — exact content: `FRONTEND=READY`
3. `tests.txt` — exact content: `TESTS=PASS`
4. `release.txt` — exact content: `RELEASE=READY`

## Dependency ordering (mandatory)
- `backend.txt` and `frontend.txt` are independent workstreams and MAY be executed in parallel.
- `tests.txt` MUST be created only after BOTH `backend.txt` and `frontend.txt` are complete.
  Before creating `tests.txt`, the executing worker MUST read `backend.txt` and `frontend.txt` and verify their exact contents (`BACKEND=READY` and `FRONTEND=READY`) before writing `tests.txt`.
- `release.txt` MUST be created only after `tests.txt` has been created successfully.
  Before creating `release.txt`, the executing worker MUST read and verify all three previous artifacts (`backend.txt`, `frontend.txt`, `tests.txt`) with their exact contents before writing `release.txt`.

## Hard constraints
- Do NOT modify or create anything outside the sandbox directory above.
- Do NOT modify the user-request.md, before.txt, bootstrap.txt, or continue-output.json files in the parent frontdoor directory.
- Verification must be real: read back each file's bytes and compare to the exact expected content before declaring PASS.
- A worker must not claim PASS without performing the read-back verification.

## Completion criteria (all must hold)
- All four files exist in the sandbox `work` directory.
- Each file's content exactly matches the required string (verified by read-back, e.g., `cat`/`od`/byte comparison).
- The dependency ordering above was actually followed (tests verified backend+frontend before writing; release verified all three before writing).
