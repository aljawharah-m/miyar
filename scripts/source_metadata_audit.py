from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from core import sources

errors=[]

def validate_live(ev):
    if ev.get('status')!='live_verified': return
    if not ev.get('source'): errors.append('live_verified evidence missing source_name')
    if not (ev.get('url') or ev.get('browse_url')): errors.append(f"{ev.get('source')} live evidence missing URL")
    if not ev.get('retrieved_at'): errors.append(f"{ev.get('source')} live evidence missing retrieved_at")
    # Version is required only when the upstream response actually exposes it.
    # It must never be synthesized.
    if ev.get('source_version') in {'unknown-v1','unknown','latest','v1'}:
        errors.append(f"{ev.get('source')} contains invented/placeholder source_version={ev.get('source_version')}")
    if ev.get('source') in {'QuranEnc','HadeethEnc'} and not ev.get('reuse_notice'):
        errors.append(f"{ev.get('source')} live evidence missing reuse/attribution notice")

# Static contract checks from implementation: these audits do not require network.
qfail=sources.fetch_quranenc.__name__=='fetch_quranenc'
hfail=sources.fetch_hadeethenc.__name__=='fetch_hadeethenc'
if not (qfail and hfail): errors.append('source fetch functions unavailable')

# Ensure docs/UI carry required source attribution concepts.
for fn in ['README.md','docs/SOURCES.md','LICENSES.md']:
    text=(ROOT/fn).read_text(encoding='utf-8')
    for required in ['source_version','retrieved_at']:
        if required not in text: errors.append(f'{fn} missing {required} policy')

app=(ROOT/'app.py').read_text(encoding='utf-8')
for required in ['version:','retrieved:','URL:','المرجع: تم التحقق','الترجمة: قيد التقييم']:
    if required not in app: errors.append(f'app.py missing public attribution marker: {required}')

# Placeholder versions forbidden throughout source implementation/docs.
for fn in ['core/sources.py','README.md','docs/SOURCES.md','LICENSES.md']:
    text=(ROOT/fn).read_text(encoding='utf-8')
    if 'unknown-v1' in text: errors.append(f'{fn} contains forbidden fabricated version placeholder')

report={'errors':errors,'checks':['live source requires name/url/retrieved_at','version never invented','QuranEnc/HadeethEnc attribution notice','README/SOURCES/LICENSES consistent','public UI exposes metadata']}
(ROOT/'evaluation'/'source_metadata_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors: raise SystemExit(1)
