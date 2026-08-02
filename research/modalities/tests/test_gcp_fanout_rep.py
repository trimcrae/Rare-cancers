"""The GCP step-1 fan-out replicate lane: unit contract, caps, and the teardown predicate.

Every test here defends a fact that already cost this repo real debugging somewhere else — the references
are in the test names and docstrings, not restated.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
sys.path.insert(0, MOD)

import congeneric_fanout as cf                      # noqa: E402
import gcp_fanout_rep as gfr                        # noqa: E402

WF = os.path.join(REPO, ".github", "workflows", "gpu-fanout-rep-gcp.yml")
STARTUP = os.path.join(REPO, "research", "compute", "s1f_rep_gcp_startup.sh")
EDGE = "e_zaienne_cmpd19__cw_ms_free_acid"


# ---- the unit contract --------------------------------------------------------------------------------

def test_the_unit_is_minted_by_congeneric_fanout_not_by_this_lane():
    """Rule 1: the fan-out module is the ONE home of what a unit is. If this lane ever formats a unit_id
    itself, a GCP replicate becomes invisible to the collector that has to reduce it against n=0."""
    u = gfr.unit_for(EDGE, 1)
    assert u["unit_id"] == cf.unit_id(EDGE, u["leg_id"], u["receptor"], u["frame"], 1)
    assert u["unit_id"].endswith("__r1")


def test_keys_come_from_the_fanout_module_so_a_gcp_replicate_lands_where_vast_would_look():
    u = gfr.unit_for(EDGE, 1)
    uris = gfr.gcs_uris(u, "b")
    assert uris["result_key"] == cf.result_key(u, gfr.RESULT_PREFIX)
    assert uris["ckpt_prefix"] == cf.checkpoint_prefix(u, gfr.RESULT_PREFIX)
    assert gfr.RESULT_PREFIX == "nr4a3-step1-fanout/results"
    assert gfr.STAGE_PREFIX == "nr4a3-step1-fanout/stage"


def test_replicate_zero_is_refused_because_it_is_the_original_not_a_repeat():
    with pytest.raises(ValueError):
        gfr.units_for(EDGE, 0)


def test_the_reaper_refuses_a_cycle_id_because_it_cannot_pick_one_of_three():
    """A cycle id is a launch-time convenience. At teardown it would mean 'delete on the evidence of some
    OTHER edge's result', which is exactly the class of mistake the evidence rule exists to stop."""
    with pytest.raises(ValueError, match="resolves to 3 edges"):
        gfr.unit_for("cycle_3carbonyl", 1)


def test_the_seed_is_the_replicate_index_and_strict_provenance_is_on():
    """congeneric_fanout.unit_env emits SEED only for a replicate, and a replicate's brand-new commit prefix
    can contain nothing unstamped — so restoring an unprovenanced generation must be refused."""
    e = gfr.leg_env(gfr.unit_for(EDGE, 2), "complex", "b")
    assert e["SEED"] == "2"
    assert e["RBFE_STRICT_PROVENANCE"] == "1"


def test_the_engine_env_is_never_second_guessed_by_this_lane():
    """Whatever unit_env says about the science, leg_env passes through unchanged; it may only ADD
    object-store keys. A lane that quietly overrode N_WINDOWS or LEG would produce a number that is not
    comparable to n=0 while looking exactly like one."""
    u = gfr.unit_for(EDGE, 1)
    base = cf.unit_env(u, "complex")
    got = gfr.leg_env(u, "complex", "b")
    for k, v in base.items():
        assert got[k] == v, f"{k} was overridden: {base[k]!r} -> {got[k]!r}"


def test_the_commit_store_is_gcs_and_per_leg():
    u = gfr.unit_for(EDGE, 1)
    cx = gfr.leg_env(u, "complex", "bkt")["RBFE_SPOT_COMMIT_GCS"]
    sv = gfr.leg_env(u, "solvent", "bkt")["RBFE_SPOT_COMMIT_GCS"]
    assert cx.startswith("gs://bkt/") and cx.endswith("/complex")
    assert sv.endswith("/solvent") and cx != sv


def test_provenance_names_the_card_as_the_axis_that_is_not_held_identical():
    """The SD this replicate feeds is sampling-AND-hardware scatter. If the artifact does not say so, a
    reader reconstructs it — or does not, and over-reads it as pure sampling scatter."""
    p = gfr.provenance(gfr.unit_for(EDGE, 1), "b")
    assert p["usd_real"] == 0.0
    assert "SEPARATE LEDGER" in p["ledger"]
    assert any("card" in s for s in p["not_held_identical"])
    assert "nr4a3fep" in p["container"]


# ---- caps ---------------------------------------------------------------------------------------------

def test_a_non_run_mode_never_inherits_a_legs_cap():
    """gcp-gpu-facts.md §6c layer 3: a non-run mode writes no result object, so no reaper can retire it and
    the cap is its ONLY bound. Lending it the leg cap turns a 5-minute smoke into a 2-day hold on the one
    GPU the whole account has."""
    assert gfr.max_run_seconds("run") == gfr.MAX_RUN_S_RUN
    for m in ("smoke", "mirror", "tail", "anything"):
        assert gfr.max_run_seconds(m) == gfr.MAX_RUN_S_NON_RUN
    assert gfr.MAX_RUN_S_NON_RUN < gfr.MAX_RUN_S_RUN


# ---- the teardown predicate ---------------------------------------------------------------------------

VM_T = "2026-07-31T20:00:00Z"


def test_reap_only_when_the_result_landed_after_the_vm():
    d = gfr.reap_decision("u", VM_T, "2026-08-01T06:00:00Z")
    assert d["action"] == "reap"


@pytest.mark.parametrize("result,cause", [
    ("", "no_result_object"),
    (None, "no_result_object"),
    ("2026-07-30T00:00:00Z", "result_older_than_vm"),
    (VM_T, "result_older_than_vm"),
    ("not-a-timestamp", "unreadable_timestamp"),
])
def test_every_other_shape_refuses(result, cause):
    d = gfr.reap_decision("u", VM_T, result)
    assert d["action"] == "refuse" and d["cause"] == cause


def test_an_unresolvable_unit_refuses_rather_than_falling_back_to_age():
    assert gfr.reap_decision("", VM_T, "2026-08-01T06:00:00Z")["cause"] == "unknown_unit"
    assert gfr.reap_decision("u", "garbage", "2026-08-01T06:00:00Z")["cause"] == "unreadable_timestamp"


def test_age_is_never_consulted_anywhere_in_the_predicate():
    """The load-bearing property. gcp-reap-vms.yml records a dry_run in which an age rule would have
    destroyed a healthy mid-production leg; a fan-out complex leg legitimately runs for many hours, so age
    inverts here exactly as it does there. A VM 30 days old with no result is STILL refused."""
    d = gfr.reap_decision("u", "1996-01-01T00:00:00Z", "")
    assert d["action"] == "refuse" and d["cause"] == "no_result_object"
    src = open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    body = src.split("def reap_decision(")[1].split("\n# ---- CLI")[0]
    # CODE only: strip the docstring and every comment, then look for any age arithmetic at all.
    body = body.split('"""')[2] if body.count('"""') >= 2 else body
    code = "\n".join(l for l in body.splitlines() if not l.strip().startswith("#"))
    code = re.sub(r'"[^"]*"', '""', code)             # and every string literal — those are messages
    for banned in ("age", "timedelta", "now(", "utcnow"):
        assert banned not in code, \
            f"{banned!r} appears in reap_decision's CODE — the predicate must rest on evidence alone"


# ---- the workflow, read as text (the same discipline as tests/test_gcp_create_flags.py) ----------------

def _wf():
    return open(WF).read()


def test_both_provisioning_branches_carry_instance_termination_action():
    """gcp-gpu-facts.md §3: GCP REQUIRES --instance-termination-action whenever --max-run-duration is set,
    for standard as well as spot. Omitting it on the standard branch silently broke on-demand for months
    and the failures were mislabelled 'stocked out'."""
    txt = _wf()
    assert "--max-run-duration" in txt
    branches = re.findall(r'PROV_FLAGS="([^"]+)"', txt)
    assert len(branches) == 2, f"expected exactly 2 provisioning branches, got {branches}"
    for b in branches:
        assert "--instance-termination-action=DELETE" in b, f"branch without a termination action: {b}"


def test_the_cap_is_not_hardcoded_in_the_workflow():
    """It comes from gcp_fanout_rep.max_run_seconds via the plan step, so the mode-dependent rule cannot be
    bypassed by a YAML edit. A literal seconds value in the create is the drift this test exists to catch."""
    txt = _wf()
    assert '--max-run-duration="$MAXRUN"' in txt
    assert not re.search(r"--max-run-duration=\d", txt)


def test_only_us_central1_zones_are_ever_tried():
    """CLAUDE.md §6: quota exists ONLY in us-central1. Another region does not fail over, it wastes the
    attempt — there is no quota there to succeed with."""
    txt = _wf()
    zones = set(re.findall(r"us-(?:central|east|west|south)\d-[a-f]", txt))
    assert zones and all(z.startswith("us-central1-") for z in zones), zones


def test_the_reap_step_runs_before_anything_that_can_provision():
    txt = _wf()
    assert txt.index("Reap finished VMs") < txt.index("Provision an L4")


def test_the_reap_step_has_no_if_so_it_runs_on_every_dispatch():
    """A teardown that only fires in one mode is a teardown that does not fire. This one has no `if:`, so
    touching the lane at all cleans it up — which is the answer to gcp-gpu-facts.md §6b's finding that a
    `schedule:` cron does not supervise anything on this repo."""
    txt = _wf()
    step = txt.split("- name: Reap finished VMs")[1].split("      - name:")[0]
    assert "if:" not in step.split("run: |")[0]


def test_the_lane_refuses_to_provision_while_any_instance_is_live():
    """GPUS_ALL_REGIONS = 1 is the binding cap and is NOT readable by this service account (§1d), so the
    freeness check must rest on `instances list`, which is."""
    txt = _wf()
    assert "gcloud compute instances list" in txt
    assert "GPUS_ALL_REGIONS=1" in txt


def test_the_lane_refuses_to_provision_without_the_mirrored_inputs():
    """A VM that boots, finds no staged tree and dies still held the single GPU for its whole boot."""
    assert "run mode=mirror first" in _wf()


def test_the_idempotent_skip_is_on_the_control_plane_not_the_vm():
    """gcp-gpu-facts.md §6c layer 4: a redundant dispatch that buys an L4 and then skips is the one shape
    BOTH reapers deliberately spare, so not making the purchase is the only fix that does not weaken a
    reaper."""
    txt = _wf()
    prov = txt.split("- name: Provision an L4")[1]
    assert "S1F-REP SKIP" in prov and "not provisioning" in prov


# ---- the startup script -------------------------------------------------------------------------------

def _startup():
    return open(STARTUP).read()


def _startup_code():
    """The script with every comment line and trailing comment removed.

    Assertions about behaviour must read CODE, not the prose explaining it — otherwise a comment that
    *names* the thing it forbids fails the test that forbids it, and the fix becomes 'stop explaining'."""
    out = []
    for ln in _startup().splitlines():
        t = ln.strip()
        if t.startswith("#"):
            continue
        out.append(ln)
    return "\n".join(out)


def test_the_vm_never_tries_to_delete_itself():
    """gcp-gpu-facts.md §6: the delete is REFUSED, and the trap that 'runs and no-ops' is what made that
    invisible for five days. There must be no self-delete here at all — not even best-effort."""
    code = _startup_code()
    assert "instances delete" not in code
    assert "poweroff" not in code and "shutdown -h" not in code
    # …and the prose must still say WHY, so the next reader does not "helpfully" add one back.
    assert "cannot delete itself" in _startup().lower()


def test_the_result_object_is_the_last_thing_written():
    """Its presence is the assertion 'there is no sampling left to lose' — the reaper keys on exactly that,
    so anything written after it would be work the reaper had already licensed destroying."""
    txt = _startup()
    i = txt.index('storage cp /work/out/ddg.json')
    tail = txt[i:]
    assert "run_leg" not in tail and "docker run" not in tail


def test_checkpoints_are_continuous_not_end_of_job():
    txt = _startup()
    assert "RBFE_SPOT_SAFE" in open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    assert "storage cp /tmp/run.log" in txt          # heartbeat
    assert "idempotent skip" in txt                  # per-leg resume


def test_a_cpu_fallback_cannot_be_filed_as_a_gpu_replicate():
    """OPENMM_REQUIRE_CUDA=1 comes from unit_env; the script additionally proves a GPU is visible INSIDE
    docker before it runs anything. gcp-gpu-facts.md §1c: an accelerator-less VM boots CPU-only and reports
    a perfectly plausible number."""
    assert gfr.leg_env(gfr.unit_for(EDGE, 1), "complex", "b")["OPENMM_REQUIRE_CUDA"] == "1"
    assert "no GPU inside docker" in _startup()


def test_the_smoke_writes_to_a_throwaway_prefix_and_requires_a_real_commit():
    """A green exit code with an empty commit prefix is 'an absent reading read as a reading of absence'
    (CLAUDE.md §4). The smoke exists to prove GCSCommitStore can WRITE, so a commit count is part of the
    pass condition."""
    txt = _startup()
    assert "/smoke" in txt
    assert "SMOKE-FAIL no-commit-written" in txt and "commits=$NC" in txt


def test_the_reduce_does_not_borrow_the_denovo_401_abfe_anchor():
    """congeneric_fanout_vast._REDUCE's reason, preserved: nr4a3_rbfe MODE=reduce annotates with an anchor
    from a DIFFERENT scaffold, meaningless for a cmpd19 congeneric edge."""
    code = _startup_code()
    assert "MODE=reduce" not in code
    assert "rb.ddg_bind" in code and "ANCHOR_401" not in code


def test_the_ddg_schema_matches_the_vast_lanes_field_for_field():
    """A replicate whose ddg.json has a different shape cannot be reduced against n=0 by the same collector.
    Read the Vast lane's own reduce and require every key it writes."""
    vast = open(os.path.join(MOD, "congeneric_fanout_vast.py")).read()
    vast = vast.split('_REDUCE = r"""')[1].split('"""')[0]
    keys = set(re.findall(r'^\s*"([a-z_]+)":', vast, re.M))
    mine_block = _startup().split("PYEOF")[1]          # the heredoc BODY, between the two PYEOF markers
    mine = set(re.findall(r'^\s*"([a-z_]+)":', mine_block, re.M))
    missing = keys - mine
    assert not missing, f"the GCP reduce omits fields the Vast lane writes: {sorted(missing)}"


def test_the_same_container_as_the_vast_fanout():
    """CLAUDE.md §6 parity: generating (or analysing) with a different pymbar/openmmtools than produced the
    n=0 numbers can move the MBAR result. The replicate must run the image the fan-out ran."""
    assert "triskit23/nr4a3fep" in _wf()


def test_no_conda_solve_anywhere():
    txt = _wf() + _startup()
    assert "micromamba create" not in txt and "conda create" not in txt
    assert "setup-micromamba" not in txt


# ---- the CLI the workflow actually calls ----------------------------------------------------------------

def test_the_plan_cli_emits_what_the_workflow_greps_for():
    out = subprocess.run(
        [sys.executable, os.path.join(MOD, "gcp_fanout_rep.py"), "plan", "--edge", EDGE,
         "--replicate", "1", "--pick", "0", "--bucket", "bkt", "--shell"],
        capture_output=True, text=True, check=True).stdout
    for k in ("UNIT_ID=", "EDGE_ID=", "LEG_ID=", "RECEPTOR=", "FRAME=", "REPLICATE=", "SEED=",
              "N_WINDOWS=", "MAXRUN=", "STAGE_URI=", "UNIT_URI=", "RESULT_KEY=", "CKPT_URI=", "LABELS="):
        assert any(ln.startswith(k) for ln in out.splitlines()), f"plan --shell never emitted {k}"
    assert "ENV_COMPLEX_SEED=1" in out and "ENV_SOLVENT_LEG=solvent" in out
    # Every variable the startup script reads must be exported by the workflow from this output.
    for v in re.findall(r'^\s*for V in ([^\n]*)', _wf(), re.M)[:1]:
        pass


def test_every_variable_the_startup_script_needs_is_exported_by_the_workflow():
    """The failure this catches is silent: an unset variable in the generated script makes a URI like
    `gs:///…` and the leg writes its result nowhere the reaper looks."""
    wf = _wf()
    block = wf.split("for V in ")[1].split("; do")[0]
    exported = set(re.findall(r"[A-Z_]+", block)) | {"MACHINE_TYPE", "SMOKE"}
    needed = set(re.findall(r'"\$(?:\{)?([A-Z][A-Z0-9_]*)', _startup()))
    # Variables the script defines itself, or that come from docker/env files rather than the header.
    local = {"GS", "PREFIX", "HB", "UNIT_ID", "CODE", "IMAGE", "DOCKER_COMMON", "MD", "GCSFIX", "NC", "L",
             "PARITY", "BASE_PARITY", "NEW_PARITY", "BASE_IMAGE"}
    missing = needed - exported - local
    assert not missing, f"the startup script reads {sorted(missing)} but the workflow never sets them"


def test_the_labels_resolve_back_to_the_same_unit_the_vm_was_bought_for():
    """The reaper is handed s1f-edge + s1f-rep off a forgotten VM and must reconstruct exactly its unit.
    unit_id itself is NOT a label because GCE caps a label value at 63 characters and some unit ids are
    longer — truncation would silently collide two siblings."""
    u = gfr.unit_for(EDGE, 1)
    assert gfr.unit_for(u["edge_id"], u["replicate"])["unit_id"] == u["unit_id"]
    for x in cf.replicate_units(["cycle_3carbonyl"], (1,)):
        assert len(x["edge_id"]) <= 63, x["edge_id"]
        assert gfr.unit_for(x["edge_id"], 1)["unit_id"] == x["unit_id"]


def test_bash_syntax_of_the_startup_script():
    hdr = "\n".join(f"{v}=x" for v in
                    ("UNIT_URI STAGE_URI CKPT_URI IMAGE RECEPTOR GITREF BUCKET EDGE_ID LEG_ID FRAME "
                     "REPLICATE SEED N_WINDOWS MACHINE_TYPE SMOKE").split())
    p = subprocess.run(["bash", "-n"], input=hdr + "\n" + _startup(), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr


def test_the_workflow_is_valid_yaml_and_under_githubs_input_cap():
    try:
        import yaml
    except ImportError:
        pytest.skip("pyyaml not available")
    d = yaml.safe_load(_wf())
    trig = d[True] if True in d else d["on"]
    inputs = trig["workflow_dispatch"]["inputs"]
    assert len(inputs) <= 10, f"GitHub silently drops dispatch inputs past 10; this has {len(inputs)}"
    assert d["permissions"]["id-token"] == "write"


def test_the_env_file_has_no_export_prefix():
    """docker's --env-file splits on the FIRST `=`, so `export FOO=1` sets a variable named `export FOO`
    and FOO is never set. The engine would then fall back to its defaults — LEG=complex, no SEED, no commit
    store — and report a confident result for the wrong unit with no error anywhere. Caught before the
    first GPU dollar; this test is what stops it coming back."""
    wf = _wf()
    gen = [ln for ln in wf.splitlines() if "/tmp/env.complex" in ln or "/tmp/env.solvent" in ln]
    assert gen, "the workflow no longer generates the env files"
    for ln in gen:
        assert "export" not in ln, f"--env-file must be plain KEY=VALUE: {ln.strip()}"
    for ln in _startup_code().splitlines():
        if "env.complex" in ln or "env.solvent" in ln:
            assert "^export " not in ln, f"startup script still edits an `export ` form: {ln.strip()}"


def test_the_smoke_lowers_the_commit_interval_so_a_commit_is_actually_forced():
    """At the real 20/40 intervals a 2.5 ps TINY run legitimately commits nothing, and the smoke's pass
    condition is that a generation reached GCS. Without this the pass condition would be unreachable and
    would be "fixed" by deleting it — which is how a shakeout stops shaking anything out."""
    code = _startup_code()
    assert "RBFE_WARMUP_CKPT_ITERS=1" in code and "RBFE_PROD_CKPT_ITERS=1" in code
    real = gfr.leg_env(gfr.unit_for(EDGE, 1), "complex", "b")
    assert real["RBFE_WARMUP_CKPT_ITERS"] == "20" and real["RBFE_PROD_CKPT_ITERS"] == "40"


# ---- the in-flight fragment --------------------------------------------------------------------------

def test_an_idle_lane_publishes_a_row_that_says_it_is_idle():
    """The whole point. A lane that renders only while busy reads as FINISHED when it is merely stopped —
    which is what inflight_board's lane registry exists to prevent, and what a 15-hour idle GPU with no
    board row looked like."""
    u = gfr.unit_for(EDGE, 1)
    rows, note = gfr.board_rows(u, "", "", "")
    assert len(rows) == 1
    assert "IDLE" in rows[0]["state"]
    assert "idle" in note.lower() and "expiring credit" in note


def test_a_running_lane_names_the_free_ledger_and_refuses_to_invent_a_usd_per_ns():
    """CLAUDE.md §1: free credit is NAMED AS SUCH and never summed into realized or ladder spend. There is
    no realized dollar to divide by ns, so quoting a $/ns against the ladder basis would be a fabricated
    number in the column whose entire job is to expose fabrication."""
    rows, _ = gfr.board_rows(gfr.unit_for(EDGE, 1), "RUNNING", "2026-07-31T22:00:00Z", "")
    up = rows[0]["usd_per_ns"]
    assert "free GCP trial credit" in up and "separate ledger" in up.lower()
    assert "× basis" not in up and "x basis" not in up
    # ★★ AND THE CELL IS A CELL. `inflight_board.render` sizes the `$/ns` column to its WIDEST entry, so a
    # three-sentence cell here set that column's width for every lane's rows, not just this one's — and it
    # blew out `orchestrator_readout.board_table`, the form actually reported. (2026-08-01.)
    assert len(up) <= 60, f"the $/ns cell sets the column width for the whole board; keep it a cell: {up!r}"
    # ⚠ NOTHING WAS DROPPED — the caveat moved to the lane NOTE, which is rendered once in the section
    # header where a standing fact belongs. This half of the assertion is what makes the move a relocation
    # rather than a deletion, so the reasoning cannot be quietly lost the next time the cell is shortened.
    _rows, note = gfr.queue_board([{"unit": gfr.unit_for(EDGE, 1), "vm_status": "RUNNING"}])
    assert "SEPARATE LEDGER" in note and "$0 real dollars" in note
    assert "NOT a go-forward cost basis" in note and "never summed into realized or ladder spend" in note


def test_a_done_unit_still_renders_a_row_at_100_pct_rather_than_vanishing():
    """SUPERSEDED, and deliberately: this test used to assert `rows == []` for a landed unit.

    A row that DISAPPEARS on completion is the same failure as a lane that renders only while busy, with
    the sign flipped — with three queued units, two landed and one running should read `2 of 3 done`, not
    as a lane that shrank to one row overnight. The note still says DONE; the row now says 100 %."""
    rows, note = gfr.board_rows(gfr.unit_for(EDGE, 1), "", "", "2026-08-02T01:00:00Z")
    assert len(rows) == 1 and rows[0]["state"] == "DONE" and rows[0]["pct"] == 100.0
    assert rows[0]["eta_s"] is None                       # nothing left to wait for
    assert "DONE" in note and "holds no GPU" in note


def test_the_running_row_says_UNKNOWN_and_why_when_no_census_was_read():
    """§1: an ETA or an explicit 'ETA unknown — why'. With no census read this tick BOTH cells are unknown
    — and the sentence must say the store was not ASKED, not that it was empty (CLAUDE.md §4)."""
    rows, _ = gfr.board_rows(gfr.unit_for(EDGE, 1), "RUNNING", "2026-07-31T22:00:00Z", "")
    assert rows[0]["eta_s"] is None and rows[0]["pct"] is None
    assert "ETA UNKNOWN" in rows[0]["why"] and "% DONE UNKNOWN" in rows[0]["why"]
    assert "not ASKED" in rows[0]["why"]


def test_the_fragment_goes_through_inflight_boards_own_writer():
    """One home for the document shape. If this lane hand-rolled the JSON, a schema change in the board
    would silently stop merging this lane rather than failing.

    ★★ AND IT MUST BE `publish`, NOT `write_fragment` (2026-08-01). `write_fragment` writes this lane's
    fragment and NOTHING else; `publish` also regenerates `inflight-board-all.md`, which is the only thing
    that dates a lane's section. With `write_fragment`, this lane's fragment was 1.8 min old and carrying an
    ETA of 4:36 AM Aug 2 while the merged board rendered the lane at "16 min ago, STALE (> 15 min)" with a
    blank ETA — because the merge had last run when some OTHER lane happened to tick. STALE is the alarm for
    "a lane went quiet while it was billing"; a healthy lane raising it about itself every tick is that
    alarm being trained into noise, and the dropped ETA is the same defect one cell over."""
    src = open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    assert "ib.publish(" in src, "the lane must re-merge the all-lane board, not only write its fragment"
    assert "ib.write_fragment(" not in src, \
        "a bare write_fragment leaves the merged board dated at whenever another lane last ticked"


def test_the_board_step_runs_on_every_outcome_including_failure():
    txt = _wf()
    step = txt.split("- name: Publish the in-flight fragment")[1]
    assert "always()" in step.split("run: |")[0]


def test_the_board_step_only_ever_stages_this_lanes_own_files():
    """Two other lanes push to main constantly. A step that staged anything else could carry their work
    backwards — so the allowlist is EXPLICIT and this test is the allowlist.

    The distinction the allowlist encodes is between two KINDS of entry, and that is the whole guard:

      STAMPED (passed as arguments, snapshotted across the reset and laid back on top)
        inflight-board.d/gcp-s1f-rep.json  — written only by this lane
        gcp-s1f-rep-rate.json              — written only by this lane

      REGENERATED (PUBLISH_REGEN, run AFTER the reset, never carried through a snapshot)
        gcp-gpu-facts.md          — MANY writers; `rate --sync-doc` edits only the bytes between the
                                    rate-table fences and fails closed without exactly one ordered pair,
                                    so the staged diff can only ever be the generated block
        inflight-board-all.md     — EVERY lane writes it; DERIVED IN FULL from every lane's fragment, so
                                    regenerating post-reset reads upstream's freshest ternary /
                                    step1-fanout / nrv04-retro fragments plus the one we just stamped

    'Stage only our own files' was always a proxy for 'never carry another writer's work backwards'. A
    file we regenerate in place cannot do that; a file we stamp from a stale checkout can. So a
    many-writer file must NEVER move from PUBLISH_REGEN_ADD into the argument list.
    ⚠ RE-POINTED 2026-08-01, when this step moved to `research/compute/publish_artifacts.sh`. The
    PROPERTY below is unchanged and still holds; what moved is where it is implemented. Asserting the
    inlined shell made this the FIFTH test in one session to go red on a refactor that changed no
    behaviour — the others blocked a rental, blinded a board detector and inverted a heartbeat count — so
    it now asserts the lane's CONTRACT WITH THE PRIMITIVE, and the primitive's own behaviour is held by
    tests/test_publish_does_not_revert_another_jobs_artifact.py.
    """
    step = _wf().split("- name: Publish the in-flight fragment")[1].split("- name: ")[0]
    args = re.findall(r"^\s+(research/\S+?)(?: \\)?$", step, re.M)
    assert args == ["research/modalities/inflight-board.d/gcp-s1f-rep.json",
                    "research/modalities/gcp-s1f-rep-rate.json"], args
    regen_add = re.search(r"PUBLISH_REGEN_ADD:\s*(.+)", step).group(1).split()
    assert regen_add == ["research/compute/gcp-gpu-facts.md",
                         "research/modalities/inflight-board-all.md"], regen_add
    # ⛔ THE TWO LISTS MUST STAY DISJOINT. A many-writer file appearing as an ARGUMENT would be stamped
    # from this checkout and would revert whatever the other lanes published in the meantime.
    assert not (set(args) & set(regen_add))
    for many_writer in regen_add:
        assert many_writer not in args, f"{many_writer} has other writers and must never be stamped"
    assert "git add -A" not in step

def test_the_publish_rewrites_onto_upstream_and_never_merges():
    """★★ A PUBLISH THAT DID NOT HAPPEN MUST NEVER READ LIKE ONE (measured 2026-08-01, run 30701290485):
    `git pull --rebase` conflicted against a sibling tick 30 s earlier, `2>/dev/null || true` swallowed it,
    the rebase was left MID-CONFLICT, and `git push HEAD:main` pushed the upstream commit back to itself —
    a no-op that exits 0 and printed `fragment published` while main's fragment stayed 67 s old.
    ⚠ RE-POINTED 2026-08-01, when this step moved to `research/compute/publish_artifacts.sh`. The
    PROPERTY below is unchanged and still holds; what moved is where it is implemented. Asserting the
    inlined shell made this the FIFTH test in one session to go red on a refactor that changed no
    behaviour — the others blocked a rental, blinded a board detector and inverted a heartbeat count — so
    it now asserts the lane's CONTRACT WITH THE PRIMITIVE, and the primitive's own behaviour is held by
    tests/test_publish_does_not_revert_another_jobs_artifact.py.
    """
    step = _wf().split("- name: Publish the in-flight fragment")[1].split("- name: Detached launch")[0]
    code = "\n".join(l for l in step.splitlines() if not l.lstrip().startswith("#"))
    assert "git pull" not in code, "a merge is the wrong operation for a single-writer file"
    assert "git pull --rebase" in step, "and the incident that retired it stays in the comment"
    assert "publish_artifacts.sh" in code, "the rewrite-onto-upstream now lives in the primitive"
    prim = (pathlib.Path(WF).resolve().parents[2] / "research/compute/publish_artifacts.sh").read_text()
    assert "git reset -q --hard FETCH_HEAD" in prim and "git rebase --abort" in prim
    assert "PUBLISHED=1" in prim and 'if [ "$PUBLISHED" = 1 ]' in prim, \
        "success must be tracked explicitly, not inferred from falling out of the loop"
    assert "ARTIFACTS NOT PUBLISHED" in prim
    # …and the artifacts are snapshotted OUTSIDE the checkout, because the reset would destroy them.
    assert 'cp -a --parents "$p" "$SNAP/"' in prim
    assert prim.index("SNAP=") < prim.index("git reset -q --hard FETCH_HEAD")


# ---- the smoke terminus, the second piece of evidence the reaper may act on ---------------------------
def test_a_finished_smoke_is_reaped_on_its_own_terminal_marker():
    """A smoke never writes a result object, so the result clause can never retire it and its only bound
    would be the 7 h non-run cap — 7 h of the account's ONE GPU for a job that finished in twenty minutes.
    Its terminal marker is evidence of the same kind: the container returned, nothing is left on the box."""
    for ph in ("SMOKE-OK rc=0 commits=3", "SMOKE-FAIL no-gpu-in-docker"):
        d = gfr.reap_decision("u", VM_T, "", vm_mode="smoke", phase=ph)
        assert d["action"] == "reap" and d["cause"] == "smoke_terminal_marker", (ph, d)


@pytest.mark.parametrize("ph", ["", "boot", "image-pulled", "staged", "smoke-running", None])
def test_a_smoke_still_working_is_refused(ph):
    d = gfr.reap_decision("u", VM_T, "", vm_mode="smoke", phase=ph)
    assert d["action"] == "refuse" and d["cause"] == "smoke_not_terminal"


@pytest.mark.parametrize("ph", ["SMOKE-OK", "done", "leg-complex-done", "reduce"])
def test_a_RUN_is_never_reaped_on_a_phase_marker(ph):
    """The dangerous direction. A run's markers are PROGRESS, and `done` is written before nothing — the
    result OBJECT is the only thing that proves the science is banked. Reaping a run on a marker would
    destroy live sampling on the strength of a string the box wrote about itself."""
    d = gfr.reap_decision("u", VM_T, "", vm_mode="run", phase=ph)
    assert d["action"] == "refuse" and d["cause"] == "no_result_object"


def test_the_smoke_path_still_never_consults_age():
    d = gfr.reap_decision("u", "1996-01-01T00:00:00Z", "", vm_mode="smoke", phase="boot")
    assert d["action"] == "refuse"


def test_the_workflow_reads_the_right_phase_object_per_mode():
    """SUPERSEDED the smoke-only read (7:20 PM ET 2026-07-31): reading a phase only for smokes left a
    run that died in bootstrap with no evidence any reaper could act on."""
    step = _wf().split("- name: Reap finished VMs")[1].split("      - name:")[0]
    assert '= smoke ]; then' in step
    assert '"$UURI/smoke/phase.txt"' in step and '"$UURI/phase.txt"' in step


# ---- what the first smoke measured (run 30670712574, 6:43-6:49 PM ET 2026-07-31) ----------------------

def test_docker_is_installed_not_merely_waited_for():
    """MEASURED, not assumed: the DLVM `common-cu129-ubuntu-2404-nvidia-580` image ships NO docker —
    `line 81: docker: command not found`, `Unit docker.service not found`. The first version waited 300 s
    for a daemon that was never going to appear. Detect, then install."""
    code = _startup_code()
    assert "apt-get install -y -qq docker.io" in code
    assert "command -v docker" in code
    i = code.index("command -v docker")
    j = code.index("nvidia-container-toolkit")
    assert i < j, "docker must be established before the container runtime is configured for it"


def test_gpg_runs_in_batch_mode_because_a_startup_script_has_no_tty():
    """`gpg: cannot open '/dev/tty'` — measured. Without --batch --yes the keyring is silently never
    written, after which apt reports 'held broken packages', which names neither the cause nor the file."""
    code = _startup_code()
    assert "gpg --batch --yes --dearmor" in code
    assert "| gpg --dearmor" not in code


def test_the_keyring_is_verified_non_empty_before_apt_is_asked_to_trust_it():
    """An absent reading is not a reading of absence (CLAUDE.md §4): a zero-byte keyring produces an apt
    error about PACKAGES, three steps away from the gpg call that actually failed."""
    assert "test -s /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg" in _startup_code()


def test_apt_waits_for_the_dlvm_first_boot_dpkg_lock():
    assert "/var/lib/dpkg/lock-frontend" in _startup_code()


def test_every_bootstrap_failure_names_itself_in_the_phase_marker():
    """A phase marker that only ever says SMOKE-FAIL forces a serial-console dig for every failure. Each
    bootstrap step gets its own cause string, so the phase marker alone identifies the stage."""
    code = _startup_code()
    for cause in ("docker-install", "docker-daemon", "nvidia-keyring", "nvidia-toolkit", "no-gpu-in-docker"):
        assert f'mark "BOOTSTRAP-FAIL {cause}' in code, cause


# ---- reading a VM's labels ----------------------------------------------------------------------------

GCLOUD_JSON = """[
 {"name":"gcp-s1frep-1","zone":"https://www.googleapis.com/compute/v1/projects/p/zones/us-central1-a",
  "status":"RUNNING","creationTimestamp":"2026-07-31T15:42:10.787-07:00",
  "labels":{"lane":"s1frep","s1f-edge":"e_zaienne_cmpd19__cw_ms_free_acid","s1f-rep":"1","s1f-mode":"run"}},
 {"name":"gcp-s1frep-2","zone":"z/us-central1-b","status":"STAGING","creationTimestamp":"t"}
]"""


def test_hyphenated_labels_survive_the_read():
    """⚠ THE FAILURE THIS PREVENTS IS A SILENT ONE. gcloud's projection grammar and its filter grammar are
    different parsers, and a hyphen in a label key is where they diverge. This reaper's correct response to
    an unlabelled VM is to REFUSE — so a projection that returned empty would give a teardown that declines
    to work forever while every log line says it ran, which is the exact shape of gcp-gpu-facts.md §6b's
    scheduled-running-and-green watchdog. JSON has one grammar and the label is a dict lookup."""
    rows = [r.split("\t") for r in gfr.vm_rows(GCLOUD_JSON)]
    assert rows[0][4] == "e_zaienne_cmpd19__cw_ms_free_acid"
    assert rows[0][5] == "1" and rows[0][6] == "run"
    assert rows[0][1] == "us-central1-a", "the zone must be the basename, not the full self-link URL"


def test_an_unlabelled_vm_yields_empty_fields_which_the_predicate_then_refuses():
    rows = [r.split("\t") for r in gfr.vm_rows(GCLOUD_JSON)]
    assert rows[1][4] == "" and rows[1][5] == "" and rows[1][6] == ""
    assert gfr.reap_decision("", rows[1][3], "x")["action"] == "refuse"


def test_no_instances_yields_no_rows():
    assert gfr.vm_rows("[]") == [] and gfr.vm_rows(None) == []


def test_the_field_order_matches_what_the_workflow_reads():
    assert gfr.VM_FIELDS == ("name", "zone", "status", "creationTimestamp",
                             "s1f-edge", "s1f-rep", "s1f-mode")
    assert len(gfr.vm_rows(GCLOUD_JSON)[0].split("\t")) == len(gfr.VM_FIELDS)
    step = _wf().split("- name: Reap finished VMs")[1].split("      - name:")[0]
    read = [ln for ln in step.splitlines() if "read -r" in ln][0]
    got = read.split("read -r")[1].split(";")[0].split()
    assert got == ["NAME", "Z", "ST", "CREATED", "EDGE_L", "REP_L", "MODE_L"], got


def test_the_workflow_never_uses_a_label_projection():
    """One grep that keeps the fix from being undone by a 'simplification'. Comments are stripped first —
    the prose that explains the hazard has to be free to name it."""
    code = "\n".join(ln for ln in _wf().splitlines() if not ln.strip().startswith("#"))
    assert "labels.s1f-" not in code
    assert "gcp_fanout_rep.py vms" in code


def test_the_reduce_container_gets_stdin():
    """`python -` reads its program from stdin and `docker run` does not forward stdin without `-i`. The
    symptom would be python exiting 0 having done nothing, surfacing three lines later as 'reduce produced
    no ddg.json' — AFTER both legs are paid for and with the cause nowhere in the message."""
    code = _startup_code()
    line = [l for l in code.splitlines() if l.startswith("docker run") and "$DOCKER_COMMON" in l]
    reduce_lines = [l for l in line if " -i " in l]
    assert reduce_lines, "no `docker run -i` — the reduce heredoc would be swallowed"
    assert "PYEOF" in code and "python - <<'PYEOF'" in code


def test_the_leg_containers_do_not_need_stdin_and_run_a_file():
    """The legs run a FILE (nr4a3_rbfe.py), so they neither need nor get `-i`. Stated so the `-i` above
    reads as deliberate rather than as an inconsistency to be tidied away."""
    code = _startup_code()
    assert "python nr4a3_rbfe.py" in code


def test_adding_the_gcs_wheel_cannot_silently_move_the_science_stack():
    """★★ PARITY IS THE SCIENTIFIC ARGUMENT (CLAUDE.md §6), so it is PROVEN, not hoped for.
    `pip install google-cloud-storage` drags in protobuf/grpcio/requests and is free to upgrade a shared
    dependency while it is there. A replicate computed on a moved openfe/openmmtools/pymbar/numpy/scipy is
    worse than no replicate, because it still looks like one. Versions are read before and after and any
    difference REFUSES."""
    code = _startup_code()
    assert "BASE_PARITY" in code and "NEW_PARITY" in code
    assert 'mark "BOOTSTRAP-FAIL parity-moved"' in code
    for pkg in ("openfe", "openmmtools", "pymbar", "numpy", "scipy"):
        assert pkg in code, pkg
    # the refusal must be a refusal, not a warning
    seg = code.split("NEW_PARITY=")[1]
    assert "exit 3" in seg


def test_the_provenance_string_names_the_base_image_not_the_derived_one():
    """A one-word ordering bug in a PROVENANCE string is still a provenance bug: `IMAGE` used to be
    reassigned before the message was built, so it claimed the wheel was installed on top of the image the
    wheel had just created."""
    code = _startup_code()
    i, j = code.index("GCSFIX=\"google-cloud-storage"), code.index("IMAGE=s1frep:gcs")
    assert "$BASE_IMAGE" in code[i:i+200]
    assert j < i, "IMAGE is reassigned before GCSFIX is built — GCSFIX must name BASE_IMAGE explicitly"


# ---- the gap the first real leg found (7:20 PM ET 2026-07-31) -----------------------------------------

@pytest.mark.parametrize("mode", ["run", "smoke"])
def test_a_bootstrap_failure_is_terminal_in_every_mode(mode):
    """★★ MEASURED. The parity guard refused on the first real leg, the startup script exited 3 — and the VM
    kept holding the account's ONE GPU with nothing on it. A `run` writes no ddg.json, so the result-object
    clause could never retire it, and its only bound was the 48 h create-time cap, for a job that died in
    four minutes. BOOTSTRAP-FAIL is written only on paths that exit BEFORE run_leg is called, so no sampling
    started and no checkpoint exists — which is precisely what makes it safe to act on in run mode."""
    d = gfr.reap_decision("u", VM_T, "", vm_mode=mode, phase="BOOTSTRAP-FAIL parity-moved")
    assert d["action"] == "reap" and d["cause"] == "bootstrap_terminal_marker"


@pytest.mark.parametrize("ph", ["leg-complex-running", "staged", "reduce", "done", "SMOKE-OK rc=0"])
def test_a_run_is_still_never_reaped_on_anything_but_a_bootstrap_marker(ph):
    """The dangerous direction is unchanged: a run's progress markers, and even a SMOKE-OK string a run
    could never legitimately write, must not license a delete. Only the result OBJECT proves banked work."""
    d = gfr.reap_decision("u", VM_T, "", vm_mode="run", phase=ph)
    assert d["action"] == "refuse" and d["cause"] == "no_result_object"


def test_the_bootstrap_prefix_is_distinct_from_the_smoke_markers():
    """They must not overlap: SMOKE-* is smoke-scoped, BOOTSTRAP-* is mode-independent. A shared prefix
    would make a run reapable on a smoke's terminus string."""
    assert not set(gfr.BOOTSTRAP_TERMINAL) & set(gfr.SMOKE_TERMINAL)
    for b in gfr.BOOTSTRAP_TERMINAL:
        assert not any(b.startswith(s) or s.startswith(b) for s in gfr.SMOKE_TERMINAL)


def test_every_pre_md_failure_in_the_script_uses_the_bootstrap_prefix():
    """The reaper can only act on markers the script actually writes. Anything pre-MD still saying
    SMOKE-FAIL would be invisible to the run-mode path and would strand a VM again."""
    code = _startup_code()
    pre_md = code.split('if [ "$SMOKE" = 1 ]; then')[0]
    assert "SMOKE-FAIL" not in pre_md, "a pre-MD path still marks SMOKE-FAIL; use BOOTSTRAP-FAIL"
    for cause in ("docker-install", "docker-daemon", "nvidia-keyring", "nvidia-toolkit",
                  "no-gpu-in-docker", "image-pull", "no-code", "no-ligand", "no-receptor",
                  "no-gcs-lib", "parity-moved"):
        assert f'mark "BOOTSTRAP-FAIL {cause}' in code, cause


def test_the_reap_step_reads_a_phase_in_both_modes():
    step = _wf().split("- name: Reap finished VMs")[1].split("      - name:")[0]
    assert '"$UURI/phase.txt"' in step and '"$UURI/smoke/phase.txt"' in step


def test_the_gcs_wheel_is_installed_under_a_constraints_file():
    """MEASURED 7:20 PM ET 2026-07-31: an unconstrained `pip install google-cloud-storage` MOVES the science
    stack, and the parity check refused — correctly, but a refusal still leaves the lane unable to run. A
    constraints file built from the env's own `pip list --format=freeze` forbids pip from changing anything
    already installed, so the install either lands additively or fails. Parity by CONSTRUCTION; the check is
    then the belt to that brace."""
    code = _startup_code()
    assert "-c /tmp/constraints.txt google-cloud-storage" in code
    assert "pip list --format=freeze" in code, \
        "`pip freeze` emits `pkg @ file:///…` for conda packages, which are not valid constraints"
    # the check must SURVIVE the constraints fix — belt AND brace, not one replacing the other
    assert "BASE_PARITY" in code and 'mark "BOOTSTRAP-FAIL parity-moved"' in code


def test_an_unreadable_parity_probe_is_not_reported_as_a_moved_stack():
    """★★ MEASURED 7:36 PM ET 2026-07-31, and the offender was this lane's OWN provenance guard.
    The probe used guessed `__version__` attribute paths and swallowed stderr with 2>/dev/null. Both
    readings came back EMPTY, the comparison saw unreadable-and-unequal, and the guard announced
    'MOVED the science stack' — a false diagnosis of a probe that had simply raised. CLAUDE.md §4: an
    ABSENT READING IS NOT A READING OF ABSENCE. The two causes are now separate refusals and the probe's
    stderr is printed."""
    code = _startup_code()
    assert 'mark "BOOTSTRAP-FAIL parity-unreadable"' in code
    assert 'mark "BOOTSTRAP-FAIL parity-moved"' in code
    assert "2>/tmp/parity.err" in code and "2>/tmp/parity2.err" in code
    assert "2>/dev/null | tail -1)" not in code.split("PARITY=")[1].split("run_leg()")[0]
    # the MOVED branch must compare two READ values, never fire on an empty one
    moved = code.split('FATAL: adding google-cloud-storage MOVED')[0].splitlines()[-1]
    assert '-z "$NEW_PARITY"' not in moved, "the moved-branch must not also fire on an unreadable probe"


def test_the_parity_probe_uses_importlib_metadata_not_guessed_attributes():
    """`openmmtools.version.version` / `pymbar.__version__` were guesses and at least one of them raised.
    importlib.metadata.version works for the conda-installed distributions here and names what is missing."""
    code = _startup_code()
    assert "importlib.metadata" in code
    assert "openmmtools.version.version" not in code


# ---- the CUDA gap the first real leg found (7:51 PM ET 2026-07-31) -------------------------------------

@pytest.mark.parametrize("ph,cause", [
    ("leg-complex-FAILED-rc1", "leg_failed_terminal"),
    ("leg-solvent-FAILED-rc3", "leg_failed_terminal"),
    ("leg-complex-NORESULT", "leg_failed_terminal"),
])
def test_a_failed_leg_is_terminal_and_reapable(ph, cause):
    """MEASURED: a leg raised, its container exited, and its VM sat on the account's ONE GPU because the
    only run-mode evidence was a ddg.json that would now never exist. Safe to reap ONLY because this lane's
    commit store is CONTINUOUS — every generation is already in GCS by the time the failure marker is
    written, so a relaunch resumes and the delete loses nothing."""
    d = gfr.reap_decision("u", VM_T, "", vm_mode="run", phase=f"{ph} 2026-07-31T23:51:24Z")
    assert d["action"] == "reap" and d["cause"] == cause


@pytest.mark.parametrize("ph", ["leg-complex-running", "leg-complex-done", "reduce", "done", "staged"])
def test_a_live_or_finishing_leg_is_still_refused(ph):
    """The boundary that matters: `-running` and `-done` are PROGRESS. Only a raise (-FAILED-) or an empty
    exit (-NORESULT) is terminal, and neither can be reached while sampling continues."""
    d = gfr.reap_decision("u", VM_T, "", vm_mode="run", phase=f"{ph} 2026-07-31T23:51:24Z")
    assert d["action"] == "refuse" and d["cause"] == "no_result_object"


def test_a_cuda_probe_runs_in_the_leg_container_before_any_leg_is_paid_for():
    """'the host has a GPU' and 'THIS container's OpenMM can open it' are different propositions. The
    bootstrap check (`docker run --gpus all … nvidia-smi -L`) established only the first, PASSED, and the
    leg then raised `No compatible CUDA device is available` at openmmtools' first Context. The probe asks
    the exact question in the exact image under the exact flags, before any leg starts, and its failure is
    a BOOTSTRAP-FAIL — terminal, reapable and named."""
    code = _startup_code()
    assert "gpu_probe()" in code and "CUDA CONTEXT OK" in code
    assert 'mark "BOOTSTRAP-FAIL cuda-not-in-leg-container"' in code
    assert "getPluginLoadFailures" in code, "a silent plugin load failure is the likeliest mechanism"
    # it must run BEFORE the first leg
    assert code.index("gpu_probe()") < code.index("run_leg complex")


def test_the_probe_refuses_a_zero_exit_without_a_cuda_context():
    """An absent reading is not a reading of absence: a probe that exits 0 having printed no context must
    not be read as success — that is how a CPU fallback gets filed as a GPU replicate."""
    code = _startup_code()
    assert 'grep -q "CUDA CONTEXT OK" /tmp/probe.log ||' in code


# ---- the periodic tick (added 2026-08-01, after the lane's first render read STALE) --------------------

SUP = os.path.join(REPO, ".github", "workflows", "step1-fanout-supervisor.yml")


def _sup():
    return open(SUP).read()


def test_the_supervisor_ticks_this_lane_AND_lets_it_feed_itself():
    """The fragment is written on every dispatch of every mode — which is worth nothing while NOTHING
    DISPATCHES THE LANE. Its first render read STALE within half an hour.

    SUPERSEDED, and this is the correction: this test used to assert `-f mode=reap`, with the rationale
    "the only mode that reads and reaps but cannot buy". That was the DEFECT dressed as a safety property.
    A tick that can end work and never start it guarantees the GPU idles the moment a unit finishes —
    measured 2026-08-01: the leg raised at 11:50 PM ET, the reap step destroyed the VM 96 s later, and
    nothing relaunched for 8 h 11 m while every tick reported it. The tick is now `autofeed`."""
    sup = _sup()
    assert "gh workflow run gpu-fanout-rep-gcp.yml" in sup
    blk = sup.split("gh workflow run gpu-fanout-rep-gcp.yml")[1][:400]
    assert "-f mode=autofeed" in blk
    assert "-f edge=" not in blk and "-f replicate=" not in blk, \
        "autofeed picks its own unit from the queue; pinning one edge here is a second home for that " \
        "choice and would strand the other two units the moment this one landed"


def test_what_stops_the_tick_running_away_is_the_predicate_not_a_missing_code_path():
    """⚠ THE LOAD-BEARING SAFETY CLAIM, RESTATED WHERE IT NOW LIVES. An 8-minute dispatch that can
    provision must be stopped by something testable rather than by which `if:` happens to be written
    where. Three refusals in `feed_decision`, plus the create step's own independent live-instance check,
    plus this workflow's concurrency group — and a `launch` is the ONLY action that reaches a create."""
    for cause, kwargs in (("gpu_busy", dict(live_instances=1)),
                          ("no_progress_breaker",
                           dict(live_instances=0,
                                attempts={QUEUE[0]: {"iteration": 5, "count": gfr.MAX_NOPROGRESS_LAUNCHES}},
                                progress={QUEUE[0]: 5}))):
        assert gfr.feed_decision(QUEUE, [], **kwargs)["cause"] == cause
        assert gfr.feed_decision(QUEUE, [], **kwargs)["action"] != "launch"
    assert gfr.feed_decision(QUEUE, QUEUE, 0)["action"] == "idle"
    wf = _wf()
    gate = wf.split("- name: Provision an L4 and run")[1].split("run: |")[0]
    cond = gate.split("if:")[1].split("\n")[0]
    assert "'smoke'" in cond and "'run'" in cond
    assert "autofeed" not in cond and "!=" not in cond, \
        "the create gate stays an explicit smoke|run allowlist — autofeed reaches it ONLY by setting " \
        "MODE=run after feed_decision returned launch, so there is one create path, not two"
    body = wf.split("- name: Provision an L4 and run")[1]
    assert 'LIVE=$(gcloud compute instances list' in body and 'if [ "${LIVE:-0}" != 0 ]' in body, \
        "the create step must re-check GPU freeness itself — the feeder's check is not the only one"


def test_the_tick_still_reaps_and_still_publishes():
    """The two things the tick exists to do. The reap step carries no `if:` at all and the board step is
    `always()` — so `mode=reap` runs both."""
    wf = _wf()
    reap = wf.split("- name: Reap finished VMs")[1].split("run: |")[0]
    assert "if:" not in reap
    board = wf.split("- name: Publish the in-flight fragment")[1].split("run: |")[0]
    assert "always()" in board and "!= 'mirror'" in board


def test_the_supervisors_concurrency_group_is_untouched():
    """It cancels a SECOND supervisor while the first is alive, which is correct: duplicate supervisors
    dispatching the same lanes is a double-buy risk. Adding a tick must never widen it."""
    sup = _sup()
    assert "group: step1-fanout-supervisor" in sup
    assert "cancel-in-progress: false" in sup


def test_the_tick_does_not_target_the_ternary_gcp_lane():
    """`gpu-ternary-fep-gcp.yml` runs its launch guard BEFORE its idempotent skip, so a redundant dispatch
    of landed work exits red rather than green (measured 7:31 AM ET 2026-07-31). On an 8-minute tick that
    manufactures a stream of false failures, and a lane that always has a red run is a lane whose real
    failures stop being read. Reported for its owner; not depended on here."""
    sup = _sup()
    assert "gh workflow run gpu-ternary-fep-gcp.yml" not in sup


def test_the_cron_is_a_backstop_that_names_the_supervisor_as_the_real_cadence():
    """CLAUDE.md §6: a `*/N` cron is a REQUEST, not a cadence, and the delivered gaps have their one home
    in fleet-supervision-alarm.yml. This entry must say so and must point at the loop that actually ticks
    the lane, or the next reader plans safety around a number GitHub does not honour."""
    txt = _wf()
    # Anchor on the YAML KEY (two-space indent, own line), not the bare word — the file's own header
    # discusses `schedule:` crons at length and a loose split lands in the prose instead of the block.
    sched = txt.split("\n  schedule:\n")[1].split("\npermissions:")[0]
    assert "REQUEST, NOT A CADENCE" in sched
    assert "step1-fanout-supervisor.yml" in sched
    assert "fleet-supervision-alarm.yml" in sched
    assert "cron:" in sched


# ---- the heartbeat (coordinator ruling, 2026-08-01) ----------------------------------------------------

def test_the_fragment_commit_is_unconditional():
    """★★ **THE REDUNDANT-LOOKING COMMIT IS THE MECHANISM.** Ruled 2026-08-01 on measured volume (1,591
    commits/24 h, 1,392 of them fragment churn, .git at 267 MB) — KEPT, because that history is
    load-bearing: it reconstructed 27 rentals on a lane recording no billed_h, exposed two
    differently-configured gates writing one file, and produced the NR-V04 pilot's exact host timeline.

    The forbidden shape is a skip on 'no content change'. It never fires while the timestamp is in the
    file, which is what makes it a LANDMINE and not a bug: it does nothing until someone stabilises
    `generated_epoch`, and from that moment a healthy IDLE lane renders byte-identically to a DEAD one.
    ⚠ RE-POINTED 2026-08-01, when this step moved to `research/compute/publish_artifacts.sh`. The
    PROPERTY below is unchanged and still holds; what moved is where it is implemented. Asserting the
    inlined shell made this the FIFTH test in one session to go red on a refactor that changed no
    behaviour — the others blocked a rental, blinded a board detector and inverted a heartbeat count — so
    it now asserts the lane's CONTRACT WITH THE PRIMITIVE, and the primitive's own behaviour is held by
    tests/test_publish_does_not_revert_another_jobs_artifact.py.
    """
    step = _wf().split("- name: Publish the in-flight fragment")[1].split("- name: ")[0]
    code = "\n".join(l for l in step.splitlines() if not l.strip().startswith("#"))
    assert "git diff --cached --quiet" not in code
    assert "fragment unchanged" not in code
    # ⛔ AND THE FLAG SPELLING OF THE SAME LANDMINE. `PUBLISH_IF_CHANGED=1` is legitimate for an EVENT
    # publish; on this lane's HEARTBEAT it would be the identical defect arriving through an env var.
    assert "PUBLISH_IF_CHANGED" not in code, \
        "this fragment IS the heartbeat — the timestamp is the only input to `_As of … STALE (> 15 min)`"
    prim = (pathlib.Path(WF).resolve().parents[2] / "research/compute/publish_artifacts.sh").read_text()
    assert "git commit -q --allow-empty" in prim, \
        "--allow-empty so the step can neither silently skip nor fail red on a no-diff"

def test_the_fragment_timestamp_always_advances():
    """The heartbeat only works if every write carries a FRESH stamp. `write_board` must not pass a fixed
    or derived `now_epoch` — a fragment republished with an old timestamp is a lane reporting someone
    else's past as its present."""
    src = open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    call = src.split("def write_board(")[1].split("ib.publish(")[1].split(")")[0]
    assert "now_epoch" not in call, "write_board must let inflight_board stamp it with time.time()"
    import time as _t
    a = gfr.board_rows(gfr.unit_for(EDGE, 1), "", "", "")
    _t.sleep(0.01)
    import inflight_board as ib
    f1 = ib.build_fragment(gfr.BOARD_LANE, a[0], note=a[1])
    _t.sleep(0.01)
    f2 = ib.build_fragment(gfr.BOARD_LANE, a[0], note=a[1])
    assert f2["generated_epoch"] > f1["generated_epoch"], \
        "two builds of identical rows must still differ in their stamp — that difference IS the heartbeat"


def test_an_idle_lane_and_a_dead_lane_are_distinguishable_only_by_that_stamp():
    """The property the ruling protects, stated as a test. An idle lane's ROWS are constant tick after
    tick; the ONLY thing separating 'idle and reporting' from 'stopped reporting' is a fresh timestamp."""
    u = gfr.unit_for(EDGE, 1)
    r1, n1 = gfr.board_rows(u, "", "", "")
    r2, n2 = gfr.board_rows(u, "", "", "")
    assert r1 == r2 and n1 == n2, "an idle lane's rows are identical between ticks — by design"
    assert "IDLE" in r1[0]["state"]


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE DERIVED CENSUS — the % DONE column, and why it never needed a rate
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def _ls(*rows):
    """A `gcloud storage ls -l` listing of COMMITTED.json markers: (leg, phase, iter, utc)."""
    base = ("gs://b/nr4a3-step1-fanout/results/"
            "e_zaienne_cmpd19__cw_ms_free_acid__neutral__neutral_acid__r1/ckpt")
    return "\n".join(
        f"       884  {utc}  {base}/{leg}/{ph}/iter-{it:08d}/hash{it}/COMMITTED.json"
        for leg, ph, it, utc in rows) + "\n  TOTAL: %d objects, 1 bytes (1KiB)\n" % len(rows)


#: The REAL series the first L4 leg banked, verbatim from the store (mode=forensic, 2026-08-01 8:17 AM ET).
#: Used here so the arithmetic is tested against the measurement it was written for, not against a fixture
#: chosen to make it pass.
MEASURED_WARMUP = [
    ("complex", "warmup", 20, "2026-08-01T00:23:12Z"), ("complex", "warmup", 40, "2026-08-01T00:29:14Z"),
    ("complex", "warmup", 60, "2026-08-01T00:38:18Z"), ("complex", "warmup", 80, "2026-08-01T00:47:47Z"),
    ("complex", "warmup", 100, "2026-08-01T00:57:56Z"), ("complex", "warmup", 120, "2026-08-01T01:08:34Z"),
    ("complex", "warmup", 140, "2026-08-01T01:19:37Z"), ("complex", "warmup", 160, "2026-08-01T01:30:51Z"),
    ("complex", "warmup", 180, "2026-08-01T01:42:09Z"), ("complex", "warmup", 200, "2026-08-01T01:53:41Z"),
    ("complex", "warmup", 220, "2026-08-01T02:05:14Z"), ("complex", "warmup", 240, "2026-08-01T02:16:50Z"),
    ("complex", "warmup", 260, "2026-08-01T02:28:17Z"), ("complex", "warmup", 280, "2026-08-01T02:39:52Z"),
    ("complex", "warmup", 300, "2026-08-01T02:51:21Z"), ("complex", "warmup", 320, "2026-08-01T03:02:58Z"),
    ("complex", "warmup", 340, "2026-08-01T03:14:42Z"), ("complex", "warmup", 360, "2026-08-01T03:26:23Z"),
    ("complex", "warmup", 380, "2026-08-01T03:38:11Z"), ("complex", "warmup", 400, "2026-08-01T03:50:00Z"),
]
#: The driver's own line from that run. The denominator has ONE home and it is this line, not a constant.
MEASURED_TARGETS_LINE = "[spot-driver] warmup_target=400 (ci=20) prod_target=2000 (ci=40)"


def test_the_smoke_prefix_is_never_counted_as_science_progress():
    """`RBFE_TINY` writes into `ckpt/smoke/` precisely so it can never be resumed into. A census that did
    not exclude it would have read `smoke/production/iter-4` as production having begun — the same
    denominator-from-a-different-experiment failure inflight_board.render already guards the % cell for."""
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(
        ("complex", "warmup", 20, "2026-08-01T00:23:12Z"),
        ("smoke", "production", 4, "2026-07-31T23:11:53Z"))))
    assert set(marks) == {"complex"}
    assert gfr.leg_stage(marks.get("smoke")) == (None, None)


def test_production_outranks_warmup_whatever_the_raw_integers_say():
    """The iteration counter restarts at the phase boundary, so a max over the integers would report a
    warmup leg at 400 as ahead of a production leg at 40."""
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(
        ("complex", "warmup", 400, "2026-08-01T03:50:00Z"),
        ("complex", "production", 40, "2026-08-01T04:10:00Z"))))
    assert gfr.leg_stage(marks["complex"]) == ("production", 40)


def test_a_rate_is_never_quoted_from_fewer_than_the_stated_threshold():
    """§1 wants an ETA or an explicit 'unknown — why', and the threshold has to be a NUMBER in the code.
    The first measured leg is why: its opening interval ran at 18.1 s/iter and it settled near twice that,
    so a rate quoted off one interval would have promised a landing roughly twice too early."""
    for n in range(1, gfr.MIN_RATE_INTERVALS + 1):
        marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP[:n])))
        q = gfr.quoted_rate(marks["complex"])
        assert q["s_per_iter"] is None
        assert str(gfr.MIN_RATE_INTERVALS) in q["why"] and "completed commit interval" in q["why"]
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP[:gfr.MIN_RATE_INTERVALS + 1])))
    assert gfr.quoted_rate(marks["complex"])["s_per_iter"] is not None, \
        "at the threshold the ETA must RENDER — 'unknown forever' is indistinguishable from a broken estimator"


def test_the_rate_uses_a_trailing_window_so_the_settling_transient_is_forgotten():
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    q = gfr.quoted_rate(marks["complex"])
    assert q["n_intervals"] == 19 and q["n_used"] == gfr.RATE_WINDOW
    assert 34.0 < q["s_per_iter"] < 36.0, q            # the settled rate, not the 18.1 s/iter first one
    assert q["spread"] < 1.05, "the trailing window is steady to a few percent — that is why it is quotable"


def test_pct_renders_from_the_census_alone_with_no_rate_anywhere():
    """THE FIX, as a property. % DONE is two integers out of the object store over the driver's own
    target line; it never needed a measured seconds-per-iteration, and leaving it blank because the ETA
    lacked one is what emptied the whole progress column for a day."""
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    p = gfr.unit_progress(marks, gfr.parse_targets(MEASURED_TARGETS_LINE), leg_rates={})
    assert p["eta_s"] is None                                   # deliberately: no rate was supplied
    assert p["pct"] is not None and 8.0 < p["pct"] < 8.5        # 400 of 2 x (400 + 2000) = 8.33 %
    assert p["stage"] == "complex-warmup" and p["iteration"] == 400


def test_the_denominator_is_the_whole_unit_not_the_leg():
    """The deliverable is ddg.json and it needs BOTH legs. A leg-scoped percentage would read 100 % with
    half the unit unbought — the same argument inflight_board.pct_complete makes one level down."""
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(
        ("complex", "production", 2000, "2026-08-02T00:00:00Z"))))
    p = gfr.unit_progress(marks, (400, 2000), legs_done=(), leg_rates={})
    assert 49.0 < p["pct"] < 51.0, p                             # complex finished == half the unit


def test_an_unreadable_target_line_refuses_rather_than_assuming_zero():
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    p = gfr.unit_progress(marks, None, leg_rates={})
    assert p["pct"] is None and "not a target of zero" in p["pct_why"]


def test_the_eta_is_scoped_to_the_leg_that_has_a_rate_and_says_so():
    """The two legs solvate different systems and differ by a large factor in seconds per iteration, so
    projecting the unit off the complex rate would be a fabricated number in the cell whose whole job is
    to be actionable."""
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    p = gfr.unit_progress(marks, (400, 2000), leg_rates={"complex": 35.19})
    assert p["eta_scope"] == "complex leg"
    assert abs(p["eta_s"] - 2000 * 35.19) < 1.0                  # the 2000 production iterations left
    assert "solvent" in p["eta_why"] and "fabricated" in p["eta_why"]
    both = gfr.unit_progress(marks, (400, 2000), leg_rates={"complex": 35.19, "solvent": 7.0})
    assert both["eta_scope"] == "unit"
    assert abs(both["eta_s"] - (2000 * 35.19 + 2400 * 7.0)) < 1.0


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE FEEDER — the launch side that did not exist, and the three things that stop it running away
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

QUEUE = [u["unit_id"] for u in gfr.queue_units()]


def test_the_queue_is_the_open_cycle_at_one_replicate_in_map_order():
    assert len(QUEUE) == 3 and all(u.endswith("__r1") for u in QUEUE)
    assert QUEUE == [u["unit_id"] for u in gfr.units_for(gfr.QUEUE_CYCLE, gfr.QUEUE_REPLICATE)]


def test_a_live_instance_anywhere_in_the_project_refuses_the_launch():
    """GPUS_ALL_REGIONS = 1 is the binding cap (gcp-gpu-facts.md #1) and it is PROJECT-wide, so the
    ternary lane's VM blocks this one exactly as this lane's own does. Not a fault — the constraint."""
    d = gfr.feed_decision(QUEUE, done=[], live_instances=1)
    assert d["action"] == "hold" and d["cause"] == "gpu_busy"
    assert "GPUS_ALL_REGIONS" in d["why"] and "serial" in d["why"]


def test_it_walks_the_queue_in_order_and_skips_what_is_already_landed():
    assert gfr.feed_decision(QUEUE, done=[], live_instances=0)["unit_id"] == QUEUE[0]
    assert gfr.feed_decision(QUEUE, done=QUEUE[:1], live_instances=0)["unit_id"] == QUEUE[1]
    d = gfr.feed_decision(QUEUE, done=QUEUE, live_instances=0)
    assert d["action"] == "idle" and d["cause"] == "queue_complete"
    assert "finished, not stopped" in d["why"]


def test_the_breaker_holds_after_repeated_launches_that_bank_nothing():
    """An unattended feeder that keeps buying is how a lane turns a systematic fault into a silent burn of
    the whole credit balance."""
    att = {QUEUE[0]: {"iteration": 400, "count": gfr.MAX_NOPROGRESS_LAUNCHES}}
    d = gfr.feed_decision(QUEUE, [], 0, attempts=att, progress={QUEUE[0]: 400})
    assert d["action"] == "hold" and d["cause"] == "no_progress_breaker"
    assert "400" in d["why"] and "mode=run" in d["why"], "a hold must say how to clear it"


def test_the_breaker_is_keyed_on_progress_not_on_tries():
    """A launch that banked even one new generation resets it: retrying is cheap when it makes progress
    and unbounded when it does not."""
    att = {QUEUE[0]: {"iteration": 400, "count": 9}}
    d = gfr.feed_decision(QUEUE, [], 0, attempts=att, progress={QUEUE[0]: 420})
    assert d["action"] == "launch"
    assert gfr.next_attempt(att[QUEUE[0]], 420)["count"] == 1


def test_an_unreadable_census_holds_and_is_never_counted_as_a_non_advance():
    """CLAUDE.md §4: `iteration is None` means the store did not answer. Counting that as 'did not move'
    would let one throttled listing trip the breaker on a perfectly healthy lane."""
    att = {QUEUE[0]: {"iteration": 400, "count": gfr.MAX_NOPROGRESS_LAUNCHES}}
    d = gfr.feed_decision(QUEUE, [], 0, attempts=att, progress={QUEUE[0]: None})
    assert d["action"] == "hold" and d["cause"] == "census_unreadable"
    assert gfr.next_attempt(att[QUEUE[0]], None)["iteration"] == 400, "carried forward, never zeroed"


def test_an_unreadable_instance_list_holds_rather_than_buying_a_second_gpu():
    d = gfr.tick({"vms_readable": False, "live_instances": 0, "units": []})
    assert d["action"] == "hold" and d["cause"] == "instance_list_unreadable"


def test_only_launch_may_provision_and_the_workflow_hands_it_to_the_unchanged_run_path():
    """An autofeed launch and a hand-typed `mode=run` must be the SAME purchase — one create, one cap, one
    `s1f-mode=run` label the reaper keys on — or the two paths are free to drift."""
    step = _wf().split("- name: Autofeed")[1].split("- name: Mirror")[0]
    assert 'if [ "$A" = launch ]' in step and 'echo "MODE=run"' in step
    prov = _wf().split("- name: Provision an L4 and run")[1].split("run: |")[0]
    assert "env.MODE == 'smoke' || env.MODE == 'run'" in prov, \
        "the create gate must read env.MODE — github.event.inputs.mode is EMPTY on a schedule event, " \
        "which is exactly why no scheduled tick could ever provision"


def test_a_scheduled_tick_defaults_to_autofeed_and_not_to_reap():
    """The whole bug in one line: with `reap` as the default, every unattended tick could end work and
    none of them could start it."""
    assert "MODE: ${{ github.event.inputs.mode || 'autofeed' }}" in _wf()


def test_the_ledger_is_written_only_after_a_create_actually_succeeded():
    """A run that never bought anything must never charge the breaker."""
    prov = _wf().split("- name: Provision an L4 and run")[1]
    i_ok = prov.index('echo "VM_LIVE=1"')
    i_ledger = prov.index("next_attempt.json")
    assert i_ledger > i_ok, "the ledger write must come after the create is confirmed"


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE MEASURED L4 RATE — the first one this program has for a step-1 fan-out leg
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def test_the_protocol_lengths_are_read_from_the_engine_not_restated_here():
    """Rule 1. `nr4a3_rbfe.py` owns the MD lengths; a copy here would go stale silently and every derived
    ns/day with it. The `nanosecond` in the pattern is load-bearing — the RBFE_TINY branch sets the same
    two attributes in PICOseconds and picking that up would report a rate ~200x wrong."""
    got = gfr.protocol_lengths_ns()
    assert got == {"equilibration": 1.0, "production": 5.0}
    src = open(os.path.join(MOD, "nr4a3_rbfe.py")).read()
    assert "equilibration_length = 2.5 * _ou.picosecond" in src, \
        "the TINY branch still exists, so the nanosecond anchor is still doing work"
    assert gfr.protocol_lengths_ns("/nonexistent") is None       # fails closed


def test_ps_per_iteration_is_derived_and_refuses_when_the_two_readings_disagree():
    assert gfr.ps_per_iteration((400, 2000), {"equilibration": 1.0, "production": 5.0}) == 2.5
    assert gfr.ps_per_iteration((400, 1000), {"equilibration": 1.0, "production": 5.0}) is None
    assert gfr.ps_per_iteration(None, {"equilibration": 1.0, "production": 5.0}) is None


def test_the_rate_report_derives_leg_hours_and_both_ns_per_day_readings():
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    rep = gfr.rate_report(marks, gfr.parse_targets(MEASURED_TARGETS_LINE))
    cx = rep["legs"]["complex"]
    assert 34.0 < cx["s_per_iteration"] < 36.0
    # 2400 iterations at ~35 s is ~23 h, and that is the number that makes an L4 fan-out leg priceable.
    assert 22.0 < cx["leg_hours"] < 25.0
    assert cx["ns_per_day_aggregate"] == cx["ns_per_day_per_replica"] * rep["n_windows"]
    assert 5.5 < cx["ns_per_day_per_replica"] < 7.0
    # The solvent leg has no markers, so every derived field is ABSENT with a reason — never a zero.
    sol = rep["legs"]["solvent"]
    assert sol["s_per_iteration"] is None and "leg_hours" not in sol
    assert "unit_hours" not in rep, "a unit total needs BOTH legs measured"


def test_the_artifact_stores_the_RAW_markers_so_every_figure_stays_recomputable(tmp_path):
    """Storing only the derived rate would make it unauditable the moment RATE_WINDOW or the arithmetic
    changes. The (leg, phase, iteration, utc) tuples are the evidence; everything else is a quotient."""
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    p = gfr.write_rate_artifact(marks, (400, 2000), "u", machine_type="g2-standard-8", root=str(tmp_path))
    doc = json.load(open(p))
    assert len(doc["marks"]) == len(MEASURED_WARMUP)
    assert gfr.marks_from_artifact(doc) == marks
    assert "SEPARATE LEDGER" in doc["_ledger"] and "not a go-forward cost basis" in doc["_ledger"].lower()
    assert "$" not in json.dumps(doc["derived"]), "no dollars: this is free credit on a separate ledger"
    assert gfr.write_rate_artifact({}, (400, 2000), "u", root=str(tmp_path)) is None


def test_nothing_is_written_when_there_is_nothing_measured(tmp_path):
    assert gfr.load_rate_artifact(root=str(tmp_path)) is None


def test_a_partially_sampled_unit_outranks_a_cold_one():
    """RESUME BEFORE START. Map order alone would have started a COLD edge while
    `…cw_ms_free_acid__…__r1` sat on 400 committed iterations and 6.2 GiB of durable checkpoints — the
    'unrecorded partial gets restarted from zero' failure, reached by a different route. On a strictly
    serial GPU a partial that keeps losing the queue is a partial that never lands."""
    d = gfr.feed_decision(QUEUE, done=[], live_instances=0, progress={QUEUE[1]: 400})
    assert d["unit_id"] == QUEUE[1], "the unit with banked work wins, not the first in map order"
    # ...and with nothing banked anywhere, map order is the tiebreak, unchanged.
    assert gfr.feed_decision(QUEUE, [], 0, progress={})["unit_id"] == QUEUE[0]
    # ...and the MOST advanced wins among several.
    d = gfr.feed_decision(QUEUE, [], 0, progress={QUEUE[1]: 400, QUEUE[2]: 900})
    assert d["unit_id"] == QUEUE[2]


def test_an_unreadable_census_never_wins_the_queue_by_not_having_been_read():
    """`None` sorts as 0, not as 'most advanced'. A listing that did not answer must not outrank a unit
    with measured banked work."""
    d = gfr.feed_decision(QUEUE, [], 0, progress={QUEUE[0]: None, QUEUE[1]: 400})
    assert d["unit_id"] == QUEUE[1]


def test_a_hostless_row_reports_the_WORK_left_but_never_a_wall_clock_eta():
    """A completion time for a unit holding no GPU would be a promise about a machine nobody has rented.
    The work remaining is measured whatever the host situation, so it renders as a DURATION."""
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    prog = gfr.unit_progress(marks, (400, 2000), leg_rates={"complex": 35.19})
    rows, _ = gfr.board_rows(gfr.unit_for(EDGE, 1), "", "", "", progress=prog)
    assert rows[0]["eta_s"] is None, "no host, no wall-clock ETA"
    assert rows[0]["pct"] is not None, "the percentage is banked work and does not depend on a host"
    assert "h of L4 wall clock" in rows[0]["why"] and "once one is running" in rows[0]["why"]
    assert "ETA is for the" not in rows[0]["why"], \
        "a hostless row must not claim an ETA it is not rendering — that contradiction is the bug"
    live, _ = gfr.board_rows(gfr.unit_for(EDGE, 1), "RUNNING", "x", "", progress=prog)
    assert live[0]["eta_s"] is not None and "ETA is for the complex leg" in live[0]["why"]


FACTS = os.path.join(REPO, "research", "compute", "gcp-gpu-facts.md")


def _live_report():
    """The report the committed artifact implies, or None when no leg has been measured yet."""
    doc = gfr.load_rate_artifact()
    if doc is None:
        return None
    return gfr.rate_report(gfr.marks_from_artifact(doc),
                           tuple(doc["derived"]["targets"] or ()) or None,
                           n_windows=doc["derived"]["n_windows"])


def _fenced(md):
    """The bytes between §1e's fences, read through the module's own constants — the fence string has ONE
    home (`gcp_fanout_rep`), so a test that re-typed it could pass against a doc nobody regenerates."""
    return md.split(gfr.RATE_TABLE_BEGIN)[1].split(gfr.RATE_TABLE_END)[0].strip()


def test_the_documented_table_is_the_measured_table():
    """The document cannot drift from the measurement. Same guard `test_gcp_card_bench.py` puts on §1c:
    the table in gcp-gpu-facts.md §1e is REGENERATED from the artifact, never hand-edited, so a figure
    that no longer follows from the committed markers fails CI instead of surviving as a quotable number.

    ⚠ THIS TEST CAUGHT A REAL DIVERGENCE AND THE FIRST FIX WAS THE WRONG ONE. Regenerating by hand cleared
    it for 3 min 41 s, until the leg committed `production 80` and the rate window moved out of warmup. The
    defect was never the stale bytes — it was that the artifact's writer did not write the doc. It does
    now (`write_rate_artifact` → `sync_rate_table_doc`), which is what the tests below pin."""
    rep = _live_report()
    if rep is None:
        pytest.skip("no leg measured on an L4 yet — nothing to document")
    want = gfr.rate_markdown_table(rep).strip()
    got = _fenced(open(FACTS).read())
    assert got == want, ("gcp-gpu-facts.md §1e has drifted from gcp-s1f-rep-rate.json. This should be\n"
                         "impossible now that the writer syncs the doc — so suspect the SYNC, not the\n"
                         "bytes, before reaching for:\n"
                         "  python3 research/modalities/gcp_fanout_rep.py rate --sync-doc\n"
                         f"--- artifact says ---\n{want}\n--- document says ---\n{got}")


def test_the_fence_the_doc_and_the_writer_agree_on_is_one_string_in_one_place():
    """A fence typed independently into the doc, the writer and this test is the same second-home bug one
    level down: the sync would write a block nobody reads and every check would still pass."""
    md = open(FACTS).read()
    assert md.count(gfr.RATE_TABLE_BEGIN) == 1 and md.count(gfr.RATE_TABLE_END) == 1
    assert md.index(gfr.RATE_TABLE_BEGIN) < md.index(gfr.RATE_TABLE_END)


def _doc_fixture(tmp_path, body="| stale | table |\n", begin=None, end=None):
    """A throwaway repo shaped like the real one: <root>/modalities + <root>/compute/gcp-gpu-facts.md."""
    mod = tmp_path / "modalities"
    comp = tmp_path / "compute"
    mod.mkdir(parents=True); comp.mkdir(parents=True)
    d = comp / "gcp-gpu-facts.md"
    d.write_text("## 1c.\n| ns/day | **177.28** |\nPROSE ABOVE\n\n"
                 + (begin or gfr.RATE_TABLE_BEGIN) + "\n" + body + (end or gfr.RATE_TABLE_END)
                 + "\n\nPROSE BELOW — 177.28 stays here too.\n")
    return mod, d


def test_writing_the_artifact_REGENERATES_the_documented_table_in_the_same_call(tmp_path):
    """★★ THE DEFECT, PINNED. `write_rate_artifact` writing the JSON and leaving the doc to a human is
    correct exactly until the next commit marker lands — which on a live leg is minutes. One call, both
    files, or this comes back the moment the rate moves again."""
    mod, d = _doc_fixture(tmp_path)
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    p = gfr.write_rate_artifact(marks, (400, 2000), "u", root=str(mod))
    assert p and os.path.exists(p)
    rep = gfr.rate_report(marks, (400, 2000))
    assert _fenced(d.read_text()) == gfr.rate_markdown_table(rep).strip(), \
        "the doc must be current the instant the artifact is, without a second command"


def test_the_sync_is_idempotent_and_reports_which_of_the_three_things_it_did(tmp_path):
    """`False` (already current) must be distinguishable from `None` (could not sync). A sync that quietly
    did nothing and a sync that had nothing to do are the same silence, and the difference is the bug."""
    mod, d = _doc_fixture(tmp_path)
    rep = gfr.rate_report(gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP))), (400, 2000))
    assert gfr.sync_rate_table_doc(rep, path=str(d)) is True      # stale -> rewritten
    assert gfr.sync_rate_table_doc(rep, path=str(d)) is False     # current -> untouched
    assert gfr.sync_rate_table_doc(rep, path=str(tmp_path / "nope.md")) is None


def test_the_sync_touches_ONLY_the_fenced_block(tmp_path):
    """The lane runs this AFTER `reset --hard`, against whatever upstream holds. gcp-gpu-facts.md has many
    writers — §1f and §3b were both hand-edited the same morning — so a whole-file stamp would silently
    discard someone else's paragraph. Byte-compare everything outside the fence."""
    mod, d = _doc_fixture(tmp_path)
    before = d.read_text()
    rep = gfr.rate_report(gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP))), (400, 2000))
    gfr.sync_rate_table_doc(rep, path=str(d))
    after = d.read_text()
    assert before.split(gfr.RATE_TABLE_BEGIN)[0] == after.split(gfr.RATE_TABLE_BEGIN)[0]
    assert before.split(gfr.RATE_TABLE_END)[1] == after.split(gfr.RATE_TABLE_END)[1]
    assert "PROSE ABOVE" in after and "PROSE BELOW" in after


def test_a_doc_the_sync_cannot_confidently_edit_is_LEFT_ALONE(tmp_path):
    """FAILS CLOSED. A missing, duplicated or inverted fence writes nothing and returns None, so the test
    above fails on a real disagreement instead of the sync mangling the file into agreement — which would
    destroy the evidence that there was a disagreement."""
    rep = gfr.rate_report(gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP))), (400, 2000))
    for body, begin, end in [("x\n", "<!-- NOT-THE-FENCE -->", None),          # no BEGIN
                             ("x\n", None, "<!-- NOT-THE-FENCE -->"),          # no END
                             (gfr.RATE_TABLE_BEGIN + "\nx\n", None, None)]:    # duplicated BEGIN
        _, d = _doc_fixture(tmp_path / str(abs(hash((body, begin, end)))), body, begin, end)
        before = d.read_text()
        assert gfr.sync_rate_table_doc(rep, path=str(d)) is None
        assert d.read_text() == before, "a doc it could not parse must be byte-identical afterwards"
    # END before BEGIN: parseable fences, nonsensical order.
    _, d = _doc_fixture(tmp_path / "inverted")
    d.write_text(gfr.RATE_TABLE_END + "\nbody\n" + gfr.RATE_TABLE_BEGIN + "\n")
    before = d.read_text()
    assert gfr.sync_rate_table_doc(rep, path=str(d)) is None
    assert d.read_text() == before


def test_the_lane_that_COMMITS_the_artifact_also_commits_the_regenerated_doc():
    """★★ THE OTHER HALF OF THE FIX, AND THE HALF A UNIT TEST CANNOT REACH. The publish holds its two
    single-writer files across a `reset --hard FETCH_HEAD` and stamps them back. A doc edit made BEFORE
    that reset is therefore DISCARDED — so the sync must run after it, and the doc must be staged, or the
    artifact lands in a commit that does not carry the table quoting it. (When that was left to a human,
    CI went red 3 min 41 s after the last hand regeneration.)
    ⚠ RE-POINTED 2026-08-01, when this step moved to `research/compute/publish_artifacts.sh`. The
    PROPERTY below is unchanged and still holds; what moved is where it is implemented. Asserting the
    inlined shell made this the FIFTH test in one session to go red on a refactor that changed no
    behaviour — the others blocked a rental, blinded a board detector and inverted a heartbeat count — so
    it now asserts the lane's CONTRACT WITH THE PRIMITIVE, and the primitive's own behaviour is held by
    tests/test_publish_does_not_revert_another_jobs_artifact.py.
    """
    step = _wf().split("- name: Publish the in-flight fragment")[1].split("- name: ")[0]
    regen = re.search(r"PUBLISH_REGEN: >-\n((?:\s+\S[^\n]*\n)+)", step).group(1)
    assert "rate --sync-doc" in regen, "the publish must regenerate §1e from the artifact it commits"
    assert "inflight_board.py --write" in regen
    assert "research/compute/gcp-gpu-facts.md" in step
    # ORDERING IS THE SAFETY PROPERTY and the primitive owns it: PUBLISH_REGEN runs after the reset and
    # before the commit, by construction, so it cannot be sequenced wrongly by a caller.
    prim = (pathlib.Path(WF).resolve().parents[2] / "research/compute/publish_artifacts.sh").read_text()
    assert prim.index("git reset -q --hard FETCH_HEAD") < prim.index('eval "$PUBLISH_REGEN"') \
        < prim.index("git commit -q --allow-empty")
    assert "/tmp/pub_facts" not in step, "gcp-gpu-facts.md must never be stamped whole — it has many writers"

def test_the_documented_section_never_quotes_the_card_probe_as_this_lanes_rate():
    """§1c's 177.28 ns/day is a water box with no alchemy, no HREX and no commit barrier. Quoting one for
    the other is the exact error §1e exists to prevent, so the section must SAY they are different
    quantities and must not claim either supersedes the other."""
    sec = open(FACTS).read().split("## 1e.")[1].split("## 1d.")[0]
    assert "DIFFERENT QUANTIT" in sec.upper()
    assert "supersedes nothing" in sec or "supersedes the other" in sec
    assert "SEPARATE LEDGER" in sec and "go-forward cost basis" in sec
    assert "**not** a go-forward cost basis" in sec, "the refusal must be stated, not merely referenced"


def test_the_card_probe_number_can_never_be_EMITTED_by_the_rate_generator(tmp_path):
    """★ THE 177.28 DISTINCTION SURVIVES THE SYNC. §1c's 177.28 ns/day is a water box; §1e's aggregate is a
    12-replica alchemical hybrid. The sync now rewrites §1e's block on every tick, so the standing risk is
    that an automated rewrite quietly absorbs the card figure into the lane's table, or scribbles over the
    comparison that keeps them apart. Neither is reachable: 177.28 is not derivable from the markers, and
    the comparison table lives OUTSIDE the fence and cites the generated block rather than restating it."""
    rep = _live_report() or gfr.rate_report(
        gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP))), (400, 2000))
    assert "177.28" not in gfr.rate_markdown_table(rep), \
        "the card probe is a different quantity and no quotient of these markers can produce it"
    md = open(FACTS).read()
    assert "177.28" not in _fenced(md), "the card probe must never appear inside the generated block"
    sec = md.split("## 1e.")[1].split("## 1d.")[0]
    assert "**177.28**" in sec and "see the aggregate column above" in sec, \
        "§1e compares the two by POINTING at the generated block, never by copying a number out of it"
    # ...and the probe's own home still holds it, so §1c is quoting evidence and not a memory.
    bench = json.load(open(os.path.join(MOD, "gcp-card-bench.json")))
    assert 177.28 in [m["ns_per_day"] for m in bench["measurements"] if m["card"] == "l4"]


def test_a_warmup_rate_projected_onto_production_is_labelled_a_LOWER_BOUND():
    """★★ THE ERROR CLASS THIS REPO HAS ALREADY PAID FOR. pricing.md's 2026-07-26 correction: an L4 card
    ratio was published off 33.91 s/iter measured in WARMUP against 56.5 s/iter in PRODUCTION on the same
    leg — 1.67x — and it propagated into a per-leg dollar figure before it was caught. Production adds the
    online MBAR analysis and the trajectory write that warmup does not, so the DIRECTION is known even
    where the magnitude is not, and an ETA that crosses the boundary can only move later."""
    marks = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))
    q = gfr.quoted_rate(marks["complex"])
    assert q["phase"] == "warmup", "which phase a rate was measured in IS part of the rate"
    p = gfr.unit_progress(marks, (400, 2000), leg_rates={"complex": q["s_per_iter"]},
                          rate_phases={"complex": q["phase"]})
    assert p["eta_s"] is not None, "the caveat annotates the ETA — it never suppresses it"
    assert "LOWER BOUND" in p["eta_why"] and "1.67x" in p["eta_why"]
    assert "only move later, never earlier" in p["eta_why"]
    # Same phase on both sides -> no caveat, because there is nothing being crossed.
    same = gfr.unit_progress(
        gfr.checkpoint_marks(gfr.parse_ls_long(_ls(
            ("complex", "production", 40, "2026-08-02T00:00:00Z"),
            ("complex", "production", 80, "2026-08-02T00:20:00Z"),
            ("complex", "production", 120, "2026-08-02T00:40:00Z"),
            ("complex", "production", 160, "2026-08-02T01:00:00Z")))),
        (400, 2000), leg_rates={"complex": 30.0}, rate_phases={"complex": "production"})
    assert "LOWER BOUND" not in same["eta_why"]


def test_interval_rates_never_spans_the_phase_boundary():
    """warmup→production restarts the iteration counter, so a pair spanning it would divide a real
    duration by a meaningless iteration delta."""
    iv = gfr.interval_rates(gfr.checkpoint_marks(gfr.parse_ls_long(_ls(
        ("complex", "warmup", 380, "2026-08-01T03:38:11Z"),
        ("complex", "warmup", 400, "2026-08-01T03:50:00Z"),
        ("complex", "production", 40, "2026-08-01T04:10:00Z"),
        ("complex", "production", 80, "2026-08-01T04:30:00Z"))))["complex"], with_phase=True)
    assert [t[4] for t in iv] == ["warmup", "production"], "production sorts last, whatever the integers"
    assert all(t[1] > t[0] for t in iv)


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE THIRD SIDE — noticing that a LIVE leg has stopped committing
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

MARKS = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*MEASURED_WARMUP)))["complex"]


def test_the_stall_budget_is_derived_from_the_legs_own_commit_interval():
    """A leg that commits every 700 s and one that commits every 30 s cannot share a typed constant, and a
    seconds figure typed today would be wrong for the solvent leg the day it is first measured."""
    iv = gfr.commit_interval_seconds(MARKS)
    assert 690 < iv < 720, iv                        # the measured warmup interval, not a constant
    v = gfr.stall_verdict(MARKS, "2026-08-01T12:41:01Z", "2026-08-01T12:50:00Z", live=True)
    assert abs(v["budget_s"] - gfr.STALL_INTERVALS_FIRST * iv) < 1


def test_the_clock_starts_at_the_LEG_START_not_at_yesterdays_commit():
    """A resumed leg's newest marker belongs to the PREVIOUS attempt and is 21 h old by construction.
    Measuring silence from it would flag every resume the instant it launched."""
    v = gfr.stall_verdict(MARKS, "2026-08-01T12:41:01Z", "2026-08-01T12:50:00Z", live=True)
    assert v["stalled"] is False and v["silent_s"] < 600, v
    assert "the leg started" in v["why"]
    # ...and far enough past the budget it does flag.
    late = gfr.stall_verdict(MARKS, "2026-08-01T12:41:01Z", "2026-08-01T18:00:00Z", live=True)
    assert late["stalled"] is True and "FLAGGED" in late["why"]


def test_a_hostless_lane_is_never_stalled_and_an_unmeasured_leg_refuses():
    assert gfr.stall_verdict(MARKS, "2026-08-01T12:41:01Z", "2026-08-02T00:00:00Z", live=False)["stalled"] is False
    v = gfr.stall_verdict([], "2026-08-01T12:41:01Z", "2026-08-02T00:00:00Z", live=True)
    assert v["stalled"] is False
    assert "NOT a reading of health" in v["why"], \
        "no measured interval means no budget — that is a reading NOT TAKEN, not a clean bill of health"


def test_a_flagged_row_never_renders_as_RUNNING():
    """Same principle as CLAUDE.md §1's paying-vs-refused rule: 'advancing' and 'up but producing nothing'
    want opposite responses, and printing both as RUNNING leaves every minute of a leg's silence
    unreadable. (The '63 minutes' this test was first written against was an ET mis-conversion and is
    withdrawn — the rendering rule stands on its own.)"""
    st = gfr.stall_verdict(MARKS, "2026-08-01T12:41:01Z", "2026-08-01T18:00:00Z", live=True)
    rows, note = gfr.board_rows(gfr.unit_for(EDGE, 1), "RUNNING", "x", "", stall=st)
    assert rows[0]["state"] == "⚠ NO NEW COMMIT" and "committed NOTHING" in note
    ok = gfr.stall_verdict(MARKS, "2026-08-01T12:41:01Z", "2026-08-01T12:50:00Z", live=True)
    assert gfr.board_rows(gfr.unit_for(EDGE, 1), "RUNNING", "x", "", stall=ok)[0][0]["state"] == "RUNNING"


def test_the_stall_flag_reaches_no_reaper_and_no_launcher():
    """⚠ THE BOUNDARY, and the retracted anecdote above is exactly why it matters: the first stall this
    detector was written for turned out to be a clock error on the reader's side. The cost of a false stall
    FLAG is a line in a readout; the cost of a false stall REAP is destroyed sampling. `reap_decision` keys only on the unit's own terminal evidence and
    `feed_decision` on landed results and banked progress — neither may ever consult this."""
    src = open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    for fn in ("def reap_decision(", "def feed_decision("):
        body = src.split(fn)[1].split("\ndef ")[0]
        assert "stall" not in body, f"{fn} must not read the stall verdict"


def test_the_phase_marker_timestamp_is_parsed_and_a_bare_marker_refuses():
    assert gfr.phase_started("leg-complex-running 2026-08-01T12:41:01Z") == "2026-08-01T12:41:01Z"
    assert gfr.phase_started("leg-complex-running") is None
    assert gfr.phase_started("") is None


def test_a_rate_window_never_mixes_warmup_and_production_intervals():
    """★★ The moment production banks its first interval, a trailing-5 window would hold 4 warmup samples
    and 1 production one, report the mean as `production`, understate the production rate — and DROP the
    lower-bound caveat exactly when it starts mattering, because that caveat fires on
    `rate phase != remaining phase`. The window is scoped to the current phase; when that phase is too
    young to quote, the PREVIOUS phase's rate is quoted and LABELLED as the previous phase, which is what
    keeps the caveat armed. (This is the state the live leg was in at 9:20 AM ET 2026-08-01: 19 warmup
    intervals banked and exactly one production MARKER, i.e. zero production intervals.)"""
    one_prod = MEASURED_WARMUP + [("complex", "production", 40, "2026-08-01T13:07:00Z")]
    m = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*one_prod)))["complex"]
    q = gfr.quoted_rate(m)
    assert q["phase"] == "warmup", "one production MARKER is zero production INTERVALS"
    assert 34.0 < q["s_per_iter"] < 36.0
    # Once production has enough of its own, the window switches wholesale and the label follows.
    prod = MEASURED_WARMUP + [("complex", "production", 40 * k, "2026-08-01T%02d:00:00Z" % (13 + k))
                              for k in range(1, 8)]
    m2 = gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*prod)))["complex"]
    q2 = gfr.quoted_rate(m2)
    assert q2["phase"] == "production" and q2["n_used"] == gfr.RATE_WINDOW
    assert abs(q2["s_per_iter"] - 3600.0 / 40) < 1e-6, "purely production intervals, no warmup contamination"
    # ...and the caveat correctly STANDS DOWN once the rate and the remaining work share a phase.
    p2 = gfr.unit_progress(gfr.checkpoint_marks(gfr.parse_ls_long(_ls(*prod))), (400, 2000),
                           leg_rates={"complex": q2["s_per_iter"]}, rate_phases={"complex": q2["phase"]})
    assert "LOWER BOUND" not in p2["eta_why"]


def test_the_artifact_and_the_table_both_name_the_phase_the_rate_came_from():
    doc = gfr.load_rate_artifact()
    if doc is None:
        pytest.skip("no leg measured on an L4 yet")
    rep = gfr.rate_report(gfr.marks_from_artifact(doc),
                          tuple(doc["derived"]["targets"] or ()) or None,
                          n_windows=doc["derived"]["n_windows"])
    assert rep["legs"]["complex"]["rate_phase"] in ("warmup", "production")
    assert "(phase measured in)" in gfr.rate_markdown_table(rep)


def test_the_doc_is_synced_from_the_ARTIFACT_not_from_the_live_report():
    """★★ THE ROOT CAUSE OF TWO RED BUILDS, and the first one was never diagnosed (35.66 vs 35.67, then
    36.08 vs 36.09 — both `.xx5` values, which is exactly the measure-zero set where one ULP changes the
    printed digit).

    `test_the_documented_table_is_the_measured_table` asserts the doc equals
    `rate_markdown_table(rate_report(marks_from_artifact(artifact)))` — i.e. the doc is a function of the
    COMMITTED ARTIFACT. But `write_rate_artifact` synced it from `rep`, the report built from the LIVE
    in-memory marks, and the two are not bit-identical across the JSON round-trip:

        rate_report(marks)                        -> s_per_iteration = 36.085
        rate_report(marks_from_artifact(doc))     -> s_per_iteration = 36.084999999999994

    One ULP apart, straddling a rounding boundary, so `%.2f` rendered 36.09 against 36.08 and CI went red on
    a figure nobody had edited. Re-running `--sync-doc` "fixed" it only until the next marker landed, which
    is why it came back.

    ⛔ TWO HOMES FOR ONE FIGURE (CLAUDE.md §1). The fix is not a tolerance — a tolerance would blind the
    guard that has already caught genuine drift. It is to make the doc a function of the bytes the test
    reads, so the invariant the writer maintains IS the invariant the test checks.
    """
    src = open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    body = src[src.index("def write_rate_artifact("):]
    body = body[:body.index("\ndef ", 10)]
    code = "\n".join(ln for ln in body.splitlines() if not ln.strip().startswith("#"))
    assert "marks_from_artifact(" in code, (
        "the doc must be rendered from the artifact's own round-trip; syncing from the live report is what "
        "let the two disagree by one ULP")
    assert "load_rate_artifact(" in code, "…which means reading back what was just written"
    # and the sync must come AFTER the write, or it would read the previous artifact
    assert code.index("json.dump(") < code.index("sync_rate_table_doc("), \
        "the doc must be synced from the file this call just wrote, not the one before it"


def test_a_round_trip_through_the_artifact_reproduces_the_documented_table():
    """The property itself, exercised rather than grepped: whatever is committed, re-deriving from it must
    reproduce the committed table byte for byte. This is the assertion that fails first if a future change
    makes `marks_from_artifact` lossy again."""
    doc = gfr.load_rate_artifact(root=MOD)
    if doc is None:
        pytest.skip("no rate artifact committed")
    rep = gfr.rate_report(gfr.marks_from_artifact(doc),
                          tuple(doc["derived"]["targets"] or ()) or None,
                          n_windows=doc["derived"]["n_windows"])
    once = gfr.rate_markdown_table(rep).strip()
    twice = gfr.rate_markdown_table(
        gfr.rate_report(gfr.marks_from_artifact(doc),
                        tuple(doc["derived"]["targets"] or ()) or None,
                        n_windows=doc["derived"]["n_windows"])).strip()
    assert once == twice, "the re-derivation is not even deterministic against itself"
    assert once == _fenced(open(FACTS).read()), (
        "the committed doc is not what the committed artifact re-derives — the sync is reading a different "
        "source than the test")


# =============================================================================================================
# the operator hold — a pause that a cron edit cannot fake and a dispatcher cannot bypass
# =============================================================================================================
def test_the_operator_hold_stops_a_launch():
    h = {"reason": "pending a reevaluation of strategy", "paused_utc": "2026-08-02T09:40:00Z"}
    assert gfr.feed_decision(["u1"], [], 0)["action"] == "launch"
    d = gfr.feed_decision(["u1"], [], 0, hold=h)
    assert d["action"] == "hold" and d["cause"] == "operator_hold"
    assert "pending a reevaluation of strategy" in d["why"], "the reason must travel with the pause"
    assert "2026-08-02T09:40:00Z" in d["why"], "and when it was applied"


def test_the_hold_outranks_every_other_cause():
    """★ IT IS CHECKED FIRST, DELIBERATELY. A paused lane that reported `gpu_busy` or `queue_complete` would
    be indistinguishable in a log from one that was never paused — same words, opposite meaning. The
    operator's reason must be the one that surfaces."""
    h = {"reason": "r"}
    assert gfr.feed_decision(["u1"], ["u1"], 0, hold=h)["cause"] == "operator_hold"   # vs queue_complete
    assert gfr.feed_decision(["u1"], [], 5, hold=h)["cause"] == "operator_hold"       # vs gpu_busy


def test_an_unreadable_hold_file_HOLDS():
    """⛔ THE SAFE DIRECTION IS NOT BUYING. An unreadable instruction to stop is not permission to spend."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, gfr.OPERATOR_HOLD), "w") as fh:
            fh.write("{ this is not json")
        h = gfr.operator_hold(root=d)
        assert h is not None, "a corrupt hold file must still hold"
        assert gfr.feed_decision(["u1"], [], 0, hold=h)["cause"] == "operator_hold"
    with tempfile.TemporaryDirectory() as d:
        assert gfr.operator_hold(root=d) is None, "no file means no hold"


def test_the_hold_is_read_at_the_call_site_not_inside_the_pure_function():
    """`feed_decision` stays PURE — it takes the hold as an argument and never touches the filesystem, which
    is what keeps every branch above unit-testable without a temp dir."""
    src = open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    body = src[src.index("def feed_decision("):]
    body = body[:body.index("\ndef ", 10)]
    assert "open(" not in body and "os.path" not in body, "feed_decision must not do I/O"
    tick = src[src.index("def tick(facts, root=None):"):]
    tick = tick[:tick.index("\ndef ", 10)]
    assert "operator_hold(root=root)" in tick, "the hold must be read by tick and passed in"


def test_the_hold_does_not_disable_reap_or_supervision():
    """⛔ A PAUSED LANE MUST STILL TEAR DOWN AN IDLE VM. If the hold reached the reap step, 'paused' would
    quietly become 'billing unwatched' — the most expensive recurring failure in this repo (CLAUDE.md §6).
    Only PROVISIONING is stopped, and the workflow's reap runs at the head of every dispatch regardless."""
    wf = open(WF).read()
    reap = wf[wf.index("REAP"):]
    assert "OPERATOR_HOLD" not in reap and "operator_hold" not in reap, (
        "the reap path must be untouched by the hold")
    src = open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    reap_fn = src[src.index("def reap_decision("):]
    reap_fn = reap_fn[:reap_fn.index("\ndef ", 10)]
    assert "hold" not in reap_fn.replace("holding", "").replace("holds", ""), (
        "reap_decision must not consult the operator hold — a paused lane still reaps")


def test_a_committed_hold_file_carries_its_reason_and_how_to_resume():
    """If a hold is committed it must be self-explanatory six months later: why, when, and the single action
    that undoes it. A pause with no stated reason is indistinguishable from an abandoned lane."""
    p = os.path.join(MOD, gfr.OPERATOR_HOLD)
    if not os.path.exists(p):
        pytest.skip("no operator hold in force")
    doc = json.load(open(p))
    for k in ("reason", "paused_utc", "_how_to_resume", "state_at_pause", "what_is_NOT_lost"):
        assert doc.get(k), f"a committed hold must record {k}"
    assert "Delete this file" in doc["_how_to_resume"]
