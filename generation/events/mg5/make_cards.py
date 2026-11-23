#!/usr/bin/env python3
"""Build the param_cards used in phase 2B (template = MG5 param_card of the restricted model,
whose SM values come from the phase-1 card model/mg5/param_card_me5.000e-04_M200.dat).
Changes w.r.t. phase 1: etaLW = +1 (gauge-consistent with the positive-norm UFO), lwRep = 0 (Eq.1 literal),
WLW = FeynRules width (phase 1, MeLW = 5e-4). Light quark / e / mu masses are set to 0 by the
restriction card restrict_lwcms.dat, so their values here are irrelevant.
Usage: python3 make_cards.py   -> cards/param_card_M{200,300,400,500}[_lwRep1].dat
"""
import re, os
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_MG5 = os.path.join(HERE, '../../../model/mg5')
WIDTHS = {200: 7.28775e-12, 300: 1.20102e-11, 400: 1.62795e-11, 500: 2.04432e-11}

def setv(txt, name, val):
    pat = re.compile(r'^(\s*\S+\s+)(\S+)(\s+#\s*%s\s*)$' % re.escape(name), re.M)
    new, n = pat.subn(lambda m: m.group(1) + ('%.6e' % val) + m.group(3), txt)
    assert n == 1, (name, n)
    return new

for M, W in WIDTHS.items():
    # template: the restricted-model param_card written by MG5 in the process dir
    src = open(os.path.join(HERE, 'PROC_lw_ejj/Cards/param_card_default.dat')).read()
    for lwrep, tag in [(0, ''), (1, '_lwRep1')]:
        c = setv(src, 'MLW', M)
        c = setv(c, 'etaLW', 1.0)
        c = setv(c, 'lwRep', lwrep)
        c = setv(c, 'MeLW', 5.0e-4)
        c = re.sub(r'^DECAY\s+9000011\s+\S+', 'DECAY  9000011   %.6e' % W, c, flags=re.M)
        open(os.path.join(HERE, 'cards', 'param_card_M%d%s.dat' % (M, tag)), 'w').write(c)
        print('wrote param_card_M%d%s.dat  WLW=%.6e  ctau0=%.4f um' % (M, tag, W, 1.97326980e-13 / W * 1e3))
