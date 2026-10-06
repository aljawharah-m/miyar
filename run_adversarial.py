from pathlib import Path
import csv, sys, json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze

rows=list(csv.DictReader((ROOT/'data'/'benchmark_adversarial.csv').open(encoding='utf-8-sig')))
tp=fp=tn=fn=0; critical_total=critical_hit=0
mistakes=[]
for row in rows:
    z=analyze(row['arabic'],row['english'],use_live_sources=False,use_semantic_ai=False)
    pred=int(bool(z['issues']))
    y=int(row['has_error'])
    if pred and y: tp+=1
    elif pred and not y: fp+=1; mistakes.append((row['id'],'FP',row['category']))
    elif not pred and not y: tn+=1
    else: fn+=1; mistakes.append((row['id'],'FN',row['category']))
    if int(row['critical']):
        critical_total+=1
        if pred: critical_hit+=1
precision=tp/(tp+fp) if tp+fp else 0
recall=tp/(tp+fn) if tp+fn else 0
f1=2*precision*recall/(precision+recall) if precision+recall else 0
fpr=fp/(fp+tn) if fp+tn else 0
cer=critical_hit/critical_total if critical_total else 0
report={'n':len(rows),'TP':tp,'FP':fp,'TN':tn,'FN':fn,'precision':precision,'recall':recall,'f1':f1,'fpr':fpr,'critical_error_recall':cer,'mistakes':mistakes,'label':'SYNTHETIC ADVERSARIAL DEVELOPMENT SET — NOT INDEPENDENT VALIDATION'}
print(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'evaluation'/'adversarial_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
