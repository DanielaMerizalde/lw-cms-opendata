#!/usr/bin/env python3
"""Compute the LW-electron width with MG5 compute_widths for M = 200..500 GeV and MeLW = 5.0e-4, 5.11e-4.
Usage: python3 mg5_widths.py   (paths are absolute; re-run after regenerating the UFO)
Step 0 writes mg5/param_card_default.dat (MG5 default card of the UFO, width computed at defaults).
Then for each point: mg5/param_card_<tag>.dat (input), mg5/widths_<tag>.dat (output),
logs/mg5_widths_<tag>.log, and logs/widths_mg5.csv."""
import os, re, subprocess, csv
HERE = os.path.dirname(os.path.abspath(__file__))
MG5 = "/Users/danielamerizalde/Downloads/lee-wick/MG5_aMC_v3_8_1/bin/mg5_aMC"
UFO = os.path.join(HERE, "LWElectron_UFO")
MGDIR = os.path.join(HERE, "mg5"); os.makedirs(MGDIR, exist_ok=True)
MASSES = [200, 300, 400, 500]
MES = [5.0e-4, 5.11e-4]

def run_mg(name, body):
    cmd = os.path.join(MGDIR, name + ".mg5")
    open(cmd, "w").write(f"set automatic_html_opening False\nimport model {UFO}\n{body}\n")
    with open(os.path.join(HERE, "logs", f"mg5_{name}.log"), "w") as f:
        subprocess.run([MG5, cmd], stdout=f, stderr=subprocess.STDOUT, cwd=MGDIR, timeout=900, check=True)

DEFAULT = os.path.join(MGDIR, "param_card_default.dat")
run_mg("default", f"display interactions elw-\ncompute_widths elw- --body_decay=2 --output={DEFAULT}")
card0 = open(DEFAULT).read()

def setval(card, pattern, val):
    new, n = re.subn(pattern, lambda m: m.group(1) + "%.6e" % val + m.group(2), card)
    assert n == 1, pattern
    return new

rows = []
for me in MES:
    for M in MASSES:
        tag = f"me{me:.3e}_M{M}"
        card = setval(card0, r"(?m)^(\s*9000011\s+)\S+(\s*#\s*MLW)", M)
        card = setval(card, r"(?m)^(\s*1\s+)\S+(\s*#\s*MeLW)", me)
        pin = os.path.join(MGDIR, f"param_card_{tag}.dat"); pout = os.path.join(MGDIR, f"widths_{tag}.dat")
        open(pin, "w").write(card)
        run_mg(f"widths_{tag}", f"compute_widths elw- --body_decay=2 --path={pin} --output={pout}")
        out = open(pout).read()
        w = float(re.search(r"(?m)^DECAY\s+9000011\s+(\S+)", out).group(1))
        blk = out.split("DECAY  9000011")[1].split("DECAY")[0]
        br = re.findall(r"(?m)^\s+(\S+)\s+2\s+(-?\d+)\s+(-?\d+)", blk)
        print(f"MeLW={me}  M={M}  Gamma_MG5={w:.6e} GeV  channels={br}")
        rows.append((me, M, w))
with open(os.path.join(HERE, "logs", "widths_mg5.csv"), "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["MeLW_GeV", "M_GeV", "Gamma_MG5_GeV"]); wr.writerows(rows)
