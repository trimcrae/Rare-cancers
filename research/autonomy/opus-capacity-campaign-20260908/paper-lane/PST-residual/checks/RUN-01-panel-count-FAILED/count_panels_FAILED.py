# First attempt, preserved as run. It assumed panel_scores_with_p.rows was a LIST of row dicts;
# it is a DICT keyed by panel name, so r['platform'] indexed a string and raised TypeError.
import json,collections
d=json.load(open('research/modalities/emc-tissue-read-statistics.json'))
rows=d['panel_scores_with_p']['rows']
c=collections.Counter()
unscored=[]
for r in rows:
    c[(r['platform'],bool(r.get('scored')))]+=1
    if not r.get('scored'): unscored.append((r['platform'],r['panel']))
print('total rows:',len(rows))
for k in sorted(c): print(k,c[k])
print('scored total:',sum(v for k,v in c.items() if k[1]))
print('unscored:',unscored)
