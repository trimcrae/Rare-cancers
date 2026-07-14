#!/usr/bin/env python3
"""Introspect the INSTALLED OpenFE to design a CPU-build / GPU-MD split of the RBFE protocol (2026-07-14, trimcrae:
run the ~80-min single-threaded hybrid-system BUILD on a cheap/free CPU box, only the MD on GPU). We must reuse
OpenFE's validated alchemical machinery, NOT hand-roll it (repo engine policy), so we need to know EXACTLY where
the build/MD boundary is and whether OpenFE exposes a clean serialization + restart hook. Prints a structured
report AND writes the full source of the ProtocolUnit's execute method to a file the workflow commits, so a fresh
session can read the real code (version-accurate — inspect.getsource on the pinned openfe>=1.1). No GPU, no MD.
"""
import inspect
import io
import os
import re


def main() -> int:
    import openfe
    out = io.StringIO()

    def p(*a):
        print(*a)
        print(*a, file=out)

    p(f"[introspect] openfe version: {getattr(openfe, '__version__', '?')}")
    from openfe.protocols import openmm_rfe as M
    # OpenFE 1.12 splits into HybridTopologySetupUnit (CPU build) -> ...SimulationUnit (GPU MD) -> ...AnalysisUnit.
    # Find ALL ProtocolUnit classes (those with _execute) + the Protocol class (has create()).
    unit_classes, proto_cls = [], None
    for name in dir(M):
        obj = getattr(M, name)
        if inspect.isclass(obj):
            if hasattr(obj, "_execute") and name.endswith("Unit"):
                unit_classes.append(obj)
            if name.endswith("Protocol") and not name.endswith("Unit") and hasattr(obj, "create"):
                proto_cls = obj
    p(f"[introspect] Protocol class: {proto_cls.__name__ if proto_cls else None}")
    p(f"[introspect] ProtocolUnit classes: {[c.__name__ for c in unit_classes]}")
    if not unit_classes:
        p("[introspect] no *Unit with _execute; dir(openmm_rfe):", dir(M))
        return 1

    # DEFAULT settings — to answer definitively where "ps per iteration" comes from (we only set the total
    # equilibration/production lengths; time_per_iteration is OpenFE's own default, which we never override).
    if proto_cls and hasattr(proto_cls, "default_settings"):
        try:
            ds = proto_cls.default_settings()
            ss = getattr(ds, "simulation_settings", None)
            for a in ("time_per_iteration", "equilibration_length", "production_length", "n_replicas",
                      "real_time_analysis_interval", "sampler_method"):
                if ss is not None and hasattr(ss, a):
                    p(f"[introspect] DEFAULT simulation_settings.{a} = {getattr(ss, a)}")
            ig = getattr(ds, "integrator_settings", None)
            for a in ("timestep", "n_steps", "nsteps"):
                if ig is not None and hasattr(ig, a):
                    p(f"[introspect] DEFAULT integrator_settings.{a} = {getattr(ig, a)}")
            ls = getattr(ds, "lambda_settings", None)
            if ls is not None and hasattr(ls, "lambda_windows"):
                p(f"[introspect] DEFAULT lambda_settings.lambda_windows = {getattr(ls, 'lambda_windows')}")
        except Exception as e:  # noqa: BLE001
            p(f"[introspect] default-settings dump failed: {e}")

    full = io.StringIO()
    # dump the Protocol.create() FIRST — it shows how the units are wired into the DAG (setup->sim->analysis
    # input dependencies) which is exactly what we need to run them on separate instances.
    if proto_cls:
        for m in ("_create", "create"):
            if hasattr(proto_cls, m):
                try:
                    print(f"\n===== {proto_cls.__name__}.{m} =====\n{inspect.getsource(getattr(proto_cls, m))}",
                          file=full)
                except (TypeError, OSError):
                    pass
    for unit_cls in unit_classes:
        methods = [n for n, _ in inspect.getmembers(unit_cls, predicate=inspect.isfunction)]
        p(f"[introspect] {unit_cls.__name__} methods: {methods}")
        want = [m for m in methods if m in ("_execute", "run", "_run", "execute", "__init__") or
                re.search(r"hybrid|system|sampler|simulat|minim|equil|restart|resume|setup|charge|serial", m, re.I)]
        for m in sorted(set(want)):
            try:
                src = inspect.getsource(getattr(unit_cls, m))
                _, ln = inspect.getsourcelines(getattr(unit_cls, m))
            except (TypeError, OSError) as e:
                p(f"[introspect]   (no source for {unit_cls.__name__}.{m}: {e})")
                continue
            print(f"\n===== {unit_cls.__name__}.{m}  (starts ~line {ln}) =====\n{src}", file=full)

    src_all = full.getvalue()
    # boundary signals: where GPU/MD begins vs where the CPU hybrid build is
    signals = ["HybridTopologyFactory", "hybrid_system", "htf", "MultiStateSampler", "MultiStateReporter",
               "from_storage", "storage_exists", "reporter", "minimize", "equilibrate", "production",
               "XmlSerializer", "serialize", "checkpoint", "dry", "n_replicas", "lambda", "create_system",
               "Interchange", "assign_partial_charges", "generate_residue_template", "Context",
               "positions", "openmm.System", "extend", "resume"]
    p("\n[introspect] SIGNAL HITS in the execute-path source (term: count):")
    for s in signals:
        c = len(re.findall(re.escape(s), src_all))
        if c:
            p(f"    {s:28s} {c}")

    # print a few lines of context around the highest-value boundary terms
    lines = src_all.splitlines()
    for term in ("HybridTopologyFactory", "hybrid_system", "MultiStateSampler", "from_storage", "dry_run",
                 "def _execute", "minimize", "sampler.run", ".extend("):
        idxs = [i for i, ln in enumerate(lines) if term in ln]
        for i in idxs[:3]:
            ctx = "\n".join(lines[max(0, i - 1):i + 2])
            p(f"\n  >> near '{term}':\n{ctx}")

    # write full source for the workflow to commit (logs may truncate)
    dest = os.environ.get("INTROSPECT_OUT", "openfe_unit_source.txt")
    with open(dest, "w") as fh:
        fh.write(f"openfe {getattr(openfe, '__version__', '?')}\nunit={unit_cls.__name__}\n\n")
        fh.write(src_all)
    p(f"\n[introspect] wrote full execute-path source ({len(src_all)} chars) -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
