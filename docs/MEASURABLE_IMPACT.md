# Measurable Impact — ما الذي تحسن فعليًا؟

مِعيار لا يدّعي نتائج ميدانية لم تُجمع. هذا الملف يعرض فقط القياسات الموجودة داخل الحزمة والتي يستطيع المحكم إعادة تشغيلها.

## 1) قيمة التركيب متعدد الطبقات

المجموعة: **130 synthetic development cases**.

| التكوين | Recall | F1 | FPR |
|---|---:|---:|---:|
| Structure rules only | 0.4762 | 0.6452 | 0.0000 |
| Terminology guard only | 0.5238 | 0.6875 | 0.0000 |
| Structure + terminology + scope | 0.9683 | 0.9839 | 0.0000 |
| Full Mi'yar deterministic path | **1.0000** | **1.0000** | **0.0000** |

المصدر: `evaluation/ablation_report.json`.

**الدلالة:** القيمة لا تأتي من قاعدة واحدة أو قاموس واحد؛ دمج الطبقات يغطي فئات لا تغطيها الطبقات المنفردة على نفس مجموعة التطوير.

## 2) سلامة الحالات الحرجة

`evaluation/benchmark_report.json`:
- Precision: 1.0000
- Recall: 1.0000
- F1: 1.0000
- FPR: 0.0000
- Critical Error Recall: 1.0000

هذه أرقام **Development/Synthetic** وليست field accuracy.

## 3) تنوع الاختبارات

- `evaluation/adversarial_report.json`: adversarial development cases.
- `evaluation/jury_stress_report.json`: **37/37**.
- `evaluation/long_text_stress_report.json`: **7/7** gap classes داخل نص طويل موزع.
- `evaluation/repeatability_report.json`: **200/200** comparisons بلا اختلاف.
- Black-box campaign: **288** user-style cases/variants، إضافة إلى وثيقة 20 مقطعًا مختلطة.

## 4) القرآن والمراجع

**حجم الـaudit:** `sacred_corpus_audit.json` يمثل **62,360 Quran checks** عبر عدة مسارات، ويضيف `hadith_reference_audit.json` **130 Hadith checks**؛ الإجمالي **62,490 deterministic audit checks**. هذا عدد عمليات تحقق، لا عدد نصوص مستقلة.

`FINAL_V15_18_VERIFICATION_REPORT.md`:
- 6,236/6,236 Quran recognitions across exact/undiacritized/quoted/natural-context forms.
- 6,236 safe references بلا false positives.
- 6,236 ayah-number mutations detected.
- 6,236 surah mutations detected.
- QuranEnc routing: 0 wrong mappings in the audit.
- Quran semantic audit: 24 safe / 31 mutated cases with 0 reported FP/miss in that audit.

## 5) السنة والمراجع

- Hadith reference audit: 20 official-safe cases بلا false positives/route failures.
- 50 semantic mutations: 0 missed in the included audit.
- Provider failures: 0 unsafe verification claims.
- Structured reference-ID changes detected with 0 misses in the audit.

## 6) واقعية التشغيل

`evaluation/resource_profile.json` للـdeterministic/offline path:
- Median latency: 395 ms
- P95: 431 ms
- Max: 439 ms
- Peak process RSS: ~98.7 MiB

**حد الدلالة:** هذه قياسات بيئة البناء للمسار deterministic، ولا تشمل زمن الشبكة أو تحميل النموذج الدلالي.

## 7) تقليل ضوضاء المراجعة عبر Evidence Fusion

على `evaluation/USER_LONG_STRESS_ALIGNMENT.txt` في النسخة الحالية:
- Raw detector signals: **175**
- Root findings after fusion: **59**
- Suppressed/merged signals: **116**
- Noise reduction before reviewer display: **66.3%**

إعادة التحقق: `python scripts/reviewer_workload_evidence.py`.

**حد الدلالة:** هذا يثبت تقليل عدد التنبيهات المعروضة داخل development stress task، ولا يساوي قياسًا ميدانيًا لزمن المراجعة البشرية.

## ما الذي لم نقسه بعد؟

- زمن مراجعة مترجمين حقيقيين قبل/بعد مِعيار.
- field precision/recall مستقل على corpus لم يبنه فريق المشروع.
- usability study مع فئة مستهدفة فعلية.

وجود هذه الحدود معلن مقصود حتى تبقى ادعاءات المشروع قابلة للتحقق.
