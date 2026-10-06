import html
import json
import re
import os

import streamlit as st

from core.engine import analyze
from core.corrections import build_high_confidence_correction
from core.semantic_ai import start_background_warmup
from core.sources import SURAH_NAMES

st.set_page_config(
    page_title="مِعيار | سلامة المعنى قبل النشر",
    page_icon="assets/miyar_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# يجهّز التحليل الدلالي في الخلفية من دون إظهار تفاصيل تشغيلية للمستخدم.
start_background_warmup()

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Readex+Pro:wght@400;500;600;700&display=swap');
:root{
  --bg:#0A1020; --bg2:#0D1428; --surface:#11192E; --surface2:#151F38;
  --line:rgba(238,242,255,.09); --text:#F5F7FF; --muted:#AAB4CB; --muted2:#8290AE;
  --purple:#6F63EE; --purple2:#8A7FF6; --mint:#43E0C2; --danger:#F26F77;
  --warning:#E9AF63; --success:#45D1A8;
}
*{box-sizing:border-box}
html,body,.stApp{direction:rtl;font-family:'Readex Pro',sans-serif!important;color:var(--text);background:
radial-gradient(760px 390px at 92% -5%,rgba(111,99,238,.13),transparent 64%),
radial-gradient(620px 340px at 2% 0%,rgba(67,224,194,.035),transparent 60%),
linear-gradient(180deg,var(--bg2),var(--bg));}
header[data-testid="stHeader"]{background:transparent;height:0}
#MainMenu,footer,div[data-testid="stToolbar"],div[data-testid="stDecoration"]{visibility:hidden}
.block-container{max-width:1240px!important;padding:1.7rem 2.2rem 3rem!important}
.stMarkdown,.stCaption,label,p,h1,h2,h3,h4,h5,h6,div[data-testid="stAlert"]{direction:rtl!important;text-align:right!important}
.nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px}.brand{display:flex;align-items:center;gap:13px}
.logo{width:54px;height:54px;border-radius:16px;background:linear-gradient(145deg,rgba(111,99,238,.18),rgba(67,224,194,.06));border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center}.logo svg{width:33px;height:33px}
.brand-name{font-size:29px;font-weight:700}.brand-sub{font-size:12px;color:var(--muted);margin-top:2px}
.hero{max-width:980px;margin:0 auto 22px;text-align:center}.hero .eyebrow{display:inline-flex;align-items:center;gap:8px;color:var(--mint);font-size:13px;font-weight:600;margin-bottom:12px}.hero .eyebrow:before{content:"";width:7px;height:7px;border-radius:50%;background:var(--mint);box-shadow:0 0 0 5px rgba(67,224,194,.065)}
.hero h1{text-align:center!important;font-size:52px;line-height:1.16;letter-spacing:-1px;margin:0 0 12px}.hero p{text-align:center!important;color:var(--muted);font-size:18px;line-height:1.85;margin:0 auto;max-width:880px}.hero strong{color:#EEF2FF}.signature-line{width:86px;height:2px;margin:16px auto 0;border-radius:999px;background:linear-gradient(90deg,transparent,var(--mint),var(--purple),transparent)}
.hero-explain{max-width:920px;margin:14px auto 18px;padding:12px 16px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.012);text-align:center!important;color:#D9E0F3;font-size:14px;line-height:1.9}.hero-explain b{color:#F4F7FF}.flow-pills{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:8px}.flow-pill{font-size:12px;color:var(--mint);border:1px solid rgba(67,224,194,.16);border-radius:999px;padding:4px 9px;background:rgba(67,224,194,.025)}
.result-shortcut{display:flex;align-items:center;justify-content:space-between;gap:14px;margin:10px 0 4px;padding:13px 15px;border:1px solid rgba(111,99,238,.18);border-radius:14px;background:rgba(111,99,238,.035)}.result-shortcut b{font-size:15px}.result-shortcut span{font-size:13px;color:var(--muted)}
.remaining-box{border:1px solid rgba(233,175,99,.18);border-radius:15px;padding:13px 15px;margin:10px 0;background:rgba(233,175,99,.025)}.remaining-box .r-title{font-size:15px;font-weight:700;margin-bottom:6px}.remaining-box .r-item{font-size:13px;color:#D9E0F3;line-height:1.8}.remaining-box .r-more{font-size:12px;color:var(--muted2);margin-top:5px}
.workspace-title{display:flex;align-items:end;justify-content:space-between;gap:14px;margin:0 0 7px}.workspace-title h3{margin:0;font-size:22px}.workspace-title span{font-size:13px;color:var(--muted2)}
div[data-testid="stTextArea"] label{font-size:15px!important;font-weight:600!important;color:#EAF0FF!important}div[data-testid="stTextArea"] textarea{min-height:190px!important;border-radius:18px!important;background:linear-gradient(180deg,#131C33,#10172C)!important;border:1px solid var(--line)!important;color:var(--text)!important;padding:16px!important;line-height:1.9!important;font-size:16px!important;box-shadow:none!important}div[data-testid="stTextArea"] textarea:focus{border-color:rgba(111,99,238,.52)!important;box-shadow:0 0 0 3px rgba(111,99,238,.07)!important}div[data-testid="column"]:first-child textarea{direction:rtl!important;text-align:right!important}div[data-testid="column"]:nth-child(2) textarea{direction:ltr!important;text-align:left!important}
div[data-testid="stButton"]{margin-top:5px}div[data-testid="stButton"]>button{width:94%;margin-left:3%;margin-right:3%;min-height:52px;border:none!important;border-radius:16px!important;background:linear-gradient(135deg,var(--purple),var(--purple2))!important;color:white!important;font-size:15px!important;font-weight:700!important;box-shadow:0 14px 28px rgba(111,99,238,.17)}div[data-testid="stButton"]>button:disabled{filter:saturate(.45);opacity:.5;box-shadow:none}.helper{text-align:center;color:var(--muted2);font-size:13px;margin-top:10px;line-height:1.8}
.section-head{font-size:23px;font-weight:700;margin:30px 0 11px;letter-spacing:-.2px}.result-card{padding:25px 27px;border:1px solid var(--line);border-radius:20px;background:var(--surface)}.result-card.critical{background:linear-gradient(180deg,rgba(242,111,119,.075),rgba(242,111,119,.018));border-color:rgba(242,111,119,.18)}.result-card.review{background:linear-gradient(180deg,rgba(233,175,99,.07),rgba(233,175,99,.018));border-color:rgba(233,175,99,.18)}.result-card.safe{background:linear-gradient(180deg,rgba(69,209,168,.07),rgba(69,209,168,.018));border-color:rgba(69,209,168,.18)}.result-title{font-size:31px;font-weight:700;margin-bottom:5px}.result-desc{font-size:16px;color:var(--muted);line-height:1.85}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:15px}.stat{border:1px solid var(--line);background:rgba(255,255,255,.015);border-radius:14px;padding:12px 14px}.stat b{display:block;font-size:20px;margin-bottom:3px}.stat span{font-size:13px;color:var(--muted2)}.publish-note{font-size:12px;color:var(--muted2);margin-top:7px;line-height:1.65}
.ai-strip{margin:12px 0 4px;border:1px solid var(--line);border-radius:15px;padding:13px 15px;display:flex;justify-content:space-between;align-items:center;gap:16px;background:rgba(255,255,255,.012)}.ai-strip .ai-k{font-size:14px;color:var(--muted2)}.ai-strip .ai-v{font-size:16px;font-weight:700;margin-top:2px}.ai-strip .ai-note{font-size:13px;color:var(--muted);margin-top:3px;line-height:1.7}.ai-score{font-size:31px;font-weight:800;white-space:nowrap}.ai-score small{font-size:12px;color:var(--muted2);font-weight:400;display:block}.ai-wow{border-color:rgba(67,224,194,.22);background:rgba(67,224,194,.025)}
.lens-mini{border:1px solid var(--line);border-radius:15px;padding:13px 14px;background:rgba(255,255,255,.012);min-height:118px}.lens-mini .k{font-size:13px;color:var(--muted2)}.lens-mini .v{font-size:17px;font-weight:700;margin-top:4px}.lens-mini .d{font-size:13px;color:var(--muted);line-height:1.75;margin-top:3px}
.impact,.note,.evidence-card,.issue,.compact-ok{border:1px solid var(--line);border-radius:16px;padding:15px 17px;margin:8px 0;background:rgba(255,255,255,.012)}.fix-card{border:1px solid rgba(67,224,194,.24);border-radius:18px;padding:18px 20px;margin:12px 0 8px;background:linear-gradient(180deg,rgba(67,224,194,.055),rgba(67,224,194,.018))}.fix-kicker{font-size:13px;color:var(--mint);font-weight:700;margin-bottom:5px}.fix-title{font-size:21px;font-weight:700;margin-bottom:8px}.fix-row{display:grid;grid-template-columns:1fr 52px 1fr;gap:10px;align-items:center;margin-top:12px}.fix-side{border:1px solid var(--line);border-radius:13px;padding:12px 14px;background:rgba(255,255,255,.015);min-width:0}.fix-side span{display:block;color:var(--muted2);font-size:12px;margin-bottom:5px}.fix-side b{font-size:15px;line-height:1.75;overflow-wrap:anywhere}.fix-arrow{text-align:center;color:var(--mint);font-size:20px;font-weight:700}.fix-note{font-size:12px;color:var(--muted2);line-height:1.75;margin-top:9px}.problem-card{border:1px solid rgba(242,111,119,.18);border-right:4px solid var(--danger);border-radius:16px;padding:15px 17px;margin:12px 0;background:rgba(242,111,119,.03)}.problem-card .p-k{font-size:12px;color:var(--danger);font-weight:700;margin-bottom:4px}.problem-card .p-t{font-size:20px;font-weight:700}.problem-card .p-d{font-size:14px;line-height:1.85;color:#D9E0F3;margin-top:5px}.gap-list{display:grid;gap:9px;margin:12px 0 14px}.gap-item{border:1px solid var(--line);border-right:4px solid var(--danger);border-radius:15px;padding:13px 15px;background:rgba(242,111,119,.028)}.gap-item.review{border-right-color:var(--warning);background:rgba(233,175,99,.022)}.gap-title{font-size:17px;font-weight:700;margin-bottom:4px}.gap-meta{display:flex;gap:7px;flex-wrap:wrap;margin-top:7px}.gap-chip{font-size:12px;color:#DDE4F6;border:1px solid var(--line);border-radius:999px;padding:4px 8px;background:rgba(255,255,255,.018)}.issue-badges{display:flex;gap:7px;flex-wrap:wrap;margin:6px 0 8px}.issue-badge{font-size:11px;font-weight:700;border-radius:999px;padding:4px 9px;border:1px solid var(--line);background:rgba(255,255,255,.02);color:#E8EDFF}.issue-badge.religious{border-color:rgba(233,175,99,.24);color:#FFD89C;background:rgba(233,175,99,.05)}.issue-badge.source{border-color:rgba(67,224,194,.22);color:#7EF0D8;background:rgba(67,224,194,.04)}.issue-badge.logic{border-color:rgba(111,99,238,.24);color:#B7B0FF;background:rgba(111,99,238,.05)}.taxonomy-summary{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 12px}.taxonomy-pill{border:1px solid var(--line);border-radius:12px;padding:8px 11px;background:rgba(255,255,255,.015);font-size:12px}.taxonomy-pill b{font-size:16px;margin-left:5px}.scope-note{margin-top:8px;border-right:3px solid var(--warning);padding:8px 10px;background:rgba(233,175,99,.035);border-radius:9px;font-size:12px;color:#EADFCF;line-height:1.75}.verify-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:10px 0}.verify-item{border:1px solid var(--line);border-radius:12px;padding:10px;background:rgba(255,255,255,.012);font-size:12px;line-height:1.7}.verify-item b{display:block;font-size:13px;margin-bottom:2px}.fix-changes{display:grid;gap:7px;margin:12px 0}.fix-change{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:8px;align-items:center;border:1px solid var(--line);border-radius:12px;padding:9px 10px;background:rgba(255,255,255,.012)}.fix-change span{font-size:12px;color:var(--muted2)}.fix-change b{font-size:13px;overflow-wrap:anywhere}.fix-coverage{font-size:13px;color:var(--mint);font-weight:700;margin-top:8px}.technical-mini{font-size:13px;color:var(--muted);line-height:1.8;padding:4px 0}.impact{border-color:rgba(67,224,194,.14);background:rgba(67,224,194,.028);font-size:15px;line-height:1.9}.next-action{border:1px solid rgba(111,99,238,.18);border-radius:14px;padding:13px 15px;margin:8px 0 14px;background:rgba(111,99,238,.045);font-size:14px;line-height:1.85;color:#E8ECFF}.compact-ok{border-color:rgba(69,209,168,.16);background:rgba(69,209,168,.028);font-size:15px;line-height:1.85}.note{color:var(--muted);font-size:13px;line-height:1.9}.issue.critical{border-color:rgba(242,111,119,.2);border-right:4px solid var(--danger);background:rgba(242,111,119,.035)}.issue.warning{border-color:rgba(233,175,99,.2);border-right:4px solid var(--warning);background:rgba(233,175,99,.025)}.issue-title,.evidence-title{font-size:17px;font-weight:700}.issue-text,.evidence-detail{font-size:14px;color:#D9E0F3;line-height:1.85}.issue-meta,.evidence-src{font-size:12px;color:var(--muted2);margin-top:7px}.evidence-src{color:var(--mint);margin:0 0 5px}.pair{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:8px;align-items:center;margin:10px 0;padding:10px 11px;border-radius:12px;background:rgba(255,255,255,.018)}.pair span{font-size:11px;color:var(--muted2)}.pair b{font-size:14px;color:#EEF2FF;overflow-wrap:anywhere}
.trace{display:grid;grid-template-columns:1fr 42px 1fr 42px 1fr;gap:8px;align-items:stretch}.trace-step{border:1px solid var(--line);border-radius:15px;padding:14px;background:rgba(255,255,255,.012)}.trace-step .n{font-size:13px;color:var(--mint);margin-bottom:5px}.trace-step b{font-size:17px;display:block;margin-bottom:4px}.trace-step p{font-size:14px;color:var(--muted);line-height:1.8;margin:0}.trace-arrow{display:flex;align-items:center;justify-content:center;color:var(--muted2);font-size:18px}
.mirror{display:grid;grid-template-columns:1fr 76px 1fr;gap:12px}.mirror-card{font-size:16px;line-height:1.95;border:1px solid var(--line);border-radius:18px;padding:18px 19px;background:linear-gradient(180deg,var(--surface),#0F172B)}.mirror-label{font-size:13px;color:var(--muted2);margin-bottom:8px}.delta{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}.delta-badge{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(111,99,238,.11);border:1px solid rgba(111,99,238,.2);font-size:19px;font-weight:700}.delta span{font-size:11px;color:var(--muted2)}
.reference-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}.reference-col{border:1px solid var(--line);border-radius:15px;padding:14px;background:rgba(255,255,255,.012);min-width:0}.reference-col .h{font-size:12px;color:var(--muted2);margin-bottom:7px}.reference-col .txt{font-size:14px;line-height:1.85;overflow-wrap:anywhere}.reference-col.reference{border-color:rgba(67,224,194,.17);background:rgba(67,224,194,.025)}
.check-summary{display:flex;align-items:center;justify-content:space-between;gap:12px;border:1px solid var(--line);border-radius:15px;padding:14px 16px;background:rgba(255,255,255,.012)}.check-summary b{font-size:16px}.check-summary span{font-size:13px;color:var(--muted2)}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.012)}div[data-testid="stExpander"] summary{font-size:14px!important}div[data-testid="stDownloadButton"] button{min-height:48px;border-radius:14px!important;background:transparent!important;border:1px solid var(--line)!important;color:#EAF0FF!important}.footer-limit{margin-top:18px;border-top:1px solid var(--line);padding-top:14px;color:var(--muted2);font-size:13px;line-height:1.9}
@media(max-width:1100px){.block-container{max-width:96vw!important;padding-left:1.4rem!important;padding-right:1.4rem!important}}
@media(max-width:760px){.fix-row{grid-template-columns:1fr}.fix-arrow{transform:rotate(90deg)}.block-container{padding-left:.9rem!important;padding-right:.9rem!important}.hero h1{font-size:35px}.hero p{font-size:15px}.workspace-title{align-items:flex-start;flex-direction:column}.workspace-title span{font-size:12px}.stats,.mirror,.trace,.reference-grid{grid-template-columns:1fr}.delta,.trace-arrow{display:none}.section-head{font-size:20px}.pair{grid-template-columns:auto 1fr}.result-title{font-size:26px}.ai-strip{align-items:flex-start;flex-direction:column}.ai-score{font-size:28px}}
</style>
""",
    unsafe_allow_html=True,
)


def esc(value):
    return html.escape(str(value or ""), quote=True)


def public_source_name(name):
    mapping = {
        "QuranEnc": "موسوعة ترجمات معاني القرآن الكريم",
        "HadeethEnc": "موسوعة الأحاديث النبوية",
        "TerminologyEnc": "موسوعة المصطلحات الإسلامية",
        "Central DB / ICADB": "قاعدة المحتوى الإسلامي المركزية",
        "ICADB": "قاعدة المحتوى الإسلامي المركزية",
        "IslamHouse": "الإسلام هاوس",
        "IslamEnc": "موسوعة الإسلام متعددة اللغات",
        "Byenah": "بيّنة",
        "التعرّف على المصدر": "تحديد المرجع",
        "النصان محل الفحص": "النصان محل الفحص",
        "الحزمة العلمية للتحدي — قاموس المصطلحات الأساسية": "دليل المصطلحات المعتمد",
        "الحزمة العلمية للتحدي — نماذج قاموس المصطلحات": "دليل المصطلحات المعتمد",
        "قاموس مِعيار المصطلحي — قاعدة محافظة": "قاعدة مِعيار للمصطلحات الحساسة",
        "قاموس مِعيار المصطلحي — قاعدة محافظة موثقة الأساس": "قاعدة مِعيار للمصطلحات الحساسة",
    }
    return mapping.get(name, name)


def evidence_attribution(ev):
    source=public_source_name(ev.get("source", ""))
    title=ev.get("translation_title") or ""
    version=ev.get("source_version")
    retrieved=ev.get("retrieved_at")
    key=ev.get("translation_key")
    parts=[source]
    if title:
        parts.append(str(title))
    if key:
        parts.append(f"key: {key}")
    parts.append(f"version: {version}" if version else "version: غير متاح من الاستجابة الحالية")
    if retrieved:
        parts.append(f"retrieved: {retrieved}")
    url=ev.get("url") or ev.get("browse_url") or ev.get("metadata_url")
    if url:
        parts.append(f"URL: {url}")
    return " — ".join(parts)


def taxonomy_label(code):
    return {
        "RELIGIOUS_SEMANTIC":"دلالي ذو أثر ديني",
        "GENERAL_SEMANTIC":"دلالي عام",
        "LOGIC_NUMERIC":"منطقي/رقمي",
        "SOURCE_INTEGRITY":"سلامة المصدر والمرجع",
        "EPISTEMIC":"معرفي/درجة يقين",
    }.get(code, code or "دلالي عام")



def arabic_gap_count_phrase(n: int) -> str:
    """Return a natural Arabic counted phrase for UI summaries."""
    n = int(n)
    if n == 1:
        return "فجوة واحدة"
    if n == 2:
        return "فجوتان"
    if 3 <= n <= 10:
        return f"{n} فجوات"
    return f"{n} فجوة"


def taxonomy_summary_label(code: str) -> str:
    return {
        "RELIGIOUS_SEMANTIC": "دلالية دينية",
        "GENERAL_SEMANTIC": "دلالية عامة",
        "LOGIC_NUMERIC": "منطقية/رقمية",
        "SOURCE_INTEGRITY": "مرجعية",
        "EPISTEMIC": "معرفية",
    }.get(code, taxonomy_label(code))

def issue_badge_label(issue):
    tax=issue.get("issue_taxonomy")
    subtype=issue.get("issue_subtype") or ""
    if tax=="RELIGIOUS_SEMANTIC":
        if subtype=="RELIGIOUS_TERMINOLOGY_DRIFT": return "مصطلح شرعي", "religious"
        if subtype=="RULING_TRANSFER_DRIFT": return "نقل حكم شرعي", "religious"
        return "أثر ديني", "religious"
    if tax=="SOURCE_INTEGRITY": return "مرجعي", "source"
    if tax=="LOGIC_NUMERIC":
        if "NUMBER" in subtype or "NUMERIC" in subtype or "DECIMAL" in subtype: return "عددي", "logic"
        return "منطقي", "logic"
    if tax=="EPISTEMIC": return "معرفي", "logic"
    return "دلالي", "logic"

def religious_impact_label(value):
    return {"high":"مرتفع","medium":"متوسط","none":"لا يوجد أثر ديني مباشر"}.get(value,value or "لا يوجد أثر ديني مباشر")

def public_check_rows(checks):
    """يعرض الفحوص المفيدة للمستخدم ويخفي طبقات التشغيل الداخلية."""
    return list(checks)


def public_layer_name(kind):
    return {
        "deterministic_rule": "دليل مباشر من النصين",
        "official_glossary_guideline": "قاعدة مصطلحية معتمدة",
        "curated_terminology_rule": "قاعدة مصطلحية محافظة",
        "local_semantic_heuristic": "فحص دلالي للسياق والنطاق",
        "coverage_heuristic": "فحص التغطية",
        "semantic_ai_embedding": "تحليل دلالي",
    }.get(kind, "فحص دلالي")


def public_gate(status):
    if status == "critical":
        return "إيقاف النشر", "لا يُنصح بالنشر قبل معالجة الفجوة المؤثرة."
    if status == "review":
        return "مراجعة قبل النشر", "النتيجة غير محسومة بما يكفي للنشر المباشر."
    return "لا يظهر مانع دلالي", "يخص سلامة انتقال المعنى فقط، ولا يثبت صحة المحتوى الشرعي الأصلي."


def public_evidence_value(res):
    if res["status"] == "safe" and not res["evidence_used"]:
        return "الفحوص الحالية مكتملة"
    return res["evidence_tier"]["label"]


def quran_ref_label(item):
    surah = item.get("surah")
    ayah = item.get("ayah")
    name = SURAH_NAMES.get(surah, f"سورة {surah}")
    return f"{name} {surah}:{ayah}"


st.markdown(
    """
<div class="nav"><div class="brand"><div class="logo"><svg viewBox="0 0 40 40" fill="none"><circle cx="17" cy="17" r="9" stroke="#43E0C2" stroke-width="2.2"/><path d="M23.7 23.7L31 31" stroke="#43E0C2" stroke-width="2.4" stroke-linecap="round"/><path d="M13 15.5H21M13 18.7H19" stroke="#8A7FF6" stroke-width="2" stroke-linecap="round"/></svg></div><div><div class="brand-name">مِعيار</div><div class="brand-sub">سلامة المعنى قبل النشر</div></div></div></div>
<div class="hero"><div class="eyebrow">سليمة لغويًا ≠ دقيقة دلاليًا</div><h1>سلامة الصياغة لا تعني سلامة المعنى</h1><p>قد تبدو الترجمة صحيحة وواضحة، بينما تفقد <strong>قيدًا أو مصطلحًا أو دلالة مؤثرة</strong>.</p><div class="signature-line"></div></div>
<div class="hero-explain"><b>مِعيار يراجع ترجمة موجودة قبل نشرها</b>، ويكشف ما فُقد أو تغيّر من المعنى. وإذا كان التصحيح واضحًا وآمنًا يقترحه بوضوح، من دون إعادة ترجمة النص من الصفر.<div class="flow-pills"><span class="flow-pill">اكتشاف</span><span class="flow-pill">تفسير</span><span class="flow-pill">تصحيح آمن</span></div></div>
<div class="workspace-title"><h3>قارن الأصل بالترجمة</h3><span>أدخل الأصل العربي وترجمته الإنجليزية لمراجعة انتقال المعنى قبل النشر</span></div>
""",
    unsafe_allow_html=True,
)

if "ar_input" not in st.session_state:
    st.session_state.ar_input = ""
if "en_input" not in st.session_state:
    st.session_state.en_input = ""

DEMO_CASES = {
    "safe": (
        "توضأ أحمد قبل أن يصلي.",
        "Before praying, Ahmad performed Wudu.",
    ),
    "ruling": (
        "يذكر النص أن هذا الفعل جائز.",
        "The text states that this action is obligatory.",
    ),
    "reference": (
        "ورد المرجع: سورة البقرة، الآية 183.",
        "The reference is Surah Al-Baqarah, verse 185.",
    ),
}

def load_demo_case(case_key: str) -> None:
    ar_demo, en_demo = DEMO_CASES[case_key]
    st.session_state.ar_input = ar_demo
    st.session_state.en_input = en_demo

st.markdown('<div class="helper" style="margin:2px 0 8px">جرّب مثالًا جاهزًا لفهم النتيجة بسرعة</div>', unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)
with d1:
    st.button("مثال سليم", key="demo_safe", on_click=load_demo_case, args=("safe",), use_container_width=True)
with d2:
    st.button("تغيّر حكم", key="demo_ruling", on_click=load_demo_case, args=("ruling",), use_container_width=True)
with d3:
    st.button("تغيّر مرجع", key="demo_reference", on_click=load_demo_case, args=("reference",), use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    ar = st.text_area("النص العربي الأصلي", placeholder="النص العربي هنا", height=190, max_chars=12000, key="ar_input")
with c2:
    en = st.text_area("الترجمة الإنجليزية", placeholder="الترجمة هنا", height=190, max_chars=12000, key="en_input")

ready = bool(ar.strip() and en.strip())
run = st.button("افحص سلامة المعنى", use_container_width=True, disabled=not ready)
st.markdown(
    '<div class="helper">حتى 12,000 حرف لكل حقل</div>',
    unsafe_allow_html=True,
)
if run:
    with st.spinner("يفحص مِعيار انتقال المعنى ويسترجع المرجع الموثوق عند الحاجة..."):
        # الإصدار العام ثابت وقابل للتكرار: لا يعتمد على طبقة توليدية خارجية اختيارية.
        res = analyze(ar, en, use_live_sources=True, use_semantic_ai=True)

    meta = {
        "critical": ("critical", "غير جاهزة للنشر", "اكتشف مِعيار تغيرًا جوهريًا في انتقال المعنى."),
        "review": ("review", "تحتاج مراجعة بشرية", "لا تكفي الأدلة الحالية لإغلاق القرار بما يسمح بالنشر المباشر."),
        "safe": ("safe", "لم يُكتشف تغير جوهري", "لم تكشف الفحوص الحالية فجوة محددة في انتقال المعنى."),
    }
    cls, title, desc = meta[res["status"]]
    gate, gate_note = public_gate(res["status"])
    sev_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    issue_priority = {
        "source_fabrication_policy_shift": 0, "reference_contradiction": 1, "reference_identifier_changed": 2,
        "ruling_polarity_shift": 3, "ruling_degree_shift": 4, "negation_scope_reversal": 5,
        "condition_gate_shift": 6, "exclusivity_shift": 7, "logical_operator_shift": 8,
        "logical_cardinality_shift": 9, "actor_role_inversion": 10, "event_order_reversal": 11,
        "causality_reversal": 12, "comparison_direction_reversal": 13, "unit_mismatch": 14,
        "asserted_quantity_shift": 15, "uncertainty_to_certainty": 16, "epistemic_overclaim": 17,
    }
    ordered_issues = sorted(
        res["issues"],
        key=lambda x: (-sev_rank.get(x.get("severity", "medium"), 2), issue_priority.get(x.get("type"), 50), -float(x.get("confidence",0) or 0)),
    )
    top_issue = ordered_issues[0] if ordered_issues else None
    correction = build_high_confidence_correction(en, ordered_issues)

    st.markdown('<div id="decision" class="section-head">قرار ما قبل النشر</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="result-card {cls}">
  <div class="result-title">{esc(title)}</div>
  <div class="result-desc">{esc(desc)}</div>
  <div class="stats">
    <div class="stat"><b>{len(res['issues'])}</b><span>فجوات محددة</span></div>
    <div class="stat"><b>{esc(public_evidence_value(res))}</b><span>الدليل المتاح</span></div>
    <div class="stat"><b>{esc(gate)}</b><span>بوابة النشر</span><div class="publish-note">{esc(gate_note)}</div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    diag_summary=(res.get("diagnostics",{}) or {})
    breakdown=diag_summary.get("taxonomy_breakdown",{})
    impact_breakdown=diag_summary.get("religious_impact_breakdown",{})
    if ordered_issues and breakdown:
        pills=[]
        for key in ("RELIGIOUS_SEMANTIC","GENERAL_SEMANTIC","LOGIC_NUMERIC","SOURCE_INTEGRITY","EPISTEMIC"):
            item=breakdown.get(key,{})
            pills.append(f'<span class="taxonomy-pill"><b>{int(item.get("count",0))}</b>&nbsp;{esc(taxonomy_summary_label(key))}</span>')
        direct_impact=int(impact_breakdown.get("high",0) or 0)+int(impact_breakdown.get("medium",0) or 0)
        pills.append(f'<span class="taxonomy-pill"><b>{direct_impact}</b>&nbsp;ذات أثر ديني مباشر</span>')
        st.markdown('<div class="taxonomy-summary">'+''.join(pills)+'</div>',unsafe_allow_html=True)
        st.caption("نوع الخطأ يصف طبيعة الخلل، أما الأثر الديني فيصف حساسية أثره في هذا السياق؛ لذلك قد يكون الخطأ عدديًا أو منطقيًا وله أثر ديني مباشر.")

    # واجهة النتيجة العامة: تعرض الخلاصة أولًا وتُبقي التفاصيل الكاملة مطوية
    # حتى لا تتحول صفحة الكاتب إلى تقرير تقني مزدحم.
    safe_fix_count = int(correction.get("resolved_issue_count", 0)) if correction else 0
    human_review_count = max(0, len(ordered_issues) - safe_fix_count)

    def _public_issue_title(issue):
        title = str(issue.get("title", "تغيّر دلالي") or "تغيّر دلالي")
        return re.sub(r"\s*[—-]\s*المقطع\s*\d+\s*$", "", title).strip()

    def _issue_source_text(issue):
        return str(issue.get("source_segment") or issue.get("source_span") or "—")

    def _issue_translation_text(issue):
        return str(issue.get("translation_segment") or issue.get("translation_span") or "—")

    if ordered_issues:
        shortcut_text = f"{len(ordered_issues)} فجوة مكتشفة"
        if safe_fix_count:
            shortcut_text += f" · {safe_fix_count} يمكن تصحيحها بأمان"
        if human_review_count:
            shortcut_text += f" · {human_review_count} تحتاج مراجعة بشرية"
        st.markdown(
            f'<div class="result-shortcut"><b>{esc(shortcut_text)}</b></div>',
            unsafe_allow_html=True,
        )

        with st.expander(f"الفجوات المكتشفة ({len(ordered_issues)})"):
            st.caption("كل فجوة مرتبطة بالنص الفعلي حتى يعرف الكاتب موضعها مباشرة، من دون الاعتماد على رقم المقطع.")
            for issue in ordered_issues:
                cssc = "" if issue.get("severity") in {"critical", "high"} else " review"
                badge,bcls=issue_badge_label(issue)
                impact=religious_impact_label(issue.get("religious_impact"))
                subref_html=""
                if issue.get("sub_evidence"):
                    state_ar={"synthetic":"معرّف اختباري","changed":"تغيّر داخل النص","verified":"تم التحقق حيًا","unverifiable":"تعذر التحقق"}
                    bits=[]
                    for sub in issue.get("sub_evidence",[]):
                        bits.append(f'<span class="gap-chip">{esc(sub.get("kind","REF"))}: {esc(sub.get("source_value",""))} → {esc(sub.get("translation_value",""))} · {esc(state_ar.get(sub.get("reference_state"),sub.get("reference_state","")))}</span>')
                    subref_html='<div class="gap-meta">'+''.join(bits)+'</div>'
                st.markdown(
                    f'<div class="gap-item{cssc}">'
                    f'<div class="gap-title">{esc(_public_issue_title(issue))}</div>'
                    f'<div class="issue-badges"><span class="issue-badge {bcls}">{esc(badge)}</span>'
                    f'<span class="issue-badge">الأثر الديني: {esc(impact)}</span></div>'
                    f'<div class="issue-text">{esc(issue.get("explanation_ar", ""))}</div>'
                    f'<div class="issue-text"><b>سبب تصنيف الأثر:</b> {esc(issue.get("religious_impact_reason", ""))}</div>'
                    f'{subref_html}'
                    f'<div class="gap-meta"><span class="gap-chip">الأصل: {esc(_issue_source_text(issue))}</span>'
                    f'<span class="gap-chip">الترجمة: {esc(_issue_translation_text(issue))}</span></div>'
                    f'<div class="scope-note">{esc(issue.get("boundary_note_ar", ""))}</div></div>',
                    unsafe_allow_html=True,
                )

    if correction:
        changes = correction["changes"]
        # نعرض التصحيح كجملة كاملة قبل/بعد بدل سهم بين كلمتين؛
        # هذا يجعل مكان التعديل ونتيجته واضحين للكاتب مباشرة.
        original_segments = [x.strip() for x in re.split(r"(?<=[.!?؟؛])\s+|\n+", en.strip()) if x.strip()]
        corrected_segments = [x.strip() for x in re.split(r"(?<=[.!?؟؛])\s+|\n+", correction.get("corrected_text", "").strip()) if x.strip()]

        def _change_before_after(ch):
            idx = ch.get("segment_index")
            try:
                idx = int(idx) if idx is not None else None
            except (TypeError, ValueError):
                idx = None
            if idx and 1 <= idx <= len(original_segments):
                before = original_segments[idx - 1]
            else:
                before = str(ch.get("translation_segment") or ch.get("from") or "")
            if idx and 1 <= idx <= len(corrected_segments):
                after = corrected_segments[idx - 1]
            else:
                after = before
                old_token = str(ch.get("from") or "")
                new_token = str(ch.get("to") or "")
                if old_token and new_token and old_token not in {"لا يوجد مقابل", "—"}:
                    after = re.sub(re.escape(old_token), lambda _m: new_token, after, count=1, flags=re.IGNORECASE)
            return before, after

        change_rows = '<div class="fix-changes">'
        for ch in changes:
            source_context = str(ch.get("source_segment") or ch.get("source") or "")
            before_text, after_text = _change_before_after(ch)
            change_rows += (
                f'<div class="fix-change"><span>الموضع في الأصل</span>'
                f'<b>{esc(source_context)}</b>'
                f'<span>قبل</span><b>{esc(before_text)}</b>'
                f'<span>بعد</span><b>{esc(after_text)}</b>'
                f'<span>السبب</span><b>{esc(ch.get("reason", ""))}</b></div>'
            )
        change_rows += '</div>'
        resolved = correction.get("resolved_issue_count", len(changes))
        total = correction.get("total_issue_count", len(ordered_issues))
        unresolved = correction.get("unresolved_issue_count", max(0, total - resolved))
        coverage = (
            f'يملك مِعيار تصحيحًا محددًا وآمنًا لـ {resolved} من {total} فجوة. أما البقية فلا يعيد صياغتها آليًا حتى لا يغيّر المعنى.'
            if unresolved
            else f'كل الفجوات المكتشفة ({resolved}) لها تصحيح آمن ومحدد يمكن للكاتب تطبيقه ثم إعادة الفحص.'
        )
        st.markdown(
            f'''<div id="suggested-fix" class="fix-card"><div class="fix-kicker">تصحيح آمن</div>
<div class="fix-title">تصحيحات آمنة مقترحة</div>
{change_rows}<div class="fix-coverage">{esc(coverage)}</div><div class="fix-note">{esc(correction['note'])}</div></div>''',
            unsafe_allow_html=True,
        )

        # لا يوجد زر تطبيق منفصل: التصحيحات الآمنة تُعرض كاقتراحات فقط،
        # ويعيد الكاتب الفحص من الزر الأساسي بعد تعديل النص.

        unresolved_issues = correction.get("unresolved_issues", []) or []
        if unresolved_issues:
            with st.expander(f"فجوات تحتاج مراجعة بشرية ({len(unresolved_issues)})"):
                st.caption("مِعيار يوضح هذه المواضع لكنه لا يعيد صياغتها آليًا عندما لا يملك تصحيحًا آمنًا بما يكفي.")
                for issue in unresolved_issues:
                    st.markdown(
                        f'<div class="gap-item review"><div class="gap-title">{esc(_public_issue_title(issue))}</div>'
                        f'<div class="issue-text">{esc(issue.get("explanation_ar", ""))}</div>'
                        f'<div class="gap-meta"><span class="gap-chip">الأصل: {esc(_issue_source_text(issue))}</span>'
                        f'<span class="gap-chip">الترجمة: {esc(_issue_translation_text(issue))}</span></div>'
                        f'<div class="issue-text"><b>لماذا مراجعة بشرية؟</b> لا يوجد تصحيح آلي محدد يملكه مِعيار بدرجة أمان كافية لهذه الفجوة.</div></div>',
                        unsafe_allow_html=True,
                    )
    elif top_issue and res["status"] != "safe":
        st.markdown(
            '<div class="note"><b>لا توجد تصحيحات آلية آمنة لهذه النتيجة.</b> كل الفجوات المكتشفة تحتاج مراجعة بشرية؛ مِعيار يوضح موضع الخلل وسببه ولا يعيد صياغة النص عندما قد يؤدي ذلك إلى تحريف المعنى.</div>',
            unsafe_allow_html=True,
        )
        with st.expander(f"فجوات تحتاج مراجعة بشرية ({len(ordered_issues)})"):
            for issue in ordered_issues:
                st.markdown(
                    f'<div class="gap-item review"><div class="gap-title">{esc(_public_issue_title(issue))}</div>'
                    f'<div class="issue-text">{esc(issue.get("explanation_ar", ""))}</div>'
                    f'<div class="gap-meta"><span class="gap-chip">الأصل: {esc(_issue_source_text(issue))}</span>'
                    f'<span class="gap-chip">الترجمة: {esc(_issue_translation_text(issue))}</span></div></div>',
                    unsafe_allow_html=True,
                )

    d = res["dimensions"]
    state_label = {
        "changed": "تغيّر مكتشف",
        "preserved": "لم يظهر تغير",
        "uncertain": "غير محسوم",
        "verified": "موثق",
        "unavailable": "غير متاح الآن",
        "not_required": "غير مطلوب",
        "not_enough": "ليست كافية وحدها",
    }

    m = dict(res["meaning_mirror"])
    symbol = "≠" if res["status"] != "safe" and res["issues"] else "="
    st.markdown(
        f"""
<div class="section-head">مرآة المعنى</div>
<div class="mirror">
  <div class="mirror-card"><div class="mirror-label">ما يفهمه قارئ الأصل</div><div>{esc(m.get('arabic_reader',''))}</div></div>
  <div class="delta"><div class="delta-badge">{symbol}</div><span>{'فجوة معنى' if symbol == '≠' else 'متقارب'}</span></div>
  <div class="mirror-card"><div class="mirror-label">ما قد يفهمه قارئ الترجمة</div><div>{esc(m.get('english_reader',''))}</div></div>
</div>
<div class="impact" style="margin-top:10px"><b>الخلاصة الدلالية:</b> {esc(m.get('gap',''))}</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-head">لماذا هذا القرار؟</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="impact"><b>{esc(res["decision_reason"])}</b></div>', unsafe_allow_html=True)
    next_action = {
        "critical": "الخطوة التالية: عدّل الموضع أو المصطلح المبيّن في الفجوات ثم أعد الفحص قبل النشر.",
        "review": "الخطوة التالية: راجع الموضع غير المحسوم مع مرجع موثوق أو مختص، ثم أعد الفحص.",
        "safe": "الخطوة التالية: يمكن متابعة المراجعة التحريرية المعتادة؛ النتيجة تخص نقل المعنى ولا تمثل اعتمادًا شرعيًا للمحتوى الأصلي.",
    }[res["status"]]
    st.markdown(f'<div class="next-action"><b>{esc(next_action)}</b></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-head">ما الذي تحقق منه مِعيار؟</div>', unsafe_allow_html=True)
    rv=res.get("reference_verification",{}) or {}
    ref_issues=[i for i in ordered_issues if i.get("issue_taxonomy")=="SOURCE_INTEGRITY"]
    term_issues=[i for i in ordered_issues if i.get("issue_subtype")=="RELIGIOUS_TERMINOLOGY_DRIFT"]
    ruling_issues=[i for i in ordered_issues if i.get("issue_subtype")=="RULING_TRANSFER_DRIFT"]

    if ref_issues:
        internal_ref_icon="✗"
        internal_ref_text=f"وُجدت {arabic_gap_count_phrase(len(ref_issues))} في تطابق/نسبة المراجع داخل النصين"
    else:
        internal_ref_icon="✓"
        internal_ref_text="لم تظهر فجوة مرجعية بين الأصل والترجمة في النتائج الحالية"

    if rv.get("source_conflict"):
        live_ref_icon="⚠"
        live_ref_text="تعارضت أدلة مصادر خارجية؛ الحالة تحتاج مراجعة بشرية"
    elif rv.get("reference_verified"):
        live_ref_icon="✓"
        live_ref_text="تم استرجاع مرجع خارجي فعلي والتحقق من هويته؛ هذا لا يعتمد ترجمة المستخدم تلقائيًا"
    else:
        live_ref_icon="—"
        live_ref_text="لم يكتمل تحقق خارجي حي يمكن الاعتماد عليه في هذا الفحص"

    if term_issues:
        term_icon="⚠"
        term_text=f"وُجدت {arabic_gap_count_phrase(len(term_issues))} مصطلحية حساسة"
    else:
        term_icon="✓"
        term_text="تم فحص المصطلحات ولم تظهر فجوة مصطلحية في النتائج الحالية"

    if ruling_issues:
        ruling_icon="✗"
        ruling_text=f"وُجدت {arabic_gap_count_phrase(len(ruling_issues))} في نقل درجة حكم مذكورة"
    else:
        ruling_icon="✓"
        ruling_text="لم يظهر تغير محدد في درجة حكم مذكورة"

    translation_icon="✗" if ordered_issues else "✓"
    translation_text=(f"وُجدت {arabic_gap_count_phrase(len(ordered_issues))} في سلامة انتقال المعنى" if ordered_issues else "لم يُكتشف تغير جوهري ضمن نطاق الفحص الحالي")

    st.markdown(
        '<div class="verify-grid">'
        f'<div class="verify-item"><b>{internal_ref_icon} مطابقة المرجع داخل النص</b>{esc(internal_ref_text)}</div>'
        f'<div class="verify-item"><b>{live_ref_icon} التحقق الخارجي الحي</b>{esc(live_ref_text)}</div>'
        f'<div class="verify-item"><b>{term_icon} فحص المصطلحات</b>{esc(term_text)}</div>'
        f'<div class="verify-item"><b>{ruling_icon} انتقال الحكم المذكور</b>{esc(ruling_text)}</div>'
        f'<div class="verify-item"><b>{translation_icon} سلامة انتقال الترجمة</b>{esc(translation_text)}</div>'
        '<div class="verify-item"><b>— صحة الحكم الشرعي الأصلي</b>خارج نطاق النظام؛ مِعيار يقيّم سلامة الانتقال ولا يصدر فتوى مستقلة</div>'
        '</div>',unsafe_allow_html=True)

    # الأدلة التفصيلية موجودة كاملة، لكنها مطوية افتراضيًا حتى لا تزاحم النتيجة الأساسية.
    with st.expander("كيف وصل مِعيار إلى هذا القرار؟"):
        st.markdown(
            '<div class="note"><b>ملخص الدليل:</b> يقارن مِعيار الأصل بالترجمة، ويفحص القيود الدلالية والمصطلحات الحساسة، ويستخدم المرجع الموثوق فقط عندما يتم التعرف عليه واسترجاعه فعليًا. المرجع يدعم قرار الفحص ولا يحول مِعيار إلى مترجم.</div>',
            unsafe_allow_html=True,
        )
        diag = res.get("diagnostics", {}) or {}
        raw_n = int(diag.get("raw_signal_count", len(ordered_issues)))
        root_n = int(diag.get("root_issue_count", len(ordered_issues)))
        suppressed_n = int(diag.get("suppressed_signal_count", max(0, raw_n-root_n)))
        if raw_n > root_n:
            st.caption(f"دمج مِعيار {raw_n} إشارة فحص داخلية في {root_n} فجوة جذرية، وأخفى {suppressed_n} إشارة مكررة أو تابعة حتى لا تتكرر المشكلة نفسها على الكاتب.")
        if os.getenv("MIYAR_DEBUG", "0") == "1":
            with st.expander("Debug trace — للمطور/الحكم فقط"):
                st.json({
                    "confidence": diag.get("confidence", {}),
                    "raw_evidence": diag.get("debug_trace", []),
                })
        if res["evidence_used"]:
            for ev in res["evidence_used"]:
                status = {
                    "live_verified": "مسترجع فعليًا",
                    "local_verified_guideline": "قاعدة معتمدة",
                    "textual_verified": "دليل نصي مباشر",
                    "locator_verified": "تحديد مرجع",
                    "local_curated_rule": "",
                }.get(ev.get("status"), "")
                detail = str(ev.get("detail", "") or "")
                preview = detail[:360] + ("…" if len(detail) > 360 else "")
                source_label = public_source_name(ev.get("source", ""))
                source_line = source_label if not status else f"{source_label} · {status}"
                attrib = evidence_attribution(ev) if ev.get("status")=="live_verified" else source_line
                verify = ev.get("verification") or {}
                verify_note = "المرجع: تم التحقق" if verify.get("reference_verified") else "المرجع: غير مكتمل التحقق"
                if ev.get("status")=="live_verified":
                    verify_note += " · الترجمة: قيد التقييم وليست معتمدة تلقائيًا"
                st.markdown(
                    f'<div class="evidence-card"><div class="evidence-src">{esc(attrib)}</div><div class="evidence-title">{esc(ev.get("title",""))}</div><div class="evidence-detail">{esc(preview)}</div><div class="issue-text"><b>نطاق التحقق:</b> {esc(verify_note)}</div></div>',
                    unsafe_allow_html=True,
                )
                if len(detail) > 360:
                    with st.expander(f'عرض المرجع الكامل — {ev.get("title","")}'):
                        st.write(detail)
        else:
            st.markdown('<div class="note">اعتمد هذا القرار على مقارنة الأصل بالترجمة والفحوص الحالية فقط؛ لم يُستخدم مرجع خارجي في اتخاذه.</div>', unsafe_allow_html=True)

    live_refs = [ev for ev in res["evidence_used"] if ev.get("status") == "live_verified" and ev.get("detail")]
    if live_refs:
        # المرجع هنا دليل تحقق مساعد: نعرض النص الأصلي، ترجمة المستخدم، والترجمة المرجعية
        # فقط عندما تم استرجاع المرجع فعلًا، مع شرح فائدته بلغة الكاتب.
        ar_units=[x.strip() for x in re.split(r"(?<=[.!?؟؛])\s+|\n+", ar.strip()) if x.strip()]
        en_units=[x.strip() for x in re.split(r"(?<=[.!?؟؛])\s+|\n+", en.strip()) if x.strip()]
        chosen={}
        for ref in live_refs:
            idx=ref.get("segment_index") or 1
            old=chosen.get(idx)
            if old is None or (ref.get("language")=="en" and old.get("language")!="en"):
                chosen[idx]=ref
        with st.expander("التحقق من الترجمة بالمراجع الموثوقة"):
            st.markdown(
                '<div class="note">إذا تعرّف مِعيار على آية أو حديث ووجد له ترجمة موثوقة في مصدر معتمد، يستخدمها كمرجع مساعد للتحقق من سلامة النقل. التحقق من المرجع أو استرجاع ترجمة مرجعية لا يعني اعتماد ترجمة المستخدم تلقائيًا ولا اعتماد صحة المحتوى دينيًا.</div>',
                unsafe_allow_html=True,
            )
            for idx,ref in sorted(chosen.items()):
                ref_detail=str(ref.get("detail","") or "")
                ref_preview=ref_detail[:480] + ("…" if len(ref_detail)>480 else "")
                ar_piece=ar_units[idx-1] if 1 <= idx <= len(ar_units) else ar
                en_piece=en_units[idx-1] if 1 <= idx <= len(en_units) else en
                related_issue = next((x for x in ordered_issues if x.get("segment_index") == idx), None)
                benefit = (
                    str(related_issue.get("explanation_ar", ""))
                    if related_issue
                    else "لم يكشف المرجع المسترجع تعارضًا محددًا في هذا الموضع؛ استُخدم للتحقق المساعد فقط."
                )
                st.markdown(
                    f'''<div class="reference-grid">
  <div class="reference-col"><div class="h">النص الأصلي</div><div class="txt">{esc(ar_piece)}</div></div>
  <div class="reference-col"><div class="h">ترجمة المستخدم</div><div class="txt">{esc(en_piece)}</div></div>
  <div class="reference-col reference"><div class="h">الترجمة المرجعية الموثوقة · {esc(public_source_name(ref.get('source','')))}</div><div class="txt">{esc(ref_preview)}</div></div>
</div>
<div class="impact" style="margin-top:8px"><b>ماذا استفاد مِعيار من المرجع؟</b> {esc(benefit)}<br><b>نسبة المصدر:</b> {esc(evidence_attribution(ref))}<br><b>حدود التحقق:</b> تحقق مِعيار من المرجع المسترجع للمقارنة؛ هذا لا يعني أن ترجمة المستخدم أو الحكم الشرعي الأصلي تم اعتمادهما تلقائيًا.</div>''',
                    unsafe_allow_html=True,
                )

    rec = res.get("recognition")
    recognitions = res.get("recognitions") or []
    domain_names = {
        "quran": "القرآن الكريم",
        "hadith": "السنة النبوية والحديث",
        "tafsir": "التفسير",
        "aqeedah": "العقيدة",
        "fiqh": "الفقه والأحكام",
        "seerah": "السيرة والتاريخ",
        "terminology": "المصطلحات الشرعية",
        "general": "لم يتحدد مجال شرعي خاص",
    }
    domains = "، ".join(domain_names.get(x, x) for x in res["source_route"]["domains"])
    if recognitions:
        details=[]
        for item in recognitions[:8]:
            idx=item.get("segment_index")
            rr=item.get("recognition") or {}
            mm=rr.get("match") or {}
            source_piece = ar_units[idx-1] if live_refs and 1 <= idx <= len(ar_units) else "النص المتعرّف عليه"
            if rr.get("kind")=="quran":
                if mm.get("ambiguous"):
                    refs="، ".join(quran_ref_label(x) for x in mm.get("candidates",[])[:5])
                    details.append(f'{esc(source_piece)}: ورد النص في أكثر من موضع قرآني: {esc(refs)}؛ لذلك لم يُخمن مِعيار موضعًا واحدًا.')
                else:
                    details.append(f'{esc(source_piece)}: قرآن <b>{esc(mm.get("surah"))}:{esc(mm.get("ayah"))}</b>.')
            elif rr.get("kind")=="hadith":
                details.append(f'{esc(source_piece)}: حديث، بطاقة HadeethEnc #{esc(mm.get("id",""))}.')
        route_detail="<br>".join(details)
    elif rec and rec["kind"] == "quran":
        mm = rec["match"]
        if mm.get("ambiguous"):
            refs = "، ".join(quran_ref_label(x) for x in mm.get("candidates", [])[:5])
            route_detail = f'تم التعرّف على النص بوصفه قرآنيًا، وورد في أكثر من موضع: {esc(refs)}. لم يخمّن مِعيار مرجعًا واحدًا.'
        else:
            route_detail = f'تم التعرّف على مرجع قرآني: <b>{esc(mm.get("surah"))}:{esc(mm.get("ayah"))}</b>.'
    elif rec and rec["kind"] == "hadith":
        route_detail = "تم التعرّف على نص حديثي، وربطه ببطاقة مرجعية عند توفر الاسترجاع."
    else:
        route_detail = "لم يتحدد نص قرآني أو حديث بثقة؛ لذلك لم يخمّن مِعيار مرجعًا غير متأكد منه."

    if res["unavailable_sources"]:
        with st.expander("مراجع تعذر استرجاعها في هذه المحاولة"):
            for ev in res["unavailable_sources"]:
                st.write(f'{public_source_name(ev.get("source",""))} — {ev.get("title","")}')

    visible_checks = public_check_rows(res["checks"])

    with st.expander("عرض تفاصيل الفحص"):
        st.markdown(f'<div class="technical-mini"><b>المسار المرجعي الداخلي</b><br><b>نوع المحتوى:</b> {esc(domains)}<br>{route_detail}</div>', unsafe_allow_html=True)
        ai = res.get("semantic_ai") or {}
        if ai.get("available") and ai.get("similarity") is not None:
            sim = max(0.0, min(1.0, float(ai["similarity"])))
            pct = round(sim * 100)
            st.markdown(f'<div class="technical-mini"><b>التقارب الدلالي العام: {pct}%</b><br>إشارة مساعدة فقط؛ القرار يعتمد أيضًا على القيود والمصطلحات والأدلة.</div>', unsafe_allow_html=True)
        elif ai.get("status") == "unavailable":
            st.markdown('<div class="technical-mini">التحليل الدلالي غير متاح في هذه المحاولة، واستمر الفحص بالقواعد والمصطلحات والمراجع المتاحة.</div>', unsafe_allow_html=True)

        st.write(f'معرّف التدقيق: {res["audit"]["id"]}')
        st.write(f'قوة الدليل: {res["evidence_tier"]["label"]}')
        for key in ["surface_language", "meaning_transfer", "reference"]:
            x = d[key]
            st.write(f'{x["label"]}: {state_label.get(x["state"], x["state"])} — {x["detail"]}')
        st.markdown('**سجل الفحوص**')
        for check in visible_checks:
            icon = "✅" if check["status"] == "pass" else ("⛔" if check["status"] == "fail" else ("⚠️" if check["status"] == "review" else "◻️"))
            st.write(f'{icon} {check["check"]} — {check["detail"]}')
        if res["suggested_sources"]:
            st.markdown('**مراجع إضافية مناسبة للمجال — لم تُستخدم في هذا القرار**')
            for ev in res["suggested_sources"]:
                st.write(f'{public_source_name(ev.get("source",""))} — {ev.get("detail","")}')

    with st.expander("كيف يعمل مِعيار؟"):
        st.markdown(
            """
يقارن مِعيار المعنى العام، ثم يفحص القيود الحرجة والمصطلحات الشرعية والمراجع الموثوقة بصورة مستقلة. **لا يعتمد على نسبة التشابه وحدها، ولا يصدر حكمًا شرعيًا مستقلًا.**
"""
        )

    if res["abstain"]["needed"]:
        st.markdown('<div class="section-head">الامتناع الآمن</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="impact"><b>{esc(res["abstain"]["reason_ar"])}</b></div>', unsafe_allow_html=True)

    # Human review is a decision state, not a fake routing workflow. It appears only
    # when Mi'yar cannot safely close the case. No UI implies that a real specialist
    # is waiting behind the product.
    saved = None
    if res["status"] == "review":
        st.markdown('<div class="section-head">تحتاج مراجعة بشرية قبل النشر</div>', unsafe_allow_html=True)
        review_reason = (res.get("abstain") or {}).get("reason_ar") or res.get("decision_reason") or "لا تكفي الأدلة الحالية للحسم الآلي بثقة."
        st.markdown(f'<div class="impact"><b>{esc(review_reason)}</b><br><span>لم يُجرِ مِعيار تصحيحًا قاطعًا في هذه الحالة حتى لا يخمّن.</span></div>', unsafe_allow_html=True)

    audit = {
        **res["audit"],
        "decision": res["status"],
        "evidence_tier": res["evidence_tier"],
        "decision_reason": res["decision_reason"],
        "issues": res["issues"],
        "recognition": res.get("recognition"),
        "recognitions": res.get("recognitions", []),
        "evidence_used": res["evidence_used"],
        "source_route": res["source_route"],
        "semantic_ai": res.get("semantic_ai"),
        "human_review": saved,
        "suggested_correction": correction,
        "privacy_note": "لا يتضمن التصدير النصين كاملين افتراضيًا.",
    }
    st.download_button(
        "تنزيل سجل التدقيق",
        json.dumps(audit, ensure_ascii=False, indent=2),
        f'miyar_audit_{res["audit"]["id"]}.json',
        "application/json",
        use_container_width=True,
    )

    st.markdown(
        '<div class="footer-limit"><b>فكرة مِعيار وحدوده:</b> مِعيار لا يصدر أحكامًا شرعية جديدة؛ بل يحمي الحكم والمصطلح والدليل الموجود أصلًا من التحريف أثناء انتقاله بين اللغات، ويستعين بالمصادر الموثوقة للتحقق عند الحاجة. تطابق المرجع لا يعني اعتماد صحة المحتوى دينيًا، وغياب التنبيه ليس ضمانًا مطلقًا للصحة.</div>',
        unsafe_allow_html=True,
    )
