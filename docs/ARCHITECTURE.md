# Architecture — Mi’yar 1.0

```text
Arabic source + English translation
        │
        ├─► Local Semantic AI (multilingual embeddings)
        │       └─ semantic similarity / drift signal
        │
        ├─► Critical Meaning Invariants
        │       └─ negation / condition / exception / exclusivity / modality / numbers / attribution
        │
        ├─► Terminology Guard
        │       └─ accepted vs risky vs context-dependent equivalents; flattening / narrowing of sensitive Islamic concepts
        │
        ├─► Scope & Coverage Checks
        │
        ├─► Source Recognition
        │       └─ Quran / Hadith candidate locator
        │
        ├─► Trusted Reference Retrieval
        │       └─ QuranEnc / HadeethEnc / ICADB routing
        │
        ├─► Evidence Fusion
        │       └─ merge duplicates + rank severity + preserve lineage
        │
        ├─► Abstention Policy
        │       └─ insufficient evidence => human review
        │
        └─► Human Review + Audit Trail
```

## Design principle

**Semantic AI is intentionally not the sole judge.** A translation can keep a high global similarity score while losing one high-impact invariant. Mi’yar combines AI breadth with deterministic precision and trusted evidence.

## Release decision path

Mi’yar 1.0 keeps the public decision path reproducible: semantic AI, deterministic meaning checks, terminology safeguards, trusted-source retrieval, abstention, and human review. No external generative model can alter the release decision.

## Long-text behavior
Critical signals are occurrence-counted across the whole passage, terminology checks can return multiple independent findings, and all detected findings remain available in the result/audit trail.


## Mixed-document isolation
When Arabic and English split into the same number of review units, Mi'yar performs structural, quantity, terminology, and source-recognition checks per aligned unit. Findings carry `segment_index`. Cross-sentence counts are not allowed to cancel or create findings. If reliable positional alignment is unavailable, the engine falls back conservatively instead of pretending sentence correspondence.
