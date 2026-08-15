#!/usr/bin/env python3
"""Render a submission manuscript from Markdown into ONE submission-ready PDF.

WHY. The ASO paper was preprint-ready by its own checklist and had no PDF, because the thing a
depositor uploads is not the thing this repository stores. The manuscript is one file, its tables
are a second generated file, its references a third, and its figures are three SVGs that the
manuscript refers to by legend and never embeds. Every venue in the plan — bioRxiv first — wants a
single document. Assembling that by hand at deposit time is exactly the re-derivation CLAUDE.md
rule 1 exists to stop, and it is where a stale table or a dropped reference gets in.

WHAT IT DOES NOT DO. It does not edit the manuscript, and it does not compute anything the
manuscript claims. Tables and references are spliced in from their generated files verbatim, so a
number in this PDF and a number in the artifact it came from cannot diverge without the generator
being wrong first. The repo's own YAML frontmatter — id, level, canonical_for, purpose, audience —
is internal routing and is stripped: it is not part of what a reviewer reads.

⛔ THE SPLICE IS ANCHORED, NOT POSITIONAL. Each insert is located by its section heading and its
pointer paragraph, and a missing anchor is a hard failure rather than a silent no-op — a PDF that
quietly lost its reference list looks exactly like one that has it until somebody opens page 30.

⚠ NO NETWORK, NO PANDOC, NO LATEX. Rendering is Chromium's own print-to-PDF over a file:// page,
which is present in this container; figures are inlined as SVG markup so they stay VECTOR in the
output rather than being rasterised. build-preprint.yml remains the pandoc/DOCX route for venues
that want an editable file; this is the PDF route and it needs nothing installed.

    python3 research/manuscripts/build_submission_pdf.py                # build every paper listed
    python3 research/manuscripts/build_submission_pdf.py --paper aso    # build one
    python3 research/manuscripts/build_submission_pdf.py --html-only    # skip the browser
"""
import argparse
import base64
import html as _html
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIGDIR = os.path.join(HERE, "figures")

#: One entry per manuscript that has a submission form. `figures` maps the legend prefix the
#: manuscript actually uses to the SVG that legend describes — the pairing is stated here rather
#: than inferred from filename order, because `aso_figure_provenance.py` is explicit that nothing
#: checks whether a legend describes its figure, and a silent mis-pairing is unreadable in a PDF.
PAPERS = {
    "aso": {
        "manuscript": "aso/fusion-junction-aso-short-communication.md",
        "tables": "aso/fusion-junction-aso-submission-tables.md",
        "references": "aso/fusion-junction-aso-submission-references.md",
        "figures": {
            "Figure 1.": "aso-junction-space.svg",
            "Figure 2.": "aso-multipartner-seam.svg",
            "Figure 3.": "aso-chance-baseline.svg",
        },
        "out": "aso/fusion-junction-aso-short-communication.pdf",
    },
}


# --------------------------------------------------------------------------- assembly

def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def strip_frontmatter(text):
    """Drop a leading YAML block. Repo frontmatter is routing metadata, not manuscript."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end != -1:
            return text[end + 5:]
    return text


def strip_generated_banner(text):
    """Drop the leading HTML comment and the H1 from a generated include."""
    text = re.sub(r"^<!--.*?-->\s*", "", text, flags=re.S)
    return re.sub(r"^#\s+[^\n]*\n", "", text.lstrip(), count=1).strip()


def splice(body, heading, replacement, label):
    """Replace the pointer paragraph under `heading` with `replacement`.

    The pointer is everything between the heading and the next `## ` heading (or end of file).
    Anchored on the heading text; absence is fatal, so a renamed section fails the build instead
    of producing a PDF with a section that says 'the tables are in another file'.
    """
    pattern = re.compile(r"(^##\s+" + re.escape(heading) + r"\s*$)(.*?)(?=^##\s|\Z)",
                         re.M | re.S)
    match = pattern.search(body)
    if not match:
        raise SystemExit(f"anchor not found: '## {heading}' ({label}) — the manuscript's section "
                         f"headings changed, so the splice would have silently dropped {label}")
    return body[:match.end(1)] + "\n\n" + replacement + "\n\n" + body[match.end(2):]


def inline_figures(body, figures):
    """Put each figure immediately above the legend that describes it.

    Anchored on the bolded legend opener (`**Figure 1. …`). A legend with no figure, or a figure
    with no legend, is a build failure: an unlabelled panel in a submission PDF is worse than none.
    """
    for prefix, svgname in figures.items():
        svg = open(os.path.join(FIGDIR, svgname), encoding="utf-8").read().strip()
        anchor = "**" + prefix
        if anchor not in body:
            raise SystemExit(f"no legend found for {svgname}: expected a paragraph opening '{anchor}'")
        block = f'\n<figure class="figure">\n{svg}\n</figure>\n\n'
        body = body.replace(anchor, block + anchor, 1)
    return body


def assemble(paper):
    body = strip_frontmatter(read(paper["manuscript"]))
    body = splice(body, "Tables", strip_generated_banner(read(paper["tables"])), "the tables")
    body = splice(body, "References", strip_generated_banner(read(paper["references"])),
                  "the reference list")
    body = inline_figures(body, paper["figures"])
    return body


# --------------------------------------------------------------------------- markdown

#: Raw inline tags the manuscripts genuinely use and that must survive escaping. `<sup>` carries
#: every citation marker; `<i>`/`<b>` arrive from PubMed titles that were stored with their markup
#: entity-escaped, and are unescaped below so a title renders as italic rather than showing tags.
KEEP_TAGS = ("sup", "sub", "i", "em", "b", "strong")
TAG_RE = re.compile(r"</?(?:" + "|".join(KEEP_TAGS) + r")>", re.I)


def escape_text(text):
    """HTML-escape everything except the small whitelist of inline tags above."""
    out, last = [], 0
    for m in TAG_RE.finditer(text):
        out.append(_html.escape(text[last:m.start()], quote=False))
        out.append(m.group(0).lower())
        last = m.end()
    out.append(_html.escape(text[last:], quote=False))
    return "".join(out)


def inline(text):
    """Inline markdown. Code spans are protected first so their contents are never re-parsed."""
    text = _html.unescape(text)
    stash = []

    def keep(fragment):
        stash.append(fragment)
        return f"\x00{len(stash) - 1}\x00"

    text = re.sub(r"`([^`]+)`",
                  lambda m: keep("<code>" + _html.escape(m.group(1), quote=False) + "</code>"),
                  text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: keep('<a href="' + _html.escape(m.group(2), quote=True) + '">'
                                 + escape_text(m.group(1)) + "</a>"),
                  text)
    text = escape_text(text)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text, flags=re.S)
    text = re.sub(r"(?<!\*)\*(?=\S)([^*]+?)(?<=\S)\*(?!\*)", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)


def render_table(rows):
    """A GitHub pipe table. Row 2 is the alignment rule and carries no content."""
    def cells(line):
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [c.strip() for c in line.split("|")]

    head, body = cells(rows[0]), [cells(r) for r in rows[2:]]
    out = ['<div class="tablewrap"><table>', "<thead><tr>"]
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def markdown_to_html(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)          # PMID markers etc: non-rendering
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("<figure") or stripped.startswith("</figure"):
            out.append(stripped)
            i += 1
            continue
        if stripped.startswith("<svg") or out[-1:] == ["<figure class=\"figure\">"]:
            # An inlined figure: pass its markup through untouched until the closing tag.
            block = []
            while i < len(lines) and not lines[i].strip().startswith("</figure"):
                block.append(lines[i])
                i += 1
            out.append("\n".join(block))
            continue

        if re.match(r"^-{3,}$", stripped):
            out.append("<hr/>")
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and re.match(
                r"^\|[\s:|-]+\|?\s*$", lines[i + 1].strip()):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(render_table(rows))
            continue

        item = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if item:
            ordered = item.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            start = re.match(r"^\s*(\d+)\.", line)
            attr = f' start="{start.group(1)}"' if ordered and start else ""
            out.append(f"<{tag}{attr}>")
            while i < len(lines):
                m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if not m:
                    if lines[i].strip() and lines[i].startswith((" ", "\t")):
                        out[-1] = out[-1][:-5] + " " + inline(lines[i].strip()) + "</li>"
                        i += 1
                        continue
                    break
                out.append("<li>" + inline(m.group(3)) + "</li>")
                i += 1
            out.append(f"</{tag}>")
            continue

        para = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,6}\s|\||-{3,}$|\s*([-*]|\d+\.)\s|<figure|<svg)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        if para:
            joined = " ".join(para)
            css = ' class="legend"' if re.match(r"^\*\*Figure \d+\.", joined) else ""
            out.append(f"<p{css}>{inline(joined)}</p>")
        else:
            i += 1
    return "\n".join(out)


# --------------------------------------------------------------------------- page

CSS = """
@page { size: A4; margin: 20mm 18mm 18mm 18mm; }
@page landscape { size: A4 landscape; margin: 16mm 14mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
/* Times-metric serif, named in the order that makes the build deterministic on this container
   (Liberation Serif is what is installed) while still resolving sensibly elsewhere. */
body { font-family: 'Liberation Serif', 'Times New Roman', Times, serif; font-size: 10.5pt;
       line-height: 1.5; color: #111; margin: 0; hyphens: auto; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 14pt 0; font-weight: 600; }
h2 { font-size: 13pt; margin: 20pt 0 6pt 0; font-weight: 600;
     border-bottom: 0.5pt solid #ccc; padding-bottom: 3pt; break-after: avoid; }
h3 { font-size: 11pt; margin: 14pt 0 4pt 0; font-weight: 600; break-after: avoid; }
p { margin: 0 0 8pt 0; text-align: justify; }
hr { border: 0; border-top: 0.5pt solid #ddd; margin: 14pt 0; }
sup { font-size: 0.72em; line-height: 0; }
code { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 0.86em;
       background: #f4f4f4; padding: 0 2px; border-radius: 2px; word-break: break-all; }
a { color: #14507d; text-decoration: none; }
ol, ul { margin: 0 0 8pt 0; padding-left: 18pt; }
li { margin-bottom: 4pt; text-align: justify; }

/* The reference list: hanging indent, and it must not be justified into rivers. */
#references-list li { text-align: left; }

/* Tables MUST be allowed to break. Table 2 is 38 rows deep and taller than any page, so
   `break-inside: avoid` does not keep it together — it pushes it whole onto the next page, which
   left one page blank and clipped the overflow. Rows are kept intact instead, and the header is a
   table-header-group so it repeats on every page the table spans. */
.tablewrap { break-inside: auto; margin: 0 0 12pt 0; }
table { border-collapse: collapse; width: 100%; font-size: 7.4pt; font-family: Helvetica, Arial,
        sans-serif; line-height: 1.3; table-layout: auto; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th, td { border: 0.4pt solid #b8b8b8; padding: 2.5pt 3.5pt; text-align: left;
         vertical-align: top; overflow-wrap: anywhere; }
th { background: #eef1f4; font-weight: 600; }
tbody tr:nth-child(even) { background: #fafbfc; }

/* One figure per page, with its legend. Figure 1 is 760x1509 and is TALLER than a page at full
   width, so without a height cap it split across two pages mid-panel. The cap leaves room for the
   legend, which must stay on the same page as the panel it describes. */
figure.figure { margin: 0 0 6pt 0; text-align: center; break-inside: avoid; break-before: page; }
figure.figure svg { max-width: 100%; max-height: 218mm; width: auto; height: auto; }
p.legend { font-size: 9pt; text-align: left; margin-bottom: 16pt; break-before: avoid;
           break-inside: avoid; }

/* Tables 1-6 are up to twelve columns wide and are unreadable in portrait. */
section.landscape { page: landscape; }
section.landscape table { font-size: 7.6pt; }
"""


def wrap_html(title, body_html):
    """Put the tables section on landscape pages and give the reference list its own id."""
    body_html = re.sub(
        r"(<h2>Tables</h2>)(.*?)(?=<h2>)",
        lambda m: '<section class="landscape">' + m.group(1) + m.group(2) + "</section>",
        body_html, count=1, flags=re.S)
    # The generated include opens with a note paragraph, so the list is not adjacent to the
    # heading — match the FIRST <ol> after it rather than an immediately-following one.
    body_html = re.sub(r"(<h2>References</h2>.*?)<ol", r'\1<ol id="references-list"',
                       body_html, count=1, flags=re.S)
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"/>"
            f"<title>{_html.escape(title)}</title><style>{CSS}</style></head>"
            f"<body>\n{body_html}\n</body></html>\n")


# --------------------------------------------------------------------------- chromium

def find_chrome():
    for candidate in (
        os.path.join(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"),
                     "chromium-1194", "chrome-linux", "chrome"),
        "/opt/pw-browsers/chromium/chrome-linux/chrome",
    ):
        if os.path.exists(candidate):
            return candidate
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    import glob
    hits = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    return hits[0] if hits else None


class WS:
    """The smallest RFC6455 client that can carry one printToPDF response.

    Chromium's CLI --print-to-pdf cannot set a footer, so page numbers need DevTools. The response
    is a megabyte of base64 and arrives fragmented, which is the only reason this handles
    continuation frames and 64-bit lengths at all.
    """

    def __init__(self, url):
        _, rest = url.split("://", 1)
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.sock = socket.create_connection((host, int(port)), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((
            f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
            f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self.next_id = 0

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("devtools socket closed mid-frame")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        payload = b""
        while True:
            b0, b1 = self._read(2)
            length = b1 & 0x7F
            if length == 126:
                length = struct.unpack(">H", self._read(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._read(8))[0]
            payload += self._read(length)
            if b0 & 0x80:                                   # FIN
                return json.loads(payload.decode("utf-8"))

    def call(self, method, **params):
        self.next_id += 1
        msg = json.dumps({"id": self.next_id, "method": method, "params": params}).encode()
        mask = os.urandom(4)
        header = bytes([0x81])
        if len(msg) < 126:
            header += bytes([0x80 | len(msg)])
        elif len(msg) < 65536:
            header += bytes([0x80 | 126]) + struct.pack(">H", len(msg))
        else:
            header += bytes([0x80 | 127]) + struct.pack(">Q", len(msg))
        self.sock.sendall(header + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(msg)))
        while True:
            frame = self.recv()
            if frame.get("id") == self.next_id:
                if "error" in frame:
                    raise RuntimeError(f"{method}: {frame['error']}")
                return frame.get("result", {})


FOOTER = ('<div style="font-size:8px;font-family:Georgia,serif;color:#666;width:100%;'
          'text-align:center;padding-top:4px;">'
          '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')


def print_pdf(chrome, html_path, pdf_path):
    profile = tempfile.mkdtemp(prefix="ccpdf-")
    proc = subprocess.Popen(
        [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-first-run",
         f"--user-data-dir={profile}", "--remote-debugging-port=0", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        portfile = os.path.join(profile, "DevToolsActivePort")
        deadline = time.time() + 45
        port = None
        while time.time() < deadline:
            if os.path.exists(portfile):
                content = open(portfile).read().split("\n")
                if len(content) >= 2:
                    port = content[0].strip()
                    break
            time.sleep(0.2)
        if not port:
            raise RuntimeError("chromium never reported a devtools port")

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=30) as resp:
            targets = json.load(resp)
        ws_url = next(t["webSocketDebuggerUrl"] for t in targets if t.get("type") == "page")

        ws = WS(ws_url)
        ws.call("Page.enable")
        ws.call("Page.navigate", url="file://" + os.path.abspath(html_path))
        # The page is local and has no external resources; a short settle is enough for layout.
        time.sleep(2.5)
        result = ws.call(
            "Page.printToPDF",
            printBackground=True,
            preferCSSPageSize=True,
            displayHeaderFooter=True,
            headerTemplate="<div></div>",
            footerTemplate=FOOTER,
        )
        with open(pdf_path, "wb") as fh:
            fh.write(base64.b64decode(result["data"]))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


# --------------------------------------------------------------------------- driver

def title_of(body):
    match = re.search(r"^#\s+(.*)$", body, re.M)
    return re.sub(r"[*_`]", "", match.group(1)) if match else "Manuscript"


def build(name, paper, html_only=False):
    body = assemble(paper)
    page = wrap_html(title_of(body), markdown_to_html(body))
    html_path = os.path.join(HERE, paper["out"].replace(".pdf", ".build.html"))
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    pdf_path = os.path.join(HERE, paper["out"])

    if html_only:
        print(f"{name}: wrote {os.path.relpath(html_path, REPO)} (--html-only, no PDF)")
        return 0

    chrome = find_chrome()
    if not chrome:
        print(f"{name}: no chromium found; HTML is at {os.path.relpath(html_path, REPO)}",
              file=sys.stderr)
        return 1
    print_pdf(chrome, html_path, pdf_path)
    os.remove(html_path)
    size = os.path.getsize(pdf_path)
    pages = open(pdf_path, "rb").read().count(b"/Type /Page\n") or None
    print(f"{name}: wrote {os.path.relpath(pdf_path, REPO)} "
          f"({size / 1024:.0f} KB{f', {pages} pages' if pages else ''})")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--paper", choices=sorted(PAPERS), help="build only this paper")
    ap.add_argument("--html-only", action="store_true", help="write the HTML and stop")
    args = ap.parse_args(argv)

    names = [args.paper] if args.paper else sorted(PAPERS)
    return max(build(n, PAPERS[n], args.html_only) for n in names)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
