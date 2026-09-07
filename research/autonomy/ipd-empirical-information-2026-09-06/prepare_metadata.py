"""Read identifiers/schema only. Never access time/status or summary-outcome values."""
import csv, hashlib, io, json, pathlib, zipfile
HERE=pathlib.Path(__file__).resolve().parent
ARCHIVE=pathlib.Path('C:/Users/mcrae/.codex/worktrees/ipd-baselines-20260906/EMC-Research/.cache/RealIPD.zip')
def digest(b): return hashlib.sha256(b).hexdigest()
def main():
    raw=ARCHIVE.read_bytes()
    assert digest(raw)=='60d8ea495aa958fb53cd63de807325026fd89184f980349221ec76ebe6890f40'
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        subgroup=list(csv.DictReader(io.TextIOWrapper(z.open('RealIPD/RIPD_subGroup.csv'),encoding='utf-8-sig')))
        identifiers=[{'curve_id':r['km_curve_id'],'source':r['group']} for r in subgroup]
        tcga=[r for r in identifiers if r['source'].startswith('TCGA-')]
        ids={}; schemas={}
        for r in tcga:
            n='RealIPD/IPD/'+r['curve_id']+'.csv'
            reader=csv.DictReader(io.TextIOWrapper(z.open(n),encoding='utf-8-sig'))
            schemas[n]=reader.fieldnames
            # Parsing a CSV necessarily reads each record's bytes; only id is accessed.
            values=[row['id'] for row in reader]
            assert all(v.startswith('TCGA-') and len(v.split('-'))==3 for v in values)
            assert len(values)==len(set(values)), 'duplicate patient IDs within a source'
            ids[r['source']]=set(values)
        components=[]
        for r in tcga:
            overlapping=[c for c in components if any(ids[r['source']]&ids[s] for s in c)]
            merged={r['source']}
            for c in overlapping: merged.update(c);components.remove(c)
            components.append(merged)
        ranked=sorted(components,key=lambda c:digest(('20260906|'+ '|'.join(sorted(c))).encode()))
        groups=[]
        for i,c in enumerate(ranked):
            gid='|'.join(sorted(c))
            groups.append({'source_group':gid,'split':'development' if i<10 else 'reserved_unopened',
                'curves':[r for r in tcga if r['source'] in c],
                'identifier_union_sha256':digest('\n'.join(sorted(set().union(*(ids[s] for s in c)))).encode())})
        out={'schema':'outcome-blind-source-manifest-v1','archive':str(ARCHIVE),'archive_sha256':digest(raw),
             'metadata_columns':list(subgroup[0]),'ipd_schemas':schemas,'all_identifiers':identifiers,
             'source_groups':groups,'quarantine':'All GEO curves: cross-series alias/provenance verification deferred.',
             'unit_policy':'Source units absent from inspected metadata; no cross-source time comparison. Each pseudoarm pair uses one cohort and common original time scale.',
             'outcome_access':'Only source labels, curve IDs, CSV headers and TCGA patient IDs accessed. No time/status or summary-outcome values inspected.',
             'source':'https://doi.org/10.5281/zenodo.18320575','license':'CC-BY-4.0'}
        (HERE/'source-manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'tcga_components':len(groups),'development':sum(g['split']=='development' for g in groups),'manifest_sha256':digest((HERE/'source-manifest.json').read_bytes())}))
if __name__=='__main__': main()
