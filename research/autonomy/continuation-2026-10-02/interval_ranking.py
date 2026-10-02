"""Conservative interval arithmetic for the frozen ASO catalogue extension.

The scanner is exhaustive through Hamming radius 3. An empty exact-hit list
therefore means every scanned stratum has minimum >=4. The archived exact
minimum supplies an upper bound because the archived corpus is retained.
"""


def _distance(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 16:
        raise ValueError(name + " must be an integer Hamming distance in 0..16")
    return value


def union_distance(archive_exact, observed_exact_list):
    """Return (lower, upper, exact_or_None) for the retained-corpus union.

    observed_exact_list contains only minima actually resolved by the radius-3
    scanner, hence values must be 0..3. It includes any resolved archive scan.
    """
    archive = _distance(archive_exact, "archive_exact")
    observed = list(observed_exact_list)
    for value in observed:
        _distance(value, "observed exact minimum")
        if value > 3:
            raise ValueError("Radius-3 exact observations must be <=3")
    if observed:
        best = min(observed)
        if best > archive:
            raise ValueError("Observed union minimum exceeds retained archive minimum")
        return best, best, best
    if archive < 4:
        raise ValueError("No radius-3 hit conflicts with archived exact minimum <4")
    return 4, archive, 4 if archive == 4 else None


def rank_primary_intervals(primary_rows):
    """Return (resolved, sorted final design IDs) among primary co-winners.

    Unresolved results return (False, []). This intentionally conservative
    function never guesses an ordering of overlapping uncertain intervals.
    Input rows must have design_id and union_hamming_lower_bound/upper_bound.
    """
    rows = list(primary_rows)
    if not rows:
        raise ValueError("At least one primary candidate is required")
    parsed = []
    seen = set()
    for row in rows:
        ident = row["design_id"]
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError("Design IDs must be nonempty unique strings")
        seen.add(ident)
        lower = _distance(row["union_hamming_lower_bound"], "lower bound")
        upper = _distance(row["union_hamming_upper_bound"], "upper bound")
        if lower > upper:
            raise ValueError("Lower bound exceeds upper bound")
        parsed.append((ident, lower, upper))
    if len(parsed) == 1:
        return True, [parsed[0][0]]
    if all(lower == upper for _, lower, upper in parsed):
        best = max(lower for _, lower, _ in parsed)
        return True, sorted(ident for ident, lower, _ in parsed if lower == best)
    for ident, lower, _ in parsed:
        if all(lower > other_upper for other, _, other_upper in parsed if other != ident):
            return True, [ident]
    return False, []
