"""Independent exact logrank arithmetic and baseline input adapter audit."""
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path


def score(rows):
    u = v = F(0)
    records = [(F(str(r['time'])), r['event'], r['arm']) for r in rows]
    for t in sorted({t for t, e, a in records if e}):
        ya = sum(x >= t and a == 'a' for x, e, a in records)
        yb = sum(x >= t and a == 'b' for x, e, a in records)
        da = sum(x == t and e and a == 'a' for x, e, a in records)
        db = sum(x == t and e and a == 'b' for x, e, a in records)
        y, d = ya + yb, da + db
        u += F(da) - F(d * ya, y)
        if y > 1:
            v += F(ya * yb * d * (y-d), y*y*(y-1))
    assert v or not u
    return u*u/v if v else F(0)


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'artifact-manifest.json').read_text())
    for entry in manifest['files']:
        b = (root/entry['path']).read_bytes()
        assert len(b) == entry['bytes'] and hashlib.sha256(b).hexdigest() == entry['sha256']
    cases = []
    for file in sorted((root/'development').glob('*-result.json')):
        out = json.loads(file.read_text())
        release = json.loads(file.with_name(file.name.replace('-result', '-release')).read_text())
        for arm in ('a', 'b'):
            supplied, logged = release[arm], out['inputs'][arm]
            assert logged['n'] == supplied['n'] and logged['events'] == supplied['total_events']
            risks = {int(k): v for k, v in supplied['risk_counts'].items()}
            assert risks.pop(1) == supplied['n']
            risks[0] = supplied['n']
            endpoint = max(release['grid'])+1
            risks[endpoint] = 0
            assert dict(zip(logged['trisk'], logged['nrisk'])) == risks
            assert logged['time'] == [0] + release['grid'] + [endpoint]
            assert list(map(F, map(str, logged['surv']))) == [F(1)] + list(map(F, supplied['survival_rounded'])) + [F(supplied['survival_rounded'][-1])]
        for method, result in out['methods'].items():
            if result['status'] == 'failure':
                cases.append(dict(case=file.stem, method=method, status='failure', error=result['error']))
                continue
            q = score(result['ipd'])
            p = math.erfc(math.sqrt(float(q)/2))
            difference = abs(p-result['logrank_p'])
            assert difference < 2e-13, (file.name, method, difference)
            cases.append(dict(case=file.stem, method=method, status='success', exact_q=str(q),
                              p_approx=p, r_p=result['logrank_p'], discrepancy=difference))
    result = dict(passed=True, manifest_files_checked=len(manifest['files']), release_adapters_checked=18,
                  successful_logrank_checks=sum(c['status']=='success' for c in cases),
                  retained_failures=sum(c['status']=='failure' for c in cases),
                  max_p_discrepancy=max(c.get('discrepancy',0) for c in cases), cases=cases,
                  scope='Coordinator exact arithmetic on returned records and explicit release-to-R adapter inputs; no clinical or superiority inference.')
    (root/'coordinator-check-result.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: result[k] for k in ('passed', 'manifest_files_checked', 'release_adapters_checked', 'successful_logrank_checks', 'retained_failures', 'max_p_discrepancy')}))


if __name__ == '__main__':
    main()
