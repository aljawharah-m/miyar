from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Ensure release-check child scripts can import the project package
# regardless of the caller's working directory or PYTHONPATH.
_MIYAR_CHILD_PYTHONPATH = str(ROOT)
_existing_pythonpath = os.environ.get("PYTHONPATH")
os.environ["PYTHONPATH"] = (
    _MIYAR_CHILD_PYTHONPATH
    if not _existing_pythonpath
    else _MIYAR_CHILD_PYTHONPATH + os.pathsep + _existing_pythonpath
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Directories that are generated locally or belong to third-party dependencies.
# They must never be treated as project source during the release secret scan.
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}

# Binary / generated artifacts that should not be decoded as source text.
SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".zip",
    ".pyc",
    ".pyd",
    ".dll",
    ".so",
    ".dylib",
    ".exe",
    ".bin",
    ".parquet",
}


def run(label: str, *args: str) -> None:
    print(f"\n=== {label} ===")
    process = subprocess.run([sys.executable, *args], cwd=ROOT)
    if process.returncode:
        raise SystemExit(process.returncode)


def scan_public_ui() -> None:
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    forbidden = [
        "sentence-transformers/",
        "تعليل LLM",
        "OPENAI_API_KEY",
        "يعمل التحليل محليًا",
        "الطبقات المستخدمة",
        "جاهزة مبدئيًا للنشر",
    ]
    leaked = [item for item in forbidden if item in app]
    if leaked:
        raise SystemExit(f"Public UI leak check failed: {leaked}")
    print("Public UI leak check: PASS")


def _is_skipped_path(path: Path) -> bool:
    """Return True for third-party/generated paths that are not project source."""
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True

    # Compare path components exactly so names such as "myvenvnotes" are not skipped.
    if any(part in SKIP_DIRS for part in relative.parts[:-1]):
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    return False


def scan_secrets() -> None:
    suspicious: list[str] = []
    patterns = [
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(
            r"(?i)(api[_-]?key|secret[_-]?key|password)\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{16,}"
        ),
    ]

    for path in ROOT.rglob("*"):
        if not path.is_file() or _is_skipped_path(path):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeError):
            continue

        for pattern in patterns:
            if not pattern.search(text):
                continue

            # Example/template files may contain obvious non-secret placeholders.
            if path.name.endswith(".example") and (
                "your_" in text.lower() or "example" in text.lower()
            ):
                continue

            suspicious.append(str(path.relative_to(ROOT)))
            break

    if suspicious:
        raise SystemExit(f"Potential secret material found: {suspicious}")
    print("Secret scan: PASS")


if __name__ == "__main__":
    print("MI'YAR FINAL RELEASE CHECK — deterministic/offline verification")
    scan_public_ui()
    scan_secrets()
    run("PYTEST", "-m", "pytest", "-q")
    run("SOURCE AUDIT", "scripts/source_audit.py")
    run("SOURCE METADATA AUDIT", "scripts/source_metadata_audit.py")
    run("ATTRIBUTION AUDIT", "scripts/attribution_audit.py")
    run("SYNTHETIC ID AUDIT", "scripts/synthetic_id_audit.py")
    run("SACRED CORPUS AUDIT", "evaluation/run_sacred_corpus_audit.py")
    run("QURAN REFERENCE AUDIT", "evaluation/run_quran_reference_audit.py")
    run("HADITH REFERENCE AUDIT", "evaluation/run_hadith_reference_audit.py")
    run("RELEASE SMOKE", "evaluation/run_release_smoke.py")
    run("JURY STRESS", "evaluation/run_jury_stress.py")
    run("BENCHMARK", "evaluation/run_benchmark.py")
    run("ADVERSARIAL", "evaluation/run_adversarial.py")
    run("REPEATABILITY", "evaluation/run_repeatability.py")
    run("LONG TEXT STRESS", "evaluation/run_long_text_stress.py")
    run("ABLATION", "evaluation/run_ablation.py")
    run("RESOURCE PROFILE", "evaluation/run_resource_profile.py")
    run("REVIEWER WORKLOAD EVIDENCE", "scripts/reviewer_workload_evidence.py")
    run("DOC CONSISTENCY", "scripts/doc_consistency_check.py")
    print("\nFINAL RELEASE CHECK: PASS")
