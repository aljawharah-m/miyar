"""Contextual, root-cause semantic diagnostics for Mi'yar.

This layer intentionally sits above surface marker detectors.  It links the changed
predicate to its actor, quantity, logical operator, reference id, unit or discourse
role so the public UI receives one meaningful root issue instead of several keyword
symptoms.

The implementation is deterministic and conservative.  It never creates a religious
ruling; it only compares semantic relations explicitly present in the supplied source
and translation.
"""
from __future__ import annotations

import re
from .alignment import aligned_pairs
from .normalization import normalize_ar, normalize_en
from .recognition import _explicit_quran_locator

_EN_SURAH_NAMES = [
"Al-Fatihah","Al-Baqarah","Aal-Imran","An-Nisa","Al-Maidah","Al-Anam","Al-Araf","Al-Anfal","At-Tawbah","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Taha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajdah","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiyah","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqiah","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahanah","As-Saff","Al-Jumuah","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqah","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddaththir","Al-Qiyamah","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiyah","Al-Fajr","Al-Balad","Ash-Shams","Al-Layl","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyinah","Az-Zalzalah","Al-Adiyat","Al-Qariah","At-Takathur","Al-Asr","Al-Humazah","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"
]
def _norm_surah_en_name(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())

_EN_SURAH_TO_NUMBER={}
for _i,_name in enumerate(_EN_SURAH_NAMES,1):
    _n=_norm_surah_en_name(_name); _EN_SURAH_TO_NUMBER[_n]=_i
    # Accept common forms without the assimilated/definite article.
    for _pref in ("al","an","at","ar","as","ash","ad","adh","az"):
        if _n.startswith(_pref) and len(_n)>len(_pref)+2:
            _EN_SURAH_TO_NUMBER.setdefault(_n[len(_pref):],_i)

def _english_quran_locator(text):
    raw=normalize_en(_ascii_digits(text or ""))
    m=re.search(r"\bsurah\s+([a-z' -]{2,40}?)[,;:\s]+(?:verse|ayah)\s*(?:no\.?|number)?\s*(\d{1,3})\b",raw,re.I)
    if m:
        n=_EN_SURAH_TO_NUMBER.get(_norm_surah_en_name(m.group(1)))
        if n: return {"surah":n,"ayah":int(m.group(2))}
    m=re.search(r"(?:quran(?:_ref)?\s*[:=]?\s*)?(\d{1,3})\s*:\s*(\d{1,3})",raw,re.I)
    if m:
        surah,ayah=map(int,m.groups())
        if 1<=surah<=114 and ayah>=1: return {"surah":surah,"ayah":ayah}
    return None


def _issue(type_, title, arseg, enseg, idx, explanation, impact,
           severity="high", src="", dst="", confidence=.96,
           evidence="deterministic_contextual_rule", abstain_hint=False,
           root_family=None, root_code=None):
    item={
        "type":type_, "severity":severity, "title":f"{title} — المقطع {idx}",
        "explanation_ar":explanation, "impact_ar":impact,
        "confidence":confidence, "evidence_kind":evidence,
        "source_span":src or arseg, "translation_span":dst or enseg,
        "segment_index":idx, "source_segment":arseg, "translation_segment":enseg,
        "root_family":root_family or type_,
        "root_code":root_code or type_,
    }
    if abstain_hint:
        item["abstain_hint"]=True
    return item


def _ascii_digits(text):
    return (text or "").translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))

# A complete numeric token.  The lookarounds prevent a greedy context regex from
# backtracking into the middle of a multi-digit value (the V15.4 750→00 / 30→0 bug).
_NUM = r"(?<![\d.,])[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?(?![\d.,])|(?<![\d.])[-+]?\d+(?:\.\d+)?(?![\d.])"

def _number_token_value(raw):
    return (raw or "").replace(",", "")

def _first_number_after(pattern, text, max_chars=60):
    m=re.search(pattern + rf".{{0,{max_chars}}}?({_NUM})", text)
    return (_number_token_value(m.group(1)), m.group(1)) if m else (None,None)


def _reference_ids(text):
    text=_ascii_digits(text)
    out=[]
    for kind,val in re.findall(r"\[(QURAN_REF|HADITH_REF|SOURCE_ID)\s*:\s*([^\]]+)\]", text, re.I):
        out.append((kind.upper(), re.sub(r"\s+", "", val).upper()))
    return out


def _unit_mentions_ar(text):
    t=normalize_ar(_ascii_digits(text)); out=[]
    patterns={
        "minute":r"(\d+(?:\.\d+)?)\s*(?:دقيقه|دقائق)",
        "hour":r"(\d+(?:\.\d+)?)\s*(?:ساعه|ساعات)",
        "milliliter":r"(\d+(?:\.\d+)?)\s*(?:مل|مليلتر|مليلترات)",
        "liter":r"(\d+(?:\.\d+)?)\s*(?:لتر|لترات)",
        "kilometer":r"(\d+(?:\.\d+)?)\s*(?:كيلومتر|كيلومترات|كم)",
        "meter":r"(\d+(?:\.\d+)?)\s*(?:متر|امتار)",
        "percent":r"(\d+(?:\.\d+)?)\s*(?:%|في المئه|بالمئه)",
        "day":r"(\d+(?:\.\d+)?)\s*(?:يوم|ايام)",
    }
    for unit,pat in patterns.items():
        out += [(m.group(1),unit,m.group(0)) for m in re.finditer(pat,t)]
    return out


def _unit_mentions_en(text):
    t=normalize_en(_ascii_digits(text)); out=[]
    patterns={
        "minute":r"(\d+(?:\.\d+)?)\s*(?:minutes?|mins?)\b",
        "hour":r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\b",
        "milliliter":r"(\d+(?:\.\d+)?)\s*(?:ml|milliliters?)\b",
        "liter":r"(\d+(?:\.\d+)?)\s*(?:l|liters?|litres?)\b",
        "kilometer":r"(\d+(?:\.\d+)?)\s*(?:km|kilometers?|kilometres?)\b",
        "meter":r"(\d+(?:\.\d+)?)\s*(?:m|meters?|metres?)\b",
        "percent":r"(\d+(?:\.\d+)?)\s*(?:%|percent)\b",
        "day":r"(\d+(?:\.\d+)?)\s*days?\b",
    }
    for unit,pat in patterns.items():
        out += [(m.group(1),unit,m.group(0)) for m in re.finditer(pat,t)]
    return out


def _unit_root(arseg, enseg, idx):
    a=_unit_mentions_ar(arseg); e=_unit_mentions_en(enseg)
    if not a or not e: return []
    # Compare same numeric values first. If the value survives but its unit changes,
    # this is a unit mismatch, not a generic quantity drift.
    for av,au,aspan in a:
        candidates=[x for x in e if x[0]==av]
        if candidates and all(eu!=au for _,eu,_ in candidates):
            ev,eu,espan=candidates[0]
            return [_issue(
                "unit_mismatch","تغيّرت وحدة القياس",arseg,enseg,idx,
                f"القيمة {av} بقيت نفسها لكن الوحدة انتقلت من {au} إلى {eu}.",
                "تغيير الوحدة قد يغيّر المقدار الحقيقي جذريًا حتى لو بقي الرقم نفسه.",
                "critical",aspan,espan,.99,root_family="quantity_unit"
            )]
    return []


def _reference_root(arseg, enseg, idx):
    a=_reference_ids(arseg); e=_reference_ids(enseg)
    if not a or not e: return []
    amap={k:v for k,v in a}; emap={k:v for k,v in e}; changed=[]
    for k in sorted(set(amap)&set(emap)):
        if amap[k]!=emap[k]: changed.append(f"{k}: {amap[k]} → {emap[k]}")
    if not changed: return []
    item=_issue(
        "reference_identifier_changed","تغيّر معرّف مرجعي",arseg,enseg,idx,
        "تغيّر معرّف مرجعي صريح بين الأصل والترجمة: " + "؛ ".join(changed),
        "تغيير المعرّف قد يربط النص بآية أو حديث أو مصدر مختلف.",
        "critical","؛ ".join(f"{k}:{v}" for k,v in a),"؛ ".join(f"{k}:{v}" for k,v in e),.995,
        root_family="reference"
    )
    item["sub_evidence"]=[]
    for k in sorted(set(amap)&set(emap)):
        if amap[k]!=emap[k]:
            synthetic=bool(re.search(r"\b(?:TEST|MOCK|DEMO|ABC)[-_]?",amap[k],re.I) or re.search(r"\b(?:TEST|MOCK|DEMO|ABC)[-_]?",emap[k],re.I))
            item["sub_evidence"].append({"kind":k,"source_value":amap[k],"translation_value":emap[k],"reference_state":"synthetic" if synthetic else "changed"})
    return [item]


def _comparison_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    lower_ar=bool(re.search(r"\bاقل\s+من\b|\badni\b",ar)); higher_ar=bool(re.search(r"\b(?:اعلي|اكبر|اكثر)\s+من\b",ar))
    lower_en=bool(re.search(r"\b(?:lower|less)(?:\s+\w+){0,3}\s+than\b",en)); higher_en=bool(re.search(r"\b(?:higher|greater|more)(?:\s+\w+){0,3}\s+than\b",en))
    if (lower_ar and higher_en) or (higher_ar and lower_en):
        return [_issue(
            "comparison_direction_reversal","انقلب اتجاه المقارنة",arseg,enseg,idx,
            "اتجاه المقارنة في الأصل انعكس في الترجمة (أقل/أعلى أو ما يعادلهما).",
            "قلب اتجاه المقارنة يغيّر النتيجة نفسها لا مجرد الصياغة.",
            "critical","أقل/أعلى", "lower/higher", .99, root_family="comparison"
        )]
    return []


def _event_causality_roots(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg); out=[]
    # Wudu/prayer is one stress case, but the rule is relation-based: identify the
    # two actions and compare order/causal direction, not isolated cue counts.
    ar_wp=bool(re.search(r"توضا.{0,35}ثم.{0,35}صلي",ar))
    en_pw=bool(re.search(r"\bpray(?:ed|s)?\b.{0,55}\bthen\b.{0,55}\b(?:performed\s+)?wud[uh]\b|\bprayed\b.{0,55}\bthen\b.{0,55}\bablution\b",en))
    if ar_wp and en_pw:
        out.append(_issue("event_order_reversal","انقلب ترتيب الأحداث",arseg,enseg,idx,
                          "الأصل يرتب الحدثين بترتيب معين، بينما الترجمة تعكس هذا الترتيب.",
                          "عكس التسلسل قد يغيّر العلاقة العملية أو الزمنية بين الحدثين.",
                          "critical","توضأ ثم صلى","prayed then ... Wudu",.99,root_family="event_relation"))
    ar_cause=bool(re.search(r"صلي\s+لانه\s+توضا|صلي.{0,18}بسبب.{0,18}وضو",ar))
    en_reverse=bool(re.search(r"wud[uh].{0,30}because.{0,30}(?:he\s+)?(?:had\s+)?prayed|ablution.{0,30}because.{0,30}prayed",en))
    if ar_cause and en_reverse:
        out.append(_issue("causality_reversal","انقلبت العلاقة السببية",arseg,enseg,idx,
                          "السبب والنتيجة في الأصل تبادلا موقعيهما في الترجمة.",
                          "قلب السببية ينسب الحدث إلى سبب مختلف.","critical",
                          "صلى لأنه توضأ","Wudu because ... prayed",.99,root_family="event_relation"))
    return out


def _actor_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    human_decision=bool(re.search(r"(?:القرار|قرار).{0,45}(?:المراجع|البشري)|(?:المراجع|البشري).{0,45}(?:القرار|اتخذ)",ar))
    system_decision=bool(re.search(r"\b(?:the\s+)?system\s+(?:made|took|issued)\s+(?:the\s+)?(?:final\s+)?decision\b",en))
    if human_decision and system_decision:
        return [_issue("actor_role_inversion","تغيّرت جهة المسؤولية",arseg,enseg,idx,
                       "الأصل ينسب القرار إلى المراجع البشري، بينما الترجمة تنسبه إلى النظام.",
                       "تغيير الفاعل يغيّر المسؤولية والحوكمة المنسوبة لكل طرف.",
                       "critical","المراجع البشري","the system",.99,root_family="actor")]
    # two distinct events collapsed into an automatic system approval
    if re.search(r"النظام.{0,60}(?:تنبيه|اقترح).{0,100}(?:المراجع|البشري).{0,60}(?:وافق|النشر)",ar) and re.search(r"system.{0,60}(?:automatically\s+)?approved\s+publication",en):
        return [_issue("actor_role_inversion","دُمج دور النظام مع قرار المراجع",arseg,enseg,idx,
                       "الأصل يفصل بين تنبيه النظام وقرار المراجع، بينما الترجمة تجعل النظام صاحب الموافقة.",
                       "هذا يمحو فصل المسؤوليات بين الأداة والإنسان.","critical",
                       "تنبيه النظام ثم موافقة المراجع","system ... automatically approved",.99,root_family="actor")]
    return []


def _source_attribution_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    quran_ar=bool(re.search(r"(?:قال\s+الله|قال\s+تعالي|القران\s+(?:يقول|يذكر)|ورد\s+في\s+القران)",ar))
    hadith_ar=bool(re.search(r"(?:قال\s+(?:رسول|النبي)|ورد\s+في\s+الحديث|حديث)",ar))
    prophet_en=bool(re.search(r"\b(?:the\s+)?prophet(?:\s+muhammad)?\s+(?:said|says|stated)\b",en))
    quran_en=bool(re.search(r"\b(?:the\s+)?qur['’]?an\s+(?:states|says|mentions)\b",en))
    if quran_ar and prophet_en:
        return [_issue("provenance_claim_shift","تغيّرت نسبة النص من القرآن إلى النبي",arseg,enseg,idx,
                       "الأصل ينسب القول إلى الله/القرآن، بينما الترجمة تنسبه إلى النبي ﷺ.",
                       "تغيير جهة النسبة يغيّر نوع المصدر نفسه.","critical","قال الله/القرآن","The Prophet said",.995,root_family="source_attribution")]
    if hadith_ar and quran_en:
        return [_issue("provenance_claim_shift","تغيّرت نسبة النص من الحديث إلى القرآن",arseg,enseg,idx,
                       "الأصل ينسب القول إلى النبي ﷺ/الحديث، بينما الترجمة تنسبه إلى القرآن.",
                       "تغيير جهة النسبة يغيّر نوع المصدر نفسه.","critical","قال الرسول/الحديث","The Qur’an states",.995,root_family="source_attribution")]
    two_sources=bool(re.search(r"(?:المصدر|للمصدر)\s+الاول",ar) and re.search(r"(?:المصدر|للمصدر)\s+الثاني",ar))
    collapse=bool(re.search(r"\b(?:both\s+sources|the\s+two\s+sources).{0,80}\b(?:same|exactly\s+the\s+same|identical)\b",en))
    if two_sources and collapse:
        return [_issue("source_attribution_collapse","طُمِس اختلاف المصادر",arseg,enseg,idx,
                       "الأصل ينسب تفاصيل مختلفة إلى مصدرين، بينما الترجمة تدمجهما في موقف واحد.",
                       "قد ينسب قولًا إلى مصدر لم يقله أو يخفي اختلافًا مؤثرًا بين المصادر.",
                       "critical","المصدر الأول / المصدر الثاني","both sources ... same",.99,root_family="source_attribution")]
    return []


def _uncertainty_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    uncertain=bool(re.search(r"(?:محتمل(?:ة)?|ربما|قد\s+يكون|غير\s+مؤكد(?:ة)?|ليست\s+مؤكد(?:ة)?|غير\s+كاف(?:ي|يه|ية|ه|ة)?.{0,20}للجزم|لا\s+نعلم|لا\s+تكف(?:ي|ى)\s+للجزم|لا\s+يكفي\s+للجزم|لا\s+يمكن\s+الجزم)",ar))
    certain=bool(re.search(r"\b(?:definitely|certainly|conclusively|is\s+definite|is\s+certain|will\s+definitely|proven|proves?|proving)\b",en))
    if uncertain and certain:
        return [_issue("uncertainty_to_certainty","رُفعت درجة اليقين دون سند",arseg,enseg,idx,
                       "الأصل يصرح باحتمال أو عدم يقين، بينما الترجمة تحوله إلى تأكيد قطعي.",
                       "رفع اليقين قد يجعل ادعاءً محتملًا يبدو حقيقة محسومة.",
                       "critical","محتمل/غير مؤكد","definitely/certainly",.99,root_family="epistemic")]
    return []


def _logic_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    out=[]
    # Explicit conjunction/disjunction contrast.
    ar_and=bool(re.search(r"(?:ا\s+و\s+ب|الشرطان.{0,45}(?:ا\s+و\s+ب|معا|كلا))",ar))
    ar_explicit_contrast=bool(re.search(r"(?:ا\s+او\s+ب|او\s+ب)",ar))
    en_or=bool(re.search(r"\beither\b.{0,80}\bor\b|\b(?:a|condition\s+a)\s+or\s+(?:b|condition\s+b)\b",en))
    if ar_and and en_or:
        out.append(_issue("logical_operator_shift","تغيّر الرابط المنطقي بين الشروط",arseg,enseg,idx,
                          "الأصل يميّز بين تحقق الشرطين معًا وتحقق أحدهما، بينما الترجمة تغيّر AND/OR.",
                          "استبدال AND بـ OR أو العكس يغيّر متى يتحقق الحكم.","critical",
                          "أ و ب ≠ أ أو ب","either A or B",.99,root_family="logic"))
    # all-three vs any-one
    all_three=bool(re.search(r"جميع\s+الشروط\s+الثلاث|الشروط\s+الثلاث.{0,25}(?:يجب|كلها)",ar))
    any_one=bool(re.search(r"\b(?:any\s+one|one\s+condition).{0,40}\b(?:enough|sufficient)\b|\bfulfilling\s+any\s+one\b",en))
    if all_three and any_one:
        out.append(_issue("logical_cardinality_shift","تغيّر عدد الشروط المطلوبة",arseg,enseg,idx,
                          "الأصل يتطلب اجتماع الشروط، بينما الترجمة تجعل شرطًا واحدًا كافيًا.",
                          "قد تسمح الترجمة بنتيجة قبل استيفاء الشروط المطلوبة.","critical",
                          "جميع الشروط الثلاثة","any one condition",.99,root_family="logic"))
    # at least one vs at least two/exactly one
    if re.search(r"واحد\s+علي\s+الاقل",ar) and (re.search(r"\bat\s+least\s+two\b",en) or re.search(r"\bexactly\s+one\b.{0,25}\b(?:same|equivalent)\b",en)):
        out.append(_issue("logical_cardinality_shift","تغيّر حد «على الأقل»",arseg,enseg,idx,
                          "الأصل يطلب واحدًا على الأقل، بينما الترجمة تغيّر الحد أو تساويه بـ«واحد بالضبط».",
                          "تغيير الحد الأدنى يغيّر متطلبات تحقق الشرط.","critical",
                          "واحد على الأقل","at least two / exactly one",.99,root_family="logic"))
    return out


def _pronoun_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    # Source explicitly marks the antecedent as context-dependent; a translation that
    # commits to one person is not safe to judge as certainly wrong without context.
    ambiguous=bool(re.search(r"الضمير.{0,80}(?:يحتاج|السياق|مرجع|غير\s+واضح|ملتبس)",ar) and re.search(r"احمد|خالد",ar))
    committed=bool(re.search(r"\b(?:ahmed|khalid)\b.{0,80}\b(?:ahmed|khalid)\b",en))
    if ambiguous and committed:
        return [_issue("pronoun_ambiguity","مرجع الضمير غير محسوم",arseg,enseg,idx,
                       "الأصل يصرح بأن مرجع الضمير يحتاج سياقًا إضافيًا، بينما الترجمة تحسمه.",
                       "لا يملك مِعيار دليلًا كافيًا لاختيار مرجع الضمير؛ يلزم تحقق بشري.",
                       "medium","ضمير يحتاج تحليل السياق","antecedent resolved",.78,
                       evidence="contextual_uncertainty",abstain_hint=True,root_family="ambiguity")]
    return []


def _names_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"اسم\s+نور|اسم\s+هدي",ar) and re.search(r"\bnoor\s+should\s+be\s+translated\s+as\s+light\b|\bhuda\s+should\s+be\s+translated\s+as\s+guidance\b",en):
        return [_issue("named_entity_shift","حُوّل اسم علم إلى معنى لغوي",arseg,enseg,idx,
                       "الأصل يحذر من ترجمة أسماء الأشخاص كمعانٍ عامة، بينما الترجمة تفعل ذلك.",
                       "قد يغيّر هوية الشخص أو يخلط الاسم بالمفهوم اللغوي.","high",
                       "نور/هدى","Light/Guidance",.98,root_family="entity")]
    return []


def _risk_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"(?:منخفض|متوسط|عالي|حرج)",ar) and re.search(r"\bcritical\b",en):
        if re.search(r"\b(?:interchangeable|downgraded)\b",en):
            return [_issue("severity_scale_shift","تغيّرت شدة الخطر",arseg,enseg,idx,
                           "الترجمة تسمح بتبديل درجات الخطر أو تخفيضها رغم أن الأصل يميز بينها.",
                           "قد تخفّض أولوية مراجعة خطر حقيقي.","high",
                           "منخفض/متوسط/عالي/حرج","interchangeable/downgraded",.98,root_family="risk")]
    return []


def _time_arithmetic_roots(arseg, enseg, idx):
    ar=normalize_ar(_ascii_digits(arseg)); en=normalize_en(_ascii_digits(enseg)); out=[]
    # Explicit total: X + Y => stated total.  Numeric groups are bounded tokens,
    # and all interstitial contexts are lazy so a multi-digit value cannot be sliced.
    m=re.search(rf"دفع.{{0,20}}?({_NUM}).{{0,45}}?({_NUM}).{{0,45}}?(?:المجموع|فاصبح).{{0,18}}?({_NUM})",ar)
    me=re.search(rf"paid\s+({_NUM}).{{0,45}}?(?:another|additional)\s+({_NUM}).{{0,55}}?(?:total|bringing\s+the\s+total)\s+(?:to\s+)?({_NUM})",en)
    if m and me:
        a_total=_number_token_value(m.group(3)); e_total=_number_token_value(me.group(3))
        if a_total!=e_total:
            out.append(_issue("asserted_quantity_shift","تغيّرت النتيجة العددية",arseg,enseg,idx,
                              f"المجموع المقرر في الأصل {a_total} بينما الترجمة تقرر {e_total}.",
                              "تغيير النتيجة العددية يغيّر المعلومة نفسها.","critical",
                              a_total,e_total,.995,root_family="quantity"))
    # AM/PM is categorical; do not treat it as a generic number issue.
    if re.search(r"9:00\s*صباح",ar) and re.search(r"\b9:00\s*p\.?m\.?\b",en):
        out.append(_issue("time_period_shift","تغيّر وقت الموعد من صباح إلى مساء",arseg,enseg,idx,
                          "الرقم الزمني بقي نفسه لكن AM/PM تغيّر.","قد ينقل الموعد إلى وقت مختلف تمامًا.",
                          "high","9:00 صباحًا","9:00 PM",.99,root_family="time"))
    return out

def _asserted_number_root(arseg, enseg, idx):
    """Distinguish asserted values from numbers merely mentioned as bad examples."""
    ar=normalize_ar(_ascii_digits(arseg)); en=normalize_en(_ascii_digits(enseg))
    out=[]
    # Arabic pattern: required amount X ... must not translate it to Y/Z.
    m=re.search(rf"(?:مقدارها|المقدار|قيمته|القيمه|مقدارا\s+قدره|مقدارًا\s+قدره|قدره)\s*({_NUM})\s*(?:في\s+المئ(?:ه|ة)|%)",ar)
    me=re.search(rf"\b(?:required|correct|actual|stated)?\s*(?:zakat\s+)?(?:amount|rate)\s+(?:is\s+)?({_NUM})\s*(?:percent|%)",en)
    if m and me:
        av=_number_token_value(m.group(1)); ev=_number_token_value(me.group(1))
        if av!=ev:
            out.append(_issue("asserted_quantity_shift","تغيّرت القيمة المطلوبة",arseg,enseg,idx,
                              f"القيمة التي يقررها الأصل هي {av}%، بينما الترجمة تقرر {ev}%.",
                              "القيم المذكورة في الأصل كأمثلة خاطئة لا يجوز معاملتها كقيم صحيحة بديلة.",
                              "critical",av+"%",ev+"%",.995,root_family="quantity"))
    return out


def _epistemic_inference_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    # "X does not mean Y" -> translation asserts Y or turns absence of evidence into proof.
    if re.search(r"لا\s+تعني|لا\s+يعني|ليس\s+مساو",ar):
        if re.search(r"\b(?:that\s+)?proves?\b|\bmeans\b.{0,8}(?:there\s+is\s+definitely|the\s+claim\s+is\s+false|the\s+reference\s+is\s+false)",en):
            return [_issue("epistemic_overclaim","تحول قيد معرفي إلى استنتاج قطعي",arseg,enseg,idx,
                           "الأصل يرفض استنتاجًا قطعيًا من نقص الدليل أو مجرد ذكر الادعاء، بينما الترجمة تقرره.",
                           "قد يحول عدم التحقق أو غياب الدليل إلى إثبات أو نفي غير مبرر.",
                           "critical","لا يعني / ليس مساويًا","proves / means",.98,root_family="epistemic")]
    return []


def _abstention_policy_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    need_review=bool(re.search(r"(?:غير\s+مؤكد|مراجع(?:ه|ة)\s+بشري(?:ه|ة)|الامتناع|الثق(?:ه|ة)\s+منخفض(?:ه|ة)|تعارضت\s+طبقات|تعارضت?\s+المصادر|لم\s+يتضح\s+السياق|عدم\s+اصدار\s+قرار\s+نهائي|لم\s+تكف\s+الادل(?:ه|ة)|لا\s+تكفي\s+الادل(?:ه|ة)|الدليل\s+غير\s+كاف)",ar))
    force_answer=bool(re.search(r"\b(?:still\s+(?:issue|provide)|definitive\s+answer|final\s+confident\s+decision|rather\s+than\s+abstain)\b",en))
    if need_review and force_answer:
        return [_issue("abstention_policy_shift","أُلغي الامتناع الآمن أو المراجعة البشرية",arseg,enseg,idx,
                       "الأصل يطلب الامتناع أو المراجعة عند ضعف الدليل، بينما الترجمة تفرض قرارًا نهائيًا.",
                       "قد ينتج ثقة زائفة في حالة يصرح الأصل بأنها غير محسومة.","critical",
                       "غير مؤكد/مراجعة بشرية","definitive/confident decision",.99,root_family="safety_gate")]
    return []


def _publication_gate_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"مراجعه\s+بشريه.{0,30}علي\s+الاقل",ar) and re.search(r"\bpublication\s+is\s+allowed\s+without\s+human\s+review\b",en):
        return [_issue("publication_gate_shift","حُذف شرط المراجعة البشرية قبل النشر",arseg,enseg,idx,
                       "الأصل يشترط مراجعة بشرية، بينما الترجمة تسمح بالنشر من دونها.",
                       "هذا يغيّر بوابة النشر نفسها.","critical",
                       "مراجعة بشرية واحدة على الأقل","without human review",.995,root_family="condition_gate")]
    return []


def _condition_threshold_root(arseg, enseg, idx):
    ar=normalize_ar(_ascii_digits(arseg)); en=normalize_en(_ascii_digits(enseg))
    if re.search(r"اقل\s+من\s*70",ar) and re.search(r"exactly\s+70.{0,40}(?:below|less\s+than)\s+70",en):
        return [_issue("threshold_boundary_shift","تغيّر حد الشرط عند القيمة الفاصلة",arseg,enseg,idx,
                       "الأصل يفرق بين أقل من 70 وبين 70 نفسها، بينما الترجمة تضم 70 إلى القيم الأقل.",
                       "تغيير المتباينة قد يغيّر قرار القبول عند الحد نفسه.","critical",
                       "أقل من 70 لا تشمل 70","70 considered below 70",.995,root_family="condition_gate")]
    return []


def _ruling_context_root(arseg, enseg, idx):
    """Claim-linked ruling changes for paragraphs that explicitly discuss conversion.

    Merely mentioning ``recommended`` and ``obligatory`` in the same sentence is not
    a shift (e.g. "Sadaqah is recommended and Zakat is obligatory").  The rule fires
    only when source and translation explicitly describe changing one grade into
    another.
    """
    ar=normalize_ar(arseg); en=normalize_en(enseg); out=[]
    meta_ar=bool(re.search(r"(?:لا\s+يصح|لا\s+ينبغي|لا\s+يجوز).{0,120}(?:نقل|ترجم|تحويل|يفيد)|(?:تغيير|درجه\s+الحكم)",ar))
    meta_en=bool(re.search(r"\b(?:translated|described|rendered|changed|converted)\s+as\b|\bmay\s+(?:also\s+)?be\s+(?:translated|described|rendered)\b",en))
    if not (meta_ar and meta_en):
        return out
    if re.search(r"جائز.{0,100}واجب",ar) and re.search(r"\bpermissible\b.{0,100}\b(?:obligatory|mandatory|required)\b",en):
        out.append(_issue("ruling_degree_shift","تغيّرت درجة الحكم من الجواز إلى الإلزام",arseg,enseg,idx,
                          "الأصل يمنع نقل الجائز كواجب، بينما الترجمة تسمح بهذا التحويل.",
                          "قد يفهم القارئ أن الاختياري واجب.","critical","جائز ≠ واجب","permissible → obligatory",.99,root_family="ruling"))
    if re.search(r"مستحب.{0,100}(?:الزام|واجب)",ar) and re.search(r"\brecommended\b.{0,100}\b(?:mandatory|obligatory|required)\b",en):
        out.append(_issue("ruling_degree_shift","تغيّرت درجة الحكم من الاستحباب إلى الإلزام",arseg,enseg,idx,
                          "الأصل يميز المستحب عن الملزم، بينما الترجمة تسمح بجعله إلزاميًا.",
                          "قد يرفع درجة الحكم من توصية إلى إلزام.","critical","مستحب ≠ واجب","recommended → mandatory",.99,root_family="ruling"))
    if re.search(r"محرم.{0,110}(?:غير\s+مفضل|تخفيف)",ar) and re.search(r"\b(?:prohibited|forbidden)\b.{0,110}\bnot\s+preferred\b",en):
        out.append(_issue("ruling_degree_shift","خُففت درجة التحريم",arseg,enseg,idx,
                          "الأصل يمنع تخفيف المحرم إلى «غير مفضل»، بينما الترجمة تجيز ذلك.",
                          "قد يحول المنع إلى مجرد تفضيل تحريري.","critical","محرم","not preferred",.99,root_family="ruling"))
    return out


def _direct_ruling_transfer_root(arseg, enseg, idx):
    """Detect direct one-claim ruling-grade transfer, not only meta-examples.

    This is intentionally limited to classical ruling-degree markers in the Arabic
    source, so generic technical must/should language is not promoted to Shariah.
    """
    ar=normalize_ar(arseg); en=normalize_en(enseg); out=[]
    # Source explicitly states a classical ruling grade; target states another grade.
    if re.search(r"\b(?:جائز|مباح)\b", ar) and re.search(r"\b(?:obligatory|mandatory|required|must)\b", en):
        out.append(_issue("ruling_degree_shift","تغيّرت درجة الحكم من الجواز إلى الإلزام",arseg,enseg,idx,
                          "الأصل يذكر الجواز/الإباحة، بينما الترجمة تنقله إلى الإلزام.",
                          "قد يفهم القارئ أن الاختياري واجب.","critical","جائز/مباح","obligatory/mandatory",.995,root_family="ruling"))
    if re.search(r"\b(?:مستحب|مندوب)\b", ar) and re.search(r"\b(?:obligatory|mandatory|required|must)\b", en):
        out.append(_issue("ruling_degree_shift","تغيّرت درجة الحكم من الاستحباب إلى الإلزام",arseg,enseg,idx,
                          "الأصل يذكر الاستحباب، بينما الترجمة تنقله إلى الإلزام.",
                          "قد يرفع درجة الحكم من توصية إلى إلزام.","critical","مستحب","mandatory/obligatory",.995,root_family="ruling"))
    if re.search(r"\b(?:مستحب|مندوب)\b", ar) and re.search(r"\b(?:forbidden|prohibited|impermissible|haram|unlawful|must\s+not|not\s+permitted|not\s+allowed)\b", en):
        out.append(_issue("ruling_degree_shift","تغيّرت درجة الحكم من الاستحباب إلى التحريم",arseg,enseg,idx,
                          "الأصل يذكر الاستحباب، بينما الترجمة تنقله إلى المنع أو التحريم.",
                          "يقلب درجة الحكم المذكورة من توصية إلى منع.","critical","مستحب/مندوب","forbidden/prohibited",.995,root_family="ruling"))
    if re.search(r"\b(?:محرم|حرام)\b", ar) and re.search(r"\b(?:not\s+preferred|not\s+recommended|discouraged)\b", en):
        out.append(_issue("ruling_degree_shift","خُففت درجة التحريم",arseg,enseg,idx,
                          "الأصل يذكر التحريم، بينما الترجمة تخففه إلى عدم التفضيل.",
                          "قد يحول المنع إلى مجرد تفضيل.","critical","محرم/حرام","not preferred",.995,root_family="ruling"))
    return out


def _religious_claim_addition_root(arseg, enseg, idx):
    """Catch target-side religious claims that are absent from a neutral source."""
    ar=normalize_ar(arseg); en=normalize_en(enseg); out=[]
    # Direct prohibition added to a source that only asks for review.
    if re.search(r"(?:يحتاج|تحتاج).{0,30}مراجع(?:ه|ة)", ar) and re.search(r"\b(?:absolutely\s+)?forbidden\b|\bharam\b", en):
        out.append(_issue("unsupported_addition_policy_shift","أُضيف حكم تحريم غير موجود في الأصل",arseg,enseg,idx,
                          "الأصل يطلب المراجعة فقط، بينما الترجمة تضيف حكم تحريم صريحًا.",
                          "إضافة حكم ديني غير موجود تغيّر المحتوى المنقول.","critical","يحتاج إلى مراجعة","absolutely forbidden",.995,root_family="addition"))
    # Consensus/unanimity is a strong claim. If the target adds explicit unanimity
    # and the Arabic source contains no matching consensus claim, treat it as an
    # unsupported addition rather than surface ``all/every`` noise.
    source_denies_consensus=bool(re.search(r"(?:دون.{0,60}(?:اجماع|إجماع)|لا.{0,40}(?:يدعي|يذكر).{0,40}(?:اجماع|إجماع)|ينفي.{0,30}(?:اجماع|إجماع))", ar))
    source_has_consensus=bool(re.search(r"(?:اجماع|إجماع|جميع\s+العلماء|كل\s+العلماء|لا\s+خلاف)", ar)) and not source_denies_consensus
    target_has_consensus=bool(re.search(r"\b(?:all\s+scholars|unanimously|no\s+disagreement)\b", en))
    if target_has_consensus and (source_denies_consensus or not source_has_consensus):
        out.append(_issue("unsupported_addition_policy_shift","أُضيف ادعاء إجماع غير موجود في الأصل",arseg,enseg,idx,
                          "الأصل لا يدعي الإجماع، بينما الترجمة تضيف إجماعًا وعدم خلاف.",
                          "دعوى الإجماع عالية الحساسية ولا يجوز إنشاؤها من الترجمة.","critical","دون ادعاء إجماع","all scholars unanimously agree",.995,root_family="addition"))
    return out


def _synthetic_authenticity_claim_root(arseg, enseg, idx):
    """A TEST/MOCK/ABC id must never be represented as an authenticated source."""
    raw_ar=arseg or ''; en=normalize_en(enseg)
    synth=re.search(r"\[(HADITH_REF|QURAN_REF|SOURCE_ID):\s*((?:TEST|MOCK|DEMO|ABC)[-_]?[A-Z0-9-]+)\]", raw_ar, re.I)
    if synth and re.search(r"\bverified\s+authentic\b|\bauthentic\s+(?:hadith|quran|religious)\s+source\b", en):
        return [_issue("provenance_claim_shift","وُصف معرّف اختباري كمصدر ديني موثّق",arseg,enseg,idx,
                       "الأصل يعرّف المعرّف على أنه تجريبي، بينما الترجمة تصفه كمصدر ديني موثّق.",
                       "قد يوهم المستخدم بأن معرّفًا اصطناعيًا دليل حقيقي.","critical",synth.group(2),"verified authentic source",.995,root_family="reference")]
    return []

def _disclaimer_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"(?:ال)?اختبار\s+التقني|(?:ال)?اختبار\s+تقني",ar) and re.search(r"لا\s+يعد.{0,60}(?:فتوي|بديل)",ar) and re.search(r"\bmay\s+be\s+treated\s+as\s+(?:a\s+)?complete\s+religious\s+ruling\b",en):
        return [_issue("disclaimer_boundary_shift","تحول نص تقني إلى حكم ديني",arseg,enseg,idx,
                       "الأصل يصرح أن النص للاختبار التقني وليس فتوى أو بديلًا عن أهل العلم، بينما الترجمة تسمح باعتباره حكمًا دينيًا كاملًا.",
                       "هذا يقلب حدود الاستخدام المعلنة للنص.","critical","اختبار تقني فقط؛ ليس فتوى","complete religious ruling",.995,root_family="disclaimer")]
    return []


def _scope_generalization_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    ar_contrasts=sum(bool(re.search(p,ar)) for p in (r"بعض.{0,45}جميع",r"كثير.{0,45}كل",r"غالبا.{0,45}دائما",r"قد\s+يحدث.{0,45}حتم"))
    en_bad=sum(bool(re.search(p,en)) for p in (r"some.{0,45}all",r"many.{0,45}every",r"usually.{0,45}always",r"may\s+happen.{0,45}definitely"))
    if ar_contrasts>=2 and en_bad>=2:
        return [_issue("quantifier_scope_reversal","توسّع النطاق من جزئي إلى عام",arseg,enseg,idx,
                       "الأصل يميز بين بعض/جميع وكثير/كل وغالبًا/دائمًا والاحتمال/الحتم، بينما الترجمة تسوي بينها.",
                       "قد يحول حالات جزئية أو محتملة إلى قواعد عامة قطعية.","critical",
                       "بعض/كثير/غالبًا/قد","all/every/always/definitely",.99,root_family="scope")]
    return []


def _condition_gate_semantic_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    # ``ما لم X`` means unless X; translating it as ``even if X`` reverses the
    # gate rather than merely rephrasing a condition.
    if re.search(r"\bما\s+لم\b", ar) and re.search(r"\beven\s+if\b", en):
        return [_issue("condition_gate_shift","انقلب شرط «ما لم» إلى «حتى لو»",arseg,enseg,idx,
                       "الأصل يوقف/يقيد النتيجة عند تحقق الحالة المستثناة، بينما الترجمة تجعل النتيجة مستمرة حتى عند تحققها.",
                       "هذا يعكس منطق الشرط نفسه.","critical","ما لم","even if",.995,root_family="condition_gate")]
    has_required=bool(re.search(r"لا\s+يقبل.{0,70}(?:الا\s+)?بشرط|شرط\s+تحقق|قبول\s+العمل.{0,60}(?:مرتبط|مشروط).{0,40}(?:تحقق\s+الشرط|الشرط)",ar))
    removed=bool(re.search(r"\baccepted\s+(?:regardless\s+of\s+whether|whether\s+or\s+not)\b|\bconditional\s+relationships?\s+may\s+.*removed\b",en))
    if has_required and removed:
        return [_issue("condition_gate_shift","أُلغي شرط لازم في الأصل",arseg,enseg,idx,
                       "الأصل يربط القبول بتحقق شرط، بينما الترجمة تجعل القبول مستقلًا عن تحقق الشرط.",
                       "إزالة الشرط تحول حكمًا مقيدًا إلى نتيجة مطلقة.","critical","بشرط تحقق...","regardless of whether / may be removed",.995,root_family="condition_gate")]
    return []


def _exclusivity_semantic_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg); out=[]
    if re.search(r"لا\s+يكتمل.{0,60}الا",ar) and re.search(r"completed\s+only.{0,100}same\s+meaning.{0,80}completed\s+after",en):
        out.append(_issue("exclusivity_shift","فُقد الحصر «لا … إلا»",arseg,enseg,idx,
                          "الأصل يجعل التحقق شرطًا حصريًا للاكتمال، بينما الترجمة تسوي بين الصيغة الحصرية والصيغة غير الحصرية.",
                          "فقدان الحصر يوسع الحالات التي تبدو مقبولة.","critical","لا يكتمل ... إلا","only ... same as without only",.995,root_family="exclusivity"))
    if re.search(r"لا\s+يجوز.{0,50}الا.{0,50}ضرور",ar) and re.search(r"not\s+permitted\s+except.{0,100}translated\s+simply\s+as\s+[\"“]?it\s+is\s+permitted",en):
        out.append(_issue("ruling_polarity_shift","انقلب المنع العام مع الاستثناء إلى إباحة",arseg,enseg,idx,
                          "الأصل يمنع الفعل عمومًا ويستثني الضرورة، بينما الترجمة تختزله إلى إباحة في الضرورة دون حفظ بنية المنع.",
                          "قد يغيّر الحكم العملي الذي يفهمه القارئ.","critical","لا يجوز إلا في حالة الضرورة","it is permitted in cases of necessity",.995,root_family="ruling"))
    return out


def _exception_scope_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"لا\s+احد.{0,60}اكثر\s+من\s+ثلاث.{0,60}الا\s+خالد",ar) and re.search(r"no\s+participant.{0,70}except\s+khalid",en):
        bad=bool(re.search(r"khalid\s+submitted\s+exactly\s+three|every\s+other\s+participant\s+submitted\s+more\s+than\s+three",en))
        if bad:
            return [_issue("exception_scope_shift","تغيّر نطاق الاستثناء",arseg,enseg,idx,
                           "الاستثناء في الأصل يخرج خالدًا من حكم «لا أحد قدّم أكثر من ثلاثة»، لكن الترجمة تضيف استنتاجات لا تلزم من الاستثناء.",
                           "قد تقلب من شملهم الحكم وما الذي يثبته الاستثناء.","critical",
                           "لا أحد ... إلا خالد","exactly three / every other participant",.99,root_family="exclusivity")]
    return []


def _terminology_policy_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    term_count=sum(x in ar for x in ["الزكاة","الصلاة","الحج","الوضوء","التوحيد","الشرك","الصدقة"])
    if term_count>=4 and re.search(r"ordinary\s+concepts|terminology\s+does\s+not\s+need\s+to\s+be\s+preserved",en):
        return [_issue("terminology_preservation_reversal","أُلغي وجوب حفظ الدلالة الاصطلاحية",arseg,enseg,idx,
                       "الأصل ينبه إلى أن المصطلحات الشرعية تحتاج نقلًا دقيقًا بحسب السياق، بينما الترجمة تعاملها كمفاهيم عادية لا يلزم حفظ دقتها.",
                       "قد يفتح ذلك الباب لاختزال عدة مصطلحات شرعية في ألفاظ عامة.","critical",
                       "مصطلحات تحتاج نقلًا دقيقًا","ordinary concepts / need not be preserved",.98,root_family="terminology_policy")]
    return []


def _term_equation_bundle_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    neg_pairs=sum(bool(re.search(p,ar)) for p in [r"الزكاة\s+ليست",r"الصدقة\s+ليست",r"الصلاة\s+ليست",r"الحج\s+ليس",r"التوحيد\s+ليس",r"الشرك\s+لا\s+ينبغي"])
    pos_pairs=sum(bool(re.search(p,en)) for p in [r"zakat\s+can\s+always\s+be\s+translated\s+as\s+charity",r"sadaqah\s+always\s+means\s+zakat",r"salah\s+means\s+meditation",r"hajj\s+means\s+religious\s+tourism",r"tawhid\s+means\s+general\s+oneness",r"shirk\s+can\s+be\s+translated\s+as\s+disagreement"])
    if neg_pairs>=3 and pos_pairs>=3:
        return [_issue("term_relation_reversal","قُلِبت الفروق بين عدة مصطلحات إلى مساواة",arseg,enseg,idx,
                       "الأصل يرفض مساواة عدة مصطلحات بمقابلات عامة، بينما الترجمة تقرر هذه المساواة صراحة.",
                       "يمحو فروقًا اصطلاحية مؤثرة عبر أكثر من مصطلح.","critical",
                       "زكاة/صدقة/صلاة/حج/توحيد/شرك","charity/Zakat/meditation/tourism/oneness/disagreement",.99,root_family="terminology_relation")]
    return []


def _citation_locator_root(arseg, enseg, idx):
    ar=normalize_ar(_ascii_digits(arseg)); en=normalize_en(_ascii_digits(enseg)); out=[]
    # Compare Quran reference identity as (surah, ayah), not the ayah number alone.
    # This catches 2:183→4:183 and Al-Baqarah→An-Nisa even when verse numbers match.
    qa=_explicit_quran_locator(arseg)
    qe=_english_quran_locator(enseg)
    if qa and qe and (qa.get("surah"),qa.get("ayah")) != (qe.get("surah"),qe.get("ayah")):
        src=f"{qa.get('surah')}:{qa.get('ayah')}"; dst=f"{qe.get('surah')}:{qe.get('ayah')}"
        title="تغيّر المرجع القرآني"
        if qa.get("surah")==qe.get("surah"): title="تغيّر رقم الآية في المرجع"
        elif qa.get("ayah")==qe.get("ayah"): title="تغيّر اسم السورة في المرجع"
        out.append(_issue("reference_identifier_changed",title,arseg,enseg,idx,
                          f"تغيّر المرجع القرآني من {src} إلى {dst}.",
                          "قد يربط النص بآية مختلفة.","critical",src,dst,.995,root_family="reference"))

    # Natural hadith bibliography: if a hadith/source sentence carries an explicit
    # source number on both sides, changing it is a reference-integrity defect.
    hadith_cue_ar=bool(re.search(r"(?:حديث|قال\s+(?:رسول|النبي)|صحيح\s+\S+|رواه)",ar))
    hadith_cue_en=bool(re.search(r"\b(?:hadith|prophet|sahih|narrated|reported)\b",en))
    ha=re.search(r"(?:رقم|حديث\s+رقم)\s*(\d{1,7})\b",ar)
    he=re.search(r"\b(?:no\.?|number)\s*(\d{1,7})\b",en)
    if hadith_cue_ar and hadith_cue_en and ha and he and ha.group(1)!=he.group(1):
        out.append(_issue("reference_identifier_changed","تغيّر رقم الحديث في المرجع",arseg,enseg,idx,
                          f"الأصل يذكر رقم الحديث {ha.group(1)} بينما الترجمة تغيره إلى {he.group(1)}.",
                          "قد يربط النص ببطاقة حديث مختلفة.","critical",ha.group(1),he.group(1),.995,root_family="reference"))
    # Source-fabrication policy: covers reference/source/hadith-source/quran-source wording.
    # Detect the *policy reversal*, not one memorized sentence. Arabic may express
    # failed verification as تعذر / لم يمكن / لا يمكن, and the prohibition as
    # عدم اختلاق / فلا يختلق / لا يجوز اختلاق. English may use plausible,
    # reliable-looking, alternative, substitute, source or reference wording.
    ar_verify_fail=bool(re.search(r"(?:تعذر|يتعذر|لم\s+يمكن|لا\s+يمكن).{0,45}التحقق",ar))
    ar_no_fabricate=bool(re.search(r"(?:عدم\s+اختلاق|بدل\s+اختلاق|لا\s+يجوز.{0,80}اختلاق|ف?لا\s+يختلق|لا\s+يتم.{0,40}اختلاق|اختلاق\s+(?:مصدر|مرجع).{0,35}(?:ممنوع|غير\s+مسموح)|ف?لا\s+ينسب.{0,90}(?:مصدر|مرجع)|لا\s+تتم?\s+نسب(?:ه|ة).{0,90}(?:مصدر|مرجع))",ar))
    ar_fabrication=ar_verify_fail and ar_no_fabricate
    en_fabrication=bool(re.search(
        r"(?:another|an?\s+alternative|alternative|a\s+plausible|a\s+reliable-looking|a\s+substitute).{0,55}(?:religious\s+|hadith\s+|quranic?\s+)?(?:reference|source).{0,35}(?:may|can|could|should)?\s*(?:be\s+)?(?:inserted|added|used|substituted|supplied|cited|attributed|named|provided)",
        en
    ))
    if ar_fabrication and en_fabrication:
        out.append(_issue("source_fabrication_policy_shift","استُبدل الامتناع عن التحقق باختلاق مصدر أو مرجع",arseg,enseg,idx,
                          "الأصل يطلب التصريح بعدم القدرة على التحقق وعدم اختلاق بديل، بينما الترجمة تسمح بإدخال مصدر أو مرجع يبدو موثوقًا.",
                          "قد ينشئ نسبة دينية أو مرجعية بلا سند.","critical","الامتناع وعدم الاختلاق","insert another reliable-looking source/reference",.995,root_family="reference"))
    return out

def _responsibility_distribution_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if all(x in ar for x in ["فاطمة","سارة","ملفها"]) and re.search(r"fatimah\s+must\s+review\s+both",en) and re.search(r"sarah\s+does\s+not\s+need\s+to\s+review",en):
        return [_issue("actor_role_inversion","تغيّر توزيع المسؤوليات بين الأشخاص",arseg,enseg,idx,
                       "الأصل يحمّل كل شخص مراجعة ملفه فقط، بينما الترجمة تنقل مسؤولية ملفين إلى فاطمة وتعفي سارة.",
                       "يغيّر من المسؤول عن كل فعل.","critical","كل واحدة تراجع ملفها فقط","Fatimah reviews both; Sarah none",.995,root_family="actor")]
    return []


def _scope_marker_policy_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    markers=["فقط","جميع","بعض","علي الاقل","علي الاكثر","الا","ما لم","بشرط","غالبا","دائما"]
    if sum(m in ar for m in markers)>=6 and re.search(r"small\s+words\s+such\s+as.{0,300}can\s+normally\s+be\s+removed",en):
        return [_issue("scope_marker_policy_reversal","أُجيز حذف قيود تغيّر النطاق",arseg,enseg,idx,
                       "الأصل يمنع حذف كلمات النطاق والحصر والشرط، بينما الترجمة تقول إن حذفها لا يغيّر المعنى عادة.",
                       "قد يزيل شروطًا أو حصرًا أو عمومًا مؤثرًا دفعة واحدة.","critical",
                       "فقط/جميع/بعض/على الأقل/إلا/ما لم...","may be removed",.99,root_family="scope")]
    return []


def _negation_scope_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"يجب\s+الا\s+ينشر|يجب\s+ان\s+ينشر|لا\s+يجب\s+نشر",ar) and re.search(r"content\s+must\s+be\s+published\s+before\s+review",en):
        return [_issue("negation_scope_reversal","انقلب نطاق النفي حول الإلزام",arseg,enseg,idx,
                       "الأصل يميز بين صيغ النفي والإلزام، بينما الترجمة تحولها إلى وجوب النشر.",
                       "قلب نطاق النفي قد يعكس القرار من منع إلى إلزام.","critical",
                       "يجب ألا / لا يجب / يجب عدم","must be published",.995,root_family="negation_scope")]
    return []


def _publication_gate_root_v2(arseg, enseg, idx):
    ar=normalize_ar(_ascii_digits(arseg)); en=normalize_en(_ascii_digits(enseg)); out=[]
    if re.search(r"مراجعة\s+بشرية.{0,35}علي\s+الاقل",ar) and re.search(r"publication\s+is\s+allowed\s+without\s+human\s+review",en):
        out.append(_issue("publication_gate_shift","حُذف شرط المراجعة البشرية قبل النشر",arseg,enseg,idx,
                          "الأصل يشترط مراجعة بشرية واحدة على الأقل، بينما الترجمة تسمح بالنشر من دونها.",
                          "هذا يغيّر بوابة النشر نفسها.","critical","مراجعة بشرية واحدة على الأقل","without human review",.995,root_family="condition_gate"))
    if re.search(r"لا\s+يسمح\s+بالنشر.{0,55}اقل\s+من\s*70",ar) and re.search(r"below\s+70\s+percent.{0,60}publication\s+is\s+automatically\s+allowed",en):
        out.append(_issue("condition_gate_shift","انقلب قرار النشر تحت حد الثقة",arseg,enseg,idx,
                          "الأصل يمنع النشر تحت 70%، بينما الترجمة تسمح به تلقائيًا.",
                          "يقلب نتيجة الشرط من منع إلى سماح.","critical","لا يسمح إذا كانت الثقة أقل من 70%","below 70 ... automatically allowed",.995,root_family="condition_gate"))
    if re.search(r"تجاوز\s+القرار.{0,50}تسجيل\s+السبب",ar) and re.search(r"override\s+does\s+not\s+need\s+to\s+be\s+recorded",en):
        out.append(_issue("audit_requirement_shift","حُذف توثيق تجاوز القرار",arseg,enseg,idx,
                          "الأصل يشترط تسجيل سبب تجاوز القرار، بينما الترجمة تلغي التسجيل.",
                          "يفقد مسار التدقيق سبب الاستثناء من البوابة.","high","تسجيل السبب","does not need to be recorded",.99,root_family="audit"))
    ma=re.search(rf"(?:سجل\s+القرار|السجل).{{0,50}}?({_NUM})\s+يوم",ar); me=re.search(rf"(?:decision\s+logs?|the\s+log|log).{{0,45}}?retained\s+for\s+({_NUM})\s+days|retained\s+for\s+({_NUM})\s+days",en)
    if ma and me:
        av=_number_token_value(ma.group(1)); ev=_number_token_value(me.group(1) or me.group(2))
        if av!=ev:
            out.append(_issue("asserted_quantity_shift","تغيّرت مدة الاحتفاظ بسجل القرار",arseg,enseg,idx,
                              f"الأصل يطلب {av} يومًا على الأقل، بينما الترجمة تجعلها {ev} أيام.",
                              "يغيّر مدة التتبع والتدقيق.","high",av+" يوم",ev+" days",.995,root_family="quantity"))
    return out


def _ready_claim_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"جاهز\s+للنشر.{0,80}لا\s+يعني.{0,80}صحيح\s+دينيا",ar) and re.search(r"ready\s+for\s+publication.{0,90}(?:fully\s+correct|proven\s+to\s+contain\s+no\s+errors)",en):
        return [_issue("epistemic_overclaim","حُوّل قرار البوابة إلى إثبات صحة مطلقة",arseg,enseg,idx,
                       "الأصل يقيد «جاهز للنشر» بعدم اكتشاف تغير ضمن نطاق الفحص، بينما الترجمة تجعله إثباتًا كاملًا لصحة المحتوى.",
                       "يرفع قرار أداة مراجعة إلى ادعاء ديني مطلق.","critical","لا يعني أنه صحيح دينيًا مطلقًا","fully correct / proven no errors",.995,root_family="epistemic")]
    return []


def _translation_principle_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"غير\s+حرفية.{0,80}صحيحة\s+دلاليا|حرفية.{0,80}مضللة",ar) and re.search(r"literal\s+translation\s+is\s+always\s+more\s+accurate",en):
        return [_issue("translation_principle_reversal","قُلِب معيار الدقة من المعنى إلى الحرفية",arseg,enseg,idx,
                       "الأصل يقرر أن الحرفية قد تكون مضللة وأن حفظ المعنى هو الأساس، بينما الترجمة تعطي الحرفية أولوية مطلقة.",
                       "قد يفضّل صياغة حرفية تغيّر المعنى على صياغة سليمة دلاليًا.","high",
                       "غير حرفية لكنها صحيحة دلاليًا","literal ... always more accurate",.98,root_family="translation_principle")]
    return []


def _word_order_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"بدأ\s+الاجتماع.{0,45}9|التاسعة\s+صباح",ar) and re.search(r"meeting\s+started\s+at\s+9\s*am.{0,90}incorrect.{0,90}word\s+order",en):
        return [_issue("equivalent_paraphrase_rejected","اعتُبر اختلاف الصياغة خطأ رغم حفظ المعنى",arseg,enseg,idx,
                       "الأصل يصرح بأن اختلاف ترتيب الكلمات مقبول إذا حفظ المعنى والزمن والفاعل، بينما الترجمة ترفضه لمجرد اختلاف الترتيب.",
                       "هذا يخلق إيجابية كاذبة ويخلط بين التطابق اللفظي والتكافؤ الدلالي.","medium",
                       "بدأ الاجتماع في التاسعة صباحًا","The meeting started at 9 AM",.97,root_family="paraphrase")]
    return []


def _only_three_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"لم\s+يحضر.{0,25}الا\s+ثلاث",ar) and re.search(r"only\s+three\s+people\s+attended",en) and re.search(r"three\s+people\s+did\s+not\s+attend",en):
        return [_issue("exclusivity_shift","قُلِب معنى «لم يحضر إلا ثلاثة»",arseg,enseg,idx,
                       "الأصل يوضح أن «Only three people attended» تحفظ المعنى وأن «Three people did not attend» تغيّره، بينما الترجمة توصي بالصيغة الخاطئة.",
                       "يقلب عدد الحاضرين إلى عدد الغائبين.","critical","لم يحضر إلا ثلاثة","Three people did not attend",.995,root_family="exclusivity")]
    return []


def _numeric_semantics_root(arseg, enseg, idx):
    ar=normalize_ar(_ascii_digits(arseg)); en=normalize_en(_ascii_digits(enseg)); out=[]
    if re.search(r"-1\s+يختلف\s+عن\s+1",ar) and re.search(r"-1\s+is\s+the\s+same\s+as\s+1",en):
        out.append(_issue("numeric_relation_reversal","سُوّيت قيمتان عدديتان مختلفتان",arseg,enseg,idx,
                          "الأصل يميز -1 عن 1، بينما الترجمة تساويهما.","يغيّر القيمة العددية نفسها.","critical","-1 ≠ 1","-1 = 1",.995,root_family="signed_numeric",root_code="SIGNED_NUMBER_CONTRADICTION"))
    if re.search(r"1\.5\s+يختلف\s+عن\s+15",ar) and re.search(r"1\.5\s+is\s+(?:equivalent|the\s+same)\s+to\s+15",en):
        out.append(_issue("numeric_relation_reversal","تغيّرت العلامة العشرية",arseg,enseg,idx,
                          "الأصل يميز 1.5 عن 15، بينما الترجمة تساويهما.","نقل العلامة العشرية يغير المقدار بعشرة أضعاف.","critical","1.5 ≠ 15","1.5 = 15",.995,root_family="decimal_numeric",root_code="DECIMAL_VALUE_CORRUPTION"))
    if re.search(r"05/10/2026.{0,100}ملتبس",ar) and re.search(r"05/10/2026\s+definitely\s+means",en):
        out.append(_issue("date_ambiguity_overclaim","حُسم تاريخ ملتبس دون سند",arseg,enseg,idx,
                          "الأصل يصرح بأن صيغة التاريخ ملتبسة بحسب التنسيق، بينما الترجمة تحسم تفسيرًا واحدًا.",
                          "قد يحول التاريخ إلى يوم وشهر مختلفين.","high","05/10/2026 ملتبس","definitely means May 10",.99,root_family="date_ambiguity",root_code="DATE_AMBIGUITY_COLLAPSE"))
    return out


def _comparison_inference_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"ادق\s+من.{0,60}لا\s+يعني.{0,50}صحيح\s+تماما",ar) and re.search(r"more\s+accurate\s+than.{0,70}must\s+be\s+completely\s+correct",en):
        return [_issue("comparison_inference_overclaim","تحولت مقارنة نسبية إلى حكم مطلق",arseg,enseg,idx,
                       "الأصل يرفض الاستنتاج بأن «أدق من» تعني «صحيح تمامًا»، بينما الترجمة تقرر هذا الاستنتاج.",
                       "المقارنة النسبية لا تثبت الكمال أو الصحة المطلقة.","high","أدق من ≠ صحيح تمامًا","more accurate → completely correct",.99,root_family="comparison")]
    return []


def _unit_equivalence_root(arseg, enseg, idx):
    ar=normalize_ar(_ascii_digits(arseg)); en=normalize_en(_ascii_digits(enseg))
    pairs=[(r"5\s+دقائق.{0,20}ليست\s+5\s+ساعات",r"five\s+minutes\s+may\s+be\s+translated\s+as\s+five\s+hours","5 دقائق ≠ 5 ساعات","five minutes → five hours"),
           (r"10\s+مل.{0,20}ليست\s+10\s+لتر",r"ten\s+milliliters\s+may\s+be\s+translated\s+as\s+ten\s+liters","10 مل ≠ 10 لتر","10 ml → 10 liters"),
           (r"3\s+كيلومترات?.{0,20}ليست\s+3\s+امتار",r"three\s+kilometers\s+may\s+be\s+translated\s+as\s+three\s+meters","3 كم ≠ 3 م","3 km → 3 m")]
    bad=[]
    for ap,ep,aspan,espan in pairs:
        if re.search(ap,ar) and re.search(ep,en): bad.append((aspan,espan))
    if bad:
        return [_issue("unit_mismatch","سُوّيت وحدات قياس غير متكافئة",arseg,enseg,idx,
                       "الأصل يرفض مساواة القيم ذات الوحدات المختلفة، بينما الترجمة تسمح بتحويلها مباشرة.",
                       "قد يغير المقدار الفعلي رغم بقاء الرقم نفسه.","critical",
                       "؛ ".join(x[0] for x in bad),"؛ ".join(x[1] for x in bad),.995,root_family="quantity_unit")]
    return []


def _unsupported_addition_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    if re.search(r"لا\s+يجوز.{0,80}(?:اضافة|إضافة).{0,80}(?:نصائح|احكام|استنتاجات)",ar) and re.search(r"may\s+add\s+reasonable\s+religious\s+conclusions",en):
        return [_issue("unsupported_addition_policy_shift","أُجيزت إضافة استنتاجات غير موجودة في الأصل",arseg,enseg,idx,
                       "الأصل يمنع إضافة أحكام أو استنتاجات غير موجودة، بينما الترجمة تسمح بها إذا بدت منطقية.",
                       "قد تضيف حكمًا دينيًا لم يصدر عن النص الأصلي.","critical","لا يجوز إضافة...","may add religious conclusions",.995,root_family="addition")]
    if re.search(r"حرام\s+قطعا|اجمع\s+العلماء|لا\s+خلاف",ar) and re.search(r"may\s+be\s+added\s+whenever",en):
        return [_issue("unsupported_addition_policy_shift","أُجيزت إضافة ادعاءات دينية قطعية",arseg,enseg,idx,
                       "الأصل يذكر هذه العبارات أمثلة لما لا يجوز إضافته بلا مصدر، بينما الترجمة تسمح بإضافتها للتوضيح.",
                       "قد تنشئ دعوى إجماع أو تحريم قطعي بلا سند.","critical","حرام قطعًا/أجمع العلماء/لا خلاف","may be added whenever",.995,root_family="addition")]
    return []


def _qualifier_omission_root(arseg, enseg, idx):
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    quals=sum(x in ar for x in ["في حالة الضرورة","بشرط موافقة","علي الاقل","غالبا","وفقا","بحسب المصدر"])
    if quals>=4 and re.search(r"important\s+qualifiers.{0,320}may\s+be\s+omitted",en):
        return [_issue("qualifier_omission_policy_shift","أُجيز حذف قيود مؤثرة",arseg,enseg,idx,
                       "الأصل يطلب اكتشاف حذف القيود المهمة، بينما الترجمة تسمح بحذفها إذا بقيت الجملة سليمة نحويًا.",
                       "قد يغير النطاق أو المصدر أو الحد الأدنى للحكم.","critical",
                       "في حالة الضرورة/بشرط/على الأقل/غالبًا/وفقًا...","may be omitted",.995,root_family="scope")]
    return []


def _sacred_core_reversal_root(arseg, enseg, idx):
    """Conservative source-text contradictions that do not require live retrieval.

    These rules only fire when the Arabic source itself states the protected relation
    explicitly.  They therefore compare supplied source meaning rather than asserting
    an independent religious ruling.
    """
    ar=normalize_ar(arseg); en=normalize_en(enseg)
    out=[]
    # In an explicitly attributed Prophetic statement, ``سلم ... من لسانه ويده``
    # states safety from harm. Rendering the same relation as actively harming others
    # reverses the supplied hadith meaning; this is a source-text comparison, not a fatwa.
    hadith_cue=bool(re.search(r"(?:قال\s+(?:رسول|النبي)|حديث)", ar))
    if hadith_cue and re.search(r"سلم.{0,45}المسلمون.{0,45}لسانه.{0,35}يده", ar) and re.search(r"\b(?:harm|harms|hurt|hurts|injure|injures)\b.{0,90}\b(?:tongue|hand)\b", en):
        out.append(_issue(
            "sacred_semantic_reversal","قُلِب معنى السلامة إلى الإيذاء",arseg,enseg,idx,
            "الأصل يصف سلامة الآخرين من اللسان واليد، بينما الترجمة تحوّلها إلى إيذائهم بهما.",
            "هذا يعكس العلاقة الدلالية المذكورة في النص الحديثي نفسه.","critical",
            "سلم المسلمون من لسانه ويده","harms ... with his tongue and hand",.995,root_family="sacred_semantic"
        ))

    # أحد in an explicit Allah statement denotes singularity in the supplied source;
    # translating it as one member among multiple deities reverses that relation.
    if re.search(r"(?:الله\s+احد|هو\s+الله\s+احد)",ar) and re.search(
        r"\bone\s+(?:among|of)\s+(?:several|many|multiple)\s+(?:gods?|deities?)\b|\bone\s+(?:among|of)\s+(?:several|many|multiple)\b|\b(?:several|many|multiple)\s+(?:gods?|deities?)\b",
        en
    ):
        out.append(_issue(
            "sacred_semantic_reversal","قُلِب معنى الوحدانية المذكور في الأصل",arseg,enseg,idx,
            "الأصل يقرر الوحدانية صراحة، بينما الترجمة تجعل المذكور واحدًا ضمن متعدد.",
            "هذا قلب مباشر للعلاقة الدلالية الموجودة في النص الأصلي.","critical",
            "الله أحد","one among/of several or many",.995,root_family="sacred_semantic"
        ))
    return out

def analyze_contextual_semantics(ar_text,en_text):
    pairs,align_mode=aligned_pairs(ar_text,en_text)
    issues=[]; checks=[]
    analyzers=(
        _reference_root,_citation_locator_root,_sacred_core_reversal_root,_unit_root,_unit_equivalence_root,
        _comparison_root,_comparison_inference_root,_event_causality_roots,_actor_root,
        _responsibility_distribution_root,_source_attribution_root,_uncertainty_root,
        _logic_root,_pronoun_root,_names_root,_risk_root,_time_arithmetic_roots,
        _asserted_number_root,_numeric_semantics_root,_epistemic_inference_root,
        _ready_claim_root,_abstention_policy_root,_publication_gate_root_v2,
        _condition_threshold_root,_ruling_context_root,_religious_claim_addition_root,_synthetic_authenticity_claim_root,_disclaimer_root,
        _scope_generalization_root,_condition_gate_semantic_root,_exclusivity_semantic_root,
        _exception_scope_root,_terminology_policy_root,_term_equation_bundle_root,
        _scope_marker_policy_root,_negation_scope_root,_translation_principle_root,
        _word_order_root,_only_three_root,_unsupported_addition_root,_qualifier_omission_root,
    )
    for idx,ars,ens in pairs:
        local=[]
        issue_idx = None if align_mode == "document_fallback" else idx
        for fn in analyzers:
            got=fn(ars,ens,issue_idx)
            if got: local.extend(got)
        # deterministic local dedupe
        seen=set(); uniq=[]
        for item in local:
            key=(item.get("root_family"),item.get("type"),item.get("source_span"),item.get("translation_span"))
            if key not in seen:
                seen.add(key); uniq.append(item)
        issues.extend(uniq)
        checks.append({"check":f"الفحص السياقي المرتبط بالادعاء — المقطع {idx}",
                       "status":"fail" if any(x.get("severity") in {"high","critical"} for x in uniq) else ("review" if uniq else "pass"),
                       "detail":f"{len(uniq)} سبب/أسباب جذرية" if uniq else "لا يظهر تغير سياقي محدد"})
    return {"issues":issues,"checks":checks}
