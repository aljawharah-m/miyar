# مواءمة مِعيار مع معايير التحكيم النهائي

**المسار:** صناعة المحتوى متعدد اللغات والتوطين الثقافي.

مِعيار يركز على **سلامة المعنى السابقة للنشر**: ألا تغير الترجمة حكمًا أو قيدًا أو مصطلحًا أو كمية أو نسبة أو مرجعًا، مع إتاحة المصدر والمراجعة البشرية.

## 25% جودة الحل التقني والـAI
- multilingual semantic AI + deterministic critical invariants.
- paragraph/local alignment + evidence fusion + root-cause suppression.
- source recognition/retrieval + terminology provenance.
- 348/348 regression على verified engine + repeatability 200/200.
- ablation يثبت أن الطبقات المنفردة أقل تغطية على نفس development set.

## 15% الموثوقية والسلامة
- QuranEnc/HadeethEnc live evidence منفصل عن local recognition.
- provider failure أو payload ناقص لا ينتج Verified وهمي.
- ambiguity لا تتحول إلى مرجع مخمّن.
- Human Review/Abstention عند ضعف الدليل.
- Quran/Hadith audits مرفقة وقابلة لإعادة التشغيل.

## 15% الابتكار والقيمة المضافة
- workflow مختلف عن الترجمة: pre-publication safety gate لترجمة موجودة.
- لا يكتفي similarity score؛ يحدد root cause عالي الأثر.
- مقارنة أقرب الأدوات في `docs/COMPARATIVE_POSITIONING.md`.
- ablation قابل للتكرار في `evaluation/ablation_report.json`.

## 10% تجربة المستفيد
- قرار نشر واضح، RTL، progressive disclosure، Meaning Mirror، خطوة تالية.
- أمثلة جاهزة داخل الواجهة تتيح فهم المنتج بنقرة واحدة.
- لا تعديل تلقائي للنص في الحالات غير الآمنة.

## 20% تحقيق النفع
- Critical Error Recall وFPR موثقان على development set.
- stress/adversarial/repeatability/black-box/sacred-reference evidence.
- `docs/MEASURABLE_IMPACT.md` يميز النتائج المقاسة عن validation غير المنجز.

## 10% واقعية التشغيل
- local-first، لا token API cost أساسي، fallbacks صريحة.
- resource profile فعلي + dependency/failure matrix + adoption plan في `docs/OPERATIONS.md`.

## 5% وضوح العرض وإتاحة التحقق
- `START_HERE_FOR_JUDGES.md`.
- `python scripts/judge_verify.py` للتحقق السريع.
- `python scripts/release_check.py` لإعادة الاختبار الكامل deterministic.
- الادعاءات مرتبطة بملفات Evidence وحدودها معلنة.
