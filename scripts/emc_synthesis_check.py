"""Reproduce a bounded cross-study comparison without pooling incompatible assays."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'research/literature/emc-census-2026-09-12/iwata-2025-screen-extraction.json'
OUTPUT = ROOT / 'site/synthesis-check.json'


def analyze():
    raw = INPUT.read_bytes()
    source = json.loads(raw)
    screen, ic50 = source['tables']
    selected = []
    for cas in ('179324-69-7', '868540-17-4', '1257044-40-8'):
        matches = [r for r in screen['records'] if r['cas'] == cas]
        if len(matches) != 1:
            raise ValueError('A drug must resolve to exactly one original CAS row')
        r = matches[0]
        selected.append({k: r[k] for k in ('drug', 'cas', 'viability_percent',
                                          'sd_percentage_points', 'source_row', 'sheet')})
    selected.sort(key=lambda r: r['viability_percent'])
    concentration_rows = [r for r in ic50['records'] if r['cas'] == '179324-69-7']
    if len(concentration_rows) != 1:
        raise ValueError('Bortezomib concentration-response row is ambiguous')
    return {
        'date': '2026-09-17',
        'question': 'Does an independent EMC model repeat proteasome-inhibitor activity relative to weak venetoclax monotherapy?',
        'source_doi': source['doi'],
        'input_sha256': hashlib.sha256(raw).hexdigest(),
        'screen_source': screen['source'],
        'model': source['model'],
        'rows_sorted_by_mean_viability': selected,
        'separate_concentration_response': concentration_rows[0],
        'result': 'Both proteasome inhibitors have lower reported mean viability than venetoclax in this screen. This is directional consistency with the earlier models, not independent replication of combination synergy.',
        'scope': 'Descriptive comparison within one published screen. SD is retained as reported; replicate count is unresolved. No standard error, confidence interval or significance test is invented.',
        'not_computed': ['No cross-study potency ratio: exposure and assay methods are not harmonized.',
                         'No pooled response rate: these are cell assays, not patient responses.',
                         'No fusion effect: one donor per fusion class in the earlier pair confounds genotype and donor.',
                         'No combination estimate in NCC-EMC1-C1: only single-agent data are available here.'],
        'methodological_warning': 'The same supplement reports doxorubicin mean viability above 70% yet a separate IC50 of 36.5 nM. Without the main methods these endpoints cannot be assumed interchangeable. No silent reconciliation or cross-assay ranking.',
    }


if __name__ == '__main__':
    result = analyze()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(result['result'])
