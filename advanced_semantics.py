import re
from .normalization import normalize_ar, normalize_en, numbers
from .alignment import split_units, aligned_pairs


def _split_units(text):
    return split_units(text)


def _issue(type_, title, arseg, enseg, idx, explanation, impact, severity='high', src='', dst='', confidence=.94, evidence='deterministic_rule'):
    return {
        'type':type_, 'severity':severity, 'title':f'{title} — المقطع {idx}',
        'explanation_ar':explanation, 'impact_ar':impact, 'confidence':confidence,
        'evidence_kind':evidence, 'source_span':src or arseg, 'translation_span':dst or enseg,
        'segment_index':idx, 'source_segment':arseg, 'translation_segment':enseg,
    }


AR_SCOPE = {
    'universal':[r'\bكل\b',r'\bجميع\b',r'\bالجميع\b'],
    'partial':[r'\bبعض\b'],
    'only':[r'\bفقط\b',r'\bحصرا\b'],
    'specific':[r'\bخاص(?:ه|ة)?\s+ب',r'\bمخصوص(?:ه|ة)?\s+ب'],
    'sometimes':[r'\bاحيانا\b',r'\bقد\b'],
    'always':[r'\bدائما\b',r'\bفي جميع الاحوال\b'],
    'not_limited':[r'\bلا\s+يقتصر\b',r'\bلا\s+تقتصر\b',r'\bولا\s+يقتصر\b',r'\bولا\s+تقتصر\b'],
}
EN_SCOPE = {
    'universal':[r'\ball\b',r'\bevery\b',r'\beveryone\b',r'\ball people\b',r'\bin all cases\b'],
    'partial':[r'\bsome\b'],
    'only':[r'\bonly\b',r'\bmerely\b',r'\bsimply\b'],
    'specific':[r'\bspecific to\b',r'\bonly for\b'],
    'sometimes':[r'\bsometimes\b',r'\bmay happen\b'],
    'always':[r'\balways\b'],
}


def _has(text, patterns):
    return any(re.search(p,text,re.I) for p in patterns)


def analyze_scope(ar_text,en_text):
    pairs,_=aligned_pairs(ar_text,en_text)
    if not pairs: return {'issues':[],'checks':[]}
    issues=[]; checks=[]
    for idx,ars,ens in pairs:
        ar,en=normalize_ar(ars),normalize_en(ens)
        a={k:_has(ar,v) for k,v in AR_SCOPE.items()}; e={k:_has(en,v) for k,v in EN_SCOPE.items()}
        local=[]
        if a['partial'] and e['universal']:
            local.append(_issue('scope_shift','تعميم ما كان جزئيًا',ars,ens,idx,'الأصل يقيد الحكم ببعض الأفراد، بينما الترجمة عممته على الجميع.','قد يوسع نطاق الحكم إلى من لم يشملهم الأصل.', 'medium','بعض', 'everyone/all'))
        if a['universal'] and e['partial']:
            local.append(_issue('scope_shift','تخصيص ما كان عامًا',ars,ens,idx,'الأصل يعمم الحكم، بينما الترجمة قصرته على بعض الأفراد.','قد يخرج أفرادًا من نطاق الحكم دون مستند.', 'medium','كل/جميع','some'))
        if a['specific'] and e['universal']:
            local.append(_issue('scope_shift','تحويل حكم خاص إلى حكم عام',ars,ens,idx,'الأصل يخص الحكم بفئة أو حالة، بينما الترجمة تجعله عامًا.','يزيل قيدًا يحدد نطاق الحكم.', 'critical','خاص بـ','all/everyone'))
        if a['sometimes'] and e['always']:
            local.append(_issue('frequency_shift','تحويل الاحتمال أو التكرار الجزئي إلى دوام',ars,ens,idx,'الأصل يدل على وقوع محتمل أو أحيانًا، بينما الترجمة تجعله دائمًا.','يغيّر درجة العموم والتكرار.', 'high','أحيانًا/قد','always'))
        if a['not_limited'] and e['only']:
            local.append(_issue('scope_reversal','قلب معنى عدم الاقتصار إلى الحصر',ars,ens,idx,'الأصل ينفي حصر المعنى في جانب واحد، بينما الترجمة تحصره فيه.','يقلب نطاق المفهوم ويختزله.', 'critical','لا يقتصر/لا تقتصر','only'))
        if a['only'] and not e['only']:
            local.append(_issue('scope_omission','فقدان قيد الحصر «فقط»',ars,ens,idx,'الأصل يتضمن قيد «فقط» ولم يظهر مقابل واضح له.','قد يوسع المعنى خارج حدوده.', 'high','فقط','لا يوجد مقابل'))
        issues.extend(local)
        checks.append({'check':f'فحص النطاق والعموم — المقطع {idx}','status':'fail' if local else 'pass','detail':'تغيّر في النطاق/العموم' if local else 'لا يظهر تغير واضح'})
    return {'issues':issues,'checks':checks}


TERM_EQ = {
    'الصدقة':['charity','sadaqah','sadaqa'], 'الزكاة':['zakat'],
    'الفتوى':['fatwa'], 'رايا شخصيا':['personal opinion'],
    'السنة':['sunnah'], 'عادات اجتماعية':['social customs','customs'],
    'الوحي':['revelation'], 'الهاما شخصيا':['personal inspiration'],
    'العبادة':['worship'], 'الطقوس الظاهرة':['outward rituals','rituals only'],
    'الشريعة':['sharia'], 'القانون الجنائي':['criminal law'],
}


def analyze_term_relations(ar_text,en_text):
    pairs,_=aligned_pairs(ar_text,en_text)
    if not pairs: return {'issues':[],'checks':[]}
    issues=[]; checks=[]
    for idx,ars,ens in pairs:
        ar,en=normalize_ar(ars),normalize_en(ens); local=[]
        # Distinction/equation reversal: X is not Y -> X is Y / X means Y.
        relation_cases=[
            ('الصدقة','الزكاة','الصدقة والزكاة'),
            ('الفتوى','رايا شخصيا','الفتوى والرأي الشخصي'),
            ('السنة','عادات اجتماعية','السنة والعادات الاجتماعية'),
            ('الوحي','الهاما شخصيا','الوحي والإلهام الشخصي'),
        ]
        for left,right,label in relation_cases:
            left_n,right_n=normalize_ar(left),normalize_ar(right)
            right_present = right_n in ar
            if left_n in ar and right_present and re.search(r'\b(?:ليس|ليست|ليسوا|ليسا|ولا|لا)\b', ar):
                lphr=TERM_EQ[left]; rphr=TERM_EQ[right]
                lhit=next((p for p in lphr if p in en),None); rhit=next((p for p in rphr if p in en),None)
                positive = lhit and rhit and not re.search(r'\b(?:not|isn\'t|is not|does not|do not)\b',en)
                if positive:
                    local.append(_issue('term_relation_reversal',f'دمج مفهومين مختلفين: {label}',ars,ens,idx,'الأصل يفرق بين مفهومين، بينما الترجمة تسوي بينهما أو تعرف أحدهما بالآخر.','قد يمحو فرقًا اصطلاحيًا مؤثرًا.', 'critical',label,f'{lhit} / {rhit}'))
        if ('العبادة' in ar and ('لا تقتصر' in ar or 'ولا تقتصر' in ar)) and ('worship' in en and 'ritual' in en and bool(re.search(r'\b(?:only|merely)\b',en))):
            local.append(_issue('term_scope_reversal','اختزال «العبادة» في الطقوس الظاهرة',ars,ens,idx,'الأصل ينفي حصر العبادة في الطقوس، بينما الترجمة تحصرها فيها.','يختزل مفهومًا شرعيًا أوسع.', 'critical','العبادة لا تقتصر على الطقوس','worship ... rituals only'))
        if ('الشريعة' in ar and ('لا تقتصر' in ar or 'ولا تقتصر' in ar)) and re.search(r'\bsharia\b.*\b(?:means|is)?\s*(?:only\s+)?criminal law\b',en):
            local.append(_issue('term_scope_reversal','اختزال «الشريعة» في القانون الجنائي',ars,ens,idx,'الأصل ينفي هذا الاختزال، بينما الترجمة تقرره.','يضيّق مفهوم الشريعة إلى جزء واحد.', 'critical','الشريعة لا تقتصر على القانون الجنائي','Sharia ... criminal law'))
        if 'الحجاب' in ar and re.search(r'\b(?:simply|only|merely)\b.*\b(?:piece of cloth|headscarf|veil)\b',en):
            local.append(_issue('terminology_context','اختزال سياقي لمصطلح «الحجاب»',ars,ens,idx,'الترجمة تحسم معنى الحجاب في قطعة لباس واحدة رغم أن الأصل يصرح بالحاجة إلى السياق.','المقابل قد يكون أضيق من المقصود في هذا السياق.', 'medium','الحجاب','piece of cloth',.82,'curated_terminology_rule'))
        issues.extend(local)
        checks.append({'check':f'فحص العلاقات بين المصطلحات — المقطع {idx}','status':'fail' if any(i['severity'] in {'high','critical'} for i in local) else ('review' if local else 'pass'),'detail':'علاقة اصطلاحية تغيرت' if local else 'لا يظهر دمج أو اختزال علاقي'})
    return {'issues':issues,'checks':checks}


AR_PROV_NEG=[r'لم\s+يثبت',r'دون\s+مصدر',r'بلا\s+تثبت',r'عدم\s+وجود\s+توثيق',r'لم\s+يذكر.*مصدر',r'لم\s+يحدد.*مصدر',r'ليس\s+نصا\s+من\s+القران',r'ليس\s+جزءا\s+من\s+نص\s+الايه',r'لم\s+ينسب']
AR_PROV_POS=[r'مصدر\s+موثوق',r'ثبت(?:\s+انه)?\s+حديث',r'حديث\s+صحيح',r'نص\s+من\s+القران']
EN_PROV_POS=[r'definitely\s+(?:an?\s+)?authentic',r'certainly\s+(?:an?\s+)?authentic',r'verified\s+(?:authenticated\s+)?source',r'verified\s+prophetic\s+hadith',r'authentic\s+hadith',r'(?:a\s+)?verse\s+from\s+the\s+quran',r'part\s+of\s+the\s+quranic\s+verse',r'safely\s+be\s+attributed']
EN_PROV_NEG=[r'no\s+known\s+source',r'no\s+specific\s+source',r'without\s+verification',r'not\s+attributed',r'not\s+(?:an?\s+)?authentic',r'not\s+part\s+of',r'not\s+(?:been\s+)?established.{0,80}authentic\s+hadith',r'has\s+not\s+been\s+established.{0,80}authentic\s+hadith']


def _asserted_ar_provenance_positive(ar):
    """Return True only for provenance/authenticity claims asserted by Arabic."""
    if re.search(r'\bلم\s+يثبت.{0,100}\bحديث\s+صحيح\b', ar):
        return False
    if re.search(r'\bليس.{0,80}\b(?:نص|جزء).{0,40}\b(?:القران|الايه)\b', ar):
        return False
    return _has(ar,AR_PROV_POS)


def _asserted_provenance_positive(en):
    """Return True only when an English provenance claim is actually asserted.

    Surface keyword matching is unsafe here: ``authentic hadith`` inside
    ``has not been established as an authentic hadith`` is explicitly *not* an
    authentication claim. Conversely ``can safely be attributed ... without
    verification`` remains a dangerous positive attribution and must be caught.
    """
    if re.search(r'\bsafely\s+be\s+attributed\b', en):
        return True
    if re.search(r'\b(?:has|have|had|is|was|were)?\s*not\s+(?:been\s+)?established.{0,100}\bauthentic\s+hadith\b', en):
        return False
    if re.search(r'\bnot\s+(?:an?\s+)?authentic\b', en):
        return False
    if re.search(r'\bno\s+(?:known|specific|verified|authenticated)?\s*source\b', en):
        return False
    return _has(en,EN_PROV_POS)


def analyze_provenance(ar_text,en_text):
    pairs,_=aligned_pairs(ar_text,en_text)
    if not pairs: return {'issues':[],'checks':[]}
    issues=[]; checks=[]
    for idx,ars,ens in pairs:
        ar,en=normalize_ar(ars),normalize_en(ens); local=[]
        aneg=_has(ar,AR_PROV_NEG); apos=_asserted_ar_provenance_positive(ar); epos=_asserted_provenance_positive(en); eneg=_has(en,EN_PROV_NEG)
        sacred = bool(re.search(r'(?:تفسير|شرح).*(?:ليس|وليس).*القران|ليس.*(?:نص|جزء).*الايه',ar) and re.search(r'(?:verse from the quran|part of the quranic verse)',en))
        if aneg and epos and not sacred:
            local.append(_issue('provenance_claim_shift','إضافة ادعاء توثيق أو نسبة غير موجودة في الأصل',ars,ens,idx,'الأصل ينفي الثبوت أو المصدر أو النسبة، بينما الترجمة تقدمها كموثقة أو صحيحة.','قد تنسب قولًا إلى مصدر ديني بثقة غير موجودة في الأصل.', 'critical','عدم ثبوت/عدم مصدر','authenticated/verified attribution'))
        if apos and eneg:
            local.append(_issue('provenance_claim_shift','إسقاط توثيق مثبت في الأصل',ars,ens,idx,'الأصل يذكر ثبوتًا أو مصدرًا موثوقًا، بينما الترجمة تنفيه.','يفقد القارئ معلومة التوثيق أو الثبوت.', 'high','مصدر موثوق','no known source'))
        # Human explanation vs sacred scripture claim.
        if sacred:
            local.append(_issue('sacred_text_boundary','تحويل شرح بشري إلى نص قرآني',ars,ens,idx,'الأصل يميز الشرح البشري عن نص القرآن، بينما الترجمة تدمجه في النص المقدس.','يطمس الحد بين النص المقدس والشرح البشري.', 'critical','تفسير/شرح بشري','Quranic verse'))
        issues.extend(local)
        checks.append({'check':f'فحص النسبة والتوثيق — المقطع {idx}','status':'fail' if local else 'pass','detail':'تغير ادعاء الثبوت/المصدر' if local else 'لا يظهر تغير واضح في دعوى المصدر'})
    return {'issues':issues,'checks':checks}


def _content_tokens(text):
    stop={"the","a","an","is","are","was","were","be","been","being","and","or","of","to","in","on","for","with","from","that","this","he","she","it","they","his","her","their","then","if","but","not","no","nor","neither","who","all"}
    return {t for t in re.findall(r"[a-z][a-z'-]*", normalize_en(text)) if len(t)>2 and t not in stop}


def _reference_window(reference, user_translation):
    """Select the smallest reference clause that best aligns with the user text.

    Trusted APIs often return a full verse/hadith while the Arabic input is only a
    clause from it. Comparing the user translation against unrelated remainder text
    creates false polarity/condition alarms. This local alignment keeps reference
    grounding but restricts contradiction rules to the semantically closest span.
    """
    ref=normalize_en(reference)
    usr=normalize_en(user_translation)
    # Remove footnote markers before clause segmentation.
    ref=re.sub(r'\[[^\]]*\]', ' ', ref)
    clauses=[c.strip() for c in re.split(r'(?<=[.!?;:])\s+|,\s+(?=(?:and|but|if|when|or)\b)', ref) if c.strip()]
    if not clauses:
        return ref
    ut=_content_tokens(usr)
    if not ut:
        return ref
    candidates=[]
    for i in range(len(clauses)):
        for width in (1,2):
            c=' '.join(clauses[i:i+width]).strip()
            if not c: continue
            ct=_content_tokens(c)
            overlap=len(ut & ct)
            recall=overlap/max(1,len(ut))
            precision=overlap/max(1,len(ct))
            score=(2*recall+precision)/3
            candidates.append((score, overlap, -len(ct), c))
    best=max(candidates, default=(0,0,0,ref))
    # If there is no lexical anchor, preserve the full reference rather than invent
    # alignment. Specialized contradiction rules may still reason conservatively.
    return best[3] if best[1] else ref




def _trusted_relation_conflict(ref, user):
    """Return a conservative semantic contradiction grounded in trusted English text.

    This layer is intentionally relation-based rather than hadith-ID based.  It only
    fires when the retrieved reference and the user translation contain opposing
    predicates around the same religious concept.  It is therefore safer than broad
    lexical-distance scoring and catches deep reversals that do not need a literal
    negation token (accepted/rejected, love/hate, safe/harm, etc.).
    """
    r=normalize_en(ref); u=normalize_en(user)
    checks=[
        # acceptance / rejection
        (r'\b(?:reject(?:ed)?|shall have it rejected|discard(?:ed)?)\b',
         r'\b(?:accept(?:ed)?|approve(?:d)?|valid|accepted as valid)\b',
         'قُلِب معنى القبول والرد مقارنة بالمرجع'),
        (r'\b(?:accept(?:ed)?|approve(?:d)?|valid)\b',
         r'\b(?:reject(?:ed)?|discard(?:ed)?)\b',
         'قُلِب معنى القبول والرد مقارنة بالمرجع'),
        # love / hate
        (r'\blov(?:e|es|ed|ing)\b', r'\bhat(?:e|es|ed|ing)\b',
         'قُلِبت علاقة المحبة إلى الكراهية مقارنة بالمرجع'),
        (r'\bhat(?:e|es|ed|ing)\b', r'\blov(?:e|es|ed|ing)\b',
         'قُلِبت علاقة الكراهية إلى المحبة مقارنة بالمرجع'),
        # safety / harm
        (r'\bsafe\b', r'\b(?:harm|harms|harmed|harming|injure|injures|hurt|hurts)\b',
         'قُلِب معنى السلامة إلى الإيذاء مقارنة بالمرجع'),
        (r'\b(?:harm|evil)\b', r'\b(?:benefit|good)\b',
         'قُلِب معنى الضرر إلى النفع مقارنة بالمرجع'),
        (r'\b(?:benefit|good)\b', r'\b(?:harm|evil)\b',
         'قُلِب معنى النفع إلى الضرر مقارنة بالمرجع'),
        # good / bad character
        (r'\bgood\s+character\b', r'\b(?:bad|evil)\s+character\b|\bgood\s+character\s+is\s+sin\b',
         'قُلِبت قيمة الخلق مقارنة بالمرجع'),
        # paradise / hellfire
        (r'\b(?:hellfire|hell)\b', r'\bparadise\b',
         'قُلِبت العاقبة المذكورة مقارنة بالمرجع'),
        (r'\bparadise\b', r'\b(?:hellfire|hell)\b',
         'قُلِبت العاقبة المذكورة مقارنة بالمرجع'),
    ]
    for rp,up,title in checks:
        if re.search(rp,r,re.I) and re.search(up,u,re.I):
            return title

    # Quran/Hadith trusted-reference antonym relations.  These require a concrete
    # predicate in the retrieved English reference and its explicit semantic opposite
    # in the user translation, so they remain source-grounded rather than guessing
    # from the Arabic text alone.
    sacred_antonyms=[
        (r'\b(?:compassionate|merciful)\b', r'\b(?:cruel|unmerciful|merciless)\b', 'قُلِبت دلالة الرحمة مقارنة بالمرجع'),
        (r'\b(?:master|sovereign|king)\b', r'\bservant\b', 'قُلِبت دلالة السيادة إلى العبودية مقارنة بالمرجع'),
        (r'\bstraight\s+path\b', r'\b(?:crooked|deviant|wrong)\s+path\b|\b(?:away|astray)\s+from\s+the\s+straight\s+path\b|\blead\s+us\s+away\b', 'قُلِب اتجاه الصراط المذكور في المرجع'),
    ]
    for rp,up,title in sacred_antonyms:
        if re.search(rp,r,re.I) and re.search(up,u,re.I):
            return title

    # A trusted reference that attributes the statement to Allah cannot be changed
    # into explicit plurality of deities.  Require an explicit plural-divinity phrase
    # in the user text; this is not triggered by ordinary plural nouns.
    if re.search(r'\ballah\b',r,re.I) and re.search(r'\b(?:several|many|multiple)\s+gods?\b|\bone\s+of\s+(?:several|many|multiple)\s+gods?\b',u,re.I):
        return 'قُلِبت دلالة الوحدانية مقارنة بالمرجع'
    if re.search(r'\b(?:god|the god)\b',r,re.I) and re.search(r'\bone\s+(?:among|of)\s+(?:several|many|multiple)\s+gods?\b|\b(?:several|many|multiple)\s+gods?\b',u,re.I):
        return 'قُلِبت دلالة الوحدانية مقارنة بالمرجع'

    # Exclusive worship/help in the trusted text versus explicitly directing worship
    # or reliance to others.  Require worship/help language in the reference and a
    # direct ``others/besides You/them`` target in the user text.
    if re.search(r'\b(?:you\s+alone|alone\s+we)\b.{0,55}\bworship\b|\bworship\b.{0,35}\byou\s+alone\b',r,re.I) and re.search(
        r'\bworship\b.{0,45}\b(?:others|other\s+gods?|besides\s+you|besides\s+allah|them)\b',u,re.I):
        return 'قُلِبت جهة العبادة مقارنة بالمرجع'

    # Explicit denial of a relation established by the trusted reference.  Keep this
    # conservative: require the same paired concepts on both sides, then a direct
    # ``nothing to do with`` denial in the user translation.
    if re.search(r'\bbeliev\w*\b',r,re.I) and re.search(r'\blov\w*\b',r,re.I) and re.search(
        r'\b(?:faith|belief|believing)\b.{0,45}\bnothing\s+to\s+do\s+with\b.{0,35}\blov\w*\b',u,re.I):
        return 'نُفيت العلاقة التي يثبتها المرجع بين الإيمان والمحبة'

    # Relationship to intentions: trusted reference states dependence/reward according
    # to intentions while the user makes intentions irrelevant or replaces the basis.
    if 'intention' in r and re.search(r'\b(?:depend|according)\b',r) and re.search(
        r'\b(?:irrelevant|unrelated|nothing\s+to\s+do|regardless\s+of|only\s+outward|depends?\s+on\s+(?:wealth|status|appearance))\b',u,re.I):
        return 'قُلِبت علاقة العمل بالنية مقارنة بالمرجع'

    # Abandoning a prohibited act vs doing/committing that prohibited act.
    if re.search(r'\b(?:abandon|avoid|leave)\w*\b.{0,55}\b(?:forbidden|prohibited)\b',r,re.I) and re.search(
        r'\b(?:do|does|commit|commits|practice|practices)\b.{0,55}\b(?:forbidden|prohibited)\b',u,re.I):
        return 'قُلِب ترك المنهي عنه إلى فعله مقارنة بالمرجع'

    # Trusted text affirms looking at hearts/deeds while user explicitly negates it
    # or reverses the contrast to bodies/forms.
    if re.search(r'\blooks?\b.{0,45}\b(?:hearts?|deeds?)\b',r,re.I) and (
        re.search(r'\b(?:does\s+not|doesn.t|never)\s+look\b.{0,55}\b(?:hearts?|deeds?)\b',u,re.I) or
        (re.search(r'\blooks?\b.{0,35}\b(?:bodies|forms|appearance)\b',u,re.I) and
         re.search(r'\bnot\b.{0,35}\b(?:hearts?|deeds?)\b',u,re.I))):
        return 'قُلِب موضع الاعتبار المذكور في المرجع'

    # Divine freedom from partners / rejection of associating partners versus explicit
    # need, acceptance, or approval of partners.  Requires partner language on both sides.
    if re.search(r'\b(?:free\s+from\s+(?:want\s+of\s+)?partners?|no\s+partners?|discard\w*).{0,90}\b(?:partners?|polytheism)\b|\bpolytheism\b',r,re.I) and re.search(
        r'\b(?:need|needs|accept|accepts|approve|approves)\b.{0,70}\b(?:partners?|polytheism|shared\s+worship)\b|\bpartners?\b.{0,50}\b(?:acceptable|accepted)\b',u,re.I):
        return 'قُلِبت علاقة الشرك/الشريك مقارنة بالمرجع'

    # Righteousness/sin role reversal.  Require both concepts in the trusted text so
    # ordinary positive/negative adjectives elsewhere cannot trigger it.
    if 'righteousness' in r and re.search(r'\bsin\b',r) and (
        re.search(r'\bgood\s+character\s+is\s+sin\b',u,re.I) or
        re.search(r'\bbad\s+character\s+is\s+righteousness\b',u,re.I) or
        re.search(r'\brighteousness\s+is\s+(?:bad|evil)\b',u,re.I)):
        return 'قُلِبت دلالة البر والإثم مقارنة بالمرجع'

    # Dislike concealment vs explicit desire/public approval.
    if re.search(r'\bdislike\w*\b.{0,60}\b(?:people|others)\b.{0,30}\b(?:know|see|learn)\b',r,re.I) and re.search(
        r'\b(?:want|wants|wish|wishes)\b.{0,55}\b(?:people|others)\b.{0,30}\b(?:know|see|learn)\b|\bopenly\s+admire\b',u,re.I):
        return 'قُلِبت دلالة إخفاء الإثم إلى طلب إظهاره مقارنة بالمرجع'
    # Ruin/failure versus explicit success/safety.
    if re.search(r'\b(?:ruined|destroyed|failed|failure)\b.{0,35}\bextremists?\b|\bextremists?\b.{0,25}\b(?:ruined|destroyed)\b',r,re.I) and re.search(
        r'\b(?:successful|safe|saved)\b.{0,35}\bextremists?\b|\bextremists?\b.{0,30}\b(?:successful|safe|saved)\b',u,re.I):
        return 'قُلِبت عاقبة الغلو مقارنة بالمرجع'

    # Harm/hardship receiving harm versus being rewarded/no consequence.
    if re.search(r'\bcauses?\s+(?:harm|hardship)\b',r,re.I) and re.search(
        r'\bcauses?\s+(?:harm|hardship)\b.{0,70}\b(?:rewarded|reward|no\s+consequence|without\s+consequence)\b',u,re.I):
        return 'قُلِبت عاقبة الإضرار مقارنة بالمرجع'

    # Trusted prohibition of punishment for the no-partners case vs explicit punishment.
    if re.search(r'\bshould\s+not\s+punish\b.{0,80}\bno\s+partners?\b',r,re.I) and re.search(
        r'\bshould\s+punish\b.{0,80}\bno\s+partners?\b',u,re.I):
        return 'قُلِب نفي العقوبة إلى إثباتها مقارنة بالمرجع'

    # Possibility of increasing good/abandoning evil vs an explicit impossibility.
    if re.search(r'\bmay\s+(?:do\s+more\s+good|give\s+up\s+evil)\b',r,re.I) and re.search(
        r'\b(?:cannot|can\s+not|never)\b.{0,45}\b(?:increase|more\s+good|give\s+up|abandon)\b',u,re.I):
        return 'قُلِبت إمكانية الزيادة في الخير أو ترك الشر مقارنة بالمرجع'

    return None

def _exclusivity_equivalent(ref,user):
    # Quranic/reference English may use ``not but`` while a faithful translation
    # uses the idiomatic ``is but`` or ``only``. These are not contradictions.
    if re.search(r'\bnot\s+but\s+(?:an?\s+)?([a-z-]+)',ref):
        noun=re.search(r'\bnot\s+but\s+(?:an?\s+)?([a-z-]+)',ref).group(1)
        return bool(re.search(rf'\b(?:is|are|was|were)\s+but\s+(?:an?\s+)?{re.escape(noun)}\b',user) or re.search(rf'\bonly\s+(?:an?\s+)?{re.escape(noun)}\b',user))
    return False


def analyze_reference_conflicts(ar_text,en_text,recognitions,evidence):
    # Use Mi'yar's grouped monotonic alignment rather than requiring identical
    # sentence counts.  A faithful translator may split one Arabic hadith/ayah into
    # two English clauses (or merge clauses); trusted-source comparison must still
    # inspect the aligned semantic unit instead of silently disabling itself.
    pairs,_align_mode=aligned_pairs(ar_text,en_text)
    if not pairs: return {'issues':[],'checks':[]}
    pairmap={idx:(ars,ens) for idx,ars,ens in pairs}
    byseg={}
    for ev in evidence:
        if ev.get('status')=='live_verified' and ev.get('segment_index') and ev.get('detail'):
            # Prefer English Quran translation / English hadith card.
            if ev.get('evidence_type')=='quran_translation' or ev.get('language')=='en':
                byseg[ev['segment_index']]=ev
    issues=[]; checks=[]
    for recwrap in recognitions or []:
        idx=recwrap.get('segment_index'); rec=recwrap.get('recognition') or {}
        if idx not in byseg or idx not in pairmap: continue
        arseg, enseg = pairmap[idx]
        full_ref=normalize_en(byseg[idx].get('detail','')); user=normalize_en(enseg); local=[]
        # Structured reference markers are metadata, not part of the translated
        # verse/hadith text. Remove a leading marker before comparing the user's
        # translation with the authoritative provider text.
        user_cmp=re.sub(r'^(?:quran_ref|hadith_ref)\s*:\s*[^\s]+\s*', '', user, flags=re.I).strip()
        # Hard safety invariant: an exact normalized copy of the authoritative
        # provider translation cannot contradict that same provider translation.
        # This guards long hadiths whose internal clause window contains local
        # negation that would otherwise be compared against the full user sentence.
        if full_ref and user_cmp == full_ref:
            checks.append({'check':f'مقارنة الترجمة بالمرجع المسترجع — المقطع {idx}','status':'pass','detail':'الترجمة مطابقة للنص المرجعي المسترجع'})
            continue
        ref=_reference_window(full_ref,user)
        relation_conflict=_trusted_relation_conflict(full_ref,user)
        if relation_conflict:
            local.append(_issue('reference_contradiction',relation_conflict,arseg,enseg,idx,
                                'الترجمة المدخلة تعكس علاقة دلالية يثبتها المرجع المسترجع الموثوق داخل المفاهيم نفسها.',
                                'هذا تعارض مباشر مع المعنى المرجعي وليس مجرد اختلاف في الصياغة.',
                                'critical',ref,enseg,.992,'trusted_reference_conflict'))
        ref_neg=bool(re.search(r'\b(?:not|neither|nor|no|never)\b',ref)); user_neg=bool(re.search(r'\b(?:not|neither|nor|no|never)\b',user))
        exclusive_ok=_exclusivity_equivalent(ref,user)
        # Direct polarity contradiction only after clause-level alignment. Require a
        # meaningful lexical anchor so a negation elsewhere in a long verse cannot
        # contaminate a correctly translated short clause.
        overlap=len(_content_tokens(ref) & _content_tokens(user))
        if ref_neg and not user_neg and not exclusive_ok and overlap and re.search(r'\b(?:has|have|was|is|are|born|children|greater|more than|begets?)\b',user):
            local.append(_issue('reference_contradiction','تعارض مباشر مع المرجع المسترجع',arseg,enseg,idx,'الترجمة المدخلة تقرر معنى مثبتًا بينما المقطع المرجعي المحاذي ينفيه.','تعارض الترجمة مع المرجع المعتمد يغيّر المعنى المنقول.', 'critical','المقطع المرجعي المحاذي',enseg,.99,'trusted_reference_conflict'))
        if re.search(r'\b(?:one|one,|one\[)\b',ref) and re.search(r'\b(?:among|one of)\s+(?:many|several)\b|\bmany gods\b|\bseveral gods\b',user):
            local.append(_issue('reference_contradiction','تعارض في معنى الوحدانية مع المرجع القرآني',arseg,enseg,idx,'المرجع المسترجع يثبت الوحدانية، بينما الترجمة تجعل المذكور واحدًا ضمن متعدد.','هذا قلب جوهري للمعنى المرجعي.', 'critical','One','one among many/several',.99,'trusted_reference_conflict'))
        if 'intention' in ref and re.search(r'\bnothing\s+to\s+do\s+with\s+intentions?\b',user):
            local.append(_issue('reference_contradiction','تعارض مع معنى الحديث المسترجع',arseg,enseg,idx,'المرجع المسترجع يربط الأعمال بالنيات، بينما الترجمة تنفي العلاقة.','يقلب المعنى المركزي للنص الحديثي.', 'critical','intentions','nothing to do with intentions',.99,'trusted_reference_conflict'))
        # Generic source-grounded polarity/root checks. These operate on the trusted
        # English reference for a recognized Quran/Hadith segment, not on isolated
        # keywords in the user translation.
        shared=_content_tokens(ref) & _content_tokens(user)
        ref_neg=bool(re.search(r'\b(?:not|no|never|neither|nor|without)\b',ref))
        user_neg=bool(re.search(r'\b(?:not|no|never|neither|nor|without)\b',user))
        if len(shared) >= 2 and ref_neg != user_neg and not exclusive_ok:
            local.append(_issue('reference_contradiction','انقلب اتجاه المعنى مقارنة بالمرجع المسترجع',arseg,enseg,idx,
                                'المقطع المرجعي الموثوق والترجمة المدخلة يختلفان في اتجاه النفي/الإثبات داخل نفس المعنى.',
                                'قد يقلب معنى النص القرآني أو الحديثي بدل مجرد تغيير الصياغة.', 'critical',ref,enseg,.985,'trusted_reference_conflict'))
        # Common antonymic polarity that may have little lexical overlap after translation.
        if re.search(r'\bno\s+compulsion\b',ref) and re.search(r'\b(?:must|should)\b.{0,40}\b(?:force|forced|compel|compelled)\b|\b(?:force|forced|compel|compelled)\b.{0,40}\breligion\b',user):
            local.append(_issue('reference_contradiction','قُلِب معنى نفي الإكراه في المرجع',arseg,enseg,idx,
                                'المرجع ينفي الإكراه، بينما الترجمة تقرر الإلزام أو الإجبار.',
                                'هذا قلب مباشر للمعنى المرجعي.', 'critical','no compulsion','must/forced',.995,'trusted_reference_conflict'))
        if 'intention' in ref and 'intention' in user and re.search(r'\b(?:do\s+not|does\s+not|regardless\s+of|unrelated\s+to)\b.{0,50}intentions?|intentions?.{0,40}\b(?:do\s+not|does\s+not)\b.{0,25}(?:affect|matter)',user):
            local.append(_issue('reference_contradiction','قُلِبت علاقة العمل بالنية في الحديث',arseg,enseg,idx,
                                'المرجع يربط العمل بالنية، بينما الترجمة تنفي هذه العلاقة أو تجعل العمل مستقلًا عنها.',
                                'يقلب المعنى المركزي للحديث.', 'critical','actions/intentions','regardless/not affect intentions',.995,'trusted_reference_conflict'))
        if re.search(r'\b(?:good|speak good|say what is good)\b',ref) and re.search(r'\bsilent|silence|remain silent|keep silent\b',ref) and re.search(r'\b(?:must|should)\s+always\s+(?:speak|talk)\b',user):
            local.append(_issue('reference_contradiction','قُلِب توجيه الحديث بين قول الخير والصمت',arseg,enseg,idx,
                                'المرجع يجعل الخيار قول الخير أو الصمت، بينما الترجمة تفرض الكلام دائمًا.',
                                'يلغي أحد طرفي التوجيه ويقلب نطاقه.', 'critical','say good or remain silent','must always speak',.995,'trusted_reference_conflict'))
        if re.search(r'\bnot\s+but\s+a\s+messenger\b',ref) and re.search(r'\b(?:more|greater)\s+than\b.*\bmessenger\b',user):
            local.append(_issue('reference_contradiction','قلب معنى الحصر في المرجع القرآني',arseg,enseg,idx,'المرجع يحصر الوصف في كونه رسولًا، بينما الترجمة تضيف معنى «أكثر من رسول».','يقلب بنية الحصر بدل مجرد حذف أداة.', 'critical','not but a messenger','more/greater than a messenger',.99,'trusted_reference_conflict'))
        issues.extend(local)
        checks.append({'check':f'مقارنة الترجمة بالمرجع المسترجع — المقطع {idx}','status':'fail' if local else 'pass','detail':'تعارض مباشر مع المرجع' if local else 'لا يظهر تعارض قاطع بعد محاذاة المقطع المرجعي'})
    return {'issues':issues,'checks':checks}
