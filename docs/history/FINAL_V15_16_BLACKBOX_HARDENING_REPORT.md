# Mi’yar 1.0 — V15.16 Black-box Hardening Report

## Scope
This release hardens the existing Arabic→English translation-safety gate through user-style black-box testing, without expanding Mi’yar into a fatwa or translation-from-scratch system.

## Validation completed
- 342/342 pytest regressions passed.
- 288 additional black-box cases/variants passed across five suites (58 + 40 + 98 + 72 + 20).
- Mixed 20-segment document: 10 intended-safe segments remained clean; 10 intended-bad segments were detected at the correct segments.
- Synthetic benchmark: Precision/Recall/F1 1.000, FPR 0.000 on the included development set only.
- Adversarial 48/48; jury 37/37; release smoke 16/16; long-text 7/7; repeatability 200/200.
- Quran locator audit: 6236 rows, zero audit errors.
- Terminology provenance: 49 rows, including curated `الصمد` grounded to QuranEnc 112:2.
- Source metadata, attribution, synthetic-ID, and documentation audits: zero errors / PASS.

## Root hardening added
- Quran reference identity compares surah + ayah and handles natural/numeric locator forms.
- Hadith bibliography-number changes are source-integrity roots.
- Quran↔Prophet attribution swaps are source-integrity roots.
- Source-fabrication policy recognizes broader wording around unverifiable Quran/Hadith sources.
- Religious-impact propagation uses recognized Quran/Hadith context while preserving nonreligious controls.
- Root fusion suppresses redundant surface symptoms when a stronger semantic/reference root explains the same change.
- Added equivalence handling for valid paraphrases, numerical formatting, negation, conditions, and epistemic uncertainty to reduce false positives.

## Claims boundary
The 1.0 benchmark values are synthetic development evidence and must not be presented as independent religious validation or a guarantee of perfect accuracy over arbitrary Quran/Hadith wording. Live provider connectivity is deployment-dependent. Mi’yar preserves Human Review/abstention when evidence is insufficient.
