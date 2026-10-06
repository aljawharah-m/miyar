import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze
rows=list(csv.DictReader((ROOT/'data'/'benchmark.csv').open(encoding='utf-8-sig')))[:20]
runs=10
failures=[]
for row in rows:
    signatures=[]
    for _ in range(runs):
        z=analyze(row['arabic'],row['english'],use_live_sources=False,use_semantic_ai=False)
        signatures.append((z['status'],tuple((i.get('type'),i.get('severity'),i.get('title')) for i in z['issues'])))
    if len(set(signatures))!=1:
        failures.append(row['id'])
report={'cases':len(rows),'runs_per_case':runs,'comparisons':len(rows)*runs,'repeatable_cases':len(rows)-len(failures),'failures':failures,'label':'DETERMINISTIC CORE REPEATABILITY — DEVELOPMENT EVIDENCE'}
print(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'evaluation'/'repeatability_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
