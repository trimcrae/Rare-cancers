# B1/B2 — public reference transcriptome availability checkpoint

**Outcome: DENIED — organization egress policy 403 at CONNECT for `ftp.ensembl.org:443`.
No reference bytes were acquired. No usable immutable copy exists in the retained index to reuse.**

**The dependent B1/B2 scientific analyses remain gated for root. Nothing downstream was started,
and nothing in this report licenses starting them.**

Date of measurement: 2026-09-08 (UTC). Sole source owner for this checkpoint; no repository file
outside this report was created or modified, no commit, no push, no test suite, no preflight.

---

## 1 · Reuse and history, checked first

### 1a · What the retained index actually holds

The two Ensembl human reference resources this checkpoint concerns **have already been read once by
this repository**, on **2026-09-02T17:42:52Z**, by `research/modalities/emc_fourth_cohort_quant.py`
(`--phase map`). What survives is **derived output and a mutable locator — not the reference.**

Retained, verbatim, in `research/modalities/emc-fourth-cohort-quant.json` and
`research/modalities/emc-fourth-cohort-quant-inputs.json` (identical `probe_map.sources` blocks):

| kind | url | state | n_transcripts | n_bases_scanned |
|---|---|---|---|---|
| cdna | `https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/cdna/Homo_sapiens.GRCh38.cdna.all.fa.gz` | read | 465,769 | 1,276,790,359 |
| ncrna | `https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/ncrna/Homo_sapiens.GRCh38.ncrna.fa.gz` | read | 203,778 | 201,604,096 |

Also retained and reusable: the derived `probe_map.probe_to_gene` dictionary (1,645 probes offered;
906 assigned to exactly one gene; 77 multi-gene; 662 unassigned), `best_core_length_nt` 34, and the
count tables `emc-fourth-cohort-probe-counts.tsv` (18,810,774 bytes, sha256
`c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc`, 213,007 rows) and
`emc-fourth-cohort-gene-counts.tsv` (47,894 bytes, sha256
`8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc`, 862 rows).

### 1b · Why that is NOT a reusable immutable source — the load-bearing finding

⛔ **The retained locator is `current_fasta`, a mutable alias, not an immutable release path.**
`/pub/current_fasta/` is a moving pointer that Ensembl repoints at every release. It is a *locator*
that no longer resolves to the bytes that were actually read.

Not retained anywhere, for either file: **release number, checksum of any kind, file size in bytes,
`CHECKSUMS`/`README` from the release directory, `_fetched_utc` for the FASTA fetch specifically,
or the FASTA bytes themselves.** Filesystem search across the whole session
(`find / -xdev -name "*cdna.all.fa*" -o -name "*ncrna.fa*"`, and `-size +20M -name "*.fa*"` under
`/home/user`, `/tmp`, `/root`) returned **nothing**. There is no cached copy to reuse.

The only quantities that fingerprint the release are the two transcript counts and the two base
counts in the table above. **Resolving those to a release number requires the blocked host**, so the
assembly is recorded (`GRCh38`, from the filename) and the **release is UNKNOWN**, not assumed.

This gap is a known, independently recorded defect in this repository, not a new observation:
`research/autonomy/review-seats/PUB-ASO-3d5c709b69bc32a00a7776bf47303771d17d87f5-seat-citations-and-archive.json`
records "*No database release or genome build version is printed … the Ensembl release appears once
in the whole deposit*".

### 1c · Previous source-route outcomes — routes NOT repeated

| Route | Prior outcome | Where recorded |
|---|---|---|
| `rest.ensembl.org:443` | **403 CONNECT, policy denial** | `reports/W20-computational-hypothesis.md`, proxy status quote |
| `ftp.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `ftp.ebi.ac.uk`, `depmap.org`, `cbioportal.org`, `api.gdc.cancer.gov`, `www.proteinatlas.org`, `rest.uniprot.org` | all `000` (tunnel refused) | ibid., 8-host egress probe |
| GSE243553 supplementary `MOESM3_ESM.zip` | 403-denied | ibid. |
| `ftp.ensembl.org:443` | **not previously probed** | — |

⛔ I did not re-probe any host on that denied list. The **one** untried official host for the exact
resources named in this checkpoint was `ftp.ensembl.org`, so that is the single probe I made.

---

## 2 · Facts the proposal did not verify

### 2a · "One GET" — **FALSE**

**cDNA and ncRNA are two separate resources**, in two separate release subdirectories, with two
separate filenames, recorded as two separate `probe_map.sources` entries with different transcript
and base counts. Acquiring the human reference transcriptome as Ensembl publishes it is a
**minimum of two GETs** (plus, for an immutable identity, the release directory `CHECKSUMS` and
`README` — four requests, not one).

### 2b · "44.3 MB" — **NOT VERIFIED, and inconsistent with retained evidence**

The true on-disk sizes are **unmeasurable from this session** because the host is denied — ⚠ I did
not obtain a `Content-Length` and do not report one. What can be said from retained evidence:

Derived lower bound from `n_bases_scanned` (DERIVED, not measured; wrapped-FASTA overhead and a
3.5–4.2× gzip ratio for nucleotide FASTA assumed, both stated so they can be checked):

| file | sequence bases (retained) | uncompressed FASTA, est. | `.gz`, est. |
|---|---|---|---|
| `Homo_sapiens.GRCh38.cdna.all.fa.gz` | 1,276,790,359 | ~1.38 GB | ~310–390 MB |
| `Homo_sapiens.GRCh38.ncrna.fa.gz` | 201,604,096 | ~0.24 GB | ~55–70 MB |
| **both** | 1,478,394,455 | **~1.6 GB** | **~370–460 MB** |

**44.3 MB is roughly an order of magnitude below the compressed pair and roughly 35× below the
uncompressed pair.** It cannot be the whole reference. I looked for what it might instead be: no
file anywhere in the tree is between 40 and 50 MB, and the repository's probe table is 18.8 MB, so
the number is **not attributable to any retained artifact** either. Treat it as unverified.

### 2c · Assembly and release

- **Assembly: GRCh38** — read from the retained filenames, which is weak but consistent evidence.
- **Release: UNKNOWN.** Not recorded, not derivable offline, and the resolving host is denied.
- **Canonical immutable form** (the shape an acquisition would have to take, stated as a locator
  only — ⚠ **this is a URL pattern, not a delivered file**):
  `https://ftp.ensembl.org/pub/release-<N>/fasta/homo_sapiens/{cdna,ncrna}/…` with the
  release-directory `CHECKSUMS`. `<N>` is exactly what could not be established.

### 2d · Cloud disk headroom in this session — measured

```
df -h /            → /dev/vda  252G  23G used  15G avail  60%
df -B1 --output=avail /  → 15966027776
```

**14.87 GiB writable, at 2026-09-08.** This is the fixed per-session allowance and it is the same
filesystem for `/`, `/tmp` and the repository. Headroom is **not** the constraint: the estimated
~460 MB compressed pair, or even the ~1.6 GB uncompressed pair, fits comfortably. ⛔ Disk was never
the blocker, and this checkpoint is **not** BLOCKED-ON-RESOURCE.

---

## 3 · Acquisition attempt and its exact condition

One probe, both files, `HEAD` with redirects followed:

```
curl -sS -I --max-time 40 -L https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/cdna/Homo_sapiens.GRCh38.cdna.all.fa.gz
curl -sS -I --max-time 40 -L https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/ncrna/Homo_sapiens.GRCh38.ncrna.fa.gz
```

Both returned, verbatim:

```
curl: (56) CONNECT tunnel failed, response 403
HTTP/1.1 403 Forbidden
```

Confirmed at the proxy (`curl -sS "$HTTPS_PROXY/__agentproxy/status"`), verbatim entries:

```
{'ts': '2026-09-08T19:22:04.870Z', 'kind': 'connect_rejected',
 'detail': 'gateway answered 403 to CONNECT (policy denial or upstream failure)',
 'host': 'ftp.ensembl.org:443'}
{'ts': '2026-09-08T19:22:05.208Z', 'kind': 'connect_rejected',
 'detail': 'gateway answered 403 to CONNECT (policy denial or upstream failure)',
 'host': 'ftp.ensembl.org:443'}
```

**Exact condition: `ftp.ensembl.org:443` is not permitted by this session's organization egress
policy. The gateway answers 403 to CONNECT.**

Per `/root/.ccr/README.md` ("*Do not retry or route around it — report the blocked host*") I did not
retry, did not try a mirror, did not try a paid or third-party redistribution, did not weaken TLS,
and did not unset `HTTPS_PROXY`. **Zero bytes of reference sequence were acquired, so there is no
sibling bytes directory and no checksum file to report — a checksum of nothing would be a fiction.**

---

## 4 · Compatibility assessment against the current mapper and transcript-identifier conventions

This is the deliverable. It is answerable offline, and the answer is **mixed: the mapper would
tolerate a new release; the repository's identifier records would not survive it silently.**

### 4a · What the current mapper actually does

`emc_fourth_cohort_quant.py --phase map` assigns a 50-nt TempO-Seq probe to a gene by **verbatim
substring matching of the probe core against the concatenated cDNA + ncRNA sequence set**, at core
lengths tried in order 50 → 42 → 34 nt (`best_core_length_nt` 34). Recorded outcome at the read:
976 probes matched at 50 nt (59.33%), 983 at 34 nt (59.76%); 906 resolved to exactly one gene.

Three consequences for compatibility:

1. **The mapper consumes gene SYMBOLS only.** It stores `probe_sequence → assigned_gene`
   (e.g. `"…CTCCTCGATC": "TAF15"`). No transcript ID, no version, no coordinate is carried into the
   product. It is therefore **immune to ENST version drift** and to transcript-ID churn.
2. **It is NOT immune to changes in the transcript SET.** A release that adds, removes or re-splices
   a transcript changes which 34-mers exist in the searched corpus, which moves probes between
   `assigned`, `multi-gene` and `unassigned`. The artifact's own caveat says the same thing:
   *"unassigned … is a statement about this matcher, NOT about the probe."* ⚠ **A different release
   will produce a different 906/77/662 split, and the current gene-count table would silently stop
   being reproducible from a re-fetched reference.**
3. **It is exquisitely sensitive to symbol nomenclature.** Gene-symbol renames between releases
   re-key `probe_to_gene` and re-key the 862-row gene-count table by extension.

### 4b · The transcript-identifier convention elsewhere in the repository — the real mismatch

`research/modalities/emc-construct-inputs.json` records the fusion-partner transcript models as
**UNVERSIONED accessions**, fetched from `rest.ensembl.org` (`_ensembl` field), with no release:

| symbol | transcript | translation |
|---|---|---|
| EWSR1 | ENST00000397938 | ENSP00000381031 |
| TAF15 | ENST00000605844 | ENSP00000474096 |
| FUS | ENST00000254108 | ENSP00000254108 |
| TCF12 | ENST00000333725 | ENSP00000331057 |
| TFG | ENST00000240851 | ENSP00000240851 |
| NR4A3 | ENST00000395097 | ENSP00000378531 |
| PGR | ENST00000325455 | ENSP00000325120 |

⛔ **Unversioned accessions are stable in name and unstable in content.** The repository already has
a recorded instance of exactly this drift, in `research/modalities/nr4a3-intron2-cryptic-exon.json`:

```json
"transcript_named_in_the_paper_vs_today": {
  "paper": "ENST00000395097.6", "ensembl_today_version": 7,
  "_reading": "⚠ THE PAPER PINS ITS INTRON NUMBERING TO A VERSIONED TRANSCRIPT AND THE VERSION HAS MOVED."
}
```

So: the repository's own NR4A3 transcript has already moved `.6 → .7`, and every accession in the
table above is stored without the suffix that would have caught it.

### 4c · Verdict, and what it means for exact-match attribution and panel annotation coverage

| Question | Assessment |
|---|---|
| **Exact-match attribution** — can a 34–50 nt probe core be attributed to a gene reproducibly? | **Compatible in mechanism, unreproducible in identity.** The verbatim-substring method needs only FASTA and gene symbols, so any Ensembl human cDNA+ncRNA release will run. But because the release that produced the committed `probe_to_gene` is unrecorded and its bytes are gone, ⛔ **no future fetch can be shown to reproduce the committed attribution** — it can only be shown to agree or disagree with it. |
| **Panel annotation coverage** — how much of the 1,645-probe panel gets a gene? | **Release-dependent and currently unpinned.** 906/1,645 (55.1%) single-gene, 662 (40.2%) unassigned, at an unknown release. Coverage is a joint property of the panel and the reference set; **quoting 906 or 862 without a release is quoting a number whose denominator moved.** |
| **Transcript-version compatibility** | **Latently broken.** Unversioned ENSTs plus a recorded `.6 → .7` drift means a re-fetch can change sequence under a name the repository treats as fixed, with no guard to notice. |
| **Assembly compatibility** | **GRCh38 throughout**, consistently, with no evidence of any GRCh37 artifact in this chain. This is the one dimension that is cleanly compatible. |

**The single repair this checkpoint identifies, independent of whether any file is ever fetched:**
record an **immutable release identity** — `release-<N>` path plus the release `CHECKSUMS` entries
and byte sizes for both files — and **version the ENST accessions** in `emc-construct-inputs.json`.
Neither can be done from this session, because both require the denied host.

---

## 5 · Onward route — named, NOT taken

The repository already has a sanctioned path for exactly this denial, and it is **not** a
route-around: `.github/workflows/emc-expression-datasets.yml` runs
`emc_fourth_cohort_quant.py --phase map` on a GitHub Actions runner precisely because, in the
module's own words, *"Ensembl REST answers 403 to CONNECT from the dev sandbox."* That workflow is
how the 2026-09-02 read happened in the first place.

⛔ **I did not dispatch it.** Dispatching is a new external act, and my fences forbid commit, push,
workflow dispatch and environment change. It is recorded here so root can authorise it, with the
concrete ask if root does: pin `release-<N>` instead of `current_fasta`, fetch the release
`CHECKSUMS`, and persist release + checksum + byte size for both files into
`emc-fourth-cohort-quant.json`.

---

## 6 · Fences honoured

- k=12 quantification threshold, the EWSR1 NULL, assay restrictions and all source identities:
  **unchanged and untouched.** No clinical endpoint rerun, no read-count group comparison, no panel
  label altered. No manuscript, artifact or producer file edited. No commit, no push, no broad test
  suite, no preflight.
- No drift toward tumour fusion status or vendor-panel verification: this report makes **no** claim
  about any tumour's fusion status and **no** claim identifying or verifying any commercial panel.
- No paid resource, no unrelated genome, no repeated large copy, no environment overhaul, no
  alternate route around the denial.
- ⚠ Every URL in this report is a **locator only**. **No reference file was retrieved.**

---

## 7 · Bottom line for root

**DENIED.** `ftp.ensembl.org:443` answers 403 at CONNECT under this session's egress policy. The two
resources are **two files, not one**, plausibly **~370–460 MB compressed / ~1.6 GB uncompressed —
not 44.3 MB**. Disk headroom (14.87 GiB) was never the constraint. No immutable copy exists in the
retained index: what survives is a derived probe→gene map plus a **mutable `current_fasta` locator
with no release, no checksum and no byte size**, so the committed panel annotation is **agreeable
but not reproducible**. **B1 and B2 remain gated.**
