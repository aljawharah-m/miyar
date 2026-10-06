# Benchmark v0.4 — Development + Ablation + External-Validation Gate

## Development set
130 synthetic development cases covering negation, exception, condition, omission/addition, ruling degree, sentence-local swaps, terminology precision, quantities, scope/provenance and multi-error passages.

Current deterministic development report is written by:

```powershell
python evaluation/run_benchmark.py
```

Metrics include Precision / Recall / F1 / FPR / Critical Error Recall.

## Ablation study

```powershell
python evaluation/run_ablation.py
```

This compares:
- structure rules only,
- terminology guard only,
- structure + terminology + scope/provenance,
- full Mi'yar without live sources or semantic AI.

Purpose: show that the value comes from layer composition, not a single regex list or dictionary.

## Semantic-AI-only baseline

After the local sentence-transformer is available:

```powershell
python scripts/preflight.py
python evaluation/run_baselines.py
```

This is the most important demo baseline for the claim **semantic similarity alone is not enough**.

## Additional regression evidence
- Jury stress.
- Adversarial set.
- Repeatability.
- Long-text stress.

## What these numbers do NOT prove
These datasets were created for engineering and regression. They do not constitute independent field accuracy.

For independent evidence, use `docs/EXTERNAL_VALIDATION_PROTOCOL.md` and do not publish field-accuracy claims until the template is completed by real reviewers.
