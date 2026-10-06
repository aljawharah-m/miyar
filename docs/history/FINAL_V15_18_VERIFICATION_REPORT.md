# Mi’yar V15.18 Final Verification

- Full regression: 348/348 passed.
- Sacred Quran corpus audit: 6,236/6,236 exact, undiacritized, quoted, and natural-context recognitions with 0 misses and 0 wrong mappings; repeated text is safely ambiguous.
- Quran reference integrity: 6,236 safe references with 0 false positives; 6,236 ayah-number mutations detected; 6,236 surah mutations detected; QuranEnc routing 0 wrong.
- Quran reference semantic audit: 24 official-safe cases, 0 false positives; 31 semantic mutations, 0 missed; provider-failure unsafe/false-live claims 0.
- Hadith reference audit: 20 official-safe cases, 0 false positives and 0 route failures; 50 semantic mutations, 0 missed; provider failures 0 unsafe claims; structured-ID changes detected with 0 misses.
- Safety fixes include short-ayah recognition boundaries, Quran/Hadith source identity, source-grounded semantic reversals, exact authoritative-translation protection, nonnumeric theological “One”, Quran lexical equivalences, and provider-failure abstention.

These are deterministic development/audit results, not a claim of universal religious accuracy.
