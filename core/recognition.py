import re, json
from pathlib import Path
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from .normalization import normalize_ar

TIMEOUT=4
_QURAN_INDEX_CACHE=None
_LOCAL_QURAN_CACHE=None

# Offline locator seeds for demo resilience. These are NOT treated as the authoritative
# evidence source; they only locate a candidate reference when the network is unavailable.
QURAN_SEEDS=[
    {"surah":2,"ayah":255,"name":"البقرة","text":"الله لا إله إلا هو الحي القيوم"},
    {"surah":1,"ayah":1,"name":"الفاتحة","text":"بسم الله الرحمن الرحيم"},
    {"surah":1,"ayah":2,"name":"الفاتحة","text":"الحمد لله رب العالمين"},
    {"surah":112,"ayah":1,"name":"الإخلاص","text":"قل هو الله أحد"},
    {"surah":112,"ayah":2,"name":"الإخلاص","text":"الله الصمد"},
    {"surah":113,"ayah":1,"name":"الفلق","text":"قل أعوذ برب الفلق"},
    {"surah":114,"ayah":1,"name":"الناس","text":"قل أعوذ برب الناس"},
    {"surah":2,"ayah":286,"name":"البقرة","text":"لا يكلف الله نفسا إلا وسعها"},
    {"surah":94,"ayah":5,"name":"الشرح","text":"فإن مع العسر يسرا"},
    {"surah":94,"ayah":6,"name":"الشرح","text":"إن مع العسر يسرا"},
]

HADITH_SEEDS=[
    {"id":"4560","text":"إنما الأعمال بالنيات وإنما لكل امرئ ما نوى","label":"إنما الأعمال بالنيات"},
    {"id":"66511","text":"إنما الأعمال بالنيات وإنما لكل امرئ ما نوى","label":"إنما الأعمال بالنيات"},
    # Canonical HadeethEnc locator.  This is only a locator seed; the live card is
    # still retrieved from HadeethEnc before it is shown as authoritative evidence.
    {"id":"4309","text":"الدين النصيحة","label":"الدين النصيحة"},
]



# Arabic surah-name locator for explicit references such as
# «سورة البقرة، الآية 183».  This only locates a candidate; QuranEnc remains
# the authoritative live evidence source.
_SURAH_NAMES = [
    "الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"
]
_SURAH_NAME_TO_NUMBER={normalize_ar(name):i for i,name in enumerate(_SURAH_NAMES,1)}

def _explicit_quran_locator(text):
    """Locate an explicitly written surah/ayah reference without judging content."""
    raw=normalize_ar(text or "")
    # Natural Arabic: سورة البقرة، الآية 183 / سوره البقره ايه 183
    m=re.search(r"(?:سوره\s+)?([\u0600-\u06FF ]{2,30}?)[،,:\s]+(?:ال)?(?:ايه|اية|آيه)\s*(?:رقم\s*)?(\d{1,3})\b", raw)
    if m:
        name=re.sub(r"\s+"," ",m.group(1)).strip()
        # Keep the shortest tail that resolves to a known surah name.
        parts=name.split()
        for start in range(len(parts)):
            cand=" ".join(parts[start:])
            n=_SURAH_NAME_TO_NUMBER.get(cand)
            if n:
                return {"surah":n,"ayah":int(m.group(2)),"text":"","score":1.0,"method":"explicit_quran_reference","authoritative":False}
    # Structured numeric locator: 2:183 or QURAN_REF: 2:183
    m=re.search(r"(?:QURAN_REF\s*:\s*)?(\d{1,3})\s*:\s*(\d{1,3})", text or "", re.I)
    if m:
        surah,ayah=map(int,m.groups())
        if 1 <= surah <= 114 and ayah >= 1:
            return {"surah":surah,"ayah":ayah,"text":"","score":1.0,"method":"explicit_quran_reference","authoritative":False}
    return None

def _quoted_arabic_candidates(text):
    raw=text or ""
    out=[]
    for pat in (r"«([^»]{2,500})»", r"\"([^\"]{2,500})\""):
        out.extend(m.group(1).strip() for m in re.finditer(pat,raw) if re.search(r"[\u0600-\u06FF]",m.group(1)))
    return out


def _load_local_quran_index():
    """Load the bundled full-Quran locator index.

    The local copy is used only to locate a likely surah/ayah reference; it is never
    treated as the authoritative translation evidence. Authoritative translation
    evidence still comes from QuranEnc when live retrieval succeeds.
    """
    global _LOCAL_QURAN_CACHE
    if _LOCAL_QURAN_CACHE is not None:
        return _LOCAL_QURAN_CACHE
    path=Path(__file__).resolve().parent.parent / "data" / "quran_locator.json"
    try:
        rows=json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        rows=[]
    clean=[]
    for row in rows if isinstance(rows,list) else []:
        if not isinstance(row,dict):
            continue
        text=row.get("text","")
        try:
            surah=int(row.get("surah")); ayah=int(row.get("ayah"))
        except Exception:
            continue
        norm=_clean_ar(text)
        if norm:
            clean.append({"surah":surah,"ayah":ayah,"text":text,"norm":norm})
    _LOCAL_QURAN_CACHE=clean
    return clean


def _local_quran_match(text):
    """Find a Quran verse or sufficiently distinctive verse fragment locally.

    Exact full-ayah matches are recognized even when very short (e.g. muqatta'at).
    Repeated identical/contained text is returned as ambiguous rather than guessed.
    The bundled corpus is only a locator; authoritative translation evidence still
    comes from QuranEnc when live retrieval succeeds.
    """
    q=_clean_ar(text)
    if not q:
        return None
    rows=_load_local_quran_index()
    raw=text or ""
    quranic_marks=sum(1 for ch in raw if ("\u0617" <= ch <= "\u061A") or ("\u064B" <= ch <= "\u0652") or ("\u06D6" <= ch <= "\u06ED") or ch=="\u0670")

    # Exact equality is safe to recognize regardless of length.  If the exact same
    # Arabic ayah text occurs at multiple Quran locations, never invent one location.
    exact=[row for row in rows if row.get("norm","")==q]
    if exact:
        # Even an exact full-ayah string may also occur as a verbatim fragment inside
        # another ayah (e.g. 3:2 is also the opening of 2:255).  In that situation the
        # pasted text alone does not justify choosing one location.
        containing_exact=[row for row in rows if q in row.get("norm","")]
        if len(containing_exact)==1:
            row=exact[0]
            return {"surah":row["surah"],"ayah":row["ayah"],"text":row["text"],
                    "score":1.0,"method":"local_full_quran_locator","authoritative":False}
        return {
            "score":1.0,"method":"local_full_quran_locator_ambiguous",
            "authoritative":False,"ambiguous":True,
            "candidates":[{"surah":r["surah"],"ayah":r["ayah"]} for r in containing_exact],
            "candidate_count":len(containing_exact),"text":exact[0]["text"],
        }

    # First find every verse that contains the pasted text. This catches the important
    # case where a phrase is itself a complete ayah in one place but also appears as a
    # fragment of another ayah. Such input is ambiguous and must not be guessed.
    containing=[]
    for row in rows:
        v=row.get("norm","")
        if q in v:
            ratio=min(len(q),len(v))/max(1,max(len(q),len(v)))
            containing.append((ratio,row))

    if containing and (len(q)>=12 or quranic_marks>=1):
        containing.sort(key=lambda x:x[0], reverse=True)
        if len(containing)==1:
            ratio,row=containing[0]
            return {
                "surah":row["surah"],"ayah":row["ayah"],"text":row["text"],
                "score":max(0.92,ratio),"method":"local_full_quran_locator","authoritative":False,
            }
        best_ratio=containing[0][0]
        # Preserve all candidates for safety.  Candidate lists are internal locator
        # evidence and prevent repeated Quran text from being misattributed.
        candidates=[{"surah":row["surah"],"ayah":row["ayah"]} for _,row in containing]
        return {
            "score":max(0.92,best_ratio),"method":"local_full_quran_locator_ambiguous",
            "authoritative":False,"ambiguous":True,"candidates":candidates,
            "candidate_count":len(candidates),"text":containing[0][1]["text"],
        }

    if len(q)<12:
        return None

    # If the input is a longer article containing one complete sufficiently long ayah,
    # locate it only when exactly one such verse is embedded.
    embedded=[]
    for row in rows:
        v=row.get("norm","")
        if len(v)>=40 and v in q:
            ratio=min(len(q),len(v))/max(1,max(len(q),len(v)))
            embedded.append((ratio,row))
    if len(embedded)==1:
        ratio,row=embedded[0]
        return {
            "surah":row["surah"],"ayah":row["ayah"],"text":row["text"],
            "score":max(0.92,ratio),"method":"local_full_quran_locator",
            "authoritative":False,
        }
    if len(embedded)>1:
        embedded.sort(key=lambda x:x[0], reverse=True)
        return {
            "score":max(0.92,embedded[0][0]),"method":"local_full_quran_locator_ambiguous",
            "authoritative":False,"ambiguous":True,
            "candidates":[{"surah":r["surah"],"ayah":r["ayah"]} for _,r in embedded[:8]],
            "text":embedded[0][1]["text"],
        }
    return None


def _clean_ar(text):
    s=normalize_ar(text)
    s=re.sub(r"[^\u0600-\u06FF\s]"," ",s)
    s=re.sub(r"\s+"," ",s).strip()
    return s


def _similarity(a,b):
    a,b=_clean_ar(a),_clean_ar(b)
    if not a or not b: return 0.0
    if a in b or b in a:
        shorter=min(len(a),len(b)); longer=max(len(a),len(b))
        return max(0.92, shorter/max(1,longer))
    return SequenceMatcher(None,a,b).ratio()


def _extract_aya_rows(payload, surah_no):
    """Best-effort parser for ICADB Quran ayah payloads without assuming one schema."""
    rows=[]
    if isinstance(payload,dict):
        candidates=None
        for k in ("results","data","ayas","ayahs","items"):
            if isinstance(payload.get(k),list): candidates=payload[k]; break
        if candidates is None and all(isinstance(v,dict) for v in payload.values()):
            candidates=list(payload.values())
    elif isinstance(payload,list):
        candidates=payload
    else:
        candidates=[]
    for idx,item in enumerate(candidates or [],1):
        if not isinstance(item,dict): continue
        text=""
        for k in ("text","aya_text","ayah_text","arabic_text","arabic","content","text_uthmani"):
            if isinstance(item.get(k),str) and item[k].strip(): text=item[k]; break
        n=item.get("aya") or item.get("ayah") or item.get("aya_no") or item.get("ayah_no") or item.get("number") or item.get("id") or idx
        try: n=int(n)
        except Exception: n=idx
        if text: rows.append({"surah":surah_no,"ayah":n,"text":text})
    return rows


def _fetch_icadb_surah(surah_no, session=None):
    ses=session or requests
    url=f"https://icadb.com/quran/api/quran/surahs/{surah_no}/ayas/"
    r=ses.get(url,timeout=TIMEOUT)
    r.raise_for_status()
    return _extract_aya_rows(r.json(),surah_no)


def build_quran_index_live(max_workers=16):
    global _QURAN_INDEX_CACHE
    if _QURAN_INDEX_CACHE is not None:
        return _QURAN_INDEX_CACHE
    rows=[]
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures={ex.submit(_fetch_icadb_surah,s):s for s in range(1,115)}
        for f in as_completed(futures):
            try: rows.extend(f.result())
            except Exception: pass
    _QURAN_INDEX_CACHE=rows
    return rows


def recognize_quran(text, live=True, live_index=None, min_chars=12):
    explicit=_explicit_quran_locator(text)
    if explicit:
        return explicit
    q=_clean_ar(text)
    if not q:
        return None
    # Explicit Quran cues or dense recitation marks raise prior confidence.
    raw=text or ""
    cue=bool(re.search(r"\b(?:سوره|اية|ايه|قال الله|القران)\b",q))
    quranic_marks=sum(1 for ch in raw if ("\u0617" <= ch <= "\u061A") or ("\u064B" <= ch <= "\u0652") or ("\u06D6" <= ch <= "\u06ED") or ch=="\u0670")
    looks_scriptural = cue or quranic_marks >= 3

    # Prefer quoted Arabic payloads when the user wraps an ayah in natural prose such
    # as: قال الله تعالى: «...».  This keeps the surrounding attribution sentence from
    # diluting an otherwise exact Quran match.
    quoted=_quoted_arabic_candidates(text)
    if quoted:
        quoted_matches=[]
        for candidate in quoted:
            m=_local_quran_match(candidate)
            if m:
                quoted_matches.append(m)
        if len(quoted_matches)==1:
            return quoted_matches[0]
        if len(quoted_matches)>1:
            # Multiple separately quoted Quran matches in one review unit are not one
            # unambiguous reference; preserve all candidate locations instead of guessing.
            locs=[]
            for m in quoted_matches:
                if m.get("ambiguous"):
                    locs.extend(m.get("candidates",[]))
                elif m.get("surah") and m.get("ayah"):
                    locs.append({"surah":m["surah"],"ayah":m["ayah"]})
            uniq=[]; seen=set()
            for x in locs:
                key=(x.get("surah"),x.get("ayah"))
                if key not in seen:
                    seen.add(key); uniq.append(x)
            return {"score":1.0,"method":"quoted_quran_locator_ambiguous",
                    "authoritative":False,"ambiguous":True,"candidates":uniq,
                    "candidate_count":len(uniq),"text":quoted[0]}

    # Prefer the bundled full-Quran locator before tiny demo seeds. This prevents a
    # short seed phrase contained inside a different longer ayah from stealing the
    # reference. Repeated text is returned as ambiguous rather than guessed.
    local=_local_quran_match(text)
    if local:
        return local

    if len(q)<min_chars:
        return None

    best=None
    for row in QURAN_SEEDS:
        v=_clean_ar(row["text"])
        # Seeds are only fallback locators for a query that is close in length to the
        # seed itself; never match merely because the seed is a small substring of a
        # much longer input.
        ratio=min(len(q),len(v))/max(1,max(len(q),len(v)))
        if ratio < 0.70:
            continue
        sc=_similarity(q,row["text"])
        if sc>=0.82 and (best is None or sc>best["score"]):
            best={**row,"score":sc,"method":"offline_locator_seed","authoritative":False}
    if best and best["score"]>=0.90:
        return best

    if live_index:
        for row in live_index:
            sc=_similarity(q,row.get("text",""))
            if sc>=0.84 and (best is None or sc>best["score"]):
                best={**row,"score":sc,"method":"icadb_text_match","authoritative":True}
    # Do not trigger a full Quran index build for an arbitrary long article merely
    # because it mentions the Quran. Live full-index matching is reserved for
    # verse-sized/scriptural-looking input after the local locator could not decide.
    live_candidate = looks_scriptural and len(q) <= 1200
    if live and live_index is None and live_candidate:
        try:
            idx=build_quran_index_live()
            for row in idx:
                sc=_similarity(q,row.get("text",""))
                if sc>=0.84 and (best is None or sc>best["score"]):
                    best={**row,"score":sc,"method":"icadb_text_match","authoritative":True}
        except Exception:
            pass
    if best and (best["score"]>=0.88 or (cue and best["score"]>=0.82)):
        return best
    return None


def _hadeeth_search_live(text):
    url="https://hadeethenc.com/api/v1/hadeeths/search/"
    r=requests.get(url,params={"phrase":text,"language":"ar"},timeout=TIMEOUT)
    r.raise_for_status()
    d=r.json()
    if isinstance(d,dict):
        for k in ("data","results","items"):
            if isinstance(d.get(k),list): return d[k]
    return d if isinstance(d,list) else []


def _hadith_live_excerpt(text):
    """Return a small cue-centered excerpt instead of sending arbitrary prose to search."""
    raw=(text or "").strip()
    if not raw:
        return ""
    m=re.search(r"(?:قال\s+(?:رسول|النبي)|رواه|ورد\s+في\s+الحديث|في\s+الحديث)", raw)
    if not m:
        return ""
    start=max(0,m.start()-120); end=min(len(raw),m.end()+520)
    return raw[start:end]


def recognize_hadith(text, live=True):
    q=_clean_ar(text)
    if len(q)<8: return None
    best=None
    # Compare both the full review unit and explicit Arabic quotations.  A source
    # sentence often wraps the actual matn with bibliographic prose, which should not
    # dilute a strong exact hadith match.
    candidates=[text]+_quoted_arabic_candidates(text)
    for row in HADITH_SEEDS:
        for candidate in candidates:
            sc=_similarity(candidate,row["text"])
            if sc>=0.78 and (best is None or sc>best["score"]):
                best={**row,"score":sc,"method":"offline_locator_seed","authoritative":False}

    # Do not send arbitrary user text to a Hadith search endpoint. Live discovery is
    # only attempted when the text contains an explicit hadith cue, and only a small
    # cue-centered excerpt is used. Known offline seed matches need no search call.
    excerpt=_hadith_live_excerpt(text)
    if live and excerpt and not (best and best["score"]>=0.90):
        try:
            rows=_hadeeth_search_live(excerpt)
            q_excerpt=_clean_ar(excerpt)
            threshold=0.72
            for item in rows[:64]:
                if not isinstance(item,dict): continue
                candidate=item.get("hadith_text") or item.get("hadeeth") or item.get("title") or ""
                sc=_similarity(q_excerpt,candidate)
                if sc>=threshold and (best is None or sc>best["score"]):
                    best={"id":str(item.get("id","")),"text":candidate,"label":item.get("title") or candidate[:80],"score":sc,"method":"hadeethenc_search","authoritative":True}
        except Exception:
            pass
    return best if best and best["score"]>=0.78 else None


def recognize_source(ar_text, live=True, quran_index=None):
    # Quran first because Quranic text can also appear inside hadith explanations/articles.
    q=recognize_quran(ar_text,live=live,live_index=quran_index)
    if q:
        return {"kind":"quran","confidence":"high" if q["score"]>=0.92 else "medium","match":q}
    h=recognize_hadith(ar_text,live=live)
    if h:
        return {"kind":"hadith","confidence":"high" if h["score"]>=0.9 else "medium","match":h}
    return None
