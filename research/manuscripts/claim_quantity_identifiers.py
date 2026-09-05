"""Recognize identifier spans that are not numerical manuscript quantities."""
import re


_ORCID = re.compile(
    r"(?:\bORCID(?: iD)?\s*:\s*\[?|https?://orcid\.org/)"
    r"(\d{4}-\d{4}-\d{4}-\d{3}[\dX])(?![\dX])", re.IGNORECASE)


def orcid_spans(text):
    """Explicitly labeled/linked ORCID iDs with valid MOD 11-2 checksums.

    This verifies syntax and checksum, not assignment or the author's identity.
    Bare numbers and malformed identifiers are never excluded by this function.
    Algorithm: https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
    """
    spans = []
    for match in _ORCID.finditer(text):
        digits = match.group(1).replace("-", "").upper()
        total = 0
        for digit in digits[:-1]:
            total = (total + int(digit)) * 2
        check = (12 - total % 11) % 11
        if digits[-1] == ("X" if check == 10 else str(check)):
            spans.append(match.span(1))
    return spans
