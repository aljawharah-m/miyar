# مِعيار 1.0 — V15.20 Submission-Ready

> **ابدأ من هنا:** `START_HERE_FOR_JUDGES.md` يلخص المشكلة، التميّز، الأدلة، وأسرع طريقة لإعادة الاختبار خلال دقيقة.

> **Engine baseline:** V15.18 Final Verified. V15.20 لا يوسّع النطاق الديني؛ يحدّث واجهة التجربة والتوثيق وإتاحة التحقق للحكم، مع الحفاظ على اختبارات V15.18.

> **آخر تحقق مثبت داخل الحزمة:** 348/348 regression، فحص Quran corpus على 6,236 آية، Quran/Hadith reference audits، provider-failure abstention، repeatability 200/200. التفاصيل في `FINAL_V15_20_SUBMISSION_READY_REPORT.md`.

> **سليمة لغويًا ≠ دقيقة دلاليًا**

**تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي**  
المسار: **صناعة المحتوى متعدد اللغات والتوطين الثقافي**

مِعيار هو **Explainable Multi-Layer Translation Safety Gate for Islamic Content**: بوابة أمان قبل النشر تراجع ترجمة عربية→إنجليزية موجودة بالفعل، وتكشف تغيّر المعنى والقيود والمصطلحات والاستشهادات قبل وصول النص إلى الجمهور.

## Source-grounded safety boundary (V15.7)

**مِعيار لا يصدر أحكامًا شرعية جديدة؛ بل يحمي الحكم والمصطلح والدليل الموجود أصلًا من التحريف أثناء انتقاله بين اللغات.**

- الاسترجاع من QuranEnc/HadeethEnc يثبت ما تم استرجاعه من المرجع فقط؛ لا يعني اعتماد ترجمة المستخدم تلقائيًا ولا اعتماد صحة الحكم الشرعي الأصلي.
- كل Finding يحمل `issue_taxonomy` من: `RELIGIOUS_SEMANTIC`, `GENERAL_SEMANTIC`, `LOGIC_NUMERIC`, `SOURCE_INTEGRITY`, `EPISTEMIC`، وحقلًا منفصلًا `religious_impact`.
- المصادر المقترحة مثل TerminologyEnc/الدرر السنية/الموسوعة الفقهية الكويتية/ICADB لا تظهر كـ used evidence إلا إذا حدث استرجاع فعلي أو استُخدمت قاعدة محلية موثقة صراحة.
- المعرّفات التجريبية `TEST/MOCK/DEMO/ABC` لا تُرسل إلى مصادر خارجية في سياق الاختبار.
- لا تُختلق أرقام إصدارات: `source_version=None` إذا لم يعدها المصدر، مع `retrieved_at` وURL/translation key حيث تتوفر.

## ما الذي يميز مِعيار؟

مِعيار ليس مترجمًا ولا محرك فتوى. يجيب عن سؤال واحد محدد:

> هل انتقل المعنى نفسه، بقيوده ودقة مصطلحاته، من الأصل العربي إلى الترجمة؟

قد تكون الترجمة طبيعية جدًا ومع ذلك تسقط `إلا`، تغيّر `يجوز` إلى `must`، تغيّر رقمًا، أو تختزل مصطلحًا شرعيًا دقيقًا إلى معنى أوسع أو أضيق.

## أين الذكاء الاصطناعي؟

المسار هجين مقصود:

- **Multilingual Semantic AI**: نموذج `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` لقياس الانجراف الدلالي العام عبر اللغتين.
- **Critical Meaning Invariants**: نفي، شرط، استثناء، حصر، درجة حكم، كمية، نطاق، نسبة وتوثيق.
- **Terminology Guard**: 49 قاعدة/صف provenance مصطلحي، لكل واحدة أساس موثق و`verification_locator` مباشر قابل للتتبع.
- **Source Recognition + Trusted Retrieval**: QuranEnc / HadeethEnc، مع ICADB/TerminologyEnc ضمن المسار المرجعي.
- **Reference Alignment**: محاذاة المقطع المسترجع مع المقطع الذي يراجعه المستخدم قبل كشف التعارض.
- **Evidence Fusion**: الدليل المستخدم فعليًا منفصل عن المرجع المقترح.
- **Abstention + Human Review**: لا يعيد صياغة الحالات غير الآمنة ولا يخمّن عند نقص الدليل.

القواعد ليست بديلًا عن AI؛ هي guardrails لحالات عالية الأثر لا يكفي فيها similarity عام. `evaluation/run_ablation.py` يوضح مساهمة الطبقات على مجموعة التطوير.

## تجربة الكاتب

1. يدخل الأصل العربي والترجمة الإنجليزية.
2. يحصل على قرار ما قبل النشر.
3. يستطيع فتح **الفجوات المكتشفة** عند الحاجة بدون ازدحام الصفحة.
4. يرى فقط **التصحيحات الآمنة المقترحة** بصيغة: الموضع → قبل → بعد → السبب.
5. بقية الحالات تظهر تحت **فجوات تحتاج مراجعة بشرية**.
6. **مرآة المعنى** تشرح الفرق الذي قد يصل للقارئ.
7. إذا تم التعرف على آية/حديث واسترجاع مرجع موثوق فعليًا، يظهر قسم **التحقق من الترجمة بالمراجع الموثوقة**: الأصل → ترجمة المستخدم → المرجع الموثوق → ماذا استفاد مِعيار من المرجع.

لا يوجد زر تطبيق تلقائي للتصحيحات ولا إعادة فحص آلية. الكاتب يحرر الترجمة بنفسه ثم يعيد الفحص من زر الفحص الأساسي.

### سياسة التصحيح في V15.2
اقتراح التصحيح الآمن محصور في **استبدال مصطلحي ذري عالي الثقة** عندما يكون هو المشكلة الوحيدة في الجملة. لا يقترح مِعيار إعادة كتابة النفي أو الشرط أو الاستثناء أو درجة الحكم أو الأرقام؛ هذه تبقى للمراجعة البشرية حتى لا يصنع تحريفًا جديدًا أثناء "الإصلاح".

## تشغيل سريع

```powershell
python -m pip install -r requirements.txt
python scripts/release_check.py
python scripts/preflight.py
python -m streamlit run app.py
```

أو على Windows:

```bat
prepare_demo.bat
run_miyar.bat
```

## إثباتات قابلة لإعادة الاختبار

```powershell
python -m pytest -q
python evaluation/run_benchmark.py
python evaluation/run_adversarial.py
python evaluation/run_ablation.py
python evaluation/run_repeatability.py
python evaluation/run_release_smoke.py
python evaluation/run_jury_stress.py
python evaluation/run_long_text_stress.py
python evaluation/run_resource_profile.py
python scripts/source_audit.py
python scripts/doc_consistency_check.py
python scripts/release_check.py
```

ولمقارنة **Semantic-AI-only** مع مِعيار الكامل بعد تجهيز النموذج المحلي:

```powershell
python scripts/preflight.py
python evaluation/run_baselines.py
```

## الموثوقية والمصادر

- كل قاعدة مصطلحية لها صف provenance مباشر في `data/terminology_provenance.json` مع `verification_locator` يمكن للمحكم الرجوع إليه.
- المصفوفة المقروءة: `docs/TERMINOLOGY_PROVENANCE_MATRIX.md`.
- القواعد اللغوية العامة موثقة بمنهج ومراجع عامة في `data/linguistic_method_references.json` و`docs/LINGUISTIC_METHOD_REFERENCES.md`.
- تنفيذ توجيه المرشد موثق في `docs/MENTOR_FEEDBACK_IMPLEMENTATION.md` و`docs/MENTOR_SOURCE_ALIGNMENT.md`.
- الصفوف الرسمية تبقى مميزة عن سياسات مِعيار الهندسية.
- المصدر يؤصل معنى المصطلح؛ أما تصنيف مقابل إنجليزي على أنه risky/review فهو سياسة سلامة هندسية معلنة وقابلة للاختبار، لا فتوى ولا اقتباس مزيف.
- المرجع الخارجي لا يظهر كـ«دليل مستخدم» إلا إذا تم استرجاعه فعليًا.

## إتاحة التحقق السريع

- `START_HERE_FOR_JUDGES.md` — خريطة دقيقة للحكم.
- `python scripts/judge_verify.py` — تحقق سريع من Evidence المشحونة.
- `python scripts/release_check.py` — إعادة حساب deterministic suite كاملة.
- `docs/MEASURABLE_IMPACT.md` — الأثر القابل للقياس وحدود دلالته.
- `docs/COMPARATIVE_POSITIONING.md` — مقارنة موثقة مع أقرب الأدوات.

## حدود الادعاء

نتائج benchmark المرفقة **Development/Synthetic Evidence** وليست تحققًا ميدانيًا مستقلًا ولا يجوز عرضها كـ«دقة 100% في العالم الحقيقي».

للوصول إلى أقوى مستوى تحكيم، جهزنا:
- `docs/EXTERNAL_VALIDATION_PROTOCOL.md`
- `docs/USABILITY_VALIDATION_PROTOCOL.md`
- `data/external_validation_template.csv`
- `data/usability_test_template.csv`

هذه الملفات لا تحتوي نتائج مختلقة؛ يجب تعبئتها بواسطة مراجعين/مستخدمين حقيقيين قبل الادعاء بوجود validation مستقل.

## أهم ملفات التحكيم

- `docs/JURY_SCORECARD.md`
- `docs/FULL_MARK_READINESS.md`
- `docs/CHALLENGE_ALIGNMENT.md`
- `docs/TERMINOLOGY_PROVENANCE_MATRIX.md`
- `docs/SOURCE_PROVENANCE.md`
- `docs/LINGUISTIC_METHOD_REFERENCES.md`
- `docs/MENTOR_FEEDBACK_IMPLEMENTATION.md`
- `docs/BENCHMARK.md`
- `docs/OPERATIONS.md`
- `docs/SAFETY.md`
- `TOOLS.md`, `LICENSES.md`, `LIMITATIONS.md`


## V15.8 — Source-grounded public safety contract
مِعيار يقيّم **سلامة انتقال المعنى** بين الأصل والترجمة. لا يصدر حكمًا شرعيًا جديدًا ولا يعتمد صحة الحكم الشرعي الأصلي. كل Finding عام يحمل taxonomy، subtype أدق، `religious_impact` وسبب هذا الأثر، وسجل provenance للمصدر/المحاذاة/الثقة. المرجع المسترجع يثبت ما تم التحقق منه فقط؛ `reference_verified` منفصل دائمًا عن `user_translation_verified`. المعرفات التجريبية TEST/MOCK/DEMO/ABC لا تُرسل للتحقق الخارجي.

نتائج Benchmark المنشورة في المشروع هي على **مجموعة تطوير صناعية حالية** وليست ادعاءً بدقة دينية 100% أو تحققًا ميدانيًا مستقلًا.

### V15.13 source-routing note
Natural Quran references such as `سورة البقرة، الآية 183` and quoted hadith text can be routed to trusted-source verification. A local locator identifies the candidate reference only; the UI reports completed external verification only after actual `live_verified` evidence is returned by the provider. Run `python scripts/preflight.py` on the deployment machine to verify live connectivity.
