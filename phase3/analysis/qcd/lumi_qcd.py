#!/usr/bin/env python3
"""Integrated luminosity of the data files already processed by the QCD production (qcd/out/data/*.root).
Same method as ../lumi_calc.py (byte fraction of each dataset; file size ~ number of events):
L = sum over datasets of L_d * (bytes of processed files) / (bytes of the whole dataset),
with L_d = 4412 pb^-1 (Run2012B, rec 6005) and 7055 pb^-1 (Run2012C, rec 6031). All 4331 files -> 11467 pb^-1.
Writes qcd/lumi_qcd.json (read by qcd_desde_datos.py).
"""
import os, glob, json
HERE = os.path.dirname(os.path.abspath(__file__)); ANA = os.path.dirname(HERE)
DS = {'6005': 4412.0, '6031': 7055.0}
done = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(HERE, 'out', 'data', '*.root')) if not f.endswith('.tmp.root')}
res = {'datasets': {}}; L = 0.
for rec, Ld in DS.items():
    sizes = {}
    for line in open(os.path.join(ANA, 'filelists', 'rec%s_sizes.tsv' % rec)):
        u, s, _ = line.split('\t'); sizes[os.path.basename(u)[:-5]] = int(s)
    mine = [b for b in sizes if b in done]
    fb = sum(sizes[b] for b in mine) / sum(sizes.values())
    res['datasets'][rec] = dict(files_done=len(mine), files_total=len(sizes), byte_fraction=fb, L_pb=Ld * fb)
    L += Ld * fb
res['L_processed_pb'] = L; res['fraction_of_11467pb'] = L / 11467.
json.dump(res, open(os.path.join(HERE, 'lumi_qcd.json'), 'w'), indent=1)
print('archivos de datos procesados: %d ; L = %.1f pb^-1 (%.1f %% de 11.5 fb^-1)' % (len(done), L, 100 * L / 11467.))
