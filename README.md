# مِعيار | Mi’yar

## Judge Quick Access

| Resource | Link |
|---|---|
| Live Demo | https://miyar-gate.streamlit.app/ |
| 2-minute Demo Video | https://drive.google.com/file/d/1wZnfSNLZjkicoM3Fa1lVwUVDSPO_dU5E/view?usp=sharing |
| Judge Guide | [START_HERE_FOR_JUDGES.md](START_HERE_FOR_JUDGES.md) |
| Source Code | https://github.com/aljawharah-m/miyar |

**Quick verification:** python scripts/judge_verify.py

Challenge scope: Arabic to English - existing translation - text only - human final decision

---


## بوابة ذكية لمراجعة سلامة ترجمة المحتوى الإسلامي قبل النشر

> **سليمة لغويًا ≠ دقيقة دلاليًا**

قد تبدو الترجمة ممتازة لغويًا، بينما يسقط منها نفي، أو يتغير شرط، أو يُختزل مصطلح شرعي، أو يتبدل مرجع دون أن يكون الخطأ واضحًا للقارئ

**مِعيار** لا ينشئ ترجمة جديدة  
بل يراجع ترجمة موجودة بالفعل ويسأل:

> **هل انتقل المعنى نفسه، بقيوده ومصطلحاته ودليله، من الأصل العربي إلى الترجمة؟**

---

## 🚀 جرّب مِعيار الآن

### [فتح النسخة الحية →](https://miyar-gate.streamlit.app/)

**المسار:** صناعة المحتوى متعدد اللغات والتوطين الثقافي  
**النطاق الحالي:** نصوص · العربية → الإنجليزية · فحص قبل النشر

---

# مِعيار في 30 ثانية

يدخل المستخدم:

**النص العربي الأصلي + الترجمة الموجودة**

ثم يقوم مِعيار بـ:

1. محاذاة الأصل والترجمة
2. تحليل وحدات المعنى
3. كشف الحذف والإضافة والانجراف الدلالي
4. فحص النفي والشرط والاستثناء والحصر والأرقام ودرجة الحكم
5. مراجعة المصطلحات الدقيقة
6. التعرف على الآيات والأحاديث والمراجع
7. التحقق من المصدر عند توفر استرجاع موثوق
8. دمج الأدلة وتقدير الخطر والثقة
9. تفسير سبب التنبيه
10. إحالة الحالات غير الآمنة للمراجعة البشرية

النتيجة ليست فقط:

> "هناك اختلاف"

بل:

> **ماذا تغيّر؟ أين؟ لماذا هو مهم؟ وما الدليل الذي استند إليه التنبيه؟**

---

# المشكلة

أدوات الترجمة العامة تهدف أساسًا إلى إنتاج نص مفهوم وطبيعي

لكن في المحتوى الإسلامي قد تكون الجملة الإنجليزية سليمة جدًا لغويًا بينما يحدث تغير صغير ذو أثر كبير، مثل:

- سقوط نفي
- حذف شرط أو استثناء
- تغير درجة الحكم
- إضافة معنى غير موجود في الأصل
- اختزال مصطلح شرعي دقيق
- تغير رقم أو كمية
- تغير آية أو حديث أو مرجع

لذلك لا يسأل مِعيار:

> **هل الترجمة تبدو جيدة؟**

بل يسأل:

> **هل انتقل المعنى بأمان؟**

---

# مثال مباشر

### الأصل

`ورد المرجع: سورة البقرة، الآية 183.`

### الترجمة

`The reference is Surah Al-Baqarah, verse 185.`

الجملة الإنجليزية سليمة لغويًا

لكن المرجع تغير من:

**2:183 → 2:185**

مِعيار يستطيع:

- التعرف على المرجع الأصلي
- اكتشاف تغير رقم الآية
- تحديد أن المشكلة مرتبطة بسلامة المرجع
- التحقق من المصدر الموثوق عند نجاح الاسترجاع
- توضيح الفرق للمراجع
- عدم اعتبار الحالة جاهزة للنشر دون مراجعة

### [جرّب الحالة على النسخة الحية →](https://miyar-gate.streamlit.app/)

---

# الفكرة الأساسية

```text
النص العربي
      ↓
الترجمة الموجودة
      ↓
   فحص مِعيار
      ↓
كشف مواضع الخطر
      ↓
تفسير + دليل + ثقة
      ↓
المراجعة البشرية
      ↓
قرار النشر
```

## **مِعيار ليس مترجمًا آخر**
## **مِعيار طبقة أمان بين الترجمة والنشر**

---

# كيف يعمل المحرك؟

مِعيار يستخدم مسارًا هجينًا متعدد الطبقات:

```text
Preprocess
    ↓
Alignment
    ↓
Semantic Units
    ↓
Critical Meaning Rules
    ↓
Terminology Guard
    ↓
Multilingual Semantic AI
    ↓
Citation Detection
    ↓
Trusted Source Verification
    ↓
Evidence Fusion
    ↓
Risk + Confidence + Trace
    ↓
Human Review
```

السبب:

> **Semantic Similarity وحدها لا تكفي في الحالات عالية الأثر**

قد تكون جملتان متشابهتين جدًا دلاليًا بصورة عامة، بينما تغير كلمة واحدة المقصود جذريًا

مثل:

`يجوز`

مقابل:

`must`

---

# طبقات الحماية

### Multilingual Semantic AI

تحليل دلالي متعدد اللغات لاكتشاف الانجراف العام بين العربية والإنجليزية

النموذج المستخدم:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### Critical Meaning Invariants

طبقة مستقلة للحالات الحساسة مثل:

- النفي
- الشرط
- الاستثناء
- الحصر
- الكمية
- الأرقام
- النطاق
- درجة الحكم
- الإسناد والاستشهاد

### Terminology Guard

حماية للمصطلحات الدقيقة التي قد يؤدي تبسيطها أو استبدالها إلى تغير المقصود

الحزمة الحالية تتضمن:

**49 صفًا موثقًا في Terminology Provenance**

مع معلومات قابلة للتتبع عن أساس كل قاعدة ومصدر التحقق منها

### Trusted Source Verification

عند التعرف على مرجع قابل للتحقق، يدعم مِعيار الاسترجاع من مصادر موثوقة مثل:

- **QuranEnc**
- **HadeethEnc**

مع فصل واضح بين:

**التعرف على المرجع**

و

**نجاح التحقق الخارجي الفعلي**

### Evidence Fusion

يفصل مِعيار بين:

- المصدر المقترح
- القاعدة المحلية الموثقة
- الدليل المسترجع فعليًا
- درجة الثقة
- نتيجة المحاذاة

### Abstention

إذا لم يكن الدليل كافيًا:

## **مِعيار لا يخمّن**

بل يحيل الحالة للمراجعة البشرية

---

# ماذا يحصل عليه المستخدم؟

بدل تقرير تقني مزدحم، يحصل المراجع على:

- **قرار قبل النشر**
- **موضع المشكلة**
- **نوع الخطر**
- **سبب التنبيه**
- **مرآة المعنى**
- **الدليل المستخدم**
- **درجة الثقة**
- **تصحيح آمن عند الإمكان**
- **إحالة للمراجعة البشرية عند عدم كفاية الدليل**

القرار النهائي يبقى للإنسان

---

# أدلة قابلة لإعادة الاختبار

> الأرقام التالية تمثل **Development / Audit Evidence** للحزمة الحالية  
> وليست ادعاءً بدقة دينية 100% في العالم الحقيقي

| الاختبار | النتيجة |
|---|---:|
| Regression Test Suite | **348 / 348** |
| Quran Full-Corpus Reference Audit | **6,236 آية** |
| Safe Quran References | **6,236 / 6,236 دون False Positives في الاختبار** |
| Verse-Number Mutations | **6,236 / 6,236 detected** |
| Surah Mutations | **6,236 / 6,236 detected** |
| Repeatability | **200 / 200** |
| Reviewer Workload Stress Fixture | **175 signals → 59 root findings** |
| Noise Reduction on Stress Fixture | **66.3%** |

وتتضمن الحزمة كذلك اختبارات لـ:

- Quran reference verification
- Hadith reference verification
- semantic mutations
- adversarial cases
- source routing
- provider failure
- abstention behavior
- baseline comparison
- ablation analysis
- source provenance
- terminology provenance
- long-text stress testing
- release smoke testing

---

# تقليل ضوضاء المراجعة

ليس الهدف فقط اكتشاف أكبر عدد ممكن من التنبيهات

بل تقديم عدد أقل من **المشكلات الجذرية المفيدة للمراجع**

في Long Stress Fixture الحالي:

```text
175 raw signals
        ↓
59 root findings
```

أي:

**116 إشارة تم دمجها أو كبح تكرارها**

بما يعادل:

### **66.3% تقليلًا في ضوضاء المراجعة على هذه العينة التجريبية**

هذه النتيجة تخص اختبار التطوير المحدد ولا تمثل قياسًا ميدانيًا عامًا

---

# لماذا مِعيار مختلف؟

| | أداة ترجمة عامة | مِعيار |
|---|---|---|
| المهمة | إنتاج ترجمة | مراجعة سلامة ترجمة موجودة |
| السؤال | كيف نترجم النص؟ | هل انتقل المعنى بأمان؟ |
| المخرج | نص مترجم | قرار + مخاطر + تفسير + دليل |
| التركيز | الطلاقة والصياغة | سلامة المعنى |
| الأخطاء الدقيقة | قد تمر داخل نص طبيعي | يحاول تحديد موضعها وسببها |
| المصطلحات | جزء من الترجمة | طبقة حماية مستقلة |
| الاستشهادات | ليست محور المهمة | مسار تحقق مستقل |
| عدم اليقين | قد ينتج إجابة | يستطيع الامتناع |
| القرار النهائي | مخرج آلي | يبقى للمراجع البشري |

---

# حدود الأمان

مِعيار:

- **لا يصدر فتوى**
- **لا ينشئ حكمًا شرعيًا جديدًا**
- **لا يعيد ترجمة النص من الصفر**
- **لا يعتبر ترجمة المستخدم صحيحة لمجرد العثور على المرجع**
- **لا يدعي نجاح التحقق إذا فشل مزود المصدر**
- **لا يعرض مصدرًا باعتباره دليلًا مستخدمًا ما لم يدخل فعليًا في مسار الاستدلال**
- **لا يعيد كتابة الحالات الحساسة عندما لا يكون التصحيح آمنًا**
- **لا يستبدل المراجع البشري**

وظيفته:

> **حماية المعنى والمصطلح والدليل الموجود أصلًا من التحريف أثناء انتقاله بين اللغات**

---

# لماذا العربية → الإنجليزية الآن؟

النسخة المشاركة في التحدي تتعمد التركيز على:

## **العربية → الإنجليزية**

بدل دعم عدة لغات بصورة سطحية

التركيز على لغة واحدة أتاح:

- Benchmark محدد
- اختبارات أعمق
- توثيق المصطلحات
- توثيق المصادر
- اختبار الحالات الحرجة
- اختبار فشل المصادر والامتناع
- نتائج قابلة لإعادة التشغيل والتحقق

## الإنجليزية هي نطاق النسخة الأولى وليست حدود الفكرة

المعمارية مصممة للتوسع مستقبلًا إلى:

- لغات إضافية
- أنواع محتوى إضافية
- مصادر تحقق إضافية
- API للجهات والمنصات
- أنظمة إدارة المحتوى
- سير عمل الناشرين وصناع المحتوى

---

# للمحكم الذي لديه دقيقة واحدة

## 1 — جرّب المنتج

### [فتح مِعيار →](https://miyar-gate.streamlit.app/)

## 2 — راجع خريطة الأدلة

### [START_HERE_FOR_JUDGES.md →](START_HERE_FOR_JUDGES.md)

## 3 — شغّل التحقق السريع

```bash
python scripts/judge_verify.py
```

---

# تشغيل المشروع محليًا

```bash
python -m pip install -r requirements.txt
python scripts/preflight.py
python -m streamlit run app.py
```

على Windows:

```text
prepare_demo.bat
run_miyar.bat
```

---

# إعادة الاختبارات

```bash
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

---

# التوثيق

### المنتج والمنهج
- [Architecture](docs/ARCHITECTURE.md)
- [AI Methodology](docs/AI_METHODOLOGY.md)
- [Decision Policy](docs/DECISION_POLICY.md)
- [Safety](docs/SAFETY.md)

### الأدلة والقياس
- [Benchmark](docs/BENCHMARK.md)
- [Measurable Impact](docs/MEASURABLE_IMPACT.md)
- [Test Matrix](docs/TEST_MATRIX.md)
- [Reviewer Workload Evidence](docs/REVIEWER_WORKLOAD_EVIDENCE.md)

### المصادر والتتبع
- [Sources](docs/SOURCES.md)
- [Source Provenance](docs/SOURCE_PROVENANCE.md)
- [Terminology Provenance](docs/TERMINOLOGY_PROVENANCE_MATRIX.md)
- [Linguistic Method References](docs/LINGUISTIC_METHOD_REFERENCES.md)

### التشغيل والشفافية
- [Operations](docs/OPERATIONS.md)
- [Limitations](LIMITATIONS.md)
- [Tools](TOOLS.md)
- [Licenses](LICENSES.md)

---

# مبدأ مِعيار

## **لا نريد من الذكاء الاصطناعي أن يقرر بدل المراجع**

نريده أن يجعل المراجعة:

**أسرع في الوصول إلى موضع الخطر**  
**أوضح في تفسير سبب الخطر**  
**أكثر قابلية للتتبع والتحقق**

---

# مِعيار | Mi’yar

### **من ترجمة تبدو صحيحة إلى ترجمة يمكن مراجعة سلامة معناها قبل النشر**

**تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي**  
**المسار: صناعة المحتوى متعدد اللغات والتوطين الثقافي**

### Live Demo
https://miyar-gate.streamlit.app/

### GitHub
https://github.com/aljawharah-m/miyar

### حدود التطبيق التلقائي

لا يوجد زر تطبيق تلقائي؛ يظل تعديل الترجمة وقرار اعتمادها بيد الكاتب أو المراجع البشري. بعد تحرير النص يمكن استخدام زر «افحص سلامة المعنى» الأساسي لإجراء فحص جديد.

### سياسة بيانات المصادر

- source_version: يُسجل إصدار المصدر فقط عندما يعلنه مزود المصدر صراحة، ولا ينشئ مِعيار رقم إصدار غير موثق.
- etrieved_at: يُسجل وقت الاسترجاع للمصادر الحية عند جلبها، بما يحافظ على قابلية التتبع والمراجعة.

### سياسة تتبع المصادر الحية

- etrieved_at: يُسجل وقت استرجاع المصدر الحي عند جلبه، حتى يمكن معرفة متى تم التحقق من البيانات وإعادة مراجعتها لاحقًا.

### تتبع بيانات المصادر الحية

عند استخدام مصدر حي، يحتفظ مِعيار باسم المصدر وURL وretrieved_at لتسجيل وقت الاسترجاع وقابلية التتبع. كما يسجل source_version فقط عندما يقدمه المصدر نفسه، ولا يتم اختراع أو افتراض رقم إصدار.

retrieved_at: يسجل مِعيار وقت استرجاع المصدر الحي لضمان قابلية التتبع والمراجعة.

---

## Transparency, Sources & AI Use

### Sources and provenance
Mi'yar distinguishes between live evidence retrieved from trusted providers, locally curated rules with documented provenance, and supporting/reference sources that are not automatically treated as evidence used in a decision.

Reference recognition alone does not verify the user translation. Live evidence is recorded only after successful retrieval. Insufficient or conflicting evidence routes the case to Human Review.

Detailed documentation:
- [Sources](docs/SOURCES.md)
- [Source Provenance](docs/SOURCE_PROVENANCE.md)
- [Terminology Provenance](docs/TERMINOLOGY_PROVENANCE_MATRIX.md)

### Rights and third-party content
Third-party software, models, datasets, and reference content remain governed by their original licenses and upstream terms. Public availability of this repository does not transfer ownership of external content to Mi'yar.

See [Licenses and Third-Party Terms](LICENSES.md).

### AI-assisted development disclosure
ChatGPT was used during development as an assistance tool for brainstorming and refinement, code-review and debugging support, documentation drafting and editing, test-case discussion, and presentation/submission preparation.

ChatGPT is **not part of Mi'yar's runtime decision engine** and is not required to produce publication-safety decisions.

Runtime findings are produced by the implemented Mi'yar pipeline through deterministic safety rules, terminology safeguards, multilingual semantic analysis, source verification, Evidence Fusion, uncertainty handling, and Human Review.

See [Tools and AI Disclosure](TOOLS.md).

### Human decision boundary
Mi'yar does not issue fatwas, does not create new religious rulings, and does not replace the human reviewer. The final publication decision remains human.

