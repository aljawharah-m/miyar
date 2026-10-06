# Mi'yar 1.0 — V15.13 Live Source Routing & Hadith Equivalence

## Why this release exists
A three-case public-site source test exposed two real defects in V15.12:
1. Natural written references such as `سورة البقرة، الآية 183` and a quoted hadith were not entering the live-source recognition path, so the UI correctly reported that no dependable live verification completed.
2. A faithful English rendering of the hadith of intentions produced false positives because `no. 1907` was read as negation, `are but` as an added exception, and `every person` as a new generalization.

## Fixes
- Added explicit Quran locator recognition for natural Arabic surah/ayah references and structured `QURAN_REF` references.
- Added all 114 Arabic surah names for locator resolution.
- Quoted Arabic hadith matn is now matched independently from surrounding bibliographic prose.
- Source review-unit segmentation now reuses the exact alignment splitter, preventing provenance segment-index drift caused by numbered lists.
- `no. <number>` is treated as a bibliographic number abbreviation, not logical negation.
- Arabic `إنما` is recognized as compatible with English `is/are but` / exclusivity wording.
- Arabic `لكل امرئ/شخص/إنسان` is recognized as compatible with `every person/individual` rather than a new generalization.
- Public `reference_verified` now requires actual `live_verified` provider evidence; local locators can never create a false green live-verification state.
- Provider failure remains abstention/review and never fabricates evidence.

## Acceptance result on the exact three pasted cases
Offline routing audit (provider network intentionally disabled):
- Case 1, Al-Baqarah 2:183 -> 2:183: no gap.
- Case 2, Al-Baqarah 2:183 -> 2:185: exactly one SOURCE_INTEGRITY gap.
- Case 3, hadith of intentions + Sahih Muslim 1907: no semantic false positives.
- Recognitions: Quran segment 1 -> 2:183; Quran segment 2 -> 2:183; Hadith segment 3 -> HadeethEnc locator #4560.
- Local locator evidence does **not** mark external verification complete.

## Regression status
- Pytest: 313/313 passed.
- Synthetic development benchmark: Precision/Recall/F1 1.000, FPR 0.000, Critical Error Recall 1.000. Not independent validation.
- Adversarial synthetic development: 48/48, no mistakes.
- Repeatability: 200/200 comparisons, no failures.
- Source audit: zero errors.
- Source metadata audit: zero errors.
- Attribution audit: zero errors.
- Synthetic-ID audit: external_calls=0, pass=true.
- Documentation consistency: PASS.

## Deployment truthfulness
This release verifies that source routing and provider-call behavior are correct under controlled regression tests. It does **not** claim that QuranEnc/HadeethEnc network access succeeded on the user's laptop until `scripts/preflight.py` or the public UI shows actual live provider evidence there.
