# Original parent receipt — the 639-PMID anchor-set check (not rerun)

Run by the **parent collector** in this turn's transcript, committed bytes only, no network. Reproduced here as
the original command and its original output. **Not re-executed to produce this file.**

## Command, as issued

```
cd /home/user/Rare-cancers
python3 - <<'PY'
import json,re,sys
sys.path.insert(0,'research/manuscripts')
probe=json.load(open('research/literature/emc-host-factor-probe.json'))
inp=json.load(open('research/manuscripts/emc-host-factor-inputs.json'))
out=json.load(open('research/manuscripts/emc-host-factor-model.json'))
src=open('research/manuscripts/emc_host_factor_model.py').read()
m=re.search(r"def anchored_pmids.*?(?=\ndef )",src,re.S); print(m.group(0).strip()[:400]); print("---")
have=set(re.findall(r'"pmid"\s*:\s*"?(\d{6,9})"?', json.dumps(probe)))
print("PMIDs anchored in the probe:",len(have))
for row in inp.get("factors",[]):
    for ev in row.get("evidence",[]):
        if ev.get("status")=="unretrieved": continue
        p=str(ev.get("pmid") or "")
        print("  %-14s input PMID %-10s anchored=%s" % (row["id"],p,p in have))
PY
```

## Output, verbatim

```
def anchored_pmids(probe: dict) -> set[str]:
    found: set[str] = set()
    for entry in (probe.get("queries") or {}).values():
        for hit in entry.get("hits") or []:
            if hit.get("pmid"):
                found.add(str(hit["pmid"]))
    return found
---
PMIDs anchored in the probe: 639
  HF-OBESITY     input PMID 42292722   anchored=True
  HF-OBESITY     input PMID 42219271   anchored=True
  HF-OBESITY     input PMID 40726433   anchored=True
  HF-OBESITY     input PMID 42192361   anchored=True
  HF-SMOKING     input PMID 41300991   anchored=True
  HF-SMOKING     input PMID 42340948   anchored=False
  HF-CV-RISK     input PMID 42068528   anchored=False
  HF-CV-RISK     input PMID 42324568   anchored=True
  HF-SARCOPENIA  input PMID 40459648   anchored=True
  HF-SARCOPENIA  input PMID 41055780   anchored=False
  HF-SARCOPENIA  input PMID 41977025   anchored=True
```

A prior parent command in the same turn additionally recorded, from `grep -rl` over `research/` and `systems/`
with the campaign directory excluded, that `42340948` occurs in 2 committed files, `42068528` and `41055780` in
3 each, and `41300991` in 4 including `research/literature/emc-host-factor-probe.json`.

## ⚠ Dated scope note, 2026-09-08 07:52 UTC — the original claim stands, its reach is bounded

The check interrogated **one canonical set**: the `hits` of `research/literature/emc-host-factor-probe.json`,
which is precisely what `check_anchors` consults. Therefore:

- **Established:** absence of `42340948`, `42068528` and `41055780` from that probe's hits is **exactly why this
  guard fails**, and the failure is correct rather than a tooling artifact.
- **NOT established:** absence from **every retrieved artifact**, or from **every committed byte elsewhere**.
  No such exhaustive search was performed or retained, so no global-absence conclusion is available. The
  `grep -rl` above is a file-occurrence count, not a retrieval-anchoring search.
- **Therefore:** the need for external retrieval on these three rows is a **precise unresolved evidence gap**,
  **not** a proved global absence and **not** a request to route around any restriction. The rows remain
  **UNKNOWN, not false**.

No new lookup, network call, statistic, variant, edit or successor arises from this receipt.
