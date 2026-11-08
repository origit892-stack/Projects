---
name: remote-api
category: devops
description: Handle masked exceptions from deployed HF Spaces; implement retry loops with exponential backoff; provide raw HTTP fallback patterns when client libraries abort silently due to uninstrumented backend errors.
tags: [api, gradio, huggingface, masked-errors, retries, fallbacks]
author: curator-managed
created: 2026-09-04
---

# Remote API with Masked Exceptions — DevOps Skill

**Purpose:** When querying external APIs (especially Gradio Spaces on Hugging Face) that throw backend exceptions without verbose error reporting, this skill provides patterns to keep working rather than aborting.

## When to Use This

You need this skill when:
- Calling `gradio_client.Client` predict() endpoints on a deployed space
- Receiving generic `AppError` or `Exception` with no details about the backend failure
- The deployed space cannot accept `show_error=True` (deployment limitation)
- Polling for results from long-running ML inference pipelines

## Known Problems — Encode Here

### 1. HF Space Backend Errors Are Masked

**Pattern:** The upstream Gradio app on a public Hugging Face Space throws exceptions that are not instrumented for verbose error reporting. `show_error=True` cannot be set on deployed spaces—it's a deployment control.

**Symptoms:**
```
gradio_client.exceptions.AppError: The upstream Gradio app has raised an exception 
but has not enabled verbose error reporting. To enable, set show_error=True in launch().
```

Because you cannot configure this flag post-deployment, the client aborts with no details about what the backend actually failed on (e.g., "image too large", "model out of memory", "processing queue full").

### 2. Silent Aborts During Long Polls

**Pattern:** When waiting for a long-running inference step (multiview synthesis, 3D reconstruction):
- The first call may fail with the above masked error
- The client immediately re-throws and doesn't continue polling
- You get no information about queue load or backend processing time

**Why:** `client.predict()` is synchronous and blocks until a response. If the upstream times out or throws, it bubbles up without retry logic built into the library.

## Retry Strategies That Work

Implement these patterns in your scripts:

### Pattern A — Fixed Wait with Type-Based Filtering

Don't blindly retry all exceptions. Filter on error message content to distinguish transient queue errors from real failures.

```python
import time, requests

def poll_with_wait(max_attempts=8, between=5):
    for attempt in range(max_attempts):
        try:
            result = api_call()
            if result and "output" in result:
                return True, result
        except Exception as e:
            err_str = str(e).lower()
            # Skip transient errors, continue polling
            if "queue" in err_str or "processing" in err_str or "backend" in err_str:
                retry_in = between * (2 ** attempt)  # exponential backoff
                print(f"  Transient error. Retry in {retry_in}s...")
                time.sleep(retry_in)
                continue
            # On real failure, log and propagate
            raise e
    # Exhausted attempts
    print("Max retries exhausted")
    raise Exception("API call failed after all retries")
```

### Pattern B — Polling Without Immediate Abort

For inference endpoints that take >10s:
- Call the API once
- Wait 10–20 seconds (let it process)
- Check for result or error
- If masked exception, sleep longer and retry

**Key:** Use a counter. On N retries without success, assume permanent failure.

### Pattern C — Fallback to Raw HTTP POST

When `gradio_client.Client` aborts, fall back directly to `requests.post()`:

```python
import requests, json, urllib.parse

BASE_URL = "https://space-name.hf.space/gradio_api/api/predict/"

def call_with_fallback(params, api_name):
    # Try gradio client first
    try:
        return gradio_client_client.predict(params, api_name=api_name)
    except Exception as e1:
        err_str = str(e1)
        if "masked" in err_str or "exception" not in err_str.lower():
            # Fallback to raw POST
            full_url = BASE_URL + api_name
            headers = {"Content-Type": "application/json"}
            payload = {"data": [params]}
            
            resp = requests.post(full_url, data=json.dumps(payload), 
                              headers=headers, timeout=300)
            if resp.status_code == 200:
                print("Raw POST fallback succeeded")
                data = json.loads(resp.text[:1500])
                return data.get('output', [])
            pass  # Still failed
    
    raise e1
```

## Session Artifacts as Evidence

This skill covers the session where `ThomasSimonini/Roblox-3D-Assets-Generator-v1`:
- Failed on all `/preprocess`, `/generate_mvs`, and `/make3d` calls
- Returned identical masked exceptions across 5+ retry attempts
- Could not progress because no real backend error could be diagnosed

**Files created during session:**
- `/tmp/run_gen_real.log` — truncated after masked abort
- `/tmp/test_preprocess.log` — same failure mode
- Script variants written to find a workaround: `run_direct.py`, `test_rest.py`

## Pitfalls to Avoid

### ❌ Don't assume client libraries will retry automatically

They don't. You must implement polls and backoff loops explicitly.

### ❌ Don't parse exception objects with indexing (`e[0]`)

Gradio's masked exceptions are Python objects, not subscriptable lists. This causes `TypeError: 'Exception' is not subscriptable`. Use `str(e)` to inspect message content.

### ❌ Don't wait forever on one endpoint

Max 8–10 attempts with exponential backoff is reasonable. Longer waits degrade throughput without guaranteeing success.

### ❌ Don't deploy your own space expecting client-side fixes

The solution is to configure your deployment for verbose errors, not patch the client library. Use `show_error=True` and proper exception instrumentation when you control the endpoint.

## Reference Implementation

See: `/Users/Ori/Documents/Projects/BunkerGame/tools/ai_3d_pipeline/run.py`
- Implements retry loops with 10s waits between attempts  
- Filters transient vs real errors by message content
- Provides summary at completion

## Related Skills

- `hermes-agent-skill-authoring`: For creating skills like this one in your repo
- `systematic-debugging`: When you hit a masked exception and need the full failure diagnostics

---

**Author Notes:** This skill was created in session ended 2026-09-04. Future sessions should preload it before attempting first-call API generation tasks on external HF Spaces.
