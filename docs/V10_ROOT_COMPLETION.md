# Mi’yar 1.0 — V10 Root Completion

V10 closes the remaining acceptance-test classes found after the V9 comprehensive stress test without changing the public UI identity.

## Root fixes

- Arabic number normalization now handles attached one-letter proclitics such as `لثلاث`, `بسبعة`, and equivalent forms instead of requiring whitespace before the number word.
- Fraction comparison treats an English whole/full amount as quantity `1` only when the aligned Arabic unit explicitly contains a fraction, so `نصف المقدار` vs `the full amount` is reported as `1/2 ↔ 1` without polluting ordinary uses of “full”.
- Clean aligned condition cases are locked by regression tests so `إذا ...` ↔ `if ...`, `عند تحقق ...` ↔ `when ...`, and exception phrases do not create false positives.
- Added a local locator seed for the canonical HadeethEnc entry `الدين النصيحة` (#4309). The seed is locator-only; authoritative evidence still requires live HadeethEnc retrieval.
- Added V10 regression coverage for quantities, fractions, clean condition alignment, and the hadith locator.

## Verification

- `pytest`: 147 passed
- Full Quran locator audit: 6236 rows, no errors
- Terminology audit: 152 checks, no errors
- Release smoke: 16/16
- Jury stress: 37/37
- Synthetic benchmark: FP=0, FN=0
- Adversarial: FP=0, FN=0
- Repeatability: 200/200
- Long-text stress: 7/7 injected classes detected
- `scripts/release_check.py`: PASS

Live provider/model readiness must still be checked on the deployment machine with `python scripts/preflight.py` after installing `requirements.txt`.
