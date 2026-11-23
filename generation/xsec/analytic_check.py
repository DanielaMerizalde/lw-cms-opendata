#!/usr/bin/env python3
"""Chequeo analítico independiente de MG5: sigma_LO(pp -> F Fbar), q qbar -> gamma*/Z* -> F Fbar,
F = fermión pesado de carga -1 con acoplamientos al Z (g_L, g_R) en unidades de e/(s_W c_W).
PDF: rejilla LHAPDF (lhagrid1) leída directamente (el binding python de LHAPDF no funciona aquí).

sigma_hat = 4 pi alpha^2/(3 s Nc) * (1/2) sum_{i=L,R} beta [ (3-beta^2)/2 |V_i|^2 + beta^2 |A_i|^2 ],
A_ij = Q_q Q_F + g_i^q g_j^F/(s_W^2 c_W^2) * s/(s - MZ^2 + i MZ GZ),  V_i=(A_iL+A_iR)/2, A_i=(A_iR-A_iL)/2.
Uso: python3 analytic_check.py  -> imprime sigma(fb) para lwRep=0/1, gamma-only, Z-only, mu_F = M y sqrt(s_hat).
"""
import numpy as np
from scipy.interpolate import RectBivariateSpline

GRID = "/Users/danielamerizalde/Downloads/lee-wick/MG5_aMC_v3_8_1/bin/HEPTools/lhapdf6_py3/share/LHAPDF/cteq6l1/cteq6l1_0000.dat"
PB = 0.3893793721e9  # GeV^-2 -> pb
ALPHA = 1 / 127.9; SW2 = 0.23370; MZ = 91.1876; GZ = 2.4952; SQS = 8000.0
CW2 = 1 - SW2


def load(path):
    blk = open(path).read().split("---")[1].strip().splitlines()
    xs = np.array(blk[0].split(), float); qs = np.array(blk[1].split(), float)
    fl = [int(v) for v in blk[2].split()]
    data = np.array([l.split() for l in blk[3:]], float).reshape(len(xs), len(qs), len(fl))
    sp = {f: RectBivariateSpline(np.log(xs), np.log(qs), data[:, :, k], kx=3, ky=3) for k, f in enumerate(fl)}
    return lambda f, x, q: sp[f].ev(np.log(x), np.log(q)) / x   # f(x,Q)


PDF = load(GRID)
QUARKS = {1: (-1/3, -1/2), 2: (2/3, 1/2), 3: (-1/3, -1/2), 4: (2/3, 1/2)}  # pid: (Q, T3); 4 sabores (MG p)


def sighat(s, M, gF, mode="full", QF=None):
    QF = QF or {"L": -1.0, "R": -1.0}
    beta = np.sqrt(np.clip(1 - 4 * M**2 / s, 0, None))
    chi = s / (s - MZ**2 + 1j * MZ * GZ) / (SW2 * CW2)
    out = {}
    for q, (Qq, T3) in QUARKS.items():
        gq = {"L": T3 - Qq * SW2, "R": -Qq * SW2}
        tot = 0
        for i in "LR":
            A = {}
            for j in "LR":
                ga = Qq * QF[j] if mode in ("full", "a") else 0.0
                gz = gq[i] * gF[j] * chi if mode in ("full", "z") else 0.0
                A[j] = ga + gz
            V = (A["L"] + A["R"]) / 2; Ax = (A["R"] - A["L"]) / 2
            tot = tot + 0.5 * beta * ((3 - beta**2) / 2 * abs(V)**2 + beta**2 * abs(Ax)**2)
        out[q] = 4 * np.pi * ALPHA**2 / (3 * s * 3) * tot
    return out


def sigma(M, gF, mode="full", mu="M", n=400, QF=None, sqs=SQS):
    S = sqs**2; tau0 = 4 * M**2 / S
    # variables: ln tau en [ln tau0, 0], y en [ln sqrt tau, -ln sqrt tau]
    gl, gw = np.polynomial.legendre.leggauss(n)
    lt = 0.5 * np.log(tau0) * (1 - gl); wlt = -0.5 * np.log(tau0) * gw   # ln tau
    tot = 0.0
    for ltau, w1 in zip(lt, wlt):
        tau = np.exp(ltau); ymax = -0.5 * ltau
        y = ymax * gl; wy = ymax * gw
        x1 = np.sqrt(tau) * np.exp(y); x2 = np.sqrt(tau) * np.exp(-y)
        s = tau * S
        Q = M if mu == "M" else (2 * M if mu == "2M" else np.sqrt(s))
        sh = sighat(s, M, gF, mode, QF)
        lum = 0.0
        for q, val in sh.items():
            lum = lum + val * (PDF(q, x1, Q) * PDF(-q, x2, Q) + PDF(-q, x1, Q) * PDF(q, x2, Q))
        tot += w1 * tau * np.sum(wy * lum)   # d tau = tau d ln tau
    return tot * PB * 1e3  # fb


if __name__ == "__main__":
    gL = -0.5 + SW2
    reps = {0: {"L": gL, "R": SW2}, 1: {"L": gL, "R": gL}}
    print("CTEQ6L1, 4 sabores, sqrt(s)=8 TeV; sigma en fb")
    print(f"{'M':>4} {'mu':>6} {'rep0':>9} {'rep1':>9} {'a-only':>9} {'Z-only0':>9} {'Z-only1':>9}")
    for mu in ("M", "2M", "shat"):
        for M in (200, 300, 400, 500):
            r = [sigma(M, reps[0], "full", mu), sigma(M, reps[1], "full", mu), sigma(M, reps[0], "a", mu),
                 sigma(M, reps[0], "z", mu), sigma(M, reps[1], "z", mu)]
            print(f"{M:4d} {mu:>6} " + " ".join(f"{v:9.4f}" for v in r))
    # hipótesis alternativas (mu_F = sqrt(s_hat)); acoplamientos por quiralidad (foton QF, Z gF)
    H = {
        "rep0 (Ec.1 + foton)": (reps[0], None, 8000),
        "rep0 sin foton (Z-only)": (reps[0], {"L": 0.0, "R": 0.0}, 8000),
        "rep1 sin foton (Z-only)": (reps[1], {"L": 0.0, "R": 0.0}, 8000),
        "solo ~e_R (foton+Z)": ({"L": 0.0, "R": SW2}, {"L": 0.0, "R": -1.0}, 8000),
        "solo ~e_L (foton+Z)": ({"L": gL, "R": 0.0}, {"L": -1.0, "R": 0.0}, 8000),
        "solo ~e_R, sin foton": ({"L": 0.0, "R": SW2}, {"L": 0.0, "R": 0.0}, 8000),
        "solo ~e_L, sin foton": ({"L": gL, "R": 0.0}, {"L": 0.0, "R": 0.0}, 8000),
        "rep0 a 7 TeV": (reps[0], None, 7000),
        "rep0 Z-only a 7 TeV": (reps[0], {"L": 0.0, "R": 0.0}, 7000),
    }
    paper = [5.97, 0.96, 0.23, 0.06]
    print("\nHipotesis (mu_F = sqrt(s_hat), CTEQ6L1): sigma(fb) M=200..500 | sigma/paper | sigma(M)/sigma(200)")
    for k, (gF, QF, sq) in H.items():
        v = [sigma(M, gF, "full", "shat", n=200, QF=QF, sqs=sq) for M in (200, 300, 400, 500)]
        print(f"{k:26s} " + " ".join(f"{x:8.4f}" for x in v) + " | " + " ".join(f"{x/p:6.3f}" for x, p in zip(v, paper))
              + " | " + " ".join(f"{x/v[0]:6.4f}" for x in v))
    print(f"{'paper':26s} " + " ".join(f"{x:8.4f}" for x in paper) + " | " + " " * 27 + " | " + " ".join(f"{x/paper[0]:6.4f}" for x in paper))
