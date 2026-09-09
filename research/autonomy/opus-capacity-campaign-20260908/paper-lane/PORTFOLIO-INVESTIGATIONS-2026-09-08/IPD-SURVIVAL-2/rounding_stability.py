"""Do the three recorded-precision differences found in checks/02 flip any clause of the rule?"""
import json,re,sys,os
REPO="/home/user/Rare-cancers"
src=open(os.path.join(REPO,"research/modalities/km_risk_row_detect.py")).read()
c=lambda n: float(re.search(rf"^{n}\s*=\s*([0-9.]+)",src,re.M).group(1))
MAX_W,MIN_GLYPH=c("MAX_MARK_WIDTH"),c("MIN_GLYPH_WIDTH")
d=json.load(open("census-verdict-rederivation.json"))
rows=[]
for m in d["mismatches"]:
    rec,red=m["recorded"],m["re_derived"]
    rows.append({**m,
        "abs_difference":round(abs(rec-red),6),
        "clause_med_width<=MAX_MARK_WIDTH":{"recorded":rec<=MAX_W,"re_derived":red<=MAX_W,
                                            "flips":(rec<=MAX_W)!=(red<=MAX_W)},
        "clause_med_width>=MIN_GLYPH_WIDTH":{"recorded":rec>=MIN_GLYPH,"re_derived":red>=MIN_GLYPH,
                                             "flips":(rec>=MIN_GLYPH)!=(red>=MIN_GLYPH)}})
out={"_what":"Whether the three 1-in-10000 differences between recorded and re-derived "
             "median_mark_width_frac change any clause outcome of the detection rule.",
     "_why_they_exist":"The artifact records median_mark_width_frac rounded to 4 dp and the text "
                       "arm's width scale (tick_row_span_pt) rounded to 1 dp; the original run "
                       "divided unrounded values. Re-deriving from the rounded record therefore "
                       "reproduces the ratio to within one unit in the last recorded place.",
     "constants":{"MAX_MARK_WIDTH":MAX_W,"MIN_GLYPH_WIDTH":MIN_GLYPH},
     "differences":rows,
     "any_clause_flips":any(r["clause_med_width<=MAX_MARK_WIDTH"]["flips"] or
                            r["clause_med_width>=MIN_GLYPH_WIDTH"]["flips"] for r in rows),
     "max_abs_difference":max([r["abs_difference"] for r in rows],default=0.0)}
out["verdict"]=("ROUNDING ONLY -- no clause outcome changes, so no verdict depends on them"
                if not out["any_clause_flips"] else "A CLAUSE FLIPS -- substantive")
json.dump(out,sys.stdout,indent=1,ensure_ascii=False);print()
