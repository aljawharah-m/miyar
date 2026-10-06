# Mi’yar 1.0 — V15.6 Semantic Dedup & Specificity Final Polish

## الهدف
إغلاق آخر طبقة ضجيج في V15.5 بدون خفض عدد الفجوات بشكل مصطنع أو حذف أخطاء مستقلة صحيحة. التركيز في V15.6 هو **specificity-aware suppression + strict span-aware dedup** بعد أن أصبحت المحاذاة والجذور الأساسية مستقرة.

## التغييرات الجذرية
1. الإشارة العامة `uncertainty_to_certainty` لا تظهر للمستخدم عندما تكون ناتجة عن تاريخ ملتبس وله root أدق في نفس المقطع. الإشارة الخام تبقى في Trace.
2. عدم over-suppression: `قد يكون صحيحًا → definitely correct` يبقى Finding مستقلًا عندما لا يوجد root أدق.
3. تصنيفات تفصيلية جديدة مع backward compatibility:
   - public type: `numeric_relation_reversal` + `root_code=SIGNED_NUMBER_CONTRADICTION`
   - public type: `numeric_relation_reversal` + `root_code=DECIMAL_VALUE_CORRUPTION`
   - public type: `date_ambiguity_overclaim` + `root_code=DATE_AMBIGUITY_COLLAPSE`
4. dedup الدلالي لا يعتمد على كون الخطأين في نفس الفقرة. الدمج يتطلب تداخلًا قويًا في **source span وtarget span** مع type/root_code متوافق.
5. أخطاء `-1↔1` و`1.5↔15` تبقى منفصلة؛ event order وcausality يبقيان منفصلين؛ وتحولات الجائز/المستحب/المحرم تبقى ثلاثة roots مستقلة.
6. root-family diagnostics موحدة إلى عائلات تفسيرية مثل REFERENCE/RULING/NUMERIC/LOGIC/SCOPE/EPISTEMIC/ACTOR/CAUSALITY/TERMINOLOGY.
7. `debug_trace` أصبح يعرض: detector, type, root_code, root_family, semantic_family, spans, confidence, suppressed_by, merged_into.
8. Meaning Mirror يعمل فقط على root issues النهائية بعد suppression/dedup، ولا يمكن لإشارة مخفية أن تصبح Representative Finding.

## نتيجة User Long Stress
- Alignment: **45 Arabic blocks ↔ 45 English blocks**
- Raw signals: **174**
- Public root issues: **57**
- Suppressed/merged signals: **117**
- Exact duplicate roots: **0**
- Generic uncertainty في فقرة الأرقام/التاريخ: **غير ظاهر للمستخدم**
- Dedicated roots في الفقرة نفسها:
  - `SIGNED_NUMBER_CONTRADICTION`
  - `DECIMAL_VALUE_CORRUPTION`
  - `DATE_AMBIGUITY_COLLAPSE`
- True semantic uncertainty remains public in the genuine uncertainty cases.
- Terminology fallback noise: **0**
- malformed `750→00` / `30→0`: **0**
- Mirror representative: **reference fabrication / unsafe source substitution**
- Stability check: **20/20 identical root ordering + identical Mirror**

## الاختبارات
- Pytest: **266/266 PASS**
- Local synthetic benchmark: Precision **1.000**, Recall **1.000**, F1 **1.000**, FPR **0.000**, Critical Error Recall **1.000**
- Adversarial: **48/48**
- Jury stress: **37/37**
- Release smoke: **16/16**
- Long-text stress: **7/7 injected classes detected**
- Repeatability: **200/200**
- Source audit: **0 errors**
- Documentation consistency: **PASS**

> هذه نتائج تطوير داخلية/اصطناعية وليست تحققًا ميدانيًا مستقلًا.

## ملفات القبول
- `evaluation/USER_LONG_STRESS_V15_6_ACCEPTANCE.json`
- `evaluation/USER_LONG_STRESS_V15_6_ROOT_ISSUES.txt`
- `evaluation/V15_6_ACCEPTANCE_AUDIT.json`
- `tests/test_v15_6_semantic_dedup_specificity.py`

## ملاحظة معمارية
V15.6 لا يحذف detector عام من النظام لمجرد وجود detector أدق. الإشارة العامة تبقى Evidence قابلة للتتبع، بينما الـpublic issue set يمر بمرحلة fusion/suppression منفصلة. هذا يحافظ على explainability ويمنع تضخيم عدد الفجوات في الوقت نفسه.
