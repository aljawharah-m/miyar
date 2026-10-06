# Mi’yar 1.0 — Current Development Quality Report

## Current shipped evidence
- Regression: **348/348 passed**.
- Development benchmark: n=130, Precision/Recall/F1=1.0, FPR=0.0; **synthetic development evidence**.
- Repeatability: **200/200** comparisons, 0 failures.
- Adversarial: **48/48**.
- Jury stress: **37/37**.
- Release smoke: **16/16**.
- Long-text stress: **7/7** injected gap classes.
- Sacred-source audits: **62,490 deterministic checks** = 62,360 Quran + 130 Hadith.
- Reviewer workload stress: **175 raw signals → 59 root findings**, 66.3% reduction before display.
- Offline deterministic profile: median ~395ms, p95 ~431ms, peak RSS ~98.7 MiB in the measured environment.

## Safety evidence
- Local recognition != live verification.
- Provider failure/empty payload does not create Verified.
- Ambiguous sacred text remains ambiguous instead of guessed.
- Synthetic IDs do not trigger external calls.
- Human review/abstention is retained for insufficient evidence.

## Boundaries
These are development/audit results, not independent field accuracy or universal religious correctness. See `LIMITATIONS.md`.

## Reproduce
```powershell
python scripts/judge_verify.py
python scripts/release_check.py
```
