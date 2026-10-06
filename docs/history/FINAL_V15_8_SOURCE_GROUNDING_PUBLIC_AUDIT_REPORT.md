# Mi’yar V15.8 — Source Grounding, Taxonomy & Public Audit

## Product boundary
**مِعيار لا يصدر أحكامًا شرعية جديدة؛ بل يحمي الحكم والمصطلح والدليل الموجود أصلًا من التحريف أثناء انتقاله بين اللغات.**

The engine evaluates transfer safety, not the independent religious correctness of the original ruling.

## Root fixes
- Public five-class taxonomy plus a more specific `issue_subtype`.
- `religious_impact` is separated from technical error type and includes an explicit reason.
- Technical modality is no longer automatically treated as a religious ruling.
- Synthetic IDs are local integrity data, never external religious evidence.
- Live reference verification and user-translation verification are separate states.
- Every public root carries evidence provenance: detector, aligned pair, spans, external source metadata if used, timestamp, confidence, and suppression field.
- Conflicting source evidence forces Human Review; Mi’yar does not auto-arbitrate source conflicts.
- Public UI exposes taxonomy, impact, impact reason, system boundary, taxonomy breakdown, verification scope, and source attribution metadata.

## Provider attribution
QuranEnc metadata retains translation key, upstream version and last update when available, retrieval timestamp and URL. HadeethEnc keeps version only when upstream exposes it; otherwise `source_version=None`.

## Claims policy
Any 1.000 benchmark score is explicitly labelled as synthetic development evidence, not independent religious validation and never “100% religious accuracy”.
