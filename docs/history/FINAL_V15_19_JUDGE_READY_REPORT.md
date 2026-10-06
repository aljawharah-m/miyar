# Mi’yar V15.19 — Judge-Ready Submission Report

## الهدف
رفع قابلية التقييم وإعادة التحقق من محرك V15.18 الموثق، دون توسيع النطاق أو اختلاق validation خارجي.

## ما تغيّر
- أمثلة جاهزة داخل الواجهة: safe / ruling shift / reference shift.
- `START_HERE_FOR_JUDGES.md` كمسار قراءة مدته نحو دقيقة.
- `docs/MEASURABLE_IMPACT.md` لربط المقاييس بالنفع وحدودها.
- `docs/COMPARATIVE_POSITIONING.md` لمقارنة موثقة مع أقرب أدوات/مصادر.
- `scripts/judge_verify.py` و`JUDGE_VERIFY.bat` للتحقق السريع.
- `scripts/release_check.py` صار يشمل sacred corpus + Quran/Hadith reference + metadata/attribution/synthetic-ID audits.
- تحديث README/Handoff/Operations/Challenge Alignment/Jury Scorecard/Full-Mark Readiness إلى الحالة الحالية.

## تحقق بعد التعديل
- Pytest: **348/348 passed**.
- Judge quick verification: **PASS**.
- Documentation consistency: **PASS**.
- Release smoke: **16/16**.
- Source audit: Quran locator 6,236 rows؛ terminology provenance 49 rows؛ **0 errors**.
- Source metadata audit: **0 errors**.
- Attribution audit: **0 errors**.
- Synthetic IDs: **0 external calls**.

## Sacred-source evidence surfaced for judges
Stored audit evidence represents **62,490 deterministic checks**:
- **62,360 Quran checks** across recognition forms, explicit/numeric references, QuranEnc routing, safe references, ayah mutations and surah mutations.
- **130 Hadith checks** across safe references, semantic mutations, provider failure and structured IDs.

هذا العدد يمثل عمليات تحقق داخل الـaudit، وليس 62,490 نصًا مستقلًا، ولا يُقدّم كدقة دينية شاملة.

## الادعاء النهائي القابل للدفاع
مِعيار هو **pre-publication translation safety gate** لترجمة عربية→إنجليزية موجودة؛ يجمع semantic AI وcritical invariants والمصطلحات والمراجع الموثوقة وEvidence Fusion والامتناع والمراجعة البشرية، بهدف منع انتقال تحريف دلالي عالي الأثر إلى المحتوى المنشور.
