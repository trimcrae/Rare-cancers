set -u
M=research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md
echo "HEAD now: $(git rev-parse HEAD)"
echo "lane-start HEAD of TXN-DEPENDENCY: 1e35538daee86e1a34345340f7562d1e91147fa0"
echo
echo "== the ten \$8 rows as printed in the manuscript =="
sed -n '441,534p' $M | grep -E '^\| *\`?research/' 
echo
echo "== per object: declared | blob at 1e35538 | blob at HEAD | worktree =="
sed -n '441,534p' $M | grep -oE 'research/[A-Za-z0-9_./-]+\.(json|py)' | sort -u | while read -r p; do
  decl=$(sed -n '441,534p' $M | grep -F "$p" | grep -oE '\b[0-9a-f]{40}\b' | head -1)
  a=$(git rev-parse 1e35538daee86e1a34345340f7562d1e91147fa0:"$p" 2>/dev/null || echo ABSENT)
  b=$(git rev-parse HEAD:"$p" 2>/dev/null || echo ABSENT)
  w=$(git hash-object "$p" 2>/dev/null || echo ABSENT)
  s1=MATCH; [ "$decl" = "$a" ] || s1=DIFF
  s2=MATCH; [ "$decl" = "$w" ] || s2=DIFF
  printf '%-62s decl=%s  at1e35538=%s[%s]  HEAD=%s  wt=%s[%s]\n' "$p" "${decl:0:8}" "${a:0:8}" "$s1" "${b:0:8}" "${w:0:8}" "$s2"
done
