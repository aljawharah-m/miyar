# Mi’yar V15.11 — Target-side Religious Impact Completion

## Why this release exists
V15.10 correctly separated issue taxonomy from religious impact, but one long-stress finding was under-classified: the source prohibits unsupported additions generally while the English target explicitly permits adding **religious conclusions**. Religious impact must therefore inspect explicit target-side religious content as well as source-side context.

## Root fix
- `_religious_context()` now considers aligned target text/spans in addition to source text.
- Strong target religious cues include explicit words such as `religious`, `Islamic`, `fatwa`, `scholar`, and established Islamic terminology.
- This does **not** reintroduce the old broad heuristic: generic technical modality such as `must`, `should`, `لا يجوز`, or administrative rules does not by itself create religious impact.
- `unsupported_addition_policy_shift` gets a dedicated explanation when the target adds an explicit religious conclusion absent from the source.

## Long-stress acceptance
- Root issues: **58** (unchanged)
- Taxonomy: **6 religious-semantic / 25 general-semantic / 14 logic-numeric / 4 source-integrity / 9 epistemic** (unchanged)
- Direct religious impact: **19** (was 18)
- The only intended reclassification is the target-side explicit `religious conclusions` addition.

## Regression protection
Added `tests/test_v15_11_target_religious_impact.py`:
1. Explicit target-side religious addition => `religious_impact=high`.
2. General unsupported addition without religious target content => `religious_impact=none`.

## Verification
- `pytest`: **297 passed**
- Benchmark: Precision/Recall/F1 **1.000**, FPR **0.000** on the synthetic development benchmark only.
- Category benchmark: all configured slices **1.000** on the synthetic development set.
- Adversarial: **48/48**
- Jury: **37/37**
- Release smoke: **16/16**
- Long-text stress: **7/7 injected gap classes detected**
- Repeatability: **200/200**
- Source audit: **0 errors**
- Source metadata audit: **0 errors**
- Attribution audit: **0 errors**
- Synthetic-ID audit: **external_calls=0**

These are development/regression results, not independent religious validation.
