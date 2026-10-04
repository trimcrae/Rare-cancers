"""Read-only extraction of the published FFPE table. See PLAN.txt before results."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,json,hashlib,statistics,math,collections
BASE=Path(__file__).resolve().parent
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
IDS=['Si01','Si02','Si05','Si09','Si10','Si14','Si15','Si16','Si17','Si19','Si20','Si22']
ALIASES=['TMEM266','C15orf27','FLJ38190','HVRP1']
CONTROLS=['NR4A3','CHRNA6','ACTA1','CKM','MYH1','MYH2','MYH7','PTPRC','LST1','PECAM1','VWF','COL1A1','COL1A2','DCN']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_source(path):
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheet=next(s for s in wb.findall('s:sheets/s:sheet',NS) if s.attrib['name']=='EMC_Gene-expression_Log2CPM')
        target=rels[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
        target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        rt=ET.fromstring(z.read(target));rows=[];formulas=[]
        for row in rt.findall('s:sheetData/s:row',NS):
            vals=[]
            for c in row.findall('s:c',NS):
                if c.find('s:f',NS) is not None:formulas.append(c.attrib['r'])
                t=c.attrib.get('t');v=c.find('s:v',NS)
                if t=='s':val=strings[int(v.text)]
                elif t=='inlineStr':val=''.join(c.find('s:is',NS).itertext())
                elif v is None:val=None
                else:val=float(v.text)
                vals.append(val)
            rows.append(vals)
    assert rows[0]==['symbol']+IDS and len(rows)==9501
    assert all(len(r)==13 for r in rows) and not formulas
    return rows[1:]
def quantile(values,p):
    a=sorted(values);x=(len(a)-1)*p;i=int(x)
    return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(x-i)
def main():
    source=BASE/'peerj-source-s009.xlsx';assert sha(source)=='20165fd3ff09ec2d5a24b3c20b78515f42a3309119f248ed055c7484deb45e75'
    rows=read_source(source);lookup=collections.defaultdict(list)
    for i,r in enumerate(rows):lookup[str(r[0]).strip()].append(i)
    vals=[r[1:] for r in rows];assert all(math.isfinite(x) for r in vals for x in r)
    hits=[(a,i) for a in ALIASES for i in lookup[a]];selected={};missing=[]
    for g in CONTROLS:
        if len(lookup[g])==1:selected[g]=lookup[g][0]
        else:missing.append(g)
    if len(hits)==1:selected['TMEM266']=hits[0][1]
    columns=list(zip(*vals));q25=[quantile(c,.25) for c in columns];out={}
    for g,i in selected.items():
        by_sample={}
        for j,s in enumerate(IDS):
            x=vals[i][j];c=columns[j]
            rank=sum(y<x for y in c)+(sum(y==x for y in c)+1)/2
            by_sample[s]={'published_log2CPM':x,'within_sample_midrank_fraction':rank/len(c),'equals_repeated_export_value':abs(x-.010026459)<=5e-10,'at_or_below_bottom_quartile':x<=q25[j]}
        out[g]={'source_symbol':rows[i][0],'excel_row':i+2,'specimens':by_sample,'median_published_log2CPM':statistics.median(vals[i]),'range_published_log2CPM':[min(vals[i]),max(vals[i])]}
    result={'schema':'TMEM266-published-FFPE/1','question':'Is a TMEM266-targeted transcript signal represented in published pathologist-reviewed scraped FFPE EMC tissue?','source_sha256':sha(source),'plan_sha256':sha(BASE/'PLAN.txt'),'script_sha256':sha(Path(__file__)),'source_doi':'10.7717/peerj.21497','matrix_dimensions':[9500,12],'literal_specimen_ids':IDS,'target_alias_matches':hits,'missing_or_ambiguous_controls':missing,'genes':out,'sample_lower_quartiles':dict(zip(IDS,q25)),'interpretation_limits':['Source is log2CPM processed export; no authenticated detection threshold or raw probe counts here.','Scraped area of interest is not single-cell localization or quantified tumor purity.','No comparison to other diseases in this table; gene ranks are descriptive, not cross-gene transcript concentration.','Missing export row is not biological absence.','Repeated export value .010026459 is not automatically a limit of detection.','Neither full-length transcript nor surface protein is demonstrated.']}
    (BASE/'peerj-tmem266-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'target_matches':hits,'target':out.get('TMEM266'),'missing_controls':missing},indent=2))
if __name__=='__main__':main()
