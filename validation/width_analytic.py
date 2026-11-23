#!/usr/bin/env python3
"""
Validacion teorica independiente (fase 1) de Sanchez, ACI 15(1) 2780 (2023), Tabla 1.

Ejecutar:  python3 -I validation/width_analytic.py
Salidas:   validation/widths_schemes.csv, validation/ctau_vs_M.png, resumen en stdout.

---------------------------------------------------------------------------
DERIVACION: anchura a dos cuerpos  F(M) -> f(m) Z(mZ)  con  L = -c Z_mu fbar g^mu P_R F + h.c.
---------------------------------------------------------------------------
Amplitud: iA = -i c  ubar_f(p) g^mu P_R u_F(P) eps*_mu(k),   P = p + k.

Suma de espines/polarizaciones (sum eps eps* = -g + k k / mZ^2):
  sum|A|^2 = c^2 Tr[(p/ + m) g^mu P_R (P/ + M) P_L g^nu] (-g_mu nu + k_mu k_nu/mZ^2)
P_R(P/+M)P_L = P/ P_L (el termino de masa M desaparece por quiralidad pura) y el
termino en m tiene un numero impar de gammas, de modo que
  Tr[...] = 2( p^mu P^nu + p^nu P^mu - g^mu nu p.P )  (+ termino eps antisimetrico, se anula)
  contraccion con -g      :  4 p.P
  contraccion con kk/mZ^2 :  4 (k.p)(k.P)/mZ^2 - 2 p.P
  =>  sum|A|^2 = c^2 [ 2 p.P + 4 (k.p)(k.P)/mZ^2 ]
con  p.P = (M^2+m^2-mZ^2)/2,  k.P = (M^2-m^2+mZ^2)/2,  k.p = (M^2-m^2-mZ^2)/2.
  Gamma = |p_cm| /(8 pi M^2) * (1/2) sum|A|^2 ,  |p_cm| = lambda^{1/2}(M^2,m^2,mZ^2)/(2M).
Limite m -> 0 (x = mZ^2/M^2):
  sum|A|^2 = c^2 (M^2-mZ^2)(M^2+2mZ^2)/mZ^2
  Gamma    = c^2 M^3 /(32 pi mZ^2) (1-x)^2 (1+2x)              (*)
El factor M^3/mZ^2 viene de la polarizacion longitudinal (eps_L ~ k/mZ). Equivalencia de
Goldstone: c = (g/cW)(1/2)(m_e/M) => c^2/mZ^2 = (g/cW)^2 m_e^2/(4 M^2 mZ^2)
= m_e^2/(M^2 v^2) * ... ; con (g/cW)^2 = 4 sqrt2 GF mZ^2 = 4 mZ^2/v^2:
  Gamma(F->eZ) = GF m_e^2 M /(16 sqrt2 pi) (1-x)^2(1+2x)  -> y_e^2 M/(64 pi)  (M >> mZ),
que coincide con Gamma(F->e h) = y_e^2 M/(64 pi)(1-mh^2/M^2)^2 (acoplamiento y_e/sqrt2 de
ebar_R l~_L h, Alvarez et al. Ec. 8): patron Z : h : W = 1 : 1 : 0 para el LW-doblete
(W nu suprimido por un m_e/M extra, Alvarez Tabla II).
OBSERVACION: con GF como input, la anchura NO depende de mW ni de sW (solo de GF, m_e, mZ
via el espacio fasico). Por eso los esquemas "on-shell+GF" y "SM.fr de FeynRules" dan
exactamente lo mismo.
"""
import csv
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HBARC = 1.973269804e-13  # GeV mm
HBAR = 6.582119569e-25   # GeV s

M_PAPER = np.array([200., 300., 400., 500.])
LAM_PAPER = np.array([2.70765e-02, 1.64300e-02, 1.21212e-02, 9.65243e-03])  # mm
SIG_PAPER = np.array([5.97, 0.96, 0.23, 0.06])  # fb, 8 TeV

GF = 1.16637e-5
MZ = 91.1876
ME_PDG = 0.51099895e-3


# ----------------------------------------------------------------------------- widths
def kallen(a, b, c):
    return a * a + b * b + c * c - 2 * (a * b + a * c + b * c)


def width_FtofV(M, c, mV, m=0.0):
    """Gamma(F -> f V), coupling c * fbar gamma^mu P_{R or L} F (pure chiral), full masses."""
    M2, m2, V2 = M * M, m * m, mV * mV
    pP = (M2 + m2 - V2) / 2
    kP = (M2 - m2 + V2) / 2
    kp = (M2 - m2 - V2) / 2
    amp2 = c * c * (2 * pP + 4 * kp * kP / V2)
    pcm = np.sqrt(np.maximum(kallen(M2, m2, V2), 0)) / (2 * M)
    return pcm / (8 * np.pi * M2) * 0.5 * amp2


def width_FtofV_massless(M, c, mV):
    x = mV ** 2 / M ** 2
    return c * c * M ** 3 / (32 * np.pi * mV ** 2) * (1 - x) ** 2 * (1 + 2 * x)


def width_Ftofh(M, y, mh):
    """Gamma(F -> f h) for chiral Yukawa y * fbar_R F_L h (+h.c.), m_f = 0."""
    r = mh ** 2 / M ** 2
    return y * y * M / (32 * np.pi) * (1 - r) ** 2


# ----------------------------------------------------------------------------- EW schemes
def gZ2_from_alpha(alpha, sw2):
    return 4 * np.pi * alpha / (sw2 * (1 - sw2))


def mg_sm_scheme(aEWM1=127.9, Gf=GF, mZ=MZ):
    aEW = 1 / aEWM1
    MW = math.sqrt(mZ ** 2 / 2 + math.sqrt(mZ ** 4 / 4 - math.pi * aEW * mZ ** 2 / (math.sqrt(2) * Gf)))
    sw2 = 1 - MW ** 2 / mZ ** 2
    return aEW, MW, sw2


aEW_mg, MW_mg, sw2_mg = mg_sm_scheme()
MW_OS = 80.385  # PDG 2012-2014 (epoca del analisis); 80.379 (PDG2020) cambia <0.1%
sw2_OS = 1 - MW_OS ** 2 / MZ ** 2

SCHEMES = [
    # name, (g/cW)^2, description
    ("a_onshell_GF", 4 * math.sqrt(2) * GF * MZ ** 2,
     "sW2=1-mW2/mZ2 (on-shell), g^2=4sqrt2 GF mW^2 -> (g/cW)^2=4sqrt2 GF mZ^2"),
    ("b_FeynRules_SMfr", gZ2_from_alpha(aEW_mg, sw2_mg),
     f"SM.fr: aEWM1=127.9, Gf, MZ -> MW={MW_mg:.4f}, sW2={sw2_mg:.5f}"),
    ("c_MSbar_alphaMZ", gZ2_from_alpha(1 / 127.9, 0.2312),
     "sW2(mZ)MSbar=0.2312, alpha(mZ)=1/127.9"),
    ("d1_alpha0_onshell", gZ2_from_alpha(1 / 137.036, sw2_OS),
     f"alpha(0)=1/137.036, sW2 on-shell={sw2_OS:.5f} (mW=80.385)"),
    ("d2_alpha0_MSbar", gZ2_from_alpha(1 / 137.036, 0.2312),
     "alpha(0)=1/137.036, sW2=0.2312"),
    ("e_GF_mW_MSbar_cW", 4 * math.sqrt(2) * GF * MW_OS ** 2 / (1 - 0.2312),
     "g from GF,mW ; cW^2=1-0.2312 (mezcla inconsistente)"),
]
ME_CHOICES = [("me_PDG", ME_PDG), ("me_0.511", 0.511e-3), ("me_0.5", 0.5e-3)]


def ctau_Z(M, gZ2, me, mZ=MZ, massive_e=True):
    c = math.sqrt(gZ2) * 0.5 * me / M
    G = width_FtofV(M, c, mZ, me if massive_e else 0.0)
    return HBARC / G, G


def main():
    rows = []
    print("=" * 78)
    print("Ratio R = (hbar c / Gamma_Z) / lambda_paper  para M = 200,300,400,500 GeV")
    print("=" * 78)
    best = None
    for sname, gZ2, desc in SCHEMES:
        for mname, me in ME_CHOICES:
            ct, G = ctau_Z(M_PAPER, gZ2, me)
            R = ct / LAM_PAPER
            spread = (R.max() - R.min()) / R.mean()
            for Mi, Gi, cti, Ri in zip(M_PAPER, G, ct, R):
                rows.append(dict(scheme=sname, me_GeV=me, gZ2=gZ2, M_GeV=Mi, Gamma_GeV=Gi,
                                 ctau_mm=cti, lambda_paper_mm=LAM_PAPER[M_PAPER == Mi][0], ratio=Ri,
                                 description=desc))
            print(f"{sname:20s} {mname:9s} gZ2={gZ2:.5f}  R={np.array2string(R, precision=5)}"
                  f"  mean={R.mean():.5f} spread={spread:.1e}")
            score = abs(math.log(R.mean())) + spread
            if best is None or score < best[0]:
                best = (score, sname, mname, R)
    print(f"\nMejor combinacion: {best[1]} + {best[2]}  R={best[3]}")

    # mZ sensitivity (scheme a, me PDG)
    print("\nSensibilidad a mZ (esquema a, me PDG):")
    for mz in (91.1876, 91.188, 91.19, 91.2):
        ct, _ = ctau_Z(M_PAPER, 4 * math.sqrt(2) * GF * mz ** 2, ME_PDG, mz)
        print(f"  mZ={mz:8.4f}  R={np.array2string(ct / LAM_PAPER, precision=6)}")

    # free fit: overall K and mZ  (Gamma = K * Gamma_a(me_PDG))
    from scipy.optimize import least_squares

    def resid(p):
        K, mz = p
        G = K * GF * ME_PDG ** 2 * M_PAPER / (16 * math.sqrt(2) * math.pi) \
            * (1 - mz ** 2 / M_PAPER ** 2) ** 2 * (1 + 2 * mz ** 2 / M_PAPER ** 2)
        return np.log(HBARC / G / LAM_PAPER)

    fit = least_squares(resid, [1.0, 91.0])
    K, mzfit = fit.x
    print(f"\nAjuste libre: Gamma_paper = K*Gamma_a,  K={K:.6f}, mZ={mzfit:.4f} GeV, "
          f"resid max={np.abs(fit.fun).max():.1e}")
    print(f"  sqrt(K)*me_PDG = {math.sqrt(K) * ME_PDG * 1e3:.5f} MeV  (=> m_e efectiva)")
    print(f"  (0.5/0.51099895)^2 = {(0.5 / 0.51099895) ** 2:.6f};  (0.5/0.511)^2 = {(0.5 / 0.511) ** 2:.6f}")

    # Higgs channel and Alvarez cross-check
    print("\nCanal h e (LW-doblete, y_e = sqrt2 me/v, acoplamiento y_e/sqrt2):")
    v = (math.sqrt(2) * GF) ** -0.5
    ye = math.sqrt(2) * ME_PDG / v
    for mh in (125.0, 200.0):
        Gz = ctau_Z(M_PAPER, 4 * math.sqrt(2) * GF * MZ ** 2, ME_PDG)[1]
        Gh = np.where(M_PAPER > mh, width_Ftofh(M_PAPER, ye / math.sqrt(2), mh), 0)
        print(f"  mh={mh:.0f}: Gh/GZ={np.array2string(Gh / Gz, precision=3)}  "
              f"BR(Ze)={np.array2string(Gz / (Gz + Gh), precision=3)}  "
              f"tau_tot[s]={np.array2string(HBAR / (Gz + Gh), precision=2)}")
    print("  Alvarez et al. Sec. IV.B: tau(Ee3, 300 GeV, mh=200) ~ 4e-14 s")
    print(f"  tau_Z-only(300) = {HBAR / ctau_Z(300., 4 * math.sqrt(2) * GF * MZ ** 2, ME_PDG)[1]:.2e} s; "
          f"paper lambda/c = {LAM_PAPER[1] * 1e-3 / 2.99792458e8:.2e} s")
    # asymptotic Goldstone check
    Mb = 1e5
    Gz = ctau_Z(Mb, 4 * math.sqrt(2) * GF * MZ ** 2, ME_PDG)[1]
    print(f"  Goldstone: Gamma_Z/Gamma_h(mh=125) at M=100 TeV = {Gz / width_Ftofh(Mb, ye / math.sqrt(2), 125.):.5f}")
    print(f"  massive-e vs massless formula at 200 GeV: "
          f"{width_FtofV(200., 1e-6, MZ, ME_PDG) / width_FtofV_massless(200., 1e-6, MZ) - 1:.1e}")

    symplectic_check()
    boost_estimate()
    xsec_coupling_ratio()

    # CSV
    with open(os.path.join(HERE, "widths_schemes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    plot()


# ----------------------------------------------------------------------------- symplectic check
def symplectic_check(me=1e-3, Ml=1.0, Me=1.7):
    """Numerical pseudo-unitary diagonalisation of Alvarez et al. Eq. (A2) with eta=diag(1,-1,-1);
    returns the R- and L-chirality off-diagonal couplings E1-E3 of Eq. (B1) in units of me/Ml."""
    eta = np.diag([1., -1., -1.])
    Mm = np.array([[me, 0, -me], [-me, -Me, me], [0, 0, -Ml]])

    def sympl(K):
        w, V = np.linalg.eig(K)
        idx = np.argsort(np.abs(w))
        w, V = w[idx].real, V[:, idx].real
        for i in range(3):
            n = V[:, i] @ eta @ V[:, i]
            V[:, i] /= math.sqrt(abs(n))
            if V[np.argmax(np.abs(V[:, i])), i] < 0:
                V[:, i] *= -1
        return np.sqrt(np.abs(w)), V

    mL, SL = sympl(eta @ Mm.T @ eta @ Mm)
    mR, SR = sympl(eta @ Mm @ eta @ Mm.T)
    # order by mass: index 0 = E1 (electron), then the LW states; identify l~ (mass ~ Ml)
    i1 = 0
    i3 = int(np.argmin(np.abs(mL - Ml)))
    XR = SR.T @ np.diag([0, 0, 1.]) @ SR  # S_R^dag_{i3} S_R,3j
    XL = SL.T @ np.diag([0, 1., 0]) @ SL  # S_L^dag_{i2} S_L,2j
    eps = me / Ml
    print("\nChequeo simplectico (Alvarez Ec. A2/B1), eps=me/Ml=%.1e, Me/Ml=%.1f:" % (eps, Me / Ml))
    print(f"  masas fisicas = {mL}")
    print(f"  X_R[E1,E3]/eps = {XR[i1, i3] / eps:+.4f}   X_R[E3,E1]/eps = {XR[i3, i1] / eps:+.4f}  (hermitico si iguales)")
    print(f"  X_L[E1,E3]/eps = {XL[i1, i3] / eps:+.2e}  (suprimido, O(eps^2) o mas)")
    print(f"  X_R[E3,E3] = {XR[i3, i3]:+.4f} -> acoplamiento Z de l~_R = gR*eta33 - (gL-gR)*X_R33 = -gL")
    return XR, XL


# ----------------------------------------------------------------------------- boost estimate
def boost_estimate(sqrts=8000.0):
    """TOY estimate of <beta gamma_T> = <pT/M>. NOT a PDF calculation.
    Partonic sqrt(s_hat) drawn from sigma_hat(s) * dL/ds with dL/ds ~ s^-n (n bracket 3..5),
    sigma_hat ~ beta(3-beta^2)/2/s (vector-like s-channel), angular dist ~ 1+cos^2."""
    rng = np.random.default_rng(1)
    print("\nEstimacion (TOY, sin PDFs) de beta*gamma transversal y desplazamiento:")
    out = {}
    for M, lam in zip(M_PAPER, LAM_PAPER):
        res = []
        for n in (3.0, 4.0, 5.0):
            shat = (2 * M) ** 2 * (1 + rng.exponential(1.0, 400000) * 1.5)  # proposal
            beta = np.sqrt(1 - 4 * M * M / shat)
            wgt = beta * (3 - beta ** 2) / 2 / shat * shat ** (-n) * np.exp((shat / (4 * M * M) - 1) / 1.5)
            ct = rng.uniform(-1, 1, shat.size)
            wgt *= (1 + ct ** 2)
            pT = np.sqrt(shat) / 2 * beta * np.sqrt(1 - ct ** 2)
            bgT = pT / M
            m_bgT = np.average(bgT, weights=wgt)
            # fraction with transverse decay length > 20 um (exponential in proper time)
            frac = np.average(np.exp(-0.020 / (bgT * lam + 1e-30)), weights=wgt)
            res.append((n, m_bgT, m_bgT * lam * 1e3, frac))
        out[M] = res
        s = "; ".join(f"n={n:.0f}: <bg_T>={b:.2f}, <L_T>={l:.1f} um, P(L_T>20um)={f:.2f}" for n, b, l, f in res)
        print(f"  M={M:.0f}: cτ0={lam * 1e3:.1f} um | {s}")
    print("  Banda conservadora beta*gamma_T in [0.3,1.5] -> L_T in [0.3,1.5]*cτ0")
    return out


# ----------------------------------------------------------------------------- xsec coupling check
def xsec_coupling_ratio():
    """Partonic qqbar -> gamma*,Z -> F Fbar. Ratio sigma(l~_R coupled with gR, as in Sanchez Eq.1)
    / sigma(l~_R coupled with gL, vector-like doublet as in Alvarez Eq.7/B1, GOW Eq.54).
    Only gamma+Z (LW gauge bosons decoupled)."""
    sw2 = 0.2312
    e2 = 4 * math.pi / 128.0
    gz = math.sqrt(e2 / (sw2 * (1 - sw2)))
    quarks = {"u": (2 / 3, 0.5), "d": (-1 / 3, -0.5)}
    QF = -1.0
    gLF, gRF = gz * (-0.5 + sw2), gz * sw2

    def sig(shat, M, gL, gR):
        beta = math.sqrt(1 - 4 * M * M / shat)
        tot = 0
        for q, (Qq, T3) in quarks.items():
            w = 2.0 if q == "u" else 1.0  # crude u:d luminosity weight
            for gq in (gz * (T3 - Qq * sw2), gz * (-Qq * sw2)):
                prop = 1 / (shat - MZ ** 2)
                aL = Qq * QF * e2 / shat + gq * gL * prop
                aR = Qq * QF * e2 / shat + gq * gR * prop
                V = (aL + aR) / 2
                A = (aL - aR) / 2
                tot += w * beta * ((3 - beta ** 2) / 2 * V * V + beta ** 2 * A * A)
        return tot

    print("\nSeccion eficaz partonica: sigma(l~_R con gR [Ec.1]) / sigma(l~_R con gL [Alvarez B1]):")
    for M in M_PAPER:
        r = [sig((k * 2 * M) ** 2, M, gLF, gRF) / sig((k * 2 * M) ** 2, M, gLF, gLF) for k in (1.1, 1.3, 1.6)]
        print(f"  M={M:.0f}: sqrt(s)/2M=1.1,1.3,1.6 -> {np.array2string(np.array(r), precision=3)}")


# ----------------------------------------------------------------------------- plot
def plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    Ms = np.linspace(150, 600, 200)
    fig, (ax, axr) = plt.subplots(2, 1, figsize=(6.4, 6.4), sharex=True,
                                  gridspec_kw=dict(height_ratios=[3, 1.4]))
    styles = [("a_onshell_GF", ME_PDG, "on-shell / SM.fr (GF), $m_e$=0.511 MeV", "-", "#1f77b4"),
              ("c_MSbar_alphaMZ", ME_PDG, r"$\overline{MS}$ $s_W^2$=0.2312, $\alpha(m_Z)$", "--", "#2ca02c"),
              ("d1_alpha0_onshell", ME_PDG, r"$\alpha(0)$, on-shell $s_W^2$", ":", "#9467bd"),
              ("a_onshell_GF", 0.5e-3, "on-shell / SM.fr (GF), $m_e$=0.500 MeV", "-", "#d62728")]
    gz = {s[0]: s[1] for s in SCHEMES}
    for sname, me, lab, ls, col in styles:
        ct, _ = ctau_Z(Ms, gz[sname], me)
        ax.plot(Ms, ct * 1e3, ls, color=col, label=lab, lw=1.6)
        ctp, _ = ctau_Z(M_PAPER, gz[sname], me)
        axr.plot(M_PAPER, ctp / LAM_PAPER, "o" + ls, color=col, ms=4, lw=1)
    ax.plot(M_PAPER, LAM_PAPER * 1e3, "ks", ms=7, mfc="none", mew=1.5, label="Sanchez 2023, Tabla 1")
    ax.axhline(20, color="gray", lw=0.8, ls="-.")
    ax.text(560, 21, "20 μm", color="gray", fontsize=8, ha="right")
    ax.set_ylabel(r"$c\tau_0=\hbar c/\Gamma(\tilde\ell\to Ze)$ [μm]")
    ax.set_yscale("log")
    ax.legend(fontsize=7.5, frameon=False)
    ax.set_title(r"LW electron $\tilde\ell\to Ze$: proper decay length", fontsize=10)
    axr.axhline(1, color="k", lw=0.8)
    axr.set_ylabel("teo / paper")
    axr.set_xlabel(r"$M_{\tilde\ell}$ [GeV]")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "ctau_vs_M.png"), dpi=150)


if __name__ == "__main__":
    main()
