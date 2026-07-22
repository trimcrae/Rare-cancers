#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — the FROZEN leg manifest + per-leg run spec (prereg §3).

Single source of truth for "what runs": each leg's system (E3 + target + ligand), whether the celastrol warhead
is covalently restrained to Cys551, any target mutation, and the restraint atom pair. Both the endpoint-MD
driver (nrv04_covalent_md.py) and the Vast launcher (via gpu_backend.JobSpec) consume this, so the panel can't
drift between them. Pure data + pure builders -> unit-tested offline.

Leg 0 (cys_conservation) already ran ($0, CI) — it is not a GPU leg and is excluded here.
Optional paralogue legs (cov_nr4a2/cov_nr4a3) are intentionally ABSENT: Leg 0 showed the reactive Cys is unique
to NR4A1, so there is nothing covalent to model on the paralogues.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SEEDS = (0, 1, 2)                                  # 3 independent replicas per leg (prereg §4)

# celastrol electrophilic carbon (Michael acceptor) and the target reactive cysteine (prereg §2 restraint).
CELASTROL_ELECTROPHILE_ATOM = "C6"
TARGET_COV_RESNUM = 551                            # NR4A1 Cys551 (confirmed a Cys by Leg 0)


@dataclass(frozen=True)
class Leg:
    leg_id: str
    ligand: str                # "nrv04" | "nrv04_epimer" | "celastrol"
    target: str                # "NR4A1" | None (binary-VHL-only legs have no target LBD)
    covalent: bool             # impose the restrained-covalent C6->Cys551 bond?
    env: str                   # ternary_nr4a1 | binary_vhl  (which protein assembly to stage)
    mutation: str = ""         # e.g. "C551A" (leg 3) — empty = WT
    role: str = ""             # human note / control role
    controls_for: tuple = field(default_factory=tuple)  # which criterion this leg feeds


# Frozen panel (prereg §3 table, rows 1-6). Order is fixed.
PANEL = (
    Leg("cov_nr4a1", "nrv04", "NR4A1", True, "ternary_nr4a1",
        role="primary covalent ternary model", controls_for=("R1", "R2", "R4")),
    Leg("noncov_nr4a1", "nrv04", "NR4A1", False, "ternary_nr4a1",
        role="noncovalent sensitivity partner of cov_nr4a1", controls_for=("R2", "R4")),
    Leg("cov_c551a", "nrv04", "NR4A1", False, "ternary_nr4a1", mutation="C551A",
        role="covalent-engagement-removed control (bond impossible)", controls_for=("R2",)),
    Leg("warhead_only", "celastrol", "NR4A1", True, "ternary_nr4a1",
        role="no-E3-moiety negative: covalent bond but no recruiter", controls_for=("R2",)),
    Leg("recruiter_active", "nrv04", "NR4A1", False, "ternary_nr4a1",
        role="active recruiter positive control", controls_for=("R2",)),
    Leg("recruiter_epimer", "nrv04_epimer", None, False, "binary_vhl",
        role="VHL-inactive epimer negative (endpoint system, not a morph)", controls_for=("R2",)),
)

# The covalent-vs-noncovalent sensitivity comparison (R4) pairs these two legs.
SENSITIVITY_PAIR = ("cov_nr4a1", "noncov_nr4a1")


def leg_by_id(leg_id: str) -> Leg:
    for lg in PANEL:
        if lg.leg_id == leg_id:
            return lg
    raise KeyError(f"unknown leg {leg_id!r}; known: {[l.leg_id for l in PANEL]}")


def enumerate_units(seeds=SEEDS):
    """All independent GPU units = every (leg, seed). Each -> one Vast instance, its own checkpoint prefix."""
    return [(lg, s) for lg in PANEL for s in seeds]


def leg_env(leg: Leg, seed: int, mode: str = "run", prod_ns: float = 5.0, equil_ns: float = 1.0) -> dict:
    """The engine env for one (leg, seed) — consumed by nrv04_covalent_md.py. Deterministic, no I/O."""
    env = {
        "PANEL": "nrv04_covalent_feasibility",
        "LEG_ID": leg.leg_id,
        "SEED": str(seed),
        "MODE": mode,                              # smoke | run
        "LIGAND": leg.ligand,
        "TARGET": leg.target or "",
        "ENV_ASSEMBLY": leg.env,
        "COVALENT": "1" if leg.covalent else "0",
        "MUTATION": leg.mutation,
        "PROD_NS": str(prod_ns),
        "EQUIL_NS": str(equil_ns),
        "OPENMM_REQUIRE_CUDA": "1",
    }
    if leg.covalent:
        env["COV_LIG_ATOM"] = CELASTROL_ELECTROPHILE_ATOM
        env["COV_RESNUM"] = str(TARGET_COV_RESNUM)
    return env


def unit_name(leg: Leg, seed: int) -> str:
    """Stable per-unit name (used for the Vast label + the S3 checkpoint prefix so units never collide)."""
    return f"nrv04cov-{leg.leg_id}-s{seed}"
