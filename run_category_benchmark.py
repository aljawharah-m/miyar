import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from core.engine import analyze

sources=[('benchmark',ROOT/'data'/'benchmark.csv'),('adversarial',ROOT/'data'/'benchmark_adversarial.csv')]
rows=[]
for dataset,path in sources:
    for r in csv.DictReader(path.open(encoding='utf-8-sig')):
        r['dataset']=dataset; rows.append(r)

GROUPS={
    'terminology': {'terminology','terminology_flattening','terminology_precision','multi_term'},
    'rulings': {'ruling_alignment','ruling_degree','modality','negation'},
    'references': {'quran','attribution'},
    'numbers': {'quantity'},
}

def metrics(sub):
    y=[]; p=[]
    for r in sub:
        z=analyze(r['arabic'],r['english'],use_live_sources=False,use_semantic_ai=False)
        y.append(int(r['has_error'])); p.append(int(bool(z['issues'])))
    tp=sum(a==1 and b==1 for a,b in zip(y,p)); fp=sum(a==0 and b==1 for a,b in zip(y,p))
    tn=sum(a==0 and b==0 for a,b in zip(y,p)); fn=sum(a==1 and b==0 for a,b in zip(y,p))
    precision=tp/(tp+fp) if tp+fp else None; recall=tp/(tp+fn) if tp+fn else None
    f1=(2*precision*recall/(precision+recall)) if precision is not None and recall is not None and precision+recall else None
    fpr=fp/(fp+tn) if fp+tn else None
    return {'n':len(sub),'TP':tp,'FP':fp,'TN':tn,'FN':fn,'precision':precision,'recall':recall,'f1':f1,'fpr':fpr}

report={'label':'CATEGORY-SLICED SYNTHETIC DEVELOPMENT EVIDENCE — NOT INDEPENDENT RELIGIOUS VALIDATION','groups':{}}
for name,cats in GROUPS.items():
    sub=[r for r in rows if r['category'] in cats]
    report['groups'][name]={'categories':sorted(cats),**metrics(sub)}
(ROOT/'evaluation'/'category_benchmark_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
