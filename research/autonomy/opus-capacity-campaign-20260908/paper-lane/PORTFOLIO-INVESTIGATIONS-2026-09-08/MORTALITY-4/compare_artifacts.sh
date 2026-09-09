#!/usr/bin/env bash
# Byte-identity of this lane's six regenerated artifacts against MORTALITY-2's and MORTALITY-3's.
set -u
rc=0
for f in corpus-metadata.json genre-classification.json handcheck-sample-skeleton.json handcheck-agreement.json genre-stratified-rates.json reclassification-sensitivity.json; do
  for peer in ../MORTALITY-2 ../MORTALITY-3; do
    if cmp -s "$f" "$peer/$f"; then echo "IDENTICAL  $f  vs $peer"; else echo "DIFFERS    $f  vs $peer"; rc=1; fi
  done
done
sha256sum corpus-metadata.json genre-classification.json handcheck-sample-skeleton.json handcheck-agreement.json genre-stratified-rates.json reclassification-sensitivity.json
exit $rc
