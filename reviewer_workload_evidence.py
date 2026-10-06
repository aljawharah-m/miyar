from __future__ import annotations
import re
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.engine import analyze

path = ROOT / 'evaluation' / 'USER_LONG_STRESS_ALIGNMENT.txt'
text = path.read_text(encoding='utf-8')
ars, ens = [], []
for m in re.finditer(r'\[(\d+)\] AR: (.*?)(?=\n\[\1\] EN: )', text, re.S):
    idx = m.group(1)
    ar = m.group(2).strip()
    em = re.search(rf'\[{idx}\] EN: (.*?)(?=\n\n\[\d+\] AR:|\Z)', text[m.end():], re.S)
    if em:
        ars.append(ar)
        ens.append(em.group(1).strip())

result = analyze('\n\n'.join(ars), '\n\n'.join(ens), use_live_sources=False, use_semantic_ai=False)
d = result.get('diagnostics', {})
raw = int(d.get('raw_signal_count', 0))
roots = int(d.get('root_issue_count', len(result.get('issues', []))))
suppressed = int(d.get('suppressed_signal_count', raw - roots))
reduction = ((raw - roots) / raw * 100.0) if raw else 0.0
print(f'raw_signals={raw}')
print(f'root_findings={roots}')
print(f'suppressed_or_merged={suppressed}')
print(f'noise_reduction_pct={reduction:.1f}')
assert raw >= roots > 0
assert suppressed == raw - roots
assert reduction > 50
