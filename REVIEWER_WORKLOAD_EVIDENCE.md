# Reviewer Workload Evidence — مِعيار 1.0

هذا الملف يثبت فائدة **Evidence Fusion + Root-Cause Clustering** على نفس النسخة الحالية، بدون ادعاء تجربة مستخدم خارجية لم تُنفذ.

## النتيجة القابلة لإعادة التشغيل

على `evaluation/USER_LONG_STRESS_ALIGNMENT.txt` (45 زوجًا عربيًا↔إنجليزيًا، نص طويل موزع الأخطاء):

- Raw detector signals: **175**
- Root findings المعروضة بعد الدمج: **59**
- Signals suppressed/merged: **116**
- Noise reduction قبل وصول التنبيهات للمراجع: **66.3%**

الحساب: `(175 - 59) / 175 = 66.3%`.

## لماذا هذا مهم؟

المراجع لا يحتاج رؤية كل symptom على أنه Finding مستقل. مثال واحد قد يولّد نفيًا + إلزامًا + تعميمًا نتيجة Root واحد. مِعيار يحتفظ بالأدلة في diagnostics ثم يعرض الجذر الأكثر تفسيرًا للمستخدم.

هذا لا يثبت وحده تقليل زمن المراجعة البشرية في الميدان؛ لكنه يثبت **تقليل عدد التنبيهات المعروضة داخل نفس المهمة** مع بقاء الـroot findings.

## إعادة التحقق

```powershell
python scripts/reviewer_workload_evidence.py
```

المخرجات المتوقعة على الحزمة الحالية:

```text
raw_signals=175
root_findings=59
suppressed_or_merged=116
noise_reduction_pct=66.3
```

## حد الادعاء

هذه **development stress evidence** وليست دراسة زمن لمراجعين مستقلين. قياس review-time البشري يبقى خطوة لاحقة موثقة في `docs/EXTERNAL_VALIDATION_PROTOCOL.md`.
