# Unapplied patch for the parent

`0001-PUB-TCIP-retire-modality-general-opening.patch` is a unified diff against the **current**
`systems/graph/publications.json`:

    base   68,790 B  sha256 8dc9b0b9894679277e94d3e283459e9fae63d13b845460bf177a1997db0e1418
    result 70,224 B  sha256 800e844ff1e6b8127c5d4d6811438e820f8c66c4efe11269e1c083d751d1902d

The base is the file as it stands after the parent's 91609d30f application, not the 68,537 B version
named in the focused freeze. Apply from the repository root:

    git apply --check research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-repair-2/patches/0001-PUB-TCIP-retire-modality-general-opening.patch
    git apply       research/autonomy/opus-capacity-campaign-20260908/paper-lane/TCIP-repair-2/patches/0001-PUB-TCIP-retire-modality-general-opening.patch

`git apply --check` exited 0 in this lane at the stated base, and the patched copy parses as JSON.

Exactly one string changes: the `PUB-TCIP` entry's `what_it_would_claim`. No other entry, key,
ordering or whitespace is touched, and no generated view was regenerated. The full new field value is
`PUB-TCIP-what_it_would_claim-NEW.txt` (5,241 B including its trailing newline; the JSON string
itself is 5,226 characters), sha256 of the file
`e6f2f99d87fb44893c15bae9eb380fbf65bc88106de31f7b51ce1336d27f7234`.

Three edits inside that one string:
1. the opening assertion "THE CLAIM IS MODALITY-GENERAL AND THE EMC ANCHOR IS THE SETTING IT WAS
   COMPUTED IN" is explicitly retired and replaced by the named-toolchain audit and the potentially
   transferable methodological caution, with the NOT-AN-EMC-SPECIFIC-RESULT designation retained;
2. the abbreviated probe/residue statement now gives the necessary lower bound, the non-sufficiency
   and non-equivalence, and the absence of any 12-residue upper bound;
3. the missing joint counts are scoped to the shared-proposal floor ablation, with the separate
   eight-rung enumeration named as a different object reporting no ratio interval and no test.

If the parent wants item 3 held back as out of F04's scope, deleting that hunk's third replacement is
safe on its own; items 1 and 2 do not depend on it.
