import re, requests
from datetime import datetime, timezone
from functools import lru_cache
from .recognition import recognize_source
from .alignment import split_units

TIMEOUT=5

TRUSTED_SOURCE_MATRIX={
    "quran":[
        {"name":"QuranEnc","role":"ترجمات معاني القرآن الكريم المعتمدة","kind":"official_api"},
        {"name":"Central DB / ICADB","role":"النص القرآني والترجمات بإصدارات قابلة للتتبع","kind":"official_api"},
    ],
    "hadith":[
        {"name":"HadeethEnc","role":"الأحاديث وشروحها وترجماتها ومراجعها","kind":"official_api"},
        {"name":"Central DB / ICADB","role":"بطاقات الحديث والترجمات المرتبطة بمصادرها","kind":"official_api"},
    ],
    "tafsir":[{"name":"الدرر السنية — التفسير","role":"مرجع تفسيري موصى به في الحزمة العلمية","kind":"trusted_reference"}],
    "aqeedah":[
        {"name":"TerminologyEnc","role":"ضبط المصطلحات العقدية ومقابلاتها","kind":"trusted_reference"},
        {"name":"الدرر السنية — العقيدة","role":"مرجع موضوعي للعقيدة","kind":"trusted_reference"},
    ],
    "fiqh":[
        {"name":"الدرر السنية — الموسوعة الفقهية","role":"مرجع فقهي موضوعي","kind":"trusted_reference"},
        {"name":"الموسوعة الفقهية الكويتية","role":"مرجع موسوعي فقهي","kind":"trusted_reference"},
    ],
    "seerah":[{"name":"الدرر السنية — التاريخ والسيرة","role":"مرجع للسيرة والتاريخ","kind":"trusted_reference"}],
    "terminology":[
        {"name":"TerminologyEnc","role":"المصطلحات الشرعية وتعريفاتها ومقابلاتها","kind":"trusted_reference"},
        {"name":"Central DB / ICADB","role":"المحاذاة والترجمات المعتمدة","kind":"official_api"},
    ],
    "general":[
        {"name":"Byenah","role":"مواد تعريفية وتعليمية بالإسلام","kind":"trusted_reference"},
        {"name":"IslamHouse","role":"محتوى إسلامي متعدد اللغات","kind":"trusted_reference"},
        {"name":"IslamEnc","role":"محتوى إسلامي متعدد اللغات","kind":"trusted_reference"},
    ],
}



def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def _version_value(value):
    """Return an explicit source version only when the upstream payload provides one.

    Never infer or fabricate version numbers. Empty values become None.
    """
    if value is None:
        return None
    value=str(value).strip()
    return value or None


@lru_cache(maxsize=32)
def fetch_quranenc_translation_metadata(translation_key):
    """Fetch QuranEnc translation metadata for attribution/version traceability.

    QuranEnc's translations-list endpoint exposes key, version and last_update.
    Failure is non-fatal: evidence remains usable with source_version=None.
    """
    url='https://quranenc.com/api/v1/translations/list/en/?localization=en'
    try:
        r=requests.get(url,timeout=TIMEOUT); r.raise_for_status(); payload=r.json()
        rows=payload.get('result') if isinstance(payload,dict) else payload
        if isinstance(rows,dict): rows=rows.get('translations') or rows.get('data') or []
        if not isinstance(rows,list): rows=[]
        row=next((x for x in rows if isinstance(x,dict) and x.get('key')==translation_key),None)
        if not row:
            # Some deployments ignore the language filter; retry the global list.
            u2='https://quranenc.com/api/v1/translations/list/?localization=en'
            r=requests.get(u2,timeout=TIMEOUT); r.raise_for_status(); payload=r.json()
            rows=payload.get('result') if isinstance(payload,dict) else payload
            if isinstance(rows,dict): rows=rows.get('translations') or rows.get('data') or []
            if not isinstance(rows,list): rows=[]
            row=next((x for x in rows if isinstance(x,dict) and x.get('key')==translation_key),None)
            url=u2
        if row:
            return {
                'translation_key':translation_key,
                'source_version':_version_value(row.get('version')),
                'source_last_update':row.get('last_update'),
                'translation_title':row.get('title'),
                'metadata_url':url,
                'metadata_status':'live_verified',
            }
    except Exception:
        pass
    return {
        'translation_key':translation_key,
        'source_version':None,
        'source_last_update':None,
        'translation_title':None,
        'metadata_url':url,
        'metadata_status':'unavailable',
    }


def _verification_payload(*, reference=False, source_text=False, user_translation=False):
    return {
        'reference_verified':bool(reference),
        'source_text_retrieved':bool(source_text),
        # Important: retrieving an authoritative reference translation does NOT prove
        # the user's translation is correct; Mi'yar still compares them separately.
        'user_translation_verified':bool(user_translation),
    }


def _is_synthetic_identifier(value):
    return bool(re.search(r'(?:TEST|MOCK|DEMO|ABC)', str(value or ''), re.I))

SURAH_NAMES={1:"الفاتحة",2:"البقرة",3:"آل عمران",4:"النساء",5:"المائدة",6:"الأنعام",7:"الأعراف",8:"الأنفال",9:"التوبة",10:"يونس",11:"هود",12:"يوسف",18:"الكهف",19:"مريم",20:"طه",24:"النور",36:"يس",55:"الرحمن",67:"الملك",94:"الشرح",112:"الإخلاص",113:"الفلق",114:"الناس"}


def _norm(s):
    s=re.sub(r"[\u064B-\u0652\u0670]","",s or "")
    return re.sub(r"[إأآٱ]","ا",s).replace("ى","ي").replace("ة","ه")


def detect_domains(text, recognition=None):
    if recognition and recognition.get("kind") in {"quran","hadith"}:
        return [recognition["kind"]]
    t=_norm(text)
    domains=[]
    if any(x in t for x in ["قران","ايه","سوره","قال الله"]): domains.append("quran")
    if any(x in t for x in ["تفسير","معني الايه","سبب النزول"]): domains.append("tafsir")
    if any(x in t for x in ["حديث","قال رسول","قال النبي","رواه"]): domains.append("hadith")
    if any(x in t for x in ["عقيده","ايمان","توحيد","اسماء الله","صفات الله"]): domains.append("aqeedah")
    if any(x in t for x in ["فقه","حكم","يجوز","لا يجوز","يحرم","واجب","مباح","صلاه","زكاه","صدقه","وضوء","تيمم","صيام","صوم","حج","عمره","ربا","نكاح","طلاق","بيع","خمر"]): domains.append("fiqh")
    if any(x in t for x in ["سيره","غزوه","صحابي","هجره","تاريخ"]): domains.append("seerah")
    if any(x in t for x in ["التوحيد","الشريعه","العباده","السنه","الفتوي","الوحي","النبوه","زكاه","صدقه","وضوء","تيمم","صيام","صوم","حج","عمره","ربا","شرك","كفر","تقوي","ذكر","دعاء","جهاد","خمر"]): domains.append("terminology")
    return list(dict.fromkeys(domains)) or ["general"]


def source_route(text, recognition=None):
    domains=detect_domains(text,recognition)
    sources=[]
    for d in domains:
        for s in TRUSTED_SOURCE_MATRIX.get(d,[]):
            item={**s,"domain":d}
            if item not in sources: sources.append(item)
    return {"domains":domains,"sources":sources}


def fetch_quranenc(surah,ayah,translation_key="english_saheeh"):
    url=f"https://quranenc.com/api/v1/translation/aya/{translation_key}/{surah}/{ayah}"
    retrieved_at=_utc_now_iso()
    meta=fetch_quranenc_translation_metadata(translation_key)
    try:
        r=requests.get(url,timeout=TIMEOUT); r.raise_for_status(); d=r.json()
        if isinstance(d,dict) and isinstance(d.get("result"),dict): d=d["result"]
        if not isinstance(d,dict): raise ValueError("unexpected response")
        tr=d.get("translation") or ""
        return {
            "source":"QuranEnc",
            "publisher":"QuranEnc.com",
            "title":f"{SURAH_NAMES.get(surah,'سورة')} {surah}:{ayah}",
            "detail":tr,
            "reference":f"{surah}:{ayah}",
            "url":url,
            "status":"live_verified",
            "evidence_type":"quran_translation",
            "translation_key":translation_key,
            "translation_title":meta.get("translation_title"),
            "source_version":meta.get("source_version"),
            "source_last_update":meta.get("source_last_update"),
            "retrieved_at":retrieved_at,
            "metadata_url":meta.get("metadata_url"),
            "metadata_status":meta.get("metadata_status"),
            "verification":_verification_payload(reference=True,source_text=bool(tr),user_translation=False),
            "reuse_notice":"Reference text retrieved from QuranEnc; do not modify the retrieved quotation when re-publishing it. Attribution/version metadata must be preserved when available.",
        }
    except Exception:
        return {
            "source":"QuranEnc","publisher":"QuranEnc.com",
            "title":f"مرجع قرآني {surah}:{ayah}",
            "detail":"تعذر استرجاع الترجمة المرجعية لحظيًا؛ لم تُنشأ بيانات بديلة.",
            "reference":f"{surah}:{ayah}","url":url,"status":"unavailable",
            "evidence_type":"quran_translation","translation_key":translation_key,
            "translation_title":meta.get("translation_title"),
            "source_version":meta.get("source_version"),
            "source_last_update":meta.get("source_last_update"),
            "retrieved_at":retrieved_at,"metadata_url":meta.get("metadata_url"),
            "metadata_status":meta.get("metadata_status"),
            "verification":_verification_payload(reference=False,source_text=False,user_translation=False),
        }


def fetch_hadeethenc(hid,language):
    url=f"https://hadeethenc.com/api/v1/hadeeths/one/?language={language}&id={hid}"
    retrieved_at=_utc_now_iso()
    try:
        r=requests.get(url,timeout=TIMEOUT); r.raise_for_status(); d=r.json()
        if isinstance(d,dict) and isinstance(d.get("result"),dict): d=d["result"]
        if not isinstance(d,dict): raise ValueError("unexpected response")
        matn=d.get("hadeeth") or d.get("hadith") or d.get("title") or ""
        grade=d.get("grade") or d.get("attribution") or ""
        refs=d.get("reference") or ""
        detail=matn[:1100]
        if grade: detail += f" — {grade}"
        # HadeethEnc requires version attribution when re-publishing, but the one-card
        # API does not consistently expose a version field. Preserve it only if present.
        source_version=_version_value(d.get("version") or d.get("translation_version") or d.get("content_version"))
        browse_url=f"https://hadeethenc.com/{language}/browse/hadith/{hid}"
        return {
            "source":"HadeethEnc","publisher":"HadeethEnc.com",
            "title":f"حديث {hid} — {'العربية' if language=='ar' else 'English'}",
            "detail":detail,"reference":refs[:600] if isinstance(refs,str) else "",
            "url":url,"browse_url":browse_url,"status":"live_verified",
            "evidence_type":"hadith_card","language":language,
            "source_version":source_version,"retrieved_at":retrieved_at,
            "verification":_verification_payload(reference=True,source_text=bool(matn),user_translation=False),
            "reuse_notice":"Reference text retrieved from HadeethEnc; preserve source attribution and upstream version information when the source provides it.",
        }
    except Exception:
        return {
            "source":"HadeethEnc","publisher":"HadeethEnc.com",
            "title":f"حديث {hid}",
            "detail":"تعذر استرجاع بطاقة الحديث لحظيًا؛ لم يعتمد مِعيار على بيانات غير مسترجعة.",
            "reference":"","url":url,"status":"unavailable","evidence_type":"hadith_card",
            "language":language,"source_version":None,"retrieved_at":retrieved_at,
            "verification":_verification_payload(reference=False,source_text=False,user_translation=False),
        }


def retrieve_reference_evidence(ar_text,live=True):
    rec=recognize_source(ar_text,live=live)
    evidence=[]
    if rec and rec["kind"]=="quran":
        m=rec["match"]
        if m.get("ambiguous"):
            candidates=[x for x in m.get("candidates",[]) if x.get("surah") and x.get("ayah")]
            refs=[f"{x.get('surah')}:{x.get('ayah')}" for x in candidates]
            named=[f"{SURAH_NAMES.get(x.get('surah'), f'سورة {x.get("surah")}')} {x.get('surah')}:{x.get('ayah')}" for x in candidates]
            evidence.append({
                "source":"التعرّف على المصدر",
                "title":"تم التعرّف على نص قرآني ورد في أكثر من موضع",
                "detail":f"وردت العبارة في: {'، '.join(named)}. لذلك لم يخمّن مِعيار موضعًا واحدًا.",
                "status":"locator_verified","evidence_type":"source_locator",
                "reference":"، ".join(refs),"verification":_verification_payload(reference=True,source_text=False,user_translation=False),
            })
        else:
            evidence.append({"source":"التعرّف على المصدر","title":f"تم التعرّف على آية {m['surah']}:{m['ayah']}","detail":f"مطابقة النص مع مرجع قرآني بدرجة {round(m['score']*100)}%. التعرّف يحدد المرجع ولا يحل محل المصدر المعتمد.","status":"locator_verified","evidence_type":"source_locator","reference":f"{m['surah']}:{m['ayah']}","verification":_verification_payload(reference=True,source_text=False,user_translation=False)})
            if live: evidence.append(fetch_quranenc(m["surah"],m["ayah"]))
    elif rec and rec["kind"]=="hadith":
        m=rec["match"]
        evidence.append({"source":"التعرّف على المصدر","title":f"تم التعرّف على حديث HadeethEnc #{m['id']}","detail":f"مطابقة المتن بدرجة {round(m['score']*100)}%. التعرّف يحدد البطاقة ولا يحل محل المصدر.","status":"locator_verified","evidence_type":"source_locator","reference":m["id"],"verification":_verification_payload(reference=True,source_text=False,user_translation=False)})
        if live:
            evidence.append(fetch_hadeethenc(m["id"],"ar"))
            evidence.append(fetch_hadeethenc(m["id"],"en"))
    return rec,evidence


def icadb_health():
    url="https://icadb.com/quran/api/quran/translation-keys/"
    try:
        r=requests.get(url,timeout=TIMEOUT)
        return {"ok":r.ok,"code":r.status_code}
    except Exception:
        return {"ok":False,"code":None}


def _split_review_units(text):
    """Use the same review-unit boundaries as the semantic alignment pipeline.

    A separate regex splitter previously detached leading enumerators (``1.``, ``2.``),
    causing source evidence segment indices to drift away from finding/alignment indices.
    Source provenance must share the exact same unit identity as the rest of Mi'yar.
    """
    return split_units(text or "")


def retrieve_reference_evidence_multi(ar_text, live=True):
    """Recognize Quran/Hadith per aligned review unit, not only once per document.

    This is essential for mixed documents containing multiple Quran verses, a hadith,
    and ordinary prose in the same paste. Each recognized segment keeps its own
    segment_index so evidence cannot be attributed to a different sentence.
    """
    units=_split_review_units(ar_text)
    if len(units)<=1:
        unit=units[0] if units else (ar_text or "")
        synthetic_id=bool(re.search(r"\[(?:QURAN_REF|HADITH_REF|SOURCE_ID)\s*:\s*[^\]]*(?:TEST|MOCK|DEMO|ABC)[^\]]*\]",unit,re.I))
        example_frame=bool(re.search(r"(?:بهذه\s+الصيغه|مثال|للاختبار|تجريبي)",unit))
        if synthetic_id and example_frame:
            return [],[]
        rec,evidence=retrieve_reference_evidence(ar_text,live=live)
        recs=[]
        if rec:
            recs=[{"segment_index":1,"text":ar_text,"recognition":rec}]
            for ev in evidence:
                ev.setdefault("segment_index",1)
        return recs,evidence

    recognitions=[]; evidence=[]
    for idx,unit in enumerate(units,1):
        # Explicit synthetic/demo identifiers are structural test data, not religious
        # sources to verify externally.  We still compare their identifiers locally.
        synthetic_id=bool(re.search(r"\[(?:QURAN_REF|HADITH_REF|SOURCE_ID)\s*:\s*[^\]]*(?:TEST|MOCK|DEMO|ABC)[^\]]*\]",unit,re.I))
        example_frame=bool(re.search(r"(?:بهذه\s+الصيغه|مثال|للاختبار|تجريبي)",unit))
        if synthetic_id and example_frame:
            continue
        rec=recognize_source(unit,live=live)
        if not rec:
            continue
        recognitions.append({"segment_index":idx,"text":unit,"recognition":rec})
        if rec["kind"]=="quran":
            m=rec["match"]
            if m.get("ambiguous"):
                candidates=[x for x in m.get("candidates",[]) if x.get("surah") and x.get("ayah")]
                refs=[f"{x.get('surah')}:{x.get('ayah')}" for x in candidates]
                named=[f"{SURAH_NAMES.get(x.get('surah'), f'سورة {x.get("surah")}')} {x.get('surah')}:{x.get('ayah')}" for x in candidates]
                evidence.append({
                    "source":"التعرّف على المصدر","title":f"المقطع {idx}: نص قرآني ورد في أكثر من موضع",
                    "detail":f"وردت العبارة في: {'، '.join(named)}. لذلك لم يخمّن مِعيار موضعًا واحدًا.",
                    "status":"locator_verified","evidence_type":"source_locator","reference":"، ".join(refs),"segment_index":idx,"verification":_verification_payload(reference=True,source_text=False,user_translation=False),
                })
            else:
                evidence.append({
                    "source":"التعرّف على المصدر","title":f"المقطع {idx}: آية {m['surah']}:{m['ayah']}",
                    "detail":f"مطابقة النص مع مرجع قرآني بدرجة {round(m['score']*100)}%. التعرّف يحدد المرجع ولا يحل محل المصدر المعتمد.",
                    "status":"locator_verified","evidence_type":"source_locator","reference":f"{m['surah']}:{m['ayah']}","segment_index":idx,"verification":_verification_payload(reference=True,source_text=False,user_translation=False),
                })
                if live:
                    ev=fetch_quranenc(m["surah"],m["ayah"]); ev["segment_index"]=idx; evidence.append(ev)
        elif rec["kind"]=="hadith":
            m=rec["match"]
            evidence.append({
                "source":"التعرّف على المصدر","title":f"المقطع {idx}: حديث HadeethEnc #{m['id']}",
                "detail":f"مطابقة المتن بدرجة {round(m['score']*100)}%. التعرّف يحدد البطاقة ولا يحل محل المصدر.",
                "status":"locator_verified","evidence_type":"source_locator","reference":m["id"],"segment_index":idx,"verification":_verification_payload(reference=True,source_text=False,user_translation=False),
            })
            if live:
                for lang in ("ar","en"):
                    ev=fetch_hadeethenc(m["id"],lang); ev["segment_index"]=idx; evidence.append(ev)
    return recognitions,evidence


def source_route_multi(text, recognitions=None):
    """Union domain routing for mixed documents instead of letting one source dominate."""
    domains=detect_domains(text,None)
    recognized_kinds=[]
    for item in recognitions or []:
        rec=item.get("recognition") or {}
        kind=rec.get("kind")
        if kind in {"quran","hadith"}:
            recognized_kinds.append(kind)
            if kind not in domains:
                domains.insert(0,kind)
    domains=list(dict.fromkeys(domains))
    # "general" is only a fallback. Once a scriptural/hadith source is actually
    # recognized, it must not remain as a competing domain label.
    if recognized_kinds and "general" in domains:
        domains=[d for d in domains if d!="general"]
    sources=[]
    for d in domains:
        for src in TRUSTED_SOURCE_MATRIX.get(d,[]):
            item={**src,"domain":d}
            if item not in sources:
                sources.append(item)
    return {"domains":domains,"sources":sources}
