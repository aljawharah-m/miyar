# Mi’yar 1.0 — V15.5 Clean Root Findings Release

## هدف الإصدار
V15.5 يغلق edge bugs التي بقيت بعد V15.4، خصوصًا سلامة استخراج الأرقام، ربط المصطلحات بمقاطع aligned فعلية، deduplication/fusion، ترتيب مرآة المعنى، استقلالية الثقة، وفصل test identifiers عن المصادر الدينية الحقيقية.

## الإصلاحات الجذرية

### 1. Robust Numeric Extraction
- أزيل سبب تقطيع القيم متعددة الخانات الناتج عن greedy regex backtracking.
- أضيف numeric token bounded pattern يحافظ على الرقم كاملًا.
- `750 → 700` يظهر الآن 750 كاملًا.
- `30 days → 3 days` يظهر الآن 30 كاملًا.
- دعم واختبار: integers, thousands, comma thousands, signed numbers, decimals, percentages, times, dates.
- ربط الأرقام بأدوارها الدلالية المتخصصة بدل المقارنة الخام كلما وجد detector أدق: total, duration, percentage, threshold, reference, time, unit.

### 2. Evidence-bound Terminology
- dictionary miss وحده لم يعد user-facing finding.
- unresolved local term يصبح `UNCERTAIN_TERMINOLOGY_EVIDENCE` داخل checks/trace فقط.
- user-facing terminology finding يحتاج target span واضح risky/review أو omission عالي الخطورة موثق.
- اختفى noise السابق مثل `النية` و`الحديث` من long-stress result بلا دليل target aligned.
- بقيت الحالات الصحيحة مثل Tawhid → oneness.

### 3. Reference/Test-ID Separation
- `TEST`, `MOCK`, `DEMO`, `ABC` identifiers داخل سياق مثال/اختبار لا تُرسل إلى external source recognition.
- تغيّر identifiers نفسه يبقى detectable محليًا كسلامة نقل، مثل `TEST-123 → TEST-321`.
- reference root findings تسبق generic numeric symptoms.

### 4. Stronger Root Fusion + Dedup
- dedup key يعتمد على segment + root family + type + normalized source/target spans + entity.
- generic symptom لا يعرض إذا root cause أدق يفسره.
- event order + causality لا يندمجان لأنهما مشكلتان مستقلتان بالفعل.
- raw signals تبقى diagnostics فقط.

### 5. Severity-ranked Meaning Mirror
المرآة لا تعتمد على أول finding. الترتيب يعتمد على:
1. severity
2. root impact priority
3. evidence specificity
4. span quality
5. confidence

في long stress الحالي أصبح أعلى ممثل هو `استُبدل الامتناع عن التحقق باختلاق مرجع` بدل مجرد أول finding في القائمة.

### 6. Confidence Independence
- لا تُجمع عدة keyword/count signals لنفس root family كأدلة مستقلة.
- diagnostics تعرض `independent_evidence_count`, `max_root_confidence`, `mean_independent_confidence`, alignment mode، وسياسة الثقة.
- generic evidence لا يرفع الثقة بمجرد كثرة التكرار.

### 7. Debug Trace بدون تلويث الواجهة العامة
- public UI يستمر بعرض root issues فقط.
- `MIYAR_DEBUG=1` يفتح Debug trace للمطور/الحكم.
- trace يتضمن detector/type/segment/confidence/suppressed_by/merged_into.

### 8. Safe Corrections
لم يتم توسيع التصحيح الآلي. قواعد الأمان السابقة بقيت محافظة، والحالات الدلالية/الغامضة/المراجع/تغيير الأحكام تبقى Human Review.

## اختبارات V15.5 الجديدة
أضيف `tests/test_v15_5_clean_root_findings.py` ويغطي 28 حالة جديدة تشمل:
- 750 / 30 وعدم تقطيع الأرقام
- 100 / 1000 / 10,000
- -1 / 1.5 / 0.25 / 2.5%
- dates / AM-PM
- asserted bad-example numbers
- thresholds
- AND/OR
- at least / exactly
- causality + event order
- actor/source attribution
- pronoun local abstention
- unresolved terminology evidence-only
- risky terminology remains public
- synthetic test IDs
- reference suppression
- root-family confidence
- debug trace
- dedup
- number roles
- full user long-stress acceptance

## Long Stress Acceptance
المصدر: `evaluation/USER_LONG_STRESS_ALIGNMENT.txt`

V15.4: 61 root issues.
V15.5: 58 root issues.

الانخفاض ليس حذفًا اصطناعيًا؛ أزيلت findings غير المؤسسة مثل global terminology fallbacks، بينما بقيت الأخطاء المستقلة الحقيقية.

Acceptance facts:
- alignment: 45 Arabic ↔ 45 English
- status: critical / غير جاهزة للنشر
- root issues: 58
- raw signals: 174
- exact duplicate root keys: 0
- malformed `00`: 0
- malformed `0 days`: 0
- unresolved terminology user-facing fallbacks: 0
- Meaning Mirror top root: source fabrication policy shift

الملفات:
- `evaluation/USER_LONG_STRESS_V15_5_ACCEPTANCE.json`
- `evaluation/USER_LONG_STRESS_V15_5_ROOT_ISSUES.txt`

## التحقق الكامل
- pytest: **254/254 passed**
- Benchmark (synthetic development set): Precision 1.000 / Recall 1.000 / F1 1.000 / FPR 0.000 / Critical Error Recall 1.000
- Adversarial: **48/48**
- Jury stress: **37/37**
- Release smoke: **16/16**
- Long-text stress: **7/7**
- Repeatability: **200/200**
- Source audit: no errors
- Documentation consistency: PASS
- Python compile checks: PASS

## Baseline / Preflight limitation in this execution environment
`run_baselines.py` يحتاج `sentence-transformers`. بيئة الاختبار الحالية لا تحتوي الحزمة ولا تسمح باتصال pip الخارجي، لذلك لم يتم اختلاق نتيجة baseline. `requirements.txt` ما زال يحتوي dependency الصحيحة، ويمكن تشغيل baseline في بيئة المشروع التي يتوفر فيها النموذج.

هذا limitation خاص ببيئة التشغيل المستخدمة هنا وليس regression في deterministic core.

## Research-informed design checks
- Semantic Role Labeling يدعم ربط predicate بالparticipants بدل عد الكلمات.
- Quantity extraction literature يؤكد أهمية ربط value بالunit/concept والسياق بدل استخراج الرقم وحده.
- MT evaluation literature يدعم تقييم meaning transfer وterminology fidelity بدل الاعتماد على surface form وحده.

V15.5 يطبق هذه المبادئ بصورة deterministic محافظة داخل نطاق المشروع، ولا يدعي أنه SRL model كامل أو independently validated field system.
