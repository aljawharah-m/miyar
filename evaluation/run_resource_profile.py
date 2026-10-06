from __future__ import annotations

import json
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze

try:
    import resource as _resource  # Unix/macOS only
except ImportError:  # Windows
    _resource=None

CASES=[
 ('الزكاة واجبة.','Charity is obligatory.'),
 ('يجوز للمريض الفطر إذا خاف الضرر.','A sick person must break the fast.'),
 ('عدد الأيام سبعة أيام.','The number of days is five.'),
 ('الصدقة مستحبة والزكاة واجبة.','Charity is recommended and Zakat is obligatory.'),
 ('هذا الحكم خاص بالمسافر.','This ruling applies to everyone.'),
 ('الزكاة واجبة.','Zakat is obligatory.'),
]

# Warm deterministic layers so import/startup cost does not dominate the profile.
for a,b in CASES:
    analyze(a,b,use_live_sources=False,use_semantic_ai=False)

tracemalloc.start()
lat=[]
for _ in range(5):
    for a,b in CASES:
        t=time.perf_counter()
        analyze(a,b,use_live_sources=False,use_semantic_ai=False)
        lat.append((time.perf_counter()-t)*1000)
_,py_peak=tracemalloc.get_traced_memory()
tracemalloc.stop()

memory={
    'python_tracemalloc_peak_mib':round(py_peak/(1024*1024),3),
    'process_peak_rss_mib':None,
    'process_peak_rss_source':None,
}
if _resource is not None:
    raw=_resource.getrusage(_resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes; Linux/BSD commonly report KiB.
    if sys.platform == 'darwin':
        memory['process_peak_rss_mib']=round(raw/(1024*1024),3)
        memory['process_peak_rss_source']='resource.ru_maxrss (bytes on macOS)'
    else:
        memory['process_peak_rss_mib']=round(raw/1024,3)
        memory['process_peak_rss_source']='resource.ru_maxrss (KiB on Linux/Unix)'

report={
 'platform':sys.platform,
 'mode':'offline deterministic layers; live retrieval and semantic model disabled',
 'calls':len(lat),
 'latency_ms':{
     'median':round(statistics.median(lat),3),
     'p95':round(sorted(lat)[max(0,int(len(lat)*0.95)-1)],3),
     'max':round(max(lat),3),
 },
 'memory':memory,
 'note':(
     'Cross-platform profile. tracemalloc measures Python-managed allocation on all supported platforms; '
     'process peak RSS is added when the operating system exposes the resource module. '
     'Deployment latency varies by hardware/network; semantic-model and live-provider timing are measured separately by preflight/baseline runs.'
 )
}
print(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'evaluation'/'resource_profile.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
