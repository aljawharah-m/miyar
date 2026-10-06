# Mi'yar V15.2 — Alignment Root Fix Report

## What changed

This patch targets the long-document alignment failure observed in stress testing while preserving the already-hardened semantic detectors in V15.2.

### 1. `core/alignment.py`
- Replaced proportional chunk partitioning for unequal sentence counts with monotonic dynamic-programming alignment.
- Supports local 1→1, 1→2, 2→1, Arabic-only omission, and English-only addition recovery.
- Added deterministic bilingual alignment anchors for high-value concepts such as Zakat, Tawhid, Wudu, Quran/Hadith references, rulings, conditions, review/publication, confidence, and evidence.
- Added numeric and explicit reference-ID anchors.
- Preserves strict 1:1 sentence alignment when both sides already have equal sentence counts, avoiding unnecessary reshuffling.
- Isolates local additions/omissions instead of shifting every later sentence.
- Fixed numbered-list markers such as `1.` so they remain attached to the following sentence and are not mistaken for quantities.

### 2. `tests/test_v15_2_root_hardening.py`
Added regression tests for:
- recovery after an extra English sentence,
- recovery after a missing English sentence,
- local split/merge punctuation differences without downstream alignment shift.

## Existing V15.2 protections preserved
The uploaded project already contained regression coverage for many requested root fixes, including:
- `أن` vs conditional `إن`,
- context-aware conditions,
- `ما لم`,
- `ليست` → positive polarity loss,
- `لا يجوز` ↔ permission reversal,
- `وجب` ↔ `may`,
- sentence-local ruling shifts,
- local number/quantity binding,
- ordinary `غسل` vs ritual `غُسل`,
- conservative safe corrections,
- no auto-rewrite for structural/ruling gaps,
- source/citation hardening and Quran-reference conflict checks.

These were not rewritten unnecessarily; the patch focuses on the root alignment defect that was contaminating them on long documents.

## Verification

### Pytest
- Before patch: **190 passed**
- After patch: **193 passed**
- Regressions: **0**

### Synthetic benchmark
- TP: 63
- FP: 0
- TN: 67
- FN: 0
- Precision: 1.000
- Recall: 1.000
- F1: 1.000
- FPR: 0.000
- Critical Error Recall: 1.000

### Adversarial development set
- 48 cases
- TP: 24
- FP: 0
- TN: 24
- FN: 0
- Precision/Recall/F1: 1.000
- FPR: 0.000
- Critical Error Recall: 1.000

### Jury stress
- 37 / 37 passed

### Long-text stress
- Passed
- 7 / 7 injected gap classes detected

### Repeatability
- 20 cases × 10 runs
- 200 comparisons
- 20/20 repeatable cases
- 0 failures

### Release smoke
- 16 / 16 passed

### Resource profile in this environment
- Linux, offline deterministic layers
- Median latency: ~500.8 ms
- P95 latency: ~1044.9 ms
- Max latency: ~1216.5 ms
- Python tracemalloc peak: ~0.456 MiB
- Process peak RSS: ~98.1 MiB

### Baselines
`evaluation/run_baselines.py` could not run in this environment because the optional semantic AI model is unavailable. The script itself was reached successfully and reported the missing model. Run `scripts/preflight.py` on the target machine and then rerun baselines when the configured local semantic model is available.

## Important evaluation note
The benchmark/adversarial/jury results are the project's synthetic development evidence and must not be presented as independent external validation.
