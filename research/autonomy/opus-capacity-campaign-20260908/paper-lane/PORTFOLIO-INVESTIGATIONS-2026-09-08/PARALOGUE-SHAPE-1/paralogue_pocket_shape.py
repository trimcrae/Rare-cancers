#!/usr/bin/env python3
"""PARALOGUE-SHAPE-1 — per-frame POCKET GEOMETRY of the homologous NR4A cryptic pocket.

Unit of analysis: for each committed unbiased release conformer, the 45 pairwise CA-CA
distances among the 10 HOMOLOGOUS Pocket-5 lining residues, plus the radius of gyration of
those 10 CA atoms. Superposition-free (internal distances only). Variance is decomposed into
species against replica-within-species, and every separation is tested against (a) an exact
replica-block species-label permutation and (b) a within-species replica-vs-replica baseline.

GEOMETRY ONLY. Nothing here is a selectivity, druggability, efficacy, safety,
therapeutic-window or clinical-readiness statement.

Read-only outside this lane directory. No network, no GPU, no re-simulation.
"""
import hashlib, itertools, json, os, sys, time
import numpy as np

REPO = "/home/user/Rare-cancers"
LANE = os.path.join(REPO, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                          "PORTFOLIO-INVESTIGATIONS-2026-09-08/PARALOGUE-SHAPE-1")

# Homologous lining set. NR4A3 Pocket-5 reference = nr4a3_metad.py REF_CV_RESIDUES;
# paralogue UniProt ids are the alignment-derived sets published in each ensemble's
# release_summary.json cv_residues; local->UniProt offsets are the committed values in
# research/modalities/nr4a-paralogue-dynamics.json construct[sp].local_to_uniprot_offset.
SPECIES = ["NR4A1", "NR4A2", "NR4A3"]
ROOT = {"NR4A1": "results/nr4a1-pocket-ensemble",
        "NR4A2": "results/nr4a2-pocket-ensemble",
        "NR4A3": "results/nr4a3-pocket-reharmonize"}
OFFSET = {"NR4A3": 372, "NR4A1": 347, "NR4A2": 343}
UNIPROT = {"NR4A3": [406, 407, 410, 411, 412, 481, 484, 485, 531, 534],
           "NR4A1": [372, 373, 376, 377, 380, 450, 453, 454, 500, 503],
           "NR4A2": [372, 373, 376, 377, 380, 450, 453, 454, 500, 503]}
# Expected CA residue names at the mapped local ids (identity check; a wrong offset must abort).
EXPECT = {"NR4A1": ["HIS", "LEU", "GLY", "PRO", "ALA", "ARG", "TYR", "ARG", "VAL", "PHE"],
          "NR4A2": ["HIS", "VAL", "ASN", "PRO", "THR", "ARG", "TYR", "ARG", "ILE", "PHE"],
          "NR4A3": ["LEU", "THR", "THR", "PRO", "ARG", "ARG", "ILE", "ARG", "ILE", "LEU"]}
REPS = ["release_rep0", "release_rep1", "release_rep2"]
PAIRS = [(i, j) for i in range(10) for j in range(i + 1, 10)]  # 45


def read_ca(path, local_ids):
    """CA coordinates (Angstrom) for the requested local residue ids, in order."""
    want = {r: k for k, r in enumerate(local_ids)}
    xyz = [None] * len(local_ids)
    names = [None] * len(local_ids)
    with open(path) as fh:
        for L in fh:
            if L.startswith("ATOM") and L[12:16].strip() == "CA":
                r = int(L[22:26])
                k = want.get(r)
                if k is not None and xyz[k] is None:
                    xyz[k] = (float(L[30:38]), float(L[38:46]), float(L[46:54]))
                    names[k] = L[17:20]
    if any(v is None for v in xyz):
        raise SystemExit(f"ABORT: missing CA for {path}")
    return np.array(xyz, float), names


def frame_dirs(sp, rep):
    d = os.path.join(REPO, ROOT[sp], rep)
    return sorted(os.path.join(d, x, "frame.pdb") for x in os.listdir(d) if x.startswith("fp_"))


def sha(path, n=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(n), b""):
            h.update(b)
    return h.hexdigest()


def collect():
    rows, meta = [], {}
    for sp in SPECIES:
        loc = [u - OFFSET[sp] for u in UNIPROT[sp]]
        meta[sp] = {"local_to_uniprot_offset": OFFSET[sp], "uniprot_lining": UNIPROT[sp],
                    "local_lining": loc}
        for rep in REPS:
            fs = frame_dirs(sp, rep)
            if len(fs) != 25:
                raise SystemExit(f"ABORT: {sp}/{rep} has {len(fs)} frames, expected 25")
            for p in fs:
                X, nm = read_ca(p, loc)
                if nm != EXPECT[sp]:
                    raise SystemExit(f"ABORT: identity mismatch {sp} {p}: {nm}")
                D = np.array([np.linalg.norm(X[i] - X[j]) for i, j in PAIRS])
                rg = float(np.sqrt(((X - X.mean(0)) ** 2).sum(1).mean()))
                rows.append({"species": sp, "replica": rep,
                             "frame": os.path.basename(os.path.dirname(p)),
                             "rg_A": rg, "d": D})
    return rows, meta


def nested_var(vals, sp_idx, rep_idx):
    """Balanced nested decomposition of one feature: species / replica(species) / residual."""
    g = np.asarray(vals, float)
    gm = g.mean()
    ss_tot = ((g - gm) ** 2).sum()
    ss_sp = 0.0
    ss_rep = 0.0
    for s in range(3):
        ms = g[sp_idx == s]
        ss_sp += ms.size * (ms.mean() - gm) ** 2
        for r in range(3):
            mr = g[(sp_idx == s) & (rep_idx == r)]
            ss_rep += mr.size * (mr.mean() - ms.mean()) ** 2
    ss_res = ss_tot - ss_sp - ss_rep
    return ss_tot, ss_sp, ss_rep, ss_res


def main():
    t0 = time.time()
    rows, meta = collect()
    Z = np.array([r["d"] for r in rows])              # 225 x 45
    rg = np.array([r["rg_A"] for r in rows])
    sp_idx = np.array([SPECIES.index(r["species"]) for r in rows])
    rep_idx = np.array([REPS.index(r["replica"]) for r in rows])
    blk = sp_idx * 3 + rep_idx                        # 0..8 replica blocks

    # --- pooled WITHIN-REPLICA sd is the scale: this makes the standardisation blind to
    # any species or replica mean shift, so it cannot manufacture separation.
    within_sd = np.zeros(45)
    for k in range(45):
        v = 0.0
        for b in range(9):
            x = Z[blk == b, k]
            v += ((x - x.mean()) ** 2).sum()
        within_sd[k] = np.sqrt(v / (225 - 9))
    S = Z / within_sd                                  # standardized shape coordinates

    # --- per-feature variance decomposition (45 distances + Rg)
    feat = []
    for k, (i, j) in enumerate(PAIRS):
        tot, s_sp, s_rep, s_res = nested_var(Z[:, k], sp_idx, rep_idx)
        feat.append({"pair": f"{UNIPROT['NR4A3'][i]}-{UNIPROT['NR4A3'][j]}",
                     "nr4a3_uniprot_i": UNIPROT["NR4A3"][i],
                     "nr4a3_uniprot_j": UNIPROT["NR4A3"][j],
                     "mean_A": round(float(Z[:, k].mean()), 4),
                     "eta2_species": round(s_sp / tot, 4),
                     "eta2_replica_within_species": round(s_rep / tot, 4),
                     "eta2_residual": round(s_res / tot, 4),
                     "within_replica_sd_A": round(float(within_sd[k]), 4)})
    tot, s_sp, s_rep, s_res = nested_var(rg, sp_idx, rep_idx)
    rg_decomp = {"eta2_species": round(s_sp / tot, 4),
                 "eta2_replica_within_species": round(s_rep / tot, 4),
                 "eta2_residual": round(s_res / tot, 4),
                 "within_replica_sd_A": round(float(np.sqrt(s_res / (225 - 9))), 4)}

    # --- multivariate separation statistic T. Computed on REPLICA CENTROIDS so that
    # frames-within-replica correlation cannot inflate it, and so the same formula gives
    # the within-species replica baseline.
    C = np.array([S[blk == b].mean(0) for b in range(9)])   # 9 x 45 replica centroids

    def T_of(labels):
        """mean between-group centroid distance / mean within-group replica spread."""
        labels = np.asarray(labels)
        gc = np.array([C[labels == g].mean(0) for g in range(3)])
        betw = np.mean([np.linalg.norm(gc[a] - gc[b]) for a, b in itertools.combinations(range(3), 2)])
        wit = []
        for g in range(3):
            M = C[labels == g]
            wit += [np.linalg.norm(M[a] - M[b]) for a, b in itertools.combinations(range(len(M)), 2)]
        return betw / np.mean(wit), betw, float(np.mean(wit))

    true_lab = np.array([b // 3 for b in range(9)])
    T_obs, betw_obs, wit_obs = T_of(true_lab)

    # exact replica-block permutation: all 1680 assignments of 9 blocks into 3 labelled
    # groups of 3; the 280 distinct partitions each appear 6 times, so the test is exact.
    perms, Ts = [], []
    for combo in itertools.combinations(range(9), 3):
        rest = [x for x in range(9) if x not in combo]
        for c2 in itertools.combinations(rest, 3):
            lab = np.empty(9, int)
            lab[list(combo)] = 0
            lab[list(c2)] = 1
            lab[[x for x in rest if x not in c2]] = 2
            perms.append(lab)
            Ts.append(T_of(lab)[0])
    Ts = np.array(Ts)
    p_block = float((Ts >= T_obs - 1e-12).sum() / Ts.size)

    # frame-level label permutation (anti-conservative; reported for contrast only)
    rng = np.random.default_rng(20260908)
    frame_T = []
    for _ in range(2000):
        pl = rng.permutation(sp_idx)
        gc = np.array([S[pl == g].mean(0) for g in range(3)])
        betw = np.mean([np.linalg.norm(gc[a] - gc[b]) for a, b in itertools.combinations(range(3), 2)])
        frame_T.append(betw)
    frame_T = np.array(frame_T)
    p_frame = float(((frame_T >= betw_obs - 1e-12).sum() + 1) / (frame_T.size + 1))

    # --- within-species replica baseline: treat each species' 3 replicas as 3 pseudo-species
    # and measure the same centroid spread. This is what the species contrast has to beat.
    per_sp_replica_spread = {}
    for s, sp in enumerate(SPECIES):
        M = C[s * 3:(s + 1) * 3]
        per_sp_replica_spread[sp] = round(float(np.mean(
            [np.linalg.norm(M[a] - M[b]) for a, b in itertools.combinations(range(3), 2)])), 4)

    # --- "states the paralogues never do": nearest-neighbour occupancy in shape space.
    par = S[sp_idx != 2]
    nr3 = S[sp_idx == 2]

    def nn(A, B):
        return np.array([np.min(np.linalg.norm(B - a, axis=1)) for a in A])

    nn_nr3_to_par = nn(nr3, par)
    # paralogue internal cross-replica baseline: each paralogue frame to all paralogue
    # frames from a DIFFERENT replica (the honest comparator for a cross-group NN).
    par_blk = blk[sp_idx != 2]
    nn_par_cross = np.array([np.min(np.linalg.norm(par[par_blk != par_blk[i]] - par[i], axis=1))
                             for i in range(par.shape[0])])
    thr = float(np.quantile(nn_par_cross, 0.95))
    frac_outside = float((nn_nr3_to_par > thr).mean())

    # 1-D Rg envelope overlap
    rg_par = rg[sp_idx != 2]
    rg3 = rg[sp_idx == 2]
    rg_overlap = {
        "nr4a3_mean_A": round(float(rg3.mean()), 4), "nr4a3_sd_A": round(float(rg3.std(ddof=1)), 4),
        "nr4a3_min_A": round(float(rg3.min()), 4), "nr4a3_max_A": round(float(rg3.max()), 4),
        "paralogue_min_A": round(float(rg_par.min()), 4), "paralogue_max_A": round(float(rg_par.max()), 4),
        "nr4a3_frames_outside_paralogue_range": int(((rg3 < rg_par.min()) | (rg3 > rg_par.max())).sum()),
        "per_species_mean_A": {sp: round(float(rg[sp_idx == i].mean()), 4) for i, sp in enumerate(SPECIES)},
        "per_replica_mean_A": {f"{SPECIES[b // 3]}/{REPS[b % 3]}": round(float(rg[blk == b].mean()), 4)
                               for b in range(9)}}

    # --- convergence / resolution floor: halve the sampling deterministically and re-run T.
    half = np.zeros(225, bool)
    for b in range(9):
        idx = np.where(blk == b)[0]
        half[idx[::2]] = True
    Ch = np.array([S[half & (blk == b)].mean(0) for b in range(9)])
    Cf = C
    C = Ch
    T_half = T_of(true_lab)[0]
    p_half = float((np.array([T_of(l)[0] for l in perms]) >= T_half - 1e-12).sum() / len(perms))
    C = Cf
    # replica-centroid standard error per coordinate (the floor below which a centroid
    # difference is not resolved by this sampling)
    sem_per_coord = float(np.mean(within_sd / np.sqrt(25)))


    # --- THE DECISIVE CONTROL. An absolute distance matrix separates three DIFFERENT
    # proteins for a trivial reason: different sequences give different backbone geometry.
    # That is a static fact about the starting models, not evidence that NR4A3 VISITS states
    # the paralogues never visit. So remove each species' own mean shape and ask the
    # question again on the FLUCTUATION coordinates only.
    Sc = S.copy()
    for s_ in range(3):
        Sc[sp_idx == s_] -= S[sp_idx == s_].mean(0)

    # per-replica dispersion about its OWN replica centroid (breathing amplitude, sd units)
    disp = np.array([float(np.mean(np.linalg.norm(S[blk == b] - S[blk == b].mean(0), axis=1)))
                     for b in range(9)])

    def disp_T(labels):
        labels = np.asarray(labels)
        gm = np.array([disp[labels == g].mean() for g in range(3)])
        betw = np.mean([abs(gm[a] - gm[b]) for a, b in itertools.combinations(range(3), 2)])
        wit = []
        for g in range(3):
            m = disp[labels == g]
            wit += [abs(m[a] - m[b]) for a, b in itertools.combinations(range(len(m)), 2)]
        return betw / np.mean(wit)

    dT_obs = disp_T(true_lab)
    dTs = np.array([disp_T(l) for l in perms])
    p_disp = float((dTs >= dT_obs - 1e-12).sum() / dTs.size)

    # fluctuation-space occupancy: same NN test, now on species-centred coordinates
    parc, nr3c = Sc[sp_idx != 2], Sc[sp_idx == 2]
    nnc = np.array([np.min(np.linalg.norm(parc - a, axis=1)) for a in nr3c])
    nnc_base = np.array([np.min(np.linalg.norm(parc[par_blk != par_blk[i]] - parc[i], axis=1))
                         for i in range(parc.shape[0])])
    thr_c = float(np.quantile(nnc_base, 0.95))

    # centred T (species mean removed): must collapse toward the permutation null
    Cc = np.array([Sc[blk == b].mean(0) for b in range(9)])
    C_save = C
    C = Cc
    Tc_obs = T_of(true_lab)[0]
    Tcs = np.array([T_of(l)[0] for l in perms])
    p_Tc = float((Tcs >= Tc_obs - 1e-12).sum() / Tcs.size)
    C = C_save

    centred = {
        "_why": "an absolute distance matrix separates three different proteins trivially; "
                "the dynamics question survives only on species-centred fluctuations",
        "species_mean_removed_T": round(float(Tc_obs), 4),
        "species_mean_removed_p_block": round(p_Tc, 5),
        "_species_mean_removed_is_degenerate": "T is 0 and p is 1 BY CONSTRUCTION once each "
            "species mean is subtracted; reported only to show the centring was applied, NOT "
            "as evidence. The informative fluctuation tests are the dispersion contrast and "
            "the fluctuation-space nearest-neighbour test below.",
        "breathing_amplitude_sd_units_by_replica":
            {f"{SPECIES[b // 3]}/{REPS[b % 3]}": round(float(disp[b]), 4) for b in range(9)},
        "breathing_amplitude_by_species":
            {sp: round(float(disp[i * 3:(i + 1) * 3].mean()), 4) for i, sp in enumerate(SPECIES)},
        "dispersion_contrast_T": round(float(dT_obs), 4),
        "dispersion_contrast_p_block": round(p_disp, 5),
        "fluctuation_space_nn": {
            "nr4a3_to_paralogue_median": round(float(np.median(nnc)), 4),
            "paralogue_cross_replica_median": round(float(np.median(nnc_base)), 4),
            "paralogue_cross_replica_p95": round(thr_c, 4),
            "frac_nr4a3_beyond_p95": round(float((nnc > thr_c).mean()), 4)},
    }

    out = {
        "_id": "PARALOGUE-SHAPE-1",
        "_title": "Per-frame NR4A pocket geometry: lining-residue distance matrix and pocket Rg, "
                  "decomposed into species against replica",
        "_question": "Does NR4A3's pocket visit conformational states the paralogues never do?",
        "_scope": "GEOMETRY ONLY. No selectivity, druggability, efficacy, safety, "
                  "therapeutic-window or clinical-readiness claim is made or follows.",
        "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inputs": {"roots": ROOT, "ensembles": REPS, "frames_per_replica": 25,
                   "n_frames_total": len(rows),
                   "biased_metad_subsets_excluded": True,
                   "lining": meta,
                   "reference_lining_source":
                       "research/modalities/nr4a3_metad.py REF_CV_RESIDUES (NR4A3 Pocket-5); "
                       "paralogue ids from each release_summary.json cv_residues; offsets from "
                       "research/modalities/nr4a-paralogue-dynamics.json construct",
                   "identity_check": "CA residue names at every mapped local id verified against "
                                     "the committed cv_identities / AF-Q92570 Pocket-5 identities"},
        "feature_definition": {
            "distance_matrix": "45 pairwise CA-CA distances among the 10 homologous lining "
                               "residues, Angstrom, superposition-free",
            "pocket_rg": "radius of gyration of the same 10 CA atoms, Angstrom",
            "standardisation": "each distance divided by the POOLED WITHIN-REPLICA sd "
                               "(216 df), which is blind to species and replica means"},
        "variance_decomposition": {"per_distance": feat, "pocket_rg": rg_decomp,
            "summary": {
                "median_eta2_species": round(float(np.median([f["eta2_species"] for f in feat])), 4),
                "median_eta2_replica_within_species":
                    round(float(np.median([f["eta2_replica_within_species"] for f in feat])), 4),
                "n_distances_species_gt_replica":
                    int(sum(f["eta2_species"] > f["eta2_replica_within_species"] for f in feat)),
                "n_distances": 45}},
        "separation": {
            "statistic": "T = mean between-group replica-centroid distance / mean within-group "
                         "replica-centroid distance, in pooled-within-replica sd units",
            "T_observed": round(float(T_obs), 4),
            "between_species_centroid_distance": round(float(betw_obs), 4),
            "within_species_replica_centroid_distance": round(float(wit_obs), 4),
            "within_species_replica_spread_by_species": per_sp_replica_spread},
        "checks_that_can_fail": {
            "exact_replica_block_permutation": {
                "n_assignments": int(Ts.size), "n_distinct_partitions": 280,
                "p_value": round(p_block, 5),
                "min_attainable_p": round(6.0 / Ts.size, 5),
                "T_permutation_median": round(float(np.median(Ts)), 4),
                "T_permutation_max": round(float(Ts.max()), 4),
                "observed_rank_from_top": int((Ts > T_obs + 1e-12).sum()) + 1},
            "frame_label_permutation": {
                "n": 2000, "p_value": round(p_frame, 5),
                "note": "anti-conservative: frames within a replica are correlated, so this "
                        "test cannot by itself establish a species effect"},
            "replica_baseline": {
                "note": "within-species replica-vs-replica centroid spread is the baseline; "
                        "the species contrast must beat it",
                "between_over_within": round(float(betw_obs / wit_obs), 4)}},
        "occupancy": {
            "question": "do NR4A3 frames occupy shape-space cells no paralogue frame reaches?",
            "nn_nr4a3_to_paralogue": {
                "min": round(float(nn_nr3_to_par.min()), 4),
                "median": round(float(np.median(nn_nr3_to_par)), 4),
                "max": round(float(nn_nr3_to_par.max()), 4)},
            "nn_paralogue_cross_replica_baseline": {
                "min": round(float(nn_par_cross.min()), 4),
                "median": round(float(np.median(nn_par_cross)), 4),
                "p95": round(thr, 4),
                "max": round(float(nn_par_cross.max()), 4)},
            "frac_nr4a3_frames_beyond_paralogue_p95_nn": round(frac_outside, 4),
            "pocket_rg_envelope": rg_overlap},
        "centred_fluctuation_control": centred,
        "convergence": {
            "resolution_floor_note": "a per-frame geometric statistic is sampling-sensitive "
                                     "(cf. ASSESS-DEGRADER-2); values below the floor are not resolved",
            "mean_replica_centroid_sem_sd_units": round(sem_per_coord / float(np.mean(within_sd)), 4),
            "T_at_full_sampling_25_frames": round(float(T_obs), 4),
            "T_at_half_sampling_13_frames": round(float(T_half), 4),
            "p_block_at_half_sampling": round(p_half, 5),
            "n_ns_per_replica": 5.0},
        "runtime_s": round(time.time() - t0, 2)}

    os.makedirs(LANE, exist_ok=True)
    with open(os.path.join(LANE, "paralogue-pocket-shape.json"), "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    # per-frame table (compact, Rg + the 6 highest-eta2 distances) for reuse
    order = np.argsort([-f["eta2_species"] for f in feat])[:6]
    pf = {"_note": "per-frame pocket Rg and the six distances with the largest species eta2",
          "columns": ["species", "replica", "frame", "rg_A"] + [feat[k]["pair"] for k in order],
          "rows": [[r["species"], r["replica"], r["frame"], round(r["rg_A"], 4)]
                   + [round(float(r["d"][k]), 4) for k in order] for r in rows]}
    with open(os.path.join(LANE, "per-frame-pocket-shape.json"), "w") as fh:
        json.dump(pf, fh, indent=1)
        fh.write("\n")

    print(f"frames={len(rows)}  T_obs={T_obs:.4f}  betw={betw_obs:.4f}  within={wit_obs:.4f}")
    print(f"exact block permutation p={p_block:.5f} (min attainable {6.0/Ts.size:.5f}), "
          f"rank {int((Ts > T_obs+1e-12).sum())+1}/{Ts.size}")
    print(f"frame-level permutation p={p_frame:.5f}")
    print(f"median eta2 species={np.median([f['eta2_species'] for f in feat]):.4f}  "
          f"median eta2 replica(species)={np.median([f['eta2_replica_within_species'] for f in feat]):.4f}  "
          f"species>replica on {sum(f['eta2_species']>f['eta2_replica_within_species'] for f in feat)}/45")
    print(f"Rg eta2 species={rg_decomp['eta2_species']} replica={rg_decomp['eta2_replica_within_species']}")
    print(f"Rg NR4A3 {rg_overlap['nr4a3_min_A']}-{rg_overlap['nr4a3_max_A']} vs paralogue "
          f"{rg_overlap['paralogue_min_A']}-{rg_overlap['paralogue_max_A']}; "
          f"outside={rg_overlap['nr4a3_frames_outside_paralogue_range']}/75")
    print(f"NN NR4A3->paralogue median={np.median(nn_nr3_to_par):.4f} vs paralogue cross-replica "
          f"p95={thr:.4f}; frac beyond={frac_outside:.4f}")
    print(f"CENTRED T={Tc_obs:.4f} p={p_Tc:.5f}; dispersion T={dT_obs:.4f} p={p_disp:.5f}")
    print(f"breathing by species: " + str({sp: round(float(disp[i*3:(i+1)*3].mean()),4) for i,sp in enumerate(SPECIES)}))
    print(f"fluct-space NN nr4a3->par median={np.median(nnc):.4f} vs par cross-replica p95={thr_c:.4f}; frac beyond={(nnc>thr_c).mean():.4f}")
    print(f"half sampling T={T_half:.4f} p={p_half:.5f}; centroid sem={sem_per_coord/np.mean(within_sd):.4f} sd")
    return 0


if __name__ == "__main__":
    sys.exit(main())
