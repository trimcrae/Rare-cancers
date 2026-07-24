# Draft: ACCESS free-compute allocation request (GPU hours for the NR4A3 degrader in-silico program)

**What this is.** A ready-to-adapt draft application for **free national-supercomputer GPU time** via
**ACCESS** (the NSF *Advanced Cyberinfrastructure Coordination Ecosystem: Services & Support*, the successor to
XSEDE). ACCESS grants GPU allocations on machines like **Anvil** (Purdue), **Expanse** (SDSC), and **Delta /
DeltaAI** (NCSA) — A100/A40/H100-class GPUs ideal for OpenMM MD. Submit at **allocations.access-ci.org**.

**Recommended tier: "Explore ACCESS"** (~400,000 ACCESS credits). It's the lightweight tier — a short
project description, **no external peer review, rolling/continuous submission, fast turnaround** — meant
exactly for exploratory and modest computational projects like ours. If we outgrow it, "Discover ACCESS"
(~1.5M credits) is the next step with a slightly longer form.

---

## ⚠️ Eligibility — read first (honest caveat)

ACCESS PIs are generally expected to be **researchers or educators at a US-based academic or non-profit
institution** (postdocs and, with a sponsor, students; some non-profits and small businesses qualify). An
**unaffiliated independent researcher may not be directly eligible as PI.** Options, in order of least effort:
1. **Apply under an existing affiliation** if you have any (adjunct, visiting, alumni-research, a collaborating
   lab willing to be PI-of-record with you as co-PI).
2. **Find an academic collaborator** to serve as PI (common for independent researchers).
3. If neither is available, pursue **alternatives that are friendlier to independents**: the **National
   Research Platform / Nautilus** (Kubernetes GPU cluster, lighter eligibility), **NVIDIA Academic Hardware
   Grants**, or cloud research-credit programs — and otherwise fall back to the cheap-marketplace route
   (RunPod/Vast) the provider-agnostic harness already supports.

Do not submit implying an affiliation you don't hold. The scientific sections below are reusable for **any** of
these programs; only the PI/institution block changes.

---

## Application fields (fill the bracketed items; the prose is drafted)

**Project title:** Physics-based in-silico design of a paralogue-selective NR4A3 degrader for
extraskeletal myxoid chondrosarcoma

**Fields of Science:** Biophysics / Computational Chemistry / Molecular Biology (primary: *Molecular
Biophysics*; secondary: *Computer & Computational Sciences*).

**PI:** [FULL NAME — Tristan McRae] · **Email:** trimcrae@gmail.com · **Institution/affiliation:**
[TO FILL — see eligibility above] · **Role:** [Independent researcher / affiliation title]

**Requested resources (pick 1–2 GPU systems):**
- **NCSA Delta GPU** (A100/A40) — strong OpenMM support, user-installable conda envs; OR
- **Purdue Anvil GPU** (A100); OR
- **SDSC Expanse GPU** (V100/A100).
Request the **GPU** queues (single-GPU jobs; see justification). Modest CPU + a few hundred GB scratch for
trajectories/checkpoints also requested.

**Software:** OpenMM (MD engine), OpenFE (relative binding free energy / RBFE + alchemical protocols),
AmberTools (parameterization), RDKit, fpocket/smina (CPU triage). All open-source and installable in a user
**conda/mamba** environment — no admin support or special licenses required.

---

## Project overview / abstract (drafted — reuse verbatim)

Extraskeletal myxoid chondrosarcoma (EMC) is a rare soft-tissue sarcoma driven by an **EWSR1::NR4A3** gene
fusion with no approved targeted therapy. This project develops, entirely in silico, a **paralogue-selective
NR4A3 degrader** (a PROTAC-type molecule) and — as a prerequisite — a **rigorous, honestly-benchmarked
computational workflow** for predicting degrader selectivity. NR4A3's two paralogues, NR4A1 and NR4A2, are
anti-targets whose ligand-binding domains are highly homologous, so selectivity is the central scientific
challenge; our hypothesis is that it emerges not from the small-molecule warhead alone but from the combined
**warhead × linker × E3-ligase × ternary-complex geometry**.

The compute is dominated by **molecular dynamics free-energy calculations**: relative binding free energy
(RBFE) across a focused congeneric warhead series in NR4A3 and in matched NR4A1/NR4A2 conformers, followed by
**ternary-complex cooperativity** calculations for candidate degraders. As a hard control, the workflow must
first **retrospectively reproduce a known result** — the family-selective NR-V04 degrader (degrades NR4A1, not
NR4A2/NR4A3) — before any prospective prediction is trusted. All methods are standard, open-source
(OpenMM/OpenFE), single-GPU, and checkpointed for resumability. Outputs are a preprint-quality computational
characterization and a small set of computationally prioritized, structure-defined, retrosynthetically annotated candidate degraders for
external wet-lab validation. No wet-lab resources are required for this allocation.

---

## Computational justification (drafted — the reviewers want GPU-hours + why GPU)

**Why GPU, and why single-GPU.** The workload is OpenMM molecular dynamics for alchemical free-energy
calculations. Each alchemical window / replica is an **independent single-GPU** simulation — the method is
embarrassingly parallel across windows and requires **no multi-GPU interconnect**, so jobs run efficiently on
one GPU each and fan out across many. CPU-only execution is ~10–50× slower and not economical; the science is
genuinely GPU-bound.

**Estimated GPU-hours.** Staged, multi-fidelity design (cheap triage → full sampling only for survivors):
- *Binary RBFE, congeneric series (~18–20 warhead analogs), NR4A3 + matched NR4A1/NR4A2 conformers* — short
  triage sampling on most, full sampling on survivors: **~800–1,500 GPU-hours.**
- *Ternary-complex cooperativity* for the surviving candidate matrix (≥3 replicas × 3 paralogues, larger
  systems) plus the **NR-V04 retrospective control**: **~1,000–2,500 GPU-hours.**
- *Method validation / stress + replicates:* **~300–600 GPU-hours.**
- **Total request: ≈ 2,500–4,500 GPU-hours** (well within an Explore allocation's envelope; we will right-size
  per the resource's credit-conversion rate and can request Discover if the ternary phase expands).

**Efficiency + good-citizenship.** Jobs **checkpoint per unit** (per window/replica) with continuous upload,
so preemption or walltime limits lose ≤ one unit and jobs resume cleanly — friendly to shared-queue policies.
We run short-sampling triage first and reserve full field-standard sampling (5 ns/window × ≥3 replicas) only
for candidates that pass earlier gates, minimizing wasted node time.

---

## Submission checklist
- [ ] Resolve eligibility / PI affiliation (see caveat).
- [ ] Register for an ACCESS ID at **operations.access-ci.org**; create the allocation request at
      **allocations.access-ci.org** → *Explore ACCESS*.
- [ ] Paste the abstract + computational justification above; fill PI/institution/resource fields.
- [ ] Attach a 1–2 page CV/biosketch for the PI (Explore is light; a short bio usually suffices).
- [ ] Submit (rolling review; typically approved in ~1–2 weeks for Explore).

*(This draft is a starting point, not a filed application. It fabricates no credentials or affiliation — those
are yours to supply. The scientific text is reusable for NRP/Nautilus, NVIDIA Academic, or cloud research
credits with minimal edits.)*
