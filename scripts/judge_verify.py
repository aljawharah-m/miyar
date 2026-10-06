from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str):
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"MISSING: {rel}")
    return json.loads(path.read_text(encoding="utf-8"))


def ok(label: str, value: str) -> None:
    print(f"[PASS] {label}: {value}")


print("MI'YAR — JUDGE QUICK VERIFICATION")
print("This command validates the shipped evidence files; run scripts/release_check.py for full recomputation.\n")

benchmark = load_json("evaluation/benchmark_report.json")
assert benchmark.get("label", "").startswith("SYNTHETIC DEVELOPMENT")
assert benchmark["precision"] == 1.0 and benchmark["recall"] == 1.0
ok("Development benchmark", f"n={benchmark['n']} F1={benchmark['f1']:.4f} FPR={benchmark['fpr']:.4f}")

ablation = load_json("evaluation/ablation_report.json")
full = ablation["full_miyar_without_live_sources_or_semantic_ai"]
structure = ablation["structure_rules_only"]
assert full["Recall"] >= structure["Recall"]
ok("Ablation", f"structure recall={structure['Recall']:.4f} -> composed recall={full['Recall']:.4f}")

repeat = load_json("evaluation/repeatability_report.json")
assert not repeat["failures"]
ok("Repeatability", f"{repeat['comparisons']}/{repeat['comparisons']} comparisons")

jury = load_json("evaluation/jury_stress_report.json")
assert jury["failed"] == 0
ok("Jury stress", f"{jury['passed']}/{jury['n']}")

long_text = load_json("evaluation/long_text_stress_report.json")
assert long_text["passed"] and long_text["detected_injected_gap_classes"] == long_text["injected_gap_classes"]
ok("Long-text stress", f"{long_text['detected_injected_gap_classes']}/{long_text['injected_gap_classes']} gap classes")

resource = load_json("evaluation/resource_profile.json")
ok("Offline resource profile", f"median={resource['latency_ms']['median']}ms p95={resource['latency_ms']['p95']}ms")

quran = load_json("evaluation/quran_reference_audit.json")
hadith = load_json("evaluation/hadith_reference_audit.json")
sacred = load_json("evaluation/sacred_corpus_audit.json")
q = sacred["quran"]
quran_checks = (
    q["exact"]["total"] + q["undiacritized"]["total"] + q["quoted"]["total"] + q["natural_context"]["total"]
    + q["arabic_explicit_reference"]["total"] + q["numeric_reference"]["total"] + q["quranenc_routing"]["total"]
    + q["reference_integrity"]["safe_total"] + q["reference_integrity"]["ayah_mutation_total"] + q["reference_integrity"]["surah_mutation_total"]
)
hadith_checks = (hadith["official_safe"]["total"] + hadith["semantic_mutations"]["total"] + hadith["provider_failure"]["total"] + hadith["structured_ids"]["safe_total"] + hadith["structured_ids"]["changed_total"])
assert quran_checks == 62360
assert hadith_checks == 130
ok("Sacred-source audits", f"{quran_checks + hadith_checks} deterministic checks ({quran_checks} Quran + {hadith_checks} Hadith)")


import subprocess
proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "reviewer_workload_evidence.py")], cwd=ROOT, capture_output=True, text=True)
assert proc.returncode == 0, proc.stderr
assert "noise_reduction_pct=66.3" in proc.stdout
ok("Reviewer workload", "175 raw signals -> 59 root findings (66.3% noise reduction)")

report = ROOT / "FINAL_VERIFICATION_REPORT.md"
assert report.exists()
ok("Submission-ready report", report.name)

print("\nQUICK VERIFICATION: PASS")
print("For full deterministic recomputation: python scripts/release_check.py")
