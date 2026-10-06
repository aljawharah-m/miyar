# مِعيار 1.0 — Jury Scorecard V15.20

هذه الخريطة تربط كل معيار نهائي في دليل التحدي بدليل قابل للفحص داخل الحزمة.

## 25% جودة الحل التقني وتوظيف الذكاء الاصطناعي

**الهدف الأعلى:** نتائج مستقرة ومتكررة، منهجية وقيود موثقة، وتحسن قابل للتحقق.

**الدليل:**
- `core/` pipeline: alignment → semantic units/rules → terminology → semantic AI → sources → evidence fusion → decision/human review.
- `evaluation/ablation_report.json`: الطبقات المنفردة أقل Recall من التركيب الكامل على نفس development set.
- `evaluation/repeatability_report.json`: 200/200.
- `FINAL_V15_18_VERIFICATION_REPORT.md`: 348/348 regression + sacred-reference verification evidence.

## 15% الموثوقية والسلامة العلمية

**الهدف الأعلى:** اتساق عبر المجموعة، معرفة الحدود، تتبع المصادر، امتناع وإحالة صحيحة.

**الدليل:**
- local recognition منفصل عن live verification.
- payload ناقص/provider failure لا ينتج Verified.
- ambiguity → candidates/Review بدل اختيار مرجع واحد.
- source/metadata/attribution/synthetic-ID audits.
- Quran/Hadith verification reports.
- `LIMITATIONS.md` يعلن ما لا يثبته النظام.

## 15% الابتكار والقيمة المضافة

**الهدف الأعلى:** أفضلية قابلة للاختبار على بديل محدد مع حدود واضحة.

**الدليل:**
- `docs/COMPARATIVE_POSITIONING.md` يضع مِعيار مقابل QuranEnc/HadeethEnc وأداة Quran translation auditing الأقرب.
- `evaluation/ablation_report.json`: similarity/rule/terminology style layers منفردة أقل تغطية من pipeline المركب.
- novelty claim محدود: **pre-publication safety gate لترجمة المستخدم نفسها**، وليس الادعاء بعدم وجود أي أداة مشابهة عالميًا.

## 10% تجربة المستفيد والتواصل والإتاحة

**الهدف الأعلى:** المستخدم ينجز المهمة ويفهم الخطأ والخطوة التالية.

**الدليل:**
- RTL writer-first UI.
- قرار نشر + Root finding + أثر ديني + الخطوة التالية.
- Meaning Mirror.
- progressive disclosure بدل تقرير تقني كثيف.
- أمثلة جاهزة: سليم / تغيّر حكم / تغيّر مرجع.
- لا auto-rewrite للحالات الحساسة.

## 20% تحقيق النفع وفق معيار نجاح المسار

**الهدف الأعلى:** تحسن واضح ومتكرر بمؤشر مناسب وحدود موثقة.

**الدليل:** `docs/MEASURABLE_IMPACT.md`:
- benchmark development metrics.
- Critical Error Recall.
- adversarial/jury/long-text/repeatability.
- V15.16 black-box campaign.
- Quran/Hadith reference and semantic audits.
- `docs/REVIEWER_WORKLOAD_EVIDENCE.md`: 175 raw signals → 59 root findings، أي **66.3%** تقليل ضوضاء في development stress task.

**الحد:** لا ندعي field validation أو review-time reduction بشريًا دون قياس حقيقي.

## 10% واقعية التشغيل والاستكمال

**الهدف الأعلى:** تكلفة واعتمادات وصيانة وبديل للاعتماد الحرج وخطة تبني.

**الدليل:**
- `docs/OPERATIONS.md` dependency/fallback matrix.
- measured offline resource profile: median 395ms, p95 431ms, peak RSS ~98.7 MiB في بيئة القياس.
- لا paid generative API per check في المسار الأساسي.
- provider/model failures لها safe fallback.
- adoption and responsibility plan.

## 5% وضوح العرض وإتاحة التحقق

**الهدف الأعلى:** موجز، منظم، يسهل إعادة الاختبار ويفصل المنجز عن المقترح.

**الدليل:**
- `START_HERE_FOR_JUDGES.md`.
- `python scripts/judge_verify.py`.
- `python scripts/release_check.py`.
- stored JSON evidence reports.
- `LIMITATIONS.md` + explicit development-evidence labeling.

## أسرع تجربة
1. شغّل التطبيق.
2. اضغط **تغيّر حكم** ثم افحص.
3. اضغط **تغيّر مرجع** ثم افحص.
4. اضغط **مثال سليم** وتأكد أن اختلاف الصياغة لا يولد إنذارًا.
