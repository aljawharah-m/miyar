from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from core import sources
samples=[
 'وفي هذا المثال التجريبي [HADITH_REF: TEST-123] بهذه الصيغة.',
 'للاختبار [SOURCE_ID: ABC-001] فقط.',
 'مثال [HADITH_REF: MOCK-9] و [SOURCE_ID: DEMO-2].',
]
external_calls=0
orig=sources.recognize_source
def fake(*a,**k):
    global external_calls
    external_calls+=1
    return None
sources.recognize_source=fake
try:
    for x in samples:
        rec,evidence=sources.retrieve_reference_evidence_multi(x,live=True)
        assert rec==[] and evidence==[]
finally:
    sources.recognize_source=orig
report={'external_calls':external_calls,'samples':len(samples),'pass':external_calls==0}
(ROOT/'evaluation'/'synthetic_id_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if external_calls: raise SystemExit(1)
