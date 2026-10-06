from __future__ import annotations
import json,time
from pathlib import Path

from core.engine import analyze
import core.recognition as recognition
import core.sources as sources

ROOT=Path(__file__).resolve().parents[1]
CASES=json.loads((ROOT/'evaluation/sacred_hadith_cases.json').read_text(encoding='utf-8'))


def live_card(row,language,status='live_verified'):
    if status!='live_verified':
        return {'source':'HadeethEnc','publisher':'HadeethEnc.com','title':f'Hadith {row["id"]}','detail':'تعذر الاسترجاع','reference':'','status':'unavailable','evidence_type':'hadith_card','language':language,'verification':{'reference_verified':False,'reference_text_retrieved':False,'user_translation_verified':False}}
    detail=row['ar'] if language=='ar' else row['en']
    return {'source':'HadeethEnc','publisher':'HadeethEnc.com','title':f'Hadith {row["id"]}','detail':detail,'reference':row['id'],'status':'live_verified','evidence_type':'hadith_card','language':language,'browse_url':row['source_url'],'verification':{'reference_verified':True,'reference_text_retrieved':True,'user_translation_verified':False}}


def main():
    started=time.time(); byid={str(x['id']):x for x in CASES}
    # No external network in the audit: model the HadeethEnc search/card contract with
    # the official Arabic/English cards recorded in the fixture.
    real_search=recognition._hadeeth_search_live; real_qidx=recognition.build_quran_index_live
    real_hfetch=sources.fetch_hadeethenc; real_qfetch=sources.fetch_quranenc
    recognition._hadeeth_search_live=lambda text:[{'id':r['id'],'hadith_text':r['ar'],'title':r['ar'][:80]} for r in CASES]
    recognition.build_quran_index_live=lambda: []
    sources.fetch_hadeethenc=lambda hid,language: live_card(byid[str(hid)],language)
    sources.fetch_quranenc=lambda s,a: {'source':'QuranEnc','status':'unavailable','evidence_type':'quran_translation','detail':'offline audit','verification':{'reference_verified':False,'reference_text_retrieved':False,'user_translation_verified':False}}
    out={'schema':'miyar-hadith-reference-audit-v1','official_safe':{},'semantic_mutations':{},'provider_failure':{},'structured_ids':{}}
    try:
        safe_fail=[]; route_fail=[]
        for row in CASES:
            r=analyze(row['ar'],row['en'],use_live_sources=True,use_semantic_ai=False)
            if r['issues'] and len(safe_fail)<10:
                safe_fail.append({'id':row['id'],'issues':[(x.get('type'),x.get('title')) for x in r['issues']]})
            refcheck=next((x for x in r.get('checks',[]) if x.get('check')=='التحقق المرجعي'),None)
            if not refcheck or refcheck.get('status')!='pass':
                if len(route_fail)<10: route_fail.append({'id':row['id'],'check':refcheck})
        out['official_safe']={'total':len(CASES),'false_positive_count':len(safe_fail),'source_route_fail_count':len(route_fail),'examples':safe_fail+route_fail}

        misses=[]; not_high=[]; total=0
        for row in CASES:
            for j,mut in enumerate(row['mutations'],1):
                total+=1; r=analyze(row['ar'],mut,use_live_sources=True,use_semantic_ai=False)
                if not r['issues']:
                    if len(misses)<12: misses.append({'id':row['id'],'mutation':j,'text':mut})
                elif not any(x.get('religious_impact')=='high' for x in r['issues']):
                    if len(not_high)<12: not_high.append({'id':row['id'],'mutation':j,'issues':[(x.get('type'),x.get('title'),x.get('religious_impact')) for x in r['issues']]})
        out['semantic_mutations']={'total':total,'missed_count':len(misses),'without_high_religious_impact':len(not_high),'miss_examples':misses,'impact_examples':not_high}

        # Provider failure: no live verification may be claimed, and safe content must
        # not become unsafe merely because the provider is unavailable.
        sources.fetch_hadeethenc=lambda hid,language: live_card(byid[str(hid)],language,status='unavailable')
        failure_bad=[]
        for row in CASES:
            r=analyze(row['ar'],row['en'],use_live_sources=True,use_semantic_ai=False)
            refcheck=next((x for x in r.get('checks',[]) if x.get('check')=='التحقق المرجعي'),None)
            if r['issues'] or (refcheck and refcheck.get('status')=='pass'):
                if len(failure_bad)<10: failure_bad.append({'id':row['id'],'issues':[(x.get('type'),x.get('title')) for x in r['issues']],'check':refcheck})
        out['provider_failure']={'total':len(CASES),'unsafe_claim_count':len(failure_bad),'examples':failure_bad}

        # Structured real-looking HadeethEnc IDs: exact match is safe, changed ID is a
        # local reference-integrity defect. No external provider call is needed here.
        safe_id_fail=[]; changed_miss=[]
        ids=[str(x['id']) for x in CASES]
        for k,row in enumerate(CASES):
            hid=str(row['id']); other=ids[(k+1)%len(ids)]
            ar=f'[HADITH_REF: {hid}]'; good=f'[HADITH_REF: {hid}]'; bad=f'[HADITH_REF: {other}]'
            rg=analyze(ar,good,use_live_sources=False,use_semantic_ai=False)
            rb=analyze(ar,bad,use_live_sources=False,use_semantic_ai=False)
            if rg['issues'] and len(safe_id_fail)<8: safe_id_fail.append({'id':hid,'issues':[(x.get('type'),x.get('title')) for x in rg['issues']]})
            if not any(x.get('issue_taxonomy')=='SOURCE_INTEGRITY' for x in rb['issues']) and len(changed_miss)<8:
                changed_miss.append({'from':hid,'to':other,'issues':[(x.get('type'),x.get('title')) for x in rb['issues']]})
        out['structured_ids']={'safe_total':len(CASES),'safe_false_positive_count':len(safe_id_fail),'changed_total':len(CASES),'changed_missed_count':len(changed_miss),'examples':safe_id_fail+changed_miss}
    finally:
        recognition._hadeeth_search_live=real_search; recognition.build_quran_index_live=real_qidx
        sources.fetch_hadeethenc=real_hfetch; sources.fetch_quranenc=real_qfetch
    out['duration_seconds']=round(time.time()-started,3)
    (ROOT/'evaluation/hadith_reference_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
