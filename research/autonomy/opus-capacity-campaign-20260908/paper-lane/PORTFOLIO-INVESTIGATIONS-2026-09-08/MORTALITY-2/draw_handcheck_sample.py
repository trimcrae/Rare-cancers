#!/usr/bin/env python3
"""Draw the hand-check sample for the genre classifier: 40 of 162 papers, simple random
without replacement, seed fixed at 20260908 (the campaign date) so the draw is reproducible
and was not re-rolled. Prints title + journal + the machine label so a human can adjudicate
each row; writes the sample skeleton. No cue, no rate, no sentence text is touched."""
import json, pathlib, random, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from genre_classifier import classified_rows  # noqa: E402

N = 40
SEED = 20260908
OUT = pathlib.Path(__file__).with_name("handcheck-sample-skeleton.json")


def main():
    rows = classified_rows()
    rng = random.Random(SEED)
    sample = rng.sample(rows, N)
    OUT.write_text(json.dumps({"seed": SEED, "n": N,
                               "pmids": [r["pmid"] for r in sample]}, indent=1) + "\n")
    for r in sample:
        print(f'{r["pmid"]}\t{r["stratum"]}\t{r["journal"]}\t{r["title"]}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
