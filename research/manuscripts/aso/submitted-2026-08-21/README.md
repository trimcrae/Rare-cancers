---
id: DOC-ASO-SUBMITTED-2026-08-21
title: "The 2026-08-21 Research Square submission of PUB-ASO — a historical record"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [maintainers, autonomous research agents]
purpose: >
  Say what these three PDFs are, that they are a superseded submission rather than the current
  deposit, and why their build-stamps were deliberately not recovered with them.
scope: >
  The three PDFs in this directory only. It makes no claim about the current ASO manuscript, whose
  live artifacts sit one directory up and are inventoried by the archive manifest.
last_verified: 2026-09-02
---

# The 2026-08-21 Research Square submission of PUB-ASO — a historical record

These three PDFs are the artifacts actually submitted to Research Square on 2026-08-21. They were
recovered on 2026-09-02 from `origin/claude/preprint-host-unaffiliated-srzofd` @ `06171eeee`, where
they were the only copy in the repository.

⛔ **They are NOT the current deposit and must not be treated as it.** They render
`fusion-junction-aso-research-article.md` as it stood on 2026-08-21; the paper has been through
further red-team rounds since, and the live journal article is
[`../fusion-junction-aso-journal-article.md`](../fusion-junction-aso-journal-article.md). They sit in
this dated subdirectory rather than beside the live artifacts precisely so that
`aso_archive_manifest.py`, whose deposit inventory globs `aso/*.pdf` and does not recurse, keeps
counting the current deposit and not this one.

⚠ **Their build-stamps were deliberately not recovered.** A build-stamp asserts that a PDF is
current against named sources at named sha256s. Checked on 2026-09-02, 3 of the 4 sources each stamp
names have moved on `main`, so landing the stamps would have put a false currency claim in the tree —
and, measured rather than predicted, it reddened
`test_every_stamped_pdf_renders_the_documents_its_stamp_names`, because the 2026-08-21 builder
predates the `artifact` key that guard requires. The stamps remain at `06171eeee` for anyone who
wants the record of what was rendered from what.

Reading: [`../../../autonomy/sprint-2026-09-01/S37-BRANCH-DEBT.md`](../../../autonomy/sprint-2026-09-01/S37-BRANCH-DEBT.md) §3b.
