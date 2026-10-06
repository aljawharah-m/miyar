# LIMITATIONS

- النسخة 1.0: نص عربي → إنجليزي قبل النشر.
- مِعيار لا يصدر فتوى ولا يمثل اعتمادًا شرعيًا نهائيًا.
- درجة التشابه الدلالي **مؤشر هندسي وليست احتمال صحة أو ثقة شرعية**.
- النموذج الدلالي قد يفوّت فروقًا دقيقة؛ لهذا لا يُستخدم منفردًا.
- فشل استرجاع المرجع يفعّل الامتناع أو المراجعة عند الحاجة، ولا يسمح باختلاق مصدر.
- benchmark الحالي تطويري/صناعي حتى تتم مراجعته بشريًا بصورة مستقلة.
- التعرف على القرآن والحديث يحتاج توسيعًا مستمرًا واختبارات أصعب قبل الإنتاج واسع النطاق.

- الحد العام في الواجهة: 12,000 حرف للنص العربي و12,000 حرف للترجمة في الفحص الواحد.
- قاموس المصطلحات واسع لكنه غير نهائي؛ المقابل الذي يعتمد على السياق يُحال للمراجعة بدل إصدار حكم قطعي.
- مِعيار يعرض كل الفجوات التي تكتشفها طبقاته الحالية، لكنه لا يدعي أنه يحصي كل خطأ ممكن في اللغة الطبيعية.

## Religious-text boundary
- Source recognition and live-reference grounding materially reduce Quran/Hadith false positives and root misclassification, but no finite rule/test suite can guarantee zero errors across every verse, hadith corpus, translation style, commentary context, or adversarial paraphrase.
- `live_verified` is shown only after an actual provider retrieval; local recognition alone never proves external verification.
- If authoritative evidence is unavailable or ambiguous, Mi'yar must preserve uncertainty and human review rather than infer religious correctness.
- Quran locator coverage has been audited across the 6,236-verse corpus for the documented recognition/reference tasks, but this does not imply universal semantic correctness. Hadith coverage, commentary contexts, translation variants, and adversarial paraphrases still require broader evaluation before wide production use.
