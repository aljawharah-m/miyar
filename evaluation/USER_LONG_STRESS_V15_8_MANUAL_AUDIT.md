# V15.8 — Manual audit of long-stress roots

هذه مراجعة تصنيفية للـ58 root issue في fixture الصناعي. لا تمثل دقة دينية 100%.

|#|المقطع|العنوان|الفئة|subtype|الأثر الديني|
|---:|---:|---|---|---|---|
|1|15|استُبدل الامتناع عن التحقق باختلاق مرجع — المقطع 15|مرجعي|REFERENCE_INTEGRITY_DRIFT|high|
|2|15|تغيّر رقم الآية في المرجع — المقطع 15|مرجعي|REFERENCE_INTEGRITY_DRIFT|high|
|3|16|تغيّر معرّف مرجعي — المقطع 16|مرجعي|REFERENCE_INTEGRITY_DRIFT|none|
|4|6|انقلب المنع العام مع الاستثناء إلى إباحة — المقطع 6|دلالي عام|GENERAL_MODALITY_DRIFT|none|
|5|3|تغيّرت درجة الحكم من الجواز إلى الإلزام — المقطع 3|دلالي ديني|RULING_TRANSFER_DRIFT|high|
|6|3|تغيّرت درجة الحكم من الاستحباب إلى الإلزام — المقطع 3|دلالي ديني|RULING_TRANSFER_DRIFT|high|
|7|3|خُففت درجة التحريم — المقطع 3|دلالي ديني|RULING_TRANSFER_DRIFT|high|
|8|22|انقلب نطاق النفي حول الإلزام — المقطع 22|دلالي عام|GENERAL_MODALITY_DRIFT|none|
|9|18|تغيّر توزيع المسؤوليات بين الأشخاص — المقطع 18|دلالي عام|ACTOR_RESPONSIBILITY_DRIFT|none|
|10|36|تغيّرت جهة المسؤولية — المقطع 36|دلالي عام|ACTOR_RESPONSIBILITY_DRIFT|none|
|11|37|دُمج دور النظام مع قرار المراجع — المقطع 37|دلالي عام|ACTOR_RESPONSIBILITY_DRIFT|none|
|12|19|تغيّر الرابط المنطقي بين الشروط — المقطع 19|منطقي/رقمي|LOGICAL_RELATION_DRIFT|none|
|13|20|تغيّر عدد الشروط المطلوبة — المقطع 20|منطقي/رقمي|LOGICAL_RELATION_DRIFT|none|
|14|33|تغيّر حد «على الأقل» — المقطع 33|منطقي/رقمي|LOGICAL_RELATION_DRIFT|none|
|15|12|انقلبت العلاقة السببية — المقطع 12|دلالي عام|CAUSAL_RELATION_DRIFT|high|
|16|12|انقلب ترتيب الأحداث — المقطع 12|دلالي عام|CAUSAL_RELATION_DRIFT|high|
|17|14|طُمِس اختلاف المصادر — المقطع 14|مرجعي|REFERENCE_INTEGRITY_DRIFT|none|
|18|5|أُلغي شرط لازم في الأصل — المقطع 5|منطقي/رقمي|LOGICAL_RELATION_DRIFT|high|
|19|23|حُذف شرط المراجعة البشرية قبل النشر — المقطع 23|منطقي/رقمي|LOGICAL_RELATION_DRIFT|none|
|20|23|انقلب قرار النشر تحت حد الثقة — المقطع 23|منطقي/رقمي|LOGICAL_RELATION_DRIFT|none|
|21|24|تغيّر حد الشرط عند القيمة الفاصلة — المقطع 24|منطقي/رقمي|NUMERIC_SEMANTIC_DRIFT|none|
|22|8|تغيّرت القيمة المطلوبة — المقطع 8|منطقي/رقمي|NUMERIC_SEMANTIC_DRIFT|high|
|23|9|تغيّرت النتيجة العددية — المقطع 9|منطقي/رقمي|NUMERIC_SEMANTIC_DRIFT|none|
|24|41|سُوّيت وحدات قياس غير متكافئة — المقطع 41|منطقي/رقمي|NUMERIC_SEMANTIC_DRIFT|none|
|25|13|رُفعت درجة اليقين دون سند — المقطع 13|معرفي|EPISTEMIC_CERTAINTY_DRIFT|none|
|26|32|رُفعت درجة اليقين دون سند — المقطع 32|معرفي|EPISTEMIC_CERTAINTY_DRIFT|none|
|27|26|حُوّل قرار البوابة إلى إثبات صحة مطلقة — المقطع 26|معرفي|EPISTEMIC_CERTAINTY_DRIFT|high|
|28|27|تحول قيد معرفي إلى استنتاج قطعي — المقطع 27|معرفي|EPISTEMIC_CERTAINTY_DRIFT|none|
|29|38|تحول قيد معرفي إلى استنتاج قطعي — المقطع 38|معرفي|EPISTEMIC_CERTAINTY_DRIFT|none|
|30|11|قُلِبت الفروق بين عدة مصطلحات إلى مساواة — المقطع 11|دلالي ديني|RELIGIOUS_TERMINOLOGY_DRIFT|high|
|31|4|توسّع النطاق من جزئي إلى عام — المقطع 4|دلالي عام|SCOPE_SEMANTIC_DRIFT|none|
|32|1|تحول نص تقني إلى حكم ديني — المقطع 1|دلالي عام|GENERAL_SEMANTIC_DRIFT|high|
|33|6|فُقد الحصر «لا … إلا» — المقطع 6|دلالي عام|SCOPE_SEMANTIC_DRIFT|none|
|34|31|قُلِب معنى «لم يحضر إلا ثلاثة» — المقطع 31|دلالي عام|SCOPE_SEMANTIC_DRIFT|none|
|35|34|سُوّيت قيمتان عدديتان مختلفتان — المقطع 34|منطقي/رقمي|SIGNED_NUMBER_CONTRADICTION|none|
|36|34|تغيّرت العلامة العشرية — المقطع 34|منطقي/رقمي|DECIMAL_VALUE_CORRUPTION|none|
|37|42|أُجيزت إضافة استنتاجات غير موجودة في الأصل — المقطع 42|دلالي عام|GENERAL_SEMANTIC_DRIFT|none|
|38|43|أُجيزت إضافة ادعاءات دينية قطعية — المقطع 43|دلالي عام|GENERAL_SEMANTIC_DRIFT|high|
|39|44|أُجيز حذف قيود مؤثرة — المقطع 44|دلالي عام|SCOPE_SEMANTIC_DRIFT|none|
|40|7|تغيّر نطاق الاستثناء — المقطع 7|دلالي عام|SCOPE_SEMANTIC_DRIFT|none|
|41|21|أُجيز حذف قيود تغيّر النطاق — المقطع 21|دلالي عام|SCOPE_SEMANTIC_DRIFT|none|
|42|28|أُلغي الامتناع الآمن أو المراجعة البشرية — المقطع 28|معرفي|EPISTEMIC_CERTAINTY_DRIFT|high|
|43|40|انقلب اتجاه المقارنة — المقطع 40|دلالي عام|GENERAL_SEMANTIC_DRIFT|none|
|44|45|أُلغي الامتناع الآمن أو المراجعة البشرية — المقطع 45|معرفي|EPISTEMIC_CERTAINTY_DRIFT|none|
|45|10|أُلغي وجوب حفظ الدلالة الاصطلاحية — المقطع 10|دلالي ديني|RELIGIOUS_TERMINOLOGY_DRIFT|high|
|46|23|تغيّرت مدة الاحتفاظ بسجل القرار — المقطع 23|منطقي/رقمي|NUMERIC_SEMANTIC_DRIFT|none|
|47|9|تغيّر وقت الموعد من صباح إلى مساء — المقطع 9|منطقي/رقمي|NUMERIC_SEMANTIC_DRIFT|none|
|48|2|ترجمة غير دقيقة لمصطلح «التوحيد» — المقطع 2|دلالي ديني|RELIGIOUS_TERMINOLOGY_DRIFT|high|
|49|23|حُذف توثيق تجاوز القرار — المقطع 23|دلالي عام|GENERAL_SEMANTIC_DRIFT|none|
|50|34|حُسم تاريخ ملتبس دون سند — المقطع 34|معرفي|DATE_AMBIGUITY_COLLAPSE|none|
|51|39|تحولت مقارنة نسبية إلى حكم مطلق — المقطع 39|دلالي عام|GENERAL_SEMANTIC_DRIFT|none|
|52|25|تغيّرت شدة الخطر — المقطع 25|دلالي عام|GENERAL_SEMANTIC_DRIFT|none|
|53|29|قُلِب معيار الدقة من المعنى إلى الحرفية — المقطع 29|دلالي عام|GENERAL_SEMANTIC_DRIFT|none|
|54|35|حُوّل اسم علم إلى معنى لغوي — المقطع 35|دلالي عام|ACTOR_RESPONSIBILITY_DRIFT|none|
|55|2|تحويل الاحتمال أو التكرار الجزئي إلى دوام — المقطع 2|دلالي عام|SCOPE_SEMANTIC_DRIFT|high|
|56|22|تعميم ما كان جزئيًا — المقطع 22|دلالي عام|SCOPE_SEMANTIC_DRIFT|none|
|57|17|مرجع الضمير غير محسوم — المقطع 17|معرفي|EPISTEMIC_CERTAINTY_DRIFT|none|
|58|30|اعتُبر اختلاف الصياغة خطأ رغم حفظ المعنى — المقطع 30|دلالي عام|GENERAL_SEMANTIC_DRIFT|none|