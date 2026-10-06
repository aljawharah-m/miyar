from __future__ import annotations
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
files=[ROOT/'README.md',ROOT/'FINAL_HANDOFF.md',ROOT/'docs'/'JURY_SCORECARD.md',ROOT/'docs'/'CHALLENGE_ALIGNMENT.md',ROOT/'docs'/'QUALITY_REPORT.md',ROOT/'docs'/'DEMO_2_MINUTES.md',ROOT/'docs'/'SUBMISSION_CHECKLIST.md']
forbidden={
 'طبّق كل التصحيحات وأعد الفحص':'V14+ removed the automatic apply/re-check button',
 'طبّق التصحيح وأعد الفحص':'V14+ removed the automatic apply/re-check button',
 'Final Complete V13 Handoff':'stale handoff version',
 'Final UX evidence: Detect → Explain → Correct → Re-check':'stale UX loop',
}
errors=[]
for p in files:
    if not p.exists():
        errors.append(f'missing required doc: {p.relative_to(ROOT)}'); continue
    txt=p.read_text(encoding='utf-8',errors='ignore')
    for phrase,why in forbidden.items():
        if phrase in txt:
            errors.append(f'{p.relative_to(ROOT)} contains stale phrase: {phrase} ({why})')
if errors:
    print('\n'.join(errors)); raise SystemExit(1)
print('Documentation consistency: PASS')
