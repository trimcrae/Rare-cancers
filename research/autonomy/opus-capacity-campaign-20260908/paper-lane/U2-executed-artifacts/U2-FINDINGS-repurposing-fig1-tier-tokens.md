# U2 — repurposing Figure 1: does it render tier tokens?  ANSWER: YES

Image identity (verified, unmodified):
  path   /home/user/Rare-cancers/research/manuscripts/figures/repurposing-fig1-design.png
  bytes  177415
  sha256 f711ea7f2c4fd3e4c3d26cfacc61519db5018fb40dcf87c208e1b45ac3ca2075
  IHDR   2786 x 1526, 8-bit, colortype 6 (RGBA), non-interlaced   [read from the file's own IHDR chunk]
  No tEXt chunk was printed by the decoder (no embedded text metadata encountered).

## 1. Every legible text label, VERBATIM (from the pixels)

Solid boxes, top-left to bottom-right:
  1. "Mechanism curation" / "(expert, literature)"
  2. "Target-to-drug enumeration" / "(DGIdb, reproducible)"
  3. "Scored candidate catalogue" / "14 existing drugs, tiers T0–T3"      [grey-filled centre box]
  4. "Manuscript and path" / "to testing"
  5. "Firewall"                                                            [bold, heavy-outlined box]
  6. "Cited clinical registry"

Edge labels:
  7. "T3 plus clinician" / "review only"     [on the edge Firewall -> Cited clinical registry]
  8. "diverged; reported as a limitation," / "no hit promoted"   [near the dashed lower row]

Dashed boxes (lower row):
  9. "Graph foundation model" / "(TxGNN, zero-shot)"
 10. "Not used as a source"

No other text is present. No title, no legend, no panel letter, no axis text.

Character-level notes (checked on 2x / 4x magnified crops of the raw pixels):
  - "tiers T0–T3" — the separator renders as an EN DASH (–), longer than a hyphen and set at
    x-height mid, not a hyphen-minus. Reported as observed glyph shape; the underlying codepoint
    cannot be proven from pixels alone.
  - "T3 plus clinician review only" — unambiguous, all glyphs legible.
  - Nothing is illegible in this figure at full resolution.

## 2. Are the tier tokens rendered? Is a T3-only admission rule rendered?

  T0 — YES, but ONLY as an endpoint of the range string "tiers T0–T3". It does not appear alone.
  T1 — NO. The token "T1" is not rendered anywhere.
  T2 — NO. The token "T2" is not rendered anywhere.
  T3 — YES, twice: as the range endpoint in "tiers T0–T3", and standalone in the edge label
       "T3 plus clinician review only".

  T3-only admission rule: YES, rendered — but NOT inside the Firewall box. The Firewall box
  contains the single bold word "Firewall" and nothing else. The admission rule lives on the
  ARROW LABEL leaving the Firewall toward "Cited clinical registry", reading
  "T3 plus clinician review only".

  So the figure does NOT read "admitting only tier T3" anywhere; the rendered wording is
  "T3 plus clinician review only", which is a stronger, two-condition rule (tier AND clinician
  review), not a tier-only rule. This is a wording difference from the manuscript caption near
  line 275 and is reported, not resolved — the caption was not opened or changed by U2.

## 3. Exactly which visual text depends on the tier decision

Two strings, and only these two:

  (a) "14 existing drugs, tiers T0–T3"        [line 2 of the grey centre box]
  (b) "T3 plus clinician" / "review only"     [edge label, Firewall -> Cited clinical registry]

Nothing else in the figure references a tier. The box "Firewall" is tier-independent as drawn.

## 4. Minimal candidate change under each of R2's options (proposal only; figure NOT modified)

Option A — keep four tiers, T3 defined but empty:
  Minimal change = NONE to string (a): "tiers T0–T3" stays correct, because T3 remains a defined
  tier of the scheme even with no member drugs. String (b) is the judgement call: as drawn it
  states the admission rule, not a population claim, so it also remains literally true (nothing
  is admitted, because nothing is T3). If the coordinator wants the emptiness visible in the
  figure rather than only in the text, the minimal edit is to append an emptiness marker to the
  edge label — e.g. make it read "T3 plus clinician review only (T3 currently empty)". That is
  one label, one added parenthetical; no box, arrow or layout change.

Option B — collapse to three tiers:
  Two label edits, no structural change:
    (a) "14 existing drugs, tiers T0–T3"  ->  the range endpoint changes to the new top tier,
        i.e. "14 existing drugs, tiers T0–T2". Only the two characters after the dash change;
        line length is unchanged so the box does not need to be resized.
    (b) "T3 plus clinician review only"   ->  the tier token changes to the new top tier,
        i.e. "T2 plus clinician review only". One character changes; the two-line wrap is
        unaffected.
  No arrow, box, dash-style or layout change is needed under either option.

  In BOTH options the count "14 existing drugs" is untouched — U2 did not verify that number
  against any registry and makes no claim about it.

## 5. Pixels vs generator

  ALL content claims above rest on the PIXELS: the full-resolution render of the PNG plus two
  magnified crops decoded from the file's own IDAT stream. The image dimensions, bit depth and
  colour type rest on the file's IHDR chunk (file structure, not generator source).
  U2 did NOT open the figure generator, the manuscript, or any prior lane's description of the
  figure, so no claim here rests on a generator.

## 6. What remains UNKNOWN

  - The exact Unicode codepoint of the dash in "T0–T3" (glyph observed as an en dash; codepoint
    is not recoverable from pixels).
  - Whether the manuscript caption near line 275 in fact says "only tier T3": not opened by U2.
    The MISMATCH flagged in section 2 is therefore between the pixels and the task brief's
    quotation of that caption, not a verified caption diff.
  - Whether any OTHER figure in the package renders tier tokens: not inspected; out of scope.
  - Whether T3 is in fact empty: no registry or data was opened. Unknown, not zero.
  - Which option is scientifically correct: coordinator's decision, not U2's.

## 7. What U2 did NOT do

  No modification or regeneration of the figure. No edit to the manuscript, caption, tier scheme,
  registry, reference list, generator or any gate. No git write, no commit, no branch, no push.
  No scripts/preflight.sh. No network. No science rerun, no data change. No whole-paper review,
  no census. Nothing written outside /tmp/claude-0/u2-lane/. Nothing deleted.

## 8. Retained artefacts (all in /tmp/claude-0/u2-lane/)

  crop.py                        the pure-python PNG decoder/cropper used (read-only on the PNG)
  crop-catalogue.png             2x magnification of the grey box text ("tiers T0–T3")
  crop-firewall-edge.png         4x magnification of the edge label ("T3 plus clinician review only")
  U2-FINDINGS-repurposing-fig1-tier-tokens.md   this file
