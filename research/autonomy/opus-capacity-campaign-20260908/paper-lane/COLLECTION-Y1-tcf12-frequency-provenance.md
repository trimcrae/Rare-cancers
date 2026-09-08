# Y1 - the frequency IS supported, but not for the population the sentence names

⛔ **Nothing applied.** The finding affects **both** the committed ATR manuscript **and** X1's
candidate; the fix is a **proposal for the coordinator**, whose decision on that candidate is pending.

| item | measured |
|---|---|
| child | `a47ee9339d1263157` |
| model strings | **`claude-opus-5` only** |
| tool pairs | **26** (self-reported 17) |
| shared writes | **none**; status empty at start and end |

## Verdict: SUPPORTED, with a denominator qualification that matters

**No committed input says "3 to 4 per cent" verbatim.** What exists is better: a **pooled computed
value inside that range**, plus the two per-series percentages that **bracket it exactly**.

**Parent-verified quotations:**

- `emc-fusion-partner-pooling.json` - `TCF12::NR4A3`: **5 events / denom 154 / 3.2 %**, Wilson 95 % CI
  **1.4-7.4**, pooled over **four independent series** (Agaram, Huang, Lenz, Paioli).
- `emc-fusion-partner-stratification.md:433` - `| TCF12::NR4A3 | 5/154 | 3.2 % | 1.4-7.4 |`, and I read
  the header myself at line 429: **"share of partner-assigned EMC"**.
- The bracketing endpoints in one committed sentence: **TCF12 4 %** (n = 26, Agaram 2014) and
  **TCF12 3 %** (n = 58, Huang 2023) - the likeliest textual ancestor of "3 to 4 per cent".
- **Agaram is already reference 6** of this manuscript - I confirmed it at line 530.

## ⭐ The mismatch, which is the real finding

**Every committed denominator is *partner-assigned* or *molecularly confirmed* EMC. The manuscript
says "of EMC".** I verified line 382 reads *"Roughly 3 to 4 per cent of EMC carries TCF12::NR4A3"* -
unqualified, and uncited.

That is a **population** error, not an arithmetic one: a share of *partner-assigned* cases is not a
share of *EMC*, because cases without an assigned partner are excluded from the denominator. The
sentence is load-bearing - the next line turns it into a class prediction.

## Y1's discipline worth recording

It reported the **non-matching** committed figures too, rather than only the confirming ones: a "1
(2 %) NR4A3-TCF12" of 62, and **Sjögren 2003's TCF12 at 1 of 10 (10 %)** - the series X1 had seen -
noting that Sjögren is **excluded from the pool on a stated policy ground**, which is *why* it does not
defeat 3.2 %. It also checked git history and found the phrase first appears in a squash-merge, so
**the introducing edit is unrecoverable** - stated, not guessed.

## Proposed fix - NOT applied, and with its own cautions

Y1 proposes: *"TCF12::NR4A3 is carried by 3.2 per cent of **partner-assigned** EMC (5 of 154 pooled
across four independent molecular series, 95 % CI 1.4 to 7.4)"*, citing the pooling artifact in §7.

⚠ **Its own cautions, which I endorse:** the Huang record is **abstract-level, UNRECOVERED with no PMC
full text**, and carries a **flagged Huang/Warmke attribution history**, so its DOI must be re-checked
against the committed record before any new reference is typed. **A lighter alternative needs no new
reference at all**: cite reference 6 alone - *"about 4 per cent in one series of 26 (1 case) [6]"*.

⛔ Y1 made **no epidemiological claim of its own**, invented no source, and did not verify the Huang
DOI or resolve the attribution question - correctly, as all three were outside its contract.

## Consequence

This is a **live precision defect in a committed manuscript**, and the same sentence is inherited by
X1's candidate. **Both should be fixed together** under the coordinator's ATR decision rather than
patched separately now.
