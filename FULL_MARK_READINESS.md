# Full-Mark Readiness — V15.20

| المعيار | ما يطلبه أعلى مستوى | ما يراه الحكم الآن | فجوة لا يجوز اختلاقها |
|---|---|---|---|
| التقنية 25% | استقرار + منهجية + تكرار + تحسن قابل للتحقق | 348 regression، ablation، repeatability، audits، architecture | semantic-AI-only baseline يحتاج النموذج المحلي إذا أراد الحكم إعادة تشغيله |
| الموثوقية 15% | مصادر + تناقض/نقص + تتبع + امتناع + مراجعة | Quran/Hadith audits، live-vs-local separation، provider failure abstention، provenance | validation بشري مستقل ليس مكتملًا |
| الابتكار 15% | أفضلية على بديل محدد وحدود المقارنة | comparative positioning + ablation على نفس set | لا ندعي مسحًا شاملًا لكل منتجات السوق |
| UX 10% | إنجاز المهمة + وضوح + اختبار فئة | writer-first UI + أمثلة جاهزة + Meaning Mirror | usability study بشري فعلي غير موجود |
| النفع 20% | تحسن مقاس ومتكرر داخل النطاق | benchmark/stress/black-box/sacred audits + measurable impact | لا يوجد before/after بشري مستقل |
| التشغيل 10% | تكلفة/اعتمادات/صيانة/بدائل/تبني | measured resource profile + fallbacks + responsibility/adoption matrix | تكلفة الاستضافة النهائية تعتمد على مزود النشر |
| العرض 5% | موجز + دليل + إعادة اختبار + فصل المنجز عن المقترح | START_HERE + judge_verify + release_check + evidence map | Live URL/GitHub/video/PPT عناصر خارجية يجب رفعها فعليًا |

## أهم مبدأ
الدرجة الكاملة قرار اللجنة. هدف الحزمة هو أن **كل ادعاء يمكن رؤيته أو إعادة اختباره**، وأن ما لم يُثبت بعد لا يُعرض كحقيقة.
