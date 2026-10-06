import re, unicodedata

AR_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]")


def normalize_ar(text):
    text = unicodedata.normalize("NFKC", text or "")
    text = AR_DIACRITICS.sub("", text).replace("ـ", "")
    text = re.sub(r"[إأآٱ]", "ا", text).replace("ى", "ي")
    return re.sub(r"\s+", " ", text).strip()



def normalize_ar_preserve_hamza(text):
    """Normalize Arabic spacing/diacritics while preserving أ/إ/آ/ا distinctions.

    Structural grammar checks use this before any hamza folding so conditional «إن»
    cannot be confused with المصدرية «أن».
    """
    text = unicodedata.normalize("NFKC", text or "")
    text = AR_DIACRITICS.sub("", text).replace("ـ", "").replace("ى", "ي")
    return re.sub(r"\s+", " ", text).strip()


def normalize_en(text):
    text = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"\s+", " ", text).strip()


def tokens_ar(text):
    return re.findall(r"[\u0600-\u06FF]+|\d+(?:\.\d+)?", normalize_ar(text))


def tokens_en(text):
    return re.findall(r"[a-zA-Z][a-zA-Z'-]*|\d+(?:\.\d+)?", normalize_en(text))


# Canonical number words used to catch quantity drift even when one side spells the
# number out. The map is intentionally bounded to common editorial / religious cases
# rather than pretending to be a full arithmetic parser.
AR_NUMBER_WORDS = {
    "صفر": 0,
    "واحد": 1, "واحده": 1, "واحدا": 1, "واحدهً": 1,
    "اثنان": 2, "اثنين": 2, "اثنتان": 2, "اثنتين": 2, "اثنانِ": 2,
    "ثلاث": 3, "ثلاثه": 3, "ثلاثة": 3, "ثلاثا": 3,
    "اربع": 4, "اربعه": 4, "اربعة": 4,
    "خمس": 5, "خمسه": 5, "خمسة": 5,
    "ست": 6, "سته": 6, "ستة": 6,
    "سبع": 7, "سبعه": 7, "سبعة": 7, "سبعا": 7,
    "ثمان": 8, "ثماني": 8, "ثمانيه": 8, "ثمانية": 8,
    "تسع": 9, "تسعه": 9, "تسعة": 9,
    "عشر": 10, "عشره": 10, "عشرة": 10,
    "احد عشر": 11, "احد عشره": 11, "احدي عشر": 11, "احدي عشره": 11,
    "اثنا عشر": 12, "اثني عشر": 12, "اثنتا عشره": 12, "اثنتي عشره": 12,
    "ثلاثه عشر": 13, "ثلاث عشره": 13,
    "اربعه عشر": 14, "اربع عشره": 14,
    "خمسه عشر": 15, "خمس عشره": 15,
    "سته عشر": 16, "ست عشره": 16,
    "سبعه عشر": 17, "سبع عشره": 17,
    "ثمانيه عشر": 18, "ثماني عشره": 18,
    "تسعه عشر": 19, "تسع عشره": 19,
    "عشرون": 20, "عشرين": 20,
    "ثلاثون": 30, "ثلاثين": 30,
    "اربعون": 40, "اربعين": 40,
    "خمسون": 50, "خمسين": 50,
    "ستون": 60, "ستين": 60,
    "سبعون": 70, "سبعين": 70,
    "ثمانون": 80, "ثمانين": 80,
    "تسعون": 90, "تسعين": 90,
    "مئه": 100, "مائه": 100, "مائة": 100,
}

EN_NUMBER_WORDS = {
    "zero": 0,
    "once": 1, "twice": 2, "thrice": 3,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
    "ninety": 90, "hundred": 100,
}


def _strip_list_markers(text):
    return re.sub(r"(?m)^\s*\d+\s*[\.\)\-:]\s+", "", text)


def _numeric_literals(text):
    t = (text or "").translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    t = _strip_list_markers(t)
    return re.findall(r"\d+(?:[.,]\d+)?%?", t)


def _word_numbers(text):
    raw = text or ""
    ar = normalize_ar(raw)
    en = normalize_en(raw)
    out = []

    # Longest phrases first to avoid counting «عشر» inside «احد عشر».
    occupied = []
    for phrase, value in sorted(AR_NUMBER_WORDS.items(), key=lambda kv: len(kv[0]), reverse=True):
        # Arabic number words often take a one-letter proclitic without a space
        # (e.g. «لثلاث فئات», «بسبعة أيام», «وثلاثة أشهر»).  Treat that clitic
        # as syntax around the number rather than as part of the lexical token.
        pat = rf"(?<![\u0600-\u06FF])(?:[وفبكل])?{re.escape(phrase)}(?![\u0600-\u06FF])"
        for m in re.finditer(pat, ar):
            if any(a <= m.start() < b or a < m.end() <= b for a, b in occupied):
                continue
            occupied.append((m.start(), m.end()))
            out.append((m.start(), str(value)))

    base = len(ar) + 1
    for phrase, value in sorted(EN_NUMBER_WORDS.items(), key=lambda kv: len(kv[0]), reverse=True):
        for m in re.finditer(rf"\b{re.escape(phrase)}\b", en):
            out.append((base + m.start(), str(value)))

    return [v for _, v in sorted(out, key=lambda x: x[0])]



AR_FRACTIONS = {
    "نصف": "1/2", "النصف": "1/2", "ثلث": "1/3", "الثلث": "1/3",
    "ربع": "1/4", "الربع": "1/4", "ثلثان": "2/3", "ثلثين": "2/3",
}
EN_FRACTIONS = {"half":"1/2", "one half":"1/2", "a half":"1/2", "third":"1/3", "one third":"1/3", "a third":"1/3", "quarter":"1/4", "one quarter":"1/4"}

def _fraction_numbers(text):
    ar=normalize_ar(text); en=normalize_en(text); out=[]
    # Longest-match + occupied spans prevents ``one third`` from also being
    # counted again as the nested token ``third``.
    occupied_ar=[]
    for k,v in sorted(AR_FRACTIONS.items(), key=lambda kv: len(kv[0]), reverse=True):
        for m in re.finditer(rf"(?<![\u0600-\u06FF])(?:[وفبكل])?{re.escape(k)}(?![\u0600-\u06FF])", ar):
            sig=(m.start(),m.end())
            if any(not (sig[1] <= a or sig[0] >= b) for a,b in occupied_ar):
                continue
            occupied_ar.append(sig); out.append((m.start(),v))
    base=len(ar)+1; occupied_en=[]
    for k,v in sorted(EN_FRACTIONS.items(), key=lambda kv: len(kv[0]), reverse=True):
        for m in re.finditer(rf"\b{re.escape(k)}\b", en):
            sig=(m.start(),m.end())
            if any(not (sig[1] <= a or sig[0] >= b) for a,b in occupied_en):
                continue
            occupied_en.append(sig); out.append((base+m.start(),v))
    return [v for _,v in sorted(out)]

def _dual_quantities(text):
    ar=normalize_ar(text); out=[]
    # Conservative list of common count-bearing duals used in editorial/religious prose.
    stems=["حالت","مرت","ركعت","يوم","شهر","فئت","ساعت"]
    for stem in stems:
        pat=rf"(?<![\u0600-\u06FF])(?:[وفبكل])?{stem}(?:ان|ين)(?![\u0600-\u06FF])"
        for m in re.finditer(pat,ar): out.append((m.start(),"2"))
    return [v for _,v in sorted(out)]

def numbers(text):
    """Return canonical quantities, including common spelled-out numbers.

    This is intentionally a comparison aid, not a general number parser. It catches
    high-value mismatches such as «ثلاث» ↔ ``four`` while avoiding list numbering.
    """
    literals = _numeric_literals(text)
    words = _word_numbers(text)
    fractions = _fraction_numbers(text)
    duals = _dual_quantities(text)
    # Preserve multiplicity and order. Deduplicate only identical values introduced by overlapping lexical detectors.
    # A lexical fraction such as ``one third`` is one quantity, not the two
    # independent quantities ``1`` and ``1/3``. Remove the component ``1`` that
    # the ordinary word-number detector saw inside the fraction phrase.
    en = normalize_en(text)
    component_ones = sum(len(re.findall(rf"\b{re.escape(p)}\b", en)) for p in ("one half","one third","one quarter"))
    if component_ones:
        kept=[]
        for v in words:
            if v == "1" and component_ones:
                component_ones -= 1
                continue
            kept.append(v)
        words=kept

    vals = literals + words + fractions + duals
    return vals
