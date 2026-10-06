# V15.20 — Submission-Ready Evidence Pack
- Added reproducible reviewer-workload evidence: 175 raw signals → 59 root findings (66.3% reduction) on the current long stress document.
- Added final demo, ≤2-minute video, and 5-minute presentation scripts.
- Added owner-only final actions checklist so device/account tasks are separated from package verification.
- Extended judge quick verification and full release check with workload evidence.
- Refreshed current quality/submission documentation; engine religious scope remains unchanged.

# V15.16 — Black-box Hardening & Release Candidate

- Added 20 permanent regressions from extensive user-style black-box testing; full suite is **342/342 passed**.
- Ran **288 additional black-box cases/variants** across rulings, Quran/Hadith wording, references, negation/condition/exception, epistemic certainty, numerics, attribution, source fabrication, and nonreligious false-positive controls; all current cases pass.
- Added a mixed 20-segment document acceptance check: 10 intended-safe segments clean and 10 intended-bad segments detected in the correct locations.
- Hardened Quran identity beyond ayah numbers: named-surah changes, numeric locators, hadith bibliography-number drift, and Quran↔Prophet attribution changes.
- Hardened semantic equivalence for natural paraphrases (`not permitted`, `cannot`, `insufficient`, `only when`, `لكل`↔`every`, thousands separators, and negative-pronoun `أحد`).
- Added curated Quranic terminology coverage for `الصمد` with QuranEnc 112:2 provenance; provider versions are never invented.
- Hardened sacred-text roots so known Quran/Hadith context carries direct religious impact and root-cause fusion suppresses misleading surface symptoms.
- Development metrics remain explicitly labeled synthetic/development evidence; this release does **not** claim 100% religious or field accuracy.

# V15.12 — Religious Acceptance Hardening

- Hardened 27-case religious acceptance behavior for ruling transfer, terminology, Quran references, source fabrication, synthetic provenance, conditions, numeric religious context, epistemic certainty and abstention.
- Fixed numbered-list quantity false positives.
- Preserved backward-compatible `modality_shift` while public taxonomy exposes religious ruling transfer.
- 27-case acceptance: 22/22 intended bad cases detected; 5/5 intended safe cases clean.
- Full regression: 308 passed.

# V15.10 — Arabic UI Polish & Status Precision

- Polished Arabic taxonomy labels and count grammar.
- Clarified external-live-verification wording.
- No detector/root-issue behavior change.
- 295/295 tests passed.

## V15.9 — UI Semantic Truthfulness & Mixed Reference Provenance
- Replaced misleading terminology success checkmarks with result-aware warning/success states.
- Separated internal source-target reference integrity from live external source verification.
- Added explicit meaning-transfer result status and direct religious-impact count.
- Fixed mixed QURAN_REF + TEST/ABC roots so individual reference states remain independent.
- Preserved synthetic-ID isolation from external calls.
- 292/292 pytest; benchmark/adversarial/jury/smoke/long/repeatability and source/metadata/attribution/synthetic audits pass.

# V15.8 — Source Grounding & Public Taxonomy Final Audit

- Public taxonomy badges and automatic category breakdown.
- Distinct religious terminology vs ruling-transfer subtypes.
- `religious_impact_reason` and stronger context gating; technical modality is not treated as religious by default.
- Per-root evidence provenance and reference state.
- `reference_verified` remains distinct from `user_translation_verified`.
- Source-conflict abstention routes to Human Review.
- TEST/MOCK/DEMO/ABC identifiers make zero external verification calls and are labelled synthetic.
- QuranEnc/HadeethEnc attribution metadata is shown when live evidence is used; versions are never fabricated.
- Added metadata, attribution and synthetic-ID audits plus V15.8 regression tests.

# V15.7 — Source-Grounded Safety

- Source version/retrieval metadata for QuranEnc/HadeethEnc without invented versions.
- Reference verification separated from user-translation verification.
- Synthetic reference IDs blocked from external retrieval in test contexts.
- Five-class issue taxonomy + separate `religious_impact`.
- Source attribution and verification boundaries surfaced in UI/audit.
- Category-sliced benchmark report added.
- 274 tests pass.

# Mi’yar 1.0 — V15.6 Semantic Dedup & Specificity Final Polish

- Added specificity-aware suppression so generic epistemic alerts remain internal evidence when a more specific date/threshold root explains the same semantic region.
- Added backward-compatible `root_code` values: `SIGNED_NUMBER_CONTRADICTION`, `DECIMAL_VALUE_CORRUPTION`, and `DATE_AMBIGUITY_COLLAPSE`, while retaining existing public `type` values.
- Strengthened semantic dedup to require two-sided source/target span overlap; sharing the same paragraph is never sufficient to merge independent issues.
- Preserved independent roots in one paragraph: signed-number vs decimal corruption, event-order vs causality, and the three distinct ruling-degree changes.
- Added semantic root-family diagnostics (`REFERENCE`, `RULING`, `NUMERIC`, `LOGIC`, `SCOPE`, `EPISTEMIC`, `ACTOR`, `CAUSALITY`, `TERMINOLOGY`).
- Debug trace now records `root_code`, `semantic_family`, `suppressed_by`, and `merged_into`.
- Meaning Mirror ranks only the final public root set after suppression/dedup; the long acceptance case continues to select reference fabrication as the representative high-impact gap.
- Added 12 V15.6 regression/unseen tests; total suite **266/266**.
- User long stress: **45↔45** alignment, **174** raw signals → **57** public root issues, **117** suppressed/merged signals, **0** exact duplicate roots, no malformed numeric explanations, no unresolved terminology fallback noise.
- Specific numeric/date paragraph now exposes exactly the dedicated signed-number, decimal, and date roots while the generic certainty signal is retained only in Trace. Genuine uncertainty→certainty findings remain public elsewhere.

# Mi’yar 1.0 — V15.5 Clean Root Findings

- Fixed multi-digit numeric truncation (`750→00`, `30→0`) at the regex/token level.
- Bound unresolved terminology to evidence only unless an aligned risky/review target span exists.
- Strengthened root dedup/fusion and source-integrity suppression.
- Added impact/specificity/confidence ranking for Meaning Mirror.
- Added independent root-family confidence diagnostics and opt-in `MIYAR_DEBUG=1` trace.
- Synthetic TEST/MOCK/DEMO/ABC identifiers in explicit examples are not routed as authoritative source lookups.
- Added 28 V15.5 regression/unseen tests; total suite 254/254.
- User long stress: 45↔45 alignment, 58 root issues from 174 raw signals, zero malformed numeric explanations and zero unresolved terminology fallbacks.

# Mi’yar 1.0 — V15.4 Contextual Root-Cause Hardening

- Added contextual predicate/relation layer and segment-local root-cause fusion.
- Reduced the user's long acceptance case from 157 user-facing detector findings to 61 semantic root issues while retaining 180 raw evidence signals internally.
- No generic condition/negation/exception/quantity/generalization symptom remains user-facing in that acceptance case when a more precise root explains it.
- Added dedicated roots for reference IDs/locators, source fabrication, comparison direction, event order, causality, actor responsibility, source attribution, AND/OR/cardinality, units/time, uncertainty and epistemic overclaim.
- Pronoun ambiguity now causes local review rather than overriding supported critical document errors.
- Added 27 regression/unseen-formulation tests; total test suite: 226.
- Development validation: benchmark P/R/F1 1.000 with FPR 0.000; adversarial 48/48; jury 37/37; smoke 16/16; long-text 7/7; repeatability 200/200.
- Semantic-AI-only baseline could not be rerun in the build runtime because the optional local semantic model was unavailable; this is not claimed as a pass.

# V15.2 — Root semantic hardening + mentor-source compliance

- Fixed Windows resource profiling: uses `tracemalloc` everywhere and `resource` only when the OS provides it.
- Preserves Arabic hamza distinction before structural parsing so `أن` is not mistaken for conditional `إن`.
- Added conservative `إن` conditional detection and explicit `ما لم ↔ unless` handling.
- Added `وجب`/`مطلوب` ruling signals and sentence/chunk-local modality checks.
- Added monotonic sentence/chunk alignment when punctuation counts differ.
- Added quantity-to-anchor binding so identical number bags cannot hide swapped quantities.
- Added ordinary `غسل` vs ritual `غُسل/الغسل` terminology gating.
- Tightened safe corrections to atomic terminology substitutions only; no automatic rewrite of conditions, exceptions, rulings, negation or quantities.
- Added new regression + blind-formulation tests; total is 190 tests in this release.
- Added direct `verification_locator` provenance for all 48 terminology rules.
- Added general linguistic-method references and mentor-feedback implementation docs.

# V15 — Full-Mark Readiness Hardening
- Added per-term provenance manifest for all terminology guards and made source audit fail on missing grounding rows.
- Added an offline layer-ablation study showing that structure-only and terminology-only baselines have lower recall than the composed Mi'yar pipeline on the development set.
- Added deterministic resource profiling for operational evidence.
- Added documentation-consistency enforcement to prevent stale UX claims from contradicting the shipped product.
- Rewrote README, handoff, jury scorecard, benchmark, operations, source provenance, challenge alignment and submission checklist around V14/V15 behavior.
- Added external-validation and usability protocols/templates without fabricating independent results.
- Safe corrections remain suggestions only; no automatic apply/re-check button.

# V14 — Final writer UX
- أزيل زر «طبّق التصحيح الآمن وأعد الفحص» بالكامل.
- التصحيحات الآمنة أصبحت اقتراحات عرض فقط: موضع الأصل، النص قبل، النص بعد، والسبب.
- لا تعديل تلقائي لخانة الترجمة ولا إعادة فحص تلقائية؛ إعادة الفحص تتم من زر الفحص الأساسي بعد تحرير الكاتب للنص.
- منطق الكشف، المصادر، المراجعة البشرية، ومرآة المعنى لم يتغير.


## V13 UX refinement
- Removed the redundant helper sentence under the result summary to keep the review surface visually quiet.
- Safe corrections now show the exact sentence **before** and **after** the edit, plus the source context and reason, instead of an ambiguous token arrow.
- Correction copy now distinguishes a proposed safe correction from a correction that has actually been applied and re-checked.
# V12 — Writer-first progressive disclosure UX

- Reworked the result page without changing Mi'yar's engine or visual identity.
- All detected gaps are now available inside one collapsed **الفجوات المكتشفة** section instead of showing only a top-four list plus a second remainder list.
- Public issue titles strip internal `المقطع N` suffixes; the writer sees the actual Arabic and English text context instead of relying on segment numbers.
- Safe correction now shows only the changes Mi'yar can apply conservatively, with the affected text, before/after token, and reason. The full translation is no longer duplicated before/after in the result card.
- Unresolved material gaps appear in one collapsed **فجوات تحتاج مراجعة بشرية** section with the actual text and an explicit explanation that Mi'yar abstains when a safe rewrite is not available.
- Evidence is now collapsed under **كيف وصل مِعيار إلى هذا القرار؟** with a short plain-language explanation.
- Renamed and redesigned source comparison as **التحقق من الترجمة بالمراجع الموثوقة**. It explicitly explains that QuranEnc/HadeethEnc translations are supporting verification evidence, not a replacement translator, and shows original text → user translation → trusted reference → what Mi'yar learned from the reference.
- Moved the internal reference-routing summary into **عرض تفاصيل الفحص** instead of presenting it as a primary public section.
- Correction payloads now preserve unresolved issue objects and writer-facing context for the UI.
- Verification: **161/161 pytest PASS** and **FINAL RELEASE CHECK PASS**. Build-environment preflight reaches the full-Quran locator then stops because `sentence-transformers` is not installed; run it after installing requirements on the deployment machine.

# V8 — UX clarity without redesign

- Preserved the existing dark premium visual identity and two-column review workspace.
- Added a concise product explanation: Mi’yar reviews an existing translation; it does not translate from scratch.
- Added a compact flow cue: detect → explain → safe correction → re-check.
- Result now surfaces the decision first, then the highest-impact gaps, then the safe correction immediately; remaining gaps stay accessible in an expander.
- Remaining unresolved review items are shown visibly (first five) instead of leaving an apparently empty review section.
- Repeated Quran matches now name the actual locations when available (for example: البقرة 2:255، آل عمران 3:2) rather than only saying “repeated Quran text.”
- Updated UI regression tests for the new progressive-disclosure flow.
- Offline release check: 130 tests passed and FINAL RELEASE CHECK PASS.
- Preflight in the build environment reaches the local Quran check, then stops because sentence-transformers is not installed in that environment; run preflight after installing requirements on the deployment machine.

## V7 — Root-cause hardening

- Segment-aware deduplication: identical error classes in different sentences are no longer collapsed.
- Occurrence-aware terminology alignment: repeated English words are bound to the corresponding Arabic term by local position before auto-correction.
- Fasting context accepts “fast/the fast” in context instead of raising a false terminology review.
- “only for …” is classified as an added restrictive scope, not a generalization.
- Added protected detection for omitted «القيوم» in Quranic translation review.
- Added regression tests for all five failures found by the mixed-document acceptance test.

# RELEASE NOTES — V6 ACCEPTANCE HARDENING

- Fixed the public UI crash `NameError: name 're' is not defined` by importing `re` in `app.py`.
- Added regression coverage so the page code compiles before release.
- Treated Arabic `بلا` as the structural counterpart of English `without`; `بلا حساب` ↔ `without reckoning` no longer creates a false added-negation alert.
- Disambiguated English `may`: probability expressions such as `may have more than one possible meaning` no longer become fake permissibility rulings, while deontic `It may be done` still participates in obligation/permission checks.
- Filtered lexical `more than one possible meaning` from quantity drift while preserving genuine written-number checks such as `ثلاث` ↔ `four`.
- Added Arabic `جاز` to the permission detector, so `إذا تحقق الشرط جاز الفعل` ↔ `The action is permissible` reports the missing condition only, not a fake added-permission issue.
- Added a targeted audience/scope guard for rulings such as `الصلاة واجبة على المسلم البالغ` ↔ `Prayer is obligatory`; the missing target qualifier is now surfaced.
- De-duplicated `لا يجوز` → `permissible`: the user sees one precise prohibition/permission reversal instead of the same defect plus a redundant bare-negation alert.
- Re-ran the exact 18-segment mixed acceptance message used during manual testing; the known V5 false positives are gone while the genuine local gaps remain isolated by segment.
- Deterministic/offline release verification: **122/122 pytest**, **16/16 smoke**, **37/37 jury stress**, **48/48 adversarial**, **200/200 repeatability**, full **6,236-ayah locator audit**, benchmark development set **FP=0**, and final release check **PASS**.
- Live-provider/model preflight still must be run on the deployment machine; this build environment cannot install `sentence-transformers` or reach package/provider networks.

## V4 HARDENED

- Added full 6,236-ayah local Quran locator for resilient source recognition.
- Fixed Quran fragment recognition for `وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا` (5:6).
- Fixed conditional `إن` detection without treating emphatic `إن الله...` as a condition.
- Repeated Quran text is marked ambiguous instead of guessing one reference.
- Removed fake public human-review workflow buttons; review is now a decision state only when the system cannot safely close a case.
- Fixed a short-text coverage false positive.
- Added strict source audit: full Quran locator integrity, terminology matrix, source routing, and public-review UI checks.
- Reference-only sources remain separated from evidence actually used.

# Mi’yar 1.0 — Jury-Max Release Notes

## Final criteria-driven hardening
- sentence-local ruling and terminology alignment
- Arabic «ليست» negation support
- context-aware «شرط» ↔ required-for handling
- Arabic/English spelled-out number comparison
- reductive-gloss detection even when transliteration is preserved
- 37-case jury stress suite and one-command final release check
- explicit user next-step copy in the public result
- updated judging scorecard, operations plan and test matrix

# Mi’yar 1.0 — Gold Release Notes

## Public experience
- Arabic-first neutral wording for all users.
- Wider desktop layout and readable typography.
- Empty submissions are disabled.
- Implementation internals are hidden from the public surface.
- Safe output is scoped to **meaning transfer** and never presented as religious approval of the Arabic source.
- Human review appears only when review/blocking is needed.
- Suggested references are separated from evidence actually used.
- Up to **12,000 characters per side** in one analysis.
- Every detected issue is rendered; the UI no longer stops after the first three findings.

## Decision quality
- Added expanded terminology precision guard with official challenge glossary rows kept distinct from conservative Mi'yar-curated rules.
- Added explicit Zakat/Sadaqah distinction: `الزكاة → charity` is flagged and explained; `الزكاة → Zakat` is accepted.
- Added guards for Wudu, Tayammum, fasting, Hajj, Umrah, Riba, Shirk, Kufr, Dhikr, Du'a, Jihad, prayer, Niyyah, Taharah, Ghusl, Qibla, Adhan, Ruku, Sujud, Ihram, Kaffarah, Waqf, Iddah and more.
- Context-dependent equivalents such as `الربا → interest` route to review rather than false certainty.
- Structural checks now compare **occurrence counts**, so a long passage with two exceptions in Arabic and one in English is not falsely marked safe.
- Fixed Arabic conjunction handling (`ولا`, `ويجوز`, etc.) so long multi-sentence text preserves separate prohibition/permission signals.
- Semantic similarity remains supporting evidence only.
- Long-text semantic chunking no longer merges later passages into oversized blocks that could be silently truncated by the embedding model.
- Public release decisions do not depend on an external generative model.

## Release verification
- **81 automated tests passed.**
- **16/16 release smoke cases passed.**
- Synthetic development benchmark: **130/130 expected classifications**.
- Synthetic adversarial set: **48/48 expected classifications**.
- Repeatability: **200/200 deterministic comparisons** with no drift.
- Long-text stress test: **passed** on a 7,034-character Arabic source and 11,513-character English translation with multiple independent errors in the middle of the text.

These figures are development evidence only, not independent real-world validation.

## Jury-Max verification refresh
- 105/105 automated tests passed.
- 37/37 jury-oriented stress cases passed.
- 130/130 synthetic benchmark classifications expected.
- 48/48 adversarial cases expected.
- 200/200 repeatability comparisons stable.
- 7/7 injected long-text gap classes detected.

## Final UX action loop
- اختُصر أعلى الصفحة إلى Hook واحد واضح ثم حقول الإدخال مباشرة.
- نُقل مؤشر التقارب الدلالي إلى «تفاصيل التدقيق» حتى لا يزاحم الخطأ الحقيقي.
- أضيفت «المشكلة الأساسية» مباشرة بعد قرار ما قبل النشر.
- أضيف تصحيح مقترح عندما يكون المقابل المصطلحي واضحًا بما يكفي.
- أضيف زر «طبّق التصحيح وأعد الفحص»: يحدّث خانة الترجمة ثم يعيد التحليل تلقائيًا.
- التصحيح التلقائي محافظ: لا يعمل في الحالات السياقية/غير المحسومة، ولا يخترع ترجمة عند نقص الدليل.
- التصحيح في النصوص متعددة الجمل يحترم رقم المقطع حتى لا يستبدل كلمة صحيحة في جملة أخرى.
- أزيل تكرار «أثر القرار» من التدفق الرئيسي؛ مرآة المعنى + المشكلة + التصحيح أصبحت مسار القراءة الأساسي.

## Submission-ready combined correction pass
- All detected high-confidence fixes are now merged into one proposed translation before re-checking.
- The public result shows every detected gap together before the proposed correction.
- Missing exception evidence now shows the full source clause (for example `إلا لعذر معتبر`) instead of a bare marker.
- Whitelisted missing exception clauses can be restored conservatively without turning Mi’yar into a free-form translator.
- Explicit numeric mismatches and deterministic ruling-degree marker shifts can participate in the same combined correction.
- The public details summary reports meaning gaps, not the larger internal count of low-level checks, preventing confusing `2 gaps` vs `4 checks` messaging.
- Common Arabic forms `يستحب` and `يكره` are recognized in ruling-degree checks.
- Latest deterministic release verification: **105/105 tests passed**, plus 16/16 release smoke, 37/37 jury stress, 130/130 synthetic benchmark classifications, 48/48 adversarial cases, 200/200 repeatability comparisons, and 7/7 injected long-text gap classes.


## V2 UI trust cleanup
- Simplified the collapsed diagnostics control to `عرض تفاصيل الفحص` only.
- Removed redundant public check-count/status explanatory copy.
- Changed local curated terminology evidence label to `قاعدة مِعيار المصطلحية` to avoid implying external verification when no direct source was used.

## V3 — Final UI cleanup
- نقل المراجع المقترحة غير المستخدمة إلى داخل «عرض تفاصيل الفحص».
- إزالة تكرار وصف قاعدة مِعيار المصطلحية من سلسلة الدليل.
- بعد التصحيح المتعدد، تعكس مرآة المعنى جميع أنواع التصحيحات المطبقة في إعادة الفحص المباشرة.

## V9 — root semantic hardening
- Added reference-grounded contradiction detection for retrieved Qur'an/Hadith evidence.
- Added Arabic written numbers, conservative dual quantities, and fractions.
- Added scope/quantifier reasoning and frequency drift detection.
- Added semantic relationship checks for sensitive Islamic terms.
- Added attribution/provenance claim drift and sacred-text-boundary checks.
- Fixed nested structural marker double-counting.
- Added semantic issue prioritization so specific diagnoses surface before generic symptoms.
- Deterministic verification: 141 pytest passed; smoke 16/16; jury 37/37; development benchmark FP=0/FN=0; adversarial FP=0/FN=0; repeatability 200/200; final release check PASS.

## V10 — acceptance root completion
- Fixed Arabic written-number detection when number words carry attached proclitics (`لثلاث`, `بسبعة`, etc.).
- Added context-safe whole/full quantity handling for fraction comparisons (`نصف` ↔ `full` => `1/2 ↔ 1`).
- Locked clean conditional alignments with regression tests to prevent the false positives exposed by the combined acceptance set.
- Added HadeethEnc locator seed for `الدين النصيحة` (#4309); live HadeethEnc retrieval remains the authoritative evidence step.
- Added V10 regression suite; 147 tests pass and final offline release check passes.

## V11 — source alignment & false-positive hardening
- Added clause-level alignment before trusted Quran/Hadith reference contradiction checks.
- Fixed false conflicts caused by negation elsewhere in a full retrieved verse.
- Added faithful handling for `is but ...`, `neither ... nor`, and attribution paraphrases.
- Made provenance/authentication detection polarity-aware.
- Fixed `one third` overlapping numeric extraction and Arabic scope substring matching.
- Added V11 regression suite; 156 tests pass.
- Synthetic development benchmark after the fixes: FP=0, FN=0; final offline release check passes.

## V15.1 — Release-check environment exclusion fix
- Fixed `scripts/release_check.py` so the secret scanner ignores local/third-party environment directories such as `.venv`, `venv`, `node_modules`, caches, build and dist outputs.
- The scanner still checks project source/configuration files and still fails on real secret-like material in the repository.
- Added binary/generated suffix exclusions to avoid false positives from compiled dependency artifacts.

## V15.11 — Target-side religious impact completion
- Religious impact now evaluates explicit target-side religious additions as well as source-side context.
- Fixed one under-classified long-stress finding: a target that permits adding “religious conclusions” now carries high religious impact.
- Root count and taxonomy distribution remain unchanged.

## V15.13 — Live Source Routing & Hadith Equivalence
- Natural `سورة ... الآية ...` references now enter Quran source routing.
- Quoted hadith matn is recognized independently from citation prose.
- Fixed false positives from `no. 1907`, `is/are but`, and `every person` in faithful hadith translation.
- Unified source provenance segment indices with semantic alignment.
- A local locator no longer counts as completed external live verification.
- Exact three-case source acceptance test now yields one real gap only: 2:183 -> 2:185.

## V15.14 — Sacred Text Root Hardening
- Source recognition now propagates into finding-level religious impact.
- Generic surah/ayah citation drift is reference integrity, not numeric drift.
- Quran/Hadith source-fabrication wording generalized.
- Trusted-source semantic contradictions suppress lower-level surface symptoms.
- Sacred-text multi-symptom findings fuse into one root when no stronger diagnosis exists.
- Preserved `not but` / `is but` equivalence to prevent valid-paraphrase false positives.
- Full regression: 317 passed.

## V15.15 — Code Freeze
- Deep sacred-text red-team hardening after V15.14.
- Added five regression tests for unseen Quran/Hadith formulations.
- Fixed single-pair context propagation, explicit-Hadith root fusion, generalized source-fabrication policy reversal, and direct unity-reversal detection.
- Trusted live reference roots suppress equivalent local sacred roots to prevent duplicate public findings.
- 322/322 pytest passed; repeatability 200/200; source/security/document audits passed.

# V15.19 — Judge-Ready Submission Packaging
- Added public-friendly one-click demo cases (safe / ruling shift / reference shift) without changing the safety scope.
- Added `START_HERE_FOR_JUDGES.md` as a one-minute evidence map.
- Added `docs/MEASURABLE_IMPACT.md` with ablation, reliability, sacred-reference and resource evidence plus explicit limits.
- Added `docs/COMPARATIVE_POSITIONING.md` with sourced nearest-tool comparison and bounded novelty claim.
- Added `scripts/judge_verify.py` + `JUDGE_VERIFY.bat` for fast evidence verification.
- Updated top-level handoff, operations, challenge alignment and full-mark readiness to the V15.18 verified engine evidence.
- Moved stale V15.16 root report to history so the repository root reflects the current submission state.
