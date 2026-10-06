# Long-text analysis

Mi'yar accepts up to 12,000 characters per field. For long text, the critical invariant is **locality**: a correct marker in sentence A must not mask an error in sentence B.

When both sides split into the same number of sentence-like units, the current engine aligns them positionally and runs structural markers, quantities, terminology, local semantic heuristics, and Quran/Hadith recognition per unit. Every local finding carries `segment_index`. Document-level attribution/version checks remain global.

If unit counts differ, Mi'yar does not invent an alignment; it falls back to conservative document-level analysis and may route uncertain cases to review.

The synthetic long-passage stress test injects seven distributed gap classes and confirms all seven are detected without the former cross-sentence issue explosion.
