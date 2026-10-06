# Mi’yar 1.0 — V9 Root Fix Report

V9 addresses the failure classes exposed by the second and combined acceptance stress tests without changing the public visual identity.

## Root fixes

1. **Reference-grounded contradiction layer**
   - When a Qur'an/Hadith segment is recognized and its trusted English reference is actually retrieved, Mi’yar can raise a dedicated source-conflict issue for direct polarity, exclusivity, and central-meaning contradictions.
   - The retrieved source remains evidence; Mi’yar does not invent a reference when retrieval is unavailable.

2. **Arabic quantity normalization**
   - Added common Arabic number spellings with taa marbuta forms.
   - Added conservative dual count forms such as حالتين / ركعتين / يومين / شهرين / فئتين.
   - Added common fractions including نصف، ثلث، ربع and English half/third/quarter.

3. **Scope and quantifier reasoning**
   - Detects partial→universal, universal→partial, specific→general, sometimes→always, lost "فقط", and "لا يقتصر"→"only" reversals.

4. **Semantic relations between sensitive terms**
   - Detects when a distinction explicitly stated in Arabic is collapsed in English, e.g. Sadaqah ≠ Zakat, Fatwa ≠ personal opinion, Sunnah ≠ social customs, Wahy ≠ personal inspiration.
   - Adds stronger diagnoses for reductive Worship/Sharia definitions.

5. **Attribution and provenance claims**
   - Detects unverified→authenticated, no-source→verified-source, and human-explanation→Qur'anic-text shifts.

6. **Span overlap correction**
   - Nested markers such as «عند تحقق» are counted once instead of also counting the inner «عند».
   - Exception phrases such as «إلا عند الحاجة» are not double-counted as a separate condition when their English realization is the same exception.

7. **Issue hierarchy**
   - Specific semantic diagnoses are prioritized over lower-level symptoms so the UI surfaces the most useful explanation first.

## Deterministic verification

- pytest: **141 passed**
- source audit: **PASS**
- Qur'an locator: **6236 rows**
- release smoke: **16/16**
- jury stress: **37/37**
- development benchmark: **TP 63 / FP 0 / TN 67 / FN 0**
- adversarial development set: **TP 24 / FP 0 / TN 24 / FN 0**
- repeatability: **200/200 comparisons without drift**
- long-text stress: **7/7 planted gap classes detected**
- final deterministic release check: **PASS**

These are development/synthetic verification results, not independent field validation.

## Environment note

`preflight.py` could not complete in the build container because `sentence-transformers` is not installed there. The dependency is already declared in `requirements.txt`. Run preflight after installing requirements on the deployment machine to verify the local semantic model and live evidence providers.
