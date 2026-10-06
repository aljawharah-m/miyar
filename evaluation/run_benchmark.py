
import csv,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from core.engine import analyze
rows=list(csv.DictReader((ROOT/"data"/"benchmark.csv").open(encoding="utf-8-sig")))
y=[];p=[];cy=[];cp=[]
for r in rows:
    z=analyze(r["arabic"],r["english"],use_live_sources=False,use_semantic_ai=False); flag=int(bool(z["issues"]))
    y.append(int(r["has_error"])); p.append(flag)
    if int(r["critical"]): cy.append(1); cp.append(flag)
tp=sum(a==1 and b==1 for a,b in zip(y,p)); fp=sum(a==0 and b==1 for a,b in zip(y,p)); tn=sum(a==0 and b==0 for a,b in zip(y,p)); fn=sum(a==1 and b==0 for a,b in zip(y,p))
precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0; f1=2*precision*recall/(precision+recall) if precision+recall else 0; fpr=fp/(fp+tn) if fp+tn else 0; cr=sum(cp)/len(cp) if cp else 0
print("MI'YAR LOCAL BENCHMARK v0.1 — SYNTHETIC DEVELOPMENT SET")
print(f"TP={tp} FP={fp} TN={tn} FN={fn}")
print(f"Precision={precision:.3f}\nRecall={recall:.3f}\nF1={f1:.3f}\nFPR={fpr:.3f}\nCritical Error Recall={cr:.3f}")
print("Do not present these as independently validated final results.")

report={"n":len(rows),"TP":tp,"FP":fp,"TN":tn,"FN":fn,"precision":precision,"recall":recall,"f1":f1,"fpr":fpr,"critical_error_recall":cr,"label":"SYNTHETIC DEVELOPMENT SET — NOT INDEPENDENT VALIDATION"}
(ROOT/"evaluation"/"benchmark_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
