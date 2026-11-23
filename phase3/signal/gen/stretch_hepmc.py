#!/usr/bin/env python3
"""stretch_hepmc.py IN.hepmc OUT.hepmc FACTOR [NMAX]
VALIDATION ONLY (not physics): move every LW decay tree so that SV' = PV + FACTOR*(SV - PV)
(FACTOR = -1 is exactly lw_reflect_hepmc.py; e.g. +20/-20 give ~1 mm displacements that the CMS tracker resolves
easily), using the same tree logic as generation/events/tools/lw_reflect_hepmc.py. Time is scaled the same way."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../generation/events/tools'))
from hepmc2io import read_events, _open  # noqa: E402
from lw_reflect_hepmc import fmt  # noqa: E402

inp, outp, F = sys.argv[1], sys.argv[2], float(sys.argv[3])
nmax = int(sys.argv[4]) if len(sys.argv) > 4 else -1
n = 0
with _open(outp, 'wt') as fo:
    for header, ev in read_events(inp):
        fo.writelines(header)
        if ev is None:
            continue
        if 0 <= nmax <= n:
            continue
        n += 1
        shift = {}
        for top, bot in ev.lw_chains(9000011):
            pv = ev.vertices[top.prod].pos if top.prod in ev.vertices else [0, 0, 0, 0]
            sv = ev.vertices[bot.end].pos
            d = [(F - 1.0) * (sv[i] - pv[i]) for i in range(4)]
            for v in ev.descendant_vertices(bot.end):
                shift[v] = d
        for v, d in shift.items():
            vx = ev.vertices[v]
            f = ev.lines[vx.line].split()
            vx.pos = [vx.pos[i] + d[i] for i in range(4)]
            f[3:7] = [fmt(x) for x in vx.pos]
            ev.lines[vx.line] = ' '.join(f) + '\n'
        fo.writelines(ev.lines)
print('stretched %d events by factor %g -> %s' % (n, F, outp))
