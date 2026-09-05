"""Retain manually inspected pixel coordinates; run only when creating the initial extraction."""
from pathlib import Path
import json,datetime
root=Path(__file__).resolve().parent
screens=[]
def add(target,file,panel,y0,top,unit,pa,fu,pys,fys,pcaps,fcaps):
 screens.append(dict(target=target,image=file,pdf='crt-2022-910-Supplementary-Fig-'+('2' if target=='B4N' else '3')+'.pdf',page=1,panel=panel,coordinate_system='native embedded raster, zero-based pixels, origin top left',axis_label='Relative mRNA expression levels',axis_ticks=[{'y':y0,'value':0},{'y':top,'value':unit}],mean_reading_halfwidth_px=4,sd_reading_halfwidth_px=6,bars=[dict(design_number=i+1,endpoint=k,x_center=x,y_mean=y,y_sd_upper=cap,status='plot_ceiling_censored' if y is None else 'digitized_mean') for k,xs,ys,caps in [('measured_parent',pa,pys,pcaps),('fusion',fu,fys,fcaps)] for i,(x,y,cap) in enumerate(zip(xs,ys,caps))]))
add('B4N','Fig-2-p1-image24.png','S5 (single qPCR panel)',356,52,1.6,
[212,272,331,391,451,511,572,630,691,750,810,870,929,989,1050],
[227,286,346,406,466,526,586,645,705,765,825,885,944,1004,1064],
[211,168,178,179,206,238,167,216,208,218,203,248,252,253,290],
[192,254,178,170,263,195,291,231,330,225,211,304,245,288,342],
[192.5,91.5,159.5,144.5,157.5,198.5,125.5,211.5,171.5,193.5,156.5,233.5,226.5,231.5,272.5],
[176.5,231.5,142.5,97.5,232.5,173.5,253.5,214.5,321.5,202.5,181.5,277.5,222.5,272.5,326.5])
add('SS','Fig-3-p1-image29.png','S6A right qPCR panel',353,41,2,
[702,750,799,848,897,946,995,1044,1093,1142,1192,1241,1289,1340,1388,1437],
[712,762,811,860,909,958,1007,1056,1105,1154,1203,1252,1301,1350,1400,1449],
[153,162,156,None,112,197,155,192,238,180,165,189,212,184,231,214],
[299,308,319,225,282,315,316,242,223,296,314,319,288,301,283,254],
[146,133,135,None,85,185,116,183,235,176,138,179,198,155,222,190],
[286,268,300,208,271,303,301,224,209,281,307,312,271,275,273,239])
r={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Manual verification of colored mean-bar top and neutral SD upper cap against native raster and 2x page renders; color scan aided top location. Legend swatches excluded explicitly. No vectors in outcome plots.','reading_uncertainty':'Conservative +/-4 native pixels for mean including edge/axis ambiguity; +/-6 pixels for mean-to-SD-cap difference. These are image-reading ranges, not confidence intervals.','screens':screens,'censoring':{'design':'SS_04','endpoint':'measured_parent','visible_lower_bound':2.0,'conservative_lower_bound':(353-41-4)/156,'upper_bound':None,'reason':'Light-green mean bar enters plot ceiling at y=41; mean and SD cap above or at ceiling cannot be recovered.'},'control_checks':{'B4N':{'NC_parent_y':167,'NC_fusion_y':165,'PC_parent_y':136,'PC_fusion_y':326},'SS':{'NC_parent_y':197,'NC_fusion_y':197}}}
(root/'extraction-coordinates.json').write_text(json.dumps(r,indent=2)+'\n')
