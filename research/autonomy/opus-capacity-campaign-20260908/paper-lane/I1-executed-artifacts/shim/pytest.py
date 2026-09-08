"""Minimal stdlib-only stand-in for the parts of pytest this lane's tests use.

Used ONLY because this sandbox has no pytest and no network to install one. The delivered
test file is pytest-native; this shim is evidence-support, not a deliverable.
"""


class Skipped(Exception):
    pass


def skip(reason=""):
    raise Skipped(reason)


class _Mark:
    @staticmethod
    def parametrize(argnames, argvalues):
        names = [a.strip() for a in argnames.split(",")] if isinstance(argnames, str) else list(argnames)

        def deco(fn):
            cases = getattr(fn, "_params", [])
            for vals in argvalues:
                if len(names) == 1:
                    vals = (vals,)
                cases.append(dict(zip(names, vals)))
            fn._params = cases
            return fn
        return deco


mark = _Mark()
