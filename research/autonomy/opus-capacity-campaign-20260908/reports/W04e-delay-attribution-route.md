<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:10:00Z UTC
     agent id a90ddccf2533db680 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a90ddccf2533db680.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Report follows (draft in response; nothing written into the Git tree).

---

## Worker

- **Worker ID:** W04e — lane 4 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to W04d.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt, running under Claude Code 2.1.42 (`CLAUDE_CODE_VERSION=2.1.42`). I did not observe the served model; no environment variable in this container names a model. The coordinator must extract the actual per-child runtime model from the transcript.
- **`date -u` at start:** `Tue Sep  8 03:03:51 UTC 2026` · **at end:** `Tue Sep  8 03:04:59 UTC 2026`
- **`git rev-parse HEAD` at start:** `a87275c14897230041fde97c9965c9646474df7a` · **at end:** `4bd79b3bca255451dc5b25aaafa882e0ebed02e8`. HEAD moved under me mid-run (the coordinator collecting other workers' reports). **Both differ** from the `92abbcb905cacf07f14b238db50d1b98f6590374` named as frozen in `COMMON-BRIEF.md`, and both differ from W04d's start/end HEADs (`4d950cf…`/`ce743d6…`). Nothing I read is a moving target: my only repository reads are the four campaign report files and two static data files, and my substantive claims rest on PubMed retrievals performed live, not on tree state.
- **`git status --porcelain` at start:** empty. **At end:** empty. All execution under `/tmp/claude-0/w04e/` (which I created and left empty — no scratch file was needed). No git write operation of any kind; no file written anywhere in `/home/user/Rare-cancers`.
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** — literal output, abridged only by dropping the five long proxy lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`), which match the grep solely because they enumerate `api.anthropic.com` and carry no model identity:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_DEBUG=true
CLAUDE_PID=522
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_EFFORT=medium
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**Attribution (required by the PubMed tool's terms).** According to PubMed and PubMed Central, every article fact in this report was retrieved from PubMed. DOI links for the two sources I assert facts about: PMID 19890812 — [DOI](https://doi.org/10.1055/s-0028-1098788); PMID 41635359 / PMC12863220 — [DOI](https://doi.org/10.7759/cureus.100687).

---

## Question

**Is the "delay in diagnostics for 1.5 years" reported in PMID 19890812 (Mroczkowski 2009, *Zentralbl Chir*) system-side or patient-side, and does any permitted route reach the full text to decide it?** Secondarily: **is W04d's transcription of PMID 41635359 (1-month duration) correct**, given that it moves a committed reported bound below its previous minimum?

It is open because W04d found the quantity in the abstract, could not attribute it, and recorded it explicitly as UNKNOWN-as-to-attribution with the full text unobtained (no PMCID, German-language journal). The attribution is the difference between "the retrievable EMC literature quantifies a system-side diagnostic delay exactly once" and "it does not quantify one at all" — which is the load-bearing distinction in W04c's most quotable negative (`W04c:196–207`).

---

## Prior-work check

Commands actually run (from `/home/user/Rare-cancers`):

```
rg -n -i "19890812|Mroczkowski|1098788" --glob '!.git' | head -20
rg -n -i "41635359|12863220|cureus.100687" --glob '!.git' | head -20
git ls-files | rg -i "w04|delay" | head -20
rg -n -i "19890812|Mroczkowski" /tmp/claude-0/frozen-corpus/extracted/corpus | head -10
```

What they showed:

- **PMID 19890812 / Mroczkowski appears in exactly one tracked file**: `research/autonomy/opus-capacity-campaign-20260908/reports/W04d-duration-set-stability.md` (lines 102, 175, 185, 192, 207, 208, 238, 239, 256, 258, 267, 300). It appears **nowhere else in the tracked tree and nowhere in the frozen corpus** under `/tmp/claude-0/frozen-corpus/extracted/corpus`. (The two `emc-ret-cistrome-inputs.json` hits are numeric coincidences — `10987885`, `109878897` — not PMIDs.) So this paper entered the repository's knowledge only via W04d, and no prior worker attributed its delay.
- **PMID 41635359 / PMC12863220 was already in the tracked tree before W04d**, in `research/data/emc-clinical-registry.json` (as `gunasekaran2026`, `accessed 2026-06-20`, `verified true`), `research/manuscripts/citation-retraction-sweep.json`, `research/manuscripts/endpoint/meta-analysis.md:256`, and three `research/literature/emc-*-probe.json` files. **It is not a new source to the repository** — it was new only to lane 4's duration set. The registry entry carries no symptom-duration or delay field.
- `git ls-files | rg -i "w04|delay"` lists only the five campaign report files (W04, W04b, W04c, W04d, W06) — no separate delay dataset exists to contradict or duplicate.

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`): I opened no route recorded as denied. I did not touch Pazopanib, Sunitinib 2014 (`PMID 24703573` — three institutional 403 routes exhausted), Trabectedin/RT 2018, Wagner 2020, CTARC 2022, the NR4A Perspective refusal, Hofvander/EGA, Brenca, or `GSE4303`/`GSE28866`. I did not re-run W04d's vocabulary widening, did not re-derive W04c's harvest, pooled nothing into any distribution, and did not enter lane 6's molecular-confirmation question.

---

## Method / inputs

**Repository files read** (read-only, live cloud checkout at `/home/user/Rare-cancers`, HEAD as recorded above — *not* the frozen corpus, except for the one novelty grep noted):

| File | Use |
|---|---|
| `research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md` | binding rules |
| `research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md` | denied-route inventory |
| `research/autonomy/opus-capacity-campaign-20260908/CORPUS-CONTEXT.md` | frozen-corpus status |
| `…/reports/W04d-duration-set-stability.md` (lines 102, 175, 185–192, 206–208, 237–258, 263–267, 300) | the two claims under test |
| `…/reports/W04c-fulltext-duration-harvest.md` (lines 180–215) | the verdict under test, verbatim |
| `…/reports/W04b-diagnostic-delay-interval.md` | grepped for the two PMIDs (absent) |
| `research/data/emc-clinical-registry.json` | prior status of PMID 41635359 |

**Retrieval — PubMed MCP only, four calls, in this order:**

1. `convert_article_ids(ids=["19890812","41635359"], id_type="pmid")` — the identifier guard, run **first**, before any content retrieval.
2. `get_article_metadata(pmids=["19890812"])`
3. `get_copyright_status(pmids=["19890812"])`
4. `find_related_articles(pmids=["19890812"], link_type="pubmed_pmc", max_results=10)`
5. `get_full_text_article(pmc_ids=["PMC12863220"])`

No web fetch, no publisher route, no mirror search, no paid API, no GPU.

**Identifier guard, RUN — verbatim result:**

```
{"status":"ok","response-date":"2026-09-07 23:04:15",
 "request":{"warnings":[],"format":"json","idtype":"pmid","ids":["19890812","41635359"],...},
 "records":[{"pmid":"19890812","requested-id":"19890812"},
            {"pmcid":"PMC12863220","pmid":"41635359","doi":"10.7759/cureus.100687","requested-id":"41635359"}]}
```

Both `requested-id` values match their returned `pmid` exactly. **Zero mismatches; nothing discarded.** Note the guard itself returns **no PMCID and no DOI for 19890812** — the DOI `10.1055/s-0028-1098788` comes from the metadata record, and its absence from the ID-converter response is consistent with a non-PMC, publisher-held record.

---

## Result

### 1. Access status of PMID 19890812 — no permitted route exists

| Probe | Result | Evidence | Label |
|---|---|---|---|
| ID converter returns a PMCID? | **No** | record is `{"pmid":"19890812","requested-id":"19890812"}` — no `pmcid` key | PRIMARY |
| PMC link exists (`pubmed_pmc`)? | **No** | `{"linksets":[{"dbfrom":"pubmed","ids":["19890812"]}]}` — linkset present, **zero linked PMC ids** | PRIMARY |
| Copyright / open-access status | **Not open access**, publisher-held | `"copyright":{"statement":"Georg Thieme Verlag Stuttgart, New York."}`, `"license":{"type":null,"url":null,"is_open_access":false}`, `"found_in_pmc":0` | PRIMARY |
| Any other permitted route | **None** | Retrieval is PubMed MCP only; PubMed MCP's only full-text path is `get_full_text_article`, which requires a PMC ID that does not exist. A Thieme publisher route and any mirror are outside the permitted set and explicitly excluded by my task | — |

**VERDICT (access): UNRECOVERED. The full text of PMID 19890812 is not reachable by any permitted route, and I stopped rather than reroute.** Per the campaign brief, this is an honest unrecovered source, not a hurdle to circumvent, and the empty PMC linkset is **UNKNOWN, not proof that no full text exists anywhere**.

### 2. Attribution of the 1.5-year delay — UNKNOWN, and the abstract cannot settle it

I retrieved the complete PubMed abstract (English-language abstract of a German-language article; `"language":"ger"`, `"article_types":["Case Reports","English Abstract","Journal Article"]`). The delay sentence, **verbatim**:

> "After a delay in diagnostics for 1.5 years, an MRI scan taken in a 42-year-old male patient with progressive swelling of the left calf showed a soft-tissue tumour in the proximal part of the muscle."

| Question | Answer | Label |
|---|---|---|
| Does the abstract state a delay quantity? | **Yes — 1.5 years, explicitly labelled "delay in diagnostics"** | PRIMARY |
| Does the abstract say whose delay it was? | **No.** The sentence names no actor, no first-contact date, no referral, no prior misreading, no patient decision. The abstract's other intervals are all post-diagnosis (discharge at 8 days, radiotherapy at 4 weeks, follow-up 28 months) | PRIMARY |
| System-side or patient-side? | **UNKNOWN** | UNKNOWN |
| Is there a full-text route to decide it? | **No permitted route** (section 1) | PRIMARY |

**I record one contextual signal and refuse to convert it into an answer.** The abstract's closing sentence reads, verbatim: *"Each persistent soft tissue swelling must be appropriately diagnosed using adequate imaging and even biopsy (in case of a doubtful finding), which should be performed with definitive surgery in mind."* That closing is addressed to clinicians and concerns diagnostic workup, which is weakly more consistent with a system-side reading than a patient-side one. **This is a rhetorical inference about how the authors framed their case, not evidence about the interval**, and I am explicitly not scoring it: a case report can draw a workup lesson from a patient who presented late just as readily as from a workup that missed. An ambiguous source is an honest UNKNOWN, not a coin flip. **The attribution stays UNKNOWN.**

**No clinical claim.** The 1.5 years describes what one 2009 case report stated about one patient. It is not prognosis, it is not evidence that delay caused harm, and it implies nothing about what care should look like. No recommendation is made or intended here.

### 3. What W04c's verdict should become — precise wording

W04c's verdict, verbatim at `W04c:~206`: *"**VERDICT: no source quantifies a system-side diagnostic delay.** Zero of four retrievable EMC misdiagnosis narratives states the time the misreading cost."*

| Component of W04c's claim | Status after this run | Label |
|---|---|---|
| "Zero of four retrievable EMC misdiagnosis narratives states the time the misreading cost" | **STANDS UNCHANGED.** PMID 19890812 is not one of those four narratives and reports no misdiagnosis at all — its abstract describes no prior misreading, and its MeSH terms and text show a workup that went MRI → percutaneous biopsy → en-bloc resection. W04c's denominator is untouched | PRIMARY |
| The sentence-initial general form "**no source quantifies a system-side diagnostic delay**" | **DOES NOT SURVIVE AS WRITTEN — but it is not refuted either.** It should not be read as established, because a source now exists that quantifies *a* diagnostic delay (1.5 years) whose side is unknown. It is equally not shown false, because that source may be patient-side | UNKNOWN |
| W04b/W04c's downstream constraint: *"any claim that diagnostic delay drives EMC presentation stage remains unsupported by the primary literature in either direction"* | **STANDS, and is if anything strengthened** — the one quantity that exists cannot be attributed to a side, so it supports no directional claim | PRIMARY |

**Recommended replacement wording for `W04c:206`** (a focused correction appended to W04c, per `CORPUS-CONTEXT.md` §4 — not a new review round):

> **VERDICT: zero of four retrievable EMC misdiagnosis narratives states the time the misreading cost.** Exactly one EMC source anywhere in the retrievable corpus states a labelled diagnostic-delay quantity — PMID 19890812 (Mroczkowski 2009), *"a delay in diagnostics for 1.5 years"* — and **whether that delay was system-side or patient-side is UNKNOWN and unresolvable by permitted routes** (no PMCID, no PMC link, Thieme-held, not open access; W04e). The one long interval that is attributed anywhere — the 30 years in PMID 35494187 — is explicitly patient-side by its own authors. **No system-side delay interval has been established in the retrievable literature; none has been excluded either.**

The operative change is narrow and worth stating plainly: **W04c's negative moves from "the literature contains no such number" to "the literature contains exactly one such number, and it cannot be attributed."** Its practical consequence for the manuscript is nil — one unattributable value from one 2009 case report supports no distribution, no rate and no direction — but the earlier absolute phrasing is no longer quotable and should not be quoted.

### 4. Independent check of PMID 41635359 — W04d's transcription is exact, but its *anchor* is not the only defensible one

I read the PMC12863220 full text directly. The relevant sentences, **verbatim**:

> "The palpable non-tender abdominal mass had been present for one month. The patient reported five to six months of significant fatigue."

| Check | Result | Label |
|---|---|---|
| W04d's quoted sentence is verbatim-accurate | **Yes — character-for-character** | PRIMARY |
| W04d's "1 mo" value, on a *mass-noticed → presentation* anchor | **Correct** | PRIMARY |
| W04d's "EMC FISH-confirmed, NR4A3/EWSR1" characterisation | **Correct**: *"A core needle biopsy of the right iliac fossa mass confirmed extra-skeletal myxoid chondrosarcoma associated with NR4A3 and EWSR1 rearrangement on FISH studies."* | PRIMARY |
| W04d's "hyphenated *Extra-skeletal* in the title" claim | **Correct**: title is *"A Case Report of a Patient Presenting With Extra-skeletal Myxoid Chondrosarcoma"* | PRIMARY |
| **Is 1 month the only defensible duration this paper supports?** | **No — and this qualifies the bound W04d moved** | PRIMARY |

**The finding that justifies the check.** W04d used this paper's 1 month to extend lane 4's committed range below its previous minimum (2 mo → 1 mo). The value is transcribed correctly, but the same paragraph reports **five to six months of significant fatigue in the same patient**. Under a *mass-noticed* anchor the value is 1 month; under a *first-symptom* anchor it is 5–6 months, and **the minimum of the committed set would not move at all**. So:

- W04d's stated anchor ("mass noticed → presentation") is applied consistently and its arithmetic is sound. I am not calling it wrong.
- But **the new minimum of 1 month is anchor-dependent, and the paper itself supplies the longer alternative.** Any downstream use of "range 1–360 months" must carry that caveat, or the bound reads as harder than the source makes it. This is exactly the class of fragility W04b and W04c flagged: the value that enters a distribution is chosen by an anchor convention, not read off the patient.
- Separately, and relevant to how "new" this source is: **PMC12863220 was already tracked in `research/data/emc-clinical-registry.json` as `gunasekaran2026` (verified, accessed 2026-06-20)** before W04d. W04d's widening surfaced a *duration* from an already-known paper; it did not discover the paper. That does not diminish W04d's result, but the campaign record should not describe it as a newly discovered source.

---

## Validation evidence

**RUN** — environment: Claude Code 2.1.42, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux, cwd `/home/user/Rare-cancers`.

| # | Command / call | Exit / status | Key verbatim output |
|---|---|---|---|
| 1 | `date -u; env \| grep …; git rev-parse HEAD; git status --porcelain; mkdir -p /tmp/claude-0/w04e` | 0 | start `Tue Sep  8 03:03:51 UTC 2026`; HEAD `a87275c1…`; status **empty**; `ok` |
| 2 | `ls -la` on the campaign dir and `reports/` | 0 | 60 report files present, incl. `W04d-duration-set-stability.md` (33321 bytes, 03:02) |
| 3 | `cat COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md` | 0 | read in full |
| 4 | `sed -n '1,400p' W04d-duration-set-stability.md` | 0 | 32.5 KB, persisted to tool-results |
| 5 | `grep -n -i -E "19890812\|41635359\|12863220\|Mroczkowski\|1\.5 year\|delay in diagnostic" W04d… W04c… W04b…` | 0 | 12 hits, all in W04d; **zero in W04b, zero in W04c** |
| 6 | `sed -n '180,215p' W04c-fulltext-duration-harvest.md` | 0 | verdict quoted above, verbatim |
| 7 | `rg` novelty greps + `git ls-files` + frozen-corpus grep | 0 | see Prior-work check |
| 8 | `mcp__PubMed__convert_article_ids` (guard) | `"status":"ok"` | quoted in full above; 2/2 ids match, 0 mismatches |
| 9 | `mcp__PubMed__get_article_metadata(["19890812"])` | `"count":1` | delay sentence + closing sentence quoted verbatim above; `"language":"ger"`, journal `Zentralbl Chir` 135(1):83-6, 2009-11-04, authors Mroczkowski/Evert/Tautenhahn/Meyer/Lippert |
| 10 | `mcp__PubMed__get_copyright_status(["19890812"])` | `"count":1` | `"pmc_id":null`, `"is_open_access":false`, `"found_in_pmc":0`, Thieme |
| 11 | `mcp__PubMed__find_related_articles(["19890812"], "pubmed_pmc")` | ok | `{"linksets":[{"dbfrom":"pubmed","ids":["19890812"]}]}` — **no linked PMC id** |
| 12 | `mcp__PubMed__get_full_text_article(["PMC12863220"])` | `"count":1` | full text retrieved; the two duration sentences quoted verbatim above |
| 13 | `python3 -c "json.load(emc-clinical-registry.json)…"` | 0 | `gunasekaran2026` entry printed, no duration field |
| 14 | `date -u; git rev-parse HEAD; git status --porcelain; ls -la /tmp/claude-0/w04e` | 0 | end `Tue Sep  8 03:04:59 UTC 2026`; HEAD `4bd79b3b…`; status **empty**; scratch dir **empty** |

**PROPOSED (NOT RUN), and deliberately not run:** any Thieme/publisher route to `10.1055/s-0028-1098788`; any mirror, aggregator or interlibrary route; any `pubmed_pubmed` similar-article sweep hunting for an English republication of the Mroczkowski case. My task forbids rerouting and mirror-hunting once no permitted route exists, and `CLOSED-WORK.md` forbids replaying denied routes. **No content-policy refusal was encountered at any point in this run.**

---

## Limitations

- **The central question is not answered.** The attribution of the 1.5-year delay is UNKNOWN and remains so. I established *that no permitted route exists*, which is a real and checkable negative, but it is a negative about access, not about the delay.
- **"No permitted route" is not "no route."** The full text plainly exists in *Zentralbl Chir* 135(1):83-6. My finding is that PubMed MCP cannot reach it and that everything else is out of bounds for this campaign. A future run with different, properly authorized access could resolve it; nothing here licenses opening one.
- **An empty PMC linkset is UNKNOWN, not proof of absence** — of a full text, of a deposit, or of an English-language companion publication.
- **n=1 throughout.** One 2009 case report; one 2026 case report. Neither supports a rate, a distribution, a median, or a comparison. I pooled nothing, and the W04b/W04c framing stands: these are publication decisions, not a sample of patients.
- **No clinical inference of any kind.** No prognosis, no claim that delay caused harm, no statement about what care should look like, no recommendation, explicit or implied.
- **The anchor problem I raise for PMID 41635359 is a caveat, not a correction.** W04d applied its declared anchor correctly; I am flagging that the resulting minimum is anchor-dependent and that the source offers a longer alternative interval for the same patient.
- **Model identity is self-report only** and my read HEAD differed from the brief's declared frozen commit and moved during the run.
- I did not verify W04d's 34-record widening, W04c's harvest, or any lane-6 material — all out of scope by instruction.

---

## Stop condition

**Set up front, before retrieval:** *Stop as soon as the deposit/access status of PMID 19890812 is established by permitted routes — either the full text is read and the delay attributed, or no permitted route exists and it is recorded UNRECOVERED/UNKNOWN — and the PMID 41635359 transcription is independently checked against its PMC full text.*

**MET, on the negative branch.** Three independent permitted probes (ID converter, `pubmed_pmc` linkset, copyright/PMC status) agree: no PMCID, no PMC link, publisher-held and not open access. I stopped at that point rather than reroute. The secondary check was completed and returned a verbatim match plus one substantive anchor caveat. I returned immediately on meeting the condition; no padding, no extra branches.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 14** (8 Bash, 2 ToolSearch, 4 PubMed MCP) — well under the ~40 target.
- **Wall clock: ~68 seconds of recorded span** (`03:03:51Z` → `03:04:59Z` by `date -u`), against a ~40-minute target. The run was short because the access question resolved negatively and cleanly on the first three probes, and the brief directs returning the moment the stop condition is met.

---

## Next concrete action

**One successor, finite and in-lane: apply the focused correction to `W04c:196–207` and to `W04d`'s Table row for 41635359 — coordinator-side, no new retrieval.** Specifically: (a) replace W04c's absolute sentence *"no source quantifies a system-side diagnostic delay"* with the replacement wording drafted in Result §3, which preserves W04c's four-narrative denominator intact while retiring the general form; (b) annotate W04d's 41635359 row so the 1-month minimum carries its anchor dependence and the source's own 5–6-month fatigue interval; (c) note in the campaign record that PMC12863220 was already tracked in `research/data/emc-clinical-registry.json` before W04d. This needs no source access and closes the loop W04d opened.

**And an explicit non-successor:** there is **no viable retrieval successor for PMID 19890812 in this lane**, because every remaining route to its full text is either outside the permitted PubMed-MCP set or a mirror/publisher route this campaign forbids. It should be carried as a standing **UNRECOVERED / attribution-UNKNOWN** entry, not re-attempted by a later worker under a new label.
