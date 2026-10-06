import re
from .normalization import normalize_ar, normalize_ar_preserve_hamza, normalize_en, numbers, AR_NUMBER_WORDS, EN_NUMBER_WORDS
from .alignment import split_units, aligned_pairs

# Structural signals are intentionally conservative. They are not a grammar parser;
# they are high-impact invariants that should survive translation.
AR_SIGNALS = {
    "negation": [r"\b(?:و|ف)?لا\b", r"\bدون\b", r"\bبلا\b", r"\b(?:و|ف)?ليس(?:ت|وا|ن)?\b", r"\b(?:و|ف)?لن\b", r"\b(?:و|ف)?لم\b"],
    "exception": [r"\b(?:و|ف)?سوي\b", r"\b(?:و|ف)?باستثناء\b", r"\b(?:و|ف)?عدا\b"],
    # Conditions are intentionally restricted to semantically strong markers.
    # Bare «إذا/متى/عند» is too ambiguous in explanatory prose (e.g. «إذا قيل...»)
    # and is handled contextually instead of by keyword counting.
    "condition": [
        r"\b(?:و|ف)?بشرط\b", r"\b(?:و|ف)?شرط(?:ا|ًا)?\b",
        r"\b(?:و|ف)?في حال\b", r"\b(?:و|ف)?عند تحقق\b",
        r"\b(?:و|ف)?عند وجود\b", r"\bما لم\b",
    ],
    "obligation": [r"\b(?:و|ف)?يجب\b", r"\b(?:و|ف)?تجب\b", r"\b(?:و|ف)?يلزم\b", r"\b(?:و|ف)?واجب(?:ا|ة)?\b", r"\b(?:و|ف)?فرض(?:ا)?\b", r"\b(?:و|ف)?وجب(?:ت|وا)?\b", r"\b(?:و|ف)?مطلوب(?:ه|ة)?\b"],
    "recommendation": [r"\b(?:و|ف)?مستحب(?:ا|ة)?\b", r"\b(?:و|ف)?يستحب\b", r"\b(?:و|ف)?مندوب(?:ا|ة)?\b", r"\b(?:و|ف)?يسن\b"],
    "disliked": [r"\b(?:و|ف)?مكروه(?:ا|ة)?\b", r"\b(?:و|ف)?يكره\b"],
    "prohibition": [r"\b(?:و|ف)?يحرم\b", r"\b(?:و|ف)?حرام\b", r"\b(?:و|ف)?محرم(?:ا|ة)?\b", r"\b(?:و|ف)?لا يجوز\b", r"\b(?:و|ف)?ممنوع\b", r"\b(?:و|ف)?يمنع\b", r"\b(?:و|ف)?نهى\b", r"\b(?:و|ف)?نهي\b"],
    # Negative look-behind avoids counting «لا يجوز» as permission.
    "permission": [r"(?<!لا )\b(?:و|ف)?يجوز\b", r"\b(?:و|ف)?جائز\b", r"\b(?:و|ف)?جاز\b", r"\b(?:و|ف)?مباح\b", r"\b(?:و|ف)?مسموح\b", r"\b(?:و|ف)?حلال\b"],
}
EN_SIGNALS = {
    "negation": [r"\bnot\b", r"\bcannot\b", r"\bcan't\b", r"\bnothing\b", r"\bnone\b", r"\bno\s+one\b", r"\bnobody\b", r"\bno\b", r"\bnever\b", r"\bwithout\b", r"\bneither\b", r"\bnor\b"],
    # ``is but a messenger`` is a standard English exclusivity construction and
    # can faithfully realize Arabic ``ما ... إلا`` without an explicit ``not``.
    "exception": [r"\bexcept\b", r"\bunless\b", r"\bother than\b", r"\bwith the exception of\b", r"\b(?:is|are|was|were)\s+but\b", r"\bnothing\s+but\b"],
    "condition": [r"\bif\b", r"\bwhen\b", r"\bunless\b", r"\bprovided that\b", r"\bon condition that\b", r"\b(?:a\s+)?condition\s+(?:for|of)\b", r"\bprerequisite\b", r"\bin case\b", r"\bunder a specific condition\b"],
    "obligation": [r"\bmust\b", r"\brequired\b", r"\bobligatory\b", r"\bmandatory\b", r"\bduty\b", r"\bbinding\b", r"\bwajib\b", r"\bfard\b"],
    "recommendation": [r"\brecommended\b", r"\bencouraged\b", r"\bpreferable\b", r"\bmustahabb\b", r"\bmandub\b"],
    "disliked": [r"\bdisliked\b", r"\bdiscouraged\b", r"\bnot\s+preferred\b", r"\bmakruh\b"],
    "prohibition": [r"\bnot\s+permissible\b", r"\bnot\s+permitted\b", r"\bimpermissible\b", r"\bforbidden\b", r"\bprohibited\b", r"\bnot\s+allowed\b", r"\bharam\b", r"\bunlawful\b", r"\bshould\s+not\b", r"\bmust\s+not\b", r"\bmay\s+not\b", r"\bcannot\s+be\s+attributed\b", r"\bcan\s+not\s+be\s+attributed\b"],
    "permission": [r"(?<!not )\bpermissible\b", r"(?<!not )\bpermitted\b", r"(?<!not )\ballowed\b", r"\bmay\b", r"\bhalal\b", r"\blawful\b"],
}
LABEL = {
    "negation": "النفي",
    "exception": "الاستثناء",
    "condition": "الشرط",
    "obligation": "الإلزام",
    "recommendation": "الاستحباب",
    "disliked": "الكراهة",
    "prohibition": "التحريم/المنع",
    "permission": "الإباحة",
}


def _hits(text, patterns):
    """Return every non-duplicate match, not only the first.

    Counting matters for long passages: if Arabic contains two exceptions while the
    English contains one, mere presence on both sides must not be treated as success.
    """
    out = {}
    for key, pats in patterns.items():
        found = []
        spans = set()
        for p in pats:
            for m in re.finditer(p, text, re.I):
                sig = (m.start(), m.end())
                # Skip exact or nested/overlapping matches. Patterns are ordered from
                # more specific to more general (e.g. «عند تحقق» before «عند»).
                if sig in spans or any(not (sig[1] <= a or sig[0] >= b) for a,b in spans):
                    continue
                spans.add(sig)
                found.append((m.start(), m.group(0)))
        if found:
            out[key] = [v for _, v in sorted(found, key=lambda x: x[0])]
    return out


def _span_summary(items, label):
    if not items:
        return "لا يوجد مقابل"
    if len(items) == 1:
        return items[0]
    preview = "، ".join(items[:3])
    suffix = "…" if len(items) > 3 else ""
    return f"{len(items)} مواضع ({preview}{suffix})"


def _rich_structural_span(original_text, key, items):
    """Return a user-readable source span for high-impact structural markers.

    A bare marker such as «إلا» is enough for detection but weak evidence for a reviewer.
    For a single exception/condition we therefore surface the short clause that carries the
    constraint, while keeping the conservative count summary for repeated markers.
    """
    if not items:
        return "لا يوجد مقابل"
    if len(items) != 1:
        return _span_summary(items, LABEL.get(key, key))
    text = original_text or ""
    if key == "exception":
        m = re.search(r"(?:إلا|الا|سوى|سوي|باستثناء|عدا)\s+[^،,.؛!?؟\n]{1,90}", text, re.I)
        if m:
            return m.group(0).strip()
    if key == "condition":
        m = re.search(r"(?:إذا|اذا|متى|متي|إن|ان|وإن|وان|فإن|فان|بشرط|في حال|عند تحقق|عند وجود)\s+[^،,.؛!?؟\n]{1,90}", text, re.I)
        if m:
            return m.group(0).strip()
    return items[0]



def _split_units(text):
    return split_units(text)


def _required_as_condition(ar_unit, en_unit):
    """Treat 'required for/to' as a condition when Arabic explicitly says شرط.

    Example: «الوضوء شرط للصلاة» → 'Wudu is required for prayer' is not an
    obligation shift. This exception is narrow and only activates with explicit شرط.
    """
    ar=normalize_ar(ar_unit)
    en=normalize_en(en_unit)
    return bool(re.search(r"\bشرط(?:ا)?\b", ar) and re.search(r"\brequired\s+(?:for|to)\b", en))


def _raw_ar_condition_hits(ar_unit):
    """Detect Arabic conditions before hamza folding.

    «أن» is never treated as conditional. «إن» is accepted only in a clause-like
    context; plain unhamzaed «ان» is accepted conservatively only at the start of a
    unit with a verbal/negation continuation.
    """
    raw=normalize_ar_preserve_hamza(ar_unit)
    hits=[]
    patterns=[
        r"(?<![\u0600-\u06FF])(?:و|ف)?إن(?=\s+(?:كن|كان|لم|لا|من\b|ت[\u0600-\u06FF]{2,}|ي[\u0600-\u06FF]{2,}|وجد|ثبت|ظهر|حصل|وقع|تعذر|أمكن|امكن))",
        r"^(?:و|ف)?ان(?=\s+(?:كن|كان|لم|لا|من\b|ت[\u0600-\u06FF]{2,}|ي[\u0600-\u06FF]{2,}|وجد|ثبت|ظهر|حصل|وقع|تعذر|امكن))",
    ]
    for pat in patterns:
        for m in re.finditer(pat,raw):
            # «إن» after a reporting/saying verb is normally a complementizer
            # ("it was said that..."), not a condition on the proposition.
            prefix=raw[max(0,m.start()-28):m.start()]
            if m.group(0).lstrip('وف').startswith('إن') and re.search(r"(?:قيل|قال|ذكر|ورد|اكد|أكد|اوضح|أوضح|بين|بيّن)\s*$", prefix):
                continue
            hits.append((m.start(),m.group(0)))
    return [x for _,x in sorted(hits)]


def _raw_ar_exception_hits(ar_unit):
    """Detect true exception «إلا/الا» without confusing المصدرية «ألا» (أن لا)."""
    raw=normalize_ar_preserve_hamza(ar_unit)
    out=[]
    for pat in (r"(?<![\u0600-\u06FF])(?:و|ف)?إلا(?![\u0600-\u06FF])", r"(?<![\u0600-\u06FF])(?:و|ف)?الا(?![\u0600-\u06FF])"):
        for m in re.finditer(pat,raw): out.append((m.start(),m.group(0)))
    return [x for _,x in sorted(out)]


def _mask_discourse_conditions(ar_norm):
    """Remove metalinguistic 'if it is said/mentioned/translated' frames.

    These introduce an example, not a condition on the underlying ruling.  Counting
    them as semantic conditions creates systematic false positives in explanatory text.
    """
    return re.sub(
        r"\bاذا\s+(?:قيل|ورد|ذكر|جاء|ترجم(?:ت|نا)?|كان\s+النص\s+يقول|كان\s+المقصود)\b",
        lambda m: m.group(0).replace('اذا','مثال',1), ar_norm, flags=re.I
    )


def _unit_signal_hits(ar_unit, en_unit):
    ar=normalize_ar(ar_unit); en=normalize_en(en_unit)
    ar_for_hits=_mask_discourse_conditions(ar)
    a=_hits(ar_for_hits,AR_SIGNALS); e=_hits(en,EN_SIGNALS)
    raw_exc=_raw_ar_exception_hits(ar_unit)
    if raw_exc:
        a.setdefault("exception",[]).extend(raw_exc)
    raw_cond=_raw_ar_condition_hits(ar_unit)
    if raw_cond:
        a.setdefault("condition",[]).extend(raw_cond)
    # Bare «إذا» is accepted only after metalinguistic frames (إذا قيل/ورد/ذكر...)
    # have been masked above.  This preserves real conditions such as «إذا تحقق
    # الشرط» and «إذا شق عليه الصوم» without reviving the framing false positives.
    for m in re.finditer(r"\b(?:و|ف)?اذا\b", ar_for_hits, re.I):
        a.setdefault("condition",[]).append(m.group(0))
    # «ما لم» is a single unless-like condition, not an independent negation + condition.
    if re.search(r"\bما لم\b", ar):
        if a.get("negation"):
            a["negation"]=[x for x in a["negation"] if normalize_ar(x)!="لم"]
            if not a["negation"]: a.pop("negation",None)
        # English ``unless`` is the direct conditional realization of «ما لم».
        # Do not also count it as an added exception in this construction.
        if e.get("exception"):
            e["exception"]=[x for x in e["exception"] if x.lower()!="unless"]
            if not e["exception"]: e.pop("exception",None)
    # «إلا عند ...» is one exception phrase, not necessarily a second independent
    # condition. Likewise "except when ..." may be the English realization of the
    # same exception. Avoid double-counting the internal temporal marker.
    if re.search(r"\bالا\s+عند\b", ar) and e.get("exception"):
        if a.get("condition")==["عند"]:
            a.pop("condition",None)
        if e.get("condition")==["when"]:
            e.pop("condition",None)
    # In the accepted explanatory gloss of «العورة», the English modal is part of
    # the term definition ("parts that must be covered"), not a newly introduced
    # ruling. Do not misclassify that lexical gloss as an obligation shift.
    if ar.strip() in {"العورة","عوره","عورة"} and re.search(r"\bparts?(?: of the body)? that must be covered\b", en):
        if e.get("obligation"):
            e["obligation"]=[x for x in e["obligation"] if x.lower()!="must"]
            if not e["obligation"]:
                e.pop("obligation",None)
    # "not preferred" is one disliked marker; its internal "not" is not an
    # independent negation shift.
    if e.get("disliked") and any(x.lower()=="not preferred" for x in e.get("disliked",[])):
        if e.get("negation"):
            e["negation"]=[x for x in e["negation"] if x.lower()!="not"]
            if not e["negation"]:
                e.pop("negation",None)

    # Bibliographic ``no. 1907`` means "number", not logical negation.
    if e.get("negation") and re.search(r"\bno\.\s*\d+", en, re.I):
        e["negation"]=[x for x in e["negation"] if not (x.lower()=="no" and re.search(r"\bno\.\s*\d+", en, re.I))]
        if not e["negation"]:
            e.pop("negation",None)

    # ``nothing but`` is an exclusivity construction; when Arabic carries an
    # equivalent exclusivity marker, its internal ``nothing`` is not an added negation.
    if re.search(r"(?<![\u0600-\u06FF])(?:و|ف)?انما\b|\bلا\b.{0,80}(?:\bإلا\b|\bالا\b)", normalize_ar_preserve_hamza(ar_unit)) and re.search(r"\bnothing\s+but\b", en, re.I):
        if e.get("negation"):
            e["negation"]=[x for x in e["negation"] if x.lower()!="nothing"]
            if not e["negation"]: e.pop("negation",None)

    # Arabic «إنما» is an exclusivity construction. English ``is/are but`` or
    # ``only`` can be its faithful realization, so do not call that an added exception.
    if re.search(r"(?<![\u0600-\u06FF])(?:و|ف)?انما\b", ar) and e.get("exception"):
        e["exception"]=[x for x in e["exception"] if not re.search(r"\b(?:is|are|was|were)\s+but\b", x, re.I)]
        if not e["exception"]:
            e.pop("exception",None)

    # Arabic negative-exception exclusivity «لا ... إلا» is often rendered as
    # English ``no ... but ...`` (e.g. لا إله إلا الله -> no god but Allah).
    # Treat the paired English construction as preserving the exception operator.
    if re.search(r"\bلا\b.{0,120}(?:\bإلا\b|\bالا\b)", normalize_ar_preserve_hamza(ar_unit)) and re.search(r"\bno\b.{0,120}\bbut\b", en, re.I):
        e.setdefault("exception",[]).append("no ... but (exclusivity)")

    # Arabic negative-exception exclusivity can be rendered idiomatically as
    # English ``only when/if/...`` without an explicit surface negation or ``except``.
    # Compare the semantic operator, not the literal words.
    if re.search(r"\bلا\b.{0,120}(?:\bإلا\b|\bالا\b)", normalize_ar_preserve_hamza(ar_unit)) and re.search(r"\bonly\s+(?:if|when|with|after|before|by|upon)\b", en, re.I):
        e.setdefault("negation",[]).append("only (exclusivity)")
        e.setdefault("exception",[]).append("only (exclusivity)")

    # Lexical Arabic negation with ``غير كافٍ/كافية`` may map to English
    # ``not sufficient`` or ``insufficient`` without a literal لا/لم marker.
    if re.search(r"\bغير\s+كاف(?:ي|يه|ية|ه|ة)?\b", ar) and re.search(r"\b(?:not\s+sufficient|insufficient|inadequate|not\s+enough)\b", en, re.I):
        a.setdefault("negation",[]).append("غير كاف")
        if not e.get("negation"): e.setdefault("negation",[]).append("insufficient")

    # ``لم تكف الأدلة`` and similar insufficiency constructions are faithfully
    # translated by lexical negatives such as ``insufficient/inadequate``.
    if re.search(r"\b(?:لم\s+تكف|لا\s+تكفي|لا\s+يكفي)\b", ar) and re.search(r"\b(?:insufficient|inadequate|not\s+enough)\b", en, re.I):
        e.setdefault("negation",[]).append("insufficient")

    if _required_as_condition(ar_unit,en_unit):
        req=[x for x in e.get("obligation",[]) if x.lower()=="required"]
        if req:
            e["obligation"]=[x for x in e.get("obligation",[]) if x.lower()!="required"]
            if not e["obligation"]:
                e.pop("obligation",None)
            e.setdefault("condition",[]).append("required for/to")

    # ``should not be attributed`` can be either a normative prohibition or a
    # plain negative attribution. Treat it as prohibition only when Arabic carries
    # an explicit prohibition marker such as «لا يجوز نسبة ...»; otherwise its
    # negation signal already captures the faithful mapping.
    if e.get("prohibition") and any(x.lower()=="should not" for x in e.get("prohibition",[])) and not a.get("prohibition"):
        e["prohibition"]=[x for x in e["prohibition"] if x.lower()!="should not"]
        if not e["prohibition"]:
            e.pop("prohibition",None)

    # English ``may`` is highly polysemous.  Only treat it as a ruling marker when
    # Arabic itself carries a permission marker or the English syntax is clearly
    # deontic.  Phrases such as ``may have more than one possible meaning`` express
    # possibility, not permissibility, and must not create a religious-ruling alert.
    if e.get("permission"):
        may_hits=[x for x in e.get("permission",[]) if x.lower()=="may"]
        if may_hits and not a.get("permission"):
            possibility=bool(
                re.search(r"(?<![\u0600-\u06FF])(?:ف|و)?لعل", ar, re.I)
                or re.search(r"\bmay\s+(?:have|seem|appear|indicate|suggest|mean|refer|contain|include|vary|differ|depend|represent|reflect)\b", en, re.I)
                or re.search(r"\bmay\s+be\s+(?!done\b|performed\b|used\b|allowed\b|permitted\b|required\b|obligatory\b|recommended\b)", en, re.I)
            )
            if possibility:
                e["permission"]=[x for x in e["permission"] if x.lower()!="may"]
                if not e["permission"]:
                    e.pop("permission",None)
    return a,e


def _numbers_for_unit(ar_unit, en_unit):
    """Return quantities after filtering clearly non-quantitative English idioms.

    ``numbers()`` intentionally recognizes written-out number words.  At sentence
    level we can safely discard a small set of lexical uses when Arabic contains no
    numeric quantity, e.g. ``more than one possible meaning``.  This avoids treating
    an English discourse phrase as an invented religious number while preserving
    genuine comparisons such as «ثلاث» ↔ ``four``.
    """
    # Leading enumerators ("26. ...") are test/document structure, not semantic quantities.
    ar_clean=re.sub(r"^\s*[0-9٠-٩]{1,3}\s*[.)\-:]\s*", "", ar_unit or "")
    en_clean=re.sub(r"^\s*[0-9]{1,3}\s*[.)\-:]\s*", "", en_unit or "")
    an=numbers(ar_clean); enm=numbers(en_clean)
    def _cmp_num(v):
        # Preserve public evidence spelling while comparing 1,250 == 1250.
        return re.sub(r"(?<=\d),(?=\d{3}(?:$|%))", "", str(v))
    an=[_cmp_num(x) for x in an]; enm=[_cmp_num(x) for x in enm]
    en=normalize_en(en_clean)
    ar_norm=normalize_ar(ar_clean)

    # Clock hours are frequently written as Arabic ordinals (التاسعة) but as
    # digits in English (9 AM).  Bind those ordinals to the hour value before
    # generic quantity comparison so an equivalent time is not flagged.
    ordinal_hours={
        "الاولى":"1", "الثانية":"2", "الثالثة":"3", "الرابعة":"4",
        "الخامسة":"5", "السادسة":"6", "السابعة":"7", "الثامنة":"8",
        "التاسعة":"9", "العاشرة":"10", "الحادية عشرة":"11", "الثانية عشرة":"12",
    }
    if not an:
        for word,val in ordinal_hours.items():
            if word in ar_norm and val in enm and re.search(rf"\b{val}\s*(?:a\.?m\.?|p\.?m\.?)\b", en, re.I):
                an.append(val); break

    # A whole/full amount is a quantitative value (= 1) when the Arabic side
    # explicitly contains a fraction.  Keep this sentence-local so ordinary uses
    # of “full” elsewhere do not become invented numbers.
    if any(x in {"1/2","1/3","1/4","2/3"} for x in an):
        if re.search(r"\b(?:the\s+)?(?:full|whole|entire)\s+(?:amount|share|portion|quantity)\b", en, re.I):
            enm.append("1")

    # Qur'anic divine-name rendering «الله أحد» -> “Allah, the One” uses
    # ``One`` as a theological descriptor, not an asserted numeric quantity.
    if "1" in enm and re.search(r"(?:الله\s+احد|هو\s+الله\s+احد)", ar_norm) and re.search(r"\ballah\b.{0,20}\bthe\s+one\b|\bhe\s+is\s+allah\b.{0,20}\bone\b", en, re.I):
        removed=False; kept=[]
        for x in enm:
            if x=="1" and not removed: removed=True; continue
            kept.append(x)
        enm=kept

    if "1" in enm:
        lexical_one_pat=(
            r"\bmore\s+than\s+one(?:\s+(?:possible|potential))?\s+(?:meaning|interpretation|reading|sense|way|possibility|explanation)s?\b|"
            r"\bone\s+of\s+(?:the\s+)?(?:principles|foundations|beliefs|reasons|ways|examples|forms|types|kinds|features|aspects)\b|"
            r"\bone\s+(?:from|for)\s+(?:whom|whose|who|which|that)\b|"
            r"\bone\s+(?:who|whose|whom|that|which)\b|"
            r"\bone[’']s\s+(?:brother|sister|self|heart|deeds?|family|neighbor|neighbour)\b|"
            r"\bone\s+(?:loves?|hates?|does|has|is|was|wants?|intends?|believes?|knows?|says?|thinks?)\b|"
            r"\bone\s+of\s+(?:you|us|them)\b|"
            r"\bone\s+(?:among|of)\s+(?:several|many|multiple)\s+gods?\b"
        )
        lexical_one_count=len(list(re.finditer(lexical_one_pat,en,re.I)))
        if lexical_one_count:
            kept=[]
            for x in enm:
                if x=="1" and lexical_one_count>0:
                    lexical_one_count-=1
                    continue
                kept.append(x)
            enm=kept

    # Arabic «ولو + singular noun» is naturally rendered as "even (if) one ...";
    # the English one is a minimality idiom, not an added numeric claim.
    if "1" in enm and re.search(r"(?<![\u0600-\u06FF])ولو\s+[\u0600-\u06FF]+", ar_norm) and re.search(r"\beven\s+(?:if\s+)?one\b", en, re.I):
        removed=False; kept=[]
        for x in enm:
            if x=="1" and not removed:
                removed=True; continue
            kept.append(x)
        enm=kept

    # Arabic dual morphology can encode the quantity two without an explicit number
    # word: «المسلمان» -> ``two Muslims``.  When English has exactly one lexical
    # ``two`` and Arabic contains a clear definite dual noun, treat that 2 as preserved.
    if enm.count("2")==1 and re.search(r"\btwo\s+[a-z][a-z'-]+", en, re.I):
        dual_tokens=re.findall(r"(?<![\u0600-\u06FF])ال[\u0600-\u06FF]{3,}(?:ان|ين)(?![\u0600-\u06FF])", ar_norm)
        dual_tokens=[t for t in dual_tokens if t not in {"الذين","اللتين","اللذين","الانسان","الدين"}]
        if dual_tokens:
            enm.remove("2")
    # «لا أحد / لم ... أحد / لن ... أحد» use أحد as a negative pronoun (no one),
    # not the numeric quantity one.
    if "1" in an and re.search(r"(?<![\u0600-\u06FF])(?:لا|لم|لن)\s+(?:[\u0600-\u06FF]+\s+){0,4}احد(?![\u0600-\u06FF])", normalize_ar(ar_unit)):
        removed=False; kept=[]
        for x in an:
            if x=="1" and not removed: removed=True; continue
            kept.append(x)
        an=kept
    if "1" in enm and re.search(r"\b(?:no\s+one|nobody)\b", en, re.I):
        removed=False; kept=[]
        for x in enm:
            if x=="1" and not removed: removed=True; continue
            kept.append(x)
        enm=kept
    # «حكم واحد» often means "the same/a single ruling" as lexical singularity,
    # not a count that must surface as the numeral one in English.
    if "1" in an and re.search(r"\bحكم\s+واحد\b", normalize_ar(ar_unit)):
        removed=False; kept=[]
        for x in an:
            if x=="1" and not removed: removed=True; continue
            kept.append(x)
        an=kept
    return an,enm


_AR_QTY_ANCHORS = {
    "prayer": ["صلوات","صلاة","ركعات","ركعة"],
    "day": ["ايام","يوم"],
    "month": ["اشهر","شهر"],
    "year": ["سنوات","سنة","احوال","حول"],
    "person": ["اشخاص","شخص","رجال","رجل","نساء","امرأة"],
}
_EN_QTY_ANCHORS = {
    "prayer": ["prayers","prayer","rak'ahs","rak'ah","rakahs","rakah"],
    "day": ["days","day"],
    "month": ["months","month"],
    "year": ["lunar years","lunar year","years","year"],
    "person": ["people","person","men","man","women","woman"],
}


def _number_occurrences(text, arabic=False):
    out=[]; occupied=[]
    # Numeric literals.
    for m in re.finditer(r"\d+(?:[.,]\d+)?",text):
        out.append((m.start(),m.end(),m.group(0).replace(',','.'))); occupied.append((m.start(),m.end()))
    mapping=AR_NUMBER_WORDS if arabic else EN_NUMBER_WORDS
    for phrase,val in sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True):
        p=normalize_ar(phrase) if arabic else normalize_en(phrase)
        pat=(rf"(?<![\u0600-\u06FF])(?:[وفبكل])?{re.escape(p)}(?![\u0600-\u06FF])" if arabic else rf"\b{re.escape(p)}\b")
        for m in re.finditer(pat,text):
            sig=(m.start(),m.end())
            if any(not (sig[1] <= a or sig[0] >= b) for a,b in occupied):
                continue
            occupied.append(sig); out.append((m.start(),m.end(),str(val)))
    return sorted(out)


def _adjacent_quantity(text, start, end, arabic=False):
    candidates=[]
    for a,b,val in _number_occurrences(text,arabic=arabic):
        if b <= start:
            dist=start-b
        elif a >= end:
            dist=a-end
        else:
            dist=0
        if dist <= 28:
            candidates.append((dist,a,val))
    return min(candidates,key=lambda x:(x[0],x[1]))[2] if candidates else None


def _anchor_matches(text, words, arabic=False):
    spans=[]
    for word in sorted(words,key=len,reverse=True):
        pat=(rf"(?<![\u0600-\u06FF]){re.escape(normalize_ar(word))}(?![\u0600-\u06FF])" if arabic else rf"\b{re.escape(word)}\b")
        for m in re.finditer(pat,text):
            sig=(m.start(),m.end())
            if any(not (sig[1] <= a or sig[0] >= b) for a,b in spans):
                continue
            spans.append(sig)
    return sorted(spans)


def _quantity_bindings(ar_unit,en_unit):
    """Bind quantities to nearby semantic anchors, preserving location not just bags."""
    ar=normalize_ar(ar_unit); en=normalize_en(en_unit)
    ab,eb={},{}
    for key,words in _AR_QTY_ANCHORS.items():
        for st,ed in _anchor_matches(ar,words,arabic=True):
            v=_adjacent_quantity(ar,st,ed,arabic=True)
            if v is not None: ab.setdefault(key,[]).append(v)
    for key,words in _EN_QTY_ANCHORS.items():
        for st,ed in _anchor_matches(en,words,arabic=False):
            v=_adjacent_quantity(en,st,ed,arabic=False)
            if v is not None: eb.setdefault(key,[]).append(v)
    return ab,eb


def _quantity_binding_issue(ar_unit,en_unit):
    ab,eb=_quantity_bindings(ar_unit,en_unit)
    for key in sorted(set(ab)&set(eb)):
        if sorted(ab[key]) != sorted(eb[key]):
            return key,ab[key],eb[key]
    return None


def _aligned_unit_issues(ar_text,en_text):
    au=_split_units(ar_text); eu=_split_units(en_text)
    # Positional sentence alignment is reliable enough only when both sides segment
    # equally and there is more than one unit. Otherwise use whole-document counts.
    if len(au)<=1 or len(au)!=len(eu):
        return [],[]
    issues=[]; checks=[]
    impacts={
        "exception":"قد يحول الحكم المقيد إلى حكم مطلق أو العكس.",
        "negation":"قد يقلب المعنى إلى نقيضه.",
        "condition":"قد يزيل قيدًا لازمًا لفهم الحكم.",
        "obligation":"قد يغير درجة الإلزام.",
        "recommendation":"قد يحول المستحب إلى واجب أو العكس.",
        "disliked":"قد يحول المكروه إلى محرم أو العكس.",
        "prohibition":"قد يغير درجة المنع.",
        "permission":"قد يغير معنى الإباحة أو الجواز.",
    }
    for idx,(ars,ens) in enumerate(zip(au,eu),1):
        a,e=_unit_signal_hits(ars,ens)
        for key in AR_SIGNALS:
            ac,ec=len(a.get(key,[])),len(e.get(key,[]))
            if ac==ec:
                continue
            checks.append({"check":f"فحص {LABEL[key]} — المقطع {idx}","status":"fail","detail":f"اختلاف داخل المقطع {idx} ({ac} مقابل {ec})"})
            if ac and not ec:
                title=f"{LABEL[key]} مفقود من الترجمة — المقطع {idx}"
                explanation=f"ظهر عنصر {LABEL[key]} في المقطع العربي دون مقابل واضح في المقطع المترجم."
            elif ec and not ac:
                title=f"{LABEL[key]} مضاف في الترجمة — المقطع {idx}"
                explanation=f"ظهر عنصر {LABEL[key]} في المقطع المترجم دون مقابل واضح في الأصل."
            elif ac>ec:
                title=f"فقدان موضع من {LABEL[key]} — المقطع {idx}"
                explanation=f"يحتوي المقطع العربي على {ac} موضع/مواضع من {LABEL[key]} بينما ظهر في الترجمة {ec}."
            else:
                title=f"إضافة موضع من {LABEL[key]} — المقطع {idx}"
                explanation=f"تحتوي ترجمة المقطع على {ec} موضع/مواضع من {LABEL[key]} بينما ظهر في الأصل {ac}."
            issues.append({
                "type":key,"severity":"critical","title":title,"explanation_ar":explanation,
                "impact_ar":impacts[key],"confidence":0.96,"evidence_kind":"deterministic_rule",
                "source_span":_rich_structural_span(ars,key,a.get(key,[])),
                "translation_span":_span_summary(e.get(key,[]),LABEL[key]),
                "source_count":ac,"translation_count":ec,"segment_index":idx,
                "source_segment":ars,"translation_segment":ens,
            })
        an,enm=_numbers_for_unit(ars,ens)
        # In Arabic exclusivity «لا ... إلا», English "one" may be part of a
        # mistranslated exclusivity claim rather than an independent quantity.
        if not an and enm==["1"] and re.search(r"\bلا\b.{0,80}\bالا\b", normalize_ar(ars)):
            enm=[]
        binding=_quantity_binding_issue(ars,ens)
        if binding:
            key,av,ev=binding
            checks.append({"check":f"فحص ارتباط الأرقام بالموضع — المقطع {idx}","status":"fail","detail":f"الكمية المرتبطة بـ {key} تغيرت"})
            issues.append({"type":"quantity","severity":"high","title":f"اختلاف كمية مرتبطة بموضعها — المقطع {idx}","explanation_ar":f"القيمة المرتبطة بالمفهوم نفسه تغيرت ({'، '.join(av)} ↔ {'، '.join(ev)}).","impact_ar":"قد تبقى الأرقام نفسها في النص لكن ترتبط بعناصر مختلفة، فيتغير المعنى.","confidence":0.99,"evidence_kind":"deterministic_rule","source_span":"، ".join(av),"translation_span":"، ".join(ev),"segment_index":idx,"source_segment":ars,"translation_segment":ens})
        elif sorted(set(an))!=sorted(set(enm)):
            checks.append({"check":f"فحص الأرقام والكميات — المقطع {idx}","status":"fail","detail":"يوجد اختلاف عددي داخل المقطع"})
            issues.append({
                "type":"quantity","severity":"high","title":f"اختلاف في رقم أو كمية — المقطع {idx}",
                "explanation_ar":f"تختلف القيمة العددية داخل المقطع ({'، '.join(an) if an else 'لا يوجد'} ↔ {'، '.join(enm) if enm else 'لا يوجد'}).",
                "impact_ar":"تغير الأرقام أو الكميات قد يغير المعلومة نفسها.","confidence":0.98,
                "evidence_kind":"deterministic_rule","source_span":"، ".join(an) if an else "لا يوجد",
                "translation_span":"، ".join(enm) if enm else "لا يوجد","segment_index":idx,
                "source_segment":ars,"translation_segment":ens,
            })
    return issues,checks

def _document_meta_issues(ar_text, en_text):
    """Document-level provenance/version checks that are safe to run across units."""
    ar, en = normalize_ar(ar_text), normalize_en(en_text)
    issues=[]; checks=[]
    ar_source = any(x in ar for x in ["مصدر", "نسبته", "ينسب", "منسوب", "مرجع", "قال العالم", "ذكر العالم", "نقل عن"])
    en_source = any(x in en for x in ["source", "attributed", "reference", "citation", "scholar said", "scholar stated", "reported from"])
    # A preserved structured reference is itself an explicit source attribution even
    # when the surrounding prose is localized differently (e.g. ``المرجع القرآني``
    # versus a bare ``QURAN_REF`` token).  Do not report a provenance omission when
    # the same structured identifier is visibly present on both sides.
    ar_struct=set(re.findall(r'\b(?:QURAN_REF|HADITH_REF)\s*:\s*[A-Za-z0-9:_-]+', ar_text or '', re.I))
    en_struct=set(re.findall(r'\b(?:QURAN_REF|HADITH_REF)\s*:\s*[A-Za-z0-9:_-]+', en_text or '', re.I))
    if ar_struct and en_struct:
        ar_source = en_source = True
    ar_version = any(x in ar for x in ["رقم الاصدار", "الاصدار", "نسخه"])
    en_version = any(x in en for x in ["version", "edition"])

    if ar_source != en_source:
        checks.append({"check": "فحص الإسناد والمصدر", "status": "fail", "detail": "اختلاف في ذكر المصدر أو الإسناد"})
        issues.append({
            "type": "attribution", "severity": "high", "title": "اختلاف في الإسناد أو المصدر",
            "explanation_ar": "ظهر ذكر للمصدر أو الإسناد في أحد النصين دون مقابل واضح في الآخر.",
            "impact_ar": "قد يفصل المعلومة عن مصدرها أو يغيّر نسبتها.",
            "confidence": 0.90, "evidence_kind": "deterministic_rule",
            "source_span": "ذكر مصدر/إسناد" if ar_source else "لا يوجد مقابل",
            "translation_span": "ذكر source/reference" if en_source else "لا يوجد مقابل",
        })
    else:
        checks.append({"check": "فحص الإسناد والمصدر", "status": "pass", "detail": "لا يظهر اختلاف واضح"})

    if ar_version != en_version:
        checks.append({"check": "فحص الإصدار والتتبع", "status": "fail", "detail": "اختلاف في ذكر الإصدار"})
        issues.append({
            "type": "version_trace", "severity": "high", "title": "فقدان معلومة الإصدار",
            "explanation_ar": "ذكر الأصل رقم الإصدار أو النسخة بينما لم يظهر مقابل واضح في الترجمة، أو العكس.",
            "impact_ar": "قد يضعف قابلية التتبع إلى النسخة المعتمدة من المحتوى.",
            "confidence": 0.92, "evidence_kind": "deterministic_rule",
            "source_span": "الإصدار/النسخة" if ar_version else "لا يوجد مقابل",
            "translation_span": "version/edition" if en_version else "لا يوجد مقابل",
        })
    else:
        checks.append({"check": "فحص الإصدار والتتبع", "status": "pass", "detail": "لا يظهر اختلاف واضح"})
    return issues,checks



RULING_KEYS={"obligation","recommendation","disliked","prohibition","permission"}


def _strong_en_condition_hits(en_unit):
    """Return condition markers that clearly constrain the proposition.

    Bare ``if`` is not treated as an added condition by itself because English often
    uses it to render Arabic metalinguistic/hypothetical phrasing (``فقول ...``).
    """
    en=normalize_en(en_unit)
    hits=[]
    for pat in (
        r"\bunless\b", r"\bprovided that\b", r"\bon condition that\b",
        r"\bonly if\b", r"\bprerequisite\b", r"\bin case of\b",
    ):
        hits.extend(m.group(0) for m in re.finditer(pat,en,re.I))
    # Threshold/state conditions are strong even with ordinary 'if'.
    for pat in (
        r"\bif\s+(?:the\s+)?(?:confidence|score|condition|requirement|evidence|source)\b",
        r"\bif\s+[^,.;]{1,80}\b(?:is|are|has|have|fails?|meets?|exceeds?|falls?)\b",
    ):
        hits.extend(m.group(0) for m in re.finditer(pat,en,re.I))
    return hits


def _has_meta_quantity_context(ar_unit):
    """Numbers are mentioned as examples/forbidden alternatives, not all asserted."""
    ar=normalize_ar(ar_unit)
    return bool(re.search(
        r"(?:لا يجوز|لا يصح).{0,80}(?:ترجم|تحويل|نقل).{0,80}(?:الرقم|القيمه|المقدار)|"
        r"(?:لا تعني|لا يعني|يختلف عن|ليست|ليس).{0,80}\d",
        ar,re.I,
    ))


def _contains_structured_reference(text):
    return bool(re.search(r"\[(?:QURAN_REF|HADITH_REF|SOURCE_ID)\s*:", text or "", re.I))


def _contains_explicit_units(text):
    raw=(text or "").translate(str.maketrans("٠١٢٣٤٥٦٧٨٩","0123456789"))
    return bool(re.search(
        r"\d+(?:\.\d+)?\s*(?:دقيقه|دقائق|ساعه|ساعات|مل|مليلتر|لتر|كيلومتر|كم|متر|minutes?|hours?|ml|liters?|litres?|km|kilometers?|meters?)\b",
        normalize_ar(raw) + " " + normalize_en(raw), re.I,
    ))

def _single_unit_issues(ar_text, en_text):
    """Original structural detector for a single aligned unit.

    Long documents must never pool conditions, numbers or modality markers across
    unrelated sentences. This helper is deliberately limited to one unit.
    """
    ar, en = normalize_ar(ar_text), normalize_en(en_text)
    a, e = _unit_signal_hits(ar_text,en_text)

    # "may" can express possibility (قد) rather than permission (يجوز).
    if e.get("permission") == ["may"] and re.search(r"\bقد\b", ar):
        e.pop("permission", None)
    # Phrase-aware equivalence: «إلا وسعها» → "beyond its capacity".
    if re.search(r"\bالا\s+وسع", ar) and re.search(r"\bbeyond\b.*\bcapacity\b", en):
        e["exception"] = (e.get("exception") or []) + ["beyond capacity"]

    issues=[]; checks=[]
    impacts={
        "exception":"قد يحول الحكم المقيد إلى حكم مطلق أو العكس.",
        "negation":"قد يقلب المعنى إلى نقيضه.",
        "condition":"قد يزيل قيدًا لازمًا لفهم الحكم.",
        "obligation":"قد يغير درجة الإلزام.",
        "recommendation":"قد يحول المستحب إلى واجب أو العكس.",
        "disliked":"قد يحول المكروه إلى محرم أو العكس.",
        "prohibition":"قد يغير درجة المنع.",
        "permission":"قد يغير معنى الإباحة أو الجواز.",
    }
    ruling_types_a={k for k in RULING_KEYS if a.get(k)}
    ruling_types_e={k for k in RULING_KEYS if e.get(k)}
    multi_ruling_context=len(ruling_types_a)>1 or len(ruling_types_e)>1

    for key in AR_SIGNALS:
        av,ev=a.get(key,[]),e.get(key,[])
        ac,ec=len(av),len(ev)

        # Contextual conditions: source-side strong constraints are protected, but a
        # bare English ``if`` never becomes an "added condition" finding by itself.
        if key=="condition":
            strong_e=_strong_en_condition_hits(en_text)
            source_has=bool(ac); target_has=bool(ec or strong_e)
            same=(source_has==target_has) or (not source_has)
            checks.append({"check":f"فحص {LABEL[key]}","status":"pass" if same else "fail",
                           "detail":"محفوظ سياقيًا" if same else "قيد شرطي صريح في الأصل بلا مقابل واضح"})
            if same: continue
            title="الشرط الدلالي مفقود من الترجمة"; explanation="يتضمن الأصل قيدًا شرطيًا صريحًا، ولم يظهر مقابل يحفظ هذا القيد في الترجمة."
            issues.append({"type":key,"severity":"critical","title":title,"explanation_ar":explanation,
                "impact_ar":impacts[key],"confidence":0.96,"evidence_kind":"deterministic_rule",
                "source_span":_rich_structural_span(ar_text,key,av),"translation_span":"لا يوجد مقابل واضح",
                "source_count":ac,"translation_count":ec})
            continue

        # Negation/exception are scope operators: compare preservation of the operator,
        # not the raw number of surface tokens. Predicate-level contextual rules below
        # diagnose multiple local changes without multiplying public findings.
        if key in {"negation","exception"}:
            same=bool(ac)==bool(ec)
        # Ruling words in an explanatory paragraph are mentions, not independent
        # verdicts.  Only simple one-ruling contexts use the generic detector.
        elif key in RULING_KEYS and multi_ruling_context:
            checks.append({"check":f"فحص {LABEL[key]}","status":"pass","detail":"أُحيل للسياق المرتبط بالادعاء"})
            continue
        else:
            same=bool(ac)==bool(ec)

        checks.append({"check":f"فحص {LABEL[key]}","status":"pass" if same else "fail",
                       "detail":"محفوظ مبدئيًا" if same else f"اختلاف في وجود {LABEL[key]}"})
        if same: continue
        if ac and not ec:
            title=f"{LABEL[key]} مفقود من الترجمة"; explanation=f"ظهر عنصر {LABEL[key]} في الأصل دون مقابل واضح في الترجمة."
        else:
            title=f"{LABEL[key]} مضاف في الترجمة"; explanation=f"ظهر عنصر {LABEL[key]} في الترجمة دون مقابل واضح في الأصل."
        issues.append({
            "type":key,"severity":"critical","title":title,"explanation_ar":explanation,
            "impact_ar":impacts[key],"confidence":0.95,"evidence_kind":"deterministic_rule",
            "source_span":_rich_structural_span(ar_text,key,av),
            "translation_span":_span_summary(ev,LABEL[key]),
            "source_count":ac,"translation_count":ec,
        })

    an,enums=_numbers_for_unit(ar_text,en_text)
    if not an and enums==["1"] and re.search(r"\bلا\b.{0,80}\bالا\b", ar):
        enums=[]
    binding=_quantity_binding_issue(ar_text,en_text)
    # Reference IDs, unit conversions and metalinguistic "do not translate X as Y"
    # examples have dedicated contextual detectors.  Bag-of-number comparison here
    # would double-count them and mistake mentioned bad values for asserted values.
    contextual_quantity = _contains_structured_reference(ar_text) or _contains_structured_reference(en_text) or _contains_explicit_units(ar_text+" "+en_text) or _has_meta_quantity_context(ar_text)
    ok=contextual_quantity or (binding is None and sorted(an)==sorted(enums))
    checks.append({"check":"فحص الأرقام والكميات","status":"pass" if ok else "fail","detail":"أُحيل للفحص السياقي" if contextual_quantity else ("متطابقة" if ok else "يوجد اختلاف")})
    if not ok:
        if binding:
            key,av,ev=binding
            qtitle="اختلاف كمية مرتبطة بموضعها"
            qexplain=f"القيمة المرتبطة بالمفهوم نفسه تغيرت ({'، '.join(av)} ↔ {'، '.join(ev)})."
            qsrc="، ".join(av); qdst="، ".join(ev)
        else:
            qtitle="اختلاف في رقم أو كمية"
            qexplain=(f"تغيرت القيمة العددية من {an[0] if an else 'لا يوجد'} إلى {enums[0] if enums else 'لا يوجد'}." if len(an)<=1 and len(enums)<=1 else "توجد قيم عددية غير متطابقة بين الأصل والترجمة.")
            qsrc=(an[0] if len(an)==1 else ("، ".join(an[:5]) if an else "لا يوجد")); qdst=(enums[0] if len(enums)==1 else ("، ".join(enums[:5]) if enums else "لا يوجد"))
        issues.append({
            "type":"quantity","severity":"high","title":qtitle,
            "explanation_ar": qexplain,
            "impact_ar":"تغير الأرقام أو الكميات قد يغير المعلومة نفسها.","confidence":0.98,
            "evidence_kind":"deterministic_rule","source_span":qsrc,
            "translation_span":qdst,"source_segment":ar_text,"translation_segment":en_text,
        })
    return issues,checks,a,e


def analyze_rules(ar_text, en_text):
    """Analyze structure with sentence-local isolation whenever alignment is available.

    V5 invariant: a marker or number in one sentence can never compensate for a
    missing marker/number in another sentence. If both sides have the same number of
    review units, every unit is inspected independently and carries segment_index.
    If alignment is not reliable, the detector falls back conservatively to a single
    document-level comparison instead of pretending to know sentence correspondence.
    """
    au=_split_units(ar_text); eu=_split_units(en_text)
    meta_issues,meta_checks=_document_meta_issues(ar_text,en_text)

    pairs,align_mode=aligned_pairs(ar_text,en_text)
    if len(pairs)>1:
        issues=[]; checks=[]; ar_hits={}; en_hits={}
        for idx,ars,ens in pairs:
            ii,cc,a,e=_single_unit_issues(ars,ens)
            for item in ii:
                item["segment_index"]=idx
                item["source_segment"]=ars
                item["translation_segment"]=ens
                item["title"]=f"{item['title']} — المقطع {idx}"
            for c in cc:
                c["check"]=f"{c['check']} — المقطع {idx}"
            issues.extend(ii); checks.extend(cc)
            for k,v in a.items(): ar_hits.setdefault(k,[]).extend(v)
            for k,v in e.items(): en_hits.setdefault(k,[]).extend(v)
        issues.extend(meta_issues); checks.extend(meta_checks)
        return {"issues":issues,"checks":checks,"ar_hits":ar_hits,"en_hits":en_hits,"alignment":{"mode":align_mode,"units":len(pairs)}}

    issues,checks,a,e=_single_unit_issues(ar_text,en_text)
    issues.extend(meta_issues); checks.extend(meta_checks)
    return {"issues":issues,"checks":checks,"ar_hits":a,"en_hits":e,"alignment":{"mode":"document_fallback","units":max(len(au),len(eu),1)}}
