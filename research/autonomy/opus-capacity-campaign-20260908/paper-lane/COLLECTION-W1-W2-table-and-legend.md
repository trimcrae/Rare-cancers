# W1 and W2 — collection: a proposed Table S3, and what Panel A's marks actually encode

⛔ **Nothing applied.** Both outputs are reviewable candidates in their lanes; the manuscript, figure,
generator and artifacts are unchanged.

| lane | child | model | pairs (self-reported) | shared writes |
|---|---|---|---|---|
| W1 | `afb6b8e0c83a21fac` | **`claude-opus-5` only** | **17** (12) | none |
| W2 | `a89e97a25d998f23d` | **`claude-opus-5` only** | **16** (12) | none |

## W1 — the table, and a check that could actually fail

24 fields x 4 junctions, plus a gap block and the input's five `_limits` verbatim. **Every cell is a
copied leaf, a fixed label, or UNRESOLVED** — the script computes nothing; the only transformation is
markdown pipe-escaping, with raw values kept in the provenance JSON.

⭐ **The best thing W1 did was prove its check is not vacuous.** It ran a faithfulness checker that
re-parses the committed JSON independently of its builder — **PASS, 92 sourced + 4 UNRESOLVED = 96
cells** — and then a **negative control**: it altered one cell (6270 -> 6271) and the same checker
**FAILED** with the exact mismatch, then restored and re-passed. Both outputs are retained.

**Parent verification.** Input digest `726aae02…c2048b` confirmed. I read the four cDNA lengths
straight from the JSON — **6270, 5943, 6393, 5477** — all matching, all `in_frame` true, type 2's
**59** extra junction residues confirmed, `registered_predictions` **4 entries**. **I re-ran W1's
checker myself: PASS, exit 0.**

**UNRESOLVED, correctly:** genomic breakpoint coordinates for all four rows — the input holds
transcript/cDNA coordinates only, and W1 **did not derive them from exon ranks**; and every assembly
field for FUS::NR4A3 and TCF12::NR4A3, whose recorded status strings are copied **verbatim** rather
than an inferred junction. That is the contract's "mark it unresolved rather than invent it", honoured
where it would have been easy to interpolate.

## W2 — ⭐ the marks are sourced, and one structural hazard falls out

**Ticks: established.** One tick = **one RG dipeptide at its arginine's 1-based position**, drawn from
`composition.rg_content.<protein>.rg_positions` (generator lines 120-121, 140-141, 168-170), filtered
to `t <= cut` in fusion rows. I confirmed the field and the drawing lines.

**Dashed boxes: sourced, but not read from data.** They are **hard-coded literals** at generator lines
130-131 — `[(300, 332), (455, 638)]` for EWSR1, `[(326, 572)]` for TAF15. **I verified the generator
contains zero references to `rgg_boxes_operational`**, while `emc-fet-construct-designs.json` carries
exactly those numbers at lines 1461-1488, and `[]` for NR4A3 (which the generator duly leaves boxless).

⚠ **The hazard W2 names, and it is real:** because the coordinates are literals and the provenance
stamp hashes only the three source files, **a change to `rgg_boxes_operational` would not mark the
figure stale.** Recorded as a finding; **nothing was changed.**

⭐ **A caption must not call them "RGG domains."** The repository's own note at designs.json:1518 says
the operational finder **merges EWSR1's 3 named domains into 2 boxes** and was deliberately not tuned.
They are **operationally defined RGG boxes**, and W2's proposed wording says exactly that.

**Where code and pixels disagree — left unresolved, correctly.** Line 141 draws an NR4A3 tick at
**371** as well as 508; I confirmed `rg_positions = [371, 508]`. **U1 reported only one.** 371 sits 2
residues from a block boundary at 373 whose heavier edge may overdraw it. **W2 did not re-open the
image** and marked occlusion-versus-omission **undecidable from code** — the right call, and it is why
"code shows intent, pixels show appearance" was written into the contract.

W2 also notes Panel A carries **four unkeyed vertical-line weights** (RG tick 0.55, box 1.3, breakpoint
end-cap 1.1, `C166` 1.6) and **no legend-drawing call anywhere** in the generator.

## Bounds held by both

No image opened by W2, no figure regenerated, no manuscript/registry/artifact/gate edit, no shared
write, no git write, no network, no preflight, nothing deleted, nothing applied.
