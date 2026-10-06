# Mi'yar V15.12 — Religious Acceptance Hardening

## Trigger
A 27-case public-site religious acceptance set exposed real gaps in V15.11: direct ruling-grade changes were falling to generic signals; a numbered safe case produced a quantity false positive; simple Quran locator changes were not always promoted to source integrity; several source-fabrication, synthetic-provenance, condition, Zakat numeric, epistemic, and abstention formulations were under-detected.

## Root fixes
- Direct classical ruling transfer now works through the backward-compatible `modality_shift` path while public taxonomy/subtype classifies it as religious ruling transfer.
- Added Arabic `جائز` as a permission marker; English `mandatory` as obligation; `not preferred` as disliked; `permitted` as permission.
- `not preferred` is treated atomically so its internal `not` does not create a duplicate negation alert.
- Quran locator comparison accepts `Al-Baqarah, verse N` and compares a single asserted target verse.
- Source fabrication catches `another/alternative reliable-looking religious reference` after verification failure.
- Synthetic TEST/MOCK/DEMO/ABC identifiers cannot be presented as verified authentic sources without a provenance finding.
- Target-side invented consensus and invented prohibition receive unsupported-addition roots; religious impact is only elevated when religious context is explicit.
- Direct condition removal (`accepted whether or not...`) maps to `condition_gate_shift`.
- Zakat 2.5%→25% maps to numeric taxonomy with high religious impact; ordinary 750→700 stays numeric with no direct religious impact.
- `proves ... with certainty` is recognized as epistemic certainty escalation.
- Source-conflict/context-unclear → definitive answer maps to abstention failure.
- Leading numbered-list prefixes are excluded from quantity semantics; lexical `one of the foundations` no longer creates a numeric false positive.

## 27-case acceptance result
- 27 aligned cases
- 22 intentionally bad cases → 22 public root findings
- 5 intentionally safe cases (4, 8, 10, 26, 27) → 0 findings
- Taxonomy: 6 religious semantic, 6 general semantic, 3 logic/numeric, 4 source integrity, 3 epistemic
- Religious impact: 14 high, 8 none

## Regression
- `308 passed`
- New suite: `tests/test_v15_12_religious_acceptance_27.py` → 11 passed

## Boundary preserved
`forbidden` alone in a generic sentence is not automatically classified as religious. A religious-impact elevation requires explicit religious context or a clearly religious target-side claim. This prevents reintroducing the over-classification fixed in V15.8–V15.11.
