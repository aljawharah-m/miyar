# Comparative Positioning — موقع مِعيار بين الأدوات الأقرب

هذه ليست مراجعة سوق شاملة؛ هي مقارنة مركزة مع أقرب أنواع الأدوات التي عثرنا عليها ويمكن للمحكم فتح مصادرها مباشرة.

| الأداة/الفئة | وظيفتها الأساسية | ما لا تغطيه مقارنة بمِعيار |
|---|---|---|
| **QuranEnc** | مصدر موثوق لترجمات معاني القرآن عبر API على مستوى السورة/الآية | ليس بوابة فحص لترجمة مستخدم قبل النشر، ولا يكتشف تلقائيًا تغيّر الحكم/الشرط/العدد/المرجع داخل ترجمة واردة |
| **HadeethEnc** | موسوعة/API للأحاديث بعدة لغات مع استرجاع حديث مفرد وبياناته | مصدر مرجعي، وليس Translation Safety Gate ولا يجمع root-cause/evidence fusion/human-review policy |
| **Qurān Cross-Lingual Translation Auditor** (مشروع بحثي مفتوح المصدر) | يسجل مدى حفظ خمس ترجمات إنجليزية منشورة للقرآن بالاعتماد على lexical/root-semantic scoring | يركز على ترجمات قرآنية محددة منشورة؛ لا يستقبل arbitrary user translation كـpre-publication gate، ولا يغطي الحديث أو source-integrity/abstention workflow كما في مِعيار |
| **مِعيار** | فحص ترجمة عربية→إنجليزية موجودة **قبل النشر** | يجمع semantic drift + critical invariants + terminology + Quran/Hadith retrieval + source integrity + evidence fusion + abstention + human review |

## ما الذي نعدّه إضافة مِعيار؟

1. **مرحلة مختلفة من سير العمل:** لا يولد ترجمة؛ يفحص ترجمة موجودة قبل اعتمادها.
2. **Root cause وليس similarity score فقط:** يميز حكمًا، نفيًا، شرطًا، استثناءً، عددًا، مرجعًا، مصطلحًا، ودرجة يقين.
3. **المصدر جزء من القرار لا مجرد رابط:** يفصل local recognition عن live verification ويمنع إعلان Verified بلا نص مسترجع.
4. **Safety behavior:** إذا لم يكف الدليل، النتيجة Review/Abstain بدل اختلاق تصحيح أو نسبة دينية.
5. **Human-review handoff:** النتيجة مصممة لتوجيه المراجع إلى موضع الخلل وسببه، لا لاستبداله.

## مصادر المقارنة

- QuranEnc API: https://quranenc.com/en/home/api/
- HadeethEnc API repository: https://github.com/islamhouse-dev/hadith-api
- Quran Translation Auditor: https://github.com/kayShahbaaz/quran-translation-auditor

## حد الادعاء

لا يدّعي هذا الملف عدم وجود أي منتج مشابه في العالم. الادعاء القابل للدفاع هو أن **التركيب والـworkflow المحدد في مِعيار** يختلف عن هذه الأدوات الأقرب التي تم فحصها، وأن الفرق قابل للتجربة داخل المنتج نفسه.
