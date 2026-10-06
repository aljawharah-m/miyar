# Mi'yar 1.0 — V15.14 Sacred Text Root Hardening

## Purpose
Harden Quran/Hadith review so source recognition, religious impact, root-cause fusion, and live-reference evidence operate as one evidence chain rather than isolated layers.

## Root fixes
- Propagate recognized source kind (`quran` / `hadith`) into each finding in the same aligned segment.
- Recognized Quran/Hadith findings now receive religious-impact context even when the source text does not literally contain words such as “Quran” or “Hadith”.
- Generic named-surah/ayah reference drift is classified as `SOURCE_INTEGRITY`, not numeric drift.
- Source-fabrication detection covers `reference`, `source`, `hadith source`, and Quran/religious source wording.
- Trusted-reference contradiction checks compare the user translation to retrieved QuranEnc/HadeethEnc evidence and collapse multiple surface symptoms into one source-grounded root.
- Sacred-text fallback fusion merges multiple surface symptoms in one short recognized/cued religious segment into one root when no more-specific root exists.
- `not but` / `is but` / `only` equivalence remains protected to avoid false positives from valid exclusivity paraphrases.

## Acceptance evidence
- Full pytest regression suite: **317 passed**.
- New sacred-text root-hardening tests: **4 passed**.
- Controlled Quran/Hadith acceptance with authoritative reference evidence: **6 intended bad cases -> 6 root findings; 6 intended good cases -> 0 findings**.
- Deterministic repeatability: **20 cases x 10 runs = 200 comparisons, 0 failures**.
- Synthetic benchmark: Precision/Recall/F1 1.000, FPR 0.000, Critical Error Recall 1.000. This is development evidence, not independent religious validation.
- Synthetic adversarial set: 48 cases, no mistakes.
- Category-sliced synthetic development evidence: terminology/rulings/references/numbers all F1 1.000.
- Long-text synthetic stress: pass, 7/7 injected gap classes detected.
- Source audit: 6236 Quran locator rows, 0 errors.
- Source metadata audit: 0 errors.
- Attribution audit: 0 errors.
- Synthetic identifier audit: external_calls=0, pass.
- Documentation consistency: PASS.

## Safety boundary
Mi'yar does not claim perfect coverage of every possible Quran/Hadith translation or every natural-language paraphrase. A live provider result is required before the UI claims external verification. When evidence is insufficient or a provider fails, Mi'yar abstains / requests human review rather than fabricating verification. The system checks transfer of meaning; it does not issue an independent fatwa or certify the original religious ruling as correct.
