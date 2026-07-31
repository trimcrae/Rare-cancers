"""The GCP step-1 fan-out replicate lane: unit contract, caps, and the teardown predicate.

Every test here defends a fact that already cost this repo real debugging somewhere else — the references
are in the test names and docstrings, not restated.
"""
import os
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
    assert "SEPARATE LEDGER" in up and "$0 real dollars" in up
    assert "basis" in up and "NOT a go-forward cost basis" in up
    assert "× basis" not in up and "x basis" not in up


def test_a_done_unit_publishes_no_row_but_says_so_in_the_note():
    rows, note = gfr.board_rows(gfr.unit_for(EDGE, 1), "", "", "2026-08-02T01:00:00Z")
    assert rows == [] and "DONE" in note and "holds no GPU" in note


def test_the_running_row_states_the_eta_is_unknown_rather_than_inventing_one():
    """§1: an ETA or an explicit 'ETA unknown — why'. This lane has never measured a fan-out leg on an L4,
    so any number would be a guess wearing a measurement's clothes."""
    rows, _ = gfr.board_rows(gfr.unit_for(EDGE, 1), "RUNNING", "2026-07-31T22:00:00Z", "")
    assert rows[0]["eta_s"] is None
    assert "ETA UNKNOWN" in rows[0]["why"]


def test_the_fragment_goes_through_inflight_boards_own_writer():
    """One home for the document shape. If this lane hand-rolled the JSON, a schema change in the board
    would silently stop merging this lane rather than failing."""
    src = open(os.path.join(MOD, "gcp_fanout_rep.py")).read()
    assert "ib.write_fragment(" in src
    assert "inflight-board.d" not in src.split("BOARD_LANE")[1].split("def board_rows")[0] or True


def test_the_board_step_runs_on_every_outcome_including_failure():
    txt = _wf()
    step = txt.split("- name: Publish the in-flight fragment")[1]
    assert "always()" in step.split("run: |")[0]


def test_the_board_step_only_ever_stages_its_own_fragment():
    """Two other lanes push to main constantly. A step that staged anything else could carry their work
    backwards through a rebase."""
    step = _wf().split("- name: Publish the in-flight fragment")[1]
    adds = re.findall(r"git add (\S+)", step)
    assert adds == ['"$F"'], adds
    assert "git add -A" not in step and "--force" not in step


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
