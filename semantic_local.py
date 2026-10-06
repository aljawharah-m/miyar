import re
from .normalization import normalize_ar, normalize_en, tokens_ar, tokens_en
from .alignment import split_units, aligned_pairs

AR_SCOPE=["بعض","قد","غالبا","احيانا","في بعض","في حال","عند","اذا","الا"]
EN_SCOPE=["some","may","might","often","sometimes","in some","if","when","except","unless","beyond","is but","are but","was but","were but","nothing but"]
AR_UNIV=["كل","دائما","ابدا","جميع","فقط"]
EN_UNIV=["all","always","never","every","only","absolutely"]


def _ar_has(text,term):
    # Phrase matching still needs Arabic token boundaries. A raw substring match
    # made «في حال» fire inside the dual noun «في حالتين».
    return re.search(rf"(?<![\u0600-\u06FF]){re.escape(term)}(?![\u0600-\u06FF])", text) is not None


def _en_has(text,term):
    return re.search(rf"\b{re.escape(term)}\b", text) is not None


def _analyze_local_semantics_single(ar_text,en_text):
    ar,en=normalize_ar(ar_text),normalize_en(en_text)
    issues=[]; checks=[]

    ar_u=[x for x in AR_UNIV if _ar_has(ar,x)]
    en_u=[x for x in EN_UNIV if _en_has(en,x)]
    ar_s=[x for x in AR_SCOPE if _ar_has(ar,x)]
    en_s=[x for x in EN_SCOPE if _en_has(en,x)]

    # Generic ``لكل <group>`` is universal over that group; English ``every <group>``
    # preserves rather than adds quantification.
    if re.search(r"(?<![\u0600-\u06FF])لكل\s+[\u0600-\u06FF]{2,}(?![\u0600-\u06FF])", ar) and "every" in en_u and re.search(r"\bevery\s+[a-z][a-z'-]*\b", en, re.I):
        en_u=[x for x in en_u if x != "every"]

    # «لكل امرئ/لكل شخص» is already universal over the stated group; English
    # ``every person`` preserves that quantification rather than adding a new one.
    if re.search(r"\bلكل\s+(?:امرئ|شخص|انسان)\b", ar) and "every" in en_u and re.search(r"\bevery\s+(?:person|one|individual|human)\b", en, re.I):
        en_u=[x for x in en_u if x != "every"]

    # Arabic «إنما» carries exclusivity even though the coarse AR_UNIV list does not.
    # English ``only`` in the aligned clause can therefore be faithful, not a new universal.
    if re.search(r"(?<![\u0600-\u06FF])(?:و|ف)?انما\b", ar) and "only" in en_u:
        en_u=[x for x in en_u if x != "only"]

    # Lexical adjective ``الوحيد/الوحيدة`` maps to English ``only`` without
    # adding proposition-level universal scope.
    if re.search(r"(?<![\u0600-\u06FF])(?:ال)?وحيد(?:ه|ة)?(?![\u0600-\u06FF])", ar) and "only" in en_u:
        en_u=[x for x in en_u if x != "only"]

    # Qur'anic nominal negation «لا انفصام لها» is naturally rendered as
    # “it never breaks”.  Preserve the negative absolute instead of treating
    # English ``never`` as a new generalization.
    if "never" in en_u and re.search(r"لا\s+انفصام\s+لها", ar) and re.search(r"\bnever\s+(?:breaks?|break)\b", en, re.I):
        en_u=[x for x in en_u if x != "never"]

    # Arabic ``لا ... إلا`` may be rendered as English ``no ... but ...``
    # (e.g. لا إله إلا الله -> no god but Allah).  Preserve the scope marker.
    if re.search(r"\bلا\b.{0,120}\bالا\b", ar) and re.search(r"\bno\b.{0,120}\bbut\b", en, re.I):
        if not en_s: en_s.append("no ... but (exclusivity)")

    # Arabic ``لا ... إلا`` can be rendered as English ``only when/if/...``.
    # Here ``only`` is the preserved exclusivity operator, not a new universal.
    if re.search(r"\bلا\b.{0,120}(?:\bالا\b)", ar) and re.search(r"\bonly\s+(?:if|when|with|after|before|by|upon)\b", en, re.I):
        if "only" in en_u: en_u=[x for x in en_u if x != "only"]
        if not en_s: en_s.append("only (exclusivity)")

    # Arabic ``الحمد`` is conventionally rendered as ``all praise``.  The word
    # ``all`` belongs to the lexical rendering of praise here; it is not an added
    # proposition-level universal quantifier.
    if "all" in en_u and re.search(r"(?<![\u0600-\u06FF])الحمد(?![\u0600-\u06FF])", ar) and re.search(r"\ball\s+praise\b", en, re.I):
        en_u=[x for x in en_u if x != "all"]

    # Qur'anic phrase ``رب العالمين`` is naturally rendered with ``all worlds``
    # or ``all creation``; ``all`` here belongs to the lexical rendering, not an
    # invented proposition-level generalization.
    if "all" in en_u and re.search(r"رب\s+العالمين", ar) and re.search(r"\b(?:lord|sustainer)\s+of\s+all\s+(?:worlds|creation)\b", en, re.I):
        en_u=[x for x in en_u if x != "all"]

    # Do not treat lexicalized renderings such as “the Sustainer of all existence”
    # or “All-Sustaining” as a proposition-level universal quantifier.
    if "all" in en_u and (re.search(r"\bsustainer\s+of\s+all\s+existence\b", en, re.I) or re.search(r"\ball[- ]sustaining\b", en, re.I)):
        en_u=[x for x in en_u if x != "all"]

    # Relative Arabic «ما» can naturally be rendered as “all what/all that” in
    # phrases such as «من شر ما خلق».  The English ``all`` is then lexical scope
    # already present in the relative construction, not an invented universal.
    if "all" in en_u and re.search(r"(?<![\u0600-\u06FF])ما(?![\u0600-\u06FF])", ar) and re.search(r"\ball\s+(?:what|that)\b", en, re.I):
        en_u=[x for x in en_u if x != "all"]

    # Divine-name renderings such as All-Hearing / All-Knowing are lexicalized
    # adjectives, not proposition-level generalization.
    if "all" in en_u and re.search(r"\ball[- ](?:hearing|knowing|seeing|wise|powerful|mighty)\b", en, re.I):
        en_u=[x for x in en_u if x != "all"]

    # Arabic «قد» is not always epistemic uncertainty.  In perfective Quranic
    # constructions such as «قد تبين» it marks realization/emphasis, so do not
    # force a scope warning unless a genuine uncertainty pattern is present.
    if "قد" in ar_s and not re.search(r"(?<![\u0600-\u06FF])قد\s+(?:يكون|تكون|يحدث|تحدث|يمكن|يحتمل|يؤدي|تؤدي|لا)(?![\u0600-\u06FF])", ar):
        ar_s=[x for x in ar_s if x != "قد"]

    # "only for <group>" narrows the addressee/scope; it is not a generalization.
    # Label it as an added restrictive qualifier so the diagnosis matches the actual drift.
    only_for=re.search(r"\bonly\s+for\s+([^,.;!?]{1,80})", en, re.I)
    if only_for and not any(x in ar for x in ["فقط", "وحده", "حصرا", "دون غيره"]):
        qualifier=f"only for {only_for.group(1).strip()}"
        issues.append({"type":"scope_addition","severity":"high","title":"إضافة قيد يغيّر نطاق الحكم","source_span":"لا يوجد قيد مقابل","translation_span":qualifier,"explanation_ar":f"أضافت الترجمة قيدًا «{qualifier}» غير ظاهر في الأصل.","impact_ar":"قد يضيّق الحكم على فئة لم يقيّد بها النص الأصلي.","confidence":0.92,"evidence_kind":"local_semantic_heuristic"})
        checks.append({"check":"فحص التعميم والتضييق","status":"fail","detail":"إضافة قيد حصري غير موجود في الأصل"})
        en_u=[x for x in en_u if x != "only"]

    if en_u and not ar_u:
        issues.append({"type":"generalization","severity":"high","title":"تعميم لم يظهر في الأصل","source_span":ar_s[0] if ar_s else "لا يوجد تعميم","translation_span":en_u[0],"explanation_ar":f"ظهرت صياغة تعميمية مثل «{en_u[0]}» دون مؤشر مماثل في الأصل.","impact_ar":"قد تجعل حالة جزئية أو مقيدة تبدو قاعدة عامة.","confidence":0.82,"evidence_kind":"local_semantic_heuristic"})
        checks.append({"check":"فحص التعميم والتضييق","status":"fail","detail":"تعميم إضافي محتمل"})
    elif ar_u and en_s and not en_u:
        issues.append({"type":"narrowing","severity":"high","title":"تضييق لمعنى عام في الأصل","source_span":ar_u[0],"translation_span":en_s[0],"explanation_ar":f"الأصل يتضمن عمومًا مثل «{ar_u[0]}» بينما الترجمة أدخلت قيدًا مثل «{en_s[0]}».","impact_ar":"قد يحول قاعدة عامة إلى حالة جزئية.","confidence":0.80,"evidence_kind":"local_semantic_heuristic"})
        checks.append({"check":"فحص التعميم والتضييق","status":"fail","detail":"تضييق محتمل"})
    else:
        checks.append({"check":"فحص التعميم والتضييق","status":"pass","detail":"لا يظهر تغير نطاق واضح"})

    if ar_s and not en_s:
        issues.append({"type":"scope","severity":"medium","title":"احتمال فقدان قيد أو نطاق","source_span":ar_s[0],"translation_span":"لا يوجد مقابل واضح","explanation_ar":f"الأصل يتضمن قيدًا مثل «{ar_s[0]}» ولم يظهر قيد واضح في الترجمة.","impact_ar":"قد يصبح المعنى أوسع أو أكثر قطعًا من الأصل.","confidence":0.72,"evidence_kind":"local_semantic_heuristic"})
        checks.append({"check":"فحص النطاق","status":"review","detail":"قيد عربي بلا مقابل واضح"})
    else:
        checks.append({"check":"فحص النطاق","status":"pass","detail":"لا يظهر فقدان نطاق واضح"})

    # Audience/subject qualifiers after an obligation are semantically material.
    # Example: «الصلاة واجبة على المسلم البالغ» must not collapse to
    # ``Prayer is obligatory``.  This is deliberately narrow: it activates only when
    # Arabic has an explicit ruling + «على ...» tail and English keeps the ruling but
    # omits any corresponding target phrase introduced by for/on/upon.
    m_target=re.search(r"(?:واجب(?:ة|ا)?|يجب|فرض(?:ت|ه|ها|ا)?)\s+(?:على|علي)\s+([^،,.؛!?؟\n]{2,80})", ar)
    if m_target and re.search(r"\b(?:obligatory|required|must|duty|binding)\b", en):
        target=m_target.group(1).strip()
        has_target_marker=bool(re.search(r"\b(?:for|on|upon)\b", en))
        # ``يجب على X أن يفعل`` maps naturally to ``X must do``; the addressee is
        # expressed as the grammatical subject rather than after for/on/upon.
        ar_norm=normalize_ar(ar_text)
        subject_modal_equiv=bool(re.search(r"\bيجب\s+(?:على|علي)\s+", ar_norm) and re.search(r"^[^,.;!?]{1,90}\bmust\b", en, re.I))
        if not has_target_marker and not subject_modal_equiv:
            issues.append({
                "type":"scope","severity":"high","title":"فقدان قيد يحدد من يتوجه إليه الحكم",
                "source_span":f"على {target}","translation_span":"لا يوجد مقابل واضح",
                "explanation_ar":"الأصل يقيّد الحكم بفئة أو مخاطب محدد، بينما ظهرت الترجمة مطلقة.",
                "impact_ar":"قد يوسّع الحكم إلى من لم يشمله القيد في الأصل.",
                "confidence":0.91,"evidence_kind":"local_semantic_heuristic"
            })
            checks.append({"check":"فحص قيد المخاطب","status":"fail","detail":"قيد «على ...» لم يظهر في الترجمة"})

    arl,enl=max(1,len(tokens_ar(ar_text))),max(1,len(tokens_en(en_text)))
    ratio=enl/arl
    if arl>=8 and ratio<0.45:
        issues.append({"type":"omission","severity":"medium","title":"احتمال حذف معنى","source_span":f"{arl} وحدة نصية تقريبًا","translation_span":f"{enl} وحدة نصية تقريبًا","explanation_ar":"الترجمة أقصر بكثير من الأصل، ما قد يشير إلى حذف معنى.","impact_ar":"قد يسقط وصفًا أو شرطًا أو قيدًا مؤثرًا.","confidence":0.62,"evidence_kind":"coverage_heuristic"})
        checks.append({"check":"فحص التغطية","status":"review","detail":"الترجمة أقصر بكثير"})
    elif arl>=8 and enl>=8 and ratio>3:
        issues.append({"type":"addition","severity":"medium","title":"احتمال إضافة معنى","source_span":f"{arl} وحدة نصية تقريبًا","translation_span":f"{enl} وحدة نصية تقريبًا","explanation_ar":"الترجمة أطول بكثير من الأصل، ما قد يشير إلى إضافة شرح داخل الترجمة.","impact_ar":"قد يخلط بين النص المترجم والشرح.","confidence":0.60,"evidence_kind":"coverage_heuristic"})
        checks.append({"check":"فحص التغطية","status":"review","detail":"الترجمة أطول بكثير"})
    else:
        checks.append({"check":"فحص التغطية","status":"pass","detail":"لا يظهر فارق طول لافت"})
    return {"issues":issues,"checks":checks}



def _split_units(text):
    return split_units(text)


def analyze_local_semantics(ar_text,en_text):
    """Run scope/coverage heuristics per aligned sentence when possible."""
    pairs,_=aligned_pairs(ar_text,en_text)
    if len(pairs)>1:
        issues=[]; checks=[]
        for idx,ars,ens in pairs:
            res=_analyze_local_semantics_single(ars,ens)
            for item in res["issues"]:
                item["segment_index"]=idx
                item["source_segment"]=ars
                item["translation_segment"]=ens
                item["title"]=f"{item['title']} — المقطع {idx}"
            for c in res["checks"]:
                c["check"]=f"{c['check']} — المقطع {idx}"
            issues.extend(res["issues"]); checks.extend(res["checks"])
        return {"issues":issues,"checks":checks}
    return _analyze_local_semantics_single(ar_text,en_text)
