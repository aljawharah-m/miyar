# SOURCES

## Judge Source Classification

| Source / Resource | Role in Mi'yar | Evidence status |
|---|---|---|
| QuranEnc | Quran reference retrieval and verification when retrieval succeeds | Can become live evidence only after successful retrieval |
| HadeethEnc | Hadith reference retrieval and verification when retrieval succeeds | Can become live evidence only after successful retrieval |
| Local Quran locator | Local reference recognition / ambiguity detection | Locator only; not external verification |
| Local terminology provenance | Curated terminology safety rules | Local curated rule with documented provenance |
| TerminologyEnc / ICADB | Supporting terminology/reference routes when applicable | Not automatically evidence-used |
| Dorar / Kuwaiti Fiqh Encyclopedia / Byenah / IslamHouse / IslamEnc | Supporting domain references | Documentary/supporting unless explicitly retrieved and used |
| Challenge official material | Challenge terminology examples and reference-policy context | Development/reference material |

**Important:** source availability or reference recognition alone never verifies the user translation. Mi'yar records live evidence only when retrieval actually succeeds; insufficient or conflicting evidence routes the case to Human Review.

For deeper provenance and licensing details, see docs/SOURCE_PROVENANCE.md, docs/TERMINOLOGY_PROVENANCE_MATRIX.md, and LICENSES.md.

---


## المصادر بحسب طريقة الاستخدام
- **QuranEnc**: ترجمة الآية عند التعرف على المرجع ونجاح الاسترجاع.
- **HadeethEnc**: البطاقة العربية/الإنجليزية عند التعرف على الحديث ونجاح الاسترجاع.
- **Local Quran locator**: تحديد موضع الآية/الغموض فقط، وليس مرجع ترجمة.
- **ICADB**: مسار مساعد/مرجعي عند توفره؛ locator لا يساوي evidence-used.
- **الحزمة العلمية الرسمية للتحدي**: أصل أمثلة المصطلحات الرسمية وسياسة الاعتماد على المرجعيات الموثوقة.
- **TerminologyEnc**: مرجع تأصيل/اقتراح للمصطلحات؛ لا يظهر كـ live used evidence إلا عند استرجاع فعلي. القواعد المحلية الموثقة تبقى `local_curated_rule` ولا تُنسب كاسترجاع حي.


## سياسة metadata ونطاق التحقق
- QuranEnc: عند نجاح الاسترجاع يحفظ مِعيار `translation_key`, `source_version` (إذا أعادها endpoint metadata), `source_last_update`, `retrieved_at`, وURL.
- HadeethEnc: يحفظ `source_version` فقط إذا أعادتها استجابة المصدر؛ وإلا تبقى `None` مع `retrieved_at` وURL. لا يتم التخمين.
- `reference_verified` منفصل عن `user_translation_verified`: استرجاع المرجع لا يعتمد ترجمة المستخدم تلقائيًا.
- `live_verified` يعني أن المرجع استُرجع فعلًا في تلك المحاولة، لا أن الحكم الشرعي الأصلي تمت المصادقة عليه.
- المصادر ذات `reference_route_only` أو `recommended` لا تُسمى evidence-used.
- `TEST/MOCK/DEMO/ABC` في سياق الاختبار synthetic identifiers ولا تُرسل إلى API خارجي.

## توثيق قواعد المصطلحات
كل قاعدة داخل Terminology Guard مرتبطة بصف في:
- `data/terminology_provenance.json`
- `docs/TERMINOLOGY_PROVENANCE_MATRIX.md`

القاعدة المهمة:
**المصدر يؤصل معنى المصطلح؛ مِعيار هو الذي يطبق سياسة السلامة على المقابل الإنجليزي.**
لذلك لا يدعي المشروع أن المصدر قال حرفيًا إن كل كلمة في `risky` خاطئة في كل سياق.

## مراجع مساندة بحسب المجال
- TerminologyEnc / ICADB للمصطلحات والترجمات المعتمدة.
- الدرر السنية للعقيدة والحديث والفقه بحسب الحاجة.
- الموسوعة الفقهية الكويتية للمسائل والمصطلحات الفقهية.
- Byenah / IslamHouse / IslamEnc للمحتوى التعريفي متعدد اللغات.

## قاعدة النزاهة في الواجهة
المصدر لا يظهر كـ«مستخدم في القرار» إلا إذا كانت حالته `live_verified` أو guideline محلي موثق. المرجع المقترح يبقى منفصلًا عن الدليل المستخدم.


### Public provenance policy
- `reference_verified` لا يساوي `user_translation_verified`.
- evidence المتعارض صراحة (`status=conflicting` أو `verification.conflict=true`) يفرض Human Review؛ لا يرجح مِعيار بين المصادر آليًا.
- synthetic IDs من نوع TEST/MOCK/DEMO/ABC تُفحص اتساقيًا محليًا فقط ولا تُرسل للتحقق الخارجي.
- أي نص مسترجع من QuranEnc/HadeethEnc يحتفظ بنسبة المصدر وURL و`retrieved_at` ونسخة المصدر إذا أرجعها upstream، بلا تخمين.
