# Mi'yar V15.15 — Code Freeze Report

V15.15 is the submission freeze candidate after deep sacred-text red-team hardening.

## Root fixes added after V15.14
- Single-pair global findings inherit their actual aligned source/translation context before religious-impact classification and root fusion.
- Explicit Prophetic-Hadith context can fuse multiple surface symptoms into one sacred semantic root.
- Source-fabrication detection covers multiple Arabic failed-verification/prohibition formulations and multiple English alternative/plausible/substitute-source formulations.
- A direct source-text contradiction of `الله أحد` into one-among-many/several deities is detected without requiring a live provider.
- When a live trusted-reference contradiction exists, it suppresses the equivalent local sacred reversal so the public UI keeps one root finding.

## Verification completed
- Pytest: 322/322 passed after adding five new regression tests.
- Synthetic development benchmark: Precision 1.0, Recall 1.0, F1 1.0, FPR 0.0. This is development evidence, not independent religious validation.
- Synthetic adversarial: 48 cases, no mistakes.
- Jury stress: 37/37.
- Release smoke: 16/16.
- Long-text stress: 7/7 injected classes detected.
- Repeatability: 200/200 comparisons, zero failures.
- Category-sliced synthetic benchmark: all included slices F1 1.0/FPR 0.0.
- Source audit: 6236 Quran locator rows; zero audit errors.
- Source metadata, attribution, synthetic-ID and documentation audits: PASS.
- Public UI leak scan and secret scan: PASS.
- Additional unseen sacred red-team: correct Quran/Hadith paraphrases remained clean; altered polarity, sacred exclusivity, hadith directive reversal and source-fabrication variants were detected.

## Safety boundary
No NLP system can guarantee correctness for every possible formulation across all Quran/Hadith-related text. Mi'yar therefore remains a pre-publication safety gate: trusted-source evidence is used when available, provider failure never becomes fabricated verification, and unresolved cases remain subject to human review.
