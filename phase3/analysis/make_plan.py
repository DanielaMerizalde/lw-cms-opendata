#!/usr/bin/env python3
"""Build production plan: random ~1% of DoublePhoton files (whole files) + the online MC files.
2012 MC AODSIM records are 'partial': only ONE file per record is online on EOS (rest on tape,
'on demand'), so only that file can be streamed for each background."""
import json, random, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
frac = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
random.seed(20231)
plan = {'data': {'isData': 1, 'files': []}}
for rec in ['6005', '6031']:
    urls = [l.split('\t')[0] for l in open(os.path.join(HERE, 'filelists/rec%s_sizes.tsv' % rec))]
    n = max(1, round(frac * len(urls)))
    plan['data']['files'] += random.sample(urls, n)
for name, rec in [('DY', 7730), ('TT', 9518), ('W1', 9863), ('W2', 9864), ('W3', 9865)]:
    m = json.load(open(os.path.join(HERE, 'meta/rec%d.json' % rec)))
    online = []
    for fi in m['_file_indices']:
        online += [f['uri'] for f in fi['files'] if f.get('availability') == 'online']
    plan[name] = {'isData': 0, 'files': online}
json.dump(plan, open(os.path.join(HERE, 'plan.json'), 'w'), indent=1)
print({k: len(v['files']) for k, v in plan.items()})
