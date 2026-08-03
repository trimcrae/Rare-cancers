#!/usr/bin/env python3
"""
Pins the BRANCH-1b reconciliation (roadmap §10.1 row 5) to the artifact it reconciles against.

⛔ THE FAILURE MODE THIS GUARDS. The §7 prose was written from an agent's REPORTED values before
`nr4a3-linker-covalent-reach.json` existed, and at least one residue disagreed with the artifact when it
landed. Reconciling it once is not enough: the artifact can be re-run, and a re-run that moves a count would
silently put the prose back out of step. So these tests re-derive the load-bearing figures from the artifact
and refuse if they no longer match the reconciliation record.

They are cheap — no generator is re-run, only two JSON files are read.
"""

import collections
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(MOD, "..", ".."))

RECON = os.path.join(MOD, "nr4a3-branch1b-reconciliation.json")
REACH = os.path.join(MOD, "nr4a3-linker-covalent-reach.json")
ROADMAP = os.path.join(REPO, "research", "manuscripts", "nr4a3-program-map.md")


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def recon():
    assert os.path.exists(RECON), (
        "the branch-1b reconciliation record is missing. Regenerate with "
        "`python3 research/modalities/nr4a3_branch1b_reconcile.py`.")
    return _load(RECON)


@pytest.fixture(scope="module")
def reach():
    return _load(REACH)


def _claim(recon, letter):
    for c in recon["claims_re_derived_independently"]:
        if c["claim"] == letter:
            return c
    raise AssertionError("claim %r is not in the reconciliation record" % letter)


# =============================================================================================================
# The two cysteines that are NOT equal, and the label that says they are
# =============================================================================================================

def test_C420_is_refuted_at_every_cell_and_C559_is_not(reach):
    rc = reach["experimental_ensemble_8xtt"]["reachable_conformer_counts"]
    per = collections.defaultdict(lambda: {"n": 0, "ts": [], "co": []})
    for v in rc.values():
        o = per[v["cysteine"]]
        o["n"] += 1
        if v["through_space"] > 0:
            o["ts"].append((v["placement"], v["pendant"], v["through_space"], v["n_conformers"]))
        if v["corridor"] > 0:
            o["co"].append((v["placement"], v["pendant"], v["corridor"], v["n_conformers"]))
    assert per["C420"]["ts"] == [] and per["C420"]["co"] == [], (
        "C420 now reaches somewhere: %s / %s. The roadmap states it is refuted at every cell under both "
        "conventions." % (per["C420"]["ts"], per["C420"]["co"]))
    assert per["C559"]["co"] == [], "C559 now has corridor reach: %s" % per["C559"]["co"]
    assert len(per["C559"]["ts"]) == 1, (
        "C559's through-space survival is no longer confined to exactly one cell: %s. The roadmap names that "
        "one cell explicitly, so the prose moves with it." % per["C559"]["ts"])
    placement, pendant, ts, nconf = per["C559"]["ts"][0]
    assert (placement, pendant, ts, nconf) == ("vhl|M3@term_a_exemplar", "dab_branch", 2, 19), (
        "C559's surviving cell moved to %r — the roadmap quotes "
        "`vhl|M3@term_a_exemplar | dab_branch`, 2 of 19 conformers."
        % ((placement, pendant, ts, nconf),))


def test_the_refuted_label_is_still_built_from_the_corridor_alone(reach):
    """The roadmap says the artifact's own label over-claims. If the artifact is fixed, that caveat must go."""
    v = reach["verdict"]
    assert "C559" in v["refuted_unique_cysteines"], (
        "the artifact no longer labels C559 refuted — good, but the roadmap's caveat that "
        "`refuted_unique_cysteines` is 'stronger than its own data' is then stale and must be removed.")
    assert v["per_unique_cysteine_conformer_counts"]["C559"]["best_through_space"] > 0
    assert v["per_unique_cysteine_conformer_counts"]["C559"]["best_corridor"] == 0


# =============================================================================================================
# The closer counts the prose quotes, and the alignments that decide what they mean
# =============================================================================================================

def test_the_closer_counts_the_prose_quotes_still_reproduce(reach):
    """24 of 30 through-space (NR4A1 C505) and 23 of 30 corridor (NR4A2 C534), over term_a_exemplar cells.

    ⚠ The denominator is not the 60 rows in the window block — `verdict()` filters to `term_a_exemplar`
    before summarising, and that filter is where every '… of 30' in the roadmap comes from.
    """
    want = {"through_space": ("NR4A1 C505", 24), "corridor": ("NR4A2 C534", 23)}
    for conv, cells in reach["★_family_wide_chemoselectivity_window"]["by_convention"].items():
        graded = [c for c in cells if "term_a_exemplar" in c["placement"]]
        assert len(graded) == 30, "the graded denominator moved to %d for %s" % (len(graded), conv)
        cnt = collections.Counter(c["closed_by"] for c in graded if c["closed_by"])
        residue, n = want[conv]
        assert cnt[residue] == n, "%s: %s closes %d of 30, the roadmap says %d" % (conv, residue, cnt[residue], n)
        assert sum(1 for c in graded if c["closed_by"] and not c["closed_by"].startswith("NR4A3")) == 30, (
            "%s: the closer is no longer on a paralogue chain in all 30 graded cells" % conv)


def test_C505_aligns_to_an_NR4A3_cysteine_and_C534_does_not(reach):
    """This is the distinction the mermaid `PAR` node still gets wrong, and the reason it must be corrected."""
    ru = reach["paralogue_control"]["reciprocal_uniqueness"]["by_paralogue"]
    assert ru["NR4A1"]["C505"]["nr4a3_aligned_residue"] == "C536"
    assert ru["NR4A1"]["C505"]["paralogue_unique_vs_NR4A3"] is False, (
        "NR4A1 C505 is now recorded as a site NR4A3 lacks. The roadmap's correction rests on the opposite.")
    for par in ("NR4A1", "NR4A2"):
        assert ru[par]["C534"]["nr4a3_aligned_residue"] == "S565"
        assert ru[par]["C534"]["paralogue_unique_vs_NR4A3"] is True


def test_the_paralogue_unique_set_has_the_two_members_the_record_names(recon, reach):
    ru = reach["paralogue_control"]["reciprocal_uniqueness"]["by_paralogue"]
    unique = sorted({c for par in ru for c, rec in ru[par].items() if rec["paralogue_unique_vs_NR4A3"]})
    assert unique == ["C534", "C551"], (
        "the paralogue-unique cysteine set is now %s. The reconciliation record names C534 (the corridor "
        "closer) and C551 (NR4A1 only, far outside the window and mentioned in no prose)." % unique)


# =============================================================================================================
# The two qualifications the prose did not carry
# =============================================================================================================

def test_the_noise_bound_still_cannot_cover_the_corridor_closer(recon, reach):
    e = _claim(recon, "e")["read"]
    covered = {p["paralogue_cysteine"] for p in reach["paralogue_control"]["aligned_pair_displacement"]["pairs"]}
    assert "C534" not in covered, (
        "C534 now has an aligned NR4A3 partner, which would mean it is no longer paralogue-unique. The "
        "roadmap's qualification — that the residue closing 23 of 30 corridor cells is the one residue the "
        "noise test cannot bound — would then be stale.")
    assert e["closers_with_NO_measured_bound"] == ["C534"]
    assert e["margin_A"] == pytest.approx(0.31, abs=0.005), (
        "the noise margin moved to %s Å; the roadmap quotes 0.31 Å (a 5 %% margin)." % e["margin_A"])


def test_closed_by_is_still_a_tie_break_in_the_minority_the_banner_quotes(recon):
    ties = None
    for f in recon["newly_found_in_this_pass"]["also"]:
        if isinstance(f.get("read"), dict) and "n_rows_where_the_closer_ties" in f["read"]:
            ties = f["read"]
    assert ties is not None, "the tie-break measurement is missing from the reconciliation record"
    assert (ties["n_rows_with_a_closer"], ties["n_rows_where_the_closer_ties"]) == (93, 35), (
        "the tie-break rate moved to %d of %d; the roadmap banner quotes 35 of 93."
        % (ties["n_rows_where_the_closer_ties"], ties["n_rows_with_a_closer"]))


# =============================================================================================================
# The diagram — the half nobody had graded
# =============================================================================================================

def test_the_diagram_findings_name_text_that_is_actually_in_the_roadmap(recon):
    """Until these edits are applied both should be live. Once applied, this test says so and is updated.

    ⚠ It deliberately does NOT assert they are still live — that would make applying the fix turn CI red.
    It asserts the record is HONEST about which state we are in.
    """
    with open(ROADMAP, encoding="utf-8") as fh:
        text = fh.read()
    for f in recon["newly_found_in_this_pass"]["findings"]:
        live_now = None
        for key in ("element",):
            assert f.get(key)
        # the record stamps liveness at generation time; re-check it against the file as it stands
        edge = 'L -->|"C420, C559: no, at every<br/>placement and pendant"| DEAD'
        node = 'PAR["The window is closed by a<br/>PARALOGUE cysteine, which<br/>NR4A3 does NOT have"]'
        live_now = (edge in text) if "edge" in f["element"] else (node in text)
        assert f["present_in_the_live_roadmap"] == live_now or not f["present_in_the_live_roadmap"], (
            "the reconciliation record says %r is present in the roadmap and it is not. Regenerate the "
            "record after applying an edit, so it never claims a correction is outstanding when it is done."
            % f["element"])


def test_every_audit_edit_is_accounted_for(recon):
    ag = recon["the_audits_own_edits"]
    assert ag["n_edits"] == len(ag["rows"])
    for r in ag["rows"]:
        assert r["status"], "an audit edit has no status: %r" % r["anchor"]
    assert ag["relocated_to"], "the record must say where the relocated edits now live"
