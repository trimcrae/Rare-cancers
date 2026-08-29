#!/usr/bin/env python3
"""Every gene-shaped identifier the FUSION-PARTNER synthesis prints is one an artifact names.

⛔⛔ WHY THIS EXISTS — ONE-OF-A-PAIR, THE SEVENTH OF ITS CLASS, AND IT WAS MEASURED.
`test_the_manuscripts_gene_identifiers_are_ones_an_artifact_names.py` guards the ASO submission's
identifiers. Nothing guarded this synthesis's. Measured 2026-08-28 (CYC-0070) by the ablation
harness against
`research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md`: perturbing the endpoint
declaration's `NR4A3` to `NR4A7` was one of seven perturbations tried, and **every guard reading the
document stayed green** — the quantity guard beside this file, the relation guard beside that, the
three linters and the pooling check. So the same identifier class was guarded in one paper of this
repository and unguarded in the other, which is `paper-hardening` §6's whole shape. Filed as
`AUT-PD-147`.

⚠ THIS IS THE PROVENANCE AXIS, NOT THE STRENGTH AXIS (CLAUDE.md §7: they are orthogonal). A hedged
sentence carrying a fabricated identifier passes `lint_claims`; a correctly-cited sentence carrying a
one-digit slip passes `lint_citations`. Every other guard on this document reads QUANTITIES or
RELATIONS, and a gene symbol is neither, so nothing was looking — in the one place where being wrong
is unrecoverable, because a reader searches the wrong gene.

★ THE RULE: an identifier earns its place by appearing in a committed artifact. Anything else is
either a typo or a fact from the literature, and a fact from the literature is declared in
`CITED_ONLY` with the reason that carries it — never left to look like an artifact-backed symbol.

⛔ EVERY SITE, NOT "IS THE RIGHT SYMBOL IN HERE SOMEWHERE" (`paper-hardening` §6). The synthesis
prints `NR4A3` 71 times, `TAF15` 100 and `EWSR1` 46, so a membership assertion passes while one site
is wrong. The unattested-symbol check below is per-site by construction — it collects the SET of
tokens the document uses, so a single corrupted site puts an unattested token in that set and the
assertion fires however many correct siblings stand beside it. `MUST_APPEAR` is deliberately the
other shape, a floor against DELETION, which the set check cannot see; it is never the drift check.

⭐ THE SCOPE IS A DIRECTORY PREDICATE, AND IT WAS MEASURED BEFORE IT WAS WRITTEN
(`paper-hardening` §8b.1: a widening is only a fix once you have run it). The ASO guard rejected
"every `.md` in the directory" because that submission's directory holds working notes and a review
backlog that legitimately name genes no artifact attests. Measured here 2026-08-29 over all three
prose documents of this synthesis: **zero unattested identifier-shaped tokens in any of them**, so
the directory predicate is honest for this family and needs no `CITED_ONLY` entry at all. A document
added to this lane tomorrow is in scope without anybody remembering it — which is §8b.2's finding
that a fix bound to a LIST regresses at a sibling and a fix bound to a PREDICATE does not.

⚠ AND THE LITERALS BELOW ARE KEPT ANYWAY, WITH THEIR COMPLETENESS ASSERTED. `claim_ablation.
guards_reading` discovers the guards that read a document by grepping test sources for its BASENAME,
so a purely derived document set makes this file invisible to the ablation gate and the sentences it
protects report BLIND. Both properties are held: the names are literals a static scan can find, and
`test_the_document_set_is_every_prose_document_of_this_synthesis` fails if the directory ever holds
one that is missing here.

⭐⭐ MEASURED, 2026-08-29, BY THE COMMITTED HARNESS — `mutate_fusion_partner_guard.py` beside this
file, which now runs three guard modules separately and names which one fired. 101 mutations, 93
caught, 0 survived, positive control green, every one single-site. **Seven of them are this
module's, and all seven were caught by this module ALONE** — the quantity and relation guards are
green on every one, which is the evidence that these bindings read a surface nothing else reaches.
Among the seven: the measured defect restored verbatim (`NR4A3` -> `NR4A7` in the endpoint
declaration), the same corruption at a second site one section away, `TAF15` -> `TAF19` at 1 of its
100 sites, `EWSR1` -> `EWSR7` at 1 of its 46, the same corruption inside the correction register,
and two pair mutations that leave EVERY token on the page attested.
⚠ AND THE FLOOR WAS MUTATION-TESTED BY HAND, NOT BY THAT HARNESS, WHICH IS SAID HERE RATHER THAN
LEFT TO LOOK COVERED. A deletion cannot be single-site, and the harness asserts every anchor occurs
exactly once — so admitting one would have meant weakening the invariant that makes its other
results readable. Measured instead in an isolated clone: a global `TAF15` -> `TAF-15` in the
register fired `test_the_document_still_names_the_gene_its_result_is_about` ALONE with the
attestation check still green, and a global `EWSR1` -> `EWSR` in the manuscript fired the floor, the
pair check and the vacuity check; both documents were restored to their pristine sha256
(`c57f5658…` and `e01aa79f…`).
⚠ THE HARNESS ALSO REPORTS 8 UN-RUN MUTATIONS whose anchors no longer occur. They are PRE-EXISTING —
reproduced on a pristine clone of `origin/main` at 8edd15fe (86 caught, 0 survived, the same 8
errors) — and none of them is one of these seven. Filed as its own ledger row.

⛔ WHAT THIS DOES NOT CATCH, NAMED RATHER THAN LEFT TO LOOK COVERED. A drift from one ATTESTED
symbol to another attested symbol is invisible to an attestation check — `NR4A3` -> `NR4A1` and
`TAF15` -> `EWSR1` are both real symbols the corpus names. Inside a FUSION-PAIR construction that
hole is closed below by `test_every_fusion_pair_is_one_the_pooling_artifact_names`, which reads the
pair out of the artifact rather than the token out of a corpus; 38 of the manuscript's 71 `NR4A3`
sites are in that form. **Outside a pair construction it remains open**, and the relation guard
beside this file covers only the specific claims it binds. Recorded as a residue, not closed.
"""
from __future__ import annotations

import importlib.util
import io
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
FUSION_PARTNER = os.path.join(MANUSCRIPTS, "fusion-partner")

#: The artifact this synthesis's every number comes from, and the record of which 5' partners it
#: pools. ⛔ The allowed fusion pairs are READ from it, never typed here.
POOLING = os.path.join(FUSION_PARTNER, "emc-fusion-partner-pooling.json")

#: ⚠ LITERALS ON PURPOSE, COMPLETENESS ASSERTED BELOW — see the docstring. `claim_ablation` finds
#: this guard by grepping for these basenames, so a derived-only set would make it invisible to the
#: ablation gate exactly as it did in the sibling module.
DOCUMENTS = {
    "emc-fusion-partner-correction-register":
        os.path.join(FUSION_PARTNER, "emc-fusion-partner-correction-register.md"),
    "emc-fusion-partner-stratification":
        os.path.join(FUSION_PARTNER, "emc-fusion-partner-stratification.md"),
    "partner-event-counts-2026-08-08":
        os.path.join(FUSION_PARTNER, "partner-event-counts-2026-08-08.md"),
}

#: Where an identifier may be attested: the same committed machine-readable corpus the sibling guard
#: reads. ⚠ DELIBERATELY WIDE AND STILL DISCRIMINATING, which is the point — measured 2026-08-29 it
#: holds ~105,600 distinct identifier-shaped tokens and `NR4A7`, `NR4A9`, `EWSR7`, `TAF19`, `TAF16`
#: and `TCF13` are in none of them. Real symbols are a SPARSE set, so a one-digit slip lands outside
#: it. ⛔ The synthesis's OWN artifacts are not in the corpus and must not be added: measured, they
#: contribute exactly one token (`FUSNR4A3`, a flattened key) and nothing else, so the only thing
#: including them buys is a document permitted to attest itself.
ARTIFACT_ROOTS = [os.path.join(REPO, "research", d) for d in ("modalities", "data", "literature")]
ARTIFACT_SUFFIXES = (".json", ".csv", ".jsonl")
#: A file bigger than this is a bulk screen dump; reading it would dominate the gate's runtime.
MAX_ARTIFACT_BYTES = 8_000_000

#: A gene symbol, a cell-line code, an accession: two or more capitals with a digit.
#: ⛔⛔ WRITTEN OUT IN FULL RATHER THAN IMPORTED, AND THE DUPLICATION IS ENFORCED RATHER THAN
#: TOLERATED. `claim_coverage` harvests regexes by STATICALLY READING test sources, so a pattern
#: assembled or imported is invisible to it — `paper-hardening` §8b.1e records the hours that cost.
#: `test_the_identifier_shape_is_the_one_the_sibling_guard_uses` compares this literal against the
#: ASO guard's at runtime and fails if they ever diverge, so the shape stays ONE FACT (CLAUDE.md
#: §1) while remaining complete where it is written.
_IDENTIFIER = re.compile(r"\b(?!PMC\d)(?!PMID)[A-Z]{2,}[0-9]+[A-Z]?[0-9]*\b")
SIBLING = os.path.join(HERE, "test_the_manuscripts_gene_identifiers_are_ones_an_artifact_names.py")

#: A gene-fusion pair as this lane writes it: `EWSR1::NR4A3`.
_FUSION_PAIR = re.compile(r"\b([A-Z][A-Z0-9]*)::([A-Z][A-Z0-9]*)\b")

#: Markdown/typesetting tokens that match the identifier shape without being identifiers.
_NOT_AN_IDENTIFIER = {"H1", "H2", "H3", "P1", "P2", "P3", "R1", "R2", "R3", "R4", "R5",
                      "T1", "T2", "S1", "S2", "S3", "S4", "UTF8", "ISO8601"}

#: ⛔ AN IDENTIFIER NO ARTIFACT NAMES IS ALLOWED ONLY WITH THE REASON THAT CARRIES IT — a bare
#: allowlist would re-open the hole this file exists to close. ⭐ EMPTY, AND THAT IS A MEASUREMENT:
#: all three prose documents were censused 2026-08-29 and every identifier-shaped token in them is
#: attested by the corpus above. An entry added here is a claim about the literature and needs the
#: citation that carries it, never a recollection (CLAUDE.md §7).
CITED_ONLY: dict = {}

#: ⛔ NOT AN ALLOWLIST — A FLOOR. These must be PRESENT; their absence means a document lost the
#: identifier its whole result is about, which no unattested-symbol check can notice. The synthesis
#: is a comparison of two 5' partners, so losing either one destroys the result while leaving a
#: grammatical, correctly-cited paper behind.
MUST_APPEAR = {
    "emc-fusion-partner-stratification": ("NR4A3", "EWSR1", "TAF15"),
    "emc-fusion-partner-correction-register": ("NR4A3", "TAF15"),
    "partner-event-counts-2026-08-08": ("NR4A3", "TAF15", "EWSR1"),
}

_ATTESTED_CACHE = None


def _attested():
    """Every identifier-shaped token any committed artifact uses. Memoised; ~1.3 s over ~820 files."""
    global _ATTESTED_CACHE
    if _ATTESTED_CACHE is not None:
        return _ATTESTED_CACHE
    seen = set()
    for root in ARTIFACT_ROOTS:
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(ARTIFACT_SUFFIXES):
                    continue
                path = os.path.join(dirpath, name)
                try:
                    if os.path.getsize(path) > MAX_ARTIFACT_BYTES:
                        continue
                    seen |= set(_IDENTIFIER.findall(
                        io.open(path, encoding="utf-8", errors="ignore").read()))
                except OSError:
                    continue
    _ATTESTED_CACHE = seen
    return seen


def _text(key):
    return io.open(DOCUMENTS[key], encoding="utf-8").read()


def _front_matter_kind(text):
    """`kind:` from the document's own front matter, or None. The scope predicate for the pair check."""
    m = re.search(r"^kind:\s*(\S+)\s*$", text, re.MULTILINE)
    return m.group(1) if m else None


def _artifact_fusion_pairs():
    """The 5'::3' pairs `emc-fusion-partner-pooling.json` itself names.

    ⛔ READ, NOT TYPED. A partner added to the pooling artifact is permitted in the prose the moment
    the artifact names it, and a partner removed from it stops being permitted — which is the
    property a typed roster does not have. The 2026-08-26 defect on this same document was exactly a
    typed roster that undercounted the moment a cohort was added.
    """
    raw = io.open(POOLING, encoding="utf-8").read()
    return {(a, b) for a, b in _FUSION_PAIR.findall(raw)}


@pytest.mark.committed_artifact
@pytest.mark.parametrize("key", sorted(DOCUMENTS))
def test_every_gene_identifier_is_attested_by_an_artifact_or_a_citation(key):
    """⛔ A ONE-CHARACTER SLIP IN A GENE SYMBOL IS UNRECOVERABLE AND WAS UNGUARDED HERE."""
    assert os.path.exists(DOCUMENTS[key]), (
        f"{key} ({os.path.basename(DOCUMENTS[key])}) is not in this checkout. Every document this "
        "guard reads is committed, so a missing one is a broken tree — which is exactly when a "
        "guard has to speak, not stand down.")
    text = _text(key)
    attested = _attested()
    found = {t for t in _IDENTIFIER.findall(text) if t not in _NOT_AN_IDENTIFIER}
    unknown = sorted(t for t in found if t not in attested and t not in CITED_ONLY)
    assert not unknown, (
        f"{key} names identifier(s) that no committed artifact uses and that are not declared as "
        f"cited-only: {', '.join(unknown)}\n\n"
        "Either the symbol is a typo — check it character by character against the artifact, "
        "because a gene symbol off by one digit reads as a real gene — or it is a fact from the "
        f"literature, in which case add it to CITED_ONLY in {os.path.basename(__file__)} with the "
        "reason and the source that carries it. Never write an identifier from recollection.")


@pytest.mark.committed_artifact
@pytest.mark.parametrize("key", sorted(MUST_APPEAR))
def test_the_document_still_names_the_gene_its_result_is_about(key):
    """⛔ THE UNATTESTED-SYMBOL CHECK ABOVE CANNOT SEE AN IDENTIFIER THAT IS SIMPLY GONE."""
    assert os.path.exists(DOCUMENTS[key]), (
        f"{key} ({os.path.basename(DOCUMENTS[key])}) is not in this checkout, so the genes this "
        "document's result is about cannot be checked at all.")
    text = _text(key)
    missing = [g for g in MUST_APPEAR[key] if not re.search(rf"\b{g}\b", text)]
    assert not missing, (
        f"{key} no longer names {', '.join(missing)}. This synthesis's whole result is a comparison "
        "between 5' fusion partners; if a partner has genuinely left the document, MUST_APPEAR is "
        "the one place to say so.")


def _pair_checked_documents():
    """The documents the fusion-pair predicate applies to: this lane's prose that is not a register.

    ⛔ A PROPERTY, NOT A FILE LIST (`paper-hardening` §8b.2), and it is resolved here rather than by
    a `pytest.skip` inside the check — a guard that declines to run is indistinguishable from one
    that never ran, which is the whole subject of `test_no_guard_can_silently_not_run.py`. The
    non-emptiness of what this returns is asserted below, so an empty scope is a failure and never
    a quiet pass.
    """
    return {k for k in DOCUMENTS if _front_matter_kind(_text(k)) != "register"}


@pytest.mark.committed_artifact
@pytest.mark.parametrize("key", sorted(_pair_checked_documents()))
def test_every_fusion_pair_is_one_the_pooling_artifact_names(key):
    """⛔ THE ATTESTATION CHECK ABOVE IS BLIND TO A DRIFT BETWEEN TWO REAL SYMBOLS.

    `TAF15::NR4A3` -> `TAF15::NR4A2` and `EWSR1::NR4A3` -> `NR4A3::EWSR1` leave two attested tokens
    on the page and invert or destroy the claim. This reads the permitted pairs out of the pooling
    artifact, so both are red, and so is a partner this synthesis does not pool.

    ⛔ THE SCOPE IS THE FRONT MATTER'S OWN `kind`, NOT A FILE LIST (`paper-hardening` §8b.2). A
    register's job is to hold what the literature reports and what this repository has superseded,
    verbatim — measured 2026-08-29, `partner-event-counts-2026-08-08.md` quotes PMID 41755350's
    novel `FUS::NR4A2` and `ACTB::NR4A3` from the source itself, neither of which the pooling
    artifact names. Applying this predicate there would go RED ON TRUE INPUT, which is worse than
    not guarding it at all (`paper-hardening` §8b.1). A manuscript added to this lane tomorrow is in
    scope the moment its front matter says `kind: manuscript`.
    """
    text = _text(key)
    permitted = _artifact_fusion_pairs()
    assert permitted, (
        f"{os.path.basename(POOLING)} names no fusion pair at all, so this check would pass while "
        "reading nothing. The artifact has moved or its shape changed — fix that, do not relax "
        "this assertion.")
    used = set(_FUSION_PAIR.findall(text))
    assert used, (
        f"{key} prints no `5'::3'` fusion pair, so this check is reading an empty set and passing "
        "vacuously. Either the document lost the nomenclature its result is stated in, or "
        "_FUSION_PAIR no longer matches the way this lane writes a fusion.")
    wrong = sorted(f"{a}::{b}" for a, b in used - permitted)
    assert not wrong, (
        f"{key} prints fusion pair(s) that {os.path.basename(POOLING)} does not name: "
        f"{', '.join(wrong)}\n\n"
        "Both halves and their ORDER are checked, because a pair written backwards names a "
        "different rearrangement and every character on the page is still a real gene. If this "
        "synthesis has genuinely started pooling another partner, the artifact is where that is "
        "recorded — regenerate it; do not add the pair here.")


@pytest.mark.committed_artifact
def test_the_attestation_set_is_not_empty_so_this_guard_is_not_vacuous():
    """⛔⛔ THE LOUD FAILURE IS A MISSING CORPUS — `attested` empties and everything is flagged.

    The QUIET one is the opposite and is the one worth asserting: `_IDENTIFIER` stops matching,
    `found` goes empty, and the check above passes while reading nothing.
    """
    attested = _attested()
    for gene in ("NR4A3", "EWSR1", "TAF15", "TCF12"):
        assert gene in attested, (
            f"{gene} is in no committed artifact, so this guard cannot attest it. An artifact root "
            "in ARTIFACT_ROOTS has moved, or the corpus is not being read.")
    # ⛔ AND THE SET MUST STILL DISCRIMINATE. A corpus this wide is only worth having if a one-digit
    # slip in the central symbols still falls outside it. If one of these ever becomes attested — a
    # screen dump listing every paralogue, say — this guard has gone quietly vacuous and the
    # attestation source needs narrowing, not this assertion relaxing.
    for slip in ("NR4A7", "NR4A9", "EWSR7", "TAF19", "TAF16", "TCF13"):
        assert slip not in attested, (
            f"{slip} is attested by some committed artifact, so a one-character corruption of a "
            "central gene symbol would now PASS the check above. The corpus has become too wide to "
            "discriminate; narrow ARTIFACT_ROOTS rather than deleting this assertion.")
    found = {t for t in _IDENTIFIER.findall(_text("emc-fusion-partner-stratification"))
             if t not in _NOT_AN_IDENTIFIER}
    for gene in ("NR4A3", "EWSR1", "TAF15"):
        assert gene in found, (
            f"_IDENTIFIER no longer matches {gene} in the synthesis, so the check above is reading "
            "an empty set and passing vacuously.")
    # ⛔ AND THE PAIR CHECK'S OWN DISCRIMINATION, for the same reason: a permitted set that had
    # grown to hold a backwards pair would make that check vacuous too.
    permitted = _artifact_fusion_pairs()
    assert ("EWSR1", "NR4A3") in permitted and ("TAF15", "NR4A3") in permitted, (
        "the pooling artifact no longer names both partners of this synthesis's comparison, so "
        "the fusion-pair check cannot bind the claim the paper is about.")
    for bad in (("NR4A3", "EWSR1"), ("TAF15", "NR4A2"), ("EWSR1", "NR4A7")):
        assert bad not in permitted, (
            f"{bad[0]}::{bad[1]} is named by the pooling artifact, so the pair check above would "
            "accept a corrupted or backwards fusion. The artifact has been widened; narrow it "
            "rather than relaxing this assertion.")
    # ⛔ AND THE PAIR CHECK'S SCOPE MUST NOT HAVE EMPTIED. A predicate that selects nothing
    # parametrizes to zero cases, and a test that generated no cases reports exactly what a test
    # that passed reports — the failure `test_no_guard_can_silently_not_run.py` exists for, reached
    # through parametrization instead of through a skip.
    scoped = _pair_checked_documents()
    assert "emc-fusion-partner-stratification" in scoped, (
        "the synthesis's own manuscript is not in the fusion-pair check's scope, so that check is "
        "running against nothing that states the paper's result. Its front matter `kind:` has "
        "changed, or _front_matter_kind has stopped reading it.")
    assert "emc-fusion-partner-correction-register" not in scoped, (
        "the correction register is inside the fusion-pair check's scope, where the predicate reds "
        "on true input — a register holds superseded and literature-reported pairs verbatim. The "
        "`kind:` predicate has stopped excluding it.")


@pytest.mark.committed_artifact
def test_the_document_set_is_every_prose_document_of_this_synthesis():
    """⛔ THE LITERAL SET ABOVE IS ONLY SAFE BECAUSE THIS FAILS WHEN IT FALLS BEHIND.

    `paper-hardening` §8b.2 measured it over 33 mutations: every fix scoped by a PREDICATE held, and
    six of eleven scoped by a LIST regressed at a sibling the fix did not name — in three of those,
    the missed sibling was named in the fix's own comment. A list whose completeness is ASSERTED is
    not a list somebody has to remember to extend, and the directory is the record.
    """
    on_disk = {n[:-3] for n in os.listdir(FUSION_PARTNER) if n.endswith(".md")}
    missing = sorted(on_disk - set(DOCUMENTS))
    assert not missing, (
        f"this lane holds {len(missing)} prose document(s) this guard does not read: {missing}\n\n"
        "Add them to DOCUMENTS. A gene symbol off by one digit reads as a real gene, and it does so "
        "just as readily in a document nobody pointed the check at.")
    stale = sorted(set(DOCUMENTS) - on_disk)
    assert not stale, (
        f"DOCUMENTS names {stale}, which is no longer in this lane. Either the file moved — follow "
        "it — or it was retired and should leave this list.")


def test_the_identifier_shape_is_the_one_the_sibling_guard_uses():
    """⛔ ONE FACT, ONE PLACE (CLAUDE.md §1) — WITH THE COPY ENFORCED RATHER THAN TRUSTED.

    The shape of a gene-shaped identifier is one fact and this repository now states it in two
    guards. It is written out in both because `claim_coverage` harvests regexes by statically
    reading test sources and cannot see an imported or assembled one (`paper-hardening` §8b.1e),
    and the ASO guard's own comments record two corrections to this pattern — a single leading
    letter that made it red on true input, and the `PMC`/`PMID` exclusions. A divergence between
    the two copies would silently give this synthesis a different, unreviewed definition.
    """
    spec = importlib.util.spec_from_file_location("_aso_identifier_guard", SIBLING)
    assert spec and spec.loader, f"cannot load {os.path.basename(SIBLING)} to compare patterns"
    sibling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sibling)
    assert sibling._IDENTIFIER.pattern == _IDENTIFIER.pattern, (
        "the identifier shape has diverged between the two gene-symbol guards:\n"
        f"  {os.path.basename(SIBLING)}: {sibling._IDENTIFIER.pattern}\n"
        f"  {os.path.basename(__file__)}: {_IDENTIFIER.pattern}\n\n"
        "One of them was corrected and the other was not. Decide which shape is right, put it in "
        "both, and say in the comment why — do not delete this assertion, which is the only thing "
        "that makes the duplication safe.")
    assert sibling._NOT_AN_IDENTIFIER == _NOT_AN_IDENTIFIER, (
        "the markdown/typesetting exclusion set has diverged between the two gene-symbol guards. "
        "A token excluded in one and checked in the other means one of the two papers is reading a "
        "definition nobody reviewed.")
