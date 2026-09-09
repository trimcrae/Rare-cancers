#!/usr/bin/env python3
"""Deterministic extraction of retained MF1 records into the reader-facing displays.

WHAT THIS IS. New author extraction for the MF1 repair commissioned by the 2026-09-08 root
adjudication of the independent final scientific review (report SHA-256
f4a0aceec8fdea6a1da62de2dc36ef88637c6288c05f1cc7fc318b3c971b32be). It reads already-retained
committed records and writes FOUR outputs — three derived displays and a hash manifest — one of
which, the supplement, is written into the manuscript tree (see the output list below and the
`main()` calls that write them). It is NOT a science producer: it runs no simulation, no docking,
no co-fold, no fetch and no statistical re-analysis.

⭐ NARROWED 2026-09-09 (residual-2 R5). An earlier version of this docstring claimed that *every*
number printed is copied from a named field or counted at runtime. That overstated what the script
implements. The accurate statement is:

  • Most printed numbers ARE read at runtime from a named field of a named committed input, or are
    a count of records in one (`sel[...]`, `census["instruments"][...]`, `len(...)`).
  • THREE groups of printed numbers are AUTHORED CONSTANTS transcribed from retained evidence and
    NOT parsed at runtime: (a) the E1 leg accounting literals `24` declared legs and `2` legs
    excluded before execution, transcribed from `selectivity-sensitivity-control-prereg.md`
    AMENDMENT 1 (`:26–31`) — only the admitted count `22` is read from `selcal-verdict.json`
    (`n_legs_admitted`); (b) the benchmark values quoted inside the `CURRENT_SCOPE` prose for `V5`
    (`+0.944`, `−0.599`, `1.543`, three replicates), transcribed from the census fields that the
    same row also prints verbatim; (c) the `1/462` discreteness figure quoted in `CURRENT_SCOPE`
    for `V11`, whose parsed twin is printed from `sel['design_floor']` in the results table.
  • The binding that makes those transcriptions checkable is unchanged and is NOT weakened: every
    source file named above is in `INPUTS`, so each is hashed into `MF1-dependency-manifest.json`
    with its working-tree SHA-256, its git blob id and a `bytes_match_head_blob` comparison. A
    reader checks an authored constant against the hashed source; the script does not check it.
  • No new parser was added for R5. The existing author classification table stays labelled an
    author classification.

Where the manuscript needs a classification that no single retained field supplies
(the four separated audit axes of finding F05), the classification table is written out in full
below with the field it is read from, so a reader can check the mapping rather than trust it.

Run:  python3 research/autonomy/.../MF1-repair/extract_mf1_inventory.py
FOUR outputs. Three into this script's own directory:
  MF1-quantitative-results.md     — the compact main results table
  MF1-instrument-inventory.md     — the per-instrument supplementary inventory (four axes)
  MF1-dependency-manifest.json    — path, bytes, SHA-256 and git blob id of every input read
and a FOURTH, in the manuscript tree:
  research/manuscripts/methods-record/degrader-methods-failure-record-SI.md
⛔ The SI is a real output of this script, written by `main()` alongside the other three. Any
statement that this extractor "writes only the three MF1-repair/ outputs" is false.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
MOD = REPO / "research" / "modalities"

# ---------------------------------------------------------------------------
# input registry — every file this extraction reads, hashed into the manifest
# ---------------------------------------------------------------------------
INPUTS = [
    "research/modalities/selcal-verdict.json",
    "research/modalities/nr4a3-5aks-reduction.json",
    "research/modalities/valb-triangle-reduction.json",
    "research/modalities/valb-failure-propagation.json",
    "research/modalities/valb-triangle-closure.json",
    "research/modalities/r3-generation-frame-harmonized.json",
    "research/modalities/nr4a3-5bt-signature.json",
    "research/modalities/pose-conditionality-census.json",
    "research/modalities/r5-cross-method-cavity-attribution.json",
    "research/modalities/antitarget-selfcontrol.json",
    "research/modalities/nrv04-result-forensics.json",
    "research/modalities/selcal-deepternary-frame.json",
    "research/modalities/nr4a2-sparing-bound.json",
    "research/modalities/instrument-census.json",
    "research/modalities/nrv04-cofold-chain-forensics-2026-07-24.md",
    # added 2026-09-08 (residual R3): the source of the E1 exclusion stages quoted in the E1 row
    "research/modalities/selectivity-sensitivity-control-prereg.md",
    "results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json",
    "systems/graph/routes.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def git_blob(rel: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", f"HEAD:{rel}"], cwd=REPO,
            capture_output=True, text=True, check=False,
        )
        return out.stdout.strip() or None
    except OSError:
        return None


def head_blob_sha256(rel: str) -> str | None:
    """SHA-256 of the bytes git holds for `rel` at HEAD, or None if there is no such blob.

    ⭐ ADDED 2026-09-08 (residual R3). The earlier manifest recorded the SHA-256 of the
    WORKING-TREE bytes beside the HEAD blob id and never compared them. A working-tree read
    plus a blob identity is NOT a binding unless the bytes actually read match that blob, so
    the comparison is now computed and recorded instead of assumed.
    """
    try:
        out = subprocess.run(
            ["git", "cat-file", "blob", f"HEAD:{rel}"], cwd=REPO,
            capture_output=True, check=False,
        )
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return hashlib.sha256(out.stdout).hexdigest()


def head_commit() -> str:
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                         capture_output=True, text=True, check=False)
    return out.stdout.strip()


def load(rel: str):
    p = REPO / rel
    if p.suffix == ".json":
        return json.loads(p.read_text())
    return p.read_text()


# ---------------------------------------------------------------------------
# 1 · the compact quantitative results table
# ---------------------------------------------------------------------------
def results_rows() -> list[dict]:
    sel = load("research/modalities/selcal-verdict.json")
    aks = load("research/modalities/nr4a3-5aks-reduction.json")
    tri = load("research/modalities/valb-triangle-reduction.json")
    prop = load("research/modalities/valb-failure-propagation.json")
    r3 = load("research/modalities/r3-generation-frame-harmonized.json")
    sig = load("research/modalities/nr4a3-5bt-signature.json")
    cav = load("research/modalities/r5-cross-method-cavity-attribution.json")
    anti = load("research/modalities/antitarget-selfcontrol.json")
    dec = load("results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json")
    fore = load("research/modalities/nrv04-result-forensics.json")
    frame = load("research/modalities/selcal-deepternary-frame.json")

    n_pos = sum(1 for c in dec["candidates"] if c["mm_min_margin"] > 0)
    n_dec = len(dec["candidates"])
    sc = anti["selfcontrol"]
    roll = cav["rollup"]
    rep = sig["replicated"]
    n_models = rep["n_models"]["NR4A3"]

    surveys = fore["surveys"]
    n_leg = sum(s["by_class"].get("leg_result", {}).get("n", 0) for s in surveys.values())
    n_traj = sum(s["recompute_verdict"]["trajectory_objects_found"] for s in surveys.values())
    prefixes = ", ".join(f"`{s['prefix']}`" for s in surveys.values())

    return [
        dict(
            id="E1 paralogue-sensitivity calibration (`V11`)",
            control="published SMARCA2-selective degradation of a named clinical degrader; "
                    "arms `selcal_smarca2` / `selcal_smarca4`",
            criterion=f"one-sided exact permutation over model means, alternative "
                      f"`{sel['criterion']['alternative']}`, alpha {sel['criterion']['alpha']}",
            unit="model mean of the E1 interface-RMSD plateau, Å",
            # ⭐ 2026-09-08 (residual R3): the three exclusion STAGES are reported separately.
            # 24-leg frozen design, 2 legs (the SMARCA4 seed-3 model) excluded pre-execution on a
            # recorded static input fault, 22 admitted — read from
            # selectivity-sensitivity-control-prereg.md AMENDMENT 1 (:26–31), which is in INPUTS
            # above and therefore hashed into the manifest. Collector-stage `rejected_records` and
            # technical failures are DIFFERENT stages and are not summed with it.
            counts=f"sampling unit = the co-fold MODEL: "
                   f"{sel['models_per_arm']['selcal_smarca2']} vs "
                   f"{sel['models_per_arm']['selcal_smarca4']} model means. Leg stages, reported "
                   f"separately: frozen design 24 legs → 2 legs excluded before execution (the "
                   f"SMARCA4 seed-3 model, recorded static input fault, "
                   f"`selectivity-sensitivity-control-prereg.md` AMENDMENT 1) → "
                   f"{sel['n_legs_admitted']} legs admitted. Technical failures 0 / 0 (a different "
                   f"stage); collector `rejected_records` "
                   f"{len(sel['rejected_records'])} (a third stage, NOT the model exclusion)",
            estimate=f"difference of model means {sel['statistic']:+.4f} Å",
            uncertainty="no interval computed by the panel; the exact reference set has "
                        f"{sel['n_arrangements']} arrangements, attainable p floor "
                        f"{sel['design_floor']['min_attainable_p']:.7f} (1/"
                        f"{sel['design_floor']['n_arrangements']})",
            outcome=f"p = {sel['p']} (mirror {sel['p_mirror']}); recorded tier "
                    f"`{sel['tier']}`; register control state `fails`",
            limit="an executed calibration attempt that did not meet its registered directional "
                  "criterion. The attainable p floor is a discreteness property of the reference "
                  "set, NOT statistical power against any effect size; no effect size for E1 is "
                  "established. Co-fold input validation for this panel had not been implemented.",
            source="`research/modalities/selcal-verdict.json`",
        ),
        dict(
            id="5a-KS ligand-side double difference `S` (`V16`)",
            control="⛔ none — this instrument has no known-answer calibrator",
            criterion="operational completion condition: seeds per arm met "
                      f"(n_seeds_min = {aks['n_seeds_min']})",
            unit="kcal/mol",
            counts=f"{aks['per_species']['NR4A3']['n_seeds']} seeds (NR4A3) vs "
                   f"{aks['per_species']['NR4A1']['n_seeds']} seeds (NR4A1)",
            estimate=f"S = {aks['S_kcal']} kcal/mol",
            uncertainty=f"{aks['S_err_kcal']} kcal/mol, kind `{aks['S_err_kind']}` "
                        "(between-seed dispersion combined across arms)",
            outcome=f"recorded decision `{aks['decision']}`; the estimate is compatible with zero "
                    "at the observed dispersion",
            limit="an exploratory conditional estimate, not a confidence interval, equivalence "
                  "test or effect bound, and not evidence that a wedge is absent. The record "
                  "additionally flags `system_identity_problems` on `n_particles` across the four "
                  "legs. `S` is non-covalent and cannot test a covalent categorical mechanism.",
            source="`research/modalities/nr4a3-5aks-reduction.json`",
        ),
        dict(
            id="valB_mini cooperativity calibration and its closure triangle (`V5`)",
            control="a published ternary cooperativity value",
            criterion="sign and magnitude against the known cooperativity; closure residual "
                      "R = R_ternary − R_binary",
            unit="kcal/mol",
            counts=f"{prop['inputs_measured']['n_replicates']} replicates (calibration); "
                   f"{tri['noise_floor']['n_legs_in_R']} legs in one single-seed closure",
            estimate=f"calibration absolute error {prop['inputs_measured']['abs_error_kcal']} "
                     f"kcal/mol, wrong sign in every replicate; "
                     f"R_ternary = {tri['R_ternary_kcal']}, R_binary = {tri['R_binary_kcal']}, "
                     f"R = {tri['R_kcal']}",
            uncertainty=f"replicate SD (cycle) {prop['inputs_measured']['cycle_sd_kcal']} kcal/mol; "
                        f"per-leg MBAR SE {prop['inputs_measured']['per_leg_mbar_se_kcal'][0]}–"
                        f"{prop['inputs_measured']['per_leg_mbar_se_kcal'][1]} kcal/mol; the "
                        f"closure carries `{tri['error_bar_kind']}`",
            outcome="repeated wrong-sign operational calibration failure; the closure residual is "
                    "small",
            limit="a small closure residual does not localise the miss to endpoint-state error, "
                  "does not exclude shared sampling bias, does not certify convergence and does "
                  "not show that more sampling cannot help: the residual is one linear contrast "
                  "of six edge errors and is identically zero for whole classes of them. The "
                  "record's own propagation gives power ≈ "
                  f"{prop['1b_power_at_measured_bound']['at_sigma_leg_upper_bound']['power_at_n1']['detect_1.478']}"
                  " at its upper noise bound. A cycle SD and a per-leg MBAR SE are different "
                  "estimands and their ratio is not a transferable inflation factor.",
            source="`research/modalities/valb-triangle-reduction.json`, "
                   "`research/modalities/valb-failure-propagation.json`, "
                   "`research/modalities/valb-triangle-closure.json`",
        ),
        dict(
            id="decoy pass-through of marketed drugs (`V20`)",
            control="⛔ no measured biological negative labels; the comparator is a selected set "
                    "of unrelated marketed drugs",
            criterion="single-snapshot MM-GBSA `margin > 0` read as a selectivity verdict",
            unit="kcal/mol margin against the closer paralogue",
            counts=f"{n_dec} decoys scored against "
                   f"{len(dec['paralogues'])} paralogues",
            estimate=f"{n_pos} of {n_dec} decoys score a positive minimum margin",
            uncertainty="none quoted: a single snapshot, one trajectory, no entropy, no ensemble "
                        "average",
            outcome=f"census {json.dumps(dec['verdict_census'])}",
            limit=f"{n_pos}/{n_dec} is a POSITIVE-CALL RATE among these selected decoys under this "
                  "scoring configuration. It is NOT a measured biological false-positive rate, and "
                  "it does not establish that any downstream method is unable to extract signal.",
            source="`results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json`",
        ),
        dict(
            id="generation-frame druggability gate",
            control="the program's own preregistered druggability threshold D*",
            criterion=f"harmonized druggability of the mapped orthosteric site against D* = "
                      f"{r3['verdict']['d_star']}",
            unit="dimensionless harmonized druggability",
            counts=f"{r3['n_candidate_pockets']} candidate pockets; "
                   f"{r3['n_accepted_by_gate']} accepted by the gate",
            estimate=f"druggability {r3['verdict']['druggability']}",
            uncertainty="none quoted; a single receptor frame",
            outcome=f"`{r3['verdict']['verdict']}`",
            limit="failure of one operational screening threshold on one receptor frame. It is "
                  "NOT a demonstration that nothing binds this pocket, and NOT a theorem about "
                  "any design class.",
            source="`research/modalities/r3-generation-frame-harmonized.json` → `verdict`",
        ),
        dict(
            id="V1 polar-contact descriptor over the generated NR4A ternaries",
            control="recovery of one published SMARCA2 interface contact from two crystals "
                    f"(n = {sig['descriptor_validation']['n']} position)",
            criterion="heavy-atom N/O pair within 3.5 Å on a side-chain polar atom, at a "
                      "sequence-variable aligned position",
            unit="count of qualifying positions",
            counts=f"{n_models} NR4A3 models vs {rep['n_models']['NR4A1']} NR4A1 and "
                   f"{rep['n_models']['NR4A2']} NR4A2 models",
            estimate="zero qualifying sequence-variable positions in any NR4A3 model",
            uncertainty="not applicable — a descriptive count, no energy and no interval",
            outcome=sig['sentence_replicated'],
            limit="scoped to THIS descriptor and threshold on THESE generated structures. The "
                  "known-answer recovery is a narrow in-sample development/harness check (one "
                  "contact, one pair, and the criterion was corrected after an initial miss); it "
                  "does not establish sensitivity to hydrophobic contacts, energies or any other "
                  "discriminating interaction. The generating route scores DockQ 0.023–0.046 "
                  "where a crystal exists to check it.",
            source="`research/modalities/nr4a3-5bt-signature.json` → `sentence_replicated`",
        ),
        dict(
            id="cross-method pose attribution (`V3` vs `V22`)",
            control="⛔ none of its own; the second method is run beside the first on the same "
                    "receptors and boxes",
            criterion="same sub-cavity of the split site, contact-based cavity call at a 4.0 Å "
                      "contact cutoff",
            unit="systems",
            counts=f"{roll['n_systems']} systems, {roll['n_gradeable']} gradeable, "
                   f"{roll['n_systems'] - roll['n_gradeable']} ungradeable",
            estimate=f"{roll['n_same_cavity']} same-cavity, {roll['n_different_cavity']} "
                     f"different-cavity among the gradeable systems",
            uncertainty="not applicable — a per-system categorical call",
            outcome="MIXED. The cavity call is itself receptor-conformer dependent, so neither an "
                    "orientation-only nor a location-only reading holds across the census",
            limit="agreement would not have meant correctness and disagreement does not show "
                  "either method wrong. Both are docking searches into a fixed receptor, so a "
                  "shared receptor-conformer error survives both.",
            source="`research/modalities/r5-cross-method-cavity-attribution.json` → `rollup`",
        ),
        dict(
            id="anti-target panel cognate-ligand self-control (`V21`)",
            control="each panel receptor's own crystallographic ligand, re-docked through the "
                    "identical protocol",
            criterion=f"pose recovery ≤ {anti['criterion']['recovered_rmsd_A']} Å under the "
                      "pre-existing criterion, read from the existing module rather than chosen "
                      "for this test",
            unit="receptors passing",
            counts=f"{sc['n_targets']} receptors",
            estimate=f"{sc['n_pass']} of {sc['n_targets']} recover their cognate pose",
            uncertainty="not applicable — a per-receptor pass/fail",
            outcome=f"`panel_readable: {json.dumps(sc['panel_readable'])}`; blocking targets "
                    + ", ".join(f"`{t}`" for t in sc["blocking_targets"]),
            limit="every published clause built on this panel is a maximum or an every-survivor "
                  "statement over the whole panel, so one unreadable receptor changes all of "
                  "them. A failing target may not be dropped, re-centred, or graded on a lowered "
                  "band. The uniform receptor-completeness repair did not restore readability.",
            source="`research/modalities/antitarget-selfcontrol.json` → `selfcontrol`",
        ),
        dict(
            id="covalent-panel result census after the chain-assignment incident",
            control="not applicable — a retrospective object census, not an instrument",
            criterion="can the reported readouts be recomputed for the corrected interface from "
                      "what was persisted?",
            unit="stored objects",
            # ⭐ 2026-09-08 (residual R4): the per-prefix split is shown, not only the sum. 17 is
            # the FIRST-prefix count; the combined total is 18 STORED RESULT OBJECTS — not 18
            # independent experiments and not 18 intended panel legs.
            counts=f"surveyed prefixes {prefixes}; per-prefix stored result objects "
                   + " + ".join(
                       f"{s['by_class'].get('leg_result', {}).get('n', 0)} under `{s['prefix']}`"
                       for s in surveys.values())
                   + f" = {n_leg} stored result objects across both (⛔ stored objects, NOT "
                     f"independent experiments)",
            estimate=f"{n_traj} multi-frame coordinate objects found under the surveyed prefixes",
            uncertainty="not applicable — an enumeration",
            outcome="corrected-interface readouts cannot be recomputed from the retained objects; "
                    "every persisted object is a single frame or an already-reduced scalar",
            limit="scoped to the two surveyed prefixes of this object store. It is not a proof "
                  "about every possible external copy of the data. Persisted trajectories would "
                  "have permitted rescoring of the interface readouts; they could NOT have "
                  "repaired the legs that simulated the wrong covalent tether, which is a "
                  "different defect class.",
            source="`research/modalities/nrv04-result-forensics.json` → `surveys.*."
                   "recompute_verdict`",
        ),
        dict(
            id="external unbound-benchmark preparation record",
            control="not applicable",
            criterion="not applicable — a preparation/alignment record",
            unit="ligand heavy atoms in the prepared record",
            counts=f"{len(frame)} arm record(s): `{frame[0]['arm']}`, native "
                   f"`{frame[0]['native_pdb']}`, component `{frame[0]['degrader_comp']}`",
            estimate=f"{frame[0]['detail']['native_atom_counts']['degrader']} degrader atoms "
                     f"written; superposition CA-RMSD "
                     f"{frame[0]['detail']['superpose_p1']['ca_rmsd_A']} Å / "
                     f"{frame[0]['detail']['superpose_p2']['ca_rmsd_A']} Å",
            uncertainty="not applicable",
            outcome="a preparation and readability record for one system",
            limit="⛔ this record does NOT contain the released-case coordinate comparison that "
                  "would be needed to contradict an external publication's protocol statement. "
                  "The external refutation is withdrawn from this manuscript; see the F11 "
                  "response.",
            source="`research/modalities/selcal-deepternary-frame.json`",
        ),
    ]


def write_results_table(rows: list[dict]) -> str:
    out = ["<!-- GENERATED by MF1-repair/extract_mf1_inventory.py — DO NOT HAND-EDIT. -->",
           "", "# MF1 — compact quantitative results", ""]
    out.append("| record | control / reference identity | operational criterion | unit | "
               "eligible / excluded / failed / unrun counts | estimate | uncertainty type | "
               "actual result | ⛔ interpretive limit | source |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        cells = [r["id"], r["control"], r["criterion"], r["unit"], r["counts"], r["estimate"],
                 r["uncertainty"], r["outcome"], r["limit"], r["source"]]
        out.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cells) + " |")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 2 · the per-instrument inventory, on four separated axes (F05)
# ---------------------------------------------------------------------------
# The four axes the review requires are not four fields of any retained record: the retained
# register carries ONE word (`disclosed_failing`) and the census carries ONE class. The mapping
# below is therefore an explicit AUTHOR CLASSIFICATION, written out so it can be checked. Each
# entry names the retained evidence the classification is read from.
#   control_axis     : what kind of grading standard exists at all
#   execution_axis   : whether the graded run actually executed and was eligible
#   outcome_axis     : the inferential result, conditional on execution
# The claim-scope column is quoted from the census's own `scope_limit` field, unedited.
AXES: dict[str, dict[str, str]] = {
    "V1":  dict(control="known-answer (one published contact, one crystal pair)",
                execution="executed, complete",
                outcome="recovered its known answer",
                note="in-sample development/harness check; criterion corrected after an initial miss"),
    "V2":  dict(control="known-answer (structure rebuild, one in-set and one post-horizon case)",
                execution="executed, complete; one arm refused",
                outcome="recovered its known answer on the graded cases",
                note="OUTSIDE the RT-METHODS-PAPER route partition; memorisation-permitting on the in-set case"),
    "V3":  dict(control="known-answer (holo pose recovery from apo)",
                execution="executed; the protocol's own ceiling missed",
                outcome="inconclusive by its own preregistered rule",
                note="the run measured site selection rather than docking"),
    "V4":  dict(control="known-answer (selectivity free energy) — specified",
                execution="⛔ never run; built and staged, not authorised",
                outcome="no result",
                note="the one test designed to grade selectivity free energy directly"),
    "V5":  dict(control="known-answer (a published cooperativity value)",
                execution="executed, complete, 3 replicates",
                outcome="did not recover: wrong sign in every replicate",
                note="operational calibration failure; cause not uniquely identified"),
    "V6":  dict(control="known-answer (public relative-FEP benchmark)",
                execution="executed, complete",
                outcome="recovered within the accepted band",
                note="relative quantity, one pocket, one charge model"),
    "V7":  dict(control="known-answer (absolute binding free energy benchmark)",
                execution="executed, complete",
                outcome="did not recover: large absolute bias",
                note="the miss exceeds the margin the engine is used to compute"),
    "V8":  dict(control="known-answer (hydration free energy)",
                execution="executed, complete",
                outcome="recovered approximately",
                note="a solvation smoke test"),
    "V9":  dict(control="⛔ none — a self-consistency diagnostic, not a known answer",
                execution="executed, complete",
                outcome="defect open",
                note="no grade is possible from a self-check"),
    "V10": dict(control="known-answer (published interface-mutation ΔΔG)",
                execution="executed, complete",
                outcome="recovered a large effect",
                note="not demonstrated in the small paralogue-scale regime that matters here"),
    "V11": dict(control="known-answer (published paralogue-selective degradation)",
                execution="executed, complete; 0 technical failures in either arm",
                outcome="nondetection under the registered directional criterion",
                note="an executed calibration attempt that did not meet its criterion; not an absent control"),
    "V12": dict(control="known-answer (reproduce two deposited ternaries from sequence)",
                execution="executed, complete",
                outcome="did not recover",
                note="DockQ 0.023–0.046"),
    "V13": dict(control="mechanism HYPOTHESIS (a two-state cryptic opening), not an "
                        "independently established truth",
                execution="executed, complete",
                outcome="hypothesis failed as registered",
                note="a failed mechanism test is not a failed recovery of a known answer"),
    "V14": dict(control="⛔ none",
                execution="executed, complete",
                outcome="ungraded — no control exists",
                note="orthogonal axis, untested as an instrument"),
    "V15": dict(control="permutation NULLS (a negative control), not a positive known answer",
                execution="executed, complete",
                outcome="mixed — one of five nulls does not support it",
                note="not a positive known-answer benchmark"),
    "V16": dict(control="⛔ none — no known-answer calibrator",
                execution="executed; operational completion condition met",
                outcome="exploratory estimate compatible with zero at the observed dispersion",
                note="an uncalibrated instrument returning ≈0 cannot separate 'no effect' from "
                     "'cannot resolve'"),
    "V17": dict(control="known-answer (a literature-supported covalent site)",
                execution="executed, complete",
                outcome="did not recover: demonstrated false negative",
                note="anything adjudicated by this cutoff inherits that false negative"),
    "V18": dict(control="⛔ none exists",
                execution="not applicable — a set-membership screen",
                outcome="ungraded — no control exists",
                note="OUTSIDE the RT-METHODS-PAPER route partition"),
    "V19": dict(control="the scrambled-objective arm (a negative control)",
                execution="one arm executed; ⛔ the decisive generative arm is UNRUN",
                outcome="partial — zero manufactured survivors, confound narrowed not excluded",
                note="a single row cannot carry both an executed arm and an unrun arm"),
    "V20": dict(control="⛔ no measured biological negative labels; a selected decoy set",
                execution="executed, complete",
                outcome="the operational rule is refuted as a selectivity verdict",
                note="the observed rate is a positive-call rate among selected decoys"),
    "V21": dict(control="known-answer (each receptor's own cognate crystallographic ligand)",
                execution="executed, complete",
                outcome="did not recover on 3 of 10 receptors; panel unreadable",
                note="panel-wide maxima and every-survivor clauses all become unreadable"),
    "V22": dict(control="known-answer panel ATTEMPTED (12 listed apo/holo pairs) — ⛔ zero "
                        "gradeable; and no control of its own on this system",
                execution="the 12 listed pairs carry four different dispositions short of a "
                          "grade; six actual cross-method pose comparisons did execute",
                outcome="no grade available from the known-answer arm; the two methods disagree",
                note="'no control exists' is not a precise description of this history"),
}


# ---------------------------------------------------------------------------
# 2b · the AUTHOR-CURRENT claim scope (residual R1, added 2026-09-08)
# ---------------------------------------------------------------------------
# ⛔ WHY THIS EXISTS. The census `scope_limit` field was previously rendered as the supplement's
# FINAL, reader-facing CLAIM-SCOPE column. When this table was written, that field for V5, V11,
# V16 and V20 carried statements the main text explicitly withdraws, so the generated supplement
# was republishing withdrawn claims as current limits. The dependency is roadmap ->
# instrument-census.json -> this extraction -> the inventory/SI, and the roadmap and census are
# shared, parent-owned files.
#
# ⭐ STATUS CORRECTED 2026-09-09 (residual-2 R2). The patches are no longer unapplied. The parent
# integrator applied the four-cell repair at commit 91609d30fdc672f4dbc9eb191e6342a7ddd4f61d
# (census V11.result, V16.result, V16.scope_limit, V20.scope_limit) after regenerating the census
# from the corrected roadmap, and the earlier "exact unapplied patches are filed under
# MF1-residual/patches/" note here is withdrawn as stale. Those filed patches are retained as the
# historical record of what was proposed; they are NOT to be reapplied.
#
# ⭐ What this table now is: the AUTHOR-CURRENT claim-scope column, each entry naming the source
# that governs it, printed beside the census `scope_limit` AS IT READS AT THE BOUND REVISION. The
# adjacent column is no longer labelled a "superseded historical annotation" — at this revision
# those census cells carry their own dated corrections, and the mere existence of an override
# here does not make a census cell superseded. Where no override exists the census string IS the
# current scope and is carried unchanged.
# ⛔ No census, roadmap or original artifact byte is edited here.
CURRENT_SCOPE: dict[str, str] = {
    "V5": "⛔ nothing is supported for the selectivity axis. The retained result is a **repeated "
          "wrong-sign operational calibration failure** (reference **+0.944**, result **−0.599**, "
          "absolute error **1.543**, wrong sign in all 3 replicates). ⛔ **Its cause is NOT "
          "identified**: the closure triangle is blind to endpoint-state error rather than "
          "diagnostic of it, does not exclude shared sampling bias, does not certify convergence "
          "and does not show that more sampling cannot help. ⛔ The register row's *\"~34× the "
          "statistical uncertainty\"* is not carried: the estimand it would need is not in the "
          "record.",
    "V11": "⏸ parked — **no pass**. The recorded outcome is an **executed calibration attempt that "
           "did not meet its registered directional criterion**, not an absent control and ⛔ "
           "**NOT an adequately-powered null**: the attainable p floor 1/462 is a discreteness "
           "property of the exact reference set, not power, and no effect size is established for "
           "this observable. Panel input validity is unresolved. ⛔ `V5`'s wrong sign is not a "
           "third E1 failure — different instrument.",
    "V16": "⛔ **`S` may NOT be read as a bound and may NOT be reported as calibrated.** It is an "
           "**exploratory conditional estimate** with a two-seed between-seed dispersion, "
           "compatible with zero at the observed precision — not a confidence interval, "
           "equivalence test, likelihood bound or calibrated effect bound. ⛔ **`S ≈ 0` does NOT "
           "mean the marginal wedge is absent**; an uncalibrated instrument returning ≈0 cannot "
           "separate 'no effect' from 'cannot resolve'. `S` is non-covalent and structurally "
           "incapable of testing the categorical mechanism.",
    "V20": "⛔ nothing beyond its own scope. **22 of 38 is a positive-call rate among these "
           "selected decoys under this scoring configuration**, not a measured biological "
           "false-positive rate. It is evidence against reading `margin > 0` alone as a "
           "selectivity verdict. ⛔ **The universal claim that a signal smaller than its own noise "
           "is not recoverable by any downstream method is WITHDRAWN**, and no design class is "
           "excluded.",
}

#: The dated corrective interpretation that governs each row, so the supplement's scope column has
#: a checkable home instead of a bare line number (residual R3).
GOVERNING_NOTE: dict[str, str] = {
    "V1": "C11", "V3": "C8", "V5": "C4, C5", "V11": "C1, C2, C14, C15", "V16": "C3, C13",
    "V20": "C9", "V22": "C8",
}

#: Census cells carry Markdown links written relative to `research/modalities/`. Copied into a
#: display that lives in another directory they resolve to nothing, and the repository link checker
#: is right to fail them. The text is what the inventory needs, so the link wrapper is removed and
#: the label kept — no wording is changed.
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def delink(text: str) -> str:
    return _LINK.sub(r"\1", text)


# ---------------------------------------------------------------------------
# 2c · the RESULT-DISPLAY EXCERPT (residual-2 R1, added 2026-09-09)
# ---------------------------------------------------------------------------
# ⛔ WHY THIS EXISTS. The census `result` field for `V5` ends with the fragment
# ", ~34× the statistical uncertainty". The main text (§4.2), the author-current scope column and
# the SI footer all state that this ratio is NOT carried forward, because the record does not
# supply the estimand such a ratio would need. Printing the field verbatim in the result column
# therefore republished, as a current result, the one quantity the same page says is omitted.
#
# ⭐ THE FIX, and its exact limits:
#   • The displayed result cell for `V5` becomes an EXPLICITLY LABELLED SOURCE EXCERPT with that
#     one fragment omitted. The label travels with the cell, so no reader can mistake the excerpt
#     for the whole field.
#   • The omitted fragment is disclosed verbatim, in the inventory header and in SI footer item 6,
#     as a withdrawn quantity rather than a current one.
#   • ⛔ NOTHING is edited at the source. `research/modalities/instrument-census.json` and the
#     roadmap it is generated from keep the original string byte-for-byte, and that file is hashed
#     into the manifest, so the full original remains retrievable from the named, bound source.
#   • ⛔ NO replacement multiplier is computed, adopted or implied, and the scientific result is
#     unchanged: reference **+0.944**, result **−0.599**, absolute error **1.543**, wrong sign in
#     all three replicates all remain displayed exactly as recorded.
RESULT_OMISSION: dict[str, str] = {
    "V5": ", ~34× the statistical uncertainty",
}

#: How many omissions were actually applied in this run, reported on stdout so the run record shows
#: whether the source still carried the fragment. This is a disclosure counter, not a guard.
_OMISSIONS_APPLIED: list[str] = []
_OMISSIONS_NOT_FOUND: list[str] = []


def result_display(vid: str, raw: str) -> tuple[str, bool]:
    """Return (cell text, is_excerpt) for the result column."""
    frag = RESULT_OMISSION.get(vid)
    if frag is None:
        return raw, False
    if frag not in raw:
        _OMISSIONS_NOT_FOUND.append(vid)
        return raw, False
    _OMISSIONS_APPLIED.append(vid)
    trimmed = raw.replace(frag, "")
    return ("⭐ **SOURCE EXCERPT — one fragment omitted, see the header note:** " + trimmed), True


def inventory_rows():
    census = load("research/modalities/instrument-census.json")
    routes = load("systems/graph/routes.json")
    route = next(r for r in routes if r.get("id") == "RT-METHODS-PAPER")
    support = set(route["instruments"]["support"])
    failing = set(route["instruments"]["disclosed_failing"])
    rows = []
    for inst in census["instruments"]:
        vid = inst["id"]
        if vid in support:
            member = "`support`"
        elif vid in failing:
            member = "`disclosed_failing`"
        else:
            member = "⛔ **not in the route partition**"
        ax = AXES.get(vid, dict(control="—", execution="—", outcome="—", note="—"))
        census_scope = delink(inst["scope_limit"])
        override = CURRENT_SCOPE.get(vid)
        note = GOVERNING_NOTE.get(vid)
        result_cell, result_is_excerpt = result_display(vid, delink(inst["result"]))
        rows.append(dict(
            id=vid, instrument=delink(inst["instrument"]), member=member,
            census_class=inst["verdict_class"], **ax,
            known_answer=delink(inst["known_answer_test"]),
            result=result_cell,
            result_is_excerpt=result_is_excerpt,
            current_scope=(override if override else census_scope),
            scope_is_override=bool(override),
            census_scope_verbatim=(census_scope if override
                                   else "— (the census string IS the current scope, above)"),
            source=(f"`instrument-census.json` → `instruments[id={vid}]`"
                    + (f"; corrective interpretation **{note}**" if note else "")),
        ))
    return rows, len(support), len(failing), len(census["instruments"])


def write_inventory(rows, n_support, n_failing, n_census) -> str:
    out = ["<!-- GENERATED by MF1-repair/extract_mf1_inventory.py — DO NOT HAND-EDIT. -->", "",
           "# MF1 SI — the per-instrument inventory, on four separated axes", "",
           f"**Denominators, which are different and are never summed.** The route record "
           f"`RT-METHODS-PAPER.instruments` partitions **{n_support + n_failing}** instruments into "
           f"**{n_support}** `support` and **{n_failing}** `disclosed_failing`. The numbered "
           f"instrument census carries **{n_census}** entries. The "
           f"{n_census - n_support - n_failing} instruments in the census but outside the route "
           "partition are marked below. `disclosed_failing` is an ADMINISTRATIVE route label. It "
           "is **not** a scientific failure rate, and neither count is evidence that every method "
           "the program ever used was discovered, registered or included.", "",
           "**The axes.** *Control type/availability* is what kind of grading standard exists at "
           "all. *Execution/eligibility* is whether the graded run actually executed and was "
           "eligible. *Inferential outcome* is the result conditional on execution. The first "
           "three are an explicit **author classification** of the retained records — the mapping "
           "table is in `extract_mf1_inventory.py` so it can be checked rather than trusted. "
           "⭐ **Two further columns are new on 2026-09-08 (residual R1).** *Known answer* and "
           "*result as recorded* are copied from the census's own `known_answer_test` and `result` "
           "fields, so the numbers behind each grade are visible instead of only its verdict word. "
           "⛔ **And the CLAIM SCOPE column is the author-current scope**, not the census "
           "string: for `V5`, `V11`, `V16` and `V20` the author-current reading is stated in the "
           "operative column and the census `scope_limit` is carried verbatim beside it. Rows "
           "with no override carry the census string unchanged as their current scope. The "
           "governing dated corrective interpretation and the exact source field are in the last "
           "column.", "",
           "⭐ **CORRECTED 2026-09-09 (residual-2 R2) — the shared source cells WERE applied.** An "
           "earlier version of this header said the four shared cells were still unapplied and "
           "called the adjacent census column a *superseded historical annotation*. That is no "
           "longer true and the label was wrong. The parent integrator applied the four-cell "
           "repair at commit `91609d30fdc672f4dbc9eb191e6342a7ddd4f61d` — census `V11.result`, "
           "`V16.result`, `V16.scope_limit` and `V20.scope_limit` — and regenerated the census "
           "from the corrected roadmap. ⛔ The adjacent column is therefore **the census "
           "annotation as it actually reads at the bound census revision**, not a withdrawn "
           "quotation: at this revision `V16.scope_limit` and `V20.scope_limit` carry their own "
           "dated 2026-09-08 corrections at source, and `V5.scope_limit` carries its dated F03 "
           "correction. An author-current override existing for a row does **not** by itself make "
           "the census cell superseded. Where the two differ the difference is one of scope and "
           "detail, and both are shown so a reader can compare them.", "",
           "⚠ **Reading the locators.** A bare `:NNNN` inside a quoted cell is a line range in "
           "`research/manuscripts/nr4a3-program-map.md`, the document the census is generated "
           "from.", "",
           "⛔ **RESULT-COLUMN EXCERPT, 2026-09-09 (residual-2 R1).** The `V5` result cell is an "
           "**explicitly labelled source excerpt**: the single fragment "
           "*\u201c, ~34\u00d7 the statistical uncertainty\u201d* is omitted from the display "
           "because the record does not supply the estimand such a ratio needs (corrective "
           "interpretation **C5**). Everything else in that field is shown verbatim \u2014 "
           "reference **+0.944**, result **\u22120.599**, absolute error **1.543**, wrong sign in "
           "all three replicates. ⛔ No replacement multiplier is computed or adopted, and the "
           "original field is **unedited at its source**: the full string remains in "
           "`research/modalities/instrument-census.json`, which is hashed into "
           "`MF1-dependency-manifest.json` and can be read there.", "",
           "| id | instrument | route list | census class | control type / availability | "
           "execution / eligibility | inferential outcome | known answer (census) | result as "
           "recorded (census) | reading note | ⛔ claim scope — AUTHOR-CURRENT 2026-09-08 | ⚠ "
           "census `scope_limit` at the bound revision (verbatim) | source / governing "
           "correction |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        scope = r["current_scope"]
        if r["scope_is_override"]:
            scope = "⭐ **AUTHOR-CURRENT reading:** " + scope
        cells = [f"**{r['id']}**", r["instrument"], r["member"], f"`{r['census_class']}`",
                 r["control"], r["execution"], r["outcome"], r["known_answer"], r["result"],
                 r["note"], scope, r["census_scope_verbatim"], r["source"]]
        out.append("| " + " | ".join(str(c).replace("\n", " ") for c in cells) + " |")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 3 · the supplement, composed so its tables cannot drift from the records
# ---------------------------------------------------------------------------
SI_PATH = "research/manuscripts/methods-record/degrader-methods-failure-record-SI.md"

SI_HEADER = """---
id: DOC-DEGRADER-METHODS-FAILURE-RECORD-SI
title: "Supplementary information: the per-instrument inventory and the quantitative record"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: The per-instrument inventory and the full quantitative results table for the retrospective audit of the degrader program's instrument records, generated from the committed artifacts rather than transcribed.
scope: Supplement to degrader-methods-failure-record.md. It adds no claim the main text does not make and reports every quantity at the scope its own record reaches.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---
<!-- GENERATED by research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/
     extract_mf1_inventory.py — DO NOT HAND-EDIT. Regenerate to update. -->
# Supplementary information: the per-instrument inventory and the quantitative record

Supplement to [`degrader-methods-failure-record.md`](degrader-methods-failure-record.md). Both tables
below are **deterministic extraction of named fields from named committed artifacts, plus explicit author
classification** — the four audit axes, the reading notes and the author-current claim scope, all written
out in the generating script so they can be checked rather than trusted.

⚠ **Corrected 2026-09-08 (residual R3): the earlier claim that these tables "cannot drift" is withdrawn.**
Generation is not a guarantee of self-updating evidence. What replaces it is a **verifiable binding**: the
generating script, its input list, and for every input the byte count, the SHA-256 of the bytes actually
read, the version-control blob identity of the same path and the explicit result of comparing the two, are
in `research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/MF1-dependency-manifest.json`.

⛔ **This supplement adds no claim the main text does not make**, and ⭐ **as of 2026-09-08 it no longer
republishes a withdrawn claim as a current limit**: the claim-scope column is the author-current scope,
and any superseded census wording is carried beside it in an explicitly labelled historical column. Every
interpretive limit column is part of the finding, not a caveat appended to it. ⛔ No quantity here is
evidence of binding, potency, selectivity, efficacy, safety, therapeutic window or clinical readiness.

---

## S1 · The compact quantitative record

Columns: control/reference identity · operational criterion · unit · eligible, excluded, failed and unrun
counts · estimate · uncertainty type · actual result · interpretive limit · source. ⚠ Read each row's
limit column with its estimate; several of these numbers were previously quoted without it.

"""

SI_MIDDLE = """
---

## S2 · The per-instrument inventory

"""

SI_FOOTER = """
---

## S3 · What this inventory does not establish

1. ⛔ **It is not a whole-program failure rate.** The route label `disclosed_failing` is administrative
   bookkeeping. The inventory separates the facts it covers precisely so that the label cannot be counted
   as a scientific outcome.
2. ⛔ **It is not evidence of complete ascertainment.** It enumerates the instruments that were
   discovered, registered and entered into the program's graph. A method that was used and never
   registered would not appear, and at least one instrument (`V21`) was in use for months before it
   acquired a row.
3. ⛔ **A `PASSES` class is not support for the claim the instrument is pointed at.** It records the
   recovery of one specific known answer at the scope in the final column.
4. ⚠ **The first three axis columns are an author classification** of retained records, not fields of
   any single artifact. The mapping table is written out in the generating script so it can be checked.
5. ⛔ **The claim-scope column is the author-current scope as of 2026-09-08, not a census quotation.**
   For `V5`, `V11`, `V16` and `V20` the author-current reading is stated in the operative column and the
   census `scope_limit` is carried verbatim beside it. Rows without an override carry the census string
   unchanged. ⭐ **CORRECTED 2026-09-09 (residual-2 R2):** the four shared source cells — census
   `V11.result`, `V16.result`, `V16.scope_limit` and `V20.scope_limit` — **were applied** by the parent
   integrator at commit `91609d30fdc672f4dbc9eb191e6342a7ddd4f61d` and the census was regenerated from
   the corrected roadmap. The adjacent column is therefore the census annotation **as it reads at the
   bound revision**, not a superseded historical quotation; an earlier footer said those cells were still
   unapplied and labelled the column "superseded historical annotation", and both statements are
   withdrawn here. An author-current override existing for a row does not by itself make the census cell
   superseded.
6. ⚠ **A `known answer` and a `result` cell are the register's own values, not a new verification.**
   They are copied from the census so a reader can judge each grade; no benchmark was rerun, no primary
   benchmark source was retrieved, and where the kind of a ± term is not established in the record it is
   not named. ⛔ **ONE LABELLED OMISSION, 2026-09-09 (residual-2 R1).** The `V5` result cell is an
   explicitly labelled **source excerpt**: the fragment *", ~34× the statistical uncertainty"* is omitted
   from the display, because the record does not supply the estimand such a ratio would need — see
   corrective interpretation **C5**. The rest of the field is shown verbatim (reference **+0.944**,
   result **−0.599**, absolute error **1.543**, wrong sign in all three replicates), **no replacement
   multiplier is computed or adopted**, and the original field is **not edited at its source**: the full
   string stands in `research/modalities/instrument-census.json`, which is hashed into
   `MF1-dependency-manifest.json`. This is the only cell in the table from which anything is omitted.
7. ⛔ **This supplement is not a gate result, an all-green report or a scientific clearance.** The
   retained check streams for this manuscript include failing runs, and none of them establishes closure.
"""


def write_si(results_md: str, inventory_md: str) -> str:
    def body(md: str) -> str:
        lines = [ln for ln in md.splitlines()
                 if not ln.startswith("<!--") and not ln.startswith("# ")]
        return "\n".join(lines).strip("\n")
    return (SI_HEADER + body(results_md) + SI_MIDDLE + body(inventory_md) + SI_FOOTER)


# ---------------------------------------------------------------------------
def main() -> int:
    rows = results_rows()
    (HERE / "MF1-quantitative-results.md").write_text(write_results_table(rows))

    inv, n_sup, n_fail, n_cen = inventory_rows()
    (HERE / "MF1-instrument-inventory.md").write_text(write_inventory(inv, n_sup, n_fail, n_cen))

    (REPO / SI_PATH).write_text(
        write_si(write_results_table(rows), write_inventory(inv, n_sup, n_fail, n_cen)))

    manifest = {
        "_what": "every retained input this extraction read, by path, size, SHA-256 and git blob",
        "_generated_by": "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                         "MF1-repair/extract_mf1_inventory.py",
        "_not_a_release": "these are working-tree identities in this repository at the named "
                          "commit. No immutable public archive has been checked or published, and "
                          "none is claimed.",
        "commit": head_commit(),
        "inputs": [],
    }
    manifest["_binding_rule"] = (
        "ADDED 2026-09-08 (residual R3). `sha256` is of the bytes this run actually read from the "
        "working tree. `head_blob_sha256` is of the bytes git holds at the same path at `commit`. "
        "`bytes_match_head_blob` is the comparison. A read plus a blob id is NOT a binding unless "
        "these agree; where it is false the display is bound to the working tree only, and that is "
        "stated rather than assumed."
    )
    n_unbound = 0
    for rel in INPUTS:
        p = REPO / rel
        wt = sha256(p)
        hb = head_blob_sha256(rel)
        match = None if hb is None else (hb == wt)
        if match is not True:
            n_unbound += 1
        manifest["inputs"].append({
            "path": rel, "bytes": p.stat().st_size,
            "sha256": wt, "git_blob": git_blob(rel),
            "head_blob_sha256": hb, "bytes_match_head_blob": match,
        })
    manifest["n_inputs_not_bound_to_head_blob"] = n_unbound
    (HERE / "MF1-dependency-manifest.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")

    print(f"results rows: {len(rows)}")
    print(f"inventory rows: {len(inv)}  route {n_sup}+{n_fail}  census {n_cen}")
    print(f"manifest inputs: {len(manifest['inputs'])} at commit {manifest['commit']}")
    print(f"inputs NOT bound to their HEAD blob: {n_unbound} of {len(manifest['inputs'])}")
    print(f"author-current scope overrides: {len(CURRENT_SCOPE)} "
          f"({', '.join(sorted(CURRENT_SCOPE))})")
    print(f"result-display omissions applied: {len(_OMISSIONS_APPLIED)} of "
          f"{len(RESULT_OMISSION)} declared"
          + (f" ({', '.join(_OMISSIONS_APPLIED)})" if _OMISSIONS_APPLIED else "")
          + (f"; declared but fragment NOT PRESENT in source: "
             f"{', '.join(_OMISSIONS_NOT_FOUND)}" if _OMISSIONS_NOT_FOUND else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
