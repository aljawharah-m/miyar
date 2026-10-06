# Source Provenance

## مبدأ الفصل
مِعيار يفرق بين أربعة أشياء لا يجوز دمجها:
1. **معنى المصطلح المؤصل من مرجع موثوق**.
2. **سياسة مِعيار الهندسية** التي تصنف مقابلاً إلى accepted/risky/review.
3. **مرجع خارجي تم استرجاعه فعليًا في الفحص الحالي**.
4. **مرجع مقترح للمراجعة** لم يستخدم في القرار الحالي.

## Terminology provenance manifest
كل واحدة من قواعد المصطلحات الـ49 لها صف مباشر قابل للتتبع في:
`data/terminology_provenance.json`

والنسخة المقروءة:
`docs/TERMINOLOGY_PROVENANCE_MATRIX.md`

### الصفوف الرسمية
المصطلحات التي وردت كأمثلة في الحزمة العلمية الرسمية موسومة `official`، مع أساس الحزمة الرسمية وTerminologyEnc.

### القواعد المحافظة
الصفوف الإضافية موسومة `curated`. الأساس المرجعي يوثق معنى المصطلح ومجاله، بينما accepted/risky/review يبقى قرار سلامة هندسيًا في مِعيار. لا يُنسب هذا التصنيف حرفيًا إلى المصدر.

## القواعد اللغوية العامة
المراجع المنهجية للقواعد اللغوية موجودة في `data/linguistic_method_references.json` و`docs/LINGUISTIC_METHOD_REFERENCES.md`. لا ننسب regex إلى مصدر شرعي؛ المرجع يثبت الظاهرة اللغوية، والاختبارات تثبت التنفيذ.

## القرآن والحديث
- Quran locator المحلي يحدد المرجع فقط.
- QuranEnc translation تصبح evidence-used فقط عند نجاح الاسترجاع.
- HadeethEnc card تصبح evidence-used فقط عند نجاح الاسترجاع.
- reference alignment يقارن المقطع المحاذي لا كامل النص المسترجع عشوائيًا.

## النزاهة
إذا فشل الاسترجاع لا يختلق مِعيار مرجعًا بديلًا. وإذا كانت القاعدة تحتاج سياقًا لا يعطي rewrite قطعيًا.

## Source verification boundary
- Reference locator success is not equivalent to translation verification.
- `reference_verified=true` records that the external/local reference was resolved; `user_translation_verified` remains false until Mi'yar's comparison layers evaluate the translation.
- QuranEnc/HadeethEnc attribution metadata is preserved when supplied upstream. Missing versions are represented as `None`, never inferred.
- Synthetic identifiers (`TEST`, `MOCK`, `DEMO`, `ABC`) are test structure and are blocked from external retrieval when presented as examples.
