---
id: DOC-SPRINT-S37-ERROR-BODIES
title: "S37-ERROR-BODIES — 44 handlers discard the server's explanation; 4 of them turn a failure into a measured absence, and the two the loop runs on were not among them"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S37-ERROR-BODIES — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S37-ERROR-BODIES — the census, the classification, and the two instruments fixed

**Item(s):** S24-CALIBRATION §5(d) item 3 (*"it is not my bug alone — it is the repo's default"*),
serving CLAUDE.md §4 (root-cause with a real diagnostic; an absent reading is not a reading of absence).

**Owned paths:** `research/autonomy/await_ci.py`, `research/autonomy/gates_verdict.py`,
`research/autonomy/tests/test_an_error_body_is_the_diagnosis.py` (new),
`research/autonomy/sprint-2026-09-01/S37-ERROR-BODIES.md`

**Started (UTC):** 2026-09-01T20:37Z **Finished (UTC):** 2026-09-01T21:10Z

---

## Verdict

**PARTIAL — fixed, with one refutation of the framing and one incident that is bigger than this seat.**

1. ✅ **S24's count reproduces, and the defect is real.** My own AST census: **59** `except ...HTTPError`
   handlers under `research/` and `scripts/`, **15 keep** the response body, **44 discard** it (§1).
2. ⭐ **BUT 44 SITES ARE NOT 44 DEFECTS, AND REPORTING THEM AS SUCH WOULD BE ITS OWN OVERCLAIM.**
   Classified against a stated test: **4 are class A** — the failure becomes indistinguishable from a
   measured absence — and **40 are class B**, a thinner log line with the failure still visibly a
   failure. All 44 named in §3; the four are named again in §3.1 with what each one silently shortens.
3. ⛔ **REFUTED, IN PART: the two files this seat was pointed at are class B, not class A.**
   `await_ci.py` **cannot** report green on an HTTP error — the `except` branch has no path to
   `return 0`, established by reading and now pinned by a test — and `gates_verdict.py` correctly
   leaves `gates_green` **unmeasured**. Neither manufactures a false absence. What they did do is
   destroy the operator's only diagnostic, and on `await_ci` that also **manufactured the exact fake
   stall the file's own docstring says it exists to remove** (§4). Both are fixed anyway, on those
   grounds and not on the stronger ones.
4. ⛔⛔ **AND THE THING THE DRIVER MUST READ FIRST IS NOT ABOUT ERROR BODIES AT ALL: at
   2026-09-01T20:55:10Z a concurrent seat ran `git reset --hard` on the shared tree and reverted
   ~38 tracked files across at least eight seats.** Measured in §6. My two files were among them; I
   re-applied from a script. Other seats' work may be gone and they will not know.

---

## 1 · The census, reproduced with my own instrument

⛔ I did not relay S24's number. The command, verbatim, is
`/tmp/.../scratchpad/census.py` and its whole discriminating logic is:

```python
# for every .py under research/ and scripts/, parsed with ast:
#   a handler counts if it is an ast.ExceptHandler whose type mentions HTTPError
#     (walking Name/Attribute nodes, so a tuple `(URLError, HTTPError, OSError)` counts)
#   it KEEPS the body if any ast.Call inside the handler has func.attr == "read"
for n in ast.walk(tree):
    if isinstance(n, ast.ExceptHandler) and n.type is not None and "HTTPError" in names_in(n.type):
        keeps = any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                    and c.func.attr == "read" for c in ast.walk(n))
```

```
except-HTTPError handlers total:                 59
except-HTTPError handlers that KEEP the body:    15
except-HTTPError handlers that DISCARD the body: 44
```

**Against S24's reported 14 keep / 46 discard.** I also reimplemented S24's instrument (grep every
line containing both `except` and `HTTPError`, then ask whether the next eight lines contain
`.read()`) and got **14 / 47 = 61**. Diffing the two site lists resolves the gap exactly and there is
no residue:

- The window instrument finds **two sites the AST does not**, and **both are prose**:
  `research/modalities/s_calibrator_survey.py:72` (a docstring sentence *"the `except HTTPError … if
  e.code == 204` guard written for it can never fire"*) and
  `research/modalities/tests/test_gpu_backend.py:499` (a comment, *"its only handler was `except
  HTTPError`"*). Neither is a handler.
- The AST finds none the window misses.
- ⭐ So **the AST census is the correct one**, and S24's total was inflated by two comments. The
  remaining one-site drift (46 → 44 discarders) is the tree moving under a twelve-seat sprint; it is
  not a disagreement about method.

⚠ **A LIMITATION OF THE INSTRUMENT, DISCLOSED BECAUSE IT AFFECTS ANY FOLLOW-UP THAT USES THE COUNT
AS A PROGRESS METRIC.** My fix does not call `.read()` *inside* the handler — it calls
`describe_http_error(exc)`, which reads. So **the census still counts my two fixed sites as
discarders**, and will keep counting them that way. A driver re-running this to measure progress must
add `describe_http_error` to the keeps-test, or the number will not move when the defect is fixed.

---

## 2 · The classification test I used, stated before the results

For each discarding handler: **after this handler runs, can a reader of the ARTIFACT distinguish
"the server refused" from "there is nothing there"?**

- **Class A — the finding.** No error marker travels with the data. The value that reaches the
  artifact or the decision is a shortened list, a `None`, a zero or an empty set that is byte-identical
  to a legitimate empty result. This is the shape S24 named: *"an empty list from a fusion probe is
  indistinguishable from 'no validated fusion-junction epitopes exist'."*
- **Class B — tidiness.** The failure stays visibly a failure: the handler re-raises, aborts, or
  records `http`/`error`/`readable: false`/`ok: false` **beside the datum**. Only the server's
  explanation is lost, so the cost is an operator with less to go on — real, but not a false absence.

⚠ **stderr and stdout do not make a site class B.** A printed line lives in a CI log that is
transient and unlinked from the artifact a future session reads. Two of the four class-A sites do
print the status code; they are still class A, and the mitigation is noted per site.

---

## 3 · All 44 discarding sites, classified

**Class A: 4 · Class B: 40**

⚠ **Line numbers are as of this seat's census.** The two owned sites are shown at their **post-fix**
positions; S24 named them at their pre-fix positions, `await_ci.py:83` and `gates_verdict.py:189`.
Same two handlers.

| site | function | what the handler does next | class |
|---|---|---|---|
| `research/autonomy/await_ci.py:175` *(was `:83`)* | `poll()` | `continue` / `print` / `return 2` | B — *fixed, §4* |
| `research/autonomy/gates_verdict.py:198` *(was `:189`)* | `main()` | `print` / `return 0` | B — *fixed, §4* |
| `research/modalities/aso_offtarget_tissue_expression.py:480` | `_ncbi_get()` | `raise` | B |
| `research/modalities/atr_hrd_sarcoma_series.py:133` | `_get()` | `break` → returns `(None, "FAILED after N tries: HTTP 404")` | B |
| `research/modalities/cys_chemoproteomics_precheck.py:174` | `fetch()` | `return (e.code, b'', "HTTPError %d")` | B |
| `research/modalities/ddddg_known_answer_search.py:267` | `post_json()` | `return {'total_count': 0, 'result_set': []}` on 204 | B — **but see §3.2, the branch is unreachable** |
| `research/modalities/deepternary_blind_controls.py:189` | `search_candidates()` | `continue` | **A** |
| `research/modalities/deepternary_blind_controls.py:207` | `_rest()` | `return None` | **A** |
| `research/modalities/e3_recruiter_staging.py:221` | `_http()` | appends `url [HTTP 404]` to `_URLS_USED`, `return None` | B |
| `research/modalities/e3_vhl_ligand_recheck.py:62` | `_get_json()` | `return {'_fetch_error': ...}` | B |
| `research/modalities/emc_data_level_sweep.py:385` | `_get()` | sets `rec['http']`, `rec['error']`, `break` | B |
| `research/modalities/emc_data_level_sweep.py:417` | `_get_bytes()` | sets `rec['http']`, `rec['error']`, `break` | B |
| `research/modalities/emc_data_level_sweep.py:950` | `_head()` | sets `rec['http']`, `rec['error']` | B |
| `research/modalities/emc_ret_cistrome.py:520` | `get()` | `_record(url, code, error=reason)`, `return None` | B |
| `research/modalities/emc_ret_cistrome.py:581` | `stream_lines()` | `_record(url, code, error=reason)` | B |
| `research/modalities/emc_ret_cistrome.py:613` | `_post_symbols()` | `_record(...)`, `return None` | B |
| `research/modalities/fleet_supervision_alarm.py:170` | `fetch_runs()` | `last = "HTTP %d %s"` → returns `(None, last)`, `runs_readable: False` | B |
| `research/modalities/fusion_junction_census.py:223` | `_get()` | `return ('', e.code, "HTTPError %d")` | B |
| `research/modalities/gse243553_eno3_overlap.py:149` | `fetch()` | sets `rec['http']`, `rec['error']`, `rec['state']='not_retrieved'` | B |
| `research/modalities/gse243553_eno3_overlap.py:768` | `_get_binary()` | same | B |
| `research/modalities/nr4a3_af2_nmr_rmsd.py:175` | `_fetch_af2()` | `continue` → all versions fail → `raise RuntimeError` | B |
| `research/modalities/nr4a3_e3_stage.py:312` | `_get()` | `raise NotAvailable` | B |
| `research/modalities/nr4a3_e3_stage.py:333` | `_post_json()` | `return {'result_set': []}` on 204 | B — **§3.2, unreachable** |
| `research/modalities/nr4a3_md.py:68` | `main()` | `continue` → all versions fail → `sys.exit("ABORT: …")` | B |
| `research/modalities/nr4a3_metad.py:596` | `_fetch_af_model()` | `continue` → all versions fail → `sys.exit("ABORT: …")` | B |
| `research/modalities/nr4a3_thiol_environment.py:118` | `fetch()` | `return (e.code, b'', "HTTPError %d")` | B |
| `research/modalities/nrv04_retro_host_history.py:105` | `main()` | `print` then `return out` (**`hits: []`, `runs_scanned: 0`**) | **A** |
| `research/modalities/replicate_standard_harvest.py:221` | `_get()` | `return (e.code, "<HTTPError %d %s>")` | B |
| `research/modalities/s4_lane_inputs_fetch.py:71` | `get()` | `return (e.code, b'', "HTTPError %d")`, recorded into the manifest as `http`/`error` | B |
| `research/modalities/safe2025_verify.py:48` | `fetch_fulltext_xml()` | `return {'http_status': e.code, 'ok': False, 'body': ''}` | B |
| `research/modalities/selcal_reference_selectivity.py:137` | `epmc_fulltext_xml()` | `return None` | B — **near-A, refuted; see §3.3** |
| `research/modalities/selcal_reference_selectivity.py:208` | `chemcomp()` | `return {'ccd': ccd, 'error': ...}` | B |
| `research/modalities/selcal_reference_selectivity.py:233` | `entry_ligands()` | `return {'pdb': pdb, 'error': ...}` | B |
| `research/modalities/selcal_reference_selectivity.py:240` | `entry_ligands()` | `continue` | **A** |
| `research/modalities/selcal_reference_selectivity.py:278` | `run()` | sets `rec['error']` + `rec['_absent_reading']`, appends, `continue` | B — *exemplary* |
| `research/modalities/selcal_vast_launch.py:1497` | `self_dispatch()` | `print("could NOT arm … rather than assume it fired")`, `return False` | B |
| `research/modalities/stuck_run_guard.py:127` | `scan()` | `rec['readable'] = False`, `rec['error'] = ...` | B — *exemplary* |
| `research/modalities/stuck_run_guard.py:139` | `scan()` | `rec['in_progress_readable'] = False` | B — *exemplary* |
| `research/modalities/stuck_run_guard.py:148` | `scan()` | appends to `rec['spared']` with *"never cancel on an absent reading"* | B — *exemplary* |
| `research/modalities/stuck_run_guard.py:187` | `scan()` | appends to `rec['cancel_failed']` + a `::warning` annotation | B |
| `research/modalities/supervisor_resurrect.py:271` | `_api_get()` | `print("that is UNREADABLE, not empty")`, `return None` → caller returns `None` = UNREADABLE | B — *exemplary* |
| `research/modalities/supervisor_resurrect.py:327` | `dispatch()` | `return (False, "dispatch of %s FAILED (%s)")` | B |
| `research/modalities/zaienne_selectivity_verify.py:40` | `fetch_fulltext_xml()` | `return {'http_status': e.code, 'ok': False, 'body': ''}` | B |
| `scripts/trigger_scan.py:118` | `_get()` | `last = e` → `raise RuntimeError("GET failed after N tries: … :: %s")` | B |

### 3.1 · The four class-A sites, and what each one silently shortens

1. ⛔ **`research/modalities/selcal_reference_selectivity.py:240` — `entry_ligands()`. The worst of
   the four, because the datum it shortens is an INVENTORY.** A failed
   `nonpolymer_entity/<pdb>/<ent>` read is swallowed by a bare `continue`, so `comps` — returned as
   `nonpolymer_ccd_ids` and consumed by `run()` to build `doc["ligands"]` — comes back **short, with
   no error field anywhere on the entry record**. A structure whose PROTAC entity failed to fetch is
   byte-identical to a structure that has no PROTAC. ⚠ And the function's own docstring, three lines
   above the handler, says *"An absent reading is not a reading of absence (CLAUDE.md §4)"* — the
   sentence is correct and the code below it does the opposite. This is the highest-value one-line
   fix in the set.
2. ⛔ **`research/modalities/nrv04_retro_host_history.py:105` — `main()`.** On a failed run listing it
   prints and returns `out`, which at that point reads `{"runs_scanned": 0, "hits": []}` **with no
   error key**. The artifact then says *no supervision line names this unit's hosts* when the truth is
   *we could not ask*. These are the rental death certificates; "no certificate found" is exactly the
   conclusion a reader would draw. Mitigation: the failure is on stdout. It is not in the artifact.
3. ⛔ **`research/modalities/deepternary_blind_controls.py:189` — `search_candidates()`.** A non-204
   HTTP error writes one stderr line and `continue`s; the returned candidate-ID set is silently short
   and carries no marker. A blind-control set that lost half its search terms to 5xx reads downstream
   as *"few candidates of this kind exist"* — in a module whose entire purpose is a control.
4. ⚠ **`research/modalities/deepternary_blind_controls.py:207` — `_rest()`. The weakest of the four,
   and named anyway.** It returns `None` for every error, and its docstring says `None` means
   "404/obsolete tolerated". Callers test `if j:`. So a 500 or a 403 is indistinguishable from the
   404 the design deliberately treats as absence. The status code does reach stderr for non-404s,
   which is why this is the weak one — but the artifact cannot tell.

### 3.2 · A SECOND defect found while classifying, same family, not a body-discard

⛔ **Three `if e.code == 204` branches are unreachable, proven twice.**
`ddddg_known_answer_search.py:267`, `nr4a3_e3_stage.py:333` and `deepternary_blind_controls.py:189`
each map an HTTP 204 to a legitimate empty result. **`urlopen` never raises `HTTPError` for a 204.**

- From the stdlib source: `urllib.request.HTTPErrorProcessor.http_response` raises only
  `if not (200 <= code < 300)`.
- Live, against a local server answering 204 — because a source reading is not a run:
  `204 -> NO HTTPError raised; status=204 body=b''`.

So a real zero-hit answer arrives as a 200 with an empty body and dies in `json.load`/`json.loads`
— which in `deepternary` is caught by a bare `except Exception: continue` (another silent shortening)
and in the other two falls through to the retry ladder and is retried three times for nothing.
⭐ **`research/modalities/s_calibrator_survey.py`'s docstring already records this exact measurement
and fixes it at its own transport. It was never propagated to the other three.** Not mine to fix
(outside owned paths); sequenced in §8.

### 3.3 · One near-A that I refuted, recorded so a follow-up seat does not re-litigate it

`selcal_reference_selectivity.py:137` (`epmc_fulltext_xml` → `None`) looks like a textbook false
absence. It is not: the caller at line 295 handles `xml is None` explicitly and writes
`_fulltext_absent: "declared open access but fullTextXML did not return — an absent reading, not a
reading of absence"`. The absence is flagged; only the *reason* (404 vs 403 vs 500) is lost. **Class
B.** Likewise `e3_recruiter_staging.py:221`, where the code reaches the artifact through
`_URLS_USED`, and the three AlphaFold version-fallback loops
(`nr4a3_af2_nmr_rmsd`, `nr4a3_md`, `nr4a3_metad`), whose terminus is a hard `raise`/`sys.exit`.

---

## 4 · The two owned instruments: the reading asked for, and the fix

### 4.1 · ⛔ Can a discarded body make `await_ci` report GREEN? **No — established, and now pinned.**

The `except` clause in `poll()` has three exits — `return 2`, `return 2`, `continue` — and **no path
to `return 0`.** `return 0` is reachable only from the success branch, which requires a parsed
response with a non-empty `workflow_runs` list. A read that raises therefore cannot become a green
verdict. That is the honest answer in the safe direction, and
`test_an_http_error_can_NEVER_make_the_poller_report_green` now asserts it across
`{400, 401, 403, 404, 422, 500, 503}` so a future edit cannot move it quietly.

### 4.2 · ⛔ Can it report UNKNOWN where a real answer existed? **Yes, and it did so expensively.**

Pre-fix, every HTTP failure printed one line: `API read failed (HTTPError)`. Not the status, not the
reason, not the body. So **a wrong repo slug (404), an expired credential (401), a rejected query
(422), a rate limit (403 + `X-RateLimit-Remaining: 0`) and a genuine GitHub hiccup (502) were five
different problems wearing one sentence** — after which the poller retried each of them **eight times
at 45 s** and reported `UNKNOWN`. For the deterministic ones that is **six minutes of fabricated
waiting followed by no information**, which is precisely the fake stall the file's own docstring says
it exists to remove, arriving through the error path instead of through a short sha.

⚠ **The file already contained the prediction.** The comment above the token read said an
exported-empty token *"earns a 401, which this poller's HTTP handling would report as an API hiccup
rather than as the quoting accident it is."* That sentence was an accurate description of a defect,
sitting in the file, load-bearing for nothing. It is now corrected in place rather than deleted.

**Live end-to-end proof, $0, against the real API** — a 403 from this sandbox's egress:

```
[await-ci]     0s  API read failed, attempt 1: HTTP 403 Forbidden — body: {"message":"GitHub access
to this repository is not enabled for this session. Use add_repo to request access. …"}
…
await_ci real exit code = 2
```

⭐ **Read what that body contains: the remedy.** Pre-fix this run printed `API read failed
(HTTPError)` four times and then `UNKNOWN`, and an operator had nothing. Post-fix the server names
the fix in its own words. Exit code **2**, confirmed separately — never green.

### 4.3 · What changed, path by path

- **`research/autonomy/await_ci.py`** — added `describe_http_error(exc, max_body=400)`: status,
  reason, the `X-RateLimit-*` pair when present, and a bounded, whitespace-collapsed body. Three
  distinguishable states — a body, `(empty body)`, `(body unreadable: …)` — because "I did not read
  it" and "there was nothing there" are opposite facts. Added `FATAL_HTTP = {401, 404, 410, 422}`:
  statuses that will not change by asking again are refused on the **first** read with a line saying
  so, still exit 2. ⚠ **403 is deliberately excluded** — on this API it is both a rate limit and a
  permission denial, and only the body and headers separate them, so it stays on the retry ladder
  where the describer now prints the distinction. The handler calls the describer **once** (the body
  is a stream) and every later line prints that string. Module docstring and the stale token comment
  corrected in place.
- **`research/autonomy/gates_verdict.py`** — imports the describer from `await_ci` rather than
  copying it (one fact, one place) and uses it in the fail-closed handler. **Behaviour is otherwise
  unchanged and deliberately so**: it still writes no file and still exits 0, so `gates_green` stays
  `unmeasured`. The gain is that `unmeasured` now arrives with a cause attached — a rate limit that
  clears in four minutes and a token that will never work again no longer print the same sentence.
  ⚠ `str(HTTPError)` yields `HTTP Error 403: Forbidden`: the reason, never the body. That is why
  this site counted as a discarder despite already interpolating the exception.
- **`research/autonomy/tests/test_an_error_body_is_the_diagnosis.py`** (new, 15 tests).

### 4.4 · Mutation test — in a scratch copy, never the live tree

Pre-fix copies of both files were fetched with `git show HEAD:<path>` into
`/tmp/.../scratchpad/mut/autonomy/`, the test file copied beside them, and pytest run from that
directory so `sys.path` resolved to the scratch copies:

```
13 failed, 2 passed          # against HEAD (the mutant)
15 passed in 0.16s           # against the fix
```

⭐ **The two that pass pre-fix are the two that should**, and I am recording that rather than
tightening them until they fail: `test_an_http_error_can_NEVER_make_the_poller_report_green` pins
behaviour that was already correct (§4.1), and `test_the_gate_reader_still_fails_closed_on_a_bodiless_error`
pins the `URLError` path, which never had a body to lose. A guard that fails on the pre-fix code for
the *wrong* reason is worse than one that honestly passes.

⛔ **The assertion that carries the finding is `test_two_different_400s_do_not_render_identically`.**
It is the one no `str(exc)` implementation can pass, because `str(HTTPError)` is `HTTP Error 400: Bad
Request` for both — which is how 90 different failures came to wear one sentence.

---

## 5 · Gates run

- `python3 -m pytest research/autonomy/tests/test_an_error_body_is_the_diagnosis.py -q` → **15 passed**.
- Both modules import cleanly and `gates_verdict.await_ci is await_ci` holds.
- `python3 research/autonomy/await_ci.py --sha deadbeef` still refuses a short sha with its existing
  message (argparse and the sha guard untouched).
- ⚠ **The full `research/autonomy/tests/` suite did not return a clean verdict, and the reason is not
  my change.** It fails in `conftest.pytest_sessionfinish` → `tracked_tree_guard.assert_tree_unchanged`,
  naming `research/manuscripts/claim-coverage.json`, `systems/graph/routes.json`,
  `systems/views/L2-rt-trabectedin.md`, `systems/views/L5-evidence-base.md` — **four files no test in
  this suite touches and that I have never opened.** Those are concurrent seats writing to the shared
  tree inside the guard's before/after window. ⛔ I did **not** revert them: the guard's own message
  says the change is evidence, and reverting another seat's work is the failure this sprint has
  already paid for once tonight. **`preflight.sh` is the driver's job on a settled tree** (charter §6).

---

## 6 · ⛔⛔ THE INCIDENT — a concurrent seat hard-reset the shared tree at 20:55:10Z

This is bigger than this seat and the driver should act on it before reading anything above.

**What happened.** My edits to `await_ci.py` and `gates_verdict.py` vanished. I did not guess at the
cause; the readings:

```
$ git reflog -n 5
38f8627c5 HEAD@{0}: reset: moving to HEAD
38f8627c5 HEAD@{1}: reset: moving to HEAD
38f8627c5 HEAD@{2}: reset: moving to HEAD
38f8627c5 HEAD@{3}: reset: moving to HEAD
38f8627c5 HEAD@{4}: reset: moving to HEAD
```

**Five consecutive `git reset --hard HEAD`.** Both my files came back byte-identical to `HEAD`
(`md5sum` of the working file equals `git show HEAD:…`), with **mtimes identical to the nanosecond**
(`20:55:10.032875831`) — the signature of a bulk restore, not of any write of mine. `.git/index` was
rewritten at `20:55:19`.

**Blast radius**, from `find … -newermt "20:55:05" ! -newermt "20:55:25"`, taken at **20:56Z** —
**at least 35 non-cache files** (the listing was truncated at 40 rows, so 35 is a **lower bound**),
spanning at least eight seats:

```
research/autonomy/{await_ci,gates_verdict,ledger_io,admissibility,claim,priority,continuity}.py
research/autonomy/{amendments.jsonl,research-ledger.json}
research/autonomy/receipts/CYC-0073-d4ccfde4.json
research/autonomy/sprint-2026-09-01/{S27-RETRACTIONS,S36-NULL-DISCLOSURE,S24-CALIBRATION,DELETED-BRANCHES}.md
research/modalities/{p1_anchor_convention.py,vaccine_threshold_calibration.py,p1-anchor-convention.json}
research/manuscripts/{claim_ablation.py,claim_coverage.py,line_citations.py,lint_citation_types.py}
research/manuscripts/{citation-retraction-sweep,claim-coverage,emc-systems-map}.json
research/manuscripts/neoantigen/emc-vaccine-development-path.md
research/data/emc-clinical-registry.json
systems/graph/evidence.json · systems/views/L5-evidence-base.md · scripts/preflight.sh
… and five test files
```

⚠ **THIS MEASUREMENT DECAYS AND MUST BE TAKEN EARLY.** Re-running the same `find` eight minutes
later returned **17** files, not 35 — not because anything was recovered, but because other seats
have since rewritten some of those paths and their mtimes moved out of the window. **A driver
reproducing this later will under-count.** The 20:56Z reading is the one to use; the reflog is the
durable evidence and it does not decay.

`git status --porcelain` afterwards: **5 entries.** A twelve-seat wave's uncommitted work was very
nearly emptied. ⚠ **`research/modalities/vaccine_threshold_calibration.py` is in that list — the file
the charter told this seat not to touch because S24 is still running against it.**

**Why my findings file and my test file survived:** they are **untracked**, and a hard reset does not
remove untracked files. Every seat editing a *tracked* file lost that edit and has no way to know.

**What I did about it, within my authority.** I wrote an idempotent re-apply script
(`/tmp/.../scratchpad/apply_s37.py`) that refuses rather than forces if an anchor is missing or
ambiguous, re-ran it (`applied 6 hunk(s)`), and confirmed idempotency (`applied 0, 6 already
present`). **The complete patch is reproduced in §9 so it survives this file being the only thing
left.** I ran no git write command at any point; my only git calls were `git show`, `git status`,
`git reflog`, `find` and `md5sum`.

⛔ **What the driver must do, and I cannot:** (1) establish which seat ran the reset, from
`journal.jsonl` or the seat transcripts; (2) tell the affected seats, because a seat that returns
"done" about a reverted edit is reporting work that is not on disk; (3) treat "no git write commands"
as a *hook-enforced* rule rather than a prose one — this is the second concurrency incident of the
sprint and prose did not hold either time. ⭐ The pattern this repository already knows:
**RECORDED IS NOT ENFORCED.**

---

## 7 · Amendment record for the driver

`research/autonomy/tests/**` is GOVERNED and I did not append to `amendments.jsonl`. Ready to paste,
every field non-empty:

```json
{"cycle_id": "SPRINT-2026-09-01/S37-ERROR-BODIES", "utc": "2026-09-01T21:10:00Z", "path": "research/autonomy/tests/test_an_error_body_is_the_diagnosis.py", "what_changed": "Added a new 15-test guard file covering await_ci.describe_http_error and the two error-handling paths in await_ci.poll and gates_verdict.main. No existing test was edited, weakened, deleted or renamed; no threshold, ceiling or pinned figure was touched anywhere in the repository.", "old_value": "no test anywhere asserted that a failed HTTP read preserves the server's response body; the census this seat ran found 44 of 59 except-HTTPError handlers under research/ and scripts/ discarding it, including both of the loop's own instruments", "new_value": "15 tests, of which 13 fail against the pre-fix code (measured in a scratch copy at /tmp/.../scratchpad/mut, using git show HEAD:<path>, never the live tree) and 15 pass after; the load-bearing one is test_two_different_400s_do_not_render_identically, which no str(exc) implementation can pass because str(HTTPError) is 'HTTP Error 400: Bad Request' for every 400", "why": "S24-CALIBRATION §5(d): 90 IEDB queries returned HTTP 400, the handler discarded all 90 bodies, and the seat then diagnosed the cause from the status code alone and was wrong. CLAUDE.md §4 requires the observation that discriminates between competing hypotheses; a handler that discards the response body makes that observation unavailable, and downstream an error that yields an empty list is indistinguishable from a measured absence.", "self_serving_check": "NOT self-serving: this ADDS a constraint and relaxes none. No bar, ceiling, threshold or pinned figure was changed; no existing assertion was weakened or removed; the new tests can only make a future edit harder to land, never easier. Two of the 15 pass against the pre-fix code and were deliberately left that way rather than tightened until they failed, because they pin behaviour that was already correct (await_ci cannot return green on an HTTP error) and a guard that goes red for the wrong reason is worse than one that honestly passes."}
```

---

## 8 · Sequencing for the remaining sites

⛔ **Not one of these is worth a seat on its own, and the four class-A ones together are worth one.**

**(a) One follow-up seat — the four class-A sites, plus the three dead 204 branches.** They share one
root cause and one shape of fix (attach the error to the datum, not to stderr), they are in four
files, and the 204 finding lands in two of the same files. Owned paths would be
`deepternary_blind_controls.py`, `selcal_reference_selectivity.py`, `nrv04_retro_host_history.py`,
`ddddg_known_answer_search.py`, `nr4a3_e3_stage.py` and one test file. **Start with
`selcal_reference_selectivity.py:240`** — an inventory that silently shortens is the one that can put
a wrong number in a paper. ⚠ Check first whether any of those five files is another seat's owned path.

**(b) One-line, no seat, fold into whatever next touches the file (12 sites).** Every handler that
already records `http`/`error`/`state` beside the datum and only needs the body added to the string
it is already building: `emc_data_level_sweep.py` ×3, `gse243553_eno3_overlap.py` ×2,
`emc_ret_cistrome.py` ×3, `fleet_supervision_alarm.py:170`, `atr_hrd_sarcoma_series.py:133`,
`s4_lane_inputs_fetch.py:71`, `replicate_standard_harvest.py:221`. The marker is already in the
artifact; only the explanation is missing.

**(c) Genuinely fine as they are — do not touch (13 sites).** `stuck_run_guard.py` ×4,
`supervisor_resurrect.py` ×2, `selcal_reference_selectivity.py:278`, `selcal_vast_launch.py:1497`,
`aso_offtarget_tissue_expression.py:480`, `nr4a3_e3_stage.py:312`, `nr4a3_af2_nmr_rmsd.py:175`,
`nr4a3_md.py:68`, `nr4a3_metad.py:596`. These either re-raise, hard-abort, or already write
`readable: false` / `_absent_reading` into the artifact. ⭐ **`stuck_run_guard` and
`supervisor_resurrect` are the pattern the other 31 should be measured against** — they were written
by someone who had internalised §4, and they are the reason this seat's finding is 4 sites and not 44.

**(d) The remaining ~15 are class B of the middling kind** — a body would help, nothing is at risk,
and they are not worth a dispatch. Fold in opportunistically.

**(e) ⭐ THE STRUCTURAL FIX, and the one thing here that would stop this recurring.** Promote
`describe_http_error` out of `await_ci.py` into `research/autonomy/httperr.py`, and make it the
repository's one way to render a failed HTTP read. This seat could not do it — the module was outside
its owned paths, which is why the helper currently lives in the larger of the two files it owned.
⚠ A linter that flags a bare `except …HTTPError` handler with no `.read()`/`describe_http_error()` in
its body is a natural gate 10 candidate — **44 existing sites means it must ship warn-only with an
allowlist, or it turns the commit loop red on day one.**

---

## 9 · The patch, reproduced, because a hard reset already ate it once

If §4.3's changes are missing from `await_ci.py` / `gates_verdict.py`, they were reverted, not
withdrawn. Re-apply from `/tmp/.../scratchpad/apply_s37.py` if that scratch still exists; otherwise
the four hunks are:

1. **`await_ci.py`** — after the `GREEN = {...}` constant and before `def _get(`: insert `FATAL_HTTP`,
   `MAX_BODY_CHARS` and `describe_http_error` as described in §4.3.
2. **`await_ci.py`** — in `poll()`'s `except` clause: call `why = describe_http_error(exc)` **as the
   first statement**, print `why` in the per-attempt line, add the `FATAL_HTTP` early return, and
   append `Last cause: {why}` to both give-up lines.
3. **`await_ci.py`** — module docstring gains the "the server's own words are kept" paragraph; the
   token comment's stale final clause is corrected in place.
4. **`gates_verdict.py`** — `import await_ci` beside `import envread`, and the fail-closed handler
   prints `await_ci.describe_http_error(exc)` instead of `"%s: %s" % (type(exc).__name__, exc)`.

The test file is untracked and survived; it will fail loudly if any hunk is missing.

---

## 10 · Ledger rows the driver should write

I may not write these.

| # | `what` | `kind` | `state` |
|---|---|---|---|
| 1 | Fix the four class-A error-body sites (`selcal_reference_selectivity.py:240`, `nrv04_retro_host_history.py:105`, `deepternary_blind_controls.py:189` and `:207`) so a failed read reaches the artifact as an error beside the datum rather than as a short list — and fix the three unreachable `if e.code == 204` branches in the same pass (`urlopen` never raises for a 204; proven live) | defect | queued |
| 2 | Promote `describe_http_error` from `await_ci.py` to `research/autonomy/httperr.py` and make it the repository's single renderer for a failed HTTP read | refactor | queued |
| 3 | Warn-only linter (gate 10 candidate) for `except …HTTPError` handlers that neither read the body nor call the shared describer; ships with an allowlist of the ~40 class-B sites so the commit loop does not go red on day one | tooling | queued |
| 4 | ⛔ **Enforce "no git write commands from a seat" with a hook, not prose.** Second concurrency incident of this sprint; `git reset --hard` at 2026-09-01T20:55:10Z reverted ~38 tracked files across ≥8 seats and every affected seat will report success on work that is not on disk (§6) | process-defect | **queued — driver, before the next wave** |
| 5 | Correct the census instrument before anyone uses the 44 as a progress metric: a handler that calls `describe_http_error` keeps the body without calling `.read()` inside the handler, so fixed sites still count as discarders (§1) | tooling | queued |
