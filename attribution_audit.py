from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
app=(ROOT/'app.py').read_text(encoding='utf-8')
licenses=(ROOT/'LICENSES.md').read_text(encoding='utf-8')
sources=(ROOT/'docs'/'SOURCES.md').read_text(encoding='utf-8')
for provider in ['QuranEnc','HadeethEnc']:
    if provider not in licenses: errors.append(f'LICENSES missing {provider}')
    if provider not in sources: errors.append(f'SOURCES missing {provider}')
for marker in ['evidence_attribution','source_version','retrieved_at']:
    if marker not in app: errors.append(f'UI attribution pipeline missing {marker}')
report={'errors':errors,'policy':'Retrieved provider text is displayed with source attribution; upstream version is shown when provided, never fabricated.'}
(ROOT/'evaluation'/'attribution_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors: raise SystemExit(1)
