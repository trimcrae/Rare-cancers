On track for **Thu Jul 30** (optimistic), though an overnight cluster of job failures is worth watching.

**Since yesterday**
- 4 congeneric-RBFE-v3 jobs (solvent-setup + complex-leg) failed with the same `AlgorithmError: ExecuteUserScriptError` — a recurring bug worth fixing before more spend goes into retries.
- 6 more complex-leg jobs were stopped early from spot preemption (short billable time each, no real loss).
- 7 jobs completed cleanly: congeneric RBFE solvent-leg setup, simulate, analyze, and checkpoint-restart steps, plus an RBFE spot-smoke solvent setup.

**Running now**
- RBFE spot-smoke solvent simulation, about 40 minutes in (1/8 spot slots in use).

**Path to done**
The ABFE λ-overlap repair and pocket-tracking re-analysis finish by Jul 17, the T4L-L99A ABFE benchmark by Jul 18, and the NR-V04 ternary control by Jul 20; those gate the congeneric RBFE series and prospective ternary ranking, with the paper folded together and red-teamed by Jul 29, landing on ChemRxiv/JCIM by **Thu Jul 30**.
