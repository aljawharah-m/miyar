from __future__ import annotations
import json, re, time
from pathlib import Path
from collections import defaultdict

import sys
import pathlib

_MIYAR_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_MIYAR_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_MIYAR_PROJECT_ROOT))
from core.recognition import recognize_quran, _SURAH_NAMES
import core.sources as sources
from core.contextual_semantics import _citation_locator_root, _EN_SURAH_NAMES

ROOT=Path(__file__).resolve().parents[1]
Q=json.loads((ROOT/'data/quran_locator.json').read_text(encoding='utf-8'))

# ayah counts for valid next-ayah mutations
counts=defaultdict(int)
for row in Q: counts[int(row['surah'])]=max(counts[int(row['surah'])],int(row['ayah']))

def undiac(s):
    return re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06EDـ]','',s)

def correct_match(rec,s,a):
    if not rec: return False, 'miss'
    m=rec.get('match') or rec
    if m.get('ambiguous'):
        ok=any(int(x.get('surah',0))==s and int(x.get('ayah',0))==a for x in m.get('candidates',[]))
        return ok, 'ambiguous' if ok else 'wrong'
    return (int(m.get('surah',0))==s and int(m.get('ayah',0))==a), ('unique' if int(m.get('surah',0))==s and int(m.get('ayah',0))==a else 'wrong')

def audit_variant(label, make_text):
    stat={'total':0,'unique':0,'ambiguous_safe':0,'miss':0,'wrong':0}
    examples=[]
    for row in Q:
        s,a=int(row['surah']),int(row['ayah']); txt=make_text(row)
        r=recognize_quran(txt,live=False)
        ok,kind=correct_match(r,s,a); stat['total']+=1
        if ok and kind=='unique': stat['unique']+=1
        elif ok: stat['ambiguous_safe']+=1
        else:
            stat[kind]+=1
            if len(examples)<8: examples.append({'ref':f'{s}:{a}','text':txt[:160],'result':r})
    return stat,examples


def main():
    started=time.time(); out={'schema':'miyar-sacred-corpus-audit-v1','quran':{},'hadith':{},'notes':[]}
    variants={
        'exact':lambda r:r['text'],
        'undiacritized':lambda r:undiac(r['text']),
        'quoted':lambda r:f'«{r["text"]}»',
        'natural_context':lambda r:f'قال الله تعالى: «{r["text"]}»',
        'arabic_explicit_reference':lambda r:f'ورد في {_SURAH_NAMES[int(r["surah"])-1]}، الآية {r["ayah"]}.',
        'numeric_reference':lambda r:f'QURAN_REF: {r["surah"]}:{r["ayah"]}',
    }
    for name,fn in variants.items():
        st,ex=audit_variant(name,fn); out['quran'][name]=st
        if ex: out['quran'][name]['examples']=ex

    # Verify every explicit Arabic reference routes to the exact QuranEnc coordinates.
    calls=[]
    real_fetch=sources.fetch_quranenc
    def mock_fetch(s,a,*args,**kwargs):
        calls.append((int(s),int(a)))
        return {'source':'QuranEnc','publisher':'QuranEnc.com','title':f'{s}:{a}','detail':'mock verified','reference':f'{s}:{a}','status':'live_verified','evidence_type':'quran_translation','translation_key':'english_saheeh','verification':{'reference_verified':True,'reference_text_retrieved':True,'user_translation_verified':False}}
    sources.fetch_quranenc=mock_fetch
    route_wrong=[]; route_total=0
    try:
        for row in Q:
            s,a=int(row['surah']),int(row['ayah'])
            text=f'ورد في {_SURAH_NAMES[s-1]}، الآية {a}.'
            before=len(calls); sources.retrieve_reference_evidence(text,live=True); route_total+=1
            got=calls[-1] if len(calls)>before else None
            if got!=(s,a) and len(route_wrong)<8: route_wrong.append({'expected':[s,a],'got':got,'text':text})
    finally:
        sources.fetch_quranenc=real_fetch
    out['quran']['quranenc_routing']={'total':route_total,'wrong':len(route_wrong),'sample_errors':route_wrong}

    # Exhaustive Quran reference-integrity comparison using natural Arabic/English refs.
    safe_fail=[]; ayah_fail=[]; surah_fail=[]
    for row in Q:
        s,a=int(row['surah']),int(row['ayah']); ar=f'ورد في {_SURAH_NAMES[s-1]}، الآية {a}.'
        en_name=_EN_SURAH_NAMES[s-1]
        safe=f'The reference is Surah {en_name}, verse {a}.'
        if _citation_locator_root(ar,safe,1) and len(safe_fail)<8: safe_fail.append(f'{s}:{a}')
        next_a = a+1 if a < counts[s] else 1
        bad_a=f'The reference is Surah {en_name}, verse {next_a}.'
        roots=_citation_locator_root(ar,bad_a,1)
        if not any(x.get('type')=='reference_identifier_changed' for x in roots) and len(ayah_fail)<8: ayah_fail.append({'ref':f'{s}:{a}','target':f'{s}:{next_a}'})
        next_s=s+1 if s<114 else 1
        bad_s=f'The reference is Surah {_EN_SURAH_NAMES[next_s-1]}, verse {a}.'
        roots=_citation_locator_root(ar,bad_s,1)
        if not any(x.get('type')=='reference_identifier_changed' for x in roots) and len(surah_fail)<8: surah_fail.append({'ref':f'{s}:{a}','target':f'{next_s}:{a}'})
    out['quran']['reference_integrity']={
        'safe_total':len(Q),'safe_false_positive_count':len(safe_fail),'safe_examples':safe_fail,
        'ayah_mutation_total':len(Q),'ayah_mutation_missed_count':len(ayah_fail),'ayah_examples':ayah_fail,
        'surah_mutation_total':len(Q),'surah_mutation_missed_count':len(surah_fail),'surah_examples':surah_fail,
    }
    out['duration_seconds']=round(time.time()-started,3)
    path=ROOT/'evaluation/sacred_corpus_audit.json'; path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
