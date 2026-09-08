"""Census: across EVERY target file and EVERY superseded entry, which matches does the new
left-edge rule suppress? Read-only over the real tree."""
import sys, re
sys.path.insert(0, "/tmp/claude-0/i1-lane/work")
import lint_consistency as lc
REPO = "/home/user/Rare-cancers"
reg = lc.load_registry()
tot = sup = 0
for rel in reg["targets"]:
    lines = lc._read_lines(REPO, rel)
    if lines is None:
        print("MISSING TARGET", rel); continue
    for e in reg["superseded"]:
        rx = re.compile(e["pattern"])
        for i, ln in enumerate(lines):
            for m in rx.finditer(ln):
                tot += 1
                if lc._begins_mid_number(ln, m.start(), m.group(0)):
                    sup += 1
                    ctx = ln[max(0, m.start()-40):m.end()+40]
                    print(f"SUPPRESSED {rel}:{i+1} [{e['id']}] {m.group(0)!r}\n    ...{ctx}...")
print(f"\ntotal pattern matches across all targets: {tot}; suppressed by the new rule: {sup}")
