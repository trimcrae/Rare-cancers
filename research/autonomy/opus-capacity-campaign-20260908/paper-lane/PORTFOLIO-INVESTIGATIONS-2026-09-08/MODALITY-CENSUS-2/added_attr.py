import json
new=json.load(open('research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/MODALITY-CENSUS-2/census-novelty-audit.REGENERATED.json'))
old=json.load(open('research/modalities/census-novelty-audit.json'))
added=sorted(set(new['findings'])-set(old['findings']))
print("For each of the 13 newly-colliding ids: are ALL its top matching files campaign-lane files?")
for k in added:
    fs=list(new['findings'][k]['files_matching_two_or_more_terms'])
    camp=[f for f in fs if f.startswith('research/autonomy/')]
    print(f"  {k:<28} n_files={new['findings'][k]['n_files']:>3}  top8 shown={len(fs)}  under research/autonomy/={len(camp)}")
    for f in fs[:3]: print(f"       {f}")
