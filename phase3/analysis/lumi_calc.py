#!/usr/bin/env python3
"""Approximate the integrated luminosity of the processed fraction of the DoublePhoton data.

brilcalc is not available, so two estimates are made:
 (1) byte fraction: L_d * (sum of sizes of fully processed files) / (dataset size), per dataset
     (file size is a good proxy of the number of events in the file; JSON filtering affects
     numerator and denominator alike);
 (2) lumi-section fraction: L_d * (# distinct certified LS seen) / (# certified LS of the run
     range of the dataset) -- underestimates slightly because LS are split across files.
L_d: 4.412 fb^-1 (Run2012B, rec 6005) and 7.055 fb^-1 (Run2012C, rec 6031), as in the paper.
"""
import json, os, glob
import uproot, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
DS = {'6005': dict(L=4412.0, runs=(193833, 196531)), '6031': dict(L=7055.0, runs=(198022, 203742))}
cert = json.load(open(os.path.join(HERE, 'data/Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt')))

def ncert(lo, hi):
    n = 0
    for r, rngs in cert.items():
        if lo <= int(r) <= hi:
            n += sum(b - a + 1 for a, b in rngs)
    return n

res = {'datasets': {}}
Lb = Lls = 0.
for rec, d in DS.items():
    sizes = {}
    for line in open(os.path.join(HERE, 'filelists/rec%s_sizes.tsv' % rec)):
        u, s, _ = line.split('\t')
        sizes[os.path.basename(u).replace('.root', '')] = int(s)
    tot = sum(sizes.values())
    done = [l.strip() for l in open(os.path.join(HERE, 'done', 'data.txt'))] if os.path.exists(os.path.join(HERE, 'done', 'data.txt')) else []
    mine = [b for b in done if b in sizes]
    psz = sum(sizes[b] for b in mine)
    ls = set()
    for b in mine:
        f = os.path.join(HERE, 'out', 'data', b + '.root')
        try:
            t = uproot.open(f)['wdv/lumis'].arrays(library='np')
            ls |= set(zip(t['run'].tolist(), t['lumi'].tolist()))
        except Exception:
            pass
    nc = ncert(*d['runs'])
    fb = psz / tot
    fl = len(ls) / nc
    res['datasets'][rec] = dict(files_done=len(mine), files_total=len(sizes), byte_fraction=fb,
                                LS_seen=len(ls), LS_certified=nc, LS_fraction=fl,
                                L_bytes_pb=d['L'] * fb, L_LS_pb=d['L'] * fl)
    Lb += d['L'] * fb; Lls += d['L'] * fl
res['L_processed_pb'] = Lb
res['L_LS_estimate_pb'] = Lls
res['fraction_of_11467pb'] = Lb / 11467.
json.dump(res, open(os.path.join(HERE, 'lumi_processed.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
