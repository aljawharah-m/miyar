# Mi'yar V15.9 — UI Semantic Truthfulness & Mixed Reference Provenance

## Goal
V15.9 is a release-polish patch over V15.8. It does not broaden Mi'yar into a fatwa engine and does not change the project scope. It fixes misleading presentation states discovered in the V15.8 long-stress output and tightens mixed-reference provenance.

## Fixes implemented
1. **Terminology status is no longer misleading.** A successful checkmark is never shown when terminology gaps exist. The UI now shows a warning and the number of detected terminology gaps.
2. **Internal reference integrity and live external verification are separate.** The result distinguishes source↔translation reference mismatches from whether a trusted provider was actually queried and verified.
3. **Translation result state is explicit.** The UI reports whether meaning-transfer gaps were found rather than showing a vague process-state label.
4. **Taxonomy and religious impact are displayed as separate dimensions.** The summary now adds an automatically computed direct-religious-impact count and explains that a numeric/logical issue may still have religious impact in context.
5. **Mixed reference IDs are not collapsed to synthetic.** A root containing a changed `QURAN_REF` together with `TEST/ABC` IDs is classified as `mixed`; each identifier is exposed as independent sub-evidence.
6. **Synthetic identifiers stay synthetic.** TEST/MOCK/DEMO/ABC entries are labelled as test identifiers and remain isolated from external verification.
7. **Religious-impact wording is clearer.** `none` is rendered as `لا يوجد أثر ديني مباشر` rather than the ambiguous `غير مباشر/غير منطبق`.
8. **Reference-impact explanation is precise for mixed roots.** The UI explains that the Quran-style reference changed while TEST/ABC remain synthetic.
9. **Taxonomy count spacing/accessibility improved.** Summary pills render count and label distinctly.

## Same 45-pair acceptance stress
- Alignment pairs: **45**
- Root issues: **58**
- Raw signals: **177**
- Taxonomy: 6 religious-semantic / 25 general-semantic / 14 logic-numeric / 4 source-integrity / 9 epistemic
- Direct religious impact: **18**
- No new root issue was added by this patch; the increase from 17 to 18 direct-impact roots is a classification correction for the mixed QURAN_REF + synthetic-ID root.
- Mirror top issue remains reference fabrication / unsafe substitution.

## Mixed-reference acceptance
`QURAN_REF: 2:183 → 2:185` = changed reference-like identifier.
`HADITH_REF: TEST-123 → TEST-321` = synthetic test identifier.
`SOURCE_ID: ABC-001 → ABC-010` = synthetic test identifier.
The root state is `mixed`, not globally `synthetic`.

## Verification after final patch
- pytest: **292/292 passed**
- benchmark: Precision 1.000 / Recall 1.000 / F1 1.000 / FPR 0.000 / Critical Error Recall 1.000
- category benchmark: passed on the current synthetic development set
- adversarial benchmark: Precision/Recall/F1 1.000, FPR 0.000
- jury stress: **37/37**
- release smoke: **16/16**
- long-text stress: PASS
- repeatability: **200/200 comparisons**, no failures
- source audit: **0 errors**
- source metadata audit: **0 errors**
- attribution audit: **0 errors**
- synthetic-ID audit: **external_calls=0**, PASS

All 1.000 figures are development-set results, not claims of religious correctness or independent field validation.

## Scope boundary
**مِعيار لا يصدر أحكامًا شرعية جديدة؛ بل يحمي الحكم والمصطلح والدليل الموجود أصلًا من التحريف أثناء انتقاله بين اللغات.**
