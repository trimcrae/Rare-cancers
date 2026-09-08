# TCIP-settlement — package manifest

Written 2026-09-08 by TCIP (sole exclusive owner). Disposition and reasoning:
[`SETTLEMENT.md`](./SETTLEMENT.md). Per-file hashes for the reader-facing files and every
dependency: [`HASHES.txt`](./HASHES.txt).

`frozen/*.md.txt` are byte-identical copies of the live `.md` files (BEFORE = as received,
AFTER = as settled); the `.txt` suffix keeps the repository's frontmatter scanner from reading
an evidence copy as a second document claiming the same `id`. Bytes and hashes are unchanged.

`checks/` holds every check attempt in its own file, failures included and never overwritten:
CHECK-04 is a failed schema assumption superseded by CHECK-05; the six CHECK-20 files include four
runs that exited 2 on a wrong command-line interface, re-run correctly as CHECK-21 through CHECK-24;
CHECK-11 through CHECK-14 are the successive attempts to locate the exit-exposure values, which
CHECK-15 found.

## Every file in this package, with its sha256

```
5f5f03217d265e27f22a3c6d6da3d72bcb304a659c06a38a7a2fc819b9871c93  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/HASHES.txt
8ac7270f5ab61151e3e5e09ba3a485a444e9dd2a48efdaa3e790abf0bb3deb6d  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/MANIFEST.md
e656e95e3683712221c68d1b0f86d749502a663913f8ebbb148245278026042e  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/SETTLEMENT.md
d442c968f3c1a6293807b68f69f8563e1aeb366174329e09e4d9b5640bdd4b1b  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-01-reach-ablation.txt
0d586b1289b4a9e99758430e0adcc81c61d86bd8205895377deb5af3c042f12c  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-02-reach-size-axis.txt
a554f6fe6ec91ead003116c89edf161b4b5d55d8de7a8e3fa3d496e987e6728b  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-03-census.txt
39825210dd23966898dca6b33e2c6c0e43fcc3f4cb37760e7bdc46892cdfccba  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-04-9mza-and-degraders.txt
dfaffff3581a80f7159df73d30a4277b431abcc099bab0d54321a1345c4d4dc0  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-05-9mza-and-degraders.txt
78cbda12176c4a9f3eb312238603028c4367a989ff959ab4130617f54f837e10  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-06-degrader-pairs-and-7lwg.txt
2a5cff9ba9ffd054408d0aa1b4453b85cd05fa4efc550809b8fc08d6e7334306  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-07-floor-provenance.txt
2b93404acc8c2657185b883cb198feb3e0e2df053a61c512c3a68351134c183e  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-08-query-points-and-bands.txt
8847f0561138fd2b9f4620fa5fb2883891534c2eef77d235fe3ccabd7eef5039  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-09-band-elif.txt
147d45cbfc7403b095b99440f83da98063e86714e1ddc354ca8fc8c52635d02e  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-10-bodies-and-named-effector.txt
35148b5eb18b8dab26a3aa5b221954426740cced33e9d2e9211bdba7c35b6ec3  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-11-exit-exposure.txt
31ef2e4ac6d06d094e5f5a9111fef436224b024f252d052bdefc0a86c89ca830  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-12-exit-exposure-source.txt
5ad2940bab6d5b4f317779be7aa2a9891eb503f7d6d0d25e9bd5a6924cf93098  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-13-exit-exposure-hunt.txt
8a1d7c04fb574d3a3354289e747fe092b7ea69569dafb51be936dce5e89ae34f  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-14-exit-exposure-in-reach.txt
02a76b2d0ee81ab7816f1044365f74fe0c7df089e760176b8a544d32ad20a9f6  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-15-exit-vector-comparability.txt
9dfad58ce0290591514898b3ce9f5bf5fe1c293c35ebf3798927e668ce54dab5  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-16-s7-source-hunt.txt
1e6c44c787e31f5a2e5671b990ffb0ceb8d1ff1893a2f2ca6922f735f0aaa8b4  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-17-floor-sizing-structure.txt
4adc994a23437f0ebd379b15635359c3568e53cf3f6feb247a2cd94279546620  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-18-s7-literature-source.txt
ac57bfbcd60d668a7110fc0c5e049cf3958166d67a443b2f32d7380bd0069b36  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-19-residual-claims.txt
99f73901d284fc85d1752c4a65cc5d731db379316063854929e1419540962c08  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_asymmetry.txt
c8528b839587a7e9cf27a6ce8fff77f90861c4fc1a617decf7a2e888cee7153d  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_citations.txt
5eaccda7f0580ca57caee5666e40937a1ef9aecf04acd01804ee9b5130e398f3  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_claims.txt
cfedd8b8ea585dd22d46c531da529150629e7bc25a00eea588e0513ef2f98c56  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_consistency.txt
9a7211fe7d4da609bd04ae303301256f0c8fde14a80fa568fa05f6bb7f129aeb  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_style.txt
ee8c7a74695fe2615b000e33854629ee7a14e90038634be30045533a2642e0e2  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_submission_residue.txt
1c7d66cd81731b2725478de4ff28b37db1c9b1501fb2a2538b16404aa66edcd1  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-21-BEFORE-lint_consistency-repo.txt
df86e29d0f3c5955db301fc7b5c29ca54e90e60a3d3c003138f1b3911a5d7e8a  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-22-BEFORE-lint_asymmetry.txt
f76dba2132a9634dd44c0f59ff1c6ad9aefa3634c013c33ca2eea4b9bb51975f  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-23-BEFORE-lint_citations.txt
0cfac078765e9418577feeb5ea5101248ad957b8f639bc3f69eb95e1ce150256  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-24-BEFORE-lint_submission_residue.txt
050f02250dd1075852581e793ce1dcdc5d1b78e70f7248b07123a1247d89c08e  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-25-BEFORE-lint_style-gatemode.txt
b34cb90da04c307da4a52797d030b080ff81f62b79aa95a71250aece9328ef51  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-26-BEFORE-lint_claims-gatemode.txt
1c7d66cd81731b2725478de4ff28b37db1c9b1501fb2a2538b16404aa66edcd1  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-30-AFTER-lint_consistency.txt
b34cb90da04c307da4a52797d030b080ff81f62b79aa95a71250aece9328ef51  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-31-AFTER-lint_claims.txt
050f02250dd1075852581e793ce1dcdc5d1b78e70f7248b07123a1247d89c08e  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-32-AFTER-lint_style.txt
df86e29d0f3c5955db301fc7b5c29ca54e90e60a3d3c003138f1b3911a5d7e8a  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-33-AFTER-lint_asymmetry.txt
f76dba2132a9634dd44c0f59ff1c6ad9aefa3634c013c33ca2eea4b9bb51975f  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-34-AFTER-lint_citations.txt
0cfac078765e9418577feeb5ea5101248ad957b8f639bc3f69eb95e1ce150256  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-35-AFTER-lint_submission_residue.txt
a75dfdc09813cf31d8c98b48796b50c43be4920e9f79e494beda668ec3adb1fe  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-36-AFTER-pytest-tcip-modules.txt
17a15f68ea8ae2a4738c7ab8dc648f7dc113c00da419d8e192c61853f8e9f64e  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-37-AFTER-systems_check.txt
230b6837a709d6d588911c8458b725afbaf1c6924da7082db1b4fa4406ddad22  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-38-AFTER-systems_check-rerun.txt
a4813c8f5748b71c6ec590f42e1416fddaec4e3a01fdfedbd2f944b6d336581b  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-39-figures-and-diff.txt
3483c0bbcbd94e4faa5b3de38da8010130b189336b79ac27cd08101c56748ba3  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/frozen/AFTER-tcip-induced-interface-preprint-si.md.txt
2e2b7862c3c6412ff4ae9086fd2acca799ae8999511ca607d1a49e416e82d9a9  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/frozen/AFTER-tcip-induced-interface-preprint.md.txt
ac387cbf8af6451771a382b8ff6ba7798c6f230fff44c92fe9ba689949a41814  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/frozen/BEFORE-tcip-induced-interface-preprint-si.md.txt
3dbac6e82df765fe9bda6d17080d1d1764d4abfca5f52b4c9e189854b25d233e  research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/frozen/BEFORE-tcip-induced-interface-preprint.md.txt
```

## Sizes

```
   2186 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/HASHES.txt
   9815 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/MANIFEST.md
  15514 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/SETTLEMENT.md
   4572 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-01-reach-ablation.txt
  10642 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-02-reach-size-axis.txt
   5117 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-03-census.txt
    286 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-04-9mza-and-degraders.txt
   2183 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-05-9mza-and-degraders.txt
   2002 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-06-degrader-pairs-and-7lwg.txt
   1944 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-07-floor-provenance.txt
   2705 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-08-query-points-and-bands.txt
   1827 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-09-band-elif.txt
   6004 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-10-bodies-and-named-effector.txt
   9348 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-11-exit-exposure.txt
   4392 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-12-exit-exposure-source.txt
   4827 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-13-exit-exposure-hunt.txt
   2566 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-14-exit-exposure-in-reach.txt
   3201 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-15-exit-vector-comparability.txt
    718 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-16-s7-source-hunt.txt
   1175 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-17-floor-sizing-structure.txt
   4664 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-18-s7-literature-source.txt
   1885 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-19-residual-claims.txt
    292 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_asymmetry.txt
    229 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_citations.txt
     34 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_claims.txt
    232 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_consistency.txt
  19770 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_style.txt
    259 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-20-BEFORE-lint_submission_residue.txt
     51 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-21-BEFORE-lint_consistency-repo.txt
    776 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-22-BEFORE-lint_asymmetry.txt
    371 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-23-BEFORE-lint_citations.txt
    268 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-24-BEFORE-lint_submission_residue.txt
   5398 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-25-BEFORE-lint_style-gatemode.txt
  74656 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-26-BEFORE-lint_claims-gatemode.txt
     51 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-30-AFTER-lint_consistency.txt
  74656 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-31-AFTER-lint_claims.txt
   5398 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-32-AFTER-lint_style.txt
    776 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-33-AFTER-lint_asymmetry.txt
    371 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-34-AFTER-lint_citations.txt
    268 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-35-AFTER-lint_submission_residue.txt
     99 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-36-AFTER-pytest-tcip-modules.txt
 644624 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-37-AFTER-systems_check.txt
 639059 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-38-AFTER-systems_check-rerun.txt
  11342 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/checks/CHECK-39-figures-and-diff.txt
  16663 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/frozen/AFTER-tcip-induced-interface-preprint-si.md.txt
  28068 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/frozen/AFTER-tcip-induced-interface-preprint.md.txt
  14116 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/frozen/BEFORE-tcip-induced-interface-preprint-si.md.txt
  26984 research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-settlement/frozen/BEFORE-tcip-induced-interface-preprint.md.txt
1662384 total
```
