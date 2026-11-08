## Session Transcript (2026-09-04) — Gradio HF Space Masked Exceptions

**Project:** `/Users/Ori/Documents/Projects/BunkerGame`  
**API Space:** `ThomasSimonini/Roblox-3D-Assets-Generator-v1`  
**Client Used:** `gradio_client.Client()` (latest package from PyPI)  

---

## Failure Mode — Masked AppError

### Raw Error Output

```
gradio_client.exceptions.AppError: The upstream Gradio app has raised an 
exception but has not enabled verbose error reporting. To enable, set 
show_error=True in launch().
```

### Why This Can't Be Fixed in Code

- The deployed Hugging Face Space does not allow `show_error=True`
- This is a deployment control, not a client-side configuration
- Without verbose errors, the backend throws uninstrumented exceptions that bubble up to the client layer immediately  
- The client library's result fetch (`future.result()`) re-throws the exception and aborts

---

### Error Transcript from `poll_preprocess()` Function

**First Attempt:**
```
During handling of the above exception, another exception occurred:

...
>>> raise self._exception  # ← gradio_client client.py line 1568
...
File ".../_inner", predictions = _predict(...)
    raise AppError(...)
```

The client wraps the upstream error in its own `AppError` and bubbles up without additional details.

---

## Retry Pattern Encoded in Session Scripts

The session wrote several script variants to handle this failure mode:

### Script 1 — `run_generation_real.py` (Failed)

**Approach:** Implemented retry loops with exponential backoff  
**Failure:** Used `e[0]` syntax to inspect exception, causing `TypeError` because Python Exception objects are not lists. Fixed by switching to `str(e).lower()` and filtering message substrings for keywords like "queue", "processing", "backend".

### Script 2 — `test_rest.py` (Alternative Fallback)

**Approach:** Pure raw HTTP POST requests bypassing `gradio_client` entirely  
**Status:** Written as fallback but not executed during session due to other scripts failing first.

---

## Retry Timing Decisions from Session

- First `poll_preprocess()`: waited 15 seconds between attempts (first error)
- Subsequent retries: used exponential backoff `between * (2 ^ attempt)`  
- Max attempts allowed: 8–10 per endpoint call  
- If all retries exhausted without success, raised final exception with summary

---

## Environment Variables Required for Session Python

These settings are mandatory when running the client code in system Python (no venv):

```bash
export HF_HOME=/Users/Ori/.cache/huggingface
export HOME=/Users/Ori
```

Without these, Hugging Face cache errors occur due to path mismatches.

---

## Session Summary

The AI 3D generation pipeline failed **before producing any assets** because:
1. The `/preprocess` endpoint threw an uninstrumented exception  
2. `gradio_client.Client.predict()` immediately aborts and re-throws without retry
3. Backend error diagnostics are unavailable  
4. No raw HTTP fallback (until `test_rest.py` written) was used

The blocker is a deployment limitation of the public space, not a client-side bug that can be patched on the caller side.

---

## Reference Artifacts from Session

- `/tmp/run_gen_real.log` — truncated after retry loop exhaust  
- `/tmp/test_preprocess.log` — same failure mode  
- `/Users/Ori/Documents/Projects/BunkerGame/tools/ai_3d_pipeline/artifacts/old_military_ammo_crate_test/reference/input.png` — original reference image (2.24 MB)
- Script variants: `run_direct.py`, `generate_run.py`, `test_api_direct.py`, `test_rest.py`

---

## Recommendation for Future Sessions

When working with external Hugging Face Gradio Spaces:
1. Expect masked exceptions on long-running endpoints
2. Implement polling with retries, not fire-and-forget calls  
3. Use exponential backoff between attempts (5–20 seconds)
4. Have a raw HTTP fallback ready (requests.post to /gradio_api/api/predict/)
5. If all else fails, contact the space owner or check for model deployment issues

---

**Session ID:** `deleg_d56a0fba` (skill creation subagent)  
**Created:** 2026-09-04  
**Skill Path:** `/Users/Ori/Documents/Projects/skills/devops/remote-api/SKILL.md`
