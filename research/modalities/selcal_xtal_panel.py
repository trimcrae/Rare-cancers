#!/usr/bin/env python3
"""The crystal sensitivity control's PANEL — units, env, and the one thing that must never be shared.

★ EVERYTHING SCIENTIFIC IS IMPORTED FROM `selcal_panel`. Protocol (PROD_NS/EQUIL_NS), direction, alpha, the
statistic, the landed-leg predicates and the gate are the parent panel's, untouched. That is the entire
content of the word `control` here: if this lane ran a different protocol, a pass would say the readout works
at THAT protocol and would be silent about the one the program actually used.

⛔ THE ONE THING THAT IS DELIBERATELY NOT SHARED IS THE PANEL NAME AND THE LABEL PREFIX. A crystal leg and a
co-fold leg must never be counted by each other's collector — the measured failure this guards against is
`nrv04_retro_panel`'s, where a completeness count believed 17 records because their fields were POPULATED
rather than produced (STRATEGY Appendix A 57). `PANEL`, `LABEL_PREFIX` and `MODEL_SOURCE` are all distinct
and all travel in the leg record, so a record's provenance is readable from the record.

★ THE UNIT OF INDEPENDENCE IS THE CRYSTALLOGRAPHIC COPY. It is carried in `COFOLD_MODEL_SEED` — the field the
frozen gate keys its collapse-to-model-means on — so the existing scorer works unchanged. ⚠ That field name
is then a lie about provenance if read alone, which is why `MODEL_SOURCE=deposited_crystal_copy` and
`CRYSTAL_COPY_ID` travel beside it in the same env and the same record. A reader who sees only
`cofold_model_seed: 3` on a crystal leg is looking at an incomplete record, and `is_crystal_leg` is the
predicate that says so.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: ⛔ DISTINCT FROM `selcal_panel.PANEL`/`LABEL_PREFIX`, and neither is a prefix of the other — the same rule
#: `selcal_panel` states for `nrv04retro-`/`nrv04cov-`, so a reaper's selector can never match a sibling
#: lane's boxes and a collector can never count a sibling lane's legs.
PANEL = "selcal_xtal_control"
LABEL_PREFIX = "selxtal-"

#: Where the staged crystal units live. A FRESH prefix per design freeze, for the parent panel's reason: a
#: staged unit is a preregistered leg's input, and reusing a prefix silently changes what the panel started
#: from.
UNIT_PREFIX = os.environ.get("SELCAL_XTAL_UNIT_PREFIX") or "selcal-xtal-units-v1"
RESULT_PREFIX = os.environ.get("SELCAL_XTAL_RESULT_PREFIX") or "selcal-xtal-results"

#: The provenance tag that makes a crystal leg self-identifying in its own record.
MODEL_SOURCE = "deposited_crystal_copy"


def arms():
    """The parent panel's arms, unchanged — same genes, same predicted direction, same ids."""
    import selcal_panel as P
    return P.ARMS


def predicted_more_stable_arm():
    import selcal_panel as P
    return P.PREDICTED_MORE_STABLE_ARM


def protocol():
    """(prod_ns, equil_ns, replicas) — IMPORTED. A second copy of these is a second chance to drift."""
    import selcal_panel as P
    return P.PROD_NS, P.EQUIL_NS, P.MD_REPLICAS


def copy_index(copy_id) -> int:
    """`c03` -> 3. The gate collapses on an integer model key, so the copy id becomes one — reversibly."""
    s = str(copy_id).lstrip("cC")
    if not s.isdigit():
        raise ValueError("copy id %r is not of the form c<NN>" % (copy_id,))
    return int(s)


def copy_id(index: int) -> str:
    return "c%02d" % int(index)


def unit_name(arm, copy_id_str: str, replica: int) -> str:
    """Vast label + S3 checkpoint namespace for one unit. `selxtal-smarca2-c01-r0`."""
    return "%s%s-%s-r%d" % (LABEL_PREFIX, arm.cofold_system, copy_id_str, replica)


def unit_prefix_s3(arm, bucket: str, copy_id_str: str, prefix: str = None) -> str:
    """The S3 prefix of the specific staged CRYSTAL COPY this leg starts from.

    PINNED, never globbed, for the parent panel's reason: the copy is the unit of independence in the
    statistics, so a leg that silently drew a different one would break the collapse to copy means."""
    return "s3://%s/%s/%s/%s/" % (bucket, (prefix or UNIT_PREFIX).strip("/"), arm.cofold_system, copy_id_str)


def enumerate_units(copies_per_arm: dict, replicas=None):
    """[(arm, copy_id, replica), ...] from the census's usable-copy counts.

    ⛔ THE PANEL SHRINKS HERE AND NOWHERE ELSE — the collector builds `expected` from this function, so a
    completeness flag can only go true because the panel HONESTLY changed, never because a predicate was
    loosened to let an unreachable panel pass."""
    _, _, default_reps = protocol()
    replicas = default_reps if replicas is None else replicas
    out = []
    for a in arms():
        n = int(copies_per_arm.get(a.arm_id, 0))
        for i in range(1, n + 1):
            for r in replicas:
                out.append((a, copy_id(i), r))
    return out


def leg_env(arm, copy_id_str: str, replica: int, mode: str = "run", prod_ns=None, equil_ns=None) -> dict:
    """The engine env for one crystal unit — consumed by `nrv04_covalent_md.py` UNCHANGED.

    Built by DELEGATING to `selcal_panel.leg_env` and then overriding only what identifies this lane, so any
    future change to the shared protocol reaches this control automatically rather than being forgotten."""
    import selcal_panel as P
    base = P.leg_env(arm, copy_index(copy_id_str), replica, mode=mode,
                     prod_ns=P.PROD_NS if prod_ns is None else prod_ns,
                     equil_ns=P.EQUIL_NS if equil_ns is None else equil_ns)
    base.update({
        "PANEL": PANEL,
        "LEG_ID": "%s__%s" % (arm.arm_id, copy_id_str),
        # The gate keys its collapse on this integer; the two fields below are what stop it being read as a
        # co-fold seed by anything else.
        "COFOLD_MODEL_SEED": str(copy_index(copy_id_str)),
        "MODEL_SOURCE": MODEL_SOURCE,
        "CRYSTAL_COPY_ID": copy_id_str,
    })
    return base


def is_crystal_leg(rec) -> bool:
    """Is this record from THIS lane? Read from the record, never inferred from a filename or a prefix."""
    if not isinstance(rec, dict):
        return False
    return rec.get("PANEL") == PANEL or rec.get("panel") == PANEL or \
        rec.get("MODEL_SOURCE") == MODEL_SOURCE or rec.get("model_source") == MODEL_SOURCE


def partition_legs(records):
    """(crystal legs, foreign legs) — a foreign record is REPORTED, never silently dropped or counted.

    ⚠ Both halves are returned because both are informative and for opposite reasons: a foreign record in
    this lane's bucket means a prefix collision, and a crystal record missing from the first list means a leg
    that did not stamp its provenance. Either is a reason to stop, and neither is visible if the filter just
    returns what it liked."""
    ours, foreign = [], []
    for r in records or []:
        (ours if is_crystal_leg(r) else foreign).append(r)
    return ours, foreign
