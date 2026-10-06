# V7 Acceptance Report

V7 addresses the root causes found by the mixed-document acceptance test rather than patching individual examples.

## Root fixes

1. **Segment-aware deduplication** — identical modality errors in separate sentences are preserved independently.
2. **Occurrence-aware term alignment** — repeated English surface forms are matched to the corresponding Arabic term by local position before correction. This prevents `الصدقة ... الزكاة` from replacing the wrong `charity`.
3. **Context-aware fasting terminology** — `fast` / `the fast` are recognized as valid renderings of `الصوم/الصيام` in context.
4. **Scope classification** — `only for ...` is treated as an added restrictive qualifier, not a generalization.
5. **Protected Quranic omission** — omission of `القيوم` is surfaced as a high-impact missing meaning.

## Exact mixed-document acceptance result

The 20-segment acceptance document returns **19 issues** with the intended sentence-local behavior. Key assertions:

- segment 18 corrects only the second `charity`: `Charity is recommended and Zakat is obligatory.`
- segment 19 reports both missing condition and permission→obligation drift, while `break the fast` does not trigger a fasting terminology false positive.
- segment 16 reports `only for scholars` as an added restrictive scope.
- segment 1 reports both lost exclusivity and omitted `القيوم`.
- no document-wide number/condition pooling is used.

## Verification

- `pytest`: **128 passed**
- source audit: **PASS**, Quran locator **6236 rows**, terminology checks **152**, 0 errors
- release smoke: **16/16 PASS**
- jury stress: **37/37 PASS**
- synthetic benchmark: TP=63, FP=0, TN=67, FN=0
- adversarial: 48 cases, FP=0, FN=0
- repeatability: 200/200 comparisons repeatable
- long-text stress: all 7 injected gap classes detected
- final offline release check: **PASS**

These are development tests, not independent field validation. Live provider/model connectivity remains deployment-machine preflight work.
