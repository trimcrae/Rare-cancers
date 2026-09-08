# Build record — fusion-output and vaccine-path PDFs (4 files, 2 pairs)

Date: 2026-09-08. Untracked working note. Production rebuild only: no manuscript, artifact,
producer or stamp was edited, nothing was committed or pushed, ATR / `atr-panel-ask` was not touched.
A rebuilt PDF is a production artifact. Nothing here asserts scientific readiness, efficacy,
safety or clinical acceptance.

## 1 · Pre-build gate

`git status --porcelain` was **empty** immediately before the first build. HEAD, and the commit all
four builds were run at:

    3e833d982f0c057804ec6a67cea64dfb1a68bfdf
    3e833d982 Figure provenance: a source equivalence recorded as a verification, not as a generation

Source manuscripts, `git log -1`:

| source | commit | date | subject |
|---|---|---|---|
| `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md` | `593e8dece4810627c4681d1206bca789fb131c08` | Tue Sep 8 18:45:17 2026 +0000 | Fusion-output and degrader batches; the release-inventory proposal |
| `research/manuscripts/neoantigen/emc-vaccine-development-path.md` | `414e661c9fbeb3d726f34525379fd57934b26d79` | Tue Sep 8 18:38:18 2026 +0000 | Vaccine path: two miscounts fixed, unsupported proteome counts withdrawn |

## 2 · Before / after

| artifact | bytes before | sha256 before | bytes after | sha256 after |
|---|---|---|---|---|
| `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.pdf` | 925784 | `d4dcfa9c2747ccde117c9ffd1b1df8e3e8cdbaa59270b6352f93e5ecd212b1d5` | 1020137 | `0c580fd7e8343ab66ed96007bb44c3542a5a959fa8561f9d60a98dd47cd83a0d` |
| `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-manuscript.pdf` | 865324 | `5e00c9bbc1308e656d5546c14d75383cfc289430bd0eabe973a86a52979a5bf2` | 968734 | `c44bbc617171848fb65c5e4310b1cb3083980a54b35be6e74ae7ffa210b7fbbd` |
| `research/manuscripts/neoantigen/emc-vaccine-development-path.pdf` | 879747 | `1cdbc93a959f4e89e15a2b4061c971be88dc0e783393b9dad299f76899c3355c` | 901331 | `bf6c03ec85e2dec423293f7435d2a78efc45eae2c357604865f1b03be54a0f6f` |
| `research/manuscripts/neoantigen/emc-vaccine-development-path-manuscript.pdf` | 778303 | `51d376f7de33d8633be6bc69ffe39c5beba2e984ae428150d9e38f4e45d1ac00` | 798024 | `7e537b5ce41a4517779f8fdfdc0f03d1768337d8a894c9e07cf7df2c779be78b` |

All four before-sizes match the sizes named in the task. Before-mtimes were all 2026-09-04 12:16:55.
Each artifact's `.build-stamp.json` was rewritten by the renderer as part of its own build; the
fusion-output journal stamp's recorded source hash moved from `c23812ff…` to `5eb8f366…`, and the
vaccine-path journal stamp's from `59a72c41…` to `ec877d12…` (both figure SVG hashes unchanged).

## 3 · The four builds — each run exactly once

Exit codes were captured from `$?` on an unpiped invocation. All four are real.

### B1
    python3 research/manuscripts/build_submission_pdf.py --paper fusion-output --style journal
    EXIT=0
stdout:
    fusion-output [journal]: wrote research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.pdf (996 KB, 14 pages; the handling statement is on every page)
stderr:
      ⚠ journal style: no deposited filename declared for emc-fourth-cohort-sra-2026-08-08.md, gse243553-eno3-overlap-2026-08-08.md, nr4a3-cistrome-search-2026-08-08.md, nr4a3-fusion-transcriptional-output-SI.md, nr4a3-fusion-transcriptional-output-cover-letter.md, nr4a3-fusion-transcriptional-output-repo-notes.md, nr4a3-fusion-transcriptional-output-submission-checklist.md — a reader is sent to a file that does not travel with the deposit
    build_submission_pdf.py:2806: DeprecationWarning: remove_identicals is deprecated and will be removed in pypdf 7.0.0. Use remove_duplicates instead.
    build_submission_pdf.py:2806: DeprecationWarning: remove_orphans is deprecated and will be removed in pypdf 7.0.0. Use remove_unreferenced instead.

### B2
    python3 research/manuscripts/build_submission_pdf.py --paper fusion-output --style manuscript
    EXIT=0
stdout:
    fusion-output [manuscript]: wrote research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-manuscript.pdf (946 KB, 30 pages; the handling statement is on every page)
stderr: same deposited-filename warning (same seven files) and the same two pypdf DeprecationWarnings.

### B3
    python3 research/manuscripts/build_submission_pdf.py --paper vaccine-path --style journal
    EXIT=0
stdout:
    vaccine-path [journal]: wrote research/manuscripts/neoantigen/emc-vaccine-development-path.pdf (880 KB, 13 pages; the handling statement is on every page)
stderr:
      ⚠ journal style: no deposited filename declared for shared-vs-individualized-neoantigen-evidence.md — a reader is sent to a file that does not travel with the deposit
    plus the same two pypdf DeprecationWarnings.

### B4
    python3 research/manuscripts/build_submission_pdf.py --paper vaccine-path --style manuscript
    EXIT=0
stdout:
    vaccine-path [manuscript]: wrote research/manuscripts/neoantigen/emc-vaccine-development-path-manuscript.pdf (779 KB, 16 pages; the handling statement is on every page)
stderr: same single deposited-filename warning and the same two pypdf DeprecationWarnings.

The deposited-filename warnings and the pypdf DeprecationWarnings are pre-existing renderer
behaviour at this commit. Nothing was changed to silence them.

## 4 · Page-1 stamp lines, as actually printed

| artifact | stamp text on page 1 |
|---|---|
| fusion-output journal | `Version of 2026-09-08 · typeset preview · built from 3e833d982` |
| fusion-output manuscript | `Version of 2026-09-08 · submission format · built from 3e833d982, tree not clean at build time` |
| vaccine-path journal | `Version of 2026-09-08 · typeset preview · built from 3e833d982, tree not clean at build time` |
| vaccine-path manuscript | `Version of 2026-09-08 · submission format · built from 3e833d982, tree not clean at build time` |

For contrast, the stamps on the replaced Sep 4 bytes were `Version of 2026-09-02 … built from
bd7af2449, tree not clean at build time` (both fusion-output files) and `Version of 2026-09-01 …
built from 54bd84d17, tree not clean at build time` (both vaccine-path files).

## 5 · Page inspection

`pdftotext` is **not installed** in this environment. Text was extracted with `pypdf` 6.17.0.

| artifact | pages before | pages after | extracted chars after | figure captions after |
|---|---|---|---|---|
| fusion-output journal | 15 | **14** | 117232 | Figure 1–5 |
| fusion-output manuscript | 27 | **30** | 118873 | Figure 1–5 |
| vaccine-path journal | 12 | **13** | 134410 | Figure 1–2 |
| vaccine-path manuscript | 16 | 16 | 135581 | Figure 1–2 |

Truncation check: every file's last extracted characters are body text followed by the running
footer `Research use only — not for administration.` and the final page number, matching the page
count. No file ends mid-sentence or mid-section.

Expected vaccine-path corrections, found in **both** vaccine-path renders:

- `6 alleles` — "those 97 peptides return 10 strong peptide-allele calls across 6 alleles".
- `five of the ten fall below 0.2755` — "…best in-frame call of 0.3736; five of the ten fall below
  0.2755." The correction note is also present: "Section 2.2, 'four of the ten fall below 0.2755'
  Five do: 0.1039, 0.1704, 0.2482, 0.2653 and 0.2745…".
- Withdrawn unreviewed-proteome counts — present, 10 occurrences of "unreviewed", including "the
  counts previously printed here for it are withdrawn", the named figures 127,090 / 12 / none
  identified as withdrawn, `trembl_included: false`, and "the state of that search is unknown here
  rather than negative".

The fusion-output renders contain none of those strings, which is correct — they belong to
vaccine-path only.

## 6 · Differences I did not expect

1. **Three of four stamps say "tree not clean at build time", although the tree was verifiably
   clean before B1.** Cause identified, and it is not the build's own outputs: the renderer
   explicitly excludes `.pdf`, `.build-stamp.json` and `.build.html` from its dirty check
   (`build_submission_pdf.py` ~line 604). The dirt is a file another writer created *during* B1:
   `research/autonomy/opus-capacity-campaign-20260908/paper-lane/ADJUDICATION-FO-figure-estimand-mismatch.md`,
   untracked, mtime `19:19:32.486`, four milliseconds after B1 finished writing its PDF at
   `19:19:32.482`. B1's stamp was computed before it existed and reads clean; B2–B4 saw it and
   stamped dirty. The rendered *sources* were still the committed ones at `3e833d982` — the
   intruding file is an untracked note in the autonomy lane, not an input to either paper — but the
   two fusion-output renders of one paper now carry disagreeing provenance lines, which is exactly
   the failure mode the code comment at line 596 was written to prevent. Flagged, not worked around;
   nothing was rebuilt to obtain a nicer stamp.
2. **Page counts moved in three of four files**, in both directions: fusion-output journal 15 → 14,
   fusion-output manuscript 27 → 30, vaccine-path journal 12 → 13. Sources changed since Sep 4, so
   movement is expected in principle; the fusion-output *decrease* alongside a 3-page *increase* in
   its own manuscript pair-member is the part I did not predict and have not traced to a cause.
3. **Byte sizes rose for all four**, including vaccine-path where the edit withdrew text.
4. The fusion-output journal render is the only one of the four whose stamp omits the document-kind
   caveat difference; both fusion-output files still print "typeset preview" / "submission format"
   as expected, so no `is_outgoing_file` behaviour was triggered here.

Rebuilt PDFs and their regenerated `.build-stamp.json` files are left in place, uncommitted, for the
parent to review.
