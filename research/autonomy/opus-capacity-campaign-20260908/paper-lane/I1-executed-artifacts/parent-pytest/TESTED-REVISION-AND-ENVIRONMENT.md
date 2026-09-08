# Tested revision and hash evidence, alongside ORIGINAL-PARENT-COMMAND-PAIRS.json

Recorded 2026-09-08 10:08 UTC. Hashes measured now over the integrated files; no re-execution.

| file | sha256 | bytes |
|---|---|---|
| `research/manuscripts/lint_consistency.py` | `b171bdcaa3371269b28a511be26a6f3af7e7a31feb16932a01d302cf862d1657` | 36454 |
| `research/modalities/tests/test_lint_consistency_identifier_boundary.py` | `3447770754fc14d27a010b617aabbebe54890dbd5a5b55944f6e00c59e278a30` | 9192 |
| `research/modalities/tests/test_lint_consistency.py` | `2d3febf1de38687c238d0dce0b6010771495a018b9498bbb66ce2286ff130738` | 18219 |
| `research/manuscripts/pinned-figures.json` | `966efbe20322fc28137cb82fbf2bdad292db06954eba2f8c4ce26a5747fa82d3` | 153842 |

Integrated at pin `7baeac8e`; native pytest results pushed at `20f19e5f`; corrections at `236b90a9`.

**Environment, as executed (exact, from the retained pairs — not from memory):**
- working directory: `/home/user/Rare-cancers`
- `PYTHONPATH` entries, in order:
  - `/root/.cache/uv/archive-v0/scQZNGqTPsQFR8AXMYebw`
  - `/root/.cache/uv/archive-v0/soxjIm7pzsJHE7gMrfqnZ`
  - `/root/.cache/uv/archive-v0/pWGD9O1xV0c3QQMFfApZX`
  - `/root/.cache/uv/archive-v0/GzB53fsbo4MLF_f9Gk4ta`
  - `/root/.cache/uv/archive-v0/1gToZRPULjR12xbur49UY`
- override used for the pre-fix comparison: `LINT_CONSISTENCY_DIR=/tmp/claude-0/i1-pytest/origtree`
- pytest invoked as `python3 -m pytest <module> -p no:cacheprovider -q`
- stdout/stderr handling and exit capture are visible verbatim in the retained pairs.

⚠ The ============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/user/Rare-cancers
plugins: xdist-3.8.0
collected 12217 items / 4 errors / 1 skipped

==================================== ERRORS ====================================
_ ERROR collecting research/autonomy/opus-capacity-campaign-20260908/paper-lane/I1-executed-artifacts/work/test_lint_consistency.py _
import file mismatch:
imported module 'test_lint_consistency' has this __file__ attribute:
  /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/I1-executed-artifacts/orig/test_lint_consistency.py
which is not the same as the test file we want to collect:
  /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/I1-executed-artifacts/work/test_lint_consistency.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
_____ ERROR collecting research/modalities/tests/test_lint_consistency.py ______
import file mismatch:
imported module 'test_lint_consistency' has this __file__ attribute:
  /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/I1-executed-artifacts/orig/test_lint_consistency.py
which is not the same as the test file we want to collect:
  /home/user/Rare-cancers/research/modalities/tests/test_lint_consistency.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
_ ERROR collecting research/modalities/tests/test_lint_consistency_identifier_boundary.py _
import file mismatch:
imported module 'test_lint_consistency_identifier_boundary' has this __file__ attribute:
  /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/I1-executed-artifacts/work/test_lint_consistency_identifier_boundary.py
which is not the same as the test file we want to collect:
  /home/user/Rare-cancers/research/modalities/tests/test_lint_consistency_identifier_boundary.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
_ ERROR collecting scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py _
import file mismatch:
imported module 'test_a_tier_budget_is_a_decision_somebody_took' has this __file__ attribute:
  /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/inputs/source-index/scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py
which is not the same as the test file we want to collect:
  /home/user/Rare-cancers/scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
=============================== warnings summary ===============================
research/manuscripts/claim_coverage.py:439
research/manuscripts/claim_coverage.py:439
research/manuscripts/claim_coverage.py:439
  /home/user/Rare-cancers/research/manuscripts/claim_coverage.py:439: DeprecationWarning: invalid escape sequence '\s'
    """Find a censused sentence in the RAW file, tolerating everything `_prose` stripped out of it.

research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py:2
research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py:2
research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py:2
  /home/user/Rare-cancers/research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py:2: DeprecationWarning: invalid escape sequence '\d'
    """Every number the FUSION-PARTNER manuscript prints, tied to the artifact field that computes it.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR research/autonomy/opus-capacity-campaign-20260908/paper-lane/I1-executed-artifacts/work/test_lint_consistency.py
ERROR research/modalities/tests/test_lint_consistency.py
ERROR research/modalities/tests/test_lint_consistency_identifier_boundary.py
ERROR scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py
!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!!
================== 1 skipped, 6 warnings, 4 errors in 52.16s =================== package was **already present in the local uv cache**; nothing was installed and no network was used. Versions: pytest 9.1.1 (`scQZ…`) alongside a cached 9.0.2 (`8uoH…`, unused).
