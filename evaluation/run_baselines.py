import csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze
from core.semantic_ai import run_semantic_ai
ROWS=list(csv.DictReader((ROOT/'data'/'benchmark.csv').open(encoding='utf-8-sig')))

def metrics(y,p):
    tp=sum(a==1 and b==1 for a,b in zip(y,p)); fp=sum(a==0 and b==1 for a,b in zip(y,p))
    tn=sum(a==0 and b==0 for a,b in zip(y,p)); fn=sum(a==1 and b==0 for a,b in zip(y,p))
    pr=tp/(tp+fp) if tp+fp else 0; rc=tp/(tp+fn) if tp+fn else 0; f1=2*pr*rc/(pr+rc) if pr+rc else 0
    fpr=fp/(fp+tn) if fp+tn else 0
    return {'TP':tp,'FP':fp,'TN':tn,'FN':fn,'Precision':pr,'Recall':rc,'F1':f1,'FPR':fpr}

y=[int(r['has_error']) for r in ROWS]
full=[]; ai_only=[]
for r in ROWS:
    z=analyze(r['arabic'],r['english'],use_live_sources=False,use_semantic_ai=False)
    full.append(1 if z['issues'] else 0)
    a=run_semantic_ai(r['arabic'],r['english'],enabled=True)
    if not a.get('available'):
        raise SystemExit('Semantic AI model is not available. Run scripts/preflight.py first.')
    ai_only.append(1 if a.get('status') in {'fail','review'} else 0)
report={'set':'synthetic development set','semantic_ai_only':metrics(y,ai_only),'miyar_without_live_sources':metrics(y,full),'note':'Development evidence only; not independent field validation.'}
print(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'evaluation'/'baseline_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
