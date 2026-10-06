from __future__ import annotations
import json,time
from pathlib import Path
from core.engine import analyze
import core.sources as sources

ROOT=Path(__file__).resolve().parents[1]
CASES=json.loads((ROOT/'evaluation/sacred_quran_reference_cases.json').read_text(encoding='utf-8'))
BY={(int(x['surah']),int(x['ayah'])):x for x in CASES}
SURAH_EN={1:'Al-Fatihah',2:'Al-Baqarah',112:'Al-Ikhlas',113:'Al-Falaq',114:'An-Nas'}

def fake_quran(s,a,translation_key='english_saheeh',status='live_verified'):
    row=BY.get((int(s),int(a)))
    if status!='live_verified' or not row:
        return {'source':'QuranEnc','publisher':'QuranEnc.com','title':f'{s}:{a}','detail':'تعذر الاسترجاع','reference':f'{s}:{a}','status':'unavailable','evidence_type':'quran_translation','verification':{'reference_verified':False,'source_text_retrieved':False,'user_translation_verified':False}}
    return {'source':'QuranEnc','publisher':'QuranEnc.com','title':f'{s}:{a}','detail':row['en'],'reference':f'{s}:{a}','status':'live_verified','evidence_type':'quran_translation','translation_key':'english_rwwad','url':row['source_url'],'verification':{'reference_verified':True,'source_text_retrieved':True,'user_translation_verified':False}}

def ar_input(row): return f"ورد المرجع القرآني QURAN_REF: {row['surah']}:{row['ayah']} والنص: «{row['ar']}»"
def en_input(row,text): return f"QURAN_REF: {row['surah']}:{row['ayah']} {text}"

def main():
    start=time.time(); real=sources.fetch_quranenc; out={'schema':'miyar-quran-reference-audit-v1'}
    try:
        sources.fetch_quranenc=fake_quran
        safe=[]
        for row in CASES:
            r=analyze(ar_input(row),en_input(row,row['en']),use_live_sources=True,use_semantic_ai=False)
            if r['issues']: safe.append({'ref':f"{row['surah']}:{row['ayah']}",'issues':[(x.get('type'),x.get('title'),x.get('religious_impact')) for x in r['issues']]})
        misses=[]; nohigh=[]; total=0
        for row in CASES:
            for i,m in enumerate(row['mutations'],1):
                total+=1; r=analyze(ar_input(row),en_input(row,m),use_live_sources=True,use_semantic_ai=False)
                if not r['issues']: misses.append({'ref':f"{row['surah']}:{row['ayah']}",'mutation':i,'text':m})
                elif not any(x.get('religious_impact')=='high' for x in r['issues']): nohigh.append({'ref':f"{row['surah']}:{row['ayah']}",'mutation':i,'issues':[(x.get('type'),x.get('title'),x.get('religious_impact')) for x in r['issues']]})
        out['official_safe']={'total':len(CASES),'false_positive_count':len(safe),'examples':safe[:10]}
        out['semantic_mutations']={'total':total,'missed_count':len(misses),'without_high_religious_impact':len(nohigh),'miss_examples':misses[:10],'impact_examples':nohigh[:10]}
        # Provider outage: exact official translation must not become unsafe merely because QuranEnc is unavailable, and no live pass may be fabricated.
        sources.fetch_quranenc=lambda s,a,translation_key='english_saheeh': fake_quran(s,a,translation_key,status='unavailable')
        bad=[]
        for row in CASES:
            r=analyze(ar_input(row),en_input(row,row['en']),use_live_sources=True,use_semantic_ai=False)
            live=[x for x in r.get('evidence',[]) if x.get('source')=='QuranEnc' and x.get('status')=='live_verified']
            if r['issues'] or live: bad.append({'ref':f"{row['surah']}:{row['ayah']}",'issues':[(x.get('type'),x.get('title')) for x in r['issues']],'live_claims':len(live)})
        out['provider_failure']={'total':len(CASES),'unsafe_or_false_live_claim_count':len(bad),'examples':bad[:10]}
    finally: sources.fetch_quranenc=real
    out['duration_seconds']=round(time.time()-start,3)
    (ROOT/'evaluation/quran_reference_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
