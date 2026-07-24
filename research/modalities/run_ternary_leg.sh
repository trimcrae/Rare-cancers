#!/usr/bin/env bash
# ============================================================================================================
# SINGLE SOURCE OF TRUTH for running ONE ternary-cooperativity alchemical leg.
#
# WHY THIS FILE EXISTS: the ternary recipe (which settings + the stage -> pre-equilibrate -> overlay -> run
# sequence) must live in ONE place so it CANNOT drift between execution lanes. Every lane — the GCP workflow
# (gpu-ternary-fep-gcp.yml) and the Vast firm lane (nrv04_vast_launch.py firm) — MUST call THIS script rather
# than re-implement the invocation. A hand-copied duplicate is what caused the Vast lane to run 16 windows and
# NaN where the proven recipe uses 12.
#
# PROVEN CLEAN: this exact recipe ran the calib_hi_to_lo ternary leg to a converged ΔG_morph = 47.28 ± 0.53
# on the GCP valB lane (see ternary-rbfe-runbook.md §1c + nr4a3-ternary-calib-prereg-addendum-2026-07-19.md).
#
# THE RECIPE, and why each piece matters (all overridable via env, but these defaults are the proven-clean set):
#   - N_WINDOWS=12              : the proven λ-window count (16 NaN'd at window 5; more windows is NOT safer).
#   - RBFE_TIMESTEP_FS=2.0      : production timestep (the calib ternary NaN's at 4 fs).
#   - RBFE_WARMUP_TIMESTEP_FS=1.0 : reduced-dt warmup — lets the integrator survive the rough softcore start.
#                                  (The workflow DEFAULT for this is EMPTY = 2 fs, which NaN's — it must be set.)
#   - RBFE_MIN_STEPS=5000       : minimization (25000 wastes ~20-60 min at ~0% GPU for no NaN benefit).
#   - CHARGE_METHOD=nagl        : must match the binary RBFE leg (ΔΔG_coop = ternary − binary cancels charges).
#   - pre-equilibration         : plain-MD relax of the physical complex BEFORE the alchemy (fixes the softcore
#                                  warmup NaN on the rough SMARCA4->SMARCA2 homology model). Deterministic
#                                  (seeded by SEED), so a fresh run == a cached one for a given seed.
#
# REQUIRED env : PY (python bin), IN (input dir), OUT (output dir), LEG_ID.
# OPTIONAL env : SEED (0), DIRECTION (fwd), TEMPLATE_PDB (8G1Q), PREEQUIL_NS (0.5), any RBFE_* override,
#                RBFE_PROD_ITERS / RBFE_WARMUP_ITERS (leave unset = full science length; set short for a timing
#                probe), SKIP_PREEQUIL=1 (caller already overlaid a relaxed structure, e.g. from a cache),
#                and any provider-specific passthrough the caller exports (e.g. RBFE_SPOT_COMMIT_GCS,
#                RBFE_SETUP_CACHE_GCS, SETUP_CACHE_VERSION) — those are inherited by nr4a3_ternary_fep.py.
# ============================================================================================================
set -eo pipefail
: "${PY:?run_ternary_leg.sh: PY (python bin) required}"
: "${IN:?run_ternary_leg.sh: IN (input dir) required}"
: "${OUT:?run_ternary_leg.sh: OUT (output dir) required}"
: "${LEG_ID:?run_ternary_leg.sh: LEG_ID required}"

# ---- frozen-correct ternary recipe (single source of truth; :- lets a caller override with good reason) ----
export SEED="${SEED:-0}"
export DIRECTION="${DIRECTION:-fwd}"
export CHARGE_METHOD="${CHARGE_METHOD:-nagl}"
export N_WINDOWS="${N_WINDOWS:-12}"
export RBFE_TIMESTEP_FS="${RBFE_TIMESTEP_FS:-2.0}"
export RBFE_WARMUP_TIMESTEP_FS="${RBFE_WARMUP_TIMESTEP_FS:-1.0}"
export RBFE_MIN_STEPS="${RBFE_MIN_STEPS:-5000}"
export RBFE_CONSTRAIN_LIGAND_CH="${RBFE_CONSTRAIN_LIGAND_CH:-0}"
export OPENMM_REQUIRE_CUDA="${OPENMM_REQUIRE_CUDA:-1}"
export INPUT_DIR="$IN" OUTPUT_DIR="$OUT" CKPT_DIR="${CKPT_DIR:-$OUT}"
export MODE=run LEG_ID

echo "[ternary-leg] LEG=$LEG_ID seed=$SEED windows=$N_WINDOWS dt=${RBFE_TIMESTEP_FS}fs warmup_dt=${RBFE_WARMUP_TIMESTEP_FS}fs charge=$CHARGE_METHOD min=$RBFE_MIN_STEPS"

# 1) STAGE the leg from the crystal template (skip if already staged)
if [ ! -f "$IN/$LEG_ID/complex.pdb" ]; then
  echo "[ternary-leg] staging $LEG_ID from ${TEMPLATE_PDB:-8G1Q}"
  $PY ternary_pdb_stage.py --leg-id "$LEG_ID" --template-pdb "${TEMPLATE_PDB:-8G1Q}" --out "$IN"
fi

# 2) PRE-EQUILIBRATION (relax the physical complex -> fixes the softcore warmup NaN), then overlay the relaxed
#    complex.pdb + ligands.sdf over the staged tree. Skip if the caller already overlaid a (cached) relaxed one.
if [ "${SKIP_PREEQUIL:-0}" != 1 ]; then
  echo "[ternary-leg] pre-equilibration (ternary_preequil.py)"
  env LEG_ID="$LEG_ID" SEED="$SEED" CHARGE_METHOD="$CHARGE_METHOD" PREEQUIL_NS="${PREEQUIL_NS:-0.5}" \
      PREEQUIL_EXACT_FF=1 OPENMM_PLATFORM=CUDA OPENMM_REQUIRE_CUDA=1 INPUT_DIR="$IN" OUTPUT_DIR="$OUT" \
      $PY ternary_preequil.py
  cp "$OUT/$LEG_ID/complex.pdb" "$OUT/$LEG_ID/ligands.sdf" "$IN/$LEG_ID/"
  echo "[ternary-leg] overlaid relaxed complex.pdb + ligands.sdf into $IN/$LEG_ID"
fi

# 3) RUN the alchemical leg. All science settings are already exported above; any provider-specific env the
#    caller exported (commit/cache URIs, RBFE_PROD_ITERS, etc.) is inherited by the process.
echo "[ternary-leg] --- MD (nr4a3_ternary_fep.py) ---"
$PY nr4a3_ternary_fep.py
