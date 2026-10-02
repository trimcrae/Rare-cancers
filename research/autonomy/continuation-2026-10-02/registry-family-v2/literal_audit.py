"""Source-coordinate fidelity audit, independent of semantic classification."""
from collections import Counter
import hashlib
import json

def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()

def require(ok, message):
    if not ok: raise ValueError(message)

def pointer(document, path):
    value = document
    for token in path.split('/')[1:]:
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value

def audit(document, extracted):
    expected = {}
    expected_cells = Counter()
    expected_rows = set()
    for si, study in enumerate(document['studies']):
        nct = study['protocolSection']['identificationModule']['nctId']
        for oi, outcome in enumerate(study.get('resultsSection', {}).get('outcomeMeasuresModule', {}).get('outcomeMeasures', [])):
            path = f'/studies/{si}/resultsSection/outcomeMeasuresModule/outcomeMeasures/{oi}'
            expected[path] = (nct, outcome)
            for ci, cls in enumerate(outcome.get('classes', [])):
                gids = set(g.get('id') for g in outcome.get('groups', []))
                for ki, cat in enumerate(cls.get('categories', [])):
                    for mi, measurement in enumerate(cat.get('measurements', [])):
                        expected_cells[(path, ci, ki, mi)] += 1
                        gids.add(measurement.get('groupId'))
                expected_rows.update((path, ci, gid) for gid in gids)
    actual = {}
    for item in extracted['outcomes']:
        path = item['sourcePointer']
        require(path in expected and path not in actual, 'Missing/duplicate/unexpected outcome coordinate')
        nct, source = expected[path]
        require(item['literal'] == source == pointer(document, path), 'Outcome literal mismatch')
        key = item['outcomeKey']
        require(key[1] == int(path.split('/')[2]) and key[3] == int(path.split('/')[-1]), 'Outcome index mismatch')
        require(key[2] == nct and key[4] == hashlib.sha256(canonical(source)).hexdigest(), 'Outcome identity/hash mismatch')
        actual[path] = item
    require(set(actual) == set(expected), 'Incomplete outcome coverage')
    inventory = []
    # Include empty categories and denominator objects with no matched group counts.
    # Their preservation is checked independently of whether any extraction row uses them.
    for path, (_, outcome) in expected.items():
        targets = [(path+'/denoms/'+str(i), v) for i,v in enumerate(outcome.get('denoms', []))]
        for ci, cls in enumerate(outcome.get('classes', [])):
            targets += [(path+f'/classes/{ci}/denoms/{i}', v) for i,v in enumerate(cls.get('denoms', []))]
            targets += [(path+f'/classes/{ci}/categories/{i}', v) for i,v in enumerate(cls.get('categories', []))]
        for target, value in targets:
            retained = pointer({'literal':actual[path]['literal']}, '/literal'+target[len(path):])
            require(value == retained == pointer(document,target), 'Unchanged category/denominator inventory failed')
            inventory.append({'pointer':target,'sha256':hashlib.sha256(canonical(value)).hexdigest()})
    keys = {tuple(v['outcomeKey']): k for k,v in actual.items()}
    seen_cells, seen_rows, evidence = Counter(), set(), []
    for row in extracted['rows']:
        path = keys[tuple(row['outcomeKey'])]
        outcome = expected[path][1]
        ci, gid = row['classIndex'], row['groupId']
        require(row['rowKey'] == row['outcomeKey']+[ci,gid], 'Row key mismatch')
        identity = (path, ci, gid)
        require(identity in expected_rows and identity not in seen_rows, 'Unexpected/duplicate class-group row')
        seen_rows.add(identity)
        cls = outcome['classes'][ci]
        require(row['classLiteral'] == {k:v for k,v in cls.items() if k!='categories'}, 'Class literal mismatch')
        require(row['groupDefinitions'] == [g for g in outcome.get('groups', []) if g.get('id')==gid], 'Group definitions mismatch')
        for cell in row['measurements']:
            ki, mi = cell['categoryIndex'], cell['measurementIndex']
            category = cls['categories'][ki]
            cp = f'{path}/classes/{ci}/categories/{ki}'
            mp = f'{cp}/measurements/{mi}'
            require(cell['categoryLiteral'] == {k:v for k,v in category.items() if k!='measurements'}, 'Category literal mismatch')
            require(cell['measurementLiteral'] == pointer(document, mp) and cell['measurementLiteral'].get('groupId')==gid, 'Measurement literal/group mismatch')
            seen_cells[(path,ci,ki,mi)] += 1
            evidence.append({'kind':'measurement','pointer':mp,'categoryPointer':cp,'sha256':hashlib.sha256(canonical(pointer(document,mp))).hexdigest()})
        for scope, parent in [('class',cls),('outcome',outcome)]:
            expected_denoms = []
            for di, denom in enumerate(parent.get('denoms', [])):
                for vi, count in enumerate(denom.get('counts', [])):
                    if count.get('groupId')==gid: expected_denoms.append((di,vi,denom,count))
            entries = row['denominators'][scope+'Entries']
            require(len(entries)==len(expected_denoms), 'Denominator entry coverage mismatch')
            for entry,(di,vi,denom,count) in zip(entries,expected_denoms):
                dp = (f'{path}/classes/{ci}' if scope=='class' else path)+f'/denoms/{di}'
                require(entry['scope']==scope and entry['denomIndex']==di and entry['countIndex']==vi and entry['unitsLiteral']==denom.get('units') and entry['countLiteral']==count, 'Denominator literal/scope mismatch')
                evidence.append({'kind':'denominator','pointer':dp,'countPointer':f'{dp}/counts/{vi}','sha256':hashlib.sha256(canonical(pointer(document,dp))).hexdigest()})
    require(seen_rows==expected_rows and seen_cells==expected_cells, 'Incomplete row/measurement coverage')
    return {'outcomes':len(actual),'rows':len(seen_rows),'measurements':sum(seen_cells.values()),'fullOutcomeLiteralsEqual':True,'allCategoryDenominatorObjects':inventory,'sourceCoordinates':evidence}
