"""Every image a lane rents a machine for must be one WE baked — never a stock upstream image.

★★ WHY THIS EXISTS (trimcrae, 2026-08-01: *"Are you ignoring your Claude.md? Is it too long?"*).
CLAUDE.md's "PULL, DON'T SOLVE" rule was read, cited correctly several times the same day, and still missed
here — because it was phrased "NEVER SOLVE A CONDA ENV **IN CI**" and filed under a heading that said
"CI environments", while the offence was on a **rented GPU**. A rule filed where it cannot fire is absent.

The offence: `nrv04_vast_launch.COFOLD_IMAGE` was the stock `pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime`,
so every co-fold rental ran `apt-get install`, `pip install boltz==2.2.1 cuequivariance-torch
cuequivariance-ops-torch-cu12`, and a **~3 GB** `download_boltz2` fetch **on the billing host** before one
second of science. Measured consequences: §6 puts a solve at ~15-25 min against a ~2-4 min pull, so that is
billed time on a 4090; **three of the four hosts that died on that lane died inside the fetch window**; and a
truncated CCD reached inference and failed six seeds at 7.2 s each on a missing **cysteine**.

So the rule stops depending on a reader noticing it. A stock image in a launcher is now a RED BUILD.

⚠ WHAT THIS IS NOT. It does not check that an image is *correct*, *current*, or *complete* — a baked image
can still be wrong (see `test_gcp_fanout_rep`'s documented-table drift, and the `min_cuda` probe that found
`ternary-fep` needed 12.6 rather than the asserted 13.0). It checks the one property whose absence means we
are renting a GPU to run `pip install`: **the image is ours, and something in this repo builds it.**
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

MODALITIES = Path(__file__).resolve().parents[1]
COMPUTE = MODALITIES.parents[0] / "compute"

#: `NAME_IMAGE = os.environ.get("X") or "..."` and `NAME_IMAGE = "..."`, which is how every launcher spells it.
_IMAGE_CONST = re.compile(
    r"^(?P<name>[A-Z][A-Z0-9_]*_IMAGE)\s*=\s*(?:os\.environ\.get\([^)]*\)\s*or\s*)?"
    r"[\"'](?P<image>[^\"']+)[\"']", re.M)

#: The account whose images this repo builds. CLAUDE.md §6 names it and wires `secrets.DOCKERHUB_TOKEN`.
OUR_REGISTRY = "triskit23/"

#: ⚠ EXEMPTIONS MUST BE ARGUED, AND THE ARGUMENT IS THE ENTRY. An exemption with no reason is how a stock
#: image creeps back in wearing an allow-list. Each entry says why the image carries no environment we could
#: have baked — NOT "this one is fine for now", which is what a dated TODO decays into.
EXEMPT = {
    # A 5 MiB probe used to test PLACEMENT, not to run science. There is no stack in it to bake, and baking
    # one would make the probe slower and less representative of a cold pull.
    "TINY_IMAGE": "alpine:latest — placement probe only; carries no scientific stack",
}

#: ⛔ THE LIVE VIOLATION, REGISTERED SO THE GUARD CAN LAND GREEN WITHOUT PARDONING IT.
#: This is NOT an exemption: it is the defect this file was written for, recorded with its remedy so that
#: (a) no NEW stock image can be added, and (b) deleting this one line is all that is needed once the bake
#: lands. A test asserts the entry still describes reality, so it cannot quietly become permanent.
KNOWN_VIOLATION = {
    "COFOLD_IMAGE": "pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime",
}


def _image_constants() -> list[tuple[str, str, str]]:
    """(module, constant, image) for every launcher in the package. Derived, never enumerated."""
    out = []
    for py in sorted(MODALITIES.glob("*.py")):
        for m in _IMAGE_CONST.finditer(py.read_text()):
            out.append((py.name, m.group("name"), m.group("image")))
    return out


def _dockerfile_for(image: str) -> Path | None:
    """The `Dockerfile.*` that builds `image`, matching on the repo tag with separators ignored.

    `triskit23/ternary-fep` is built by `Dockerfile.ternaryfep` and `triskit23/nr4a-metad` by
    `Dockerfile.nr4ametad`, so a literal comparison would fail on both — the separator is a naming habit,
    not a fact about the image.
    """
    repo = image.split("/")[-1].split(":")[0]
    want = re.sub(r"[-_.]", "", repo).lower()
    for df in COMPUTE.glob("Dockerfile.*"):
        if re.sub(r"[-_.]", "", df.suffix.lstrip(".")).lower() == want:
            return df
    return None


def test_the_scan_finds_the_launchers_at_all():
    """A guard whose subject vanished must fail, not pass vacuously — the failure mode that let a dead
    tripwire sit green through the fix it claimed to police (`test_the_RESIDUAL_gap...`, same day)."""
    consts = _image_constants()
    assert len(consts) >= 8, f"only found {len(consts)} image constants; the regex has lost its subject"
    assert any(c[1] == "COFOLD_IMAGE" for c in consts), "the constant this file exists for is not being seen"


@pytest.mark.parametrize("module,name,image", _image_constants(),
                         ids=[f"{m}:{n}" for m, n, _ in _image_constants()])
def test_every_lane_image_is_one_we_baked(module, name, image):
    if name in EXEMPT:
        return
    if name in KNOWN_VIOLATION:
        assert image == KNOWN_VIOLATION[name], (
            f"{module}:{name} changed to {image!r}. If it now pulls a baked image, DELETE its "
            f"KNOWN_VIOLATION entry — that is the whole point of the entry.")
        return
    assert OUR_REGISTRY in image, (
        f"{module}:{name} = {image!r} is a STOCK UPSTREAM IMAGE. A lane that rents a machine and then builds "
        f"its environment there pays GPU rates to run `pip install` (~15-25 min solve vs a ~2-4 min pull, "
        f"CLAUDE.md §6) and stands in the phase where hosts die — three of four on the co-fold lane died "
        f"inside exactly that window. Bake it: add research/compute/Dockerfile.<name>, a bake workflow "
        f"mirroring ternary-fep-bake.yml, and publish to {OUR_REGISTRY}. If it genuinely carries no stack, "
        f"add it to EXEMPT **with the argument**.")
    assert _dockerfile_for(image) is not None, (
        f"{module}:{name} = {image!r} is in our registry but NOTHING IN THIS REPO BUILDS IT. An image we "
        f"cannot rebuild is one we cannot fix, patch or reproduce — the same class as a declared artifact "
        f"nothing produces (test_lane_registry_contract.py).")


def test_the_known_violation_still_exists_or_the_entry_goes():
    """⚠ A registered violation that has been fixed but not deregistered is a lie the guard tells forever.

    This is the `terminal_artifact_unbacked` shape from `test_lane_registry_contract.py`: a marker that is
    legal only beside the defect it names, and that goes RED the moment the defect is gone."""
    live = {n: i for _, n, i in _image_constants()}
    for name, image in KNOWN_VIOLATION.items():
        assert name in live, f"{name} no longer exists — delete its KNOWN_VIOLATION entry"
        assert live[name] == image, (
            f"{name} is now {live[name]!r}, not the registered violation {image!r}. If it is baked, DELETE "
            f"the KNOWN_VIOLATION entry so this guard tightens; leaving it pardons a stock image forever.")


def test_an_exemption_must_carry_its_argument():
    """`EXEMPT` is the obvious escape hatch, so it is the obvious place for a stock image to hide. An entry
    whose reason is empty or a placeholder is not an argument."""
    for name, why in EXEMPT.items():
        assert len(why) > 30 and not re.search(r"\b(todo|tbd|for now|temporar)", why, re.I), \
            f"EXEMPT[{name}] does not argue its case: {why!r}"
