#!/usr/bin/env python3
"""Turn each committed figure PDF into the two files a print journal's portal accepts: a vector
CMYK **EPS** and a 1200 dpi CMYK **TIFF**.

WHY THIS EXISTS, AND WHY IT IS SEPARATE FROM `svg_to_submission_formats.py`. That script owns the
SVG -> PDF/PNG step and it is the deposit's renderer: dependency-free, offline, driven by the
Chromium that ships with the Playwright bundle. This one owns the last mile to a specific
publisher's checklist. Nucleic Acid Therapeutics asks for figures as "TIFF or EPS, line art
1200 DPI, CMYK not RGB, no Word, PowerPoint or JPEG" (checklist item A8), and none of those four
words describes a PDF or a PNG. So the PDF stays the vector master and this converts it.

⛔⛔ THE FINDING THAT MADE THIS SCRIPT POSSIBLE, AND IT IS A FIGURE DEFECT, NOT A CONVERTER OPTION
(measured 2026-08-25). PostScript has NO transparency model. When an input PDF carries a
transparency group, Ghostscript's `eps2write` cannot translate it and falls back to rendering the
ENTIRE PAGE into one inline image — every rule, every glyph, the lot. Measured on the four ASO
figures before the fix:

    figure                     /Transparency groups   eps2write output
    aso-junction-space                 0              VECTOR, 164 text-showing operators
    aso-multipartner-seam              3              ONE inline image, 0 text operators
    aso-gap-length-tradeoff           39              ONE inline image, 0 text operators
    aso-chance-baseline              136              ONE inline image, 0 text operators

The one figure that never used `opacity=` is the one figure that converted. That is the
discriminating observation, and it is why the fix went into the GENERATORS — see
`aso_figure_text.blend_over_white`, which composites a colour onto white and returns a solid, so
the drawn pixel is unchanged and the transparency group never exists. With that done all four
convert to vector EPS with live text, which this script re-asserts on every run rather than
trusting.

⚠ WHAT "CMYK" HERE IS AND IS NOT. Ghostscript converts through its own ICC profiles and EMBEDS the
CMYK output profile in the TIFF (the file carries a `prtr`/`CMYK`/`Lab` profile header, 187,484
bytes). That is a real, colour-managed, device-CMYK separation — NOT the naive `255 - channel`
inversion a library does when it has no profile. It is nonetheless GHOSTSCRIPT'S default CMYK space
and not the press's: a publisher who separates to their own condition will re-separate, which is
normal and expected. Do not describe these files as matching any named print standard.

⛔ AND ONE HONEST LIMITATION, MEASURED RATHER THAN GUESSED: BLACK TYPE IS A FOUR-COLOUR BUILD.
Sampling the CMYK TIFF of the seam figure, the body type — authored `#111` — separates to
C181 M172 Y170 K210, a total area coverage of 287.5%. It is inside the ~300% most coated stocks
allow, and it is not what a prepress operator would choose for 8 pt type, where any press
misregistration shows as colour fringing. The cause is structural, not a setting: the source is a
browser-written PDF whose text is DeviceRGB, and an ICC conversion of near-black RGB legitimately
lands on a rich black.

⚠ THE ONE SWITCH THAT FIXES IT WAS TESTED AND REFUSED, WITH THE MEASUREMENT THAT REFUSED IT.
`-dBlackText=true -dBlackVector=true` does give C0 M0 Y0 K255 — 100% ink, perfect for type. It also
renders the WHOLE FIGURE neutral: counted over the same page, chromatic samples fall from 46,653 to
**zero**. Every blue donor base, every green acceptor base and the purple divergent box come out
grey. That is not a black-generation option, it is a "draw everything in black" option, and it
would silently destroy the colour coding this figure's own legend describes. `-dUseFastColor=true`
is worse again: C153 M153 Y153 K0, a CMY black with an EMPTY black plate.
★ So the files ship as they are, and the fact is written down here instead of being rediscovered.
If the submission goes out greyscale — which is this deposit's recorded position, since Nucleic
Acid Therapeutics charges for colour and this submission does not request it — `--greyscale-tiff`
sidesteps the whole question: a K-only greyscale TIFF has black type at exactly 100% K by
construction.

⛔ THIS SCRIPT IS IN `regenerate_aso_chain.sh` AS OF 2026-08-25, AND ONLY BECAUSE SOMETHING ELSE
NOW READS ITS OUTPUT. It was deliberately kept out, on an argument that still holds on its own
terms: ghostscript is not present in a fresh sandbox — `command -v gs` fails on the image this
repository develops on — and a chain step most sessions cannot run turns the chain red for everyone
in exchange for files only a submission needs.
★ WHAT CHANGED IS THE READER, NOT THE COST. `SUBMISSION-PACKET.md` now names these files, one per
row, in the upload manifest a depositor reads AT THE PORTAL, and it names them by reading
`print-formats-manifest.json`. A stale manifest therefore puts a stale filename on a checklist
consulted at the moment there is no time to verify it — and a producer whose output is read by
another generated artifact has to be a step of the chain, or the check measures a file nothing
maintains.
⚠ THE OLD OBJECTION IS ANSWERED RATHER THAN OVERRULED, because `--check` needs no ghostscript at
all: it compares recorded hashes against the PDFs on disk. The chain builds where ghostscript
exists and VERIFIES where it does not, so a sandbox that changed no figure stays green and one that
changed a figure goes red — which is true, not incidental. Install it with
`apt-get install -y ghostscript`; the GitHub Actions Ubuntu runner can do the same in one step.

DETERMINISM. Ghostscript stamps the wall clock into the EPS `%%CreationDate` comment and into the
TIFF `DateTime` tag (306). Both are overwritten in place with a fixed timestamp of IDENTICAL byte
length, so offsets stay valid and two runs over unchanged inputs produce byte-identical files —
which is what lets `git status` mean "the figure really changed". Measured before the fix: two
consecutive runs differed in exactly one byte of the TIFF and one line of the EPS, both the clock.
Set `SOURCE_DATE_EPOCH` to choose the stamp.

    python3 research/manuscripts/figures/svg_to_print_formats.py             # all four ASO figures
    python3 research/manuscripts/figures/svg_to_print_formats.py --check     # verify, write nothing
    python3 research/manuscripts/figures/svg_to_print_formats.py --only aso-multipartner-seam
    python3 research/manuscripts/figures/svg_to_print_formats.py --dpi 600 --greyscale-proof
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "submission")
PROOFDIR = os.path.join(OUTDIR, "greyscale-proof")
MANIFEST = os.path.join(OUTDIR, "print-formats-manifest.json")

#: The figures this deposit submits, in manuscript order. Named rather than globbed for the same
#: reason `svg_to_submission_formats.ASO_FIGURES` is: this directory also holds figures belonging
#: to four other papers, and converting those would put files nobody asked for into a submission
#: folder. ⚠ THE JOURNAL ARTICLE SHIPS ONLY THE SEAM PANEL — `build_submission_pdf.py` maps it as
#: that paper's Figure 1 — while the research article ships all four. Both come from this list.
ASO_FIGURES = [
    "aso-junction-space",
    "aso-multipartner-seam",
    "aso-gap-length-tradeoff",
    "aso-chance-baseline",
]

#: Nucleic Acid Therapeutics checklist A8: "Line art 1200 DPI". Combination art is usually allowed
#: at 600, and these panels are line art plus flat colour fills, so 1200 clears the strictest
#: reading of the row. The cost is size, not time: the seam figure renders in about five seconds.
DEFAULT_DPI = 1200
PROOF_DPI = 150

#: Same fixed instant `svg_to_submission_formats.FIXED_PDF_DATE` uses, in the two shapes Ghostscript
#: writes. The value is arbitrary; that it never moves is the point. Both must keep their exact
#: byte length, because they are overwritten in place.
FIXED_EPS_DATE = "D:20000101000000Z00'00'"
FIXED_TIFF_DATE = "2000:01:01 00:00:00"

_TIFF_TAGS = {256: "ImageWidth", 257: "ImageLength", 258: "BitsPerSample",
              259: "Compression", 262: "PhotometricInterpretation", 277: "SamplesPerPixel",
              282: "XResolution", 283: "YResolution", 296: "ResolutionUnit", 306: "DateTime",
              34675: "ICCProfile"}
_PHOTOMETRIC = {0: "WhiteIsZero", 1: "BlackIsZero", 2: "RGB", 3: "Palette", 5: "Separated (CMYK)"}


def _gs():
    """The Ghostscript binary, or a refusal that names the fix.

    ⛔ NOT A SILENT SKIP. A converter that returns success having produced nothing is how a
    submission folder ends up holding yesterday's files; this repository has shipped a fail-quiet
    guard before and the rule since is that an absent tool is a finding.
    """
    for name in ("gs", "ghostscript", "gsc"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit(
        "⛔ Ghostscript is not installed, and it is the only offline path from PDF to EPS and to a\n"
        "   colour-managed CMYK TIFF that this environment has. Measured on this image: no\n"
        "   inkscape, no rsvg-convert, no pdftops, no cairosvg, no ImageMagick.\n"
        "   Install it and re-run:  apt-get install -y ghostscript\n"
        "   (The GitHub Actions Ubuntu runner takes the same line as a workflow step.)")


def _fixed_timestamp():
    stamp = os.environ.get("SOURCE_DATE_EPOCH")
    if not stamp:
        return FIXED_EPS_DATE, FIXED_TIFF_DATE
    t = time.gmtime(int(stamp))
    return (time.strftime("D:%Y%m%d%H%M%SZ00'00'", t), time.strftime("%Y:%m:%d %H:%M:%S", t))


def _destamp(path):
    """Overwrite Ghostscript's wall-clock stamps with a fixed one of the same byte length."""
    eps_date, tiff_date = _fixed_timestamp()
    data = open(path, "rb").read()
    before = data
    data = re.sub(rb"D:\d{14}Z00'00'", eps_date.encode(), data)
    data = re.sub(rb"\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}", tiff_date.encode(), data)
    assert len(data) == len(before), "de-stamping changed the file length; offsets are now invalid"
    if data != before:
        open(path, "wb").write(data)


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _run(argv):
    proc = subprocess.run(argv, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"⛔ {argv[0]} failed ({proc.returncode})\n"
                         f"   {' '.join(argv[1:])}\n{proc.stdout}\n{proc.stderr}")
    return proc


# --------------------------------------------------------------------------------------------
# verification — stdlib only, for the same reason tests/test_aso_figures_are_vector_not_raster.py
# is: pypdf, pikepdf and PIL are all absent from a fresh sandbox, and a check that skips when its
# parser is missing is a check that reports green on a broken file.
# --------------------------------------------------------------------------------------------

#: A text-showing operator inside a content stream, matched on its OPERAND so that two bytes of
#: entropy inside a compressed blob cannot stand in for one. Same shape as the PDF guard's.
_SHOW_TEXT = re.compile(rb"(?:\)|>|\])\s*T[Jj][\s\[<(/]")
#: An inline image. `eps2write`'s whole-page fallback emits exactly one of these and nothing else.
_INLINE_IMAGE = re.compile(rb"\bBI\b[^\n]*\n(?:[^\n]*\n){0,12}?\s*ID\b")


def _svg_label_count(stem):
    """How many non-blank `<text>` nodes the SVG draws — the floor the EPS must clear.

    Derived from the sibling artifact, never typed, so a figure that gains or loses labels moves
    its own floor. Identical in spirit to the PDF guard, which is what makes the two comparable.
    """
    svg = os.path.join(HERE, f"{stem}.svg")
    if not os.path.exists(svg):
        raise SystemExit(f"⛔ {stem}.svg is missing; the EPS is converted from its PDF and its "
                         f"label floor cannot be derived")
    text = open(svg, encoding="utf-8").read()
    return len([t for t in re.findall(r"<text\b[^>]*>([^<]*)</text>", text) if t.strip()])


def verify_eps(path, stem):
    """Assert the EPS is vector, carries live text, and is separated to CMYK.

    ⛔ THIS IS THE ASSERTION THE WHOLE SCRIPT EXISTS FOR. `eps2write` succeeds, exits zero and
    writes a plausible 600 KB file whether it translated the page or photographed it. The only
    difference visible from outside is in the content: an operator count against a label count.
    """
    body = open(path, "rb").read()
    end = body.find(b"%%EndProlog")
    content = body[end:] if end >= 0 else body

    images = _INLINE_IMAGE.findall(content) + re.findall(rb"/Subtype\s*/Image", content)
    show = _SHOW_TEXT.findall(content)
    labels = _svg_label_count(stem)
    cmyk = re.findall(rb"[\d.]+ [\d.]+ [\d.]+ [\d.]+ (?:k|K)\b", content) \
        + re.findall(rb"\bsetcmykcolor\b", content)
    rgb = re.findall(rb"[\d.]+ [\d.]+ [\d.]+ (?:rg|RG)\b", content) \
        + re.findall(rb"\bsetrgbcolor\b", content)

    if images:
        raise SystemExit(
            f"⛔ {os.path.basename(path)} is a PICTURE of the figure: {len(images)} embedded "
            f"image(s) and {len(show)} text operator(s).\n"
            f"   The cause is almost always a transparency group in the source PDF, which "
            f"PostScript cannot express, so Ghostscript rasterises the whole page.\n"
            f"   Look for `opacity=` or `fill-opacity=` in {stem}.svg and route the colour through "
            f"`aso_figure_text.blend_over_white` in its generator. Do NOT relax this check: a "
            f"raster EPS cannot be re-typeset, cannot be searched, and prints at whatever "
            f"resolution it happened to be rendered at.")
    if len(show) < labels:
        raise SystemExit(
            f"⛔ {os.path.basename(path)} carries {len(show)} text-showing operator(s) against "
            f"{labels} non-blank <text> node(s) in {stem}.svg. Glyphs were outlined or labels were "
            f"lost; either way the figure is unsearchable and a journal cannot re-set its type.")
    if rgb:
        raise SystemExit(f"⛔ {os.path.basename(path)} still emits {len(rgb)} RGB colour "
                         f"operator(s); checklist A8 asks for CMYK, not RGB.")
    if not cmyk:
        raise SystemExit(f"⛔ {os.path.basename(path)} emits no CMYK colour operator at all — the "
                         f"colour conversion did not run.")
    return {"text_operators": len(show), "svg_labels": labels,
            "cmyk_operators": len(cmyk), "rgb_operators": len(rgb), "embedded_images": 0}


def _tiff_ifd(path):
    """The first IFD of a TIFF, as {tag name: value}. Baseline TIFF only; no library.

    ⚠ PRESENCE IS NOT PROVENANCE (CLAUDE.md §4). This reads what the file HEADER says, which is
    the same class of claim `check_figure_specs.py` warns about for PNG `pHYs`: it records the
    resolution the pixels were authored for. The DETAIL is carried by the pixel COUNT, so the
    caller cross-checks width against `dpi x physical width` and fails if they disagree — that is
    what makes a 1200 dpi label a measurement rather than an assertion.
    """
    raw = open(path, "rb").read()
    if raw[:2] == b"II":
        end = "<"
    elif raw[:2] == b"MM":
        end = ">"
    else:
        raise SystemExit(f"⛔ {path} is not a TIFF (magic {raw[:4]!r})")
    (magic,) = struct.unpack(end + "H", raw[2:4])
    if magic != 42:
        raise SystemExit(f"⛔ {path}: TIFF magic is {magic}, expected 42 (BigTIFF is not parsed)")
    (offset,) = struct.unpack(end + "I", raw[4:8])
    (count,) = struct.unpack(end + "H", raw[offset:offset + 2])
    sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}
    out = {}
    for i in range(count):
        at = offset + 2 + i * 12
        tag, typ, n = struct.unpack(end + "HHI", raw[at:at + 8])
        payload = raw[at + 8:at + 12]
        nbytes = sizes.get(typ, 1) * n
        if nbytes > 4:
            (where,) = struct.unpack(end + "I", payload)
            payload = raw[where:where + nbytes]
        name = _TIFF_TAGS.get(tag)
        if name is None:
            continue
        if typ == 3:
            out[name] = struct.unpack(end + "H", payload[:2])[0] if n == 1 else \
                list(struct.unpack(end + f"{n}H", payload[:2 * n]))
        elif typ == 4:
            out[name] = struct.unpack(end + "I", payload[:4])[0]
        elif typ == 5:
            num, den = struct.unpack(end + "II", payload[:8])
            out[name] = num / den if den else 0
        elif typ == 2:
            out[name] = payload.split(b"\0")[0].decode("ascii", "replace")
        else:
            out[name] = f"<{n} bytes, type {typ}>"
        if name == "ICCProfile":
            out[name] = nbytes
    return out


def verify_tiff(path, dpi, width_pt, greyscale=False):
    """Assert the TIFF is CMYK (or K-only grey), at the dpi claimed, and that its PIXELS back it."""
    ifd = _tiff_ifd(path)
    photometric = ifd.get("PhotometricInterpretation")
    want, samples = ((1, 1) if greyscale else (5, 4))
    if photometric != want:
        raise SystemExit(
            f"⛔ {os.path.basename(path)} is {_PHOTOMETRIC.get(photometric, photometric)}, not "
            f"{_PHOTOMETRIC[want]}. Checklist A8 asks for CMYK, not RGB.")
    if ifd.get("SamplesPerPixel") != samples:
        raise SystemExit(f"⛔ {os.path.basename(path)} has "
                         f"{ifd.get('SamplesPerPixel')} samples per pixel; expected {samples}.")
    if ifd.get("ResolutionUnit") != 2 or round(ifd.get("XResolution", 0)) != dpi:
        raise SystemExit(f"⛔ {os.path.basename(path)} declares "
                         f"{ifd.get('XResolution')} per unit {ifd.get('ResolutionUnit')}, "
                         f"not {dpi} per inch.")
    #: ⛔ THE HEADER IS NOT THE MEASUREMENT. A resolution tag can be written onto any raster; what
    #: cannot be faked is the pixel count. `width_pt` is the PDF's own MediaBox, so this asserts
    #: the file really was RENDERED at the resolution it advertises, which is exactly the failure
    #: `check_figure_specs.py`'s docstring names — "REGENERATE at 300, do not relabel".
    expected = round(width_pt / 72.0 * dpi)
    if abs(ifd.get("ImageWidth", 0) - expected) > 2:
        raise SystemExit(
            f"⛔ {os.path.basename(path)} is {ifd.get('ImageWidth')} px wide but a "
            f"{width_pt:.2f} pt page at {dpi} dpi is {expected} px. The header claims detail the "
            f"pixels do not carry — re-render, never relabel.")
    return {"photometric": _PHOTOMETRIC.get(photometric), "samples_per_pixel": samples,
            "dpi": round(ifd.get("XResolution", 0)), "pixels": [ifd.get("ImageWidth"),
                                                                ifd.get("ImageLength")],
            "icc_profile_bytes": ifd.get("ICCProfile", 0),
            "compression": ifd.get("Compression")}


def _media_box(pdf):
    """Page width and height in points, read from the PDF's MediaBox."""
    raw = open(pdf, "rb").read()
    m = re.search(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)", raw)
    if not m:
        raise SystemExit(f"⛔ {pdf} declares no /MediaBox, so its physical size is unknown")
    x0, y0, x1, y1 = (float(v) for v in m.groups())
    return x1 - x0, y1 - y0


def convert(stem, dpi, greyscale_proof, check_only, greyscale_tiff=False):
    gs = _gs()
    pdf = os.path.join(HERE, f"{stem}.pdf")
    if not os.path.exists(pdf):
        raise SystemExit(f"⛔ {stem}.pdf is missing. Run svg_to_submission_formats.py first — the "
                         f"PDF is this script's input, not the SVG.")
    width_pt, height_pt = _media_box(pdf)
    eps = os.path.join(OUTDIR, f"{stem}.eps")
    tif = os.path.join(OUTDIR, f"{stem}.tif")
    #: ⛔ THE DEVICE IS THE ONLY DIFFERENCE, AND IT IS A REAL ONE. `tiffgray` renders straight to a
    #: single K channel, so black type lands at 100% K rather than the 287% four-colour build the
    #: CMYK route produces (see the module docstring). Use it when the submission is greyscale.
    device = "tiffgray" if greyscale_tiff else "tiff32nc"

    if not check_only:
        os.makedirs(OUTDIR, exist_ok=True)
        #: ⚠ `-dEPSCrop` takes the bounding box from the PDF's MediaBox rather than from the ink,
        #: so the EPS keeps the same 180 mm measure every other deliverable of this figure has.
        _run([gs, "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=eps2write", "-dEPSCrop",
              "-dColorConversionStrategy=/CMYK", f"-sOutputFile={eps}", pdf])
        #: `tiff32nc` is the 32-bit CMYK TIFF device; `-sCompression=lzw` is lossless, which JPEG
        #: would not be — and checklist A8 names JPEG as unacceptable, for exactly that reason.
        _run([gs, "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", f"-sDEVICE={device}", f"-r{dpi}",
              "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4", "-sCompression=lzw",
              f"-sOutputFile={tif}", pdf])
        _destamp(eps)
        _destamp(tif)
        if greyscale_proof:
            #: ⛔ THE PROOF IS RENDERED BY THE SAME ENGINE, NOT DESATURATED BY EYE. Checklist A10
            #: says colour is author-subsidised, so unless colour reproduction is bought the
            #: PRINTED figure is this file and not the one above it. `pnggray` is Ghostscript's
            #: own luminance conversion, which is the transform a press-side workflow applies.
            #: ⚠ NOT A SUBMISSION FILE. It lives in its own directory and is named a proof so it
            #: cannot be uploaded by mistake.
            os.makedirs(PROOFDIR, exist_ok=True)
            _run([gs, "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=pnggray",
                  f"-r{PROOF_DPI}", "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
                  f"-sOutputFile={os.path.join(PROOFDIR, stem + '-greyscale-proof.png')}", pdf])

    for path in (eps, tif):
        if not os.path.exists(path):
            raise SystemExit(f"⛔ {os.path.basename(path)} is missing from {OUTDIR}. Run this "
                             f"script without --check to build it.")
    record = {
        "source_pdf": f"{stem}.pdf",
        "source_pdf_sha256": _sha(pdf),
        "source_svg_sha256": _sha(os.path.join(HERE, f"{stem}.svg")),
        "page_pt": [round(width_pt, 2), round(height_pt, 2)],
        "page_mm": [round(width_pt * 25.4 / 72, 2), round(height_pt * 25.4 / 72, 2)],
        "eps": {"file": f"{stem}.eps", "bytes": os.path.getsize(eps), "sha256": _sha(eps),
                **verify_eps(eps, stem)},
        "tiff": {"file": f"{stem}.tif", "bytes": os.path.getsize(tif), "sha256": _sha(tif),
                 **verify_tiff(tif, dpi, width_pt, greyscale_tiff)},
    }
    return record


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", action="append", metavar="STEM",
                    help="convert just this figure (repeatable)")
    ap.add_argument("--dpi", type=int, default=DEFAULT_DPI,
                    help=f"TIFF resolution (default {DEFAULT_DPI}, the A8 line-art figure)")
    ap.add_argument("--greyscale-proof", action="store_true", default=True,
                    help="also write a greyscale proof PNG (default on; see checklist A10)")
    ap.add_argument("--no-greyscale-proof", dest="greyscale_proof", action="store_false")
    ap.add_argument("--greyscale-tiff", action="store_true",
                    help="write the TIFF as K-only greyscale instead of CMYK. Use when the "
                         "submission does not buy colour reproduction: black type then separates "
                         "at 100% K instead of a 287% four-colour build (see the module docstring)")
    ap.add_argument("--check", action="store_true",
                    help="verify what is already on disk and re-check the manifest; write nothing")
    args = ap.parse_args(argv)

    stems = args.only or ASO_FIGURES
    unknown = [s for s in stems if s not in ASO_FIGURES]
    if unknown:
        raise SystemExit(f"⛔ not an ASO submission figure: {', '.join(unknown)}. "
                         f"Known: {', '.join(ASO_FIGURES)}")

    records = {}
    for stem in stems:
        records[stem] = convert(stem, args.dpi, args.greyscale_proof, args.check,
                                args.greyscale_tiff)
        r = records[stem]
        print(f"{stem}")
        print(f"  EPS   {r['eps']['bytes']:>10,} B  vector, {r['eps']['text_operators']:>4} text "
              f"op(s) over {r['eps']['svg_labels']} label(s), {r['eps']['cmyk_operators']} CMYK "
              f"op(s), {r['eps']['rgb_operators']} RGB")
        print(f"  TIFF  {r['tiff']['bytes']:>10,} B  {r['tiff']['photometric']}, "
              f"{r['tiff']['dpi']} dpi, {r['tiff']['pixels'][0]} x {r['tiff']['pixels'][1]} px, "
              f"ICC {r['tiff']['icc_profile_bytes']:,} B")

    if args.check:
        if not os.path.exists(MANIFEST):
            raise SystemExit(f"⛔ {os.path.basename(MANIFEST)} is missing; nothing pins these "
                             f"deliverables to the figures they were made from")
        old = json.load(open(MANIFEST, encoding="utf-8"))["figures"]
        stale = [s for s in stems
                 if old.get(s, {}).get("source_pdf_sha256") != records[s]["source_pdf_sha256"]]
        if stale:
            raise SystemExit(
                f"⛔ the print deliverables for {', '.join(stale)} were built from a different "
                f"PDF than the one on disk. Re-run this script without --check.")
        print(f"\n--check: {len(stems)} figure(s) verified against {os.path.basename(MANIFEST)}")
        return 0

    os.makedirs(OUTDIR, exist_ok=True)
    payload = {
        "_what": "the EPS and TIFF deliverables for Nucleic Acid Therapeutics checklist A8, and "
                 "the hash of the figure PDF each was built from",
        "_why": "nothing else ties a submission file to the figure it depicts. --check compares "
                "these hashes against the PDFs on disk and refuses a stale deliverable.",
        "_regenerate": "python3 research/manuscripts/figures/svg_to_print_formats.py",
        "_requires": "ghostscript (apt-get install -y ghostscript); absent from a fresh sandbox, "
                     "so scripts/regenerate_aso_chain.sh builds this step where ghostscript "
                     "exists and runs --check where it does not, which needs none",
        "_colour": "Ghostscript's default CMYK ICC profile, embedded in each TIFF. A real "
                   "colour-managed separation with black generation, not a naive inversion — but "
                   "not any named press condition either, so a publisher may re-separate.",
        "dpi": args.dpi,
        "tiff_colour_space": "K-only greyscale" if args.greyscale_tiff else "DeviceCMYK",
        "ghostscript": _run([_gs(), "--version"]).stdout.strip(),
        "figures": records,
    }
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
        fh.write("\n")
    total = sum(r["eps"]["bytes"] + r["tiff"]["bytes"] for r in records.values())
    print(f"\nwrote {2 * len(records)} deliverable(s) for {len(records)} figure(s) "
          f"into {os.path.relpath(OUTDIR, os.path.dirname(os.path.dirname(os.path.dirname(HERE))))}"
          f"  ({total / 1e6:.1f} MB total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
