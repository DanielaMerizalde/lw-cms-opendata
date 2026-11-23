#!/usr/bin/env python3
"""truth_analysis.py -- generator-level study of the LW-electron signal (phase 2B).

Inputs (written by pythia/lw_pythia_hepmc): samples/M{M}/truth_M{M}_elw.csv, truth_M{M}_jets.csv.
  elw rows : one per LW particle (bottom copy = the one that decays): p4, PV, SV (mm), tau,
             immediate electron daughter, final (post-QED-FSR) electron, Z->q q~ partons, vertex-check counts.
  jet rows : anti-kT R=0.5 truth jets (pT>20 GeV, |eta|<4.7) on visible stable particles excluding the
             two LW-decay electrons; f_w0/f_w1 = pT fraction from the descendants of LW #0/#1.
Acausal vertices: SV' = 2 PV - SV (verified on the HepMC files by tools/hepmc_vertex_check.py,
refl_ok = all decays).  Paper "flip": kappa -> -kappa of the causal sample.

Outputs: analysis/plots/*.png, analysis/summary_truth.csv, analysis/summary_truth.txt
Usage: python3 truth_analysis.py [--masses 200 300 400 500]
"""
import argparse
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLOTS = os.path.join(HERE, 'plots')
CTAU0_UM = {200: 27.0765, 300: 16.4300, 400: 12.1212, 500: 9.65243}
COL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#6250d6']
plt.rcParams.update({'figure.dpi': 110, 'axes.grid': True, 'grid.alpha': 0.25, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False, 'font.size': 10})


def load(M):
    d = os.path.join(os.environ.get('LW_SAMPLES', os.path.join(ROOT, 'samples')), 'M%d' % M)
    e = np.genfromtxt(os.path.join(d, 'truth_M%d_elw.csv' % M), delimiter=',', names=True)
    j = np.genfromtxt(os.path.join(d, 'truth_M%d_jets.csv' % M), delimiter=',', names=True)
    return e, j


def p4(a, pre):
    return np.stack([a[pre + '_px'], a[pre + '_py'], a[pre + '_pz'], a[pre + '_E']], axis=-1)


def pt(v):
    return np.hypot(v[..., 0], v[..., 1])


def eta(v):
    p = np.linalg.norm(v[..., :3], axis=-1)
    return 0.5 * np.log((p + v[..., 2]) / np.maximum(p - v[..., 2], 1e-12))


def phi(v):
    return np.arctan2(v[..., 1], v[..., 0])


def mass(v):
    return np.sqrt(np.maximum(v[..., 3] ** 2 - np.sum(v[..., :3] ** 2, axis=-1), 0))


def dR(a, b):
    dphi = np.angle(np.exp(1j * (phi(a) - phi(b))))
    return np.hypot(eta(a) - eta(b), dphi)


def analyse(M):
    e, j = load(M)
    nev = int(e['iev'].max()) + 1
    # ---------------- LW kinematics and displacement
    pw = np.stack([e['px'], e['py'], e['pz'], e['E']], -1)
    m = e['m']
    bg = np.linalg.norm(pw[:, :3], axis=1) / m
    bgT = pt(pw) / m
    PV = np.stack([e['xp'], e['yp'], e['zp']], -1)
    SV = np.stack([e['xd'], e['yd'], e['zd']], -1)
    D = SV - PV                                     # mm
    L = np.linalg.norm(D, axis=1) * 1e3             # um
    LT = np.hypot(D[:, 0], D[:, 1]) * 1e3           # um
    # consistency: L = bg * c tau  (tau column = proper c*tau in mm)
    lcheck = np.max(np.abs(L - bg * e['tau'] * 1e3) / np.maximum(L, 1e-9))

    # ---------------- objects per elw
    ef = p4(e, 'ef')                                # final electron
    q1, q2 = p4(e, 'q1'), p4(e, 'q2')
    ei = p4(e, 'e')
    iev = e['iev'].astype(int)
    iw = e['iw'].astype(int)

    # jets: build per-event arrays (up to 10 jets, pT ordered by SlowJet)
    J = np.zeros((nev, 10, 4))
    F = np.zeros((nev, 10, 2))
    nJ = np.zeros(nev, int)
    for r in j:
        k, i = int(r['iev']), int(r['ij'])
        J[k, i] = [r['px'], r['py'], r['pz'], r['E']]
        F[k, i] = [r['f_w0'], r['f_w1']]
        nJ[k] = max(nJ[k], i + 1)
    jpt = pt(J)
    jeta = np.where(jpt > 0, eta(np.where(jpt[..., None] > 0, J, [1, 0, 0, 1])), 99)
    jgood = (jpt > 20) & (np.abs(jeta) < 2.5)

    # ---------------- event selection resembling the paper (truth level)
    # two opposite-sign electrons pT>40/25, |eta|<2.5 ; >=4 jets pT>20 |eta|<2.5
    eptev = np.zeros((nev, 2))
    eetaev = np.full((nev, 2), 99.0)
    eptev[iev, iw] = pt(ef)
    eetaev[iev, iw] = eta(ef)
    eacc = np.abs(eetaev) < 2.5
    ptsorted = np.sort(np.where(eacc, eptev, 0), axis=1)
    sel_e = (ptsorted[:, 1] > 40) & (ptsorted[:, 0] > 25)
    sel_j = jgood.sum(1) >= 4
    sel_ev = sel_e & sel_j
    sel = sel_ev[iev]

    # ---------------- visible system at the vertex and kappa_par
    # (a) parton level: e (immediate daughter) + q + q~ (= p_LW exactly)
    Pa = ei + q1 + q2
    # (b) truth jets: final electron + the two leading jets whose pT is dominated (>50%) by this LW's descendants
    Pb = np.zeros_like(Pa)
    okb = np.zeros(len(e), bool)
    mjj_b = np.full(len(e), np.nan)
    for r in range(len(e)):
        k, w = iev[r], iw[r]
        idx = [i for i in range(nJ[k]) if jgood[k, i] and F[k, i, w] > 0.5]
        if len(idx) >= 2:
            jj = J[k, idx[0]] + J[k, idx[1]]
            Pb[r] = ef[r] + jj
            mjj_b[r] = mass(jj)
            okb[r] = True
    # (b') naive: final electron + the two leading jets of the event (no truth matching)
    Pc = np.zeros_like(Pa)
    okc = nJ[iev] >= 2
    Pc[okc] = ef[okc] + J[iev[okc], 0] + J[iev[okc], 1]

    def kap(P):
        return np.sum(D * P[:, :3], axis=1)        # mm*GeV (3D)

    def kapT(P):
        return D[:, 0] * P[:, 0] + D[:, 1] * P[:, 1]
    ka, kb, kc = kap(Pa), kap(Pb), kap(Pc)
    kaT, kbT = kapT(Pa), kapT(Pb)
    # acausal: D' = -D  -> kappa' = -kappa exactly (same P); paper flip: -kappa
    ka_ref = np.sum((-D) * Pa[:, :3], axis=1)

    # WDVC-like: L_T > 20 um and |P_tot|_T > 20 GeV (visible e+jj, truth jets)
    wdvc = (LT > 20) & okb & (pt(Pb) > 20)

    # ---------------- masses
    mjj_a = mass(q1 + q2)
    mejj_a = mass(ei + q1 + q2)
    mejj_b = np.where(okb, mass(Pb), np.nan)
    # paper-like combinatorics: every electron with every pair of good jets
    comb = []          # (mjj, mejj, correct)
    for r in np.where(sel)[0]:
        k, w = iev[r], iw[r]
        idx = [i for i in range(nJ[k]) if jgood[k, i]]
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                jj = J[k, idx[a]] + J[k, idx[b]]
                corr = F[k, idx[a], w] > 0.5 and F[k, idx[b], w] > 0.5
                comb.append((mass(jj), mass(jj + ef[r]), corr))
    comb = np.array(comb) if comb else np.zeros((0, 3))

    res = dict(M=M, n_events=nev, n_lw=len(e), ctau0_um=CTAU0_UM[M],
               mean_bg=bg.mean(), mean_bgT=bgT.mean(), mean_L_um=L.mean(), mean_LT_um=LT.mean(),
               median_LT_um=np.median(LT),
               frac_LT_gt20=np.mean(LT > 20), frac_L_gt20=np.mean(L > 20),
               eff_sel_events=sel_ev.mean(),
               frac_LT_gt20_sel=np.mean(LT[sel] > 20) if sel.any() else np.nan,
               mean_LT_sel_um=LT[sel].mean() if sel.any() else np.nan,
               frac_wdvc_all=wdvc.mean(),
               frac_wdvc_sel=np.mean(wdvc[sel]) if sel.any() else np.nan,
               frac_matched_2jets=okb.mean(),
               kappa_a_mean_mmGeV=ka.mean(), kappa_a_median_mmGeV=np.median(ka),
               kappa_a_q95_mmGeV=np.quantile(ka, 0.95), kappa_a_q99_mmGeV=np.quantile(ka, 0.99),
               kappa_aT_median_mmGeV=np.median(kaT),
               kappa_b_median_mmGeV=np.median(kb[okb]), kappa_b_q95_mmGeV=np.quantile(kb[okb], 0.95),
               frac_kappa_b_neg_causal=np.mean(kb[okb] < 0),
               frac_kappa_c_neg_causal=np.mean(kc[okc] < 0),
               kappa_b_wdvc_median_mmGeV=np.median(kb[wdvc]) if wdvc.any() else np.nan,
               kappa_b_wdvc_q90_mmGeV=np.quantile(kb[wdvc], 0.90) if wdvc.any() else np.nan,
               frac_kappa_b_wdvc_within150=np.mean(np.abs(kb[wdvc]) < 150) if wdvc.any() else np.nan,
               frac_kappa_a_within150=np.mean(np.abs(ka) < 150),
               frac_kappa_a_within15=np.mean(np.abs(ka) < 15),
               kappa_ref_plus_flip_maxabs=np.max(np.abs(ka_ref + ka)),
               mjj_parton_median=np.median(mjj_a), mejj_parton_median=np.median(mejj_a),
               mjj_jets_median=np.nanmedian(mjj_b), mejj_jets_median=np.nanmedian(mejj_b),
               frac_mjj_jets_in_80_160=np.mean((mjj_b[okb] > 80) & (mjj_b[okb] < 160)) if okb.any() else np.nan,
               frac_mejj_jets_in_80_160=np.mean((mejj_b[okb] > 80) & (mejj_b[okb] < 160)) if okb.any() else np.nan,
               frac_mjj_jets_in_70_110=np.mean((mjj_b[okb] > 70) & (mjj_b[okb] < 110)) if okb.any() else np.nan,
               comb_pairs_per_e=len(comb) / max(sel.sum(), 1),
               comb_purity_mjj_80_160=(comb[(comb[:, 0] > 80) & (comb[:, 0] < 160), 2].mean()
                                       if len(comb) else np.nan),
               comb_purity_all=comb[:, 2].mean() if len(comb) else np.nan,
               comb_frac_mejj_80_160=np.mean((comb[:, 1] > 80) & (comb[:, 1] < 160)) if len(comb) else np.nan,
               L_vs_bgctau_maxreldev=lcheck,
               vtx_desc_at_PV=int(e['n_atPV'].sum()),
               vtx_desc_at_SV=int(e['n_atSV'].sum()), vtx_desc_further=int(e['n_further'].sum()))
    arr = dict(bg=bg, bgT=bgT, L=L, LT=LT, ka=ka, kb=kb[okb], kc=kc[okc], kaT=kaT, kbT=kbT[okb],
               ka_ref=ka_ref, sel=sel, mjj_a=mjj_a, mejj_a=mejj_a, mjj_b=mjj_b[okb], mejj_b=mejj_b[okb],
               comb=comb, tau=e['tau'])
    return res, arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--masses', type=int, nargs='+', default=[200, 300, 400, 500])
    a = ap.parse_args()
    os.makedirs(PLOTS, exist_ok=True)
    R, A = [], {}
    for M in a.masses:
        if not os.path.exists(os.path.join(os.environ.get('LW_SAMPLES', os.path.join(ROOT, 'samples')), 'M%d' % M, 'truth_M%d_elw.csv' % M)):
            print('skip M=%d (no truth file)' % M)
            continue
        r, arr = analyse(M)
        R.append(r)
        A[M] = arr
    keys = list(R[0].keys())
    with open(os.path.join(HERE, 'summary_truth.csv'), 'w') as f:
        f.write(','.join(keys) + '\n')
        for r in R:
            f.write(','.join(('%.6g' % r[k]) if isinstance(r[k], float) else str(r[k]) for k in keys) + '\n')
    with open(os.path.join(HERE, 'summary_truth.txt'), 'w') as f:
        for r in R:
            f.write('---- M = %d GeV\n' % r['M'])
            for k in keys:
                f.write('  %-28s %s\n' % (k, ('%.5g' % r[k]) if isinstance(r[k], float) else r[k]))
    print(open(os.path.join(HERE, 'summary_truth.txt')).read())

    Ms = sorted(A)
    # ---- 1. beta*gamma, L, L_T
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    for c, M in zip(COL, Ms):
        ax[0].hist(A[M]['bg'], bins=60, range=(0, 6), histtype='step', lw=1.6, density=True, color=c,
                   label=r'M=%d: $\langle\beta\gamma\rangle$=%.2f, $\langle\beta\gamma_T\rangle$=%.2f'
                   % (M, A[M]['bg'].mean(), A[M]['bgT'].mean()))
        ax[1].hist(A[M]['L'], bins=80, range=(0, 400), histtype='step', lw=1.6, density=True, color=c,
                   label=r'M=%d: $\langle|L|\rangle$=%.1f $\mu$m' % (M, A[M]['L'].mean()))
        ax[2].hist(A[M]['LT'], bins=80, range=(0, 200), histtype='step', lw=1.6, density=True, color=c,
                   label=r'M=%d: $\langle L_T\rangle$=%.1f $\mu$m, %.0f%% >20$\mu$m'
                   % (M, A[M]['LT'].mean(), 100 * np.mean(A[M]['LT'] > 20)))
    ax[0].set_xlabel(r'$\beta\gamma = |\vec p|/M$ of $\tilde e$')
    ax[1].set_xlabel(r'$|L| = |SV-PV|$ [$\mu$m]')
    ax[2].set_xlabel(r'$L_T$ [$\mu$m]')
    ax[1].set_yscale('log')
    ax[2].set_yscale('log')
    ax[2].axvline(20, color='0.4', ls='--', lw=1)
    for x in ax:
        x.legend(fontsize=7.5)
        x.set_ylabel('normalised')
    fig.suptitle(r'LW electron, pp $\to\tilde e^+\tilde e^-$, $\sqrt{s}$=8 TeV (MG5+Pythia8 truth)', fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, 'displacement_vs_mass.png'))
    plt.close(fig)

    # ---- 2. kappa_par (M=200 main)
    for M in Ms:
        X = A[M]
        fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.9))
        rng = (-150, 150)
        ax[0].hist(X['ka'], bins=120, range=rng, histtype='step', lw=1.8, color=COL[0], label='causal (MG5 VTIMUP)')
        ax[0].hist(X['ka_ref'], bins=120, range=rng, histtype='step', lw=1.8, color=COL[1],
                   label=r'acausal: reflected SV$^\prime$=2PV$-$SV')
        ax[0].hist(-X['ka'], bins=120, range=rng, histtype='step', lw=1.2, ls='--', color='k',
                   label=r'paper: flip $\kappa\to-\kappa$ (identical)')
        ax[0].set_xlabel(r'$\kappa_\parallel=(SV-PV)\cdot\vec P_{e q\bar q}$ [mm$\cdot$GeV]')
        ax[0].set_title('(a) parton level, 3D', fontsize=9)
        ax[1].hist(X['kb'], bins=120, range=(-150, 150), histtype='step', lw=1.8, color=COL[0], label='causal, e + 2 matched jets')
        ax[1].hist(-X['kb'], bins=120, range=(-150, 150), histtype='step', lw=1.8, color=COL[1], label='acausal (= flip)')
        ax[1].hist(X['kc'], bins=120, range=(-150, 150), histtype='step', lw=1.2, color=COL[2],
                   label='causal, e + 2 leading jets (no matching)')
        ax[1].set_xlabel(r'$\kappa_\parallel$ [mm$\cdot$GeV]')
        ax[1].set_title('(b) truth jets anti-kT 0.5, 3D', fontsize=9)
        ax[2].hist(X['kaT'] / 10, bins=100, range=(-5, 5), histtype='step', lw=1.8, color=COL[0], label='causal, transverse')
        ax[2].hist(X['ka'] / 10, bins=100, range=(-5, 5), histtype='step', lw=1.8, color=COL[3], label='causal, 3D')
        ax[2].hist(-X['ka'] / 10, bins=100, range=(-5, 5), histtype='step', lw=1.8, color=COL[1], label='acausal, 3D')
        ax[2].set_xlabel(r'$\kappa_\parallel$ [cm$\cdot$GeV]  (parton level)')
        ax[2].set_title('(c) same in cm$\\cdot$GeV; transverse vs 3D', fontsize=9)
        for x in ax:
            x.set_yscale('log')
            x.legend(fontsize=7)
            x.set_ylabel(r'$\tilde e$ decays')
        fig.suptitle(r'Truth parallelity, M=%d GeV ($c\tau_0$=%.1f $\mu$m)' % (M, CTAU0_UM[M]), fontsize=10)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, 'kappa_par_M%d.png' % M))
        plt.close(fig)

    # ---- 3. masses (M=200 and all)
    for M in Ms:
        X = A[M]
        fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.8))
        ax[0].hist(X['mjj_a'], bins=80, range=(0, 300), histtype='step', lw=1.6, color=COL[0], density=True, label=r'$m_{q\bar q}$ (parton)')
        ax[0].hist(X['mjj_b'], bins=80, range=(0, 300), histtype='step', lw=1.6, color=COL[1], density=True, label=r'$m_{jj}$ (2 matched jets)')
        ax[0].set_xlabel(r'$m_{jj}$ [GeV]')
        ax[1].hist(X['mejj_a'], bins=80, range=(0, 2.0 * M), histtype='step', lw=1.6, color=COL[0], density=True, label=r'$m_{eq\bar q}$ (parton)')
        ax[1].hist(X['mejj_b'], bins=80, range=(0, 2.0 * M), histtype='step', lw=1.6, color=COL[1], density=True, label=r'$m_{ejj}$ (matched jets)')
        ax[1].set_xlabel(r'$m_{ejj}$ [GeV]')
        C = X['comb']
        if len(C):
            ax[2].hist(C[:, 0], bins=60, range=(0, 600), histtype='step', lw=1.6, color=COL[2], label=r'$m_{jj}$ all pairs')
            ax[2].hist(C[C[:, 2] > 0, 0], bins=60, range=(0, 600), histtype='step', lw=1.6, color=COL[0], label=r'$m_{jj}$ correct pairs')
            ax[2].hist(C[:, 1], bins=60, range=(0, 600), histtype='step', lw=1.6, color=COL[3], label=r'$m_{ejj}$ all pairs')
            ax[2].hist(C[C[:, 2] > 0, 1], bins=60, range=(0, 600), histtype='step', lw=1.6, color=COL[1], label=r'$m_{ejj}$ correct pairs')
            ax[2].set_xlabel('mass [GeV]  (selected events, each e x every jet pair)')
        for x in ax:
            for v in (80, 160):
                x.axvline(v, color='0.4', ls='--', lw=1)
            x.legend(fontsize=7.5)
        fig.suptitle('Invariant masses, M=%d GeV: paper window 80-160 GeV (dashed)' % M, fontsize=10)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, 'masses_M%d.png' % M))
        plt.close(fig)


if __name__ == '__main__':
    main()
