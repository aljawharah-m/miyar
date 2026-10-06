# LICENSES AND THIRD-PARTY TERMS

## Software dependencies
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — Apache-2.0 model license.
- Sentence Transformers — Apache-2.0.
- Streamlit — Apache-2.0.
- Requests — Apache-2.0.
- pytest — MIT.

## Reference content
- `data/quran_locator.json`: فهرس محلي لنص القرآن يُستخدم **لتحديد السورة والآية فقط** ولا يُعامل كترجمة مرجعية أو دليل خارجي. تم توليد الفهرس من ملف `qurantext-simple.def` في حزمة LaTeX `quran` (حقوق Seiied-Mohammad-Javad Razavian، وترخيص LaTeX Project Public License 1.3c أو أحدث). النص لا يُعرض كمصدر ترجمة معتمد؛ عند الحاجة إلى دليل ترجمة يستخدم مِعيار QuranEnc عند نجاح الاسترجاع المباشر.
- QuranEnc: شروط المصدر الرسمية عند إعادة نشر الترجمة تتطلب عدم تعديل المحتوى، نسبة المصدر بوضوح، وذكر رقم الإصدار. يحفظ مِعيار `translation_key/version/last_update/retrieved_at` عندما توفرها API، ولا يخترع نسخة إذا لم تُرجع.
- HadeethEnc: شروط المصدر الرسمية عند إعادة نشر الترجمات تتطلب عدم تعديل المحتوى، نسبة المصدر بوضوح، وذكر رقم الإصدار. يحفظ مِعيار النسخة إذا أعادها المصدر؛ وإلا `source_version=None` مع وقت الاسترجاع، بلا تخمين.
- بقية المرجعيات في مسار التوجيه (TerminologyEnc، الدرر السنية، الموسوعة الفقهية الكويتية، Byenah، IslamHouse، IslamEnc) لا تُعرض كـ«دليل مستخدم» لمجرد وجودها في الكتالوج.

## Mi’yar code
كود المشروع المقدم للتحدي مملوك لفريق مِعيار ما لم يذكر خلاف ذلك في ملف أو مكوّن بعينه.


### V15.8 attribution enforcement
عند عرض أو إعادة استخدام نص مسترجع من QuranEnc أو HadeethEnc يحافظ مِعيار على نسبة المصدر، وبيانات النسخة إذا وفرها المصدر، ووقت الاسترجاع والرابط. إذا لم تُرجع API رقم إصدار، تبقى `source_version=None` ولا يتم اختلاق قيمة بديلة.
