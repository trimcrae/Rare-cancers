---
id: DOC-IPD-EMPIRICAL-RUNTIME-AMENDMENT-20260906
title: Dated empirical runtime amendment
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve source evidence, exact execution scope and limitations for the current research checkpoint.
scope: Reader metadata added at integration; scientific source body unchanged.
audience: [maintainers, autonomous research agents]
---

# Second pre-outcome amendment: installed survival interface

Synthetic runtime verification of survival 3.8.6 failed before empirical outcome access: explicit `survdiff(...,timefix=FALSE)` passes timefix into model.frame, producing a variable-length error. The installed function removes m$rho but does not remove m$timefix from its matched call. This prevents the first amendment's literal call from executing.

The adapter now makes a local copy of survival::survdiff and sets ONLY its formal default timefix to FALSE. It calls this local function without an explicit timefix argument. The function body and installed package remain byte-for-byte unmodified, checked at runtime with identical(body(...),body(survival::survdiff)). Thus matched-call construction receives no timefix argument and the unchanged body skips aeqSurv. This is a documented interface bridge, not a reconstruction implementation or tuned statistical algorithm.

Synthetic R and Python fixtures verify distinct near ties (Q=1/17), exact ties (Q=0), and zero variance. No empirical run occurred before this repair. The scientific protocol, source manifest, development gate and no-held-out boundary remain unchanged.
