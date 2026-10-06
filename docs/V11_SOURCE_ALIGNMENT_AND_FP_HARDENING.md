# Mi’yar 1.0 — V11 Source Alignment & False-Positive Hardening

V11 fixes the remaining clean-text false positives found by the final acceptance test while keeping the public UI and product scope unchanged.

## Root fixes
- Trusted-source comparison now aligns the user translation to the closest clause/span inside the retrieved Quran/Hadith reference before applying polarity rules. This prevents unrelated negation/conditions elsewhere in a full verse or hadith from contaminating a short translated clause.
- Recognizes faithful English exclusivity patterns such as `is but ...` for Arabic `ما ... إلا`.
- Recognizes paired English negation `neither ... nor` as two preserved negation positions.
- Provenance analysis is polarity-aware: `has not been established as an authentic hadith` is treated as a negated authentication claim, not a positive one.
- `should not be attributed` can preserve `لا يجوز نسبة ...` without creating a false prohibition drift; descriptive negative attribution remains distinct.
- English fraction phrases such as `one third` are consumed as one semantic quantity (`1/3`) rather than `1 + 1/3 + 1/3`.
- Arabic scope phrase matching now respects token boundaries, so `في حال` does not fire inside the dual noun `حالتين`.
- Arabic attribution metadata recognizes forms such as `نسبة` / `منسوب` for source-trace comparison.

## Regression coverage
New tests cover:
- Quran full-reference vs short-clause alignment.
- `Muhammad is but a messenger` vs `not but a messenger` equivalence.
- `He neither begets nor is born` negation preservation.
- negated hadith-authentication statements.
- `should not be attributed ... without verification`.
- `one third` numeric span deduplication.
- preservation of genuine contradictions after the new alignment logic.

## Verification
- Pytest: 156/156 PASS.
- Source audit: PASS.
- Release smoke: 16/16 PASS.
- Jury stress: 37/37 PASS.
- Synthetic development benchmark: TP=63, FP=0, TN=67, FN=0; Precision/Recall/F1=1.000, FPR=0.000.
- Adversarial development set: FP=0, FN=0.
- Repeatability: 200/200 comparisons.
- Long-text stress: PASS.
- Final offline release check: PASS.

These are development/synthetic validation results, not independent field validation. Live source connectivity remains a deployment-machine preflight check.
