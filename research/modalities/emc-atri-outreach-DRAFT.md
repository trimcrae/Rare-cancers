# ATR-inhibitor / EMC — collaborator outreach **DRAFT, HELD, NOT SENT**

> ⛔ **NOTHING HERE HAS BEEN SENT, AND NOTHING HERE MAY BE SENT WITHOUT trimcrae.** Contacting a lab is
> outward-facing and irreversible, so CLAUDE.md §3 gates it. This file exists because *drafting* is
> free and self-doable and because the ask should be ready the moment the answer is yes — it is not a
> request to send, and no address has been looked up.
>
> **The ask rests on:** the preregistration [`emc-atri-prereg.md`](./emc-atri-prereg.md) (criteria fixed
> in advance, including the PARP negative-translation control), the structural census
> [`emc-fet-idr-census.json`](./emc-fet-idr-census.json), and the route write-up
> [`emc-post-degrader-options.md`](../manuscripts/emc-post-degrader-options.md) route 1.
>
> **Etiquette, inherited unchanged from [`nr4a3-degrader-outreach-emails.md`](../manuscripts/nr4a3-degrader-outreach-emails.md):**
> short (~150 words), one low-friction ask, honest that it is a prediction, generous terms, and
> **never overclaim** — "a preregistered hypothesis", never "we found a treatment".

---

## Who, and why them specifically

| group | why them | which template |
|---|---|---|
| **The USZ (Zurich) group** — established USZ20-EMC1 and USZ22-EMC2 and *already runs ex-vivo drug-sensitivity and synergy screens on them* ([Bangerter et al., *Human Cell* 2023;36:446–455](https://link.springer.com/article/10.1007/s13577-022-00818-x)) | the single best fit in the world: they hold two of the ~4 EMC models and the assay is one they already do | **1** |
| **The NCC (Japan) group** — established NCC-EMC1-C1, explicitly *"for screening experiments"* ([Iwata et al., *Human Cell* 2025](https://link.springer.com/article/10.1007/s13577-025-01250-7)) | a second, independent model — and the design needs ≥ 2 | **1** |
| **The FET/ATR authors** (PMID 37205599) | they built the assay, hold the comparator lines, and EMC is the untested fourth TF-partner class in their own class argument | **2** |
| **Sarcoma translational labs / EMC-focused foundations** | model access and onward introductions | **1**, lightly edited |

⚠ **Verify every name, affiliation and address at send time.** None has been looked up, and a stale or
guessed address is worse than no email.

---

## Template 1 — a group that holds an EMC model

**Subject:** A preregistered prediction for EMC: ATR-inhibitor sensitivity from its FET rearrangement

Dear Prof. [LAST NAME],

[ONE PERSONAL LINE — e.g. "you established and drug-profiled USZ20-EMC1 and USZ22-EMC2, which is why
I'm writing to you rather than anyone else."]

FET fusion oncoproteins impair ATM activation at double-strand breaks, leaving the ATR axis
load-bearing; ATR inhibitors are synthetic lethal in Ewing sarcoma, clear cell sarcoma and DSRCT
(PMID 37205599). EMC is FET-rearranged in ~89–95 % of cases, and its commonest fusion retains an
EWSR1 segment **byte-identical** to the Ewing fusion that work was done on — but **no NR4A3 fusion has
ever been tested.**

The ask is one plate: a 7-point ATR-inhibitor dose–response in your EMC model versus a non-FET
sarcoma line, with γH2AX, a PARP-inhibitor arm and a proliferation index. The criteria are
preregistered and public — including what counts as a null, which I would publish either way.

This is a computational prediction, not a validated treatment, and I have no wet lab. Happy on any
terms you prefer: collaboration, hand-off, or simply telling me it has already been tried.

[NAME] · [CONTACT] · prereg + analysis: [REPO_URL]

---

## Template 2 — the group that established the FET/ATR mechanism

**Subject:** EMC (EWSR1::NR4A3) — the untested fourth partner class for your ATR result

Dear Prof. [LAST NAME],

Your FET-fusion/ATR work spans an ETS partner, a bZIP partner and a zinc-finger partner. Extraskeletal
myxoid chondrosarcoma is the fourth case and it is untested: a **nuclear-receptor** partner, with
FET-family 5′ partners in ~89–95 % of cases.

Two things may be useful to you rather than only to me. First, EMC's canonical fusion retains
EWSR1(1–264) — byte-identical to the Ewing type-1 retained segment, keeping none of EWSR1's 30 RG
dipeptides — so it meets your structural precondition at least as well as the clear-cell fusion.
Second, re-cutting GDSC2 by FET status rather than Ewing-vs-rest, and correcting for each line's
general chemosensitivity, the ATR-inhibitor effect survives (AZD6738 Δ −0.49) but PARP inhibitors are
2–4× larger in the same lines — which, given the Ewing PARP-inhibitor clinical result, seems worth a
control arm in anything downstream.

Preregistration and all analysis code are public: [REPO_URL]. No ask beyond your view on whether EMC
is worth adding.

[NAME] · [CONTACT]

---

## What must be true before any of this is sent

1. **trimcrae approves** — the §3 reviewer block, not a mention in passing.
2. **The repo link resolves** to the prereg and the census on `main`, not a feature branch.
3. **Addresses verified** at send time.
4. **The claims in the emails match the artifacts** — every figure above has one home and is read
   from it, not typed. If a number moves, this file is wrong until it is regenerated.
