# Mi'yar 1.0 — Tools, Models, Services, and Development Disclosure

This document lists the main tools, models, external services, data sources, and development utilities used in Mi'yar 1.0.

Mi'yar is an explainable pre-publication translation safety gate for Islamic content.

Challenge scope:

- Text only
- Arabic → English
- Existing translations
- Human final decision
- No fatwa generation
- No full translation generation from scratch

---

## 1. Runtime Stack

### Python

Primary implementation language for Mi'yar's analysis pipeline, verification logic, tests, and supporting scripts.

### Streamlit

Used to provide the interactive web interface and Live Demo.

### Requests

Used for HTTP communication with supported external reference providers when live retrieval is required.

### SQLite

Used where lightweight local structured storage is required by the application.

---

## 2. Semantic AI

### Sentence Transformers

Mi'yar uses Sentence Transformers for multilingual semantic comparison.

Model used in the challenge release:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Its role includes:

- Arabic–English semantic comparison
- support for detecting possible meaning drift
- producing semantic evidence alongside deterministic rules

The embedding model does not independently decide whether content is safe to publish.

Its output is combined with structural rules, terminology checks, source evidence, and other signals before a finding is produced.

---

## 3. Deterministic Safety Analysis

Mi'yar includes deterministic checks for meaning-sensitive structures such as:

- negation
- exception
- exclusivity
- conditions
- quantities and numbers
- modality and ruling-degree shifts
- sensitive Islamic terminology
- Quran and Hadith reference changes

These checks complement semantic AI instead of relying on a single similarity score.

---

## 4. Evidence Fusion

Mi'yar combines related signals into root findings through an Evidence Fusion stage.

Its purpose is to:

- reduce duplicate alerts
- group symptoms caused by the same underlying issue
- present fewer actionable findings to the reviewer
- preserve traceability to the underlying evidence

In the documented reviewer-workload stress fixture:

`175 raw signals → 59 root findings`

This represents a `66.3%` reduction in review noise within that specific development test.

This is development evidence and is not a claim of universal real-world performance.

---

## 5. External Islamic Reference Services

### QuranEnc

Used for supported Quran-related reference retrieval and verification when live retrieval is available.

Mi'yar distinguishes between:

- reference recognition
- live source retrieval
- externally verified evidence

A reference is not displayed as externally verified unless the source was actually retrieved successfully.

### HadeethEnc

Used for supported Hadith-related reference retrieval and verification.

Synthetic or test identifiers are not sent to the live provider.

If the provider fails or evidence is insufficient, Mi'yar abstains from claiming verification and routes the case to human review.

---

## 6. Source and Evidence Policy

Mi'yar follows a conservative evidence policy:

- no fabricated source verification
- no invented source version
- no false `Verified` state
- provider failures lead to review rather than false confidence
- retrieved evidence may include source URL and retrieval metadata
- the final decision remains human

Additional documentation is available in:

- `SOURCES.md`
- `LICENSES.md`
- `LIMITATIONS.md`

---

## 7. Testing and Verification

### pytest

Used for automated regression and safety testing.

The challenge release includes documented regression, semantic, source-integrity, adversarial, and repeatability development tests.

### Judge Verification

Judges can run:

`python scripts/judge_verify.py`

This provides a reproducible entry point for checking documented release evidence.

### Release Verification

Additional deterministic release checks are included in the repository to verify regression behavior, source safety, and release readiness.

---

## 8. Version Control and Repository

### Git

Used for source version control during development.

### GitHub

Used for:

- public source-code hosting
- challenge submission
- version history
- documentation
- reproducibility for judges

Repository:

`https://github.com/aljawharah-m/miyar`

---

## 9. Deployment

### Streamlit Community Cloud

Used to deploy the challenge Live Demo.

Live Demo:

`https://miyar-gate.streamlit.app/`

The deployed interface demonstrates the Mi'yar safety-gate workflow documented in this repository.

---

## 10. Development Environment

Development and testing were primarily performed using:

- Windows
- Python virtual environment (`venv`)
- Visual Studio Code
- PowerShell
- Git
- GitHub

---

## 11. AI-Assisted Development Disclosure

ChatGPT was used during development as an assistance tool for activities such as:

- brainstorming and refinement
- code review and debugging support
- documentation drafting and editing
- test-case discussion
- presentation and submission preparation

ChatGPT is development assistance only and is **not part of Mi'yar's runtime decision engine**.

Mi'yar does not depend on ChatGPT to produce its publication-safety decision.

Runtime findings are produced by Mi'yar's implemented pipeline, including deterministic checks, semantic comparison, terminology logic, source verification, Evidence Fusion, and human-review policy.

The final decision remains human.

---

## 12. Experimental Development Tools

Local-model experiments were performed during development while evaluating offline and low-cost execution options.

Experimental tools that are not part of the final challenge runtime should not be interpreted as production dependencies.

Only dependencies required by the submitted release are listed in the repository requirements files.

---

## 13. Reproducibility and Evaluation Scope

Reported benchmark and audit results are scoped to their documented development and audit datasets.

They must not be interpreted as:

- universal religious accuracy
- independent field validation
- a guarantee of zero errors on unseen Islamic content

Mi'yar is designed to support human review, not replace it.

For evaluation details, see the benchmark, audit, limitations, and judge-verification documentation included in the repository.
