"""Frozen external-to-575 evaluation wrapper. No network and no classifier fitting."""
import argparse
import copy
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import time

from literal_audit import audit, canonical, pointer, require

SOURCE_SHA = 'd20367d3d14f99716b20309ee8bed1cebe4b6a1270077fc0ac234a4cc5b91fa6'
EXTRACTOR_BLOB = 'dc7d9540df807bf072f1833dee1c1300a9081c00'
COMPANION_BLOB = 'f7b1d257106c255fe86d20c5fde17166431792e8'
REVISION = '52a9fd8b8bf119d30912dca308baa0cc5541df69'
ORACLE_SHA = '302ba913bdebe23f312f7cdb674b34af79ed4b7a4b8c0b57f3695c8794e6af6e'
OFFSET_AMENDMENT_SHA = '8977179a2c54afefa75e05e8a1fba87fa965526dd36998b6609833a67109bcb3'

def sha(raw): return hashlib.sha256(raw).hexdigest()

def module(path, name, expected):
    require(path.stat().st_size < 65536, 'Code size cap')
    raw = path.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    require(blob == expected, 'Frozen code Git blob mismatch: '+name)
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)  # Verified files use guarded CLI entry points.
    return loaded

def prediction_view(family):
    chosen = next((m for m in family['mentions'] if m['explicitAssessmentContext']), None) if family['status']=='assigned' else None
    return {'status':family['status'], 'family':chosen['baseName'] if chosen else None,
            'version':family['criteriaVersion'], 'modifier':(chosen['modifier'] or None) if chosen else None}

def oracle_view(family):
    require(family['status'] in ('assigned','unknown','ambiguous'), 'Invalid oracle family status')
    return {k:(family[k] or None) if k!='status' else family[k] for k in ('status','family','version','modifier')}

def verify_oracle_evidence(value, document):
    # Verify supplied literal evidence only; derive no semantic labels from text.
    if isinstance(value, dict):
        if 'pointer' in value:
            actual = pointer(document, value['pointer'])
            if 'value' in value: require(actual == value['value'], 'Oracle source value mismatch')
            if 'literal' in value:
                if 'decodedStringStart' in value:
                    actual = actual[value['decodedStringStart']:value['decodedStringEndExclusive']]
                require(actual == value['literal'], 'Oracle literal/span mismatch')
        for child in value.values(): verify_oracle_evidence(child, document)
    elif isinstance(value, list):
        for child in value: verify_oracle_evidence(child, document)

def apply_offsets(original, amendment):
    require(amendment['schema']=='blind-oracle-offset-amendment/1', 'Offset amendment schema mismatch')
    require(amendment['originalOracleSHA256']==ORACLE_SHA and amendment['semanticLabelsChanged'] is False, 'Invalid offset amendment binding')
    result = copy.deepcopy(original)
    require(len(amendment['changes'])==2, 'Expected two frozen offset scalar changes')
    paths = set()
    for change in amendment['changes']:
        path = change['oraclePointer']
        require(path not in paths and re.fullmatch(r'/outcomes/\d+/literalRoles/\d+/(decodedStringStart|decodedStringEndExclusive)',path), 'Only unique role offset scalar replacements allowed')
        paths.add(path)
        require(pointer(result,path)==change['old'], 'Offset amendment old value mismatch')
        require(type(change['new']) is int and change['new']>=0, 'Invalid offset replacement')
        parent,key = path.rsplit('/',1)
        pointer(result,parent)[key] = change['new']
    def without_offsets(value):
        if isinstance(value,dict): return {k:without_offsets(v) for k,v in value.items() if k not in ('decodedStringStart','decodedStringEndExclusive')}
        if isinstance(value,list): return [without_offsets(v) for v in value]
        return value
    require(without_offsets(result)==without_offsets(original), 'Offset amendment changed semantic content')
    return result

def evaluate(args):
    started = time.monotonic()
    require(not args.out.exists(), 'Output must be a fresh directory')
    require(args.source.stat().st_size == 235396, 'Source bytes mismatch')
    require(args.oracle.stat().st_size <= 1024*1024, 'Oracle exceeds1MiB')
    require(args.offset_amendment.stat().st_size <= 16384, 'Offset amendment cap')
    raw, gold_raw = args.source.read_bytes(), args.oracle.read_bytes()
    amendment_raw = args.offset_amendment.read_bytes()
    require(sha(amendment_raw)==OFFSET_AMENDMENT_SHA, 'Offset amendment hash mismatch')
    require(sha(raw)==SOURCE_SHA, 'Source hash mismatch')
    require(args.oracle_sha256==ORACLE_SHA and sha(gold_raw)==ORACLE_SHA, 'Oracle hash mismatch')
    extractor = module(args.extractor, 'frozen_literal', EXTRACTOR_BLOB)
    companion = module(args.companion, 'frozen_companion', COMPANION_BLOB)
    document, receipt = extractor.load_verified(raw, SOURCE_SHA, {'kind':'live-capture','retrievedUtc':'2026-10-02T17:27:10.614620+00:00','name':'checkpoint05-api-response.json'})
    original_gold = json.loads(gold_raw)
    amendment = json.loads(amendment_raw)
    gold = apply_offsets(original_gold, amendment)
    require(gold['sourceSHA256']==SOURCE_SHA and bool(gold['frozenUTC']), 'Oracle source/freeze binding mismatch')
    literals = extractor.extract(document, receipt)
    fidelity = audit(document, literals)
    require(len(document['studies'])==10 and fidelity['outcomes']==68, 'Frozen selection coverage mismatch')
    by_pointer = {x['sourcePointer']:x for x in literals['outcomes']}
    oracle = {}
    for item in gold['outcomes']:
        path = item['sourcePointer']
        require(path in by_pointer and path not in oracle, 'Oracle missing/duplicate/unexpected coordinate')
        source = by_pointer[path]
        key = source['outcomeKey']
        require(item['studyIndex']==key[1] and item['nctId']==key[2] and item['outcomeIndex']==key[3], 'Oracle identity mismatch')
        require(item['title']==source['literal'].get('title'), 'Oracle title mismatch')
        require(item['eligibility'] in ('eligible','excluded','uncertain'), 'Invalid eligibility')
        verify_oracle_evidence(item, document)
        oracle[path] = item
    require(set(oracle)==set(by_pointer), 'Oracle must screen all68 outcomes')
    rows_by_outcome = {}
    for row in literals['rows']: rows_by_outcome.setdefault(tuple(row['outcomeKey']), []).append(row)
    comparisons, companions = [], []
    for path, gold_item in oracle.items():
        require(time.monotonic()-started < 120, 'Evaluation exceeds120seconds')
        if gold_item['eligibility']=='excluded': continue
        require('family' in gold_item, 'Eligible/uncertain oracle requires explicit family object')
        source = by_pointer[path]
        before = canonical(source['literal'])
        predicted = companion.classify_context(source['literal'])
        view, expected = prediction_view(predicted), oracle_view(gold_item['family'])
        agreement = {k:view[k]==expected[k] for k in expected}
        result = {'sourcePointer':path, 'outcomeKey':source['outcomeKey'], 'eligibility':gold_item['eligibility'],
                  'oracle':gold_item, 'prediction':predicted, 'comparisonPrediction':view,
                  'comparisonOracle':expected, 'fieldAgreement':agreement, 'jointAgreement':all(agreement.values())}
        role_predictions = {}
        for row in rows_by_outcome.get(tuple(source['outcomeKey']), []):
            before_row = canonical(row)
            ci, gid = row['classIndex'], row['groupId']
            unit = [source['outcomeKey'][2],source['outcomeKey'][4],ci,gid]
            coordinates = [{'source':'api-response.json','sha256':SOURCE_SHA,'pointer':path+f'/classes/{ci}','groupId':gid}]
            output = companion.accompany(unit, row, source['literal'], coordinates)
            require(canonical(row)==before_row==canonical(output['acceptedRowUnchanged']), 'Companion mutated accepted row')
            require(output['acceptedRowSHA256']==sha(before_row), 'Companion accepted-row hash mismatch')
            companions.append(output)
            for cell in output['categoryAssignments']:
                cp = path+f'/classes/{ci}/categories/{cell["categoryIndex"]}/title'
                role_predictions.setdefault(cp, []).append({'groupId':gid,'measurementIndex':cell['measurementIndex'],'familyRole':cell['familyRole']})
        result['literalRoleComparisons'] = []
        for role in gold_item.get('literalRoles', []):
            matches = role_predictions.get(role['pointer'], [])
            comparable = bool(matches) and 'decodedStringStart' not in role
            result['literalRoleComparisons'].append({'oracle':role,'measurementPredictions':matches,'comparable':comparable,
                'allMeasurementRolesAgree':all(x['familyRole']==role['role'] for x in matches) if comparable else None,
                'scope':'Only whole category-title annotations compare automatically; description spans/aggregate roles retained, not imputed'})
        require(canonical(source['literal'])==before, 'Companion mutated outcome')
        comparisons.append(result)
    counts = dict(Counter(x['eligibility'] for x in oracle.values()))
    summary = {'schema':'registry-independent-evaluation/1','status':'complete','sourceSHA256':SOURCE_SHA,
        'oracleSHA256':sha(gold_raw),'offsetAmendmentSHA256':sha(amendment_raw),'codeRevision':REVISION,'extractorGitBlobSHA1':EXTRACTOR_BLOB,'companionGitBlobSHA1':COMPANION_BLOB,
        'wrapperSHA256':sha(Path(__file__).read_bytes()),'auditSHA256':sha(Path(__file__).with_name('literal_audit.py').read_bytes()),
        'screeningCounts':counts,'allOutcomes':68,'literalRows':len(literals['rows']),'companionRows':len(companions),
        'strata':{},'limits':['Small date-defined capped snapshot; no population or clinical error rate inference.',
        'Uncertain outcomes separate from eligible-only agreement denominator. No outcome exclusions based on predictions.',
        'Status/family/version/modifier exact-string agreement; no alias equivalence or semantic adjudication by wrapper.',
        'All oracle fields retained; confirmation/reader/aggregate roles are not automatically adjudicated.']}
    for eligibility in ('eligible','uncertain'):
        subset = [x for x in comparisons if x['eligibility']==eligibility]
        summary['strata'][eligibility] = {'outcomes':len(subset),'jointAgreements':sum(x['jointAgreement'] for x in subset),
            'fieldAgreements':{k:sum(x['fieldAgreement'][k] for x in subset) for k in ('status','family','version','modifier')},
            'predictedStatusCounts':dict(Counter(x['prediction']['status'] for x in subset))}
    args.out.mkdir(parents=True, exist_ok=False)
    for name,value in [('summary.json',summary),('literal-extraction.json',literals),('literal-fidelity.json',fidelity),('outcome-comparisons.json',comparisons),('family-companions.json',companions),('oracle-preserved.json',original_gold),('oracle-offsets-applied.json',gold),('offset-amendment-preserved.json',amendment)]:
        data = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode()+b'\n'
        require(len(data)<=8*1024*1024, 'Output cap')
        (args.out/name).write_bytes(data)
    print(json.dumps(summary))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('source','oracle','offset-amendment','extractor','companion','out'): p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--oracle-sha256',required=True)
    evaluate(p.parse_args())
