# LANE 13 watch board

`
########## tick 66  2026-07-26T16:09:28Z`

**nr4a-pdyn-nr4a1: phase=done ns=None done=True | nr4a-pdyn-nr4a1-smoke: phase=done ns=None done=True | nr4a-pdyn-nr4a2: phase=done ns=None done=True | nr4a-pdyn-nr4a2-smoke: phase=None ns=None done=False**

```
[ops] bucket=sagemaker-us-east-2-646605541856 prefix=nr4a-paralogue-ensemble

=== nr4a-pdyn-nr4a1
  deliverable in S3: YES
  phase: done {'n_frame_pdbs': 100, 'tarball': 'nr4a1-pocket-ensemble.tar.gz'}  (written 2026-07-26T16:06:42Z, 3 min ago)
    | [pdyn] 2026-07-26T16:09:25Z start target=NR4A1 metad_ns=60 release_ns=5 mode=real
    | [pdyn] result already in S3 -> nothing to do (awaiting CI reap)

=== nr4a-pdyn-nr4a1-smoke
  deliverable in S3: YES
  phase: done {'n_frame_pdbs': 12, 'tarball': 'nr4a1-pocket-ensemble.tar.gz'}  (written 2026-07-25T23:32:53Z, 997 min ago)
    | [pdyn] 2026-07-25T23:34:09Z start target=NR4A1 metad_ns=0.4 release_ns=0.2 mode=smoke
    | [pdyn] result already in S3 -> nothing to do (awaiting CI reap)

=== nr4a-pdyn-nr4a2
  deliverable in S3: YES
  phase: done {'n_frame_pdbs': 100, 'tarball': 'nr4a2-pocket-ensemble.tar.gz'}  (written 2026-07-26T12:22:34Z, 227 min ago)
    | [pdyn] 2026-07-26T12:24:24Z start target=NR4A2 metad_ns=60 release_ns=5 mode=real
    | [pdyn] result already in S3 -> nothing to do (awaiting CI reap)

=== nr4a-pdyn-nr4a2-smoke
  deliverable in S3: no
  phase: (none yet)
    | (no run.log yet)

=== Vast instances
  45878836 nr4a-pdyn-nr4a1 intended=running actual=running gpu=RTX 4080S dph=0.12977777777777777 up=10.45 h gpu_util=0.0 status_msg=success, running docker.io/triskit23/nr4a-metad_latest/ssh
[ops] DESTROY 45878836 nr4a-pdyn-nr4a1: deliverable already in S3

```
