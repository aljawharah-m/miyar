# Mi'yar AI Methodology — Gold Final

## Core thesis
A translation can be fluent and semantically similar overall while still changing one critical Islamic meaning invariant. Mi'yar therefore never treats fluency or embedding similarity as proof of correctness.

## What the AI actually does
Mi'yar uses a local multilingual sentence-transformer as an independent cross-lingual semantic-drift signal. It does not issue fatwas and does not decide religious correctness by itself.

The AI signal is fused with deterministic meaning invariants, Islamic terminology safeguards, Qur'an/Hadith recognition, trusted-source retrieval, abstention, and human review.

## Safety policy
- Semantic similarity is supporting evidence, not a calibrated confidence probability.
- A low similarity score does not create a standalone "meaning gap" in the UI.
- Low similarity without corroboration requests human review rather than inventing a diagnosis.
- High similarity never overrides a lost negation, condition, exception, ruling degree, number, attribution, or trusted-source conflict.
- If the model is unavailable, the safety core continues operating.
- The public 1.0 decision path does not depend on an external generative model or paid API.

## Performance
The model warms in the background while the user reads/types. Semantic AI and trusted-source retrieval run in parallel during analysis.

## Terminology precision
Mi'yar does not treat general semantic similarity as enough for sensitive terms. The terminology layer has three outcomes: accepted equivalent, risky flattening, and context-dependent review. Challenge-provided glossary rows are tracked separately from Mi'yar-curated conservative guards.

## Long passages
The public UI accepts up to 12,000 characters per side. Structural and terminology checks process the full strings. The semantic layer chunks long input into bounded passages and embeds every chunk under the public input limit, then aggregates the representation.
