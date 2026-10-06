from __future__ import annotations
import sys, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from core.semantic_ai import run_semantic_ai
from core.sources import retrieve_reference_evidence, icadb_health, fetch_hadeethenc
from core.recognition import recognize_quran

print("MI'YAR PREFLIGHT — local runtime + live evidence providers")

print("1) Local full-Quran locator...")
q=recognize_quran("وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا",live=False)
q_ok=bool(q and q.get('surah')==5 and q.get('ayah')==6)
print("local Quran locator:", "PASS" if q_ok else "FAIL")
if not q_ok:
    sys.exit(2)

print("2) Local multilingual semantic model...")
ai=run_semantic_ai("لا يجوز هذا إلا عند الضرورة","This is not permissible except in case of necessity",enabled=True)
print(json.dumps({k:v for k,v in ai.items() if k not in {"issue","error","model"}},ensure_ascii=False,indent=2))
if not ai.get("available"):
    print("ERROR: local semantic AI is not ready.")
    print(ai.get("error",""))
    sys.exit(2)

print("3) QuranEnc live retrieval...")
rec,evidence=retrieve_reference_evidence("اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",live=True)
quranenc_ok=any(e.get("source")=="QuranEnc" and e.get("status")=="live_verified" for e in evidence)
print("QuranEnc:", "PASS" if quranenc_ok else "WARN — unavailable in this run; Mi'yar will not claim live verification")

print("4) ICADB live health...")
ic=icadb_health()
print("ICADB:", "PASS" if ic.get('ok') else f"WARN — unavailable in this run (HTTP {ic.get('code')})")

print("5) HadeethEnc live retrieval...")
h=fetch_hadeethenc("4560","en")
h_ok=h.get('status')=='live_verified'
print("HadeethEnc:", "PASS" if h_ok else "WARN — unavailable in this run; Mi'yar will not claim live verification")

print("6) Ready.")
print("Note: TerminologyEnc, Dorar, the Kuwaiti Fiqh Encyclopedia, Byenah, IslamHouse and IslamEnc are routed reference sources unless a case retrieves them explicitly; they are not mislabeled as evidence-used merely because they are in the reference catalog.")
print("Run: python -m streamlit run app.py")
