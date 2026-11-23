#!/usr/bin/env python3
"""results_raw.csv -> xsec.csv (una fila por configuración y masa, con banda de escala) + xsec_vs_M.png."""
import os, csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = {200: 5.97, 300: 0.96, 400: 0.23, 500: 0.06}
rows = list(csv.DictReader(open(os.path.join(HERE, "results_raw.csv"))))
for r in rows:
    r["M"] = int(r["M"]); r["sf"] = float(r["sf"]); r["sigma_fb"] = float(r["sigma_fb"]); r["err_fb"] = float(r["err_fb"])


def cfg(r):
    c = f"{r['proc']}|{r['pdf']}|lwRep{r['lwRep']}|{r['scale']}"
    if r["eta"] != "1":
        c += f"|eta{r['eta']}"
    return c + (f"|{r['tag'].strip('_')}" if r["tag"] else "")


nom = {}; var = defaultdict(list)
for r in rows:
    key = (cfg(r), r["M"])
    if r["sf"] == 1.0:
        nom[key] = r
    else:
        var[key].append(r["sigma_fb"])

out = []
for (c, M), r in sorted(nom.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    s = r["sigma_fb"]; v = var.get((c, M), [])
    up = (max(v + [s]) / s - 1) if v else ""
    dn = (min(v + [s]) / s - 1) if v else ""
    out.append(dict(config=c, M_GeV=M, sigma_fb=f"{s:.5g}", stat_err_fb=f"{r['err_fb']:.2g}",
                    scale_up_rel=f"{up:+.4f}" if v else "", scale_down_rel=f"{dn:+.4f}" if v else "",
                    ratio_to_paper=f"{s / PAPER[M]:.4f}"))
with open(os.path.join(HERE, "xsec.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)

# ----- tabla resumen en pantalla
by = defaultdict(dict)
for o in out:
    by[o["config"]][o["M_GeV"]] = float(o["sigma_fb"])
print(f"{'config':58s} " + " ".join(f"{m:>8d}" for m in PAPER) + " | ratio/paper | sigma(M)/sigma(200)")
for c, d in by.items():
    if len(d) < 4:
        print(f"{c:58s} " + " ".join(f"{d.get(m, float('nan')):8.4f}" for m in PAPER)); continue
    print(f"{c:58s} " + " ".join(f"{d[m]:8.4f}" for m in PAPER) + " | "
          + " ".join(f"{d[m] / PAPER[m]:5.3f}" for m in PAPER) + " | " + " ".join(f"{d[m] / d[200]:.4f}" for m in PAPER))

# ----- gráfico
SHOW = [("full|nn23lo1|lwRep0|dyn-1", "γ+Z, lwRep=0 (Ec. 1), NNPDF2.3LO", "C0", "-"),
        ("full|nn23lo1|lwRep1|dyn-1", "γ+Z, lwRep=1 (doblete), NNPDF2.3LO", "C1", "-"),
        ("full|cteq6l1|lwRep0|dyn-1", "γ+Z, lwRep=0, CTEQ6L1", "C0", "--"),
        ("aonly|nn23lo1|lwRep0|dyn-1", "solo γ, NNPDF2.3LO", "C2", ":"),
        ("zonly|nn23lo1|lwRep0|dyn-1", "solo Z, lwRep=0, NNPDF2.3LO", "C3", "-"),
        ("zonly|cteq6l1|lwRep0|dyn-1", "solo Z, lwRep=0, CTEQ6L1", "C3", "--"),
        ("zonly|nn23lo1|lwRep1|dyn-1", "solo Z, lwRep=1, NNPDF2.3LO", "C4", "-"),
        ("chainjj|nn23lo1|lwRep0|dyn-1", "γ+Z, lwRep=0 × BR(Z→jj)² (cadena MG)", "C5", "-.")]
Ms = list(PAPER)
fig, (a0, a1, a2) = plt.subplots(3, 1, figsize=(7.5, 9.5), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.4, 1.4]))
a0.plot(Ms, [PAPER[m] for m in Ms], "ko", ms=8, label="Sánchez 2023, Tabla 1", zorder=5)
for c, lab, col, ls in SHOW:
    if c not in by or len(by[c]) < 4:
        continue
    y = [by[c][m] for m in Ms]
    band = [(nom[(c, m)]["sigma_fb"], var.get((c, m), [])) for m in Ms]
    a0.plot(Ms, y, color=col, ls=ls, marker=".", label=lab)
    if all(v for _, v in band):
        a0.fill_between(Ms, [min(v + [s]) for s, v in band], [max(v + [s]) for s, v in band], color=col, alpha=0.15)
    a1.plot(Ms, [by[c][m] / PAPER[m] for m in Ms], color=col, ls=ls, marker=".")
    a2.plot(Ms, [by[c][m] / by[c][200] / (PAPER[m] / PAPER[200]) for m in Ms], color=col, ls=ls, marker=".")
c = "chainjj|nn23lo1|lwRep0|dyn-1|cutdec"
if c in by:
    mm = sorted(by[c]); a0.plot(mm, [by[c][m] for m in mm], "s", color="C5", mfc="none", ms=8,
                                label="γ+Z, lwRep=0 × BR(Z→jj)² + cortes MG (cut_decays)")
    a1.plot(mm, [by[c][m] / PAPER[m] for m in mm], "s", color="C5", mfc="none")
    a2.plot(mm, [by[c][m] / by[c][200] / (PAPER[m] / PAPER[200]) for m in mm], "s", color="C5", mfc="none")
a0.set_yscale("log"); a0.set_ylabel("σ(pp → ẽ⁺ẽ⁻) [fb], √s = 8 TeV, LO")
a0.legend(fontsize=7.5, loc="upper right"); a0.grid(alpha=0.3)
a1.axhline(1, color="k", lw=0.8); a1.set_yscale("log"); a1.set_ylabel("σ / σ_artículo"); a1.grid(alpha=0.3)
a2.axhline(1, color="k", lw=0.8); a2.set_ylabel("[σ(M)/σ(200)] /\n[ídem artículo]"); a2.grid(alpha=0.3)
a2.set_xlabel("M_ẽ [GeV]"); a2.set_xticks(Ms)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "xsec_vs_M.png"), dpi=150)
print("escrito xsec.csv y xsec_vs_M.png")
