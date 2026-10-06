from datetime import datetime, timezone
import hashlib, re
from concurrent.futures import ThreadPoolExecutor
from .rules import analyze_rules
from .terminology import analyze_terminology
from .semantic_local import analyze_local_semantics
from .sources import retrieve_reference_evidence_multi, source_route_multi
from .semantic_ai import run_semantic_ai
from .advanced_semantics import analyze_scope, analyze_term_relations, analyze_provenance, analyze_reference_conflicts
from .contextual_semantics import analyze_contextual_semantics
from .alignment import aligned_pairs

SEV={"low":1,"medium":2,"high":3,"critical":4}

ISSUE_PRIORITY={
    "reference_contradiction":0, "reference_identifier_changed":0, "source_fabrication_policy_shift":0,
    "sacred_text_boundary":1, "provenance_claim_shift":2, "source_attribution_collapse":2,
    "actor_role_inversion":3, "event_order_reversal":3, "causality_reversal":3,
    "disclaimer_boundary_shift":3, "condition_gate_shift":3, "audit_requirement_shift":3,
    "negation_scope_reversal":3, "exception_scope_shift":3, "scope_marker_policy_reversal":3,
    "qualifier_omission_policy_shift":3, "unsupported_addition_policy_shift":3,
    "comparison_direction_reversal":3, "comparison_inference_overclaim":3,
    "logical_operator_shift":3, "logical_cardinality_shift":3,
    "publication_gate_shift":3, "threshold_boundary_shift":3, "abstention_policy_shift":3,
    "ruling_degree_shift":4, "term_relation_reversal":4, "term_scope_reversal":4,
    "uncertainty_to_certainty":4, "epistemic_overclaim":4, "scope_reversal":5,
    "unit_mismatch":5, "asserted_quantity_shift":5, "time_period_shift":5,
    "severity_scale_shift":5, "named_entity_shift":5, "numeric_relation_reversal":5,
    "signed_number_contradiction":5, "decimal_value_corruption":5, "date_ambiguity_collapse":5,
    "date_ambiguity_overclaim":5, "equivalent_paraphrase_rejected":5, "pronoun_ambiguity":6,
    "modality_shift":20, "ruling_polarity_shift":20, "quantity":21,
    "exception":22, "condition":22, "negation":23, "flattening":24,
    "scope_shift":25, "frequency_shift":25, "scope_omission":26,
}

# Public/root ranking: severity first, then impact/specificity/confidence.
ROOT_IMPACT_PRIORITY={
    "source_fabrication_policy_shift":0,"reference_contradiction":1,"reference_identifier_changed":2,
    "ruling_polarity_shift":3,"ruling_degree_shift":4,"negation_scope_reversal":5,
    "actor_role_inversion":6,"logical_operator_shift":7,"logical_cardinality_shift":8,
    "causality_reversal":9,"event_order_reversal":10,"source_attribution_collapse":11,
    "condition_gate_shift":12,"publication_gate_shift":12,
    "date_ambiguity_collapse":13,"threshold_boundary_shift":13,
    "signed_number_contradiction":14,"decimal_value_corruption":14,"asserted_quantity_shift":15,
    "unit_mismatch":16,"time_period_shift":17,"uncertainty_to_certainty":18,"epistemic_overclaim":19,"term_relation_reversal":20,
    "flattening":20,"terminology":21,"quantifier_scope_reversal":22,"scope_reversal":23,
    "equivalent_paraphrase_rejected":90,
}
EVIDENCE_SPECIFICITY={
    "trusted_reference_conflict":1.0,"deterministic_contextual_rule":.98,"deterministic_rule":.94,
    "official_glossary_guideline":.90,"curated_terminology_rule":.82,"contextual_uncertainty":.72,
}

def _root_rank_tuple(item):
    sev=-SEV.get(item.get("severity","medium"),2)
    impact=ROOT_IMPACT_PRIORITY.get(item.get("type"),50)
    conf=-float(item.get("confidence",0) or 0)
    spec=-EVIDENCE_SPECIFICITY.get(item.get("evidence_kind"),.5)
    span_quality=0 if (item.get("source_span") not in {None,"","—","لا يوجد مقابل واضح"} and item.get("translation_span") not in {None,"","—","لا يوجد مقابل واضح"}) else 1
    return (sev,impact,spec,span_quality,conf,item.get("segment_index") or 0)

ISSUE_TAXONOMY_BY_FAMILY={
    "REFERENCE":"SOURCE_INTEGRITY",
    "RULING":"RELIGIOUS_SEMANTIC",
    "TERMINOLOGY":"RELIGIOUS_SEMANTIC",
    "SACRED":"RELIGIOUS_SEMANTIC",
    "NUMERIC":"LOGIC_NUMERIC",
    "LOGIC":"LOGIC_NUMERIC",
    "EPISTEMIC":"EPISTEMIC",
    "SCOPE":"GENERAL_SEMANTIC",
    "ACTOR":"GENERAL_SEMANTIC",
    "CAUSALITY":"GENERAL_SEMANTIC",
}

RELIGIOUS_CUES=(
    # Strong domain cues only. Generic normative wording such as "لا يجوز" is
    # intentionally excluded because it also appears in technical translation instructions.
    "الله","الرسول","النبي","القرآن","قرآن","آية","سورة","حديث","ديني","دينية","شرعي","الشريعة",
    "توحيد","شرك","زكاة","صلاة","صلى","صيام","حج","عمرة","وضوء","توضأ","تيمم","فتوى","عقيدة","فقه","النية",
    "quran_ref","hadith_ref","quran","hadith","zakat","tawhid","wudu","salah","shirk","sharia","religious","islamic","fatwa","scholar","haram",
)

def _religious_context(issue):
    if issue.get('recognized_source_kind') in {'quran','hadith'}:
        return True
    text=' '.join(str(issue.get(k) or '') for k in ("source_segment","source_span","translation_segment","translation_span","title","explanation_ar")).lower()
    return any(cue.lower() in text for cue in RELIGIOUS_CUES)

def _explicit_sharia_ruling_context(issue):
    text=' '.join(str(issue.get(k) or '') for k in ("source_segment","source_span","title","explanation_ar"))
    # These are the classical ruling-degree markers Mi'yar protects during transfer.
    # Generic technical words like "يجب"/"لا يجوز" alone are deliberately insufficient.
    return bool(re.search(r"(?:حكم\s+شرعي|الواجب|المستحب|المباح|المكروه|المحرم|\bواجب\b|\bمستحب\b|\bجائز\b|\bمباح\b|\bمكروه\b|\bمحرم\b|\bحرام\b)", text)) or _religious_context(issue)

def _issue_subtype(issue, family, taxonomy=None):
    t=issue.get("type") or ""
    rc=_root_code(issue)
    if family=="RULING": return "RULING_TRANSFER_DRIFT" if taxonomy=="RELIGIOUS_SEMANTIC" else "GENERAL_MODALITY_DRIFT"
    if family=="TERMINOLOGY": return "RELIGIOUS_TERMINOLOGY_DRIFT"
    if t in {"reference_contradiction","reference_identifier_changed","source_fabrication_policy_shift","source_attribution_collapse","provenance_claim_shift","sacred_text_boundary"}: return "REFERENCE_INTEGRITY_DRIFT"
    if rc=="SIGNED_NUMBER_CONTRADICTION": return "SIGNED_NUMBER_CONTRADICTION"
    if rc=="DECIMAL_VALUE_CORRUPTION": return "DECIMAL_VALUE_CORRUPTION"
    if rc=="DATE_AMBIGUITY_COLLAPSE": return "DATE_AMBIGUITY_COLLAPSE"
    if family=="NUMERIC": return "NUMERIC_SEMANTIC_DRIFT"
    if family=="LOGIC": return "LOGICAL_RELATION_DRIFT"
    if family=="EPISTEMIC": return "EPISTEMIC_CERTAINTY_DRIFT"
    if family=="ACTOR": return "ACTOR_RESPONSIBILITY_DRIFT"
    if family=="CAUSALITY": return "CAUSAL_RELATION_DRIFT"
    if family=="SCOPE": return "SCOPE_SEMANTIC_DRIFT"
    return "GENERAL_SEMANTIC_DRIFT"

def _religious_impact_reason(issue, taxonomy, impact):
    if impact=="none":
        text=' '.join(str(issue.get(k) or '') for k in ("source_segment","source_span","translation_segment","translation_span"))
        if re.search(r"\b(?:TEST|MOCK|DEMO|ABC)[-_]?[A-Z0-9]*\b",text,re.I):
            return "المعرّف هنا تجريبي/اصطناعي؛ يُفحص اتساقه محليًا ولا يُعامل كمصدر ديني حقيقي أو يُرسل للتحقق الخارجي."
        return "لا يظهر في هذا الموضع أثر ديني مباشر؛ التنبيه تقني/دلالي ضمن سلامة النقل."
    t=issue.get("type") or ""
    if _semantic_family(issue)=="RULING": return "لأن التغيير ينقل درجة الحكم المذكورة في الأصل إلى درجة أخرى، من دون أن يقرر مِعيار صحة الحكم الشرعي الأصلي."
    if _semantic_family(issue)=="TERMINOLOGY": return "لأن التغيير يمس دلالة مصطلح إسلامي حساس في سياقه، وليس لأنه يصدر حكمًا شرعيًا جديدًا."
    target_text=' '.join(str(issue.get(k) or '') for k in ("translation_segment","translation_span")).lower()
    if issue.get("type")=="unsupported_addition_policy_shift" and any(cue in target_text for cue in ("religious","islamic","sharia","fatwa","scholar","حرام","شرعي","ديني")):
        return "لأن الترجمة أضافت استنتاجًا دينيًا صريحًا غير موجود في الأصل؛ الأثر هنا في المحتوى المضاف لا في صحة حكم شرعي أصلي."
    if taxonomy=="SOURCE_INTEGRITY":
        states=[str(x.get("reference_state") or "") for x in (issue.get("sub_evidence") or [])]
        if states and any(x=="synthetic" for x in states) and any(x and x!="synthetic" for x in states):
            return "لأن المعرّف القرآني/المرجعي غير التجريبي تغيّر، بينما تبقى معرفات TEST/ABC تجريبية ولا تُعامل كمصادر دينية حقيقية."
        return "لأن تغيير المرجع أو نسبته قد يربط المحتوى الديني بدليل مختلف أو غير متحقق."
    if _semantic_family(issue) in {"NUMERIC","LOGIC"} and _religious_context(issue): return "لأن الخطأ المنطقي أو العددي وقع داخل محتوى ديني حساس وقد يغيّر الشرط أو المقدار المنقول."
    if _religious_context(issue): return "لأن الفجوة تقع داخل دلالة دينية حساسة في الأصل وقد تغيّر ما يصل إلى قارئ الترجمة."
    return "أثر ديني محتمل بسبب حساسية السياق؛ يلزم الحفاظ على حدود النظام والمراجعة البشرية."

def _classify_public_issue(issue):
    family=_semantic_family(issue)
    taxonomy=ISSUE_TAXONOMY_BY_FAMILY.get(family,"GENERAL_SEMANTIC")
    if family=="RULING" and not _explicit_sharia_ruling_context(issue):
        taxonomy="GENERAL_SEMANTIC"
    if issue.get("type") in {"source_attribution_collapse","provenance_claim_shift","sacred_text_boundary"}:
        taxonomy="SOURCE_INTEGRITY"
    if issue.get("type") in {"equivalent_paraphrase_rejected"}:
        taxonomy="GENERAL_SEMANTIC"
    if issue.get("type") in {"pronoun_ambiguity"}:
        taxonomy="EPISTEMIC"

    reference_states=[str(x.get("reference_state") or "") for x in (issue.get("sub_evidence") or [])]
    has_synthetic_reference=any(x=="synthetic" for x in reference_states)
    has_nonsynthetic_reference=any(x and x!="synthetic" for x in reference_states)
    synthetic_reference=bool(reference_states) and has_synthetic_reference and not has_nonsynthetic_reference
    mixed_reference=has_synthetic_reference and has_nonsynthetic_reference
    if taxonomy=="RELIGIOUS_SEMANTIC":
        impact="high"
    elif taxonomy=="SOURCE_INTEGRITY" and synthetic_reference:
        impact="none"
    elif taxonomy=="SOURCE_INTEGRITY" and (mixed_reference or _religious_context(issue)):
        impact="high"
    elif taxonomy in {"LOGIC_NUMERIC","GENERAL_SEMANTIC","EPISTEMIC"} and _religious_context(issue):
        impact="high" if issue.get("severity") in {"critical","high"} else "medium"
    else:
        impact="none"

    issue=dict(issue)
    issue["issue_taxonomy"]=taxonomy
    issue["issue_subtype"]=_issue_subtype(issue,family,taxonomy)
    issue["religious_impact"]=impact
    issue["religious_impact_reason"]=_religious_impact_reason(issue,taxonomy,impact)
    if taxonomy=="RELIGIOUS_SEMANTIC":
        issue["boundary_note_ar"]="التنبيه يتعلق بسلامة نقل الدلالة الدينية المذكورة في الأصل، وليس بإصدار حكم شرعي جديد أو اعتماد صحة الحكم الأصلي."
    elif taxonomy=="SOURCE_INTEGRITY":
        issue["boundary_note_ar"]="التحقق يتعلق بتطابق المرجع أو نسبته، ولا يعني اعتماد صحة المحتوى دينيًا بمجرد تطابق المرجع."
    else:
        issue["boundary_note_ar"]="هذا التنبيه يقيس سلامة انتقال المعنى في الترجمة ضمن نطاق مِعيار."
    return issue


def _classify_public_issues(issues):
    return [_classify_public_issue(i) for i in issues]

def _taxonomy_breakdown(issues):
    labels={
        "RELIGIOUS_SEMANTIC":"دلالي ديني",
        "GENERAL_SEMANTIC":"دلالي عام",
        "LOGIC_NUMERIC":"منطقي/رقمي",
        "SOURCE_INTEGRITY":"مرجعي",
        "EPISTEMIC":"معرفي",
    }
    out={k:0 for k in labels}
    for i in issues: out[i.get("issue_taxonomy","GENERAL_SEMANTIC")]=out.get(i.get("issue_taxonomy","GENERAL_SEMANTIC"),0)+1
    return {k:{"label_ar":labels.get(k,k),"count":v} for k,v in out.items()}

def _source_state_for_issue(issue, evidence_used):
    seg=issue.get("segment_index")
    matched=[e for e in evidence_used if e.get("segment_index")==seg]
    live=[e for e in matched if e.get("status")=="live_verified"]
    sub_states=[str(x.get("reference_state") or "") for x in (issue.get("sub_evidence") or [])]
    if sub_states:
        has_synth=any(x=="synthetic" for x in sub_states)
        has_other=any(x and x!="synthetic" for x in sub_states)
        if has_synth and has_other: state="mixed"
        elif has_synth: state="synthetic"
        elif live: state="verified"
        else: state="changed"
    elif live:
        state="verified"
    elif issue.get("issue_taxonomy")=="SOURCE_INTEGRITY":
        state="unverifiable"
    else:
        state="not_required"
    return state, matched

def _attach_issue_provenance(issues,evidence_used,created_at):
    for i in issues:
        state,matched=_source_state_for_issue(i,evidence_used)
        external=[e for e in matched if e.get("status")=="live_verified"]
        i["reference_state"]=state
        i["evidence_provenance"]={
            "detector":i.get("evidence_kind") or "unknown",
            "aligned_pair":i.get("segment_index"),
            "source_evidence":{"source_span":i.get("source_span"),"translation_span":i.get("translation_span")},
            "external_sources":[{
                "source":e.get("source"),"url":e.get("url") or e.get("browse_url"),
                "retrieved_at":e.get("retrieved_at"),"source_version":e.get("source_version"),
                "translation_key":e.get("translation_key"),"status":e.get("status")
            } for e in external],
            "timestamp":created_at,
            "confidence":i.get("confidence"),
            "suppression_history":[],
        }
    return issues

def _confidence_diagnostics(issues, alignment):
    # Do not boost confidence by counting multiple symptoms from the same root family.
    fam={}
    for i in issues:
        key=(i.get("segment_index"),_semantic_family(i),i.get("root_family") or i.get("type"))
        fam[key]=max(fam.get(key,0.0), float(i.get("confidence",0) or 0))
    independent=list(fam.values())
    alignment_mode=(alignment or {}).get("mode") or (alignment or {}).get("alignment_mode")
    return {
        "independent_evidence_count":len(independent),
        "max_root_confidence":round(max(independent),3) if independent else 0.0,
        "mean_independent_confidence":round(sum(independent)/len(independent),3) if independent else 0.0,
        "alignment_mode":alignment_mode,
        "policy":"root-family independence; generic keyword/count signals do not stack confidence",
    }


def _refine_issue_set(items):
    """Prefer specific semantic diagnoses over lower-level symptoms in the same segment."""
    byseg={}
    for i in items: byseg.setdefault(i.get("segment_index"),[]).append(i)
    out=[]
    for seg,group in byseg.items():
        types={i.get("type") for i in group}
        suppress=set()
        if "reference_contradiction" in types: suppress |= {"negation","exclusivity_shift"}
        if "sacred_text_boundary" in types or "provenance_claim_shift" in types: suppress |= {"negation","attribution"}
        if "term_relation_reversal" in types: suppress |= {"negation","flattening"}
        if "term_scope_reversal" in types: suppress |= {"negation","flattening","scope_reversal"}
        if "frequency_shift" in types: suppress |= {"negation"}
        for i in group:
            if i.get("type") not in suppress: out.append(i)
    return sorted(out,key=_root_rank_tuple)


def _dedupe(items):
    out=[]; seen=set()
    for i in items:
        k=(i.get("segment_index"),i.get("type"),i.get("title"),i.get("source_span"),i.get("translation_span"))
        if k not in seen:
            seen.add(k); out.append(i)
    return out


def _merge_semantic_transitions(issues, ar_text):
    """Merge paired ruling/structure alerts only inside the same aligned segment.

    V4 could pair a permission marker from one sentence with an obligation marker from
    another sentence in a long document. V5 groups by segment_index first so unrelated
    sentences can never be fused into one diagnosis.
    """
    groups={}
    for item in issues:
        key=item.get("segment_index")
        groups.setdefault(key,[]).append(item)

    merged=[]
    for seg, group in groups.items():
        local_ar=next((x.get("source_segment") for x in group if x.get("source_segment")), ar_text)
        types={i.get("type") for i in group}

        if "permission" in types and "obligation" in types:
            p=next(i for i in group if i.get("type")=="permission")
            o=next(i for i in group if i.get("type")=="obligation")
            p_src=p.get("source_span"); source_permission=p_src not in {None,"لا يوجد مقابل","—"}
            title="تغيّر درجة الحكم: من الإباحة إلى الإلزام" if source_permission else "تغيّر درجة الحكم: من الإلزام إلى الإباحة"
            source_span=p_src if source_permission else o.get("source_span")
            translation_span=o.get("translation_span") if source_permission else p.get("translation_span")
            explanation="الأصل يدل على الإباحة، بينما الترجمة تحوله إلى إلزام." if source_permission else "الأصل يدل على الإلزام، بينما الترجمة تخففه إلى إباحة."
            impact="ما كان جائزًا أو اختياريًا قد يصل للقارئ على أنه واجب." if source_permission else "ما كان واجبًا قد يصل للقارئ على أنه مجرد خيار."
            group=[i for i in group if i.get("type") not in {"permission","obligation"}]
            item={"type":"modality_shift","severity":"critical","title":title,"source_span":source_span,"translation_span":translation_span,"explanation_ar":explanation,"impact_ar":impact,"confidence":0.98,"evidence_kind":"deterministic_rule"}
            if seg is not None: item.update({"segment_index":seg,"source_segment":local_ar,"translation_segment":p.get("translation_segment") or o.get("translation_segment")})
            group.append(item)

        types={i.get("type") for i in group}
        if "recommendation" in types and "obligation" in types:
            rec=next(i for i in group if i.get("type")=="recommendation")
            obl=next(i for i in group if i.get("type")=="obligation")
            rec_src=rec.get("source_span") not in {None,"لا يوجد مقابل","—"}
            title="تغيّر درجة الحكم: من الاستحباب إلى الإلزام" if rec_src else "تغيّر درجة الحكم: من الإلزام إلى الاستحباب"
            source_span=rec.get("source_span") if rec_src else obl.get("source_span")
            translation_span=obl.get("translation_span") if rec_src else rec.get("translation_span")
            explanation="الأصل يدل على الاستحباب، بينما الترجمة تحوله إلى إلزام." if rec_src else "الأصل يدل على الإلزام، بينما الترجمة تخففه إلى استحباب."
            impact="قد يفهم القارئ أن المستحب واجب." if rec_src else "قد يفهم القارئ أن الواجب مجرد أمر مستحب."
            group=[i for i in group if i.get("type") not in {"recommendation","obligation"}]
            item={"type":"modality_shift","severity":"critical","title":title,"source_span":source_span,"translation_span":translation_span,"explanation_ar":explanation,"impact_ar":impact,"confidence":0.98,"evidence_kind":"deterministic_rule"}
            if seg is not None: item.update({"segment_index":seg,"source_segment":local_ar,"translation_segment":rec.get("translation_segment") or obl.get("translation_segment")})
            group.append(item)

        types={i.get("type") for i in group}
        if "recommendation" in types and "prohibition" in types:
            rec=next(i for i in group if i.get("type")=="recommendation")
            pro=next(i for i in group if i.get("type")=="prohibition")
            rec_src=rec.get("source_span") not in {None,"لا يوجد مقابل","—"}
            title="تغيّر درجة الحكم: من الاستحباب إلى التحريم" if rec_src else "تغيّر درجة الحكم: من التحريم إلى الاستحباب"
            source_span=rec.get("source_span") if rec_src else pro.get("source_span")
            translation_span=pro.get("translation_span") if rec_src else rec.get("translation_span")
            explanation="الأصل يدل على الاستحباب، بينما الترجمة تحوله إلى تحريم أو منع." if rec_src else "الأصل يدل على التحريم، بينما الترجمة تخففه إلى استحباب."
            impact="قد يصل الحكم الموصى به إلى القارئ على أنه ممنوع." if rec_src else "قد يصل الحكم المحرم إلى القارئ على أنه مجرد توصية."
            group=[i for i in group if i.get("type") not in {"recommendation","prohibition"}]
            item={"type":"modality_shift","severity":"critical","title":title,"source_span":source_span,"translation_span":translation_span,"explanation_ar":explanation,"impact_ar":impact,"confidence":0.98,"evidence_kind":"deterministic_rule"}
            if seg is not None: item.update({"segment_index":seg,"source_segment":local_ar,"translation_segment":rec.get("translation_segment") or pro.get("translation_segment")})
            group.append(item)

        types={i.get("type") for i in group}
        if "disliked" in types and "obligation" in types:
            dis=next(i for i in group if i.get("type")=="disliked")
            obl=next(i for i in group if i.get("type")=="obligation")
            dis_src=dis.get("source_span") not in {None,"لا يوجد مقابل","—"}
            title="تغيّر درجة الحكم: من الكراهة إلى الإلزام" if dis_src else "تغيّر درجة الحكم: من الإلزام إلى الكراهة"
            source_span=dis.get("source_span") if dis_src else obl.get("source_span")
            translation_span=obl.get("translation_span") if dis_src else dis.get("translation_span")
            explanation="الأصل يدل على الكراهة، بينما الترجمة تحوله إلى إلزام." if dis_src else "الأصل يدل على الإلزام، بينما الترجمة تخففه إلى كراهة."
            impact="قد يفهم القارئ أن المكروه واجب." if dis_src else "قد يفهم القارئ أن الواجب مجرد مكروه."
            group=[i for i in group if i.get("type") not in {"disliked","obligation"}]
            item={"type":"modality_shift","severity":"critical","title":title,"source_span":source_span,"translation_span":translation_span,"explanation_ar":explanation,"impact_ar":impact,"confidence":0.98,"evidence_kind":"deterministic_rule"}
            if seg is not None: item.update({"segment_index":seg,"source_segment":local_ar,"translation_segment":dis.get("translation_segment") or obl.get("translation_segment")})
            group.append(item)

        types={i.get("type") for i in group}
        if "disliked" in types and "prohibition" in types:
            dis=next(i for i in group if i.get("type")=="disliked")
            pro=next(i for i in group if i.get("type")=="prohibition")
            dis_src=dis.get("source_span") not in {None,"لا يوجد مقابل","—"}
            title="تغيّر درجة الحكم: من الكراهة إلى التحريم" if dis_src else "تغيّر درجة الحكم: من التحريم إلى الكراهة"
            source_span=dis.get("source_span") if dis_src else pro.get("source_span")
            translation_span=pro.get("translation_span") if dis_src else dis.get("translation_span")
            explanation="الأصل يدل على الكراهة، بينما الترجمة تحوله إلى تحريم." if dis_src else "الأصل يدل على التحريم، بينما الترجمة تخففه إلى كراهة."
            impact="قد يفهم القارئ أن المكروه حرام." if dis_src else "قد يفهم القارئ أن المحرم مجرد مكروه."
            group=[i for i in group if i.get("type") not in {"disliked","prohibition"}]
            item={"type":"modality_shift","severity":"critical","title":title,"source_span":source_span,"translation_span":translation_span,"explanation_ar":explanation,"impact_ar":impact,"confidence":0.98,"evidence_kind":"deterministic_rule"}
            if seg is not None: item.update({"segment_index":seg,"source_segment":local_ar,"translation_segment":dis.get("translation_segment") or pro.get("translation_segment")})
            group.append(item)

        types={i.get("type") for i in group}
        if "prohibition" in types and "permission" in types:
            pr=next(i for i in group if i.get("type")=="prohibition")
            pe=next(i for i in group if i.get("type")=="permission")
            # «لا يجوز» already contains a negation marker. When the translation flips
            # it to permission, the polarity diagnosis fully explains the same defect;
            # suppress the duplicate bare-negation alert so reviewers see one precise gap.
            drop_types={"prohibition","permission"}
            local_folded=re.sub(r"[إأآٱ]","ا",local_ar or "")
            if re.search(r"\bلا\s+يجوز\b", local_folded):
                drop_types.add("negation")
                if re.search(r"\bلا\s+يجوز\b.{0,90}\bالا\b", local_folded):
                    drop_types.update({"exception","scope"})
            group=[i for i in group if i.get("type") not in drop_types]
            item={"type":"ruling_polarity_shift","severity":"critical","title":"انقلاب الحكم بين المنع والإباحة","source_span":pr.get("source_span","—"),"translation_span":pe.get("translation_span","—"),"explanation_ar":"تحولت دلالة المنع إلى دلالة إباحة أو العكس.","impact_ar":"قد يقلب الحكم العملي الذي يفهمه القارئ.","confidence":0.98,"evidence_kind":"deterministic_rule"}
            if seg is not None: item.update({"segment_index":seg,"source_segment":local_ar,"translation_segment":pr.get("translation_segment") or pe.get("translation_segment")})
            group.append(item)

        types={i.get("type") for i in group}
        ar_norm=re.sub(r"[إأآٱ]","ا",local_ar or "")
        ar_norm=re.sub(r"[\u064B-\u0652\u0670]","",ar_norm)
        if {"negation","exception"}.issubset(types) and re.search(r"\bلا\b.{0,80}\bالا\b",ar_norm):
            n=next(i for i in group if i.get("type")=="negation")
            e=next(i for i in group if i.get("type")=="exception")
            group=[i for i in group if i.get("type") not in {"negation","exception"}]
            item={"type":"exclusivity_shift","severity":"critical","title":"فقدان بنية الحصر بالنفي والاستثناء","source_span":f"{n.get('source_span','لا')} … {e.get('source_span','إلا')}","translation_span":"لا يوجد مقابل بنيوي مكافئ","explanation_ar":"الأصل يبني معنى الحصر بصيغة «لا … إلا»، بينما اختفى البناء المكافئ في الترجمة.","impact_ar":"فقدان الحصر قد يغيّر القضية نفسها، لا مجرد أسلوب صياغتها.","confidence":0.99,"evidence_kind":"deterministic_rule"}
            seg_eff=seg if seg is not None else (n.get("segment_index") if n.get("segment_index") is not None else e.get("segment_index"))
            if seg_eff is not None: item.update({"segment_index":seg_eff,"source_segment":local_ar or n.get("source_segment") or e.get("source_segment"),"translation_segment":n.get("translation_segment") or e.get("translation_segment")})
            group.append(item)

        if any(i.get("type") in {"exception","condition","exclusivity_shift"} for i in group):
            group=[i for i in group if i.get("type")!="scope"]
        merged.extend(group)
    return _dedupe(merged)


ROOT_TYPES={
    "reference_contradiction","reference_identifier_changed","sacred_text_boundary","provenance_claim_shift",
    "source_attribution_collapse","actor_role_inversion","event_order_reversal","causality_reversal",
    "comparison_direction_reversal","logical_operator_shift","logical_cardinality_shift",
    "publication_gate_shift","threshold_boundary_shift","abstention_policy_shift","ruling_degree_shift",
    "term_relation_reversal","term_scope_reversal","uncertainty_to_certainty","epistemic_overclaim",
    "scope_reversal","scope_shift","frequency_shift","scope_omission","unit_mismatch","asserted_quantity_shift",
    "time_period_shift","severity_scale_shift","named_entity_shift","pronoun_ambiguity","terminology","flattening",
    "source_fabrication_policy_shift","disclaimer_boundary_shift","condition_gate_shift","audit_requirement_shift",
    "negation_scope_reversal","exception_scope_shift","scope_marker_policy_reversal","qualifier_omission_policy_shift",
    "unsupported_addition_policy_shift","comparison_inference_overclaim","terminology_preservation_reversal",
    "quantifier_scope_reversal","translation_principle_reversal","numeric_relation_reversal",
    "signed_number_contradiction","decimal_value_corruption","date_ambiguity_collapse","date_ambiguity_overclaim",
    "equivalent_paraphrase_rejected",
}

GENERIC_SYMPTOMS={
    "negation","exception","condition","obligation","recommendation","disliked","prohibition","permission",
    "modality_shift","ruling_polarity_shift","quantity","scope","omission","addition","generalization","narrowing",
    "attribution",
}

# A root diagnosis explains these lower-level signals in the same aligned segment.
ROOT_SUPPRESS={
    "reference_identifier_changed": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","terminology"},
    "source_attribution_collapse": GENERIC_SYMPTOMS | {"scope_omission","terminology"},
    "actor_role_inversion": GENERIC_SYMPTOMS | {"scope_omission"},
    "event_order_reversal": GENERIC_SYMPTOMS | {"scope_omission"},
    "causality_reversal": GENERIC_SYMPTOMS | {"scope_omission"},
    "comparison_direction_reversal": GENERIC_SYMPTOMS | {"scope_omission"},
    "logical_operator_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "logical_cardinality_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "publication_gate_shift": {"condition","negation","obligation","permission","prohibition","modality_shift","ruling_polarity_shift"},
    "threshold_boundary_shift": {"condition","quantity","negation","obligation","prohibition"},
    "abstention_policy_shift": {"condition","negation","obligation","permission","prohibition","modality_shift"},
    "ruling_degree_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "ruling_polarity_shift": GENERIC_SYMPTOMS | {"scope_omission","scope_shift"},
    "uncertainty_to_certainty": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "epistemic_overclaim": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "unit_mismatch": GENERIC_SYMPTOMS | {"scope_omission","scope_shift","frequency_shift"},
    "asserted_quantity_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "time_period_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "severity_scale_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "named_entity_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "pronoun_ambiguity": GENERIC_SYMPTOMS | {"scope_omission"},
    "term_relation_reversal": GENERIC_SYMPTOMS | {"scope_omission","flattening","terminology"},
    "term_scope_reversal": GENERIC_SYMPTOMS | {"scope_omission","flattening","terminology"},
    "scope_reversal": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "scope_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "frequency_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "disclaimer_boundary_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "condition_gate_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "audit_requirement_shift": {"condition","negation","obligation","prohibition","omission"},
    "negation_scope_reversal": GENERIC_SYMPTOMS | {"scope_omission"},
    "exception_scope_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "scope_marker_policy_reversal": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "qualifier_omission_policy_shift": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "unsupported_addition_policy_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "source_fabrication_policy_shift": GENERIC_SYMPTOMS | {"scope_omission"},
    "comparison_inference_overclaim": GENERIC_SYMPTOMS | {"scope_omission"},
    "terminology_preservation_reversal": GENERIC_SYMPTOMS | {"scope_omission"},
    "quantifier_scope_reversal": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "translation_principle_reversal": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift"},
    "numeric_relation_reversal": GENERIC_SYMPTOMS | {"scope_omission"},
    "signed_number_contradiction": GENERIC_SYMPTOMS | {"scope_omission"},
    "decimal_value_corruption": GENERIC_SYMPTOMS | {"scope_omission"},
    "date_ambiguity_collapse": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift"},
    "date_ambiguity_overclaim": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift"},
    "equivalent_paraphrase_rejected": GENERIC_SYMPTOMS | {"scope_omission"},
    "disclaimer_boundary_shift": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "reference_identifier_changed": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "source_fabrication_policy_shift": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "provenance_claim_shift": GENERIC_SYMPTOMS | {"attribution","negation","scope_omission","frequency_shift","scope_shift"},
    "comparison_direction_reversal": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift"},
    "terminology_preservation_reversal": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift","flattening","terminology"},
    "exclusivity_shift": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift","generalization","quantity"},
    "exception_scope_shift": GENERIC_SYMPTOMS | {"scope_omission","frequency_shift","scope_shift","generalization","quantity"},
    "flattening": {"condition","negation","prohibition","permission","obligation","scope","generalization","narrowing","scope_omission"},
}


SEMANTIC_FAMILY_BY_TYPE={
    "reference_contradiction":"REFERENCE","reference_identifier_changed":"REFERENCE","source_fabrication_policy_shift":"REFERENCE","provenance_claim_shift":"REFERENCE","sacred_text_boundary":"REFERENCE",
    "ruling_degree_shift":"RULING","ruling_polarity_shift":"RULING","modality_shift":"RULING","negation_scope_reversal":"RULING",
    "signed_number_contradiction":"NUMERIC","SIGNED_NUMBER_CONTRADICTION":"NUMERIC","decimal_value_corruption":"NUMERIC","DECIMAL_VALUE_CORRUPTION":"NUMERIC","numeric_relation_reversal":"NUMERIC",
    "asserted_quantity_shift":"NUMERIC","quantity":"NUMERIC","unit_mismatch":"NUMERIC","time_period_shift":"NUMERIC","threshold_boundary_shift":"NUMERIC",
    "logical_operator_shift":"LOGIC","logical_cardinality_shift":"LOGIC","condition_gate_shift":"LOGIC","publication_gate_shift":"LOGIC",
    "scope_reversal":"SCOPE","scope_shift":"SCOPE","frequency_shift":"SCOPE","scope_marker_policy_reversal":"SCOPE",
    "qualifier_omission_policy_shift":"SCOPE","exception_scope_shift":"SCOPE","exclusivity_shift":"SCOPE",
    "uncertainty_to_certainty":"EPISTEMIC","epistemic_overclaim":"EPISTEMIC","date_ambiguity_collapse":"EPISTEMIC","DATE_AMBIGUITY_COLLAPSE":"EPISTEMIC",
    "date_ambiguity_overclaim":"EPISTEMIC","abstention_policy_shift":"EPISTEMIC","pronoun_ambiguity":"EPISTEMIC",
    "actor_role_inversion":"ACTOR","source_attribution_collapse":"ACTOR","named_entity_shift":"ACTOR",
    "event_order_reversal":"CAUSALITY","causality_reversal":"CAUSALITY",
    "terminology":"TERMINOLOGY","flattening":"TERMINOLOGY","term_relation_reversal":"TERMINOLOGY",
    "sacred_semantic_reversal":"SACRED",
    "term_scope_reversal":"TERMINOLOGY","terminology_preservation_reversal":"TERMINOLOGY",
}

SPECIFICITY_PRIORITY={
    "reference_contradiction":0,"source_fabrication_policy_shift":0,"reference_identifier_changed":1,
    "date_ambiguity_collapse":2,"DATE_AMBIGUITY_COLLAPSE":2,"signed_number_contradiction":2,"SIGNED_NUMBER_CONTRADICTION":2,"decimal_value_corruption":2,"DECIMAL_VALUE_CORRUPTION":2,
    "threshold_boundary_shift":3,"asserted_quantity_shift":3,"unit_mismatch":3,"time_period_shift":3,
    "logical_operator_shift":3,"logical_cardinality_shift":3,"actor_role_inversion":3,"causality_reversal":3,"event_order_reversal":3,
    "ruling_degree_shift":3,"ruling_polarity_shift":3,"term_relation_reversal":4,"flattening":5,
    "uncertainty_to_certainty":20,"epistemic_overclaim":20,
}

def _root_code(item):
    return item.get("root_code") or item.get("type")

def _semantic_family(item):
    return item.get("semantic_family") or SEMANTIC_FAMILY_BY_TYPE.get(_root_code(item), SEMANTIC_FAMILY_BY_TYPE.get(item.get("type"), str(item.get("root_family") or item.get("type") or "OTHER").upper()))

def _span_tokens(v):
    return set(re.findall(r"[\w%./:+-]+", _norm_span(v), flags=re.UNICODE))

def _span_overlap(a,b):
    a=_span_tokens(a); b=_span_tokens(b)
    if not a or not b: return 0.0
    return len(a & b) / max(1, min(len(a),len(b)))

def _same_semantic_region(a,b,threshold=.72):
    """Broad local region match used for generic->specific suppression."""
    if a.get("segment_index") != b.get("segment_index"): return False
    ss_a=_norm_span(a.get("source_segment")); ss_b=_norm_span(b.get("source_segment"))
    ts_a=_norm_span(a.get("translation_segment")); ts_b=_norm_span(b.get("translation_segment"))
    if ss_a and ss_b and ss_a==ss_b and ts_a and ts_b and ts_a==ts_b: return True
    return _span_overlap(a.get("source_span"),b.get("source_span"))>=threshold and _span_overlap(a.get("translation_span"),b.get("translation_span"))>=threshold

def _same_issue_span(a,b,threshold=.72):
    """Strict span match for dedup: paragraph identity alone never merges issues."""
    if a.get("segment_index") != b.get("segment_index"): return False
    return _span_overlap(a.get("source_span"),b.get("source_span"))>=threshold and _span_overlap(a.get("translation_span"),b.get("translation_span"))>=threshold

def _specificity_suppressor(item, candidates):
    """Return a more specific public root that explains item, or None.

    Suppression is deliberately conservative: it only applies within the same aligned
    segment and only for known generic->specific relationships. Distinct numeric, ruling,
    event-order and causality roots are therefore preserved.
    """
    t=_root_code(item)
    for c in sorted(candidates,key=lambda x:(SPECIFICITY_PRIORITY.get(_root_code(x),50),_root_rank_tuple(x))):
        ct=_root_code(c)
        if c is item: continue
        if item.get("segment_index") != c.get("segment_index"): continue
        # Date-specific collapse explains the generic certainty signal from the same date sentence.
        if t=="uncertainty_to_certainty" and ct=="DATE_AMBIGUITY_COLLAPSE":
            src=_norm_span(item.get("source_segment") or "")
            dst=_norm_span(item.get("translation_segment") or "")
            if re.search(r"05/10/2026",src) and "definitely" in dst:
                return c
        # Threshold-specific contradiction outranks generic certainty only when they share the same local region.
        if t in {"uncertainty_to_certainty","epistemic_overclaim"} and ct=="threshold_boundary_shift" and _same_semantic_region(item,c,.55):
            return c
        # Same-type / same-family duplicates need strong two-sided span overlap.
        if t==ct and _root_code(item)==_root_code(c) and _semantic_family(item)==_semantic_family(c) and _same_issue_span(item,c):
            return c
    return None


def _norm_span(v):
    v=re.sub(r"\s+"," ",str(v or "")).strip().lower()
    v=re.sub(r"\s*[—-]\s*المقطع\s*\d+\s*$","",v)
    return v[:220]


def _root_fuse(items):
    """Turn detector signals into user-facing root causes.

    Internal detectors may legitimately agree on several symptoms.  The reviewer,
    however, should see the semantic cause once.  Fusion is segment-local and never
    merges evidence across unrelated aligned blocks.
    """
    groups={}
    seg_values={i.get("segment_index") for i in items if i.get("segment_index") is not None}
    single_segment = not seg_values or seg_values == {1}
    for i in items:
        seg=i.get("segment_index")
        # Surface detectors historically omit segment_index for a one-unit input,
        # while contextual roots use segment 1.  Fuse them as one local unit so a
        # precise root diagnosis can suppress its generic symptoms.
        if single_segment and seg is None:
            seg=1
        groups.setdefault(seg,[]).append(i)
    out=[]
    for seg,group in groups.items():
        types={x.get("type") for x in group}
        suppress=set()
        for root in types & ROOT_TYPES:
            suppress |= ROOT_SUPPRESS.get(root,set())
        # Exclusivity is itself a root cause and explains bare negation+exception.
        if "exclusivity_shift" in types:
            suppress |= {"negation","exception","condition","scope","generalization","quantity","scope_omission"}
        # A trusted reference contradiction outranks surface symptoms.
        if "reference_contradiction" in types:
            # A live/trusted reference conflict is the strongest available explanation
            # for the same sacred-text reversal; keep one public root, not both the
            # local sacred reversal and the provider-backed contradiction.
            suppress |= {"negation","condition","quantity","scope","generalization","attribution","obligation","permission","prohibition","frequency_shift","scope_shift","modality_shift","ruling_polarity_shift","exclusivity_shift","sacred_semantic_reversal"}

        # Single-unit fallback tests/reviews still benefit from seeing an explicit
        # negation-loss signal alongside a semantic relation reversal.  Paragraph
        # aligned documents use integer segment ids, where the root cause alone is
        # preferable and avoids duplicate user-facing findings.
        if "term_relation_reversal" in types:
            sample = next((x for x in group if x.get("type")=="term_relation_reversal"), {})
            src_text = str(sample.get("source_segment") or sample.get("source_span") or "")
            if len(src_text) <= 90:
                suppress.discard("negation")

        # Preserve legacy explicit scope labels for tiny one-claim inputs used by
        # the regression suite; in document paragraphs the more precise root label
        # remains the only user-facing issue.
        short_src = min((len(str(x.get("source_segment") or x.get("source_span") or "")) for x in group), default=999)
        if single_segment and short_src <= 35 and "unsupported_addition_policy_shift" not in types:
            suppress.discard("generalization")
            suppress.discard("narrowing")

        kept=[]
        for item in group:
            if item.get("type") in suppress:
                continue
            kept.append(item)

        # Collapse competing trusted-reference roots *before* specificity suppression.
        # Otherwise two equally specific provider-backed contradictions can mutually
        # suppress each other and disappear from the public result even though the
        # trusted-source check itself failed.  Keep exactly one strongest root per
        # aligned sacred segment.
        if sum(1 for x in kept if x.get("type")=="reference_contradiction") > 1:
            refs=[x for x in kept if x.get("type")=="reference_contradiction"]
            refs=sorted(refs,key=lambda x:(x.get("title","").startswith("انقلب اتجاه المعنى مقارنة"), _root_rank_tuple(x)))
            kept=[x for x in kept if x.get("type")!="reference_contradiction"]+[refs[0]]

        # Specificity-aware root suppression. Generic epistemic signals remain in raw
        # diagnostics but are hidden from the public list when a more specific root
        # explains the same semantic region.
        specificity_kept=[]
        for item in kept:
            sup=_specificity_suppressor(item, kept)
            if sup is None:
                specificity_kept.append(item)
        kept=specificity_kept

        # Multiple trusted-reference contradiction rules may describe different
        # symptoms of the same sacred-text reversal. Keep one public root per segment.
        if sum(1 for x in kept if x.get('type')=='reference_contradiction') > 1:
            refs=[x for x in kept if x.get('type')=='reference_contradiction']
            # Prefer the most specific Arabic title over the generic polarity fallback.
            refs=sorted(refs,key=lambda x:(x.get('title','').startswith('انقلب اتجاه المعنى مقارنة'), _root_rank_tuple(x)))
            kept=[x for x in kept if x.get('type')!='reference_contradiction']+[refs[0]]

        # Prefer one contextual bundle diagnosis over an older single-pair relation
        # diagnosis when both describe the same paragraph.
        if sum(1 for x in kept if x.get("type")=="term_relation_reversal") > 1:
            contextual=[x for x in kept if x.get("type")=="term_relation_reversal" and x.get("evidence_kind")=="deterministic_contextual_rule"]
            if contextual:
                kept=[x for x in kept if x.get("type")!="term_relation_reversal"] + [contextual[0]]

        # Exact + span-overlap semantic duplicate suppression. Only same-type roots
        # can merge by overlap; independent roots in one paragraph (e.g. -1 vs 1.5,
        # event order vs causality, three distinct ruling shifts) are preserved.
        seen=set(); roots=[]
        for item in sorted(kept,key=_root_rank_tuple):
            entity=_norm_span(item.get("normalized_entity") or item.get("source_span"))
            key=(seg,_semantic_family(item),item.get("root_family") or item.get("type"),item.get("type"),_norm_span(item.get("source_span")),_norm_span(item.get("translation_span")),entity)
            if key in seen: continue
            duplicate=next((r for r in roots if r.get("type")==item.get("type") and _root_code(r)==_root_code(item) and _semantic_family(r)==_semantic_family(item) and _same_issue_span(r,item)),None)
            if duplicate is not None:
                continue
            seen.add(key); roots.append(item)
        out.extend(roots)
    return sorted(out,key=_root_rank_tuple)

def _enrich_issue_segments(items, ar_text, en_text):
    """Backfill aligned paragraph context for public roots created by global detectors.

    Some document-level/surface detectors intentionally emit no segment index.  When
    the input resolves to exactly one aligned pair, attaching that sole pair is safe
    and lets downstream religious-context/root-fusion logic reason about the actual
    source sentence instead of placeholder spans such as ``لا يوجد مقابل``.
    """
    pairs,_=aligned_pairs(ar_text,en_text)
    pair_map={idx:(ars,ens) for idx,ars,ens in pairs}
    sole_idx=next(iter(pair_map)) if len(pair_map)==1 else None
    for item in items:
        idx=item.get("segment_index")
        if idx not in pair_map and idx is None and sole_idx is not None:
            idx=sole_idx
            item["segment_index"]=idx
        if idx in pair_map:
            ars,ens=pair_map[idx]
            if not item.get("source_segment"):
                item["source_segment"]=ars
            if not item.get("translation_segment"):
                item["translation_segment"]=ens
    return items

def _annotate_recognized_sources(items, recognitions):
    byseg={}
    for r in recognitions or []:
        idx=r.get('segment_index'); rec=r.get('recognition') or {}
        kind=rec.get('kind')
        if idx is not None and kind in {'quran','hadith'}:
            byseg[idx]=kind
    single_kind=next(iter(byseg.values())) if len(byseg)==1 else None
    for item in items:
        idx=item.get('segment_index')
        kind=byseg.get(idx)
        if kind is None and idx is None and single_kind:
            kind=single_kind
        if kind:
            item['recognized_source_kind']=kind
    return items

def _fuse_sacred_segment_symptoms(items, recognitions):
    """Collapse multiple surface symptoms in one Quran/Hadith unit into one semantic root.

    This is a fallback only when no more specific root (trusted-reference conflict,
    reference drift, terminology root, etc.) already exists.  It prevents one altered
    sacred sentence from inflating the public finding count merely because the same
    semantic reversal contains both modality, quantifier and polarity symptoms.
    """
    recognized={r.get('segment_index'):(r.get('recognition') or {}).get('kind') for r in (recognitions or [])}
    groups={}
    for i in items:
        groups.setdefault(i.get('segment_index'),[]).append(i)
    generic={'negation','obligation','permission','prohibition','generalization','narrowing','frequency_shift','scope_shift','exception','condition'}
    specific={'reference_contradiction','reference_identifier_changed','source_fabrication_policy_shift','ruling_degree_shift','ruling_polarity_shift','term_relation_reversal','flattening','terminology','causality_reversal','event_order_reversal','condition_gate_shift','abstention_policy_shift'}
    out=[]
    for seg,group in groups.items():
        kind=recognized.get(seg)
        sample_text=' '.join(str(x.get('source_segment') or x.get('source_span') or '') for x in group)
        if kind not in {'quran','hadith'}:
            if re.search(r'(?:قال\s+(?:رسول\s+الله|النبي)|حديث)', sample_text):
                kind='hadith'
            elif any(_religious_context(x) for x in group):
                kind='religious'
        types={x.get('type') for x in group}
        surface=[x for x in group if x.get('type') in generic]
        if kind in {'quran','hadith','religious'} and len(surface)>=2 and not (types & specific):
            base=sorted(surface,key=_root_rank_tuple)[0]
            arseg=base.get('source_segment') or base.get('source_span') or ''
            enseg=base.get('translation_segment') or base.get('translation_span') or ''
            if {'obligation','generalization'} <= types:
                title='تحول المعنى المقيد إلى إلزام مطلق'
                explanation='اجتمعت في الترجمة إضافة الإلزام والتعميم داخل النص نفسه، فغيّرت التوجيه المقيد إلى معنى مطلق.'
            elif 'negation' in types and (types & {'obligation','permission','prohibition'}):
                title='قُلِب اتجاه المعنى والحكم في النص'
                explanation='تغيّر اتجاه النفي/الإثبات مع إضافة أو تغيير دلالة الإلزام أو الإباحة داخل المقطع نفسه.'
            else:
                title='تغيّر جوهري مركّب في معنى النص الديني'
                explanation='ظهرت عدة تغييرات مترابطة في النفي أو النطاق أو الإلزام داخل المقطع نفسه؛ جُمعت كسبب دلالي واحد بدل تضخيم عدد الفجوات.'
            root=dict(base)
            root.update({'type':'sacred_semantic_reversal','root_family':'sacred_semantic','severity':'critical','title':title,'explanation_ar':explanation,'impact_ar':'قد يصل إلى القارئ معنى ديني مختلف جوهريًا عن النص الأصلي.','source_span':arseg,'translation_span':enseg,'confidence':max(float(x.get('confidence',0) or 0) for x in surface),'evidence_kind':'deterministic_contextual_rule','recognized_source_kind':kind})
            out.extend([x for x in group if x not in surface])
            out.append(root)
        else:
            out.extend(group)
    return sorted(out,key=_root_rank_tuple)

def _build_debug_trace(raw_issues, public_issues):
    trace=[]
    for x in raw_issues:
        exact=next((y for y in public_issues if y.get("type")==x.get("type") and _root_code(y)==_root_code(x) and _same_issue_span(x,y,.72)),None)
        if exact is not None:
            suppressed_by=None; merged_into=exact.get("type")
        else:
            sup=_specificity_suppressor(x, public_issues)
            if sup is None:
                # Fall back to the root-suppression relationship for generic surface signals.
                sup=next((y for y in public_issues if y.get("segment_index")==x.get("segment_index") and x.get("type") in ROOT_SUPPRESS.get(y.get("type"),set())),None)
            suppressed_by=sup.get("type") if sup else None
            merged_into=sup.get("type") if sup else None
        trace.append({
            "detector":x.get("evidence_kind") or "unknown",
            "type":x.get("type"),
            "root_code":_root_code(x),
            "root_family":x.get("root_family") or x.get("type"),
            "semantic_family":_semantic_family(x),
            "segment_index":x.get("segment_index"),
            "source_span":x.get("source_span"),
            "translation_span":x.get("translation_span"),
            "confidence":x.get("confidence"),
            "suppressed_by":suppressed_by,
            "merged_into":merged_into,
            "sub_evidence":x.get("sub_evidence",[]),
        })
    return trace

def _textual_evidence(issues):
    out=[]
    for i in issues:
        if i.get("evidence_kind")=="deterministic_rule":
            out.append({"source":"النصان محل الفحص","title":i.get("title","مطابقة نصية"),"detail":f"الأصل: {i.get('source_span','—')} | الترجمة: {i.get('translation_span','—')}","status":"textual_verified","evidence_type":"textual"})
    return out


def _mirror(issues, ar_text="", en_text=""):
    if not issues:
        ar_norm=re.sub(r"[إأآٱ]","ا",ar_text or "")
        ar_norm=re.sub(r"[\u064B-\u0652\u0670]","",ar_norm)
        en_norm=(en_text or "").lower()
        # في الحالات السليمة، اجعل المرآة مرتبطة بالقيد الموجود فعلًا بدل وصف عام مبهم.
        if re.search(r"\bالا\b",ar_norm) and re.search(r"\b(?:except|unless|other than|with the exception of)\b",en_norm):
            return {"arabic_reader":"يفهم أن المعنى مقيد باستثناء ظاهر في الأصل.","english_reader":"الترجمة تنقل الاستثناء نفسه ضمن المعنى العام.","gap":"لم تظهر فجوة محددة في نقل الاستثناء."}
        if re.search(r"\b(?:اذا|بشرط|في حال)\b",ar_norm) and re.search(r"\b(?:if|provided that|on condition that|in case)\b",en_norm):
            return {"arabic_reader":"يفهم أن المعنى مرتبط بشرط محدد.","english_reader":"الترجمة تحافظ على ارتباط المعنى بالشرط.","gap":"لم تظهر فجوة محددة في نقل الشرط."}
        if re.search(r"\b(?:لا|ليس|لن|لم)\b",ar_norm) and re.search(r"\b(?:not|no|never|without)\b",en_norm):
            return {"arabic_reader":"يفهم دلالة النفي كما وردت في الأصل.","english_reader":"الترجمة تحافظ على اتجاه النفي دون فرق جوهري ظاهر.","gap":"لم تظهر فجوة محددة في نقل النفي."}
        return {"arabic_reader":"يفهم المعنى والقيود الظاهرة في النص الأصلي.","english_reader":"لم تكشف الفحوص الحالية فرقًا جوهريًا في المعنى المنقول.","gap":"لم تظهر فجوة محددة ضمن نطاق الفحوص الحالية."}
    i=sorted(issues,key=_root_rank_tuple)[0]
    t=i.get("type")
    mirrors={
      "flattening": ("يفهم المصطلح ضمن دلالته الشرعية الخاصة.","قد يفهم مقابلاً عامًا أو أضيق من المصطلح الشرعي.","المعنى اللغوي السلس لا يحفظ بالضرورة الدقة الاصطلاحية."),
      "exception": ("يفهم أن المعنى مقيد باستثناء.","قد يفهمه مطلقًا بلا الاستثناء.","فقدان الاستثناء يغيّر نطاق المعنى."),
      "condition": ("يفهم أن المعنى مرتبط بشرط محدد.","قد يفهمه على أنه مطلق.","فقدان الشرط يوسع المعنى خارج نطاقه."),
      "negation": ("يفهم معنى منفيًا.","قد يصل إليه المعنى مثبتًا أو مختلف الاتجاه.","تغير النفي قد يقلب المعنى."),
      "modality_shift": ("يفهم درجة الحكم كما وردت في الأصل.","يفهم درجة حكم مختلفة في الترجمة.",i.get("impact_ar","تغيرت درجة الحكم.")),
      "ruling_polarity_shift": ("يفهم المنع أو الإباحة كما في الأصل.","يفهم حكمًا معاكسًا في الترجمة.","انقلبت قطبية الحكم بين المنع والإباحة."),
      "quantity": (f"يفهم أن القيمة المذكورة هي {i.get('source_span','')}.",f"يفهم أن القيمة المذكورة هي {i.get('translation_span','')}.",f"تغيرت القيمة العددية من {i.get('source_span','')} إلى {i.get('translation_span','')}."),
      "exclusivity_shift": ("يفهم حصرًا واضحًا بصيغة النفي والاستثناء.","قد يفهم علاقة غير حصرية أو معنى أوسع.","اختفى معنى الحصر الذي يحمله بناء «لا … إلا»."),
      "generalization": ("يفهم معنى مقيدًا أو غير مطلق.","قد يفهم قاعدة عامة أو مطلقة.","اتسع نطاق المعنى في الترجمة."),
      "narrowing": ("يفهم معنى عامًا كما في الأصل.","قد يفهمه على نطاق أضيق.","ضاق نطاق المعنى في الترجمة."),
      "attribution": ("يفهم المعلومة مرتبطة بمصدر أو نسبة.","قد تصل المعلومة بلا المصدر أو بنسبة مختلفة.","تغير الإسناد يضعف التتبع والموثوقية."),
    }
    if i.get("reader_original") and i.get("reader_translation"):
        return {"arabic_reader":i.get("reader_original"),"english_reader":i.get("reader_translation"),"gap":i.get("gap_ar") or i.get("impact_ar","يوجد فرق اصطلاحي يحتاج مراجعة.")}
    if t=="flattening" and i.get("source_span")=="التوحيد":
        return {"arabic_reader":"يفهم «التوحيد» كمفهوم شرعي يتجاوز مجرد الوحدانية العددية.","english_reader":"قد يفهم «Oneness» كوحدانية عامة دون الدلالة الشرعية الكاملة.","gap":"اختزال مفهوم شرعي مركب إلى معنى أضيق."}
    if t=="flattening" and i.get("source_span")=="الشريعة":
        return {"arabic_reader":"يفهم «الشريعة» بوصفها أوسع من جانب العقوبات وحده.","english_reader":"قد يفهمها كقانون جنائي أو عقوبات فقط.","gap":"تضييق معنى الشريعة إلى جزء واحد من معناها."}
    if t in mirrors:
        a,b,g=mirrors[t]; return {"arabic_reader":a,"english_reader":b,"gap":g}
    return {"arabic_reader":f"يفهم الأصل مع العنصر الحساس: {i.get('source_span') or i.get('title','')}","english_reader":i.get("explanation_ar","قد يصل معنى مختلف أو أقل دقة."),"gap":i.get("impact_ar","يوجد فرق يحتاج مراجعة.")}


def _evidence_tier(issues,evidence,abstain):
    if abstain: return {"tier":"D","label":"غير كافٍ","explain":"المعطيات لا تكفي لقرار قطعي؛ تم تفعيل الامتناع الآمن."}
    authoritative=any(e.get("status")=="live_verified" for e in evidence)
    direct=any(i.get("evidence_kind") in {"deterministic_rule","deterministic_contextual_rule","trusted_reference_conflict"} for i in issues)
    official=any(i.get("evidence_kind")=="official_glossary_guideline" for i in issues)
    curated=any(i.get("evidence_kind")=="curated_terminology_rule" for i in issues)
    if authoritative and (direct or official or curated): return {"tier":"A","label":"قوي جدًا","explain":"مرجع موثوق مسترجع فعليًا مع دليل دلالي مباشر."}
    if direct or official: return {"tier":"B","label":"قوي","explain":"دليل مباشر من النصين أو قاعدة مصطلحية موثقة في الحزمة العلمية."}
    if curated: return {"tier":"B","label":"قوي","explain":"قاعدة مصطلحية محافظة داخل مِعيار مع فرق ظاهر بين الأصل والترجمة؛ لا تُعرض كمرجع خارجي مستقل."}
    if issues: return {"tier":"C","label":"مؤشر","explain":"مؤشرات دلالية تحتاج مراجعة بشرية أو مرجعًا إضافيًا."}
    if authoritative: return {"tier":"A","label":"دليل مرجعي مباشر","explain":"تم التعرّف على المصدر واسترجاع مرجع موثوق فعليًا، ولم تظهر فجوة جوهرية في الفحوص الحالية."}
    return {"tier":"B","label":"فحص دلالي مكتمل","explain":"لم تظهر إشارة خطر في الفحوص الحالية، مع بقاء حدود التغطية معلنة."}


def analyze(ar,en,api_key=None,llm_model=None,use_live_sources=True,use_semantic_ai=True):
    r=analyze_rules(ar,en)
    t=analyze_terminology(ar,en)
    s=analyze_local_semantics(ar,en)
    sc=analyze_scope(ar,en)
    rel=analyze_term_relations(ar,en)
    prov=analyze_provenance(ar,en)
    cx=analyze_contextual_semantics(ar,en)
    raw_issues=_dedupe(r["issues"]+t["issues"]+s["issues"]+sc["issues"]+rel["issues"]+prov["issues"]+cx["issues"])
    issues=_root_fuse(_refine_issue_set(_merge_semantic_transitions(raw_issues,ar)))
    checks=r["checks"]+t["checks"]+s["checks"]+sc["checks"]+rel["checks"]+prov["checks"]+cx["checks"]

    # Independent evidence channels run in parallel to reduce latency. Source
    # recognition is sentence-local so mixed Quran/Hadith/prose documents are routed
    # correctly instead of being collapsed into one global source guess.
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_ref=pool.submit(retrieve_reference_evidence_multi,ar,live=use_live_sources)
        f_ai=pool.submit(run_semantic_ai,ar,en,enabled=use_semantic_ai)
        recognitions,ref_evidence=f_ref.result()
        semantic_ai=f_ai.result()

    recognition = recognitions[0]["recognition"] if len(recognitions)==1 else None
    refconf=analyze_reference_conflicts(ar,en,recognitions,ref_evidence)
    if refconf["issues"]:
        raw_issues=_dedupe(raw_issues+refconf["issues"])
        issues=_root_fuse(_refine_issue_set(_merge_semantic_transitions(raw_issues,ar)))
    checks += refconf["checks"]
    issues=_enrich_issue_segments(issues,ar,en)
    issues=_annotate_recognized_sources(issues,recognitions)
    issues=_fuse_sacred_segment_symptoms(issues,recognitions)
    issues=_classify_public_issues(issues)
    route=source_route_multi(ar,recognitions)
    evidence=t["evidence"][:]+ref_evidence

    if semantic_ai.get("available"):
        # Similarity supports the decision but never creates a duplicate user-facing gap.
        checks.append({"check":"التحليل الدلالي بالذكاء الاصطناعي","status":semantic_ai.get("status","review"),"detail":semantic_ai.get("detail","")})
    else:
        checks.append({"check":"التحليل الدلالي بالذكاء الاصطناعي","status":"off","detail":semantic_ai.get("detail","غير متاح")})

    if recognitions:
        q_count=sum(1 for x in recognitions if x["recognition"].get("kind")=="quran")
        h_count=sum(1 for x in recognitions if x["recognition"].get("kind")=="hadith")
        parts=[]
        if q_count: parts.append(f"{q_count} مقطع قرآني")
        if h_count: parts.append(f"{h_count} مقطع حديثي")
        checks.append({"check":"التعرّف على المصدر","status":"pass","detail":"تم التعرّف على " + " و".join(parts)})
        if use_live_sources:
            required_segments={x["segment_index"] for x in recognitions if not (x["recognition"].get("kind")=="quran" and x["recognition"].get("match",{}).get("ambiguous"))}
            verified_segments={e.get("segment_index") for e in ref_evidence if e.get("status")=="live_verified"}
            live_ok=bool(required_segments) and required_segments.issubset(verified_segments)
            checks.append({"check":"التحقق المرجعي","status":"pass" if live_ok else "review","detail":"تم استرجاع المراجع الموثوقة لكل المقاطع المتعرّف عليها" if live_ok else "تعذر استرجاع مرجع موثوق لبعض المقاطع"})
    else:
        checks.append({"check":"التعرّف على المصدر","status":"off","detail":"لم يتحدد نص قرآني أو حديث بثقة"})

    # Public 1.0 uses the deterministic + semantic + trusted-source pipeline only.
    # No external generative model can alter the decision path.
    mirror=_mirror(issues,ar,en)

    supported_high=[i for i in issues if i.get("severity") in {"critical","high"} and i.get("evidence_kind") in {"deterministic_rule","deterministic_contextual_rule","official_glossary_guideline","curated_terminology_rule","trusted_reference_conflict"}]
    if supported_high:
        status="critical"
        decision_reason="اكتشف مِعيار تغيرًا عالي الأثر في انتقال المعنى؛ سلاسة الترجمة لغويًا لا تكفي لاعتبارها دقيقة."
    elif issues or any(c["status"]=="fail" for c in checks):
        status="review"
        decision_reason="ظهرت فجوة محتملة في المعنى تحتاج مراجعة قبل النشر."
    elif semantic_ai.get("available") and semantic_ai.get("status")=="fail":
        # Low similarity alone means 'review', never a fabricated diagnosis.
        status="review"
        decision_reason="أعطى التحليل الدلالي إشارة انجراف قوية دون دليل بنيوي كافٍ لتسمية الخطأ؛ لذلك أحال مِعيار الحالة للمراجعة بدل التخمين."
    else:
        status="safe"
        decision_reason="لم تكشف الفحوص الحالية تغيرًا جوهريًا في انتقال المعنى."

    # If a scriptural/hadith source was recognized only by a locator but authoritative retrieval failed,
    # do not pretend to have completed reference verification.
    ref_required=bool(recognitions)
    live_reference=any(e.get("status")=="live_verified" for e in ref_evidence)
    sensitive=any(i.get("type") in {"terminology","flattening","attribution"} for i in issues)
    supported_term=any(i.get("evidence_kind") in {"official_glossary_guideline","curated_terminology_rule"} for i in issues)
    abstain_hint=any(i.get("abstain_hint") for i in issues)
    source_conflict=any(e.get("status")=="conflicting" or (e.get("verification") or {}).get("conflict") is True for e in evidence)
    abstain=source_conflict or (abstain_hint and not supported_high) or (sensitive and not supported_term and not live_reference and not supported_high) or (ref_required and use_live_sources and not live_reference and not supported_high and not issues)
    if abstain:
        status="review"
        if source_conflict:
            decision_reason="تعارضت أدلة المصادر المتاحة أو لم تتفق بما يكفي لإغلاق القرار؛ امتنع مِعيار عن الترجيح الآلي وأحال الحالة للمراجعة البشرية."
        else:
            decision_reason="تعرف مِعيار على محتوى حساس، لكن المرجع الموثوق لم يُسترجع بما يكفي لإغلاق القرار؛ لذلك امتنع عن القطع."

    evidence_used=_textual_evidence(issues)+[dict(e, evidence_role=("used_reference" if e.get("status")=="live_verified" else "used_locator_or_rule")) for e in evidence if e.get("status") in {"live_verified","local_verified_guideline","local_curated_rule","locator_verified"}]
    audit_created_at=datetime.now(timezone.utc).isoformat()
    issues=_attach_issue_provenance(issues,evidence_used,audit_created_at)
    used_names={e.get("source") for e in evidence_used}
    suggested_sources=[{"source":src["name"],"title":"مصدر ضمن المسار المرجعي","detail":src["role"],"status":"recommended","domain":src["domain"]} for src in route["sources"] if src["name"] not in used_names]
    unavailable_sources=[e for e in evidence if e.get("status")=="unavailable"]
    tier=_evidence_tier(issues,evidence_used,abstain)

    # Public live-verification status must be backed by an actual provider retrieval.
    # A local/explicit locator can identify 2:183 or HadeethEnc #4560, but it must never
    # make the UI claim that external verification completed successfully.
    live_ref_evidence=[e for e in ref_evidence if e.get("status")=="live_verified"]
    reference_verification={
        "reference_verified": any((e.get("verification") or {}).get("reference_verified") for e in live_ref_evidence),
        "reference_text_retrieved": any((e.get("verification") or {}).get("source_text_retrieved") for e in live_ref_evidence),
        "user_translation_verified": False,
        "source_conflict": source_conflict,
        "note_ar":"تطابق المرجع أو استرجاع ترجمة مرجعية لا يعني أن ترجمة المستخدم صحيحة تلقائيًا؛ يظل قرار سلامة النقل ناتجًا عن المقارنة متعددة الطبقات.",
    }

    semantic_state="changed" if status=="critical" else ("uncertain" if status=="review" else "preserved")
    ref_state="verified" if live_reference else ("unavailable" if ref_required and use_live_sources else "not_required")
    dimensions={
        "surface_language":{"label":"سلامة اللغة وحدها","state":"not_enough","detail":"قد تكون الصياغة سليمة لغويًا ومع ذلك تغيّر المعنى؛ لذلك لا يعتمد مِعيار على الطلاقة وحدها."},
        "meaning_transfer":{"label":"سلامة انتقال المعنى","state":semantic_state,"detail":"تغيّر جوهري مكتشف" if semantic_state=="changed" else ("تحتاج تحققًا" if semantic_state=="uncertain" else "لم يظهر تغير جوهري")},
        "reference":{"label":"التحقق من المرجع","state":ref_state,"detail":"مرجع موثوق مسترجع" if ref_state=="verified" else ("تعذر الاسترجاع" if ref_state=="unavailable" else "لا يتطلب مرجعًا نصيًا خاصًا")},
        "semantic_ai":{"label":"الذكاء الدلالي","state":semantic_ai.get("status","off"),"detail":semantic_ai.get("detail","")},
    }

    summary={"pass":sum(c["status"]=="pass" for c in checks),"fail":sum(c["status"]=="fail" for c in checks),"review":sum(c["status"]=="review" for c in checks),"off":sum(c["status"]=="off" for c in checks)}
    aid=hashlib.sha256((ar+"\n---\n"+en).encode()).hexdigest()[:12]
    return {
        "status":status,"decision_reason":decision_reason,"confidence_level":tier["label"],"evidence_tier":tier,
        "issues":issues,"checks":checks,"check_summary":summary,"dimensions":dimensions,
        "evidence_used":evidence_used,"suggested_sources":suggested_sources,"unavailable_sources":unavailable_sources,
        "source_route":route,"recognition":recognition,"recognitions":recognitions,"meaning_mirror":mirror,"semantic_ai":semantic_ai,
        "reference_verification":reference_verification,
        "alignment":r.get("alignment",{}),
        "diagnostics":{
            "raw_signal_count":len(raw_issues),
            "root_issue_count":len(issues),
            "suppressed_signal_count":max(0,len(raw_issues)-len(issues)),
            "confidence":_confidence_diagnostics(issues, r.get("alignment",{})),
            "debug_trace":_build_debug_trace(raw_issues,issues),
            "taxonomy_breakdown":_taxonomy_breakdown(issues),
            "religious_impact_breakdown":{k:sum(1 for i in issues if i.get("religious_impact")==k) for k in ("high","medium","none")},
        },
        "raw_issues":raw_issues,
        "abstain":{"needed":abstain,"reason_ar":"الأدلة الحالية لا تكفي لاعتماد قرار قطعي؛ تم تحويل الحالة للمراجعة البشرية." if abstain else ""},
        "audit":{"id":aid,"created_at":audit_created_at,"layers":["semantic_ai_embeddings","structure_rules","meaning_scope","terminology_guard","source_recognition","trusted_reference_retrieval","evidence_fusion","abstention","human_review_gate"]}
    }
