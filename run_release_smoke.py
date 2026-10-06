import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze

CASES=[
    {"name":"safe_exception","ar":"لا يجوز هذا إلا في حالة الضرورة","en":"This is not permissible except in a case of necessity","status":"safe","issues":0},
    {"name":"lost_exception","ar":"لا يجوز هذا إلا في حالة الضرورة","en":"This is not permissible","status":"critical","issues":1,"type":"exception"},
    {"name":"modality_shift","ar":"يجوز فعل ذلك","en":"It must be done","status":"critical","issues":1,"type":"modality_shift"},
    {"name":"tawhid_flattening","ar":"التوحيد أصل عظيم","en":"Oneness is a great principle","status":"critical","issues":1,"type":"flattening"},
    {"name":"zakat_flattening","ar":"الزكاة واجبة","en":"Charity is obligatory","status":"critical","type":"flattening","term":"الزكاة"},
    {"name":"zakat_precise","ar":"الزكاة واجبة","en":"Zakat is obligatory","status":"safe","issues":0},
    {"name":"sadaqah_not_zakat","ar":"الصدقة مستحبة","en":"Zakat is recommended","status":"critical","type":"flattening","term":"الصدقة"},
    {"name":"wudu_not_washing","ar":"الوضوء شرط للصلاة","en":"Washing is a condition for prayer","status":"critical","type":"flattening","term":"الوضوء"},
    {"name":"multi_term_clean","ar":"الزكاة واجبة والصدقة مستحبة","en":"Zakat is obligatory and charity is recommended","status":"safe","issues":0},
    {"name":"repeated_term_partial_flattening","ar":"الزكاة واجبة. والزكاة لها مصارف محددة.","en":"Zakat is obligatory. Charity has specified recipients.","status":"critical","type":"flattening","term":"الزكاة"},
    {"name":"recommended_to_obligatory","ar":"هذا مستحب","en":"This is obligatory","status":"critical","issues":1,"type":"modality_shift"},
    {"name":"makruh_to_haram","ar":"هذا مكروه","en":"This is haram","status":"critical","issues":1,"type":"modality_shift"},
    {"name":"multiple_gaps","ar":"الزكاة واجبة. لا يجوز هذا إلا للضرورة. العدد 3.","en":"Charity is obligatory. This is not permissible. The number is 4.","status":"critical","min_issues":3,"types":["flattening","exception","quantity"]},
    {"name":"long_exception_count","ar":"لا يجوز الأول إلا للضرورة. ولا يجوز الثاني إلا بإذن.","en":"The first is not permissible except in necessity. The second is not permissible.","status":"critical","type":"exception"},
    {"name":"quran_valid","ar":"اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ","en":"Allah—there is no deity except Him, the Ever-Living, the Sustainer of existence.","status":"safe","issues":0,"recognition":"quran"},
    {"name":"quran_exclusivity_error","ar":"اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ","en":"Allah is one god among many, the Ever-Living.","status":"critical","issues":2,"types":["exclusivity_shift","omission"],"recognition":"quran"},
]

results=[]
for c in CASES:
    z=analyze(c["ar"],c["en"],use_live_sources=False,use_semantic_ai=False)
    ok=z["status"]==c["status"]
    if "issues" in c:
        ok=ok and len(z["issues"])==c["issues"]
    if c.get("min_issues") is not None:
        ok=ok and len(z["issues"])>=c["min_issues"]
    if c.get("type"):
        ok=ok and any(i.get("type")==c["type"] for i in z["issues"])
    if c.get("types"):
        got={i.get("type") for i in z["issues"]}
        ok=ok and set(c["types"]).issubset(got)
    if c.get("term"):
        ok=ok and any(i.get("source_span")==c["term"] for i in z["issues"])
    if c.get("recognition"):
        ok=ok and z.get("recognition") and z["recognition"].get("kind")==c["recognition"]
    results.append({
        "name":c["name"],"passed":bool(ok),"status":z["status"],"issue_count":len(z["issues"]),
        "issue_types":[i.get("type") for i in z["issues"]],
        "recognition":z.get("recognition",{}).get("kind") if z.get("recognition") else None,
    })

report={"suite":"Mi'yar Gold release smoke suite","passed":sum(r["passed"] for r in results),"total":len(results),"results":results,"note":"Model-independent smoke test. Local semantic-model and live-source connectivity are checked separately by scripts/preflight.py on the deployment machine."}
print(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'evaluation'/'release_smoke_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if not all(r["passed"] for r in results):
    raise SystemExit(1)
