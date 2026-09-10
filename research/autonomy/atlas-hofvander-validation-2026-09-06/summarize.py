"""Report already-completed frozen results; no raw expression access or reanalysis."""
from pathlib import Path
import csv,json,hashlib
P=Path(__file__).parent
def writecsv(name,rows):
    with (P/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def direction(a):return 'undefined' if a is None else 'positive' if a>.5 else 'negative' if a<.5 else 'neutral'
def front(ident,title):return f'''---
id: DOC-{ident}
title: {title}
level: cross-cutting
kind: memo
status: live
canonical_for: []
purpose: Report every prespecified gene and contrary sensitivity from the completed frozen analysis.
scope: Single-cohort tissue RNA prioritization and separate shared-histology array replication.
audience: [autonomous research agents, external reviewers]
date: "2026-09-06"
last_verified: "2026-09-06"
related: [DOC-ATLAS-HOFVANDER-VALIDATION-20260906]
---

'''
def main():
    a=json.loads((P/'results/result.json').read_text());b=json.loads((P/'replication-results/result.json').read_text());panel=[];contrasts=[];sensitivity=[];rep=[];cells=[]
    for g,r in a['genes'].items():
        ints=r['bootstrap_pointwise_conditional_95']['summary'];anchor=b['genes'][g]['contrasts']['Low-grade fibromyxoid sarcoma']
        panel.append({'gene':g,'role':r['role'],'Hof_marginal_A':r['primary']['summary']['marginal'],'Hof_marginal_pointwise_conditional95_low':ints['marginal'][0],'Hof_marginal_pointwise_conditional95_high':ints['marginal'][1],'Hof_matched_A':r['primary']['summary']['matched'],'Hof_matched_pointwise_conditional95_low':ints['matched'][0],'Hof_matched_pointwise_conditional95_high':ints['matched'][1],'array_LGFMS_A':anchor['array']['A'],'Hof_LGFMS_A':anchor['hofvander']['summary']['marginal'],'Hof_LGFMS_matched_A':anchor['hofvander']['summary']['matched'],'allocation_pass':r['allocation_rule'].get('consistent_RNA_rationale','context_not_applied')})
        for group in ['primary','context']:
            for h,v in r[group]['histologies'].items():
                it=r['bootstrap_pointwise_conditional_95'].get(h,{})
                contrasts.append({'gene':g,'role':r['role'],'group':group,'histology':h,'n_emc':v['n_emc'],'n_comparator':v['n_comparator'],'n_matched_emc':v['matched_emc'],'marginal_A':v['marginal'],'marginal_direction':direction(v['marginal']),'matched_A':v['matched'],'matched_direction':direction(v['matched']),'marginal_conditional_interval':json.dumps(it.get('marginal')),'matched_conditional_interval':json.dumps(it.get('matched'))})
                for c in v['cells']:cells.append({'gene':g,'histology':h,**c})
        for kind,ds in r['deletions'].items():
            for d in ds:
                sensitivity.append({'gene':g,'deletion_type':kind,'deleted':d['deleted'],'marginal_A':d['summary']['marginal'],'marginal_direction':direction(d['summary']['marginal']),'matched_A':d['summary']['matched'],'matched_direction':direction(d['summary']['matched'])})
        for h,c in b['genes'][g]['contrasts'].items():
            rr={'gene':g,'gene_role':r['role'],'histology':h,'contrast_role':c['role'],'array_n_emc':c['array']['n_emc'],'array_n_comparator':c['array']['n_comparator'],'array_A':c['array']['A'],'array_direction':c['array']['direction'],'array_EMC_deletion_range':json.dumps(c['array']['deletion_ranges']['EMC']),'array_comparator_deletion_range':json.dumps(c['array']['deletion_ranges']['comparator']),'Hof_A':c['hofvander']['summary']['marginal'],'Hof_direction':direction(c['hofvander']['summary']['marginal']),'Hof_matched_A':c['hofvander']['summary']['matched'],'Hof_matched_direction':direction(c['hofvander']['summary']['matched'])}
            for typ,ds in c['hofvander_deletions'].items():
                for mode in ['marginal','matched']:
                    vs=[d['summary'][mode] for d in ds];vs=[x for x in vs if x is not None];rr[f'Hof_{typ}_{mode}_deletion_range']=json.dumps([min(vs),max(vs)] if vs else None)
            rep.append(rr)
    writecsv('all12-gene-effects.csv',panel);writecsv('all-hofvander-contrasts.csv',contrasts);writecsv('all-primary-deletions.csv',sensitivity);writecsv('all-year-cells.csv',cells);writecsv('all-shared-histology-replication.csv',rep)
    table='| Gene | Hof marginal A [conditional95%] | Hof matched A [conditional95%] | LGFMS array / Hof / matched | Frozen rule |\n|---|---|---|---|---|\n'
    for r in panel:
        table+=f"| {r['gene']} | {r['Hof_marginal_A']:.3f} [{r['Hof_marginal_pointwise_conditional95_low']:.3f},{r['Hof_marginal_pointwise_conditional95_high']:.3f}] | {r['Hof_matched_A']:.3f} [{r['Hof_matched_pointwise_conditional95_low']:.3f},{r['Hof_matched_pointwise_conditional95_high']:.3f}] | {r['array_LGFMS_A']:.3f} / {r['Hof_LGFMS_A']:.3f} / {r['Hof_LGFMS_matched_A']:.3f} | {r['allocation_pass']} |\n"
    report=front('ATLAS-HOFVANDER-RESULT-20260906','Frozen tissue RNA checkpoint results')+'''CSPG4 is the only one of11 address genes meeting the frozen Hofvander tissue-validation allocation rule. Its all9-EMC equal-histology probability of superiority is0.89454 and its year-matched summary is0.81111. The result is materially year-sensitive: deleting2019 lowers the matched summary to0.43333, while the marginal summary remains0.83333. This supports a **qualified tissue-validation rationale**, not a batch-robust or universally EMC-specific enrichment claim. CHRNA6 has A=1 across the three primary contrasts, but was a separate prior-supported control and does not count as address-panel success.

The primary shared-histology LGFMS anchor agrees for CSPG4: original array A=1.000 (6 EMC biopsies versus17 LGFMS), Hofvander marginal A=0.96581 (9 versus13), and matched A=0.93333 (3 supported EMC). Array LGFMS direction survives every single-biopsy deletion. Separately, CSPG4 array A=1 versus MFS, SFT and desmoid; Hofvander marginal/matched estimates are0.85370/0.85714,0.87879/0.62500 and1/1 respectively. These are named comparator results, not a cross-cohort composite or proof of universally independent recruitment.

## Full fixed panel

Higher A means higher EMC ranks;0.5 means neutral pair ordering including half ties. Hof summaries weight MLPS,LGFMS,synovial equally. Marginal uses9 EMC; matched uses3 EMC per contrast, union4. Intervals are pointwise2000-resample bootstrap percentiles, conditional on observed year strata; singleton strata stay fixed and can yield misleadingly narrow/degenerate intervals. They are not simultaneous confidence claims, clinical intervals or statistical discovery thresholds. Full precision is retained in CSV/JSON. L1CAM rounds to0.699 here and remains below the frozen0.70 benchmark; no rounding was used in the rule.

'''+table+'''
## Contrary evidence and sensitivity

CSPG4 is not higher than DFSP on the marginal comparison (A=0.46667); this context was not part of the pass rule and is retained. The DFSP matched contrast is only1 EMC versus3 comparators. CSPG4's leave-one-EMC-out equal-histology ranges are0.88136–0.94035 marginal and0.71667–0.94444 matched; leave-one-histology-out ranges0.85891–0.94896 and0.75000–0.88333. Comparator-patient deletion ranges are0.88905–0.89976 and0.80317–0.83333. Year deletion ranges are0.83333–0.94618 and0.43333–0.94444, exposing the2019 dependence. Revised-diagnosis sensitivity gives0.89475 marginal and0.81111 matched, but partly expression-informed revisions cannot supersede original labels.

All10 other address genes fail the original broad allocation rule. PRAME and L1CAM are positive against LGFMS in both cohorts yet weak/reversed against other primary Hofvander histologies. MSLN, SSTR2, GPC3 and FAP have opposed array-versus-Hofvander LGFMS directions. CD276, CD248 and CDH17 remain negative against LGFMS in both cohorts. ALPP has positive marginal LGFMS directions but exactly neutral matched A=0.5. These directions narrow the biological question rather than being dropped as inconvenient targets. Complete primary/context directions, all individual year cells, all deletions and all48 shared-histology contrasts are provided in the tables below and original JSON.

## Sources, reproducibility and scope

Primary sources are [Hofvander2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13133608/), its [author data v1.0.1](https://github.com/JakobHofvander/Transcriptomic_subgroups_in_soft_tissue_tumors_correlate_with_morphologic_subtype_genomic_features/tree/v1.0.1), [GSE24369](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369), and [GPL6244](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL6244). Exact original source hashes, sample/lesion decisions and unique probes are frozen in metadata-manifest.json and replication-manifest.json. All42 array samples were parsed from original SOFT values at full released precision; MFS and SFT source-label corrections were frozen before outcomes. Array biopsies have unknown lesion stage and no universal patient crosswalk. Two pooled skeletal muscle RNAs are descriptive only, not evidence of normal-organ safety. GSE4303 was not treated as abundance replication.

Both authorized processes completed once with exit0. Raw logs, command times/elapsed, exact authorization and execution states are preserved in analyze-run.log,analyze-command.json,replication-run.log,replication-command.json and each output directory. There were no empirical errors, repairs, reruns or tuning. Initial arithmetic fixtures and replication parser/rank fixtures passed before outcomes. summarize.py reads completed outputs only; original analyze.py and replication.py remain unchanged. Independent raw-source arithmetic review is pending at the time of this memo; no manuscript-ready or publication claim is made. No process remains running.

Useful next interpretation is CSPG4 tissue protein/localization assessment in relevant EMC material with explicit batch and DFSP context, alongside CHRNA6 as a separate established-context signal. Bulk RNA cannot distinguish malignant-cell expression from stroma/immune composition, prove normal sparing, demonstrate a therapeutic window or establish efficacy. Source convenience sampling and partial overlap evidence further limit generalization.

Files: all12-gene-effects.csv (compact effects/conditional intervals); all-hofvander-contrasts.csv (all60 initial gene×histology effects); all-year-cells.csv (unsupported and singleton cells retained); all-primary-deletions.csv (every deletion summary); all-shared-histology-replication.csv (all48 cohort comparisons and deletion ranges). results/ and replication-results/ preserve full patient values/placements and individual sensitivities. No candidate or unfavorable comparison was removed.
'''
    (P/'result.md').write_text(report,encoding='utf-8')
    root=Path('C:/Users/mcrae/.codex/worktrees/8010/EMC-Research')
    context=root/'.cache/atlas-normal-context-recovery-20260906'
    normal=json.loads((context/'fixed-panel-normal-context-roster.json').read_text())
    assert {r['gene'] for r in normal}==set(a['genes'])
    context_text='''## Separate normal-expression context; no change to frozen analysis

The new12-gene [HPA source roster](C:/Users/mcrae/.codex/worktrees/8010/EMC-Research/.cache/atlas-normal-context-recovery-20260906/fixed-panel-normal-context-roster.json) is joined by the fixed symbols for interpretation only. Its original XML entries are version25; current HPA methods/download pages describe25.1/Ensembl109. Exact response hashes and retrieval provenance remain in that source packet; this is not a tumor/normal matched comparison. HPA consensus tissue RNA takes maxima across HPA/GTEx sources and grouped sub-tissues, not an independent cohort average. No nTPM/TPM safety ratio, normal-sparing label or membrane-accessibility verdict is computed.

| Gene | Normal tissue IHC reliability | Missing/discordant context retained |
|---|---|---|
'''
    constraints={
      'CD276':'Broad normal cytoplasmic/membranous IHC versus vesicle ICC/IF.',
      'SSTR2':'Brain context; uncertain IHC and intracellular ICC/IF.',
      'PRAME':'Testis-associated evidence; nucleoplasm/membrane tags do not establish intact surface accessibility or EMC peptide-HLA presentation.',
      'FAP':'Uncertain IHC; missing ICC/IF is not absent membrane protein; stromal source unresolved.',
      'CD248':'Normal cell-type/membrane annotations do not identify the EMC compartment.',
      'CSPG4':'Broad cytoplasmic normal IHC; membrane ICC/IF does not establish normal sparing or EMC accessibility.',
      'MSLN':'Normal epithelial staining; mesothelial surfaces are not comprehensively surveyed.',
      'L1CAM':'CNS/PNS and renal-tubule normal context retained.',
      'GPC3':'No normal tissue-IHC summary/cell rows; placenta RNA and membrane ICC/IF are not adult protein-absence evidence.',
      'ALPP':'Placental/cervical RNA and trophoblast IHC; antibody multi-gene cross-reactivity retained.',
      'CDH17':'Gastrointestinal epithelial protein and differing intracellular/junction tags retained.',
      'CHRNA6':'Retinal RNA enrichment; no tissue-IHC rows/ICC summary, not evidence of absent normal neural protein.'}
    by_gene={r['gene']:r for r in normal}
    for g in a['genes']:
        r=by_gene[g];context_text+=f"| [{g}]({r['xml_versioned_url']}) | {r.get('normal_IHC_reliability') or 'missing'} | {constraints[g]} |\n"
    context_text+='''
The previously independently verified [GSE28866 sample/organ report](../atlas-sample-organ-2026-09-06/report.md) is historical evidence under a different, cancer-selected3SEQ peak estimand. CSPG4's positive medians coexist with an individual normal-colon record exceeding the lowest EMC library value. CHRNA6 is nonuniform in those peak records despite the present array/TPM direction. Those four EMC library records are not four newly established independent patients. No unchanged3SEQ analysis was rerun, no peak-scale quantity pooled with the present ranks, and no result from normal context altered panel membership or the frozen rule.

'''
    report=report.replace('## Sources, reproducibility and scope',context_text+'## Sources, reproducibility and scope')
    report=report.replace('Independent raw-source arithmetic review is pending at the time of this memo; no manuscript-ready or publication claim is made.','An independent reader separately parsed original sources and reported zero discrepancies across8,448 Hofvander values,504 array values,2,436 estimate/deletion blocks and266,772 scalar comparisons. This verifies arithmetic and the frozen gate, not biological independence or localization; no manuscript-ready or publication claim is made.')
    (P/'result.md').write_text(report,encoding='utf-8')
    files=[context/'fixed-panel-normal-context-roster.json',context/'normal-context-memo.md',context/'file-manifest.json',root/'research/autonomy/atlas-sample-organ-2026-09-06/report.md']
    (P/'interpretation-context-references.json').write_text(json.dumps({str(f):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'use':'interpretation only; no frozen selection/analysis modification'} for f in files},indent=2)+'\n')
    manifest={f.relative_to(P).as_posix():{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in P.rglob('*') if f.is_file() and f.name!='packet-manifest.json'}
    (P/'packet-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
