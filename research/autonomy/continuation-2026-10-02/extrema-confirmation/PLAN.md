---
id: DOC-ASO-UNION-EXTREMA-CERTIFICATE-20261002
title: Independent ASO union-extrema certificate plan
level: cross-cutting
kind: memo
status: live
purpose: Define an independent retrospective certificate check of the reported ASO union sequence extrema.
scope: All 220 union Hamming minima and complete-core gap maxima across two pinned reference corpora; individual-stratum extrema are excluded.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: unverified
---

# Independent union-extrema certificate — prepared 2026-10-02

This is a retrospective verification plan, not a preregistration. Frontmatter remains unverified while compilation and execution are pending.

## Scope and present status

Prepared code and synthetic tests; **no compilation, synthetic execution, or full-corpus execution has occurred in this seat**. Quiet Python syntax inspection only is permitted locally. Root must review and cloud-execute before using a pass claim. This specifically closes a named gap in the earlier exact-census/witness verification: its checked witnesses establish attainability but do not prove global nonzero Hamming minimality or complete-core-tract maximality.

The pinned result has 220 designs: 215 research target designs and 5 annotation-error controls. All union Hamming claims are exact 0, 1, or 2 (19/170/31 designs respectively); union gap maxima are 12–16. The checker certifies **220 union Hamming minima and 220 union gap maxima across BOTH archived seven-gene FASTA and GENCODE v50**. It does not certify the 660 individual-stratum Hamming minima/censoring bounds, individual-stratum gap maxima, nearest-hit counts, or ranking implementation. Do not relabel the output as an independent full-stratum reproduction.

## Certificate argument

Hamming: for a challenged minimum h in {0,1,2}, construct literal DNA strings at every distance 0..h from the 16-base target. Scan both complete corpora with Aho–Corasick and report the smallest matched distance (sentinel 3 means no generated pattern found). Equality to h requires both an attained distance-h window and absence of any smaller-distance window. A falsely low challenge fails through absence; a falsely high challenge fails through finding a closer hit. Although radius-0/1 plus a saved distance-2 witness would suffice, explicit radius-2 enumeration for the 31 challenged designs removes dependence on the previous witness selection and validates existence directly. It remains bounded: 1+48+1080 strings per h=2 design.

Gap: the complete core is target positions [5,11), in target-sense orientation. For each claimed maximum g, generate every target substring [l,r) with l<=5, r>=11 and r-l=g (attainment), plus all such substrings of length g+1 (counterexample). Every longer complete-core exact tract contains an interval of length g+1 that still contains the complete core. For zero, search length 6; for 16, no longer tract is possible. A dictionary hit is eligible only if its inferred aligned full 16-base window lies wholly within the same transcript and every base in that window is unambiguous. This rejects short terminal matches and Ns outside an otherwise matching core. The full window and transcript/start witness are emitted for attained or violating claims.

The C++ engine only reports challenge evidence; the Python conjunction requires coverage of every design in both corpus outputs, the challenged minimum, attained positive gap maximum, and no greater tract. Supplied thresholds are proof challenges, never assumed truths.

## Independence and limitations

The original engine uses rolling two-bit windows, encoded mismatch-neighborhood hash lookup and a six-base gap seed followed by extension. This engine uses literal-string Aho–Corasick transitions and interval-pattern dictionaries, with a prefix count of ambiguous characters for full-window eligibility. Gap logic is structurally independent. Hamming uses the same necessary mathematical neighborhood definition, independently represented/traversed; this is not a claim of completely unrelated mathematics. Synthetic oracle uses direct positionwise comparisons and brute-force all core-containing intervals, with no automaton/encoding.

Normalization uppercases sequence, maps U to T and removes whitespace; other symbols invalidate the entire 16-base window. Transcript records are never joined; duplicate record identifiers fail. Source orientation is checked against the archived catalogue antisense complement. GENCODE header lengths are checked. Corpus record/base/window/parent totals must equal the frozen result, serving coverage checks rather than another accepted exact-match census.

No tissue expression, RNA accessibility, cleavage, potency or clinical safety claim follows.

## Pinned inputs and cloud invocation

Result:
https://raw.githubusercontent.com/trimcrae/Rare-cancers/6514d5c0399453d5cbd38c3989ba632dfd336d88/research/autonomy/continuation-2026-10-02/results/aso-transcriptome.json
Git blob: 54450defc4fac3fb1b9f159e3157a8f713f47f53

Catalogue:
https://raw.githubusercontent.com/trimcrae/Rare-cancers/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/results/all-designs.tsv
40363 bytes; SHA256 f231499b036e4c6b79f729cee0a44a4c482ab6215167e61c2fc0c4a3ceed7799

Archive:
https://raw.githubusercontent.com/trimcrae/Rare-cancers/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/results/normal-reference-transcripts.fasta
356744 bytes; SHA256 4cabff15767f8d7b38aefc75fa46233a954d13ac7802010b672aee3d9723c580

GENCODE:
https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz
183554921 compressed bytes; SHA256 5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56

Reuse already cached cloud inputs when available. The runner has no networking and checks all pins before compilation. Root may obtain missing inputs in its cloud job through the existing bounded/hash-checked fetch routine. No local bulk retrieval. Cloud transient budget: <1 GiB including compressed input, compiler output, automaton and small certificates; allow <=2 GiB RAM conservatively. No expanded FASTA is written.

Example, using fresh output directory:
~~~sh
python3 run_extrema_confirmation.py \
  --result /path/aso-transcriptome.json \
  --catalogue /path/all-designs.tsv \
  --archive /path/normal-reference-transcripts.fasta \
  --gencode /path/gencode.v50.transcripts.fa.gz \
  --out /path/extrema-output
~~~

Requires existing cloud g++, zlib headers/library and Python standard library only. Compile timeout 120 s; synthetic suite 120 s; each corpus scan 1800 s. Use a 40-minute outer job bound including bounded input acquisition. Publish only scripts, tests, plan and small output TSV/JSON receipts, never the raw transcriptome. Stop on first pin, syntax, test, coverage or certificate failure; investigate the concrete counterexample rather than retry unchanged.

14 named synthetic tests cover endpoint windows, record boundaries, incomplete flanks, ambiguous bases inside/outside the core, all 16 single-mismatch locations, a true distance-2 case, too-low/too-high Hamming and gap challenges, no radius-2 hit, zero gap, orientation-sensitive core, RNA/lowercase/whitespace normalization, gzip/final-no-newline, aliases, 360 deterministic mixed-threshold challenges, missing/duplicate certificates, and invalid challenge ranges. These are authored tests, not passed tests at preparation time.

## Focused static review — 2026-10-02

No blocking algorithm defect identified in this bounded static review. Python syntax inspection passed; C++ compilation and synthetic/corpus execution remain unperformed.

- Boundary eligibility: a pattern ending at position p and representing target interval [l,r) yields full-window start p+1-(r-l)-l. Signed arithmetic rejects negative starts before conversion to size_t. The upper bound requires start+16<=transcript length; ambiguity prefix differences inspect all 16 bases, not merely the matched tract. The automaton state resets at ambiguous characters and at each transcript. Both terminal windows are included; no cross-record match is possible.
- Duplicate targets: query IDs must be unique, while target sequences may repeat. Each trie output retains its query index and metric, so aliases and differing challenges for the same sequence remain separate certificates. Synthetic cases cover aliases and repeated targets under different thresholds.
- Radius-2 negative certificate: mutations use strictly increasing positions and restore the literal target after recursion. This generates every string at distances 0, 1 and 2 without omitting positions or double-mutating a position. The reported best match must equal the challenged value across both corpora; an unattained challenge retains sentinel 3 and fails, while an overstated minimum returns the smaller value and fails. At gap maximum 16 the upper bound is inherent in the 16-base window, but attainment is still mandatory.
- Watchdogs: compilation, synthetic tests and each corpus subprocess have explicit timeouts. The 40-minute outer job deadline is a separate hard budget, not the sum of those individual allowances; it may stop a slow second scan before its own 1800-second allowance expires. The wrapper must set this outer deadline. Certificate success is written only after both scans and all checks; timeout or partial TSVs are not a pass.
- Storage: the runner itself does not fetch or expand FASTA and does not enforce a free-space floor. Root's cloud wrapper must measure free space before acquiring any missing input, reserve the stated budget, and preserve at least 10 GiB free. Reuse pinned cached inputs first. The <1 GiB transient-disk and <=2 GiB RAM figures are conservative planning estimates, not measured maxima or enforced resource quotas; the compressed input is 183,554,921 bytes. A failure should retain small diagnostics, never trigger an unchanged retry or local bulk fallback.

Finite next action: root review, then one cloud execution. A successful output is extrema-confirmation.json plus both per-corpus certificate TSVs and coverage metadata. On pass, manuscript methods may say union extrema independently certified; individual-stratum censoring and occurrence-count limitations remain.
