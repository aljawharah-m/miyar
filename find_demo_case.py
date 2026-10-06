"""Find the strongest 'fluent but unsafe' live-demo case on this machine.

It deliberately chooses a case that Mi'yar blocks for a concrete invariant while
its multilingual semantic-AI similarity is as high as possible. This prevents us
from hand-picking a similarity score or making an unreproducible claim.
"""
from core.engine import analyze

CASES=[
    ("لا يجوز نشر هذا إلا بعد مراجعة المختص.","It is not permissible to publish this after specialist review."),
    ("يجوز استخدام المادة إذا ذُكر مصدرها.","The material may be used and its source may be mentioned."),
    ("يجب حفظ النص كما هو إلا عند وجود خطأ مطبعي.","The text must be preserved as it is."),
    ("لا يُنسب هذا القول إلى النبي إلا بدليل صحيح.","This statement is attributed to the Prophet with authentic evidence."),
    ("يجوز نشر الترجمة بشرط ألا تغيّر المعنى.","The translation may be published without changing the meaning."),
    ("قد يُذكر هذا المعنى في بعض السياقات.","This meaning is always stated in these contexts."),
    ("لا يُعمل بهذا الحكم إلا عند تحقق الشرط.","This ruling is applied when the condition is met."),
    ("هذا مباح وليس واجبًا.","This is obligatory."),
    ("لا يجوز حذف الاستثناء لأن ذلك يغيّر نطاق الحكم.","The exception may be removed because the ruling remains the same."),
    ("يُقبل النقل إذا حُفظت النسبة إلى المصدر.","The quotation is accepted."),
]

rows=[]
for ar,en in CASES:
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=True)
    ai=r.get("semantic_ai") or {}
    if r["status"]=="critical" and ai.get("available") and ai.get("similarity") is not None:
        rows.append((float(ai["similarity"]),ar,en,r["issues"][0]["title"]))

if not rows:
    raise SystemExit("No semantic model result available. Run prepare_demo.bat first.")

rows.sort(reverse=True,key=lambda x:x[0])
score,ar,en,issue=rows[0]
print("MI'YAR DEMO CASE SELECTOR")
print(f"Semantic similarity: {score*100:.1f}%")
print(f"Critical finding: {issue}")
print("Arabic:",ar)
print("English:",en)
print("\nThis score is a model similarity signal, not a confidence probability.")
