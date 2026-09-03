#!/usr/bin/env python3
"""Europe PMC probe for the EMC mechanism-of-death / supportive-care sweep.

Pure stdlib. Two jobs, in one run, because they answer two halves of one question:

  (a) A QUERY INDEX, like scripts/lit_lane_probe.py: a fixed list of Europe PMC
      searches with their hit counts and top hits. A hit count of ZERO is the only
      honest basis for "nothing on this exists", which is otherwise indistinguishable
      from "nobody looked".

  (b) A TERMINAL-EVENT CORPUS, which is the part no prior artifact here has. Every
      OPEN-ACCESS extraskeletal myxoid chondrosarcoma paper is retrieved as full text
      and scanned for the sentences that describe a patient DYING. EMC's published
      record is dominated by case reports and small series, and those state the
      terminal event in prose ("died of respiratory failure due to progressive
      pulmonary metastases") while every pooled outcome table reduces it to a vital
      status. The sentences are the evidence a cause-of-death breakdown has to rest on
      and they are not tabulated anywhere.

⛔ THIS SCRIPT CLASSIFIES NOTHING. It retrieves sentences and records where each came
from. The reading — is this an EMC death, a competing cause, a treatment complication —
is done by a human or an agent afterwards, against the quoted sentence, so that every
row of the resulting breakdown can be checked against its source. A regex that decided
"cause of death = respiratory failure" would be a fabricated clinical fact wearing an
artifact's costume (CLAUDE.md section 4: a populated field is not a measured one).

The dev sandbox's egress proxy 403s www.ebi.ac.uk on CONNECT, so this runs on a GitHub
runner (CLAUDE.md section 6, escape hatch 1).

Output: research/literature/emc-mortality-probe.json
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
OUT = pathlib.Path("research/literature/emc-mortality-probe.json")

UA = "rare-cancers-research/1.0 (github.com/trimcrae/Rare-cancers; mailto:trimcrae@gmail.com)"

# The disease, spelled every way the literature spells it. Reused by both halves so the
# corpus and the index cannot silently be about different populations.
EMC = ('("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" '
       'OR "chordoid sarcoma" OR "extraskeletal myxoid chondro-sarcoma")')

# (key, query). Kept verbatim-quotable so the memo can state what was asked.
QUERIES: list[tuple[str, str]] = [
    # --- (a) what actually kills EMC patients ---------------------------
    ("emc_cause_of_death",
     f'{EMC} AND ("cause of death" OR "died of" OR "died from" OR "causes of death")'),
    ("emc_respiratory_failure",
     f'{EMC} AND ("respiratory failure" OR "respiratory insufficiency" OR dyspnoea OR dyspnea)'),
    ("emc_pulmonary_metastases_burden",
     f'{EMC} AND ("pulmonary metastases" OR "lung metastases") AND (progressive OR burden OR bilateral OR miliary)'),
    ("emc_metastasectomy",
     f'{EMC} AND (metastasectomy OR "pulmonary metastasectomy" OR "surgical resection of metastases")'),
    ("emc_late_recurrence",
     f'{EMC} AND ("late recurrence" OR "long-term follow-up" OR "20 years" OR "15 years" OR indolent)'),
    ("emc_competing_mortality",
     f'{EMC} AND ("other cause" OR "competing risk" OR "non-cancer" OR "unrelated cause" OR "intercurrent")'),
    ("emc_sites_of_metastasis",
     f'{EMC} AND (metastas*) AND (bone OR liver OR brain OR "soft tissue" OR "lymph node" OR retroperitoneal)'),
    ("emc_local_complications",
     f'{EMC} AND ("spinal cord" OR "cord compression" OR obstruction OR haemorrhage OR hemorrhage OR "airway")'),
    ("emc_seer_population",
     f'{EMC} AND (SEER OR "population-based" OR registry OR nationwide)'),
    ("emc_disease_specific_survival",
     f'{EMC} AND ("disease-specific survival" OR "cancer-specific survival" OR "relative survival")'),

    # --- (b) mortality mechanisms in sarcoma more broadly ---------------
    # EMC-specific data will be thin; the class-level literature is what a rate has to
    # be borrowed from, and borrowing has to be visible.
    ("sarcoma_cause_of_death",
     '(sarcoma OR "soft tissue sarcoma") AND ("cause of death" OR "causes of death") AND (analysis OR series OR registry)'),
    ("sarcoma_lung_metastases_death",
     '"soft tissue sarcoma" AND "pulmonary metastases" AND (mortality OR "cause of death" OR "respiratory failure")'),
    ("sarcoma_treatment_related_mortality",
     '(sarcoma) AND ("treatment-related mortality" OR "toxic death" OR "febrile neutropenia" OR "neutropenic sepsis")'),
    ("sarcoma_vte",
     '(sarcoma) AND ("venous thromboembolism" OR "pulmonary embolism" OR thromboprophylaxis)'),
    ("cancer_competing_mortality_noncancer",
     '("non-cancer mortality" OR "competing causes of death" OR "cardiovascular mortality") AND (cancer survivors OR "cancer patients") AND SEER'),

    # --- (c) does supportive / symptom-directed care move SURVIVAL? -----
    # The question the portfolio has never asked. These are the trials that would have
    # to exist for any of this to be more than a plausible story.
    ("early_palliative_care_survival",
     '("early palliative care" OR "specialist palliative care") AND (survival OR "overall survival") AND ("randomized" OR "randomised" OR trial)'),
    ("palliative_care_sarcoma",
     '("palliative care" OR "supportive care") AND (sarcoma OR "soft tissue sarcoma")'),
    ("cachexia_survival_trial",
     '(cachexia OR "weight loss") AND cancer AND (anamorelin OR olanzapine OR "nutritional support") AND (survival OR trial)'),
    ("exercise_oncology_survival",
     '(exercise OR "physical activity") AND cancer AND survival AND ("randomized controlled trial" OR "randomised controlled trial")'),
    ("thromboprophylaxis_ambulatory_cancer",
     '(apixaban OR rivaroxaban OR "low molecular weight heparin") AND ("ambulatory cancer" OR "cancer-associated thrombosis") AND (prophylaxis) AND (randomized OR randomised)'),
    ("sepsis_bundle_mortality",
     '(sepsis) AND ("early goal-directed" OR "sepsis bundle" OR "Surviving Sepsis") AND mortality AND (neutropenic OR cancer OR "immunocompromised")'),
    ("pleural_effusion_management_survival",
     '("malignant pleural effusion") AND ("indwelling pleural catheter" OR pleurodesis) AND (survival OR mortality)'),
    ("oligometastatic_local_therapy_survival",
     '(oligometastatic OR oligometastases) AND ("stereotactic body radiotherapy" OR SABR OR metastasectomy) AND (survival) AND (randomized OR randomised OR phase)'),
    ("patient_reported_outcomes_survival",
     '("patient-reported outcomes" OR "symptom monitoring" OR "electronic symptom") AND (survival OR "overall survival") AND (randomized OR randomised)'),
]

# Bounded so a single pathological query cannot dominate the run or the artifact.
PAGE_SIZE = 25
CORPUS_CAP = 600          # OA EMC papers to enumerate
FULLTEXT_CAP = 400        # of those, how many full texts to actually pull
SLEEP = 0.34              # Europe PMC asks for <= 3 req/s

# ---------------------------------------------------------------------------
# Terminal-event sentence extraction
# ---------------------------------------------------------------------------
# A sentence is KEPT if it contains a death/terminal cue. That is deliberately a
# recall-first filter: it over-collects (an "died" in a cited study's summary, a
# survival-analysis sentence) and the over-collection is visible to whoever reads
# the artifact. The alternative — a tighter pattern — would silently drop the
# unusual terminal events, which are exactly the rows this corpus exists to find.
DEATH_CUES = re.compile(
    r"\b("
    r"died|death|deaths|deceased|fatal|fatality|demise|"
    r"succumb\w*|"
    r"mortality|"
    r"terminal(?:ly)?|"
    r"cause of death|"
    r"expired|"
    r"end-of-life|hospice|palliative"
    r")\b",
    re.I,
)

# Cues that make a kept sentence more likely to describe a MECHANISM rather than a
# bare vital status. Recorded as a flag on the sentence, never used to drop one.
MECHANISM_CUES = re.compile(
    r"\b("
    r"respiratory (?:failure|insufficiency|distress)|"
    r"pulmonary (?:insufficiency|failure|embolism|haemorrhage|hemorrhage)|"
    r"sepsis|septic|infection|pneumonia|"
    r"cachexia|malnutrition|"
    r"haemorrhage|hemorrhage|bleeding|"
    r"thrombosis|thromboembolism|embolism|"
    r"cord compression|"
    r"obstruction|"
    r"hepatic failure|liver failure|renal failure|"
    r"cardiac|myocardial|"
    r"cerebral|intracranial|"
    r"multi-?organ|"
    r"asphyxia|airway|"
    r"toxicity|complication|postoperative|"
    r"unrelated|other cause|intercurrent|comorbid"
    r")\b",
    re.I,
)

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def get(url: str, tries: int = 3) -> str:
    """GET with a small retry. Returns '' rather than raising, so one dead PMCID
    cannot discard a whole corpus."""
    last = ""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as fh:
                return fh.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001 - a probe must not die on one URL
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(1.5 * (attempt + 1))
    print(f"  ! give up on {url}: {last}", file=sys.stderr)
    return ""


def search(query: str, page_size: int = PAGE_SIZE, cursor: str = "*") -> dict:
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "cursorMark": cursor,
        "resultType": "core" if page_size <= 25 else "lite",
    })
    raw = get(f"{SEARCH}?{params}")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def hit_row(r: dict) -> dict:
    return {
        "pmid": r.get("pmid"),
        "pmcid": r.get("pmcid"),
        "doi": r.get("doi"),
        "title": r.get("title"),
        "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title")
                   or r.get("journalTitle"),
        "year": r.get("pubYear"),
        "isOpenAccess": r.get("isOpenAccess"),
        "citedBy": r.get("citedByCount"),
    }


def strip_xml(xml: str) -> str:
    """Full text XML -> plain text. Deliberately crude: the goal is sentences a human
    can read and check against the source, not a faithful document model."""
    # Drop the reference list: it is full of other papers' titles containing 'death'
    # and 'mortality', and those are not this paper's patients.
    for end_tag in ("<ref-list", "<back>"):
        cut = xml.find(end_tag)
        if cut > 0:
            xml = xml[:cut]
    xml = re.sub(r"<(table-wrap|fig|inline-formula|disp-formula)\b.*?</\1>", " ", xml, flags=re.S)
    txt = TAG.sub(" ", xml)
    txt = (txt.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
              .replace("&#x2013;", "-").replace("&#x2019;", "'").replace("&quot;", '"'))
    return WS.sub(" ", txt).strip()


def sentences(text: str) -> list[str]:
    # Protect the abbreviations that otherwise split a clinical sentence mid-clause.
    guard = text
    for abbr in ("Dr.", "Fig.", "e.g.", "i.e.", "vs.", "No.", "approx.", "cf.", "et al."):
        guard = guard.replace(abbr, abbr.replace(".", "\x00"))
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(])", guard)
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]


def probe_queries() -> dict:
    out = {}
    for key, q in QUERIES:
        print(f"[query] {key}", file=sys.stderr)
        data = search(q)
        res = (data.get("resultList") or {}).get("result", []) if data else []
        out[key] = {
            "query": q,
            "hitCount": data.get("hitCount") if data else None,
            "retrieved": len(res),
            "hits": [hit_row(r) for r in res],
        }
        if data.get("hitCount") is None:
            print(f"  ! {key}: no hitCount (API error)", file=sys.stderr)
        time.sleep(SLEEP)
    return out


def enumerate_oa_corpus() -> list[dict]:
    """Every open-access EMC paper Europe PMC knows about, paged to CORPUS_CAP."""
    query = f"{EMC} AND (OPEN_ACCESS:Y OR IN_EPMC:Y)"
    rows, cursor, seen = [], "*", set()
    while len(rows) < CORPUS_CAP:
        data = search(query, page_size=100, cursor=cursor)
        if not data:
            break
        res = (data.get("resultList") or {}).get("result", [])
        if not res:
            break
        for r in res:
            pmcid = r.get("pmcid")
            if pmcid and pmcid not in seen:
                seen.add(pmcid)
                rows.append(hit_row(r))
        nxt = data.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(SLEEP)
        print(f"[corpus] {len(rows)} open-access EMC papers enumerated", file=sys.stderr)
    return rows[:CORPUS_CAP]


def harvest_terminal_events(corpus: list[dict]) -> tuple[list[dict], dict]:
    """Pull full text for each OA paper and keep every death-cue sentence."""
    events, stats = [], {"attempted": 0, "fulltext_ok": 0, "papers_with_sentences": 0}
    for row in corpus[:FULLTEXT_CAP]:
        pmcid = row.get("pmcid")
        if not pmcid:
            continue
        stats["attempted"] += 1
        xml = get(FULLTEXT.format(pmcid=pmcid))
        time.sleep(SLEEP)
        if not xml or "<" not in xml:
            continue
        stats["fulltext_ok"] += 1
        text = strip_xml(xml)
        kept = []
        for s in sentences(text):
            if len(s) > 600 or len(s) < 25:
                continue
            if not DEATH_CUES.search(s):
                continue
            kept.append({
                "sentence": s,
                "has_mechanism_cue": bool(MECHANISM_CUES.search(s)),
            })
        if kept:
            stats["papers_with_sentences"] += 1
            events.append({
                "pmcid": pmcid,
                "pmid": row.get("pmid"),
                "doi": row.get("doi"),
                "title": row.get("title"),
                "journal": row.get("journal"),
                "year": row.get("year"),
                "n_sentences": len(kept),
                "sentences": kept,
            })
        print(f"[fulltext] {stats['fulltext_ok']}/{stats['attempted']} ok, "
              f"{len(events)} papers with death sentences", file=sys.stderr)
    return events, stats


# ---------------------------------------------------------------------------
# Background mortality: is the observed gap the size age and sex explain anyway?
# ---------------------------------------------------------------------------
# THE DECOMPOSITION IS UNINTERPRETABLE WITHOUT THIS. It subtracts a disease-specific
# survival figure from one study out of an all-cause figure from another and calls the
# remainder "deaths from other causes". A remainder far LARGER than an ordinary cohort
# of this age and sex would produce does not mean EMC patients die of other things -- it
# means the two studies were never describing one population, and the subtraction is an
# artifact. So the check is not a nicety; it is what decides whether the headline number
# may be quoted.
#
# Source: the Social Security Administration period life table, which is US public
# domain, needs no key, and publishes the one column required -- q(x), the probability
# that a person aged exactly x dies within one year.
LIFE_TABLE_URL = "https://www.ssa.gov/oact/STATS/table4c6.html"

# The row for one age carries male and female q(x) in the first and fifth numeric
# columns of that row. Parsed positionally because the table has no machine-readable
# identifiers; the parsed rows are echoed into the artifact so the parse is checkable
# against the published page rather than trusted.
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)


def fetch_life_table(start_age: int, years: int, male_fraction: float) -> dict:
    html = get(LIFE_TABLE_URL)
    if not html:
        return {"status": "FETCH_FAILED", "url": LIFE_TABLE_URL,
                "why": "the life table could not be retrieved; the background check stays NOT RUN"}

    qx: dict[int, tuple[float, float]] = {}
    for row_html in ROW.findall(html):
        cells = [WS.sub(" ", TAG.sub("", c)).strip().replace(",", "")
                 for c in CELL.findall(row_html)]
        nums = []
        for c in cells:
            try:
                nums.append(float(c))
            except ValueError:
                nums.append(None)
        # age, m_qx, m_lx, m_ex, f_qx, f_lx, f_ex
        if len(nums) >= 7 and all(n is not None for n in (nums[0], nums[1], nums[4])):
            age = int(nums[0])
            if 0 <= age <= 119 and 0 <= nums[1] < 1 and 0 <= nums[4] < 1:
                qx[age] = (nums[1], nums[4])

    needed = [a for a in range(start_age, start_age + years)]
    missing = [a for a in needed if a not in qx]
    if missing:
        return {"status": "PARSE_FAILED", "url": LIFE_TABLE_URL,
                "ages_parsed": len(qx), "ages_missing": missing,
                "why": ("the published table was retrieved but the ages this cohort needs "
                        "were not parsed out of it, so no background figure is asserted")}

    # Survive each single year in turn, by sex, then blend at the cohort's sex ratio.
    surv_m = surv_f = 1.0
    for age in needed:
        m_q, f_q = qx[age]
        surv_m *= (1.0 - m_q)
        surv_f *= (1.0 - f_q)
    blended_surv = male_fraction * surv_m + (1.0 - male_fraction) * surv_f

    return {
        "status": "OK",
        "url": LIFE_TABLE_URL,
        "table": "SSA period life table (actuarial), US, all causes",
        "start_age": start_age,
        "horizon_years": years,
        "male_fraction": male_fraction,
        "cumulative_mortality_male": round(1.0 - surv_m, 4),
        "cumulative_mortality_female": round(1.0 - surv_f, 4),
        "cumulative_mortality_blended": round(1.0 - blended_surv, 4),
        "qx_rows_used": {str(a): {"male": qx[a][0], "female": qx[a][1]} for a in needed},
        "limits": (
            "A general-population period life table. An EMC cohort is not the general "
            "population -- it is fit enough to have reached a sarcoma diagnosis and to have "
            "been treated, which biases its non-cancer mortality DOWNWARD relative to this "
            "figure. So this is an upper estimate of background mortality, and the check it "
            "supports is one-sided: it can show the observed gap is too LARGE to be "
            "background, and cannot prove the gap IS background."
        ),
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    queries = probe_queries()
    life_table = fetch_life_table(start_age=55, years=10, male_fraction=0.66)
    print(f"[life-table] {life_table.get('status')}", file=sys.stderr)
    corpus = enumerate_oa_corpus()
    events, stats = harvest_terminal_events(corpus)

    n_sent = sum(e["n_sentences"] for e in events)
    n_mech = sum(1 for e in events for s in e["sentences"] if s["has_mechanism_cue"])

    payload = {
        "_readme": (
            "EMC mechanism-of-death / supportive-care probe. Produced by "
            "scripts/lit_mortality_probe.py on a GitHub runner. TWO PARTS. `queries` is a "
            "citation index: each entry is a Europe PMC search, its total hitCount and its "
            "top hits, so a claim can carry a real PMID and an absence can carry a real "
            "zero. `terminal_events` is the corpus this probe exists for: every "
            "open-access EMC paper Europe PMC returns, scanned for sentences containing a "
            "death cue, with the sentence quoted verbatim and its source recorded. "
            "NOTHING HERE IS CLASSIFIED. A sentence being present does not mean it "
            "describes an EMC patient's death -- it may be a survival-analysis sentence, a "
            "reference to another cohort, or a negative ('no deaths occurred'). The "
            "classification is done by reading, downstream, against these quoted "
            "sentences, so that every row of a cause-of-death breakdown resolves to a "
            "source a reader can check. `has_mechanism_cue` is a retrieval hint, not a "
            "finding."
        ),
        "generated_by": "scripts/lit_mortality_probe.py",
        "disease_query_fragment": EMC,
        "caps": {"corpus": CORPUS_CAP, "fulltext": FULLTEXT_CAP, "page_size": PAGE_SIZE},
        "summary": {
            "n_queries": len(QUERIES),
            "n_queries_with_hits": sum(1 for v in queries.values() if (v["hitCount"] or 0) > 0),
            "n_queries_zero": sum(1 for v in queries.values() if v["hitCount"] == 0),
            "n_queries_failed": sum(1 for v in queries.values() if v["hitCount"] is None),
            "background_mortality_status": life_table.get("status"),
            "oa_corpus_enumerated": len(corpus),
            "fulltext_attempted": stats["attempted"],
            "fulltext_retrieved": stats["fulltext_ok"],
            "papers_with_death_sentences": stats["papers_with_sentences"],
            "death_sentences_total": n_sent,
            "death_sentences_with_mechanism_cue": n_mech,
        },
        "queries": queries,
        "background_mortality": life_table,
        "oa_corpus": corpus,
        "terminal_events": events,
    }

    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    s = payload["summary"]
    print(json.dumps(s, indent=1))
    if s["oa_corpus_enumerated"] == 0:
        print("::error::corpus enumeration returned nothing - the search did not run", file=sys.stderr)
        return 1
    if s["death_sentences_total"] == 0:
        print("::error::no death-cue sentences in any full text - extraction is broken",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
