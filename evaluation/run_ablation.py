from __future__ import annotations
import csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze
from core.rules import analyze_rules
from core.terminology import analyze_terminology
from core.advanced_semantics import analyze_scope, analyze_term_relations, analyze_provenance

ROWS=list(csv.DictReader((ROOT/'data'/'benchmark.csv').open(encoding='utf-8-sig')))

def metrics(y,p):
    tp=sum(a==1 and b==1 for a,b in zip(y,p)); fp=sum(a==0 and b==1 for a,b in zip(y,p))
    tn=sum(a==0 and b==0 for a,b in zip(y,p)); fn=sum(a==1 and b==0 for a,b in zip(y,p))
    pr=tp/(tp+fp) if tp+fp else 0.0; rc=tp/(tp+fn) if tp+fn else 0.0
    f1=2*pr*rc/(pr+rc) if pr+rc else 0.0; fpr=fp/(fp+tn) if fp+tn else 0.0
    return {'TP':tp,'FP':fp,'TN':tn,'FN':fn,'Precision':round(pr,4),'Recall':round(rc,4),'F1':round(f1,4),'FPR':round(fpr,4)}

y=[int(r['has_error']) for r in ROWS]
struct=[]; term=[]; structured_plus_term=[]; full=[]
for r in ROWS:
    ar,en=r['arabic'],r['english']
    rr=analyze_rules(ar,en)
    tt=analyze_terminology(ar,en)
    adv=(analyze_scope(ar,en).get('issues',[])+analyze_term_relations(ar,en).get('issues',[])+analyze_provenance(ar,en).get('issues',[]))
    struct.append(1 if rr.get('issues') else 0)
    term.append(1 if tt.get('issues') else 0)
    structured_plus_term.append(1 if (rr.get('issues') or tt.get('issues') or adv) else 0)
    z=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    full.append(1 if z.get('issues') else 0)

report={
  'set':'synthetic development set — ablation evidence only',
  'n':len(ROWS),
  'structure_rules_only':metrics(y,struct),
  'terminology_guard_only':metrics(y,term),
  'structure_plus_terminology_plus_scope':metrics(y,structured_plus_term),
  'full_miyar_without_live_sources_or_semantic_ai':metrics(y,full),
  'interpretation':'This is an ablation study on the included development set. It demonstrates the contribution of Mi\'yar layers; it is not independent field validation and does not replace the semantic-AI-only baseline, which requires the local embedding model.'
}
print(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'evaluation'/'ablation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
