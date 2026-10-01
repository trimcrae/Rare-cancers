import argparse,json,copy,hashlib,re,datetime
from pathlib import Path
import numpy as np
from scipy import ndimage
import spatial_marker_followthrough_actual as sm
import ewing_cellpose_all_patient_actual as cp
OUT=sm.OUT;SEED=20261001;OLD_SHA='419eaa6870efe3b793a2a5a0d7acd3e8c4a43fa32bcd1e98a7c257e8e1006c63';PAIRS=[('CD68','CD68'),('HLA-DR','CD68'),('CD68','MRC1'),('CD68','NKX2.2'),('NKX2.2','PSMA3')];MARKERS=['CD68','HLA-DR','MRC1','NKX2.2','PSMA3'];ALIASES={'cd68':'CD68','hla2':'HLA-DR','mrc1':'MRC1','nkx2_2':'NKX2.2','psma3':'PSMA3'}
AMENDMENT={'dated_utc':'2026-10-01','scope':'All26Panel3 fixednuclei/thresholdreplay;2.5/5umVoronoi windows frozenbeforecaseinference','source_window_ambiguity':'Code5um paper5pixels; retainsnucleuscenters/0um baseline. Noauthorclassifierreplay','selection':'All234acquiredfixedtiles, no morepixels/models','limits':'Continuousmarkergeometry notcellidentity/surface/causality/treatment;HLAbroadclassII/PSMA3proteasomealpha3'}
def receipt(p):
 b=p.read_bytes();return {'saved':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def save(obj,p):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(sm.clean(obj),allow_nan=False));return receipt(p)
def valid(t):return t.get('reference_status') in ['measured','normalization_degenerate'] and 'pixels_masks_sha256' in t and 'error' not in t
def merged_cp(roots):
 paths=sorted({p for root in roots for p in root.rglob('ewing-cellpose-batch-*.json')});assert paths;bysha={receipt(p)['sha256']:(p,json.loads(p.read_bytes())) for p in paths};replacement={}
 for sha,(path,b) in bysha.items():
  if 'repair_replaces_original_batch_sha256' not in b:continue
  oldsha=b['repair_replaces_original_batch_sha256'];assert oldsha==OLD_SHA and oldsha in bysha;old=bysha[oldsha][1];assert b['range']==old['range'];newfiles={f['global_panel3_index']:f for f in b['files']}
  for f in old['files']:
   nt={t['label']:t for t in newfiles[f['global_panel3_index']]['tiles']}
   for t in f['tiles']:
    if valid(t):assert t==nt[t['label']],'Repairchangedvalidtile'
  assert oldsha not in replacement;replacement[oldsha]=sha
 files={};density=[];receipts=[]
 for sha,(path,b) in sorted(bysha.items()):
  if sha in replacement:continue
  assert b['schema']=='emc-ewing-cellpose-batch/1' and b['complete'];receipts.append(receipt(path));assert any(w['sha256']=='89ca45e4a45048d5010d29621466b1274b91b3dcb9714dce9f9e90a9a8671303' for w in b['weights'])
  for f in b['files']:
   i=f['global_panel3_index'];assert i not in files and f['status']=='measured' and len(f['tiles'])==9 and all(valid(t) for t in f['tiles']);files[i]=f
  density.extend(b['density_records'])
 assert set(files)==set(range(26)) and len({r['label'] for r in density})==len(density);return files,density,{'all_input_receipts':[receipt(p) for p in paths],'selected_receipts':receipts,'pinned_replacements':replacement}
def pixels(roots,t):
 paths=sorted({p for root in roots for p in root.rglob(Path(t['pixels_masks_saved']).name)});matches=[p for p in paths if receipt(p)['sha256']==t['pixels_masks_sha256']];assert matches,'RawpixelSHA mismatch'
 with np.load(matches[0],allow_pickle=False) as z:raw=z['all_channel_pixels'];names=z['OME_channels'].tolist();mask=z['nuclei_mask'];pixel=float(z['physical_pixel_um'])
 dna_idx=[j for j,x in enumerate(names) if re.fullmatch(r'(dapi|hoechst|nuclei)',x,re.I)];assert len(dna_idx)==1;mi=[j for j,x in enumerate(names) if j!=dna_idx[0] and not re.fullmatch(r'(af|autofluorescence)',x,re.I)];labels=[ALIASES.get(names[j].lower(),names[j]) for j in mi];assert set(labels)==set(MARKERS);mi=[mi[labels.index(m)] for m in MARKERS];return raw,names,mask,pixel,raw[:,:,dna_idx[0]],raw[:,:,mi],receipt(matches[0])
def main():
 p=argparse.ArgumentParser();p.add_argument('--input-root',action='append');a=p.parse_args();roots=[Path(x) for x in(a.input_root or ['restored-artifacts','restored-artifacts-extra'])];files,drecords,provenance=merged_cp(roots);OUT.mkdir(parents=True,exist_ok=True);source={'schema':'emc-spatial-marker-followthrough/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'cell_window_um':0,'IMC':[],'TIFF':[files[i] for i in range(26)],'CP_checkpoint_provenance':provenance};density={'schema':'emc-spatial-density-sensitivity/1','records':drecords,'amendment':AMENDMENT};base=[save(source,OUT/'spatial-marker-followthrough-cellpose-actual.json'),save(density,OUT/'spatial-density-cellpose-actual.json')]
 threshold={'schema':'emc-spatial-followthrough-batch/1','executed_utc':source['executed_utc'],'initial_run':36879244424,'mode':'tiff','range':[24,50],'frozen_total':50,'measurement_amendment':sm.AMENDMENT,'repair_amendment':AMENDMENT,'records':[],'complete':False};variants={w:{'source':copy.deepcopy(source),'density':{'schema':'emc-spatial-density-sensitivity/1','records':[],'amendment':AMENDMENT},'pixel_audit':[]} for w in [2.5,5.]};oldpairs=sm.PAIRS;oldout=cp.OUT;sm.PAIRS=PAIRS
 try:
  for i,f in sorted(files.items()):
   mfile={'path':f['path'],'manifest_bytes':f['manifest_bytes'],'OME_channels':[ALIASES.get(x.lower(),x) for x in f['OME_channels']],'physical_pixel_um':f['physical_pixel_um'],'range_downloaded_bytes':f.get('range_downloaded_bytes',0),'tiles':[],'original_pixel_source_receipts':[]};threshold['records'].append({'global_index':24+i,'status':'measured','result':mfile});tiles=sorted(f['tiles'],key=lambda x:(x['tile_row'],x['tile_column']))
   for ti,t in enumerate(tiles):
    raw,names,nuclei,pixel,dna,stack,prec=pixels(roots,t);assert names==f['OME_channels'];stack=np.asarray(stack,np.float32);y,x=t['tile_row'],t['tile_column'];label='Panel3-'+Path(f['path']).stem+f'-grid{y}-{x}';images={ALIASES.get(name.lower(),name):raw[:,:,j] for j,name in enumerate(names) if not re.fullmatch(r'(dapi|hoechst|nuclei|af|autofluorescence)',name,re.I)};measured=sm.measurements(images,dna,pixel,label,SEED+1000+(24+i)*20+ti);measured.update(tile_row=y,tile_column=x,segments=t['segments']);mfile['tiles'].append(measured);mfile['original_pixel_source_receipts'].append(prec)
    if nuclei.max():dist,nearest=ndimage.distance_transform_edt(nuclei==0,sampling=pixel,return_indices=True);nearest_label=nuclei[tuple(nearest)]
    for w,var in variants.items():
     folder=OUT/('cellwindow-'+str(w)+'um');folder.mkdir(parents=True,exist_ok=True);cp.OUT=folder;window=np.where((nuclei>0)|(dist<=w),nearest_label,0).astype(np.int32) if nuclei.max() else np.zeros(nuclei.shape,np.int32);newlabel=t['label']+'-CellWindow'+str(w)+'um';rec,comparisons=cp.measure(window,stack,MARKERS,pixel,newlabel,SEED+16000+i*20+ti,coordinate_mask=nuclei);new=copy.deepcopy(t);new.update(rec,cell_window_um=w,nucleus_centers_preserved=True,cell_window_interpretation='NearestnucleusVoronoi notauthorclassifier');var['source']['TIFF'][i]['tiles'][ti]=new;core=rec['analyses'][0];var['density']['records'].append({'kind':'Ewing','label':newlabel,'status':'measured' if comparisons else'not_analyzable','nuclear_components':core['nuclear_components'],'comparisons':comparisons});var['pixel_audit'].append({'label':newlabel,'source_pixels':prec,'nuclear_objects':int(nuclei.max()),'nucleus_foreground_pixels':int((nuclei>0).sum()),'expanded_window_pixels':int((window>0).sum())})
    print('EMC_EWING_SAVED_PIXEL_FINALIZE '+str(i)+'/'+str(ti),flush=True)
 finally:sm.PAIRS=oldpairs;cp.OUT=oldout
 threshold.update(complete=True,requested=26,measured=26,errors=0);tr=save(threshold,OUT/'spatial-followthrough-batch-tiff-24-50-pixel-repair.json');summaries=[]
 for w,var in variants.items():
  folder=OUT/('cellwindow-'+str(w)+'um');var['source']['cell_window_um']=w;receipts=[save(var['source'],folder/'spatial-marker-followthrough-cellwindow-actual.json'),save(var['density'],folder/'spatial-density-cellwindow-actual.json'),save(var['pixel_audit'],folder/'cellwindow-pixel-audit.json')];summaries.append({'cell_window_um':w,'derived_receipts':receipts})
 result={'schema':'emc-ewing-saved-pixel-finalization/1','executed_utc':source['executed_utc'],'amendment':AMENDMENT,'coverage':{'Panel3files':26,'fixed_raw_tiles':234,'nuclei_predictions':sum(t['reference_status']=='measured' for f in files.values() for t in f['tiles']),'degenerate_DNA_tiles':sum(t['reference_status']=='normalization_degenerate' for f in files.values() for t in f['tiles'])},'CP_input_provenance':provenance,'primary_CP_derived_receipts':base,'original_threshold_repair':tr,'frozen_window_sensitivities':summaries,'patient_analysis_executed':False};save(result,OUT/'ewing-finalize-pixels-actual.json');print('EMC_EWING_FINALIZE_PIXELS_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_EWING_FINALIZE_PIXELS_END')
if __name__=='__main__':main()
