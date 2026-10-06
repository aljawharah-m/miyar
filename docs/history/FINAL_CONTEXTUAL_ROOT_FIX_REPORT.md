# Mi'yar 1.0 — V15.4 Contextual Root-Cause Hardening Report

## Scope
This release implements the 38-item detector/fusion hardening checklist supplied after the V15.3 long-text acceptance run. The design goal is not to hide errors; it is to stop presenting keyword/count symptoms as independent user-facing gaps when a more precise semantic root cause explains them.

## Architectural change
Previous public flow (simplified):

`keyword/count detectors -> user-facing findings -> light dedupe`

V15.4 public flow:

`alignment -> contextual relation tagging -> raw detector evidence -> root-cause fusion -> semantic dedupe -> ranked user-facing gaps`

Raw signals are retained in `raw_issues` for trace/debug use. The public `issues` array contains fused root causes. `diagnostics` reports `raw_signal_count`, `root_issue_count`, and `suppressed_signal_count`.

## Implemented fixes
- Condition framing: prevents `إذا قيل/ورد/ذكر/جاء/ترجم...` and ordinary hypothetical English `If ...` from being treated as standalone semantic gates without context.
- True condition gates: dedicated root diagnosis when an actual acceptance/publication condition is removed or inverted.
- Negation/exceptions: predicate-aware fusion; `لا ... إلا` is treated as an exclusivity construction rather than separate negation+exception noise.
- Ruling degree: claim-linked permission/obligation/recommendation/prohibition comparisons instead of paragraph-wide word bags.
- Quantities: lexical `one/one of/no one` filtering, asserted-value vs mentioned-bad-example distinction, contextual threshold/cardinality logic, and Arabic ordinal clock-hour normalization.
- References: bracket IDs and verse locator changes are root reference issues, separated from generic quantity mismatches; source-fabrication policy changes are explicit.
- Terminology: semantic duplicate suppression and bundled relation reversal for multi-term paragraphs.
- Scope/uncertainty: quantifier/generalization and probability->certainty receive higher-priority root diagnoses.
- Relations: dedicated comparison-direction, event-order, causality, AND/OR/cardinality, actor/responsibility and source-attribution roots.
- Units/time: unit equivalence and AM/PM changes are separated from generic number mismatches.
- Ambiguity/abstention: pronoun ambiguity is local Human Review evidence; it does not downgrade a document that also contains supported critical errors.
- Meta/quoted examples: number/ruling logic is made conservative when values or labels are mentioned as examples of what *not* to translate.
- Fusion/dedup: exact, semantic and same-root suppression is segment-local. Specific roots suppress their generic symptoms.
- UI: root issues are ranked by severity + semantic priority. The evidence expander reports how many raw signals were fused/suppressed. Mirror-of-Meaning uses the strongest root rather than merely the first detector hit.
- Safe correction policy remains conservative; no broad generative rewriting was introduced.

## Acceptance result on the user's long stress case
- Alignment: `hierarchical_paragraph_1to1`
- Aligned blocks: **45 Arabic ↔ 45 English**
- Decision: **critical / not ready for publication**
- Raw detector evidence: **180**
- User-facing root issues after fusion: **61**
- Suppressed duplicate/dependent signals: **119**
- Generic user-facing symptom types remaining in this acceptance case (`condition`, `negation`, `exception`, `prohibition`, `permission`, `obligation`, `quantity`, `generalization`, `narrowing`, `scope_omission`): **0**

The count 61 is intentionally not forced to 45: several aligned paragraphs contain multiple independent planted errors (for example event-order + causality, or amount + AM/PM). The goal is one issue per semantic root, not one issue per paragraph.

See:
- `evaluation/USER_LONG_STRESS_V15_4_ACCEPTANCE.json`
- `evaluation/USER_LONG_STRESS_V15_4_ROOT_ISSUES.txt`

## Regression and release evidence
- Pytest: **226/226 passed** (199 previous tests + 27 new contextual/root-fusion regression and unseen-formulation tests)
- Synthetic benchmark: Precision **1.000**, Recall **1.000**, F1 **1.000**, FPR **0.000**, Critical Error Recall **1.000**
- Adversarial development set: **48/48** expected classifications
- Jury stress: **37/37**
- Release smoke: **16/16**
- Long-text injected classes: **7/7**
- Repeatability: **200/200** deterministic comparisons
- Source audit during release-check: **0 errors** (6,236 Quran locator rows; 152 terminology checks)
- `python -m compileall`: passed

These are bundled/synthetic development checks and must not be presented as independent real-world validation.

## Optional semantic baseline limitation in this build environment
`evaluation/run_baselines.py` could not execute the semantic-AI-only baseline here because the optional local semantic model was unavailable in this runtime. The script exits explicitly with:

`Semantic AI model is not available. Run scripts/preflight.py first.`

This is recorded as an environment limitation, not as a passing baseline. Run it on the deployment machine after the local embedding model is available.

## Main changed files
- `core/contextual_semantics.py` — new contextual/root relation layer
- `core/rules.py` — narrowed surface detectors and contextual number/condition handling
- `core/engine.py` — root-cause fusion, diagnostics, local abstention policy, root ranking
- `app.py` — root ranking + fusion diagnostics in the evidence details
- `tests/test_v15_4_contextual_root_fusion.py` — 27 new regression/unseen tests
- acceptance artifacts under `evaluation/`
