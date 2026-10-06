# Mi'yar Final Root Alignment Fix

## Root cause fixed
The long-document failure was not primarily a detector failure. Arabic and English were segmented differently, especially around multi-line structured references. Once one side gained extra units, later sentences were compared with unrelated content.

## Architectural fix
- Added paragraph/block-first alignment for long documents.
- Added structured reference packet coalescing for `QURAN_REF`, `HADITH_REF`, and `SOURCE_ID` blocks.
- Paragraph boundaries are treated as hard editorial anchors when normalized block counts match.
- Sentence-level monotonic split/merge recovery remains the fallback for unstructured/unequal-block text.
- Added cached alignment signatures to keep fallback matching fast.
- Preserved explicit gap handling for insertion/deletion recovery.

## Linguistic false-positive fixes
- `ألا` is no longer folded into `إلا` before exception detection.
- Reporting-clause `إن` after verbs such as `قيل/قال/ذكر` is not treated as a condition.
- Metalinguistic frames such as `إذا قيل/إذا ورد/إذا ذكر` are not treated as semantic conditions on the underlying ruling.
- English lexical `one of the principles/...` is not treated as an invented numeric quantity.
- Arabic `لا أحد` / English `no one` are treated as negative pronouns, not quantity `1`.
- Generic number comparison uses distinct values to avoid repeated mentions creating fake quantity drift; anchored quantity bindings still preserve local number-to-concept checks.

## Windows/Streamlit startup hardening
Added `.streamlit/config.toml` with `fileWatcherType = "none"`. Mi'yar is text-only, so Streamlit no longer introspects lazy Transformers vision modules and emits irrelevant `torchvision` warnings during startup.

## Verification
- Pytest: **199 passed**
- Synthetic benchmark: Precision 1.000 / Recall 1.000 / F1 1.000 / FPR 0.000 / Critical Error Recall 1.000
- Adversarial: **48/48**
- Jury stress: **37/37**
- Release smoke: **16/16**
- Long-text stress: all **7/7** injected gap classes detected
- Repeatability: **200/200** comparisons stable

These benchmark results are development/synthetic evidence, not independent external validation.

## Exact user long-stress acceptance
- Arabic blocks after safe normalization: **45**
- English blocks after safe normalization: **45**
- Aligned pairs: **45**
- Alignment mode: `hierarchical_paragraph_1to1`
- Unmatched Arabic pairs: **0**
- Unmatched English pairs: **0**
- Deterministic-core findings on the intentionally corrupted translation: **157**
- Previous observed UI count from the broken alignment run: **219**

The important acceptance condition is not merely a lower count: post-reference content now stays aligned with its actual counterpart instead of drifting into unrelated paragraphs.

See:
- `evaluation/USER_LONG_STRESS_ACCEPTANCE.json`
- `evaluation/USER_LONG_STRESS_ALIGNMENT.txt`
