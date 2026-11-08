# BDS: Review Farming

Run with the terminal tool:

```bash
bds analyze farming
bds review farming
```

Then respond in Hebrew with:

1. Confirmed facts
2. Deterministic review results
3. PASS checks
4. WARN and FAIL checks
5. NOT_FOUND items that are not defects by themselves
6. Recommended next actions

Do not add risks that are absent from `bds review farming` unless you first inspect exact source ranges with `bds range` and cite them.
Do not modify files.
