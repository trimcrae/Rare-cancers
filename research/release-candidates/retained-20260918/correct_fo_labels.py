"""Replace three retained PDF title labels, proving every outside pixel unchanged."""
from pathlib import Path
import hashlib,json,zipfile
import fitz
from PIL import Image,ImageChops,ImageDraw

def correct(here,guard):
    plan=json.loads((here/'inputs/FO/figure-label-plan.json').read_text())
    destination=here/'rendered/FO/figures';destination.mkdir(parents=True,exist_ok=True)
    records=[];images={}
    proofs=json.loads((here/'inputs/FO/original-content-stream-proof.json').read_text())
    for item in plan['replacements']:
        guard('FO title correction '+item['figure'])
        src=here/'inputs/FO/figures'/(item['figure']+'.pdf')
        png=here/'inputs/FO/figures'/(item['figure']+'.png')
        assert hashlib.sha256(src.read_bytes()).hexdigest()==item['pdf_sha256']
        assert hashlib.sha256(png.read_bytes()).hexdigest()==item['png_sha256']
        doc=fitz.open(src);assert len(doc)==1;page=doc[0]
        boxes=page.search_for(item['before'])
        assert boxes,('Original title not located exactly',item['figure'])
        rect=fitz.Rect(boxes[0])
        for b in boxes[1:]:rect.include_rect(b)
        rect=rect+(-1,-1,1,1)
        original_image=Image.open(png);scale=original_image.width/page.rect.width
        before=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
        before_image=Image.frombytes('RGB',[before.width,before.height],before.samples)
        # Redaction rewrites unrelated content operators. Remove only hash-pinned
        # isolated BT..ET title blocks, preserving every other decoded byte.
        proof=next(p for p in proofs if p['figure']==item['figure'])
        xrefs=page.get_contents();assert len(xrefs)==1
        raw=doc.xref_stream(xrefs[0])
        assert hashlib.sha256(raw).hexdigest()==proof['content_stream_sha256']
        parts=[];cursor=0
        for block in proof['removed_title_blocks']:
            start,end=block['start'],block['end']
            assert hashlib.sha256(raw[start:end]).hexdigest()==block['block_sha256']
            parts.append(raw[cursor:start]);cursor=end
        parts.append(raw[cursor:]);patched=b''.join(parts)
        assert hashlib.sha256(patched).hexdigest()==proof['remaining_content_bytes_sha256']
        doc.update_stream(xrefs[0],patched,compress=True)
        assert doc.xref_stream(xrefs[0])==patched
        page=doc.reload_page(page)
        available=rect+(-1,-1,1,1)
        size=10.0
        while size>=6:
            shape=page.new_shape()
            left=shape.insert_textbox(available,item['after'],fontname='helv',fontsize=size,color=(0,0,0),align=1)
            if left>=0:
                shape.commit();break
            size-=0.25
        assert size>=6,('Title does not fit',item['figure'])
        dest=destination/(item['figure']+'.pdf');doc.save(dest,garbage=0,clean=False,deflate=True);doc.close()
        new=fitz.open(dest);after=new[0].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
        after_image=Image.frombytes('RGB',[after.width,after.height],after.samples)
        assert before_image.size==after_image.size
        diff=ImageChops.difference(before_image,after_image)
        mask_box=(int(available.x0*scale)-3,int(available.y0*scale)-3,int(available.x1*scale)+4,int(available.y1*scale)+4)
        ImageDraw.Draw(diff).rectangle(mask_box,fill=(0,0,0))
        assert diff.getbbox() is None,('Non-title pixels changed',item['figure'])
        text=' '.join(new[0].get_text().split())
        assert ' '.join(item['after'].split()) in text
        assert ' '.join(item['before'].split()) not in text
        newpng=destination/(item['figure']+'.png');after.save(newpng)
        images[item['png_sha256']]=newpng.read_bytes()
        records.append({'figure':item['figure'],'source_pdf_sha256':item['pdf_sha256'],'source_png_sha256':item['png_sha256'],'pdf_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'png_sha256':hashlib.sha256(newpng.read_bytes()).hexdigest(),'before':item['before'],'after':item['after'],'title_rectangle_points':list(available),'all_pixels_outside_title_rectangle_exact':True,'font_size_points':size,'scientific_analysis_recomputed':False})
        new.close()
    source=here/'inputs/FO/main.docx';dest=here/'rendered/FO/main-with-corrected-labels.docx'
    changed=[]
    with zipfile.ZipFile(source) as zin,zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as zout:
        for entry in zin.infolist():
            data=zin.read(entry.filename);digest=hashlib.sha256(data).hexdigest()
            if entry.filename.startswith('word/media/') and digest in images:
                data=images[digest];changed.append(entry.filename)
            zout.writestr(entry,data)
    assert len(changed)==3
    with zipfile.ZipFile(source) as a,zipfile.ZipFile(dest) as b:
        assert a.namelist()==b.namelist()
        assert all(a.read(n)==b.read(n) for n in a.namelist() if n not in changed)
    result={'status':'exact_title_only_correction_visual_pending','figures':records,'docx_path':str(dest.relative_to(here)),'docx_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changed_media_members':changed,'all_other_DOCX_members_exact':True}
    (destination/'LABEL-CORRECTION-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    return dest,result
