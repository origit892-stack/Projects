# Acceptance Criteria: research-worldmanifest-gate (focused)

PASS requires:
1. The validation function name + line in WorldManifest.luau.
2. The runtime call site (file + line) where it is invoked at server start.
3. A HARD_GATE / SOFT_CHECK / UNKNOWN classification.
4. 3-5 quoted lines proving the classification (how the result is used: error/abort vs
   warn/log).
5. No file modified (read-only).

FAIL if the classification is missing or unsupported by quoted lines, or any file changed.
