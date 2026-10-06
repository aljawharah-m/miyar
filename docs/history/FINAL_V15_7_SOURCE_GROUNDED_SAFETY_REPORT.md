# Mi’yar V15.7 — Source-Grounded Safety Final Report

## الفكرة المثبتة
**مِعيار لا يصدر أحكامًا شرعية جديدة؛ بل يحمي الحكم والمصطلح والدليل الموجود أصلًا من التحريف أثناء انتقاله بين اللغات.**

المصادر الدينية تقوي التحقق من المرجع والمصطلح والدلالة الحساسة، لكنها لا تحول مِعيار إلى محرك فتوى ولا تجعل `reference_verified` مساوية لـ`user_translation_verified`.

## إصلاحات V15.7
1. QuranEnc metadata: `translation_key`, `source_version` إذا وفرها المصدر، `source_last_update`, `translation_title`, `retrieved_at`, URL وmetadata URL.
2. HadeethEnc metadata: `source_version` فقط إذا أعادها المصدر؛ وإلا `None` صراحة، مع `retrieved_at` وURL.
3. لا يتم اختلاق أي version.
4. فصل `reference_verified` و`source_text_retrieved` عن `user_translation_verified`.
5. synthetic IDs (`TEST/MOCK/DEMO/ABC`) في سياق الاختبار لا تذهب إلى external recognition/retrieval.
6. route-only/recommended sources لا تظهر `used evidence` بلا استرجاع فعلي أو قاعدة محلية موثقة.
7. كل public finding يحمل taxonomy: `RELIGIOUS_SEMANTIC`, `GENERAL_SEMANTIC`, `LOGIC_NUMERIC`, `SOURCE_INTEGRITY`, `EPISTEMIC`.
8. حقل `religious_impact` منفصل عن taxonomy لمنع الخلط بين نوع الخطأ والأثر الديني.
9. Ruling/terminology findings توضح أنها تقيس **نقل الدلالة المذكورة في الأصل** لا صحة الحكم الشرعي الأصلي.
10. Source-integrity findings توضح أن تطابق المرجع لا يساوي اعتماد صحة المحتوى دينيًا.
11. واجهة الأدلة تعرض attribution/version/retrieval timestamp عند توفرها.
12. Debug/audit export يحتفظ بالmetadata الجديدة والتصنيف وحدود التحقق.
13. README/SOURCES/LICENSES/source catalog متسقة مع نفس السياسة.
14. Benchmark فئوي مستقل للمصطلحات/الأحكام/المراجع/الأرقام مع تسمية واضحة أنه synthetic development evidence وليس دقة دينية ميدانية.

## التحقق
- pytest: 274/274 passed.
- Development benchmark: Precision/Recall/F1 = 1.000, FPR = 0.000 on the bundled synthetic development set.
- Adversarial: 48/48.
- Jury stress: 37/37.
- Release smoke: 16/16.
- Long-text stress: 7/7 injected classes detected.
- Repeatability: 200/200 comparisons.
- Source audit: 0 errors.
- Documentation consistency: PASS.
- Category-sliced synthetic benchmark: terminology, rulings, references, numbers each 1.000 P/R/F1 on their current bundled slices; this is not independent religious validation.

## Acceptance fixture
The bundled 45↔45 long-stress fixture produces 57 root issues from 174 raw signals after fusion. Every public root has taxonomy, religious impact, and aligned source/translation context. The exact count is not treated as a universal target; root IDs/spans and correctness are the acceptance criterion.

## نزاهة الادعاء
لا توجد عبارة “دقة دينية 100%”. نتائج 1.000 تخص مجموعات الاختبار الصناعية المرفقة فقط. Live provider connectivity remains deployment-dependent and is checked separately by preflight.
