# Mi’yar 1.0 — Final Submission Handoff

## القرار
هذه الحزمة هي **نسخة التسليم النهائية** المبنية على محرك تم التحقق منه، مع تحسينات عرض وإتاحة تحقق لا توسّع نطاق الفتوى أو الترجمة.

## أسرع نقطة دخول
افتح `START_HERE_FOR_JUDGES.md`.

## Evidence الحالية
- Regression: **348/348 passed** على المحرك المتحقق منه.
- Quran corpus recognition: **6,236/6,236** عبر exact / undiacritized / quoted / natural-context representations مع 0 wrong mappings في audit الأخير.
- Quran reference integrity: 6,236 safe references بلا FP؛ 6,236 ayah-number mutations؛ 6,236 surah mutations؛ QuranEnc routing 0 wrong في audit.
- Quran semantic reference audit: 24 safe cases بلا FP؛ 31 mutations بلا miss.
- Hadith reference audit: 20 official-safe cases بلا FP/route failures؛ 50 semantic mutations بلا miss.
- Provider failure: لا يوجد unsafe/false-live claim في audits المرفقة.
- Repeatability: **200/200** comparisons.
- Jury stress: **37/37**.
- Long-text: **7/7** injected gap classes.
- Black-box campaign retained as regression evidence: **288** cases/variants + mixed 20-segment document.

## قيمة الطبقات
`evaluation/ablation_report.json` على development set:
- structure-only Recall 0.4762
- terminology-only Recall 0.5238
- structure+terminology+scope Recall 0.9683
- full deterministic Mi'yar Recall 1.0000

هذه Development Evidence وليست field validation مستقلة.

## التشغيل
```powershell
python -m pip install -r requirements.txt
python scripts/judge_verify.py
python scripts/preflight.py
python -m streamlit run app.py --server.fileWatcherType none
```

لإعادة الاختبارات الثقيلة:
```powershell
python scripts/release_check.py
```

## Safety contract
- لا فتوى مستقلة.
- لا اعتماد تلقائي لصحة الحكم الشرعي الأصلي.
- local recognition ≠ live verification.
- لا `live_verified` دون نص مرجعي مسترجع فعليًا.
- provider failure/ambiguity → Review/Abstention.
- TEST/MOCK/DEMO/ABC IDs لا تُرسل خارجيًا.
- Human Review هو القرار النهائي للحالات غير المحسومة.

## متطلبات تسليم خارج الحزمة
يجب أن تكون هذه العناصر موجودة فعليًا في منصة التحدي قبل الإرسال:
1. Live Demo URL يعمل من جهاز آخر.
2. Public GitHub repository.
3. فيديو ≤ دقيقتين.
4. Presentation PDF/PPT.
5. اختبار `scripts/preflight.py` على بيئة العرض.

لا تعتبر الحزمة وجود هذه العناصر الخارجية مثبتًا لمجرد وجود الكود.
