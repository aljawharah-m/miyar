# V6 Acceptance Report

## Scope
This report records deterministic/offline checks performed after the mixed-document manual acceptance test exposed V5 false positives and a public UI crash.

## Fixes verified
- `app.py` imports `re`; Python compilation succeeds.
- `بلا حساب` ↔ `without reckoning`: no false negation gap.
- `may have more than one possible meaning`: no permission gap.
- `more than one possible meaning`: no quantity gap.
- `إذا تحقق الشرط جاز الفعل` ↔ `The action is permissible`: missing condition remains; no added-permission false positive.
- `لا يجوز فعل ذلك` ↔ `It is permissible to do this`: one ruling-polarity gap, not duplicate negation + polarity gaps.
- `الصلاة واجبة على المسلم البالغ` ↔ `Prayer is obligatory`: missing audience/scope qualifier detected.
- Genuine `ثلاث` ↔ `four` quantity drift remains detected.
- Quran segments and known hadith remain recognized sentence-locally.

## Automated results
- Pytest: 122/122 passed.
- Release smoke: 16/16 passed.
- Jury-oriented synthetic stress: 37/37 passed.
- Synthetic development benchmark: TP=63, FP=0, TN=67, FN=0.
- Synthetic adversarial: 48/48 expected classifications; FP=0.
- Deterministic repeatability: 200/200 comparisons stable.
- Long-text injected gap classes: 7/7 detected.
- Full Quran locator audit: 6,236 rows; source audit errors: 0.
- Final deterministic release check: PASS.

These are development tests, not independent real-world validation.

## Runtime/live limitation of this verification environment
`python scripts/preflight.py` reaches the local Quran-locator check, then stops because `sentence_transformers` is not installed in this isolated build environment. Package installation/network access is unavailable here. Therefore live provider connectivity and the local embedding model must be checked on the deployment machine after `pip install -r requirements.txt`.
