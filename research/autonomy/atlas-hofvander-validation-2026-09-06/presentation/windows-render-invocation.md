---
id: DOC-ATLAS-WINDOWS-RENDER-20260906
title: Windows invocation for the registered tissue RNA renderer
kind: runbook
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Supply the actual local renderer invocation without building an artifact in this task.
scope: surface-tissue-rna entry and existing Windows Chromium adapter.
audience: [maintainers, autonomous research agents]
---

Run the following PowerShell from `C:/Users/mcrae/.codex/worktrees/8010/EMC-Research` after integration has registered `surface-tissue-rna` in `research/manuscripts/build_submission_pdf.py`. It uses the existing ASO Windows adapter pattern without editing the renderer or changing document/figure inputs.

```powershell
@'
from pathlib import Path
import sys
sys.path.insert(0, str(Path('research/manuscripts').resolve()))
import build_submission_pdf as renderer

chrome = Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
assert chrome.is_file(), 'Expected installed Chrome is absent'
assert 'surface-tissue-rna' in renderer.PAPERS, 'Renderer registration not integrated'
renderer.find_chrome = lambda: str(chrome)

class PortableWS(renderer.WS):
    def call(self, method, **params):
        if method == 'Page.navigate' and params.get('url', '').startswith('file://'):
            params['url'] = Path(params['url'][7:]).resolve().as_uri()
        return super().call(method, **params)

renderer.WS = PortableWS
raise SystemExit(renderer.main(['--paper', 'surface-tissue-rna', '--style', 'preprint']))
'@ | & 'C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 -
$atlasRenderExit = $LASTEXITCODE
if ($atlasRenderExit -ne 0) { throw "Atlas renderer exited $atlasRenderExit" }
```

The `preprint` style is the renderer's single-column, non-journal-house style. Main dispatch also builds declared supplementary material. Output uses the registered entry's `out` path with `-preprint.pdf`; the renderer writes its same-stem `.build-stamp.json`. Read the integrated PAPERS entry for exact output/source paths rather than guessing a filename. Preserve stdout/stderr and inspect the generated PDF before a release claim.

Actual local inspection: Chrome exists at the path above; Edge also exists at `C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`. The bundled Python imports pypdf from its `Lib/site-packages/pypdf`; no installation is required. The renderer's Markdown converter and WebSocket client are internal. Pandoc, LaTeX, the Python markdown package and Playwright are not required. The normal renderer uses headless Chromium, a temporary profile and local DevTools; no network source retrieval is part of this invocation.

Two genuine Windows portability issues exist in the currently inspected base renderer: `find_chrome()` searches Linux browser locations/PATH and returned None here despite installed Chrome; `Page.navigate` concatenates `file://` with Windows absolute paths instead of producing a proper file URI. Explicit Chrome selection and `Path.as_uri()` address both. The same implementation is already in the prior ASO helper `research/release-candidates/PUB-ASO/2026-09-04/build_candidate.py:62` through its PortableWS assignment. That helper is evidence for the adapter; do not invoke its ASO build or copy its journal-specific CSS/geometry changes for this paper.

At this read-only inspection, the root renderer did not yet contain the `surface-tissue-rna` PAPERS entry. This is a concrete integration dependency, not an assertion that the writer's intended registration is wrong. The invocation deliberately fails before rendering if it remains missing. No PDF, HTML or build stamp was generated in this task; only module import, dependency discovery and binary existence checks were run.
