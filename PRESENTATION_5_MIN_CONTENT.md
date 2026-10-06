# محتوى العرض النهائي — 5 دقائق

## Slide 1 — المشكلة (35 ثانية)
**العنوان:** سليمة لغويًا ≠ دقيقة دلاليًا

- ترجمة سلسة قد تغيّر حكمًا أو شرطًا أو مصطلحًا أو رقمًا أو مرجعًا.
- الخطر ليس خطأ لغويًا؛ بل وصول معنى مختلف للقارئ.
- حالة الاستخدام: مراجعة ترجمة عربية→إنجليزية قبل النشر.

**الجملة الأساسية:**
> المشكلة التي نحلها ليست كيف نترجم، بل كيف نتأكد أن المعنى الحساس لم يتغير بعد الترجمة.

## Slide 2 — الحل والتميّز (40 ثانية)
**العنوان:** مِعيار: Translation Safety Gate قبل النشر

- Existing Arabic + existing English translation.
- Detect → Explain → Source-ground → Human Review.
- ليس مترجمًا ولا محرك فتوى.
- يختلف عن المصدر المرجعي نفسه وعن أدوات similarity العامة.

## Slide 3 — كيف يعمل (55 ثانية)
**العنوان:** Multi-layer, explainable, source-grounded

Pipeline مختصر:
1. Alignment
2. Critical meaning invariants
3. Terminology Guard
4. Semantic AI
5. Quran/Hadith source routing
6. Evidence Fusion / Root Cause
7. Risk + Confidence + Trace
8. Human Review

**النقطة المهمة:** القواعد لا تستبدل AI؛ تحمي الحالات التي قد يخفيها similarity العام.

## Slide 4 — Live Demo (70 ثانية)
اعرضي فقط:
- جائز → obligatory
- البقرة 183 → 185
- paraphrase سليمة

ركزي على القرار والـRoot والمرجع، لا تفتحي كل diagnostics.

## Slide 5 — إثبات قابل لإعادة التحقق (55 ثانية)
- 348/348 regression
- 62,490 sacred-source deterministic audit checks
- 6,236 Quran corpus recognition/reference coverage
- 200/200 repeatability comparisons
- 48/48 adversarial
- Evidence Fusion: 175 raw → 59 roots = 66.3% noise reduction on current stress document
- Ablation: structure-only recall 0.4762; terminology-only 0.5238; composed deterministic path 1.0 on the same synthetic development set

**قولي بوضوح:** Development/audit evidence، وليست field accuracy 100%.

## Slide 6 — السلامة والتشغيل والأثر (45 ثانية)
- No fabricated verification
- Provider failure → abstain/review
- Human remains final reviewer
- Median deterministic offline latency ~395ms; p95 ~431ms in measured environment
- No paid generative API required per core check
- Pilot path: فريق ترجمة → held-out validation → governance → scale

## النهاية (20 ثانية)
> مِعيار لا يحاول استبدال المترجم أو المختص الشرعي. هو يجعل فجوة المعنى مرئية وقابلة للتتبع قبل أن تصل إلى الجمهور.
