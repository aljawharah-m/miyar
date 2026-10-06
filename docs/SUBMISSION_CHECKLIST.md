# Final Submission Checklist

## داخل الحزمة — منجز
- [x] Engine frozen on verified core + submission-ready evidence/docs
- [x] 348/348 regression tests
- [x] 62,490 sacred-source deterministic audit checks
- [x] 200/200 repeatability comparisons
- [x] benchmark + adversarial + jury stress + long-text + ablation
- [x] reviewer workload evidence: 175 raw → 59 roots = 66.3% reduction
- [x] terminology provenance + source/metadata/attribution audits
- [x] resource profile
- [x] secret scan + public UI leak scan
- [x] `scripts/judge_verify.py`
- [x] `scripts/release_check.py`
- [x] Judge scorecard + evidence map + demo/video/presentation scripts

## يحتاج جهاز/حساب صاحبة المشروع
- [ ] Live Demo عام يعمل من متصفح نظيف
- [ ] `python scripts/preflight.py` على جهاز العرض النهائي
- [ ] Public GitHub بدون أسرار وآخر commit مطابق للـLive Demo
- [ ] تجربة Live Verification لحالة قرآن وحالة حديث من جهاز العرض
- [ ] فيديو ≤2 دقيقة
- [ ] Presentation PDF/PPT
- [ ] اختبار روابط البوابة ثم حفظ تأكيد التسليم

## تحسين اختياري فقط إذا كان الوقت يسمح
- [ ] `evaluation/run_baselines.py` بعد توفر نموذج `sentence-transformers` محليًا؛ لا تؤخري التسليم بسببه
- [ ] external/usability validation حقيقي؛ لا يُدعى وجوده دون تنفيذ

## ادعاءات ممنوعة بلا دليل
- «دقة دينية 100%»
- «اختبار مستقل/ميداني» إذا لم ينفذ
- «مصدر X استُخدم في القرار» إذا لم يُسترجع فعليًا
