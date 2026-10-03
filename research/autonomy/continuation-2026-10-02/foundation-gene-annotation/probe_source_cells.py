"""Cloud-only two-cell encoding probe; no gene repair or identity re-extraction."""
import argparse, hashlib, json
from pathlib import Path
import xlrd

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workbook',type=Path,required=True)
    args=p.parse_args()
    raw=args.workbook.read_bytes()
    if len(raw)!=4812800 or hashlib.sha256(raw).hexdigest()!='88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475':
        raise ValueError('Workbook identity mismatch')
    book=xlrd.open_workbook(file_contents=raw,formatting_info=True)
    try:
        sheet=book.sheet_by_name('variants_table_final_for_supple')
        if sheet.row_values(0)[:4]!=['de-identified ID','gene','partner_gene','alteration_type']:
            raise ValueError('Header mismatch')
        records=[]
        for excelrow,sid,gene,value in [(8570,2290,'NOD1',44621.0),(20794,5458,'HDAC4',44812.0)]:
            row=excelrow-1
            if sheet.row_values(row)[:4]!=[float(sid),gene,value,'RE']:
                raise ValueError('Coordinate/sentinel mismatch')
            cell=sheet.cell(row,2)
            xf=book.xf_list[cell.xf_index]
            fmt=book.format_map[xf.format_key]
            record={'sourceExcelRow':excelrow,'column_zero_based':2,'sourceID':sid,'gene':gene,'alteration_type':'RE',
                    'raw_value':cell.value,'xlrd_ctype':cell.ctype,'xlrd_type_name':{xlrd.XL_CELL_NUMBER: "number", xlrd.XL_CELL_DATE: "date"}.get(cell.ctype, "other"),
                    'xf_index':cell.xf_index,'format_key':xf.format_key,'format_string':fmt.format_str,
                    'format_type':fmt.type,'datemode':book.datemode}
            if cell.ctype==xlrd.XL_CELL_DATE:
                record['date_encoding_only']=xlrd.xldate_as_datetime(cell.value,book.datemode).isoformat()
            records.append(record)
        print(json.dumps({'status':'passed','reader_version':xlrd.__version__,'workbook_sha256':hashlib.sha256(raw).hexdigest(),
                          'cells':records,'scope':'Two-cell encoding evidence only; dates do not establish intended gene symbols.'},indent=2))
    finally:
        book.release_resources()

if __name__=='__main__': main()
