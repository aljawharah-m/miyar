import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze

# Synthetic article-sized stress test. Errors are intentionally distributed across the
# document so a correct marker elsewhere cannot mask a later wrong rendering.
filler_ar = "هذا شرح تعليمي عام يوضح الفكرة للقارئ دون إضافة حكم جديد. "
filler_en = "This is a general educational explanation that clarifies the idea without adding a new ruling. "

ar_errors = (
    "الزكاة واجبة. "
    "والصدقة مستحبة. "
    "الوضوء شرط للصلاة. "
    "لا يجوز هذا إلا للضرورة. "
    "عدد الركعات ثلاث. "
    "السنة هدي النبي صلى الله عليه وسلم. "
)
en_errors = (
    "Charity is obligatory. "
    "Zakat is obligatory. "
    "Wudu is required for prayer. "
    "This is not permissible. "
    "The number of rakahs is four. "
    "Sunnah is merely tradition. "
)

ar = (filler_ar*45) + ar_errors + (filler_ar*45) + "الوضوء طهارة مخصوصة. " + (filler_ar*30)
en = (filler_en*45) + en_errors + (filler_en*45) + "Washing is simple cleaning. " + (filler_en*30)
assert len(ar) < 12000 and len(en) < 12000
z=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)

findings=z['issues']
checks={
    'zakat_flattening': any(i.get('type')=='flattening' and i.get('source_span')=='الزكاة' for i in findings),
    'sadaqah_to_zakat': any(i.get('type')=='flattening' and i.get('source_span')=='الصدقة' for i in findings),
    'exception_loss': any(i.get('type') in {'exception','exclusivity_shift'} for i in findings),
    'word_number_shift': any(i.get('type')=='quantity' and i.get('source_span')=='3' and i.get('translation_span')=='4' for i in findings),
    'ruling_degree_shift': any(i.get('type')=='modality_shift' for i in findings),
    'sunnah_reductive_gloss': any(i.get('type')=='terminology' and i.get('source_span')=='السنة' for i in findings),
    'later_wudu_flattening': any(i.get('type')=='flattening' and i.get('source_span')=='الوضوء' for i in findings),
}
ok=z['status']=='critical' and all(checks.values())
report={
  'passed':bool(ok),
  'arabic_chars':len(ar),
  'english_chars':len(en),
  'injected_gap_classes':len(checks),
  'detected_injected_gap_classes':sum(checks.values()),
  'checks':checks,
  'issue_count':len(findings),
  'issue_types':[i.get('type') for i in findings],
  'note':'Synthetic long-passage development stress test; validates distributed structural, ruling, quantity and terminology errors. It is not independent field validation.'
}
print(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'evaluation'/'long_text_stress_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if not ok: raise SystemExit(1)
