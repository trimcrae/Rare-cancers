import json, statistics as st, collections
d = json.load(open('nr4a2-experimental-competitor-reach.json'))
pc = d['per_cell']; frames = sorted(pc[0]['experimental']['by_frame'])
print("committed closer tally:", dict(collections.Counter(c['committed']['closed_by'] for c in pc)))
for f in frames:
    v = [c['experimental']['by_frame'][f]['nr4a2_c534_atoms'] for c in pc]
    print(f, dict(collections.Counter(c['experimental']['by_frame'][f]['closed_by'] for c in pc)),
          "| C534 atoms median/min/max", st.median(v), min(v), max(v))
com_open = {(c['placement'], c['pendant']) for c in pc if c['committed']['width'] > 0}
print("open-cell set identical in all 10 experimental frames:",
      all({(c['placement'], c['pendant']) for c in pc
           if c['experimental']['by_frame'][f]['width'] > 0} == com_open for f in frames),
      "| n_open =", len(com_open))
dw = [max(c['experimental']['by_frame'][f]['width'] for f in frames) - c['committed']['width'] for c in pc]
dl = [min(c['experimental']['by_frame'][f]['width'] for f in frames) - c['committed']['width'] for c in pc]
print("window width delta vs committed: worst shrink", min(dl), "best growth", max(dw))
closers = {c['experimental']['by_frame'][f]['closed_by'] for c in pc for f in frames}
print("every closer identity seen:", sorted(x or 'NONE' for x in closers))
