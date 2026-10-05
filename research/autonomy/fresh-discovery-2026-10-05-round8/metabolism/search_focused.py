import search_sources as s
s.QUERIES={
 'EMC_TITLE_ABS':'TITLE_ABS:"extraskeletal myxoid chondrosarcoma" AND TITLE_ABS:(ferroptosis OR GPX4 OR SLC7A11 OR cystine OR glutathione OR lipid OR oxidative OR metabolism OR metabolomics)',
 'EMC_GENE_TITLE_ABS':'TITLE_ABS:("myxoid chondrosarcoma" OR "NCC-EMC1-C1" OR "USZ20-EMC1" OR "USZ22-EMC2" OR "TFG-TEC" OR "EWSR1-NR4A3") AND TITLE_ABS:(ferroptosis OR GPX4 OR SLC7A11 OR cystine OR glutathione OR lipid OR oxidative OR metabolism OR enolase)',
 'SARCOMA_FERRO_TITLE_ABS':'TITLE_ABS:(sarcoma AND ferroptosis)',
 'EMC_FULL_FERRO':'"extraskeletal myxoid chondrosarcoma" AND (GPX4 OR SLC7A11 OR erastin OR RSL3 OR ferrostatin OR liproxstatin)',
 'EMC_REDOX_SPECIFIC':'"extraskeletal myxoid chondrosarcoma" AND ("lipid peroxidation" OR "cystine deprivation" OR "oxygen consumption" OR "glutamine dependency" OR "metabolic flux")',
 'MESENCHYMAL_FERROSTUDIES':'TITLE_ABS:(GPX4 AND (mesenchymal OR sarcoma))',
 'AUTHENTIC_MODEL_NEW':'"USZ" AND "extraskeletal myxoid chondrosarcoma"'
}
out=list(s.concurrent.futures.ThreadPoolExecutor(max_workers=4).map(s.fetch,s.QUERIES.items()))
(s.BASE/'FOCUSED-SEARCH-RECEIPTS.json').write_text(s.json.dumps([r for r,_ in out],indent=2)+'\n')
(s.BASE/'FOCUSED-SEARCH-CANDIDATES.json').write_text(s.json.dumps({r['key']:v for r,v in out},indent=2)+'\n')
for r,v in out:print(r['key'],r.get('hit_count'),len(v),r.get('error',''))
