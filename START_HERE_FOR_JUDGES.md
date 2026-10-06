# مِعيار 1.0 — ابدأ من هنا

## Judge Quick Access

| Resource | Link |
|---|---|
| Live Demo | https://miyar-gate.streamlit.app/ |
| 2-minute Demo Video | https://drive.google.com/file/d/1wZnfSNLZjkicoM3Fa1lVwUVDSPO_dU5E/view?usp=sharing |
| Source Code | https://github.com/aljawharah-m/miyar |
| Quick Verification | python scripts/judge_verify.py |

> Evaluation claims in this repository are Development/Audit evidence within the documented test scope, not a claim of universal religious accuracy.

---


**المسار:** صناعة المحتوى متعدد اللغات والتوطين الثقافي
**مواءمة المسار:** النسخة الحالية تركز بعمق على طبقة الأمان السابقة للتوطين: المحافظة على الدلالة الشرعية ودقة المصطلحات، ولا تدعي تنفيذ التوطين الثقافي الكامل.
**النطاق:** مراجعة ترجمة عربية→إنجليزية موجودة قبل النشر
**ليس مترجمًا ولا محرك فتوى.**

> **الفكرة في سطر واحد:** مِعيار يمنع أن تكون الترجمة سليمة لغويًا لكنها تغيّر حكمًا أو قيدًا أو مصطلحًا أو رقمًا أو مرجعًا دينيًا أثناء انتقال المعنى.

## أسرع طريقة لتجربة القيمة

شغّل التطبيق ثم اختر أحد الأمثلة الجاهزة أعلى حقول الإدخال:

1. **مثال سليم** → يجب ألا يختلق فجوة لمجرد اختلاف ترتيب الكلمات.
2. **تغيّر حكم** → `جائز` → `obligatory` يجب أن يظهر كـ **نقل حكم شرعي**.
3. **تغيّر مرجع** → البقرة 183 → 185 يجب أن يظهر كـ **SOURCE_INTEGRITY**.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.fileWatcherType none
```

## لماذا مِعيار ليس مجرد Regex؟

المحرك يجمع بين:
- multilingual semantic AI لالتقاط الانجراف عند اختلاف الصياغة؛
- invariants حتمية للحالات عالية الأثر: النفي، الشرط، الاستثناء، الحكم، العدد، النسبة والمرجع؛
- Terminology Guard موثق؛
- QuranEnc/HadeethEnc للاسترجاع الموثوق عند الحاجة؛
- Evidence Fusion لتجميع الأعراض في Root Cause؛
- Abstention + Human Review عند ضعف الدليل.

دراسة ablation المرفقة توضح أن الطبقات المنفردة أقل تغطية من التركيب الكامل. انظر `evaluation/ablation_report.json`.

## أدلة قابلة لإعادة الاختبار

**آخر تحقق مثبت للمحرك:**
- Regression: **348/348 passed**.
- القرآن: **6,236/6,236** تعرّف كامل/بلا تشكيل/داخل اقتباس/في سياق طبيعي، دون ربط خاطئ؛ النص المتكرر يبقى Ambiguous بدل التخمين.
- Sacred-source audit المخزن يجمع **62,490 فحصًا deterministic**: 62,360 للقرآن + 130 للحديث، موزعة على التعرف والمراجع والتحريفات وفشل المزود؛ الرقم يمثل checks وليس نصوصًا مستقلة.
- Reference integrity: **6,236** مراجع سليمة دون false positives + **6,236** تغييرات رقم آية مكتشفة + **6,236** تغييرات سورة مكتشفة.
- Quran semantic audit: **24** safe cases بلا false positives + **31** mutations بلا miss.
- Hadith reference audit: **20** safe cases بلا false positives + **50** semantic mutations بلا miss.
- Repeatability: **200/200** comparisons.
- Development benchmark: Precision/Recall/F1/FPR موثقة في `evaluation/benchmark_report.json`.

> هذه **Development/Audit Evidence** وليست ادعاء دقة دينية شاملة أو تحققًا ميدانيًا مستقلًا.

## كيف تتعامل السلامة مع المصادر؟

- التعرف المحلي على آية/حديث **لا يساوي** تحققًا حيًا.
- `live_verified` لا يُعلن إلا بعد استرجاع نص مرجعي فعلي.
- إذا فشل QuranEnc/HadeethEnc أو عاد payload ناقص: **Review/Abstention** بدل Verified وهمي.
- معرفات `TEST/MOCK/DEMO/ABC` لا تُرسل للمصادر الخارجية.
- صحة الحكم الشرعي الأصلي خارج نطاق مِعيار؛ مِعيار يراجع **سلامة انتقاله** فقط.

## النفع القابل للقياس داخل النطاق

- Critical errors في مجموعة التطوير: `critical_error_recall = 1.0`.
- Full deterministic pipeline رفع Recall من **0.4762** في structure-only و**0.5238** في terminology-only إلى **1.0** على مجموعة التطوير نفسها.
- deterministic/offline path: median **395 ms**، p95 **431 ms**، peak RSS نحو **98.7 MiB** في بيئة القياس.
- Evidence Fusion على stress document الحالي: **175 raw signals → 59 root findings**، أي **66.3% تقليل ضوضاء** قبل عرض التنبيهات للمراجع.
- المسار الأساسي لا يحتاج API توليدي مدفوع لكل فحص.

التفاصيل: `docs/MEASURABLE_IMPACT.md` و`docs/REVIEWER_WORKLOAD_EVIDENCE.md` و`docs/OPERATIONS.md`.

## ما الإضافة مقارنة بأقرب الأدوات؟

راجع `docs/COMPARATIVE_POSITIONING.md`.

الخلاصة: المصادر مثل QuranEnc/HadeethEnc توفر محتوى موثوقًا؛ وبعض أدوات البحث تقارن ترجمات قرآنية منشورة؛ **مِعيار يتموضع كـ pre-publication safety gate لترجمة المستخدم نفسها** ويجمع سلامة المعنى + الحكم + المصطلح + الأرقام + المراجع + الامتناع + المراجعة البشرية.

## أمر تحقق واحد

```powershell
python scripts/judge_verify.py
```

ولإعادة الحزمة الثقيلة كاملة:

```powershell
python scripts/release_check.py
```

## أهم الملفات

- `FINAL_VERIFICATION_REPORT.md`
- `docs/MEASURABLE_IMPACT.md`
- `docs/COMPARATIVE_POSITIONING.md`
- `docs/JURY_SCORECARD.md`
- `docs/SAFETY.md`
- `docs/SOURCES.md`
- `docs/OPERATIONS.md`
- `LIMITATIONS.md`
