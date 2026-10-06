from __future__ import annotations

import re
from functools import lru_cache

_UNIT_SPLIT_RE = re.compile(r"(?<=[.!?؟؛;])\s+|\n+")
_BLOCK_SPLIT_RE = re.compile(r"\n\s*\n+")

# Small bilingual anchors used only for alignment. They are deliberately broad,
# deterministic concepts (not religious verdicts) and therefore cannot create a
# user-facing finding by themselves. Their job is to stop a long-document shift.
_CONCEPTS = {
    "zakat": (["زكاة", "الزكاة", "زكاه"], ["zakat", "zakah", "almsgiving"]),
    "tawhid": (["توحيد", "التوحيد"], ["tawhid", "tawheed", "oneness"]),
    "wudu": (["وضوء", "الوضوء"], ["wudu", "wudhu", "ablution"]),
    "hajj": (["حج", "الحج"], ["hajj", "pilgrimage"]),
    "umrah": (["عمرة", "العمرة", "عمره"], ["umrah", "minor pilgrimage"]),
    "salah": (["صلاة", "الصلاة", "صلوات", "ركعة", "ركعات"], ["salah", "prayer", "prayers", "rakah", "rak'ah"]),
    "fasting": (["صيام", "الصيام", "صوم", "الصوم"], ["fasting", "fast"]),
    "shirk": (["شرك", "الشرك"], ["shirk", "polytheism"]),
    "charity": (["صدقة", "الصدقة", "صدقه"], ["sadaqah", "sadaqa", "charity"]),
    "source": (["مصدر", "المصدر", "مرجع", "المرجع"], ["source", "reference"]),
    "quran": (["قرآن", "القرآن", "سورة", "آية", "الاية", "الآية"], ["quran", "surah", "verse", "ayah"]),
    "hadith": (["حديث", "الحديث"], ["hadith"]),
    "condition": (["شرط", "بشرط", "إذا", "اذا", "إن"], ["condition", "if", "unless", "provided"]),
    "obligation": (["يجب", "وجب", "واجب", "يلزم", "فرض"], ["must", "required", "obligatory", "duty", "binding"]),
    "prohibition": (["لا يجوز", "يحرم", "حرام", "محرم", "ممنوع"], ["not permissible", "impermissible", "forbidden", "prohibited", "not allowed", "must not"]),
    "permission": (["يجوز", "مباح", "مسموح"], ["permissible", "allowed", "may"]),
    "review": (["مراجعة", "المراجعة", "مراجع"], ["review", "reviewer"]),
    "publish": (["نشر", "النشر"], ["publish", "publication"]),
    "confidence": (["ثقة", "الثقة"], ["confidence"]),
    "risk": (["خطر", "المخاطر", "مخاطر"], ["risk", "critical", "high", "medium", "low"]),
    "system": (["نظام", "النظام"], ["system"]),
    "evidence": (["دليل", "الدليل", "أدلة", "الادلة"], ["evidence"]),
    "scholars": (["علماء", "العلماء"], ["scholars"]),
}

_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _is_pure_structured_reference(block: str) -> bool:
    return bool(re.fullmatch(
        r"\s*\[(?:QURAN_REF|HADITH_REF|SOURCE_ID)\s*:[^\]]+\]\s*",
        block or "", re.I,
    ))


def _coalesce_reference_blocks(blocks: list[str]) -> list[str]:
    """Keep a multi-line citation packet as one alignment block.

    Editors often paste Arabic reference metadata in one paragraph while an English
    translation places each structured id on its own blank line.  Treating those as
    four unrelated paragraphs creates a permanent +3 shift.  This normalizer groups
    only an unmistakable run of structured reference blocks; it does not merge normal
    prose.
    """
    out=[]; i=0
    while i < len(blocks):
        if _is_pure_structured_reference(blocks[i]):
            j=i
            while j < len(blocks) and _is_pure_structured_reference(blocks[j]):
                j += 1
            if j-i >= 2:
                # A short explanatory metadata sentence immediately after a packet is
                # part of the same logical reference block (e.g. "the identifiers above").
                if j < len(blocks) and len(blocks[j]) <= 240 and re.search(
                    r"\b(?:identifier|identifiers|reference|references|source|sources)\b|(?:المعرفات|المعرّفات|المراجع|المصادر)",
                    blocks[j], re.I,
                ):
                    j += 1
                out.append("\n".join(blocks[i:j]))
                i=j
                continue
        out.append(blocks[i]); i += 1
    return out


def split_blocks(text: str) -> list[str]:
    """Split on real paragraph boundaries and normalize citation packets."""
    raw = (text or "").strip()
    if not raw:
        return []
    parts=[p.strip() for p in _BLOCK_SPLIT_RE.split(raw) if p and p.strip()]
    return _coalesce_reference_blocks(parts)



def split_units(text: str) -> list[str]:
    raw = (text or "").strip()
    if not raw:
        return []
    parts = [p.strip() for p in _UNIT_SPLIT_RE.split(raw) if p and p.strip()]
    # A leading numbered-list marker such as ``1.`` is metadata, not a sentence.
    # Keep it attached to the following unit so number detectors can strip it safely.
    merged = []
    i = 0
    while i < len(parts):
        if re.fullmatch(r"\d+[.)]?", parts[i]) and i + 1 < len(parts):
            merged.append(parts[i] + " " + parts[i + 1])
            i += 2
        else:
            merged.append(parts[i])
            i += 1
    return merged


def _norm(text: str) -> str:
    text = (text or "").translate(_AR_DIGITS).lower()
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = re.sub(r"[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06EDـ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _numbers(text: str) -> set[str]:
    t = _norm(text)
    return {m.group(0).replace(",", ".") for m in re.finditer(r"\d+(?:[.,]\d+)?%?", t)}


def _concepts(text: str, arabic: bool) -> set[str]:
    t = _norm(text)
    out = set()
    for key, (ars, ens) in _CONCEPTS.items():
        vals = ars if arabic else ens
        for value in vals:
            v = _norm(value)
            if arabic:
                if re.search(rf"(?<![\u0600-\u06FF]){re.escape(v)}(?![\u0600-\u06FF])", t):
                    out.add(key); break
            elif re.search(rf"\b{re.escape(v)}\b", t):
                out.add(key); break
    return out


def _ids(text: str) -> set[str]:
    # Explicit ids/references are excellent anchors even across languages.
    return {x.upper() for x in re.findall(r"\b(?:[A-Z][A-Z0-9_-]*-\d+|\d+\s*:\s*\d+)\b", text or "", re.I)}


@lru_cache(maxsize=8192)
def _signature(text: str, arabic: bool):
    return (frozenset(_concepts(text, arabic)), frozenset(_numbers(text)), frozenset(_ids(text)), max(1, len(_norm(text))))


@lru_cache(maxsize=32768)
def _pair_score(ar: str, en: str) -> float:
    """Fast alignment-only similarity in [0,1].

    It intentionally uses only deterministic cross-lingual anchors.  A low score is
    not a semantic-error verdict; it only tells the aligner not to force unrelated
    spans together.
    """
    if not ar or not en:
        return 0.0
    ac, an, ai, la = _signature(ar, True)
    ec, enm, ei, le = _signature(en, False)

    score = 0.0
    weight = 0.0
    if ac or ec:
        union = ac | ec
        score += 0.56 * (len(ac & ec) / max(1, len(union)))
        weight += 0.56
    if an or enm:
        union = an | enm
        score += 0.32 * (len(an & enm) / max(1, len(union)))
        weight += 0.32
        # Numbers are powerful anchors. A complete numeric mismatch should make a
        # forced pair less attractive, but must not itself create a user finding.
        if an and enm and not (an & enm):
            score -= 0.12
    if ai or ei:
        union = ai | ei
        score += 0.58 * (len(ai & ei) / max(1, len(union)))
        weight += 0.58
        if ai and ei and not (ai & ei):
            score -= 0.18

    ratio = min(la, le) / max(la, le)
    score += 0.08 * ratio
    weight += 0.08
    return max(0.0, min(1.0, score / max(weight, 1e-9)))

def _join(items: list[str], start: int, width: int) -> str:
    return " ".join(items[start:start + width]).strip()


def _semantic_monotonic_align(au: list[str], eu: list[str], max_merge: int = 2, gap_cost: float = 0.60, merge_penalty: float = 0.20) -> list[tuple[str, str, float]]:
    """Monotonic DP with local split/merge recovery.

    Supports 1:N and N:1 groups up to ``max_merge`` plus explicit gaps.  The DP is
    deliberately monotonic: translations may split/merge material, but later content
    cannot jump backwards to match an earlier paragraph.
    """
    n, m = len(au), len(eu)
    inf = float("inf")
    dp = [[inf] * (m + 1) for _ in range(n + 1)]
    prev = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    def relax(ni, nj, cost, pi, pj, action):
        if cost < dp[ni][nj]:
            dp[ni][nj] = cost
            prev[ni][nj] = (pi, pj, action)

    for i in range(n + 1):
        for j in range(m + 1):
            base = dp[i][j]
            if base == inf:
                continue
            if i < n and j < m:
                max_aw = min(max_merge, n - i)
                max_ew = min(max_merge, m - j)
                # Only one side may merge in a transition.  This is enough to recover
                # ordinary translation splits/merges and keeps the search stable.
                for aw in range(1, max_aw + 1):
                    ew = 1
                    a = _join(au, i, aw); e = eu[j]
                    sim = _pair_score(a, e)
                    relax(i+aw, j+1, base + (1.0-sim) + merge_penalty*(aw-1), i, j, (aw,1,sim))
                for ew in range(2, max_ew + 1):
                    a = au[i]; e = _join(eu, j, ew)
                    sim = _pair_score(a, e)
                    relax(i+1, j+ew, base + (1.0-sim) + merge_penalty*(ew-1), i, j, (1,ew,sim))
            if i < n:
                relax(i+1, j, base + gap_cost, i, j, (1,0,0.0))
            if j < m:
                relax(i, j+1, base + gap_cost, i, j, (0,1,0.0))

    actions=[]; i,j=n,m
    while i or j:
        item=prev[i][j]
        if item is None:
            if i: actions.append((1,0,0.0)); i-=1
            elif j: actions.append((0,1,0.0)); j-=1
            continue
        pi,pj,action=item; actions.append(action); i,j=pi,pj
    actions.reverse()

    out=[]; i=j=0
    for aw,ew,sim in actions:
        a=_join(au,i,aw) if aw else ""
        e=_join(eu,j,ew) if ew else ""
        out.append((a,e,sim)); i+=aw; j+=ew
    return out


def _paragraph_alignment(ar_text: str, en_text: str):
    ab, eb = split_blocks(ar_text), split_blocks(en_text)
    if len(ab) < 2 or len(eb) < 2:
        return None
    # Paragraphs are editorial anchors.  Allow a wider merge only here because
    # citations are often one Arabic paragraph but several English reference lines.
    raw = _semantic_monotonic_align(ab, eb, max_merge=4, gap_cost=0.74, merge_penalty=0.13)
    return raw


def aligned_pairs(ar_text: str, en_text: str) -> tuple[list[tuple[int, str, str]], str]:
    """Return robust Arabic↔English pairs while preserving the legacy API.

    Long documents use paragraph boundaries as hard editorial anchors after citation
    packet normalization.  If both sides then have the same block count, positional
    block alignment is substantially safer than a lexical scorer because Arabic and
    English may share almost no surface vocabulary.  Only genuinely unstructured or
    unequal-block documents fall back to sentence-level monotonic recovery.
    """
    ab, eb = split_blocks(ar_text), split_blocks(en_text)
    if len(ab) >= 2 and len(ab) == len(eb):
        return [(i,a,e) for i,(a,e) in enumerate(zip(ab,eb),1)], "hierarchical_paragraph_1to1"

    au, eu = split_units(ar_text), split_units(en_text)
    if not au or not eu:
        return [], "empty"
    if len(au) == len(eu):
        return [(i, a, e) for i, (a, e) in enumerate(zip(au, eu), 1)], "sentence_1to1"

    # If one language keeps the entire review unit as one sentence while the other
    # splits it into several sentences/clauses, there is only one monotonic semantic
    # choice: align the whole side to the whole other side.  Allowing DP gaps here can
    # create empty Arabic/English pairs and manufacture false findings on perfectly
    # faithful long Quran/Hadith translations.
    if len(au) == 1 and len(eu) > 1:
        return [(1, au[0], " ".join(eu))], "single_ar_grouped_en"
    if len(eu) == 1 and len(au) > 1:
        return [(1, " ".join(au), eu[0])], "grouped_ar_single_en"

    raw = _semantic_monotonic_align(au, eu, max_merge=3, gap_cost=0.64, merge_penalty=0.18)
    pairs = [(idx, a, e) for idx, (a, e, _sim) in enumerate(raw, 1)]
    mode = "monotonic_grouped_en" if len(au) < len(eu) else "monotonic_grouped_ar"
    return pairs, mode

