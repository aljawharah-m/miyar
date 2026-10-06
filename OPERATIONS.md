# تشغيل واستمرارية مِعيار 1.0 — Judge-Ready

## الاعتمادات الحرجة والبدائل

| الاعتماد | الوظيفة | عند التعطل |
|---|---|---|
| Python + Streamlit | واجهة وتشغيل التطبيق | لا توجد خدمة بدون runtime؛ موثق في requirements وتشغيل Windows |
| `sentence-transformers` | إشارة semantic AI محلية | تستمر deterministic/terminology/source layers ويُعلن غياب الإشارة بدل اختلاقها |
| QuranEnc | مرجع حي للقرآن | local locator لا يتحول إلى Verified؛ Review/Abstention عند الحاجة للحسم |
| HadeethEnc | مرجع حي للحديث | لا اعتماد لمرجع حي؛ Review/Abstention بدل تخمين المصدر |
| Terminology provenance المحلي | guardrails المصطلحية | source audit يفشل قبل الإصدار إذا نقص صف provenance |

## قياس تشغيلي فعلي داخل الحزمة

`evaluation/resource_profile.json` للـdeterministic/offline path:
- Median latency: **395 ms**
- P95: **431 ms**
- Max: **439 ms**
- Peak process RSS: **~98.7 MiB**

هذه أرقام بيئة القياس وليست SLA للإنتاج؛ الشبكة والنموذج الدلالي يختلفان حسب بيئة النشر.

## التكلفة

- المسار الأساسي لا يستدعي API توليديًا مدفوعًا لكل فحص.
- النموذج الدلالي يعمل محليًا بعد التنزيل الأول.
- QuranEnc/HadeethEnc dependencies خارجية؛ لا يسجل المشروع تكلفة استضافة غير مقاسة.
- نموذج تكلفة التبني: **تكلفة الاستضافة + تشغيل Python/Streamlit + شبكة المصادر**؛ لا توجد variable LLM-token cost في المسار الأساسي.

## الصيانة والمسؤوليات

- كل تعديل detector حرج → regression test.
- كل قاعدة مصطلحية → provenance row.
- قبل كل إصدار: `python scripts/release_check.py`.
- قبل العرض/النشر: `python scripts/preflight.py`.
- بعد تحديث provider أو terminology source: source/metadata/attribution audits.

مسؤوليات التبني:
- تقني: المحرك، الاختبارات، الأداء، provider adapters.
- لغوي/مترجم: equivalence وparaphrase وFalse Positives.
- مختص شرعي: اعتماد السياسات الحساسة والحالات الخلافية.
- مسؤول محتوى: Human Review وسجل القرار.

## خطة تبني واقعية

1. Pilot عربي→إنجليزي على فريق ترجمة واحد.
2. Held-out review مستقل لا يبنيه فريق التطوير.
3. قياس FP/FN ووقت المراجعة.
4. Governance للمصطلحات والمراجع.
5. تثبيت monitoring للمصادر الخارجية.
6. توسيع لغة/نوع محتوى جديد فقط بعد اجتياز acceptance gate مستقل.
