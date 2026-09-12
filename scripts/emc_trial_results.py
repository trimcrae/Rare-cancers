"""Extract explicitly named EMC outcome groups from saved ClinicalTrials.gov data.

Offline, aggregate results only. Group IDs are scoped to each outcome, never
reused across modules. Preserve original strings, missingness and source wording.
Eligibility mentions alone are not evidence of enrollment or subgroup results.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/literature/emc-census-2026-09-12'


def select_groups(value, ids):
    if isinstance(value, list):
        return [select_groups(item, ids) for item in value
                if not isinstance(item, dict) or 'groupId' not in item
                or item['groupId'] in ids]
    if isinstance(value, dict):
        return {key: select_groups(item, ids) for key, item in value.items()}
    return value


def extract(study):
    selected = []
    outcomes = study.get('resultsSection', {}).get('outcomeMeasuresModule', {}).get('outcomeMeasures', [])
    for index, outcome in enumerate(outcomes):
        groups = [g for g in outcome.get('groups', [])
                  if 'extraskeletal myxoid' in g.get('title', '').lower()]
        if not groups:
            continue
        ids = {g['id'] for g in groups}
        copy = select_groups(outcome, ids)
        copy['groups'] = groups
        # Cross-group statistical comparisons require their own review.
        copy.pop('analyses', None)
        selected.append({'source_path': f'resultsSection.outcomeMeasuresModule.outcomeMeasures[{index}]',
                         'outcome': copy})
    return selected


def main():
    studies = {}
    receipts = []
    queries = [('clinicaltrials-discovery.json', 'query.cond=extraskeletal myxoid chondrosarcoma'),
               ('clinicaltrials-fulltext-discovery.json', 'query.term="extraskeletal myxoid"')]
    for filename, query in queries:
        path = OUT / 'sources' / filename
        data = json.loads(path.read_bytes())
        if data.get('nextPageToken') or data['totalCount'] != len(data['studies']):
            raise ValueError('Incomplete trial discovery pagination')
        receipts.append({'file': str(path.relative_to(ROOT)).replace('\\', '/'),
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'query': query, 'retrieved': len(data['studies'])})
        for study in data['studies']:
            studies[study['protocolSection']['identificationModule']['nctId']] = study
    records = []
    for nct, study in sorted(studies.items()):
        outcomes = extract(study)
        if outcomes:
            records.append({'nct_id': nct, 'url': 'https://clinicaltrials.gov/study/' + nct + '?tab=results',
                            'outcomes': outcomes})
    result = {'retrieved_date': '2026-09-12', 'source_receipts': receipts,
              'unique_trial_records': len(studies),
              'records_with_posted_results': sum(bool(s.get('hasResults')) for s in studies.values()),
              'records_with_explicitly_named_emc_outcome_groups': len(records),
              'limitations': 'Exact group-title selection is not exhaustive: abbreviation-only labels, baseline subgroups and unstratified reports still require review. Outcome values are source-reported, not reconciled or estimates of causal treatment benefit.',
              'records': records}
    (OUT / 'trial-subgroup-extraction.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print({key: value for key, value in result.items() if key.startswith('records_') or key == 'unique_trial_records'})


if __name__ == '__main__':
    main()
