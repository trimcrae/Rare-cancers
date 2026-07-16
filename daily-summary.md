On track for **Tue Aug 11, 2026** (optimistic) — the RBFE infra shakeout (RUNG 0) is now running clean after early script failures.

**Since yesterday**
- Two spot-smoke RBFE solvent-simulate runs failed Wed evening with script errors (`ExecuteUserScriptError`); a fixed "am1bcc-v2" pipeline then reran solvent setup → simulate → analysis end-to-end successfully overnight.
- Step0 RBFE (OpenFE + managed-spot GPU shakeout) now completes cleanly — this is the last gate before real RBFE science starts.
- A congeneric-RBFE-v3 checkpoint-resume test also completed.

**Running now**
Nothing running.

**Path to done**
Next: reference-reproduction smoke (RUNG 1, ~Jul 19), then known-answer ternary + cmpd19 conditional RBFE (RUNG 2, Jul 19–22), benchmark expansion + NR-V04 covalent feasibility (RUNG 3, Jul 22–26), the prospective degrader matrix (RUNG 5, Jul 31–Aug 5), and manuscript write-up/submission (RUNG 6) — landing at the projected completion of **Tue Aug 11, 2026**.
