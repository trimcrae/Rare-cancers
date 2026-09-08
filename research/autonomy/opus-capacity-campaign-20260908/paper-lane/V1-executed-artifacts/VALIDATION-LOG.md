# V1 VALIDATION LOG

## Start state
```
$ date -u
Tue Sep  8 11:46:25 UTC 2026
$ git rev-parse HEAD
0330edbef9e85276ec518dbf2c445bf1d026fd26
$ git status --porcelain
(empty)
```

## End state
```
$ date -u
Tue Sep  8 11:49:55 UTC 2026
$ git rev-parse HEAD
3be62db0eb09fe0c918cd72d4cad406fc7be6c6e
$ git status --porcelain
(exit 0)
```

## Commands run in lane
```
$ diff R2-BASELINE research/manuscripts/repurposing/repurposing-hypotheses.md   -> exit 0 (byte-identical)
$ python3 /tmp/claude-0/v1-lane/apply_v1_edits.py
edits applied: 8
baseline lines: 711 candidate lines: 736
exit=0
$ diff -u BASELINE-committed... V1-CANDIDATE...  > V1-CANDIDATE-vs-committed.diff   -> exit 1 (differences, expected), 107 lines
$ reference-section sha256 (from "## 9. References" to EOF), both files:
  6d5f11139792bca06a4905e4a87dd66c98ba7759a40ee0229f168b29ac4f009a
$ sentence-set diff: 7 removed / 19 added (all intended)
No figure generator copied, modified or executed. No gate, no preflight, no network.
```

## Lane file hashes
```
1933916c41e74a724da9c79bd2f16ee3ff7169e808477fb8562456c467aa802e  ./BASELINE-committed-repurposing-hypotheses.md
3a29d868d4675552a42f8dba60f0fe5cddeb51e6d72e3cc783088a933bf187f5  ./MEMO-V1-t2-candidate.md
e16408f590a111cc63cfbe9a82ba689de817ccddb7936cee0f6d0801cafb09da  ./R2-original-proposal/CANDIDATE-A-T2-repurposing-hypotheses.md
54d90c08067ae52b87657a6a3b2d3d26c322e73bceb0370f8614b1993a701a01  ./R2-original-proposal/CANDIDATE-A-T2.diff
ee3e7914d526dad3017563ab66a03de857b6a2c72f4dc685b426d5f5392cfe21  ./R2-original-proposal/MEMO-R2-tier-decision.md
6c55cf5261ef85c808a9fb75fbe45c569a38919c739ffd5d086e0ec99c7392b8  ./V1-CANDIDATE-repurposing-hypotheses.md
f0160341135b69e5b52a77c06c99d9e57e3e6ecaa693c41fc52a7fad73940cde  ./V1-CANDIDATE-vs-committed.diff
7aae6f765981bbd59ced0c49a9198034b773ae593027d90abb5880c6a214ca3b  ./VALIDATION-LOG.md
ec695907e62cb4403f577ae84023aaf134025c7e1c750922a508640e9991dea0  ./apply_v1_edits.py
```

## Committed figure (from U2, NOT re-inspected by V1)
```
research/manuscripts/figures/repurposing-fig1-design.png  177,415 B
sha256 f711ea7f2c4fd3e4c3d26cfacc61519db5018fb40dcf87c208e1b45ac3ca2075
UNCHANGED - V1 made no figure change.
```
