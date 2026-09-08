import json
d = json.load(open('research/modalities/emc-tissue-read-statistics.json'))
rows = d['panel_scores_with_p']['rows']
scored = {'GPL6244': [], 'GPL3290': []}
unscored = {'GPL6244': [], 'GPL3290': []}
for panel, per in rows.items():
    for plat, rec in per.items():
        (scored if rec.get('scored') else unscored)[plat].append(panel)
print('panels in artifact:', len(rows))
for plat in ('GPL6244', 'GPL3290'):
    print(plat, 'scored=%d' % len(scored[plat]), 'unscored=%d' % len(unscored[plat]), 'unscored panels:', sorted(unscored[plat]))
total = len(scored['GPL6244']) + len(scored['GPL3290'])
print('SCORED CONTRAST TOTAL =', total)
assert total == 16, 'expected 16 scored contrasts, artifact gives %d' % total
assert len(scored['GPL6244']) == 9 and len(scored['GPL3290']) == 7
assert sorted(unscored['GPL3290']) == ['hla_presented_intracellular_antigens_NOT_surface', 'somatostatin_receptor_family']
assert unscored['GPL6244'] == []
print('OK 9 + 7 = 16; the two GPL3290 unscored panels are somatostatin_receptor_family and hla_presented_intracellular_antigens_NOT_surface')
