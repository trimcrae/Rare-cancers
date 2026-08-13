"""The gene-symbol authority — and the two ways it must refuse rather than guess.

★ WHAT THIS INDEX IS FOR. Three consumers, each of which was previously either wrong or hand-written:
symbol validation for the fusion census (`ACT` is not a gene), parent RefSeq accessions for the
off-target screen (inert for every non-EWSR1 donor until this existed), and the alias table (four genes
by hand, now 45,032 fetched).

⛔ THE REFUSALS ARE THE POINT. An unknown symbol and an ambiguous alias must be distinguishable from a
resolved one, because both of the downstream uses — "is this a fusion?" and "which transcript is the
parent?" — are silently wrong if a guess is substituted for either.
"""
from __future__ import annotations

import gzip
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hgnc_index as hg  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(hg.OUT),
                                reason="hgnc-gene-index.json.gz not built in this checkout")


# ── schema discipline ───────────────────────────────────────────────────────────────────────────
HEADER = ("hgnc_id\tsymbol\tname\tlocus_group\tstatus\talias_symbol\tprev_symbol\t"
          "refseq_accession\tensembl_gene_id\tentrez_id")


def _row(sym, status="Approved", aliases="", prev="", refseq="", ens="", entrez=""):
    return f"HGNC:1\t{sym}\tname\tprotein-coding gene\t{status}\t{aliases}\t{prev}\t{refseq}\t{ens}\t{entrez}"


def test_a_changed_schema_raises_rather_than_building_a_partial_index():
    """⛔ A positional read of a file that gained a column is a silent mis-parse. Refuse instead."""
    with pytest.raises(RuntimeError, match="missing"):
        hg.build_index("symbol\tstatus\nEWSR1\tApproved")


def test_withdrawn_symbols_are_excluded():
    genes, _alias, stats = hg.build_index(
        f"{HEADER}\n{_row('GOODGENE')}\n{_row('DEADGENE', status='Entry Withdrawn')}")
    assert "GOODGENE" in genes and "DEADGENE" not in genes
    assert stats["not_approved"] == 1


def test_an_alias_shared_by_two_genes_resolves_to_ambiguous(tmp_path):
    """⛔ THE REFUSAL THAT MATTERS MOST. Picking one of two approved genes would retarget a screen at
    the wrong transcript, and nothing downstream would notice."""
    genes, alias_to, _ = hg.build_index(
        f"{HEADER}\n{_row('GENEA', aliases='SHARED')}\n{_row('GENEB', aliases='SHARED')}")
    assert alias_to["SHARED"] == hg.AMBIGUOUS
    assert set(genes) == {"GENEA", "GENEB"}


def test_a_gene_that_is_its_own_alias_does_not_self_ambiguate():
    _genes, alias_to, _ = hg.build_index(f"{HEADER}\n{_row('GENEA', aliases='GENEA|OTHER')}")
    assert alias_to.get("GENEA") is None      # not recorded as an alias of itself
    assert alias_to["OTHER"] == "GENEA"


def test_previous_symbols_resolve_like_aliases():
    _genes, alias_to, _ = hg.build_index(f"{HEADER}\n{_row('TAF15', prev='TAF2N')}")
    assert alias_to["TAF2N"] == "TAF15"


# ── against the committed index ─────────────────────────────────────────────────────────────────
def test_the_committed_index_is_self_consistent():
    assert hg.check() == 0


def test_act_is_not_a_gene_which_is_why_the_shakeout_row_was_junk():
    """The census shakeout (run 31740571888) scored `ACT::FOSB` as attempted on 322 records because
    `ACT` matches the English word. Symbol validation removes that row at the source."""
    assert hg.is_approved_symbol("ACT") is False
    assert hg.is_approved_symbol("FOSB") is True


@pytest.mark.parametrize("symbol,accession", [
    ("EWSR1", "NM_005243"),      # was hardcoded in junction_aso.py — independently confirmed here
    ("NR4A3", "NM_006981"),      # likewise
    ("TAF15", "NM_139215"),      # the three the repo declined to type from memory
    ("TCF12", "NM_003205"),
    ("FUS", "NM_004960"),
])
def test_parent_accessions_come_from_a_fetch_not_from_memory(symbol, accession):
    """These are the accessions `junction_aso_offtarget.PARENT_ACCS` could not hold. A test pins them
    to the fetched index so a future edit cannot quietly substitute a remembered value."""
    assert hg.refseq_for(symbol) == accession


def test_nor1_is_ambiguous_even_though_it_is_the_emc_genes_common_name():
    """⚠ The EMC manuscript calls NR4A3 'NOR-1' throughout. `NOR1` is nonetheless an alias of more than
    one approved gene, so this must NOT resolve — the familiar name is not a safe key."""
    assert hg.resolve("NOR1") == hg.AMBIGUOUS
    assert hg.resolve("EWS") == "EWSR1"
    assert hg.resolve("TAF2N") == "TAF15"


def test_an_unknown_symbol_resolves_to_none_not_to_a_guess():
    assert hg.resolve("NOTAGENE12345") is None


def test_aliases_include_the_symbol_itself():
    a = hg.aliases_for("FUS")
    assert a[0] == "FUS" and "TLS" in a


def test_a_missing_index_raises_rather_than_reading_as_empty(tmp_path):
    """⚠ An absent reading is not a reading of absence — an empty index would silently reject every
    real gene, i.e. report a universe of zero fusions as though it were measured."""
    hg._CACHE = None
    with pytest.raises(RuntimeError, match="missing"):
        hg.load(str(tmp_path / "nope.json.gz"))
    hg._CACHE = None


def test_the_index_round_trips_through_gzip():
    with gzip.open(hg.OUT, "rt") as fh:
        blob = json.load(fh)
    assert blob["n_approved_symbols"] == len(blob["genes"])
    assert blob["_source_url"].startswith("https://")
