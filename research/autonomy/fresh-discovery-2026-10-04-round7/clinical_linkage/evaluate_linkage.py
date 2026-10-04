"""Reproduce source-level linkage gate. No pooled patient estimate or treatment test.
Run with --inbrx pointing to the retained independent-worker primary XML.
"""
import argparse, collections, datetime, hashlib, json, pathlib, re
import xml.etree.ElementTree as ET

D = pathlib.Path(__file__).resolve().parent

def text(e):
    return ' '.join(''.join(e.itertext()).split())

def read(path):
    b = path.read_bytes()
    return ET.fromstring(b), {'file': str(path), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def tables(root):
    out = []
    for t in root.findall('.//table-wrap'):
        out.append({'id': t.get('id'), 'caption': text(t.find('caption')) if t.find('caption') is not None else '',
                    'rows': [[text(c) for c in r if c.tag in ('td','th')] for r in t.findall('.//tr')],
                    'footnotes': [text(x) for x in t.findall('./table-wrap-foot')]})
    return out

def paras(root, terms):
    return [text(p) for p in root.findall('.//body//p') if any(x.lower() in text(p).lower() for x in terms)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inbrx', type=pathlib.Path, required=True)
    ap.add_argument('--chiusole', type=pathlib.Path, required=True)
    a=ap.parse_args()
    sources={}
    ant,sources['anthracycline2013']=read(D/'anthracycline2013.xml')
    su,sources['sunitinib2012']=read(D/'sunitinib2012.xml')
    tm,sources['temozolomide2017']=read(D/'temozolomide2017.xml')
    dv,sources['davis2017']=read(D.parents[1]/'fresh-discovery-2026-10-04-round2'/'genomics'/'davis2017.xml')
    ib,sources['inbrx2023']=read(a.inbrx)
    ch,sources['chiusole2020']=read(a.chiusole)
    antt=tables(ant)
    ar=next(t['rows'] for t in antt if t['id']=='T2')
    cases=[dict(zip(ar[0],r)) for r in ar[1:] if len(r)==len(ar[0]) and r[0].isdigit()]
    assert len(cases)==11
    assert all(r['NR4A3 rearrangement']=='yes' for r in cases)
    counts=dict(collections.Counter(r['RECIST evaluation'] for r in cases))
    assert counts=={'PR':4,'PD':3,'NV':1,'SD':3}
    t3=next(t for t in antt if t['id']=='T3')
    assert t3['rows'][0]==['Pt ID','S100','Synaptophysin','EMA','PPARγ']
    tmts=tables(tm)
    tmcase={}
    for t in tmts:
        if t['id'].endswith(('t001','t003')):
            row=[r for r in t['rows'] if 'Extraskeletal myxoid chondrosarcoma' in r]
            assert len(row)==1
            tmcase[t['id']]=dict(zip(t['rows'][0],row[0]))
        elif t['id'].endswith('t004'):
            row=[r for r in t['rows'] if r and r[0]=='Patient 2']
            assert len(row)==1
            tmcase[t['id']]=row[0]
    dvts=tables(dv)
    dvrows=dvts[0]['rows']
    dvcases=[dict(zip(dvrows[0],r)) for r in dvrows[1:] if r and r[0].startswith('MO-')]
    assert len(dvcases)==6
    # Read exact original DOCX paragraphs for the already-retained supplement.
    import zipfile
    sp=D.parents[1]/'fresh-discovery-2026-10-04-round2'/'genomics'/'davis-supplement2.docx'
    sb=sp.read_bytes(); sources['davis2017_supplement2']={'file':str(sp),'bytes':len(sb),'sha256':hashlib.sha256(sb).hexdigest()}
    with zipfile.ZipFile(sp) as z:
        sr=ET.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    sparts=[' '.join(''.join(p.itertext()).split()) for p in sr.findall('.//w:p',ns)]
    selected=[p for p in sparts if any(s in p.lower() for s in ['patient history','pazopanib','doxorubicin','rapamycin','cytoxan','r1507','10/2014','12/2015','03/03/2016'])]
    inbrx_t=[t for t in tables(ib) if any('Extraskeletal myxoid' in ' '.join(r) for r in t['rows'])]
    assert len(inbrx_t)==1
    result={
      'evaluated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'question':'Fusion partner by antiangiogenic-versus-cytotoxic clinical activity',
      'sources':sources,
      'anthracycline2013':{'all11_cases':cases,'response_counts_source_reproduction':counts,
        'all_tables':antt,'molecular_paragraphs':paras(ant,['rearranged in 9','NR4A2','FISH was carried']),
        'eligibility':'All11 NR4A3-positive, aggregate EWS9/11; public XML Table3 has IHC only. Individual EWS and alternate partners cannot be assigned. No fusion-treatment comparison.',
        'source_discordance':'Narrative says 4/10 PR but another sentence mentions responses in4 combination+1 single-agent. Preserve table4PR; do not invent regimen mapping. Narrative NR4A2 and NR3A4 typographical strings are retained, not used to recode diagnosis.'},
      'sunitinib2012':{'case_paragraphs':paras(su,['53-year','67-years','anthracycline-based chemotherapy','abscess','Both patients are still']),
        'all_case_conditions':[{'id':'case1','fusion_support':'EWSR1 and CHN break-apart rearrangements; authors call EWSR1-CHN','prior_treatments':['anthracycline followed by surgery/RT, no numeric best response','high-dose ifosfamide plus surgery, no numeric best response','trabectedin, progression'],'sunitinib':'37.5mg/day, PET complete metabolic response at4weeks, later >30% shrinkage; stopped for abscess then progression off drug and response on rechallenge','limits':'Different treatment lines and surgery; already published case. Early infection/progression must not be conflated.'},{'id':'case2','fusion_support':'authors EWSR1-CHN translocated','prior_treatments':['multiple chemotherapy lines, unnamed and responses not separately mapped'],'sunitinib':'37.5mg/day with stabilization at3months, increased dose then dimensional response at6months','limits':'Source dose text says50g/day, retained as source typo and not a usable dosing fact. No alternate-fusion comparator.'}],
        'overlap':'2014 same-team abstract describes strengthening the initial2 observations in a10-case series; overlap is suspected, not case-crosswalk verified. Do not count12 independent. The2012 case1 starts June2011 but2014 abstract says fromJuly2011. Potential overlap with2013 Italian anthracycline cohort unresolved; apparent age/site similarities not a crosswalk.',
        'eligibility':'Actual sequential EWS-supported observations already original conclusion; no new comparative result.'},
      'temozolomide2017':{'all_eligible_EMC_rows':tmcase,
        'conditions':'Case2: prior sunitinib, radiation, nivolumab with no separate outcomes; pazopanib800mg until progression, SD19months; then pazopanib400mg titrated as tolerated + temozolomide150mg/m2 intermittent, PD and2months treatment. These are source durations, not derived PFS ratios.',
        'measurement_methods':paras(tm,['RECIST version1.1','RECIST version 1.1','eight weeks','every 8 weeks','next-generation sequencing']),
        'eligibility':'EWSR1-NR4A3 individual link exists. Published nonresponse to combination is retained; one case with no TAF15 comparator and therapy after selected pazopanib progression cannot identify treatment-by-fusion effect.',
        'overlap':'Ohio State2014-2016, no public donor crosswalk to broader profiling/other referral cohorts; not pooled as proven independent.'},
      'davis2017':{'all6_cases':dvcases,'original_supplement_selected_paragraphs':selected,
        'eligibility':'All6 EWSR1-NR4A3, including one low-quality RNA biopsy authenticated from archived primary. No TAF15 comparator. MO-1582 has both pazopanib and doxorubicin histories but no common RECIST best-response matrix.',
        'material_discordance':'MO-1582 main Table1 says pazopanib x2months; supplement says start10/2014, stop12/2015. Do not silently fix or calculate a growth-modulation/PFS ratio. Both report subsequent doxorubicin progression. Difference is unresolved without source clarification.',
        'positive_and_negative_preserved':'MO-1381 cyclophosphamide/rapamycin prolonged treatment is published, interrupted for RT and eventually progressed. Treatment duration alone is not causally attributable efficacy. No new rapalog claim.'},
      'inbrx2023':{'eligible_author_label_table':inbrx_t,
        'eligibility':'One investigator-labelled extraskeletal myxoid case; footnote says chondrosarcoma/chondrosarcoma-like features. No NR4A3 partner or case-mapped outcome authenticated here. Keep pending identity, not definitive exclusion.'},
      'chiusole2020':{'all_tables':tables(ch),'relevant_paragraphs':paras(ch,['23 patients','EWSR1','second-line','second line']),
        'eligibility':'Published23 molecular cases all EWSR1, without released crosswalk to systemic-treatment cases/lines. No fusion comparator or patient-matched antiangiogenic/cytotoxic matrix.'},
      'decision':'SHELVE standalone proposed fusion-treatment comparison. No new biological effect estimated. Published observations remain useful reference evidence; this source linkage audit is not a discovery.',
      'coverage_limit':'Scoped evaluated sources only; unavailable full2014/2019 tables and unresolved individual mappings remain visible. No exhaustive-public-data or drug-efficacy claim.'}
    (D/'linkage-evaluation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'source_files':len(sources),'anthracycline_cases':len(cases),'anthracycline_responses':counts,'davis_cases':len(dvcases),'temozolomide_EMC_cases':1,'decision':result['decision']},indent=2))

if __name__=='__main__': main()
