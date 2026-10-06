# Mi’yar V15.10 — Arabic UI Polish & Status Precision

## Scope
V15.10 is a presentation-semantic polish release built on V15.9. It does not change the detector/root-issue logic.

## Fixes
- Added Arabic count morphology for `فجوة`: one/two/3–10/11+.
- Replaced `4 فجوة` and `3 فجوة` with natural Arabic forms such as `4 فجوات` and `3 فجوات`.
- Reworded live-reference status from a heavy/ambiguous phrase to: `لم يكتمل تحقق خارجي حي يمكن الاعتماد عليه في هذا الفحص`.
- Taxonomy summary labels are now grammatically polished category labels: `دلالية دينية`, `دلالية عامة`, `منطقية/رقمية`, `مرجعية`, `معرفية`.
- Preserved the V15.9 distinction between internal reference matching and external live verification.
- Preserved mixed-reference provenance: real/structural reference changes remain distinct from TEST/ABC synthetic identifiers.

## Verification
- pytest: 295/295 passed.
- Synthetic development benchmark: Precision/Recall/F1 = 1.000, FPR = 0.000.
- Category benchmark: terminology/rulings/references/numbers = F1 1.000 on the synthetic development set.
- Adversarial: 48/48.
- Jury stress: 37/37.
- Release smoke: 16/16.
- Long-text stress: 7/7 injected classes detected.
- Repeatability: 200/200 comparisons.
- Source audit: 0 errors.
- Source metadata audit: 0 errors.
- Attribution audit: 0 errors.
- Synthetic-ID audit: external_calls = 0.

## Important interpretation
These metrics are development evidence on synthetic/internal test sets, not independent religious validation. Mi’yar evaluates transfer safety and does not issue an independent fatwa or certify the original ruling as religiously correct.
