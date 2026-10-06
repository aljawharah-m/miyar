# مصفوفة الاختبار النهائية

## اختبارات الوحدة والتكامل

`python -m pytest -q`

تشمل: قواعد القيود، المصطلحات، المصادر، UI public-copy، النص الطويل، وإصلاحات false positives.

## Smoke

`python evaluation/run_release_smoke.py`

حالات أساسية للديمو، القرآن، المصطلحات، درجات الحكم وتعدد الفجوات.

## Jury Stress

`python evaluation/run_jury_stress.py`

37 حالة مصممة خصيصًا لأعلى مستويات التحكيم: حالات صحيحة قريبة من الخطأ، false-positive control، مصطلحات حساسة، sentence-local swaps، مراجعة سياقية، وتعدد مواضع.

## Benchmark

`python evaluation/run_benchmark.py`

130 حالة صناعية تطويرية. النتائج ليست تحققًا مستقلاً.

## Adversarial

`python evaluation/run_adversarial.py`

48 حالة صناعية هجومية/حدية.

## Repeatability

`python evaluation/run_repeatability.py`

20 حالة × 10 تشغيلات = 200 مقارنة للقرار الحتمي.

## Long Text

`python evaluation/run_long_text_stress.py`

مقال بحجم آلاف الأحرف، مع 7 فئات أخطاء مزروعة وموزعة في الوسط والنهاية للتحقق أن موضعًا صحيحًا لا يخفي خطأً لاحقًا.

## Full release check

`python scripts/release_check.py`

يشغل الفحوص السابقة المناسبة للإصدار، ويفحص تسرب التفاصيل التقنية العامة والمواد السرية المحتملة.
