"""Resolution floor: recompute the headline group means at n_points 96 / 256 / 512 on a 9-frame subset."""
import json,os,sys,statistics
sys.path.insert(0,"/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/UNIQUE-RESIDUE-ADDRESSABILITY-1")
import unique_residue_addressability as M
M._init()
paths=M.frame_paths(); sub=[paths[i] for i in (0,8,16,25,33,41,50,58,66)]
LAB=[380,381,382,383,385,386,387,388,390,394,570]
pocket=set(M.UNIQ.CRYPTIC_POCKET_UNIPROT)
prev=None
for npz in (96,256,512):
    M.NPOINTS=npz
    fr=[M.score_frame(p) for p in sub]
    per={}
    for rid in fr[0]["rows"]:
        u=fr[0]["rows"][rid]["uniprot"]
        per[u]={"rsa":statistics.fmean(f["rows"][rid]["rsa"] for f in fr),
                "d":statistics.fmean(f["rows"][rid]["d_pocket"] for f in fr)}
    lab=statistics.fmean(per[u]["rsa"] for u in LAB)
    allm=statistics.fmean(per[u]["rsa"] for u in per if u not in pocket)
    labd=statistics.fmean(per[u]["d"] for u in LAB)
    line=f"n_points={npz}: indel RSA mean={lab:.4f}  all-modelled RSA mean={allm:.4f}  indel d_pocket mean={labd:.3f}"
    if prev: line+=f"   delta_vs_prev: RSA {lab-prev[0]:+.4f} / {allm-prev[1]:+.4f}, d {labd-prev[2]:+.4f}"
    print(line,flush=True)
    prev=(lab,allm,labd)
