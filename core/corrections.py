from __future__ import annotations

import re
from typing import Any

from .normalization import normalize_ar
from .terminology import TERMS


_TERM_BY_AR = {t["ar"]: t for t in TERMS}
_UNIT_SPLIT_RE = re.compile(r"(?<=[.!?؟؛])\s+|\n+")
_MISSING = {"", "لا يوجد مقابل", "لا يوجد مقابل واضح", "—", "لا يوجد"}


def _unit_spans(text: str) -> list[tuple[int, int]]:
    """Return spans of sentence-like units while preserving the original text."""
    spans: list[tuple[int, int]] = []
    start = 0
    for match in _UNIT_SPLIT_RE.finditer(text or ""):
        end = match.start()
        if text[start:end].strip():
            left = start
            while left < end and text[left].isspace():
                left += 1
            right = end
            while right > left and text[right - 1].isspace():
                right -= 1
            spans.append((left, right))
        start = match.end()
    end = len(text or "")
    if (text or "")[start:end].strip():
        left = start
        while left < end and text[left].isspace():
            left += 1
        right = end
        while right > left and text[right - 1].isspace():
            right -= 1
        spans.append((left, right))
    return spans


def _render_replacement(original: str, new: str) -> str:
    if original[:1].isupper() and new[:1].islower():
        return new[:1].upper() + new[1:]
    return new


def _replace_once(text: str, old: str, new: str, segment_index: int | None = None) -> tuple[str, bool, str]:
    if not text or not old or old in _MISSING:
        return text, False, new

    search_start, search_end = 0, len(text)
    if segment_index:
        spans = _unit_spans(text)
        if 1 <= segment_index <= len(spans):
            search_start, search_end = spans[segment_index - 1]
        else:
            return text, False, new

    region = text[search_start:search_end]
    match = re.search(re.escape(old), region, flags=re.IGNORECASE)
    if not match:
        return text, False, new

    absolute_start = search_start + match.start()
    absolute_end = search_start + match.end()
    original = text[absolute_start:absolute_end]
    replacement = _render_replacement(original, new)
    return text[:absolute_start] + replacement + text[absolute_end:], True, replacement


def _replace_nth_once(text: str, old: str, new: str, segment_index: int | None, occurrence_index: int | None) -> tuple[str, bool, str]:
    """Replace the intended occurrence inside one aligned unit, never the first by default."""
    if not occurrence_index or occurrence_index < 1:
        return _replace_once(text, old, new, segment_index)
    if not text or not old or old in _MISSING:
        return text, False, new
    search_start, search_end = 0, len(text)
    if segment_index:
        spans=_unit_spans(text)
        if not (1 <= segment_index <= len(spans)):
            return text, False, new
        search_start,search_end=spans[segment_index-1]
    region=text[search_start:search_end]
    matches=list(re.finditer(re.escape(old),region,flags=re.IGNORECASE))
    if occurrence_index > len(matches):
        return text, False, new
    match=matches[occurrence_index-1]
    a=search_start+match.start(); b=search_start+match.end()
    original=text[a:b]; replacement=_render_replacement(original,new)
    return text[:a]+replacement+text[b:],True,replacement


def _append_clause(text: str, clause: str, segment_index: int | None = None) -> tuple[str, bool, str]:
    """Append a short, high-confidence missing clause to the relevant sentence."""
    if not text or not clause:
        return text, False, clause
    if re.search(re.escape(clause), text, flags=re.IGNORECASE):
        return text, False, clause

    start, end = 0, len(text)
    if segment_index:
        spans = _unit_spans(text)
        if not (1 <= segment_index <= len(spans)):
            return text, False, clause
        start, end = spans[segment_index - 1]

    segment = text[start:end]
    m = re.search(r"([.!?])\s*$", segment)
    insert_at = end - (len(m.group(0)) if m else 0)
    prefix = "" if text[:insert_at].endswith((" ", "\n")) else " "
    rewritten = text[:insert_at] + prefix + clause + text[insert_at:]
    return rewritten, True, clause


def _exception_clause(source_span: str, source_segment: str = "") -> str | None:
    """Translate only a small whitelist of explicit exception clauses.

    Mi'yar must not become a free-form translator. Auto-restoration therefore happens
    only for phrases whose English equivalent is unambiguous in this review context.
    """
    norm = normalize_ar(f"{source_span} {source_segment}")
    patterns = [
        (r"الا\s+لعذر\s+معتبر", "except for a valid excuse"),
        (r"الا\s+في\s+حالة\s+الضرورة", "except in a case of necessity"),
        (r"الا\s+عند\s+الضرورة", "except in cases of necessity"),
        (r"الا\s+لضرورة", "except in cases of necessity"),
        (r"الا\s+باذن", "except with permission"),
        (r"الا\s+في\s+حال\s+الحاجة", "except in case of need"),
    ]
    for pattern, english in patterns:
        if re.search(pattern, norm):
            return english
    return None


def _modality_replacement(issue: dict[str, Any]) -> str | None:
    title = str(issue.get("title", ""))
    # Use grammar-compatible modal tokens only. A blind replacement such as
    # ``must -> permissible`` creates broken English ("It permissible be done").
    mapping = {
        "من الإباحة إلى الإلزام": "may",
        "من الإلزام إلى الإباحة": "must",
        "من الاستحباب إلى الإلزام": "recommended",
        "من الإلزام إلى الاستحباب": "obligatory",
    }
    for phrase, replacement in mapping.items():
        if phrase in title:
            return replacement
    # Polarity flips such as prohibition <-> permission need phrase-level rewriting
    # (often insertion/removal of negation), so V5 never auto-fixes them by token swap.
    return None




def _replace_modality_safely(text: str, issue: dict[str, Any], replacement: str) -> tuple[str, bool, str]:
    """Apply only grammar-safe modal repairs inside one aligned segment."""
    old=str(issue.get("translation_span","") or "")
    seg=issue.get("segment_index")
    if replacement=="recommended" and old.lower()=="must":
        spans=_unit_spans(text)
        start,end=(0,len(text))
        if seg:
            if not (1 <= seg <= len(spans)):
                return text,False,replacement
            start,end=spans[seg-1]
        region=text[start:end]
        m=re.search(r"\bmust\s+be\s+done\b",region,flags=re.I)
        if not m:
            return text,False,replacement
        repl="is recommended to be done"
        a=start+m.start(); b=start+m.end()
        return text[:a]+repl+text[b:],True,repl
    return _replace_once(text,old,replacement,seg)

def build_high_confidence_correction(translation: str, issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return only atomic terminology substitutions that are safe to suggest.

    V15.2 deliberately does not auto-rewrite missing conditions/exceptions, ruling
    modality, negation or quantities. Those changes can require sentence-level
    reasoning and remain human-review tasks. The public UI shows suggestions only;
    it never mutates the user's translation automatically.
    """
    corrected = translation
    changes: list[dict[str, Any]] = []
    resolved_ids: set[int] = set()

    for idx, issue in enumerate(issues):
        if issue.get("type") != "flattening" or issue.get("severity") not in {"high", "critical"}:
            continue
        if issue.get("evidence_kind") not in {"official_glossary_guideline", "curated_terminology_rule"}:
            continue
        term = _TERM_BY_AR.get(str(issue.get("source_span", "")))
        if not term or not term.get("accepted"):
            continue
        old = str(issue.get("translation_span", "") or "")
        suggested = str(term["accepted"][0])
        segment_index = issue.get("segment_index")
        if not old or old in _MISSING or not suggested:
            continue

        # Only an isolated lexical problem is eligible. Any other meaningful issue in
        # the same sentence makes even a correct term substitution insufficient.
        if segment_index is not None:
            blockers=[x for j,x in enumerate(issues) if j!=idx and x.get("segment_index")==segment_index and x.get("severity") in {"medium","high","critical"}]
            if blockers:
                continue
            spans=_unit_spans(corrected)
            if not (1 <= segment_index <= len(spans)):
                continue
            a,b=spans[segment_index-1]
            segment_text=corrected[a:b]
            if re.search(rf"\b{re.escape(suggested)}\b", segment_text, flags=re.IGNORECASE):
                continue
        else:
            # Single-unit input: any other meaningful issue belongs to the same sentence.
            blockers=[x for j,x in enumerate(issues) if j!=idx and x.get("severity") in {"medium","high","critical"}]
            if blockers:
                continue

        corrected_next, changed, rendered = _replace_nth_once(
            corrected, old, suggested, segment_index, issue.get("translation_occurrence_index")
        )
        if not changed:
            continue
        changes.append({
            "kind":"terminology",
            "issue_title":issue.get("title","تصحيح مصطلحي"),
            "source":term["ar"], "from":old, "to":rendered,
            "reason":term["guide"], "segment_index":segment_index,
            "source_segment":issue.get("source_segment") or issue.get("source_span", ""),
            "translation_segment":issue.get("translation_segment") or issue.get("translation_span", ""),
        })
        corrected=corrected_next
        resolved_ids.add(idx)

    if not changes or corrected == translation:
        return None
    unresolved=[issue for idx,issue in enumerate(issues) if idx not in resolved_ids]
    return {
        "corrected_text":corrected,
        "changes":changes,
        "safe_to_apply":True,
        "resolved_issue_count":len(resolved_ids),
        "total_issue_count":len(issues),
        "unresolved_issue_count":len(unresolved),
        "unresolved_titles":[str(x.get("title","موضع يحتاج مراجعة")) for x in unresolved],
        "unresolved_issues":unresolved,
        "resolved_issue_indices":sorted(resolved_ids),
        "note":"اقتُرحت فقط استبدالات مصطلحية ذرّية عالية الثقة؛ ولا يعيد مِعيار صياغة القيود أو الأحكام أو الأرقام آليًا.",
    }
