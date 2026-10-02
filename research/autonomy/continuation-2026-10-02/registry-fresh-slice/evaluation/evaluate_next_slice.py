"""Prospective frozen-input evaluation; no network, fitting or semantic amendments."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil

PINS = {
 'extractor': 'c9ea1a864b0c5a16eebd7a41f5dc1575395fcf3d6f6affb00f1b2a68695af154',
 'companion': '8becca0c0143cf5384d12c5db6467df00b85ff10f00d1dc8c014eed743e50f1a',
 'audit': 'ec6d15b34d8f7f8e5e8f746ab0c1b90c845bbf3a3991110befd5c8a321a2bed8',
 'payloadAudit': '5cb79ad7a51afd7ae4cc69b630c88bf9d54294840b3d3cf81f0ab4c4baa14d25'}
FIELDS = ('status', 'family', 'version', 'modifier')
MODULES = ('identificationModule', 'statusModule', 'conditionsModule')

def require(ok, message):
    if not ok: raise ValueError(message)

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def sha(raw): return hashlib.sha256(raw).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result

def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))

def same(a, b): return canonical(a) == canonical(b)

def read_bound(base, entry, cap):
    path = (base / entry['path']).resolve()
    require(path.is_relative_to(base.resolve()), 'Input path escapes manifest directory')
    require(path.stat().st_size <= cap, 'Input size cap')
    raw = path.read_bytes()
    require(re.fullmatch('[0-9a-f]{64}', entry['sha256']) and sha(raw) == entry['sha256'], 'Input hash mismatch')
    return raw

def load_code(base, entry, role):
    require(entry['sha256'] == PINS[role], 'Fixed implementation mismatch: ' + role)
    read_bound(base, entry, 65536)
    path = (base / entry['path']).resolve()
    spec = importlib.util.spec_from_file_location('next_slice_' + role, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def pointer(document, path):
    require(isinstance(path, str) and path.startswith('/'), 'Invalid JSON pointer')
    value = document
    for token in path.split('/')[1:]:
        require(re.search(r'~(?![01])', token) is None, 'Bad pointer escaping')
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list):
            require(re.fullmatch(r'0|[1-9][0-9]*', token) is not None, 'Invalid array index')
            value = value[int(token)]
        else: value = value[token]
    return value

def evidence(item, document, outcome_path):
    require(isinstance(item, dict) and 'pointer' in item, 'Evidence requires pointer')
    path = item['pointer']
    require(path == outcome_path or path.startswith(outcome_path + '/'), 'Evidence crosses outcome boundary')
    present = item.get('sourceFieldPresent', True)
    require(type(present) is bool, 'Presence must be boolean')
    if not present:
        parent, leaf = path.rsplit('/', 1)
        obj = pointer(document, parent)
        leaf = leaf.replace('~1', '/').replace('~0', '~')
        require(isinstance(obj, dict) and leaf not in obj, 'False absence assertion')
        require(item.get('value', 'MISSING') is None and 'literal' not in item, 'Absence requires explicit null placeholder')
    else:
        actual = pointer(document, path)
        require('value' in item or 'literal' in item, 'Evidence has no bound value/literal')
        if 'value' in item: require(same(actual, item['value']), 'Evidence value/type differs')
        has_start, has_end = 'decodedStringStart' in item, 'decodedStringEndExclusive' in item
        require(has_start == has_end, 'Incomplete span coordinates')
        if has_start:
            start, end = item['decodedStringStart'], item['decodedStringEndExclusive']
            require(isinstance(actual, str) and type(start) is int and type(end) is int and 0 <= start < end <= len(actual), 'Invalid decoded-string span')
            require('literal' in item, 'Span requires literal')
            actual = actual[start:end]
        if 'literal' in item: require(same(actual, item['literal']), 'Evidence literal/span differs')

def family_view(family):
    require(isinstance(family, dict) and set(family) == set(FIELDS), 'Family requires four explicit fields')
    require(family['status'] in ('assigned', 'unknown', 'ambiguous'), 'Family status')
    require(all(family[k] is None or isinstance(family[k], str) for k in FIELDS[1:]), 'Family scalar type')
    # Freeze only null/empty equivalence. No whitespace, case, alias or version normalization.
    return {k: (None if k != 'status' and family[k] == '' else family[k]) for k in FIELDS}

def walk_evidence(value, document, outcome_path):
    if isinstance(value, dict):
        if 'pointer' in value: evidence(value, document, outcome_path)
        for child in value.values(): walk_evidence(child, document, outcome_path)
    elif isinstance(value, list):
        for child in value: walk_evidence(child, document, outcome_path)

def validate_oracle(gold, document, source_sha):
    require(gold['schema'] == 'registry-next-slice-oracle/1' and gold['sourceSHA256'] == source_sha and bool(gold['frozenUTC']), 'Oracle source/freeze binding')
    reviewer = gold['reviewer']
    require(all(isinstance(reviewer.get(k), str) and reviewer[k] for k in ('identity', 'model', 'effort', 'prompt', 'accessExposureAttestation')), 'Reviewer provenance missing')
    require(reviewer.get('blindToClassifierAndPredictions') is True, 'Blindness attestation missing')
    expected, inventory = {}, []
    for si, study in enumerate(document['studies']):
        nct = study['protocolSection']['identificationModule']['nctId']
        result = study.get('resultsSection', {})
        module = result.get('outcomeMeasuresModule', {})
        outcomes = module.get('outcomeMeasures', [])
        require(isinstance(outcomes, list), 'Outcomes must be array or absent')
        inventory.append({'studyIndex': si, 'nctId': nct, 'outcomeCount': len(outcomes), 'resultsSectionPresent': 'resultsSection' in study, 'outcomeModulePresent': 'outcomeMeasuresModule' in result, 'outcomeArrayPresent': 'outcomeMeasures' in module})
        for oi, outcome in enumerate(outcomes):
            expected[f'/studies/{si}/resultsSection/outcomeMeasuresModule/outcomeMeasures/{oi}'] = (si, nct, oi, outcome)
    require(same(gold['studyInventory'], inventory), 'Missing/zero outcome inventory differs')
    seen = {}
    for item in gold['outcomes']:
        path = item['sourcePointer']
        require(path in expected and path not in seen, 'Oracle outcome missing/duplicate/unexpected')
        si, nct, oi, outcome = expected[path]
        require(same([item['studyIndex'], item['nctId'], item['outcomeIndex']], [si,nct,oi]), 'Oracle identity differs')
        require(item['outcomeSHA256'] == sha(canonical(outcome)), 'Oracle full outcome hash differs')
        require(item['eligibility'] in ('eligible', 'uncertain', 'excluded') and isinstance(item['reason'], str) and bool(item['reason']), 'Screening decision/reason')
        require(isinstance(item['evidence'], list) and bool(item['evidence']), 'Outcome evidence required')
        for e in item['evidence']: evidence(e, document, path)
        require(isinstance(item['literalRoles'], list), 'Literal roles array required')
        for role in item['literalRoles']:
            evidence(role, document, path)
            require(isinstance(role.get('role'), str) and isinstance(role.get('scope'), str), 'Role/scope missing')
        require(all(k in item for k in ('confirmationContext', 'scopeDenominatorReferences', 'absentEvidence')), 'Interpretation fields absent')
        for e in item['scopeDenominatorReferences'] + item['absentEvidence']: evidence(e, document, path)
        walk_evidence(item, document, path)
        if item['eligibility'] != 'excluded': family_view(item['family'])
        seen[path] = item
    require(set(seen) == set(expected), 'Oracle must cover every outcome')
    return seen, inventory

def assemble(base, manifest):
    require(manifest['schema'] == 'registry-next-slice-inputs/1' and bool(manifest['frozenUTC']), 'Manifest schema/freeze')
    selection = parse(read_bound(base, manifest['selectionReceipt'], 1048576))
    metadata = parse(read_bound(base, manifest['selectedMetadata'], 1048576))
    require(selection['status'] == 'metadata_frame_frozen' and selection['cutoffTieComplete'] is True, 'Selection not frozen')
    require(sha(read_bound(base, manifest['selectedMetadata'], 1048576)) == selection['selectedMetadataSHA256'], 'Selection metadata binding')
    records = selection['selected']
    require(len(records) <= 10 and len({r['nctId'] for r in records}) == len(records), 'Selected trial cap/uniqueness')
    require(records == sorted(records, key=lambda r:(r['resultsFirstPostDate'],r['nctId'])), 'Selection order')
    require(set(metadata) == {r['nctId'] for r in records} and len(manifest['rawSources']) == len(records), 'Source/metadata trial coverage')
    studies, total = [], 0
    for record, entry in zip(records, manifest['rawSources']):
        raw = read_bound(base, entry, 1048576)
        total += len(raw)
        require(total <= 1048576, 'Aggregate outcome-source cap')
        study = parse(raw)
        protocol = study['protocolSection']
        require(set(protocol) == set(MODULES), 'Requested source metadata modules changed')
        require(same(protocol, metadata[record['nctId']]), 'Selection metadata drift')
        require(sha(canonical(protocol)) == record['metadataSHA256'], 'Metadata projection digest mismatch')
        require(protocol['identificationModule']['nctId'] == entry['nctId'] == record['nctId'], 'Source identity/order mismatch')
        require(protocol['statusModule']['resultsFirstPostDateStruct']['date'] == record['resultsFirstPostDate'], 'Source date drift')
        require(set(study) <= {'protocolSection','resultsSection','hasResults'}, 'Unexpected study modules')
        require(set(study.get('resultsSection',{})) <= {'outcomeMeasuresModule'}, 'Unexpected results modules')
        studies.append(study)
    document = {'studies': studies}
    require(sha(canonical(document)) == manifest['assembledSourceSHA256'], 'Assembled source digest')
    return document

def predict(document, literals, companion):
    before = canonical(literals)
    predictions, carried = [], []
    for item in literals['outcomes']:
        outcome_before = canonical(item['literal'])
        result = companion.classify_context(item['literal'])
        require(canonical(item['literal']) == outcome_before, 'Outcome mutated')
        chosen = next((m for m in result['mentions'] if m['explicitAssessmentContext']), None) if result['status'] == 'assigned' else None
        view = family_view({'status':result['status'], 'family':chosen['baseName'] if chosen else None, 'version':result['criteriaVersion'], 'modifier':chosen['modifier'] if chosen else None})
        predictions.append({'sourcePointer':item['sourcePointer'], 'prediction':result, 'view':view})
    paths = {tuple(x['outcomeKey']): x for x in literals['outcomes']}
    # Carry and check every literal row, including excluded outcomes.
    for row in literals['rows']:
        item = paths[tuple(row['outcomeKey'])]
        key, ci, gid = row['outcomeKey'], row['classIndex'], row['groupId']
        carried.append(companion.accompany([key[2],key[4],ci,gid], row, item['literal'], [{'source':'assembled-source.json','sha256':sha(canonical(document)), 'pointer':item['sourcePointer']+f'/classes/{ci}','groupId':gid}]))
    require(canonical(literals) == before, 'Classifier/companion mutated literal export')
    return predictions, carried

def compare(oracle, predictions, inventory):
    pred = {x['sourcePointer']:x for x in predictions}
    require(len(pred) == len(predictions) and set(pred) == set(oracle), 'Prediction coverage differs')
    rows = []
    for path, item in oracle.items():
        result = {'sourcePointer':path, 'nctId':item['nctId'], 'eligibility':item['eligibility'], 'oracle':item, 'prediction':pred[path]}
        if item['eligibility'] != 'excluded':
            expected = family_view(item['family'])
            observed = family_view(pred[path]['view'])
            result['fieldAgreement'] = {k: observed[k] == expected[k] for k in FIELDS}
            result['jointAgreement'] = all(result['fieldAgreement'].values())
        rows.append(result)
    strata = {}
    for stratum in ('eligible','uncertain'):
        subset = [r for r in rows if r['eligibility'] == stratum]
        studies = sorted({r['nctId'] for r in subset})
        strata[stratum] = {'outcomes':len(subset),'studies':len(studies),'jointAgreements':sum(r['jointAgreement'] for r in subset),'fieldAgreements':{k:sum(r['fieldAgreement'][k] for r in subset) for k in FIELDS}, 'studyAllOutcomesJointAgreement':{n:all(r['jointAgreement'] for r in subset if r['nctId']==n) for n in studies}}
    return {'screeningCounts':dict(Counter(r['eligibility'] for r in rows)), 'studyInventory':inventory, 'strata':strata, 'comparisons':rows, 'literalRoleScoring':'Roles and confirmation/reader/scope judgments are retained but not automatically scored; no scope equivalence is inferred.', 'limitations':['Observed metadata frame only, not atomic population.', 'No clinical accuracy, safety, efficacy or population error inference.', 'Classification disagreement is a result, not execution failure.']}

def run(manifest_path, out):
    require(not out.exists(), 'Output must be fresh')
    base = manifest_path.resolve().parent
    require(shutil.disk_usage(base).free >= 10*1024**3+20*1024**2, 'Headroom requires 10 GiB plus 20 MiB')
    manifest_raw = manifest_path.read_bytes()
    manifest = parse(manifest_raw)
    require(manifest['adapterSHA256'] == sha(Path(__file__).read_bytes()), 'Adapter freeze mismatch')
    require(manifest['schemaSHA256'] == sha(Path(__file__).with_name('evaluation-schema.json').read_bytes()), 'Schema freeze mismatch')
    document = assemble(base, manifest)
    gold_raw = read_bound(base, manifest['oracle'], 1048576)
    gold = parse(gold_raw)
    oracle, inventory = validate_oracle(gold, document, manifest['assembledSourceSHA256'])
    extractor = load_code(base, manifest['code']['extractor'], 'extractor')
    audit = load_code(base, manifest['code']['audit'], 'audit')
    payload = load_code(base, manifest['code']['payloadAudit'], 'payloadAudit')
    raw = canonical(document)
    loaded, receipt = extractor.load_verified(raw, sha(raw), {'kind':'live-capture','name':'assembled-source.json','retrievedUtc':manifest['frozenUTC']})
    literals = extractor.extract(loaded, receipt)
    fidelity = audit.audit(document, literals)
    # Hash equality adds JSON scalar-type sensitivity to the reused audit's Python equality.
    for item in literals['outcomes']: require(same(item['literal'],pointer(document,item['sourcePointer'])), 'Full outcome JSON type/literal mismatch')
    companion = load_code(base, manifest['code']['companion'], 'companion')
    out.mkdir(parents=True)
    used = 0
    def save(name, value):
        nonlocal used
        data = canonical(value) + b'\n'
        used += len(data)
        require(used <= 16*1024**2, 'Derived artifact cap (4 MiB reserved for original input archive)')
        (out/name).write_bytes(data)
        return sha(data)
    save('assembled-source.json', document)
    save('oracle-preserved.json', gold)
    save('input-manifest.json', manifest)
    predictions, carried = predict(document, literals, companion)
    # Freeze outputs before the first agreement calculation.
    prediction_sha = save('predictions.json', predictions)
    carried_sha = save('family-companions.json', carried)
    save('literal-extraction.json', literals)
    native = payload.verify(document, literals, carried)
    require(native['companionRows'] == len(literals['rows']), 'Companion row coverage incomplete')
    for c in carried: require(c['acceptedRowSHA256'] == sha(canonical(c['acceptedRowUnchanged'])), 'Carried row hash mismatch')
    result = compare(oracle, predictions, inventory)
    result.update(schema='registry-next-slice-evaluation/1', status='complete', manifestSHA256=sha(manifest_raw), sourceSHA256=sha(raw), oracleSHA256=sha(gold_raw), predictionsSHA256=prediction_sha, companionsSHA256=carried_sha, literalFidelity=fidelity, payloadAudit=native)
    save('results.json', result)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = p.parse_args()
    run(args.manifest,args.out)
