---
id: DOC-EMC-PHARMACOLOGY-IDENTITY-AMENDMENT-20260906
title: NCC pharmacology source identity amendment
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Correct catalogue identity and apply the original descriptive rules to additional source evidence.
scope: Retrospective NCC screen annotation and bounded interpretation.
audience: [maintainers, autonomous research agents]
---

The original 26 files, including protocol, report, results and both freeze/file manifests, were archived byte-for-byte in `original-2026-09-06/frozen-packet.zip` before this amendment. `archive-manifest.json` records each original path and SHA256, archive timestamp and ZIP hash. This amendment follows independent source review and is not outcome-blind. No threshold, denominator or stop condition changes.

The original report incorrectly treated supplier/catalogue identity as missing. MOESM4 already supplies catalogue, CAS, name, target, pathway and provider in columns A:F. Rows 111–113 identify S2180, S4432 and S2181 respectively. The current [S2181 product page](https://www.selleckchem.com/products/MLN9708.html) resolves CAS1201902-80-8 as an ixazomib citrate analogue; its [datasheet](https://www.selleckchem.com/datasheet/MLN9708-S218103-DataSheet.html) corroborates the product/CAS link. Its six-member boronate connectivity remains distinct from S4432 regulatory citrate's five-member boronate and S2180 active ixazomib. The previous PubChem connectivity observation stands; the inference that current catalogue identity was unavailable does not.

MOESM4 annotates all five candidates as Proteasome/Proteases. The supplier also places S2181 in this pharmacology context, but nearby numerical biochemical activities are attributed to MLN2238 in its explanatory prose. They are not evidence of S2181-specific potency. This repair retains S2181 as a separately measured, source-annotated analogue with unresolved active moiety. No hydrolysis equivalence, additional validated active moiety, clinical use or analogue-specific potency is inferred. Historical lot composition and in-well conversion remain unmeasured, as assay/material uncertainty rather than a selective missing-product gate.

Original annotation: unresolved candidate identity, missing family and active moiety; complete descriptive claim false. Updated annotation: resolved catalogue analogue identity, boronic-acid/ester chemical lineage, active moiety still unresolved. The other boronic family labels are broadened in wording to include their already recognized ester preparations; this is still two broad families. `annotation-change.json` preserves both annotations.

Applying each original condition: documented active-moiety worst ranks remain 15, 24 and 17, below 55.25; two chemical families remain; all five source candidates now have resolved current catalogue identity; removing either family retains low-quartile observations. Thus the original **descriptive two-family consistency rule passes**. Completeness of experimentally validated mechanism does not follow. The catalogue annotation is not NCC target engagement, and the analogue contributes neither a fourth documented active moiety nor a third family. The old blocker is superseded, not silently preserved as a historical-lot requirement.

No source measurement or rank changes. Original binary64 stress arithmetic is retained. Independent decimal addition changes Carmustine 137.5 to 137, Goserelin Acetate 135.5 to 136, Olaparib 137.5 to 138, and Pemetrexed disodium 135.5 to 135. This numerical tie sensitivity affects neither the five candidates nor their lowest-quartile classifications. Exact decimal values are preserved in the copied arithmetic verification and amended result.

All 221 exact MOESM5 names remain in `source_name`; exact MOESM4 names are separate `catalogue_source_name` fields, with row/CAS/catalogue/provider/target/pathway pointers. MOESM6 row18 continues to say Ixazomib for CAS1201902-80-8 and 1982 nM; it is not reassigned to active ixazomib. This corrects display-name ambiguity without changing the source tables.

`apply-source-amendment.py` reads the immutable archive and cached MOESM4 to produce amended roster, ranked screen, result, change record and checks. It reuses all original ranks and measurements. Original top-level result/roster/ranked files and original scripts remain historical; use the `amended-` files for the current interpretation. The protocol display adds frontmatter and an archive notice around its unchanged original body; the current report is a replacement reader document. The ZIP stores the original unwrapped Markdown bytes. Original freeze checks apply to that archived version, not administrative display wrappers.
