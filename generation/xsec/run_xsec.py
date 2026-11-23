#!/usr/bin/env python3
"""Fase 2A: sigma(pp -> elw+ elw-) a sqrt(s) = 8 TeV con MG5 3.8.1 (LO, sin shower).

Uso:  python3 run_xsec.py [grupo ...]      (sin argumentos corre todos los grupos)
Cada grupo = un directorio de proceso MG (proc_*) + una lista de corridas `launch`.
Los resultados se agregan (append/actualizan) en results_raw.csv; luego make_table.py
construye xsec.csv y el gráfico.

Notas:
 * Las corridas se identifican por un nombre único (run name de MG). Si la corrida ya
   existe en results_raw.csv se omite (re-ejecución incremental).
 * A LO, pp -> elw elw es puramente electrodébil: no hay alpha_s, solo depende de mu_F.
   La variación de escala se hace con corridas separadas (scalefact = 0.5, 2) porque el
   módulo `systematics` de MG requiere el binding python de LHAPDF, que en esta
   instalación no carga (lhapdf.so compilado para py3.11 hace segfault).
"""
import os, re, sys, csv, subprocess, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
MGROOT = "/Users/danielamerizalde/Downloads/lee-wick/MG5_aMC_v3_8_1"
MG5 = os.path.join(MGROOT, "bin", "mg5_aMC")
LHACFG = os.path.join(MGROOT, "bin/HEPTools/lhapdf6_py3/bin/lhapdf-config")
UFO = "/Users/danielamerizalde/Downloads/lee-wick/lw-cms-opendata/model/LWElectron_UFO"
RAW = os.path.join(HERE, "results_raw.csv")
NEV = 10000
MASSES = [200, 300, 400, 500]
# anchos de fase 1 (MeLW = 5e-4); irrelevantes para sigma (estado final, anchura estrecha)
WIDTH = {200: 7.28775e-12, 300: 1.20102e-11, 400: 1.62795e-11, 500: 2.04432e-11}

PDF = {  # etiqueta -> comandos set
    "nn23lo1": ["set pdlabel nn23lo1"],
    "cteq6l1": ["set pdlabel lhapdf", "set lhaid 10042"],
    "mstw08lo": ["set pdlabel lhapdf", "set lhaid 21000"],
}


def scale_cmds(scale, M):
    """scale: 'dynN' (dynamical_scale_choice N), 'M', '2M', 'M/2' (fijas, muR = muF)."""
    if scale.startswith("dyn"):
        return ["set fixed_ren_scale False", "set fixed_fac_scale False",
                f"set dynamical_scale_choice {scale[3:]}"]
    mu = {"M": 1.0, "2M": 2.0, "M/2": 0.5}[scale] * M
    return ["set fixed_ren_scale True", "set fixed_fac_scale True",
            f"set scale {mu}", f"set dsqrt_q2fact1 {mu}", f"set dsqrt_q2fact2 {mu}"]


def run(proc, pdf, lwRep, M, scale="dyn-1", sf=1.0, eta=1, extra=(), tag=""):
    name = f"{proc}_{pdf}_rep{lwRep}_M{M}_{scale.replace('/', 'o')}_sf{sf:g}_eta{eta:+d}{tag}"
    name = name.replace("-", "m").replace("+", "p").replace(".", "p")
    cmds = [f"set ebeam1 4000", f"set ebeam2 4000", f"set nevents {NEV}", "set use_syst False",
            f"set MLW {M}", f"set WLW {WIDTH[M]}", f"set etaLW {eta}", f"set lwRep {lwRep}",
            f"set scalefact {sf}"] + PDF[pdf] + scale_cmds(scale, M) + list(extra)
    return dict(name=name, proc=proc, pdf=pdf, lwRep=lwRep, M=M, scale=scale, sf=sf, eta=eta,
                tag=tag, cmds=cmds)


def groups():
    G = {}
    # 1. línea base: proceso completo, PDF por defecto de MG, escala dinámica por defecto
    G["base"] = [run("full", "nn23lo1", r, M) for r in (0, 1) for M in MASSES]
    G["base"] += [run("full", "nn23lo1", 0, 200, eta=-1)]                       # etaLW es fase global
    G["base"] += [run("full", "nn23lo1", r, M, sf=f) for r in (0, 1) for M in MASSES for f in (0.5, 2.0)]
    # mu_R aislado: muR = 10*M fijo, muF dinámico -> debe dar el mismo sigma (no hay alpha_s)
    G["base"] += [run("full", "nn23lo1", 0, 200, tag="_muR10M",
                      extra=["set fixed_ren_scale True", "set scale 2000"])]
    # 2. PDFs de 2012 y escalas
    G["pdf"] = [run("full", p, r, M, scale=s) for p in ("cteq6l1", "mstw08lo") for r in (0, 1)
                for M in MASSES for s in ("dyn-1",)]
    G["pdf"] += [run("full", "cteq6l1", 0, M, scale=s) for M in MASSES for s in ("M", "2M", "dyn3", "dyn4")]
    G["pdf"] += [run("full", "cteq6l1", r, M, sf=f) for r in (0, 1) for M in MASSES for f in (0.5, 2.0)]
    # 4. diagnóstico: solo gamma / solo Z
    G["diag"] = [run("aonly", "nn23lo1", 0, M) for M in MASSES] + [run("aonly", "nn23lo1", 1, 200)]
    G["diag"] += [run("zonly", "nn23lo1", r, M) for r in (0, 1) for M in MASSES]
    # protón de 5 sabores (b b~ inicial, b masivo en el UFO)
    G["5f"] = [run("full5f", "nn23lo1", r, M) for r in (0, 1) for M in MASSES]
    # cadena de decaimiento del artículo: elw -> e Z, Z -> j j (j = g u c d s, 4 sabores)
    # (cada launch recompila 64 subprocesos -> muy lento; solo M = 200: nominal y con cut_decays)
    G["chain"] = [run("chainjj", "nn23lo1", 0, 200)]
    G["chain"] += [run("chainjj", "nn23lo1", 0, M, tag="_cutdec", extra=["set cut_decays True"]) for M in (200, 500)]
    # hipótesis "sin fotón" (solo Z, Ec. 1 literal sin derivada covariante): PDFs/escalas
    G["zbest"] = [run("zonly", p, r, M) for p in ("cteq6l1", "mstw08lo") for r in (0, 1) for M in MASSES]
    G["zbest"] += [run("zonly", p, 0, M, sf=f) for p in ("nn23lo1", "cteq6l1") for M in MASSES for f in (0.5, 2.0)]
    G["zbest"] += [run("zonly", "cteq6l1", 0, M, scale=s) for M in MASSES for s in ("M", "2M")]
    G["zbest"] += [run("zonly", "mstw08lo", 0, M, sf=f) for M in MASSES for f in (0.5, 2.0)]
    return G



FIELDS = ["name", "proc", "pdf", "lwRep", "M", "scale", "sf", "eta", "tag", "sigma_fb", "err_fb"]
SLOTS = {"full": 4, "zonly": 3, "aonly": 1, "full5f": 1, "chainjj": 2}   # copias del dir. de proceso
NCORE = 2


def parse(log):
    out = {}
    txt = open(log, errors="replace").read()
    for m in re.finditer(r"Results Summary for run: (\S+) tag: \S+ ===\s+Cross-section :\s+(\S+) \+- (\S+) pb", txt):
        out[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    return out


def load_raw():
    if not os.path.exists(RAW):
        return {}
    return {r["name"]: r for r in csv.DictReader(open(RAW))}


def slot_dir(proc, k):
    base = os.path.join(HERE, f"proc_{proc}")
    if k == 0:
        return base
    d = f"{base}_slot{k}"
    if not os.path.isdir(d):   # copia sin Events (MG trabaja en un solo run a la vez por directorio)
        subprocess.run(["rsync", "-a", "--exclude", "Events/*", "--exclude", "HTML/*", base + "/", d + "/"], check=True)
    for lock in ("RunWeb",):
        try: os.remove(os.path.join(d, lock))
        except FileNotFoundError: pass
    return d


def exec_batch(proc, k, rs):
    """Una sesión de MG por corrida: si una corrida aborta, no arrastra a las siguientes."""
    pdir = slot_dir(proc, k); res = []
    os.makedirs(os.path.join(HERE, "logs", "runs"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "scripts", "runs"), exist_ok=True)
    for r in rs:
        lines = ["set automatic_html_opening False", "set run_mode 2", f"set nb_core {NCORE}",
                 f"set lhapdf_py3 {LHACFG}", f"launch {pdir} -n {r['name']}", "shower=OFF", "done"] + r["cmds"] + ["done"]
        script = os.path.join(HERE, "scripts", "runs", f"{r['name']}.mg5")
        open(script, "w").write("\n".join(lines) + "\n")
        log = os.path.join(HERE, "logs", "runs", f"launch_{r['name']}.log")
        try: os.remove(os.path.join(pdir, "RunWeb"))
        except FileNotFoundError: pass
        with open(log, "w") as f:
            subprocess.run([MG5, script], stdout=f, stderr=subprocess.STDOUT, cwd=HERE, timeout=3 * 3600)
        xs = parse(log)
        if r["name"] in xs:
            s, e = xs[r["name"]]
            res.append({k2: r[k2] for k2 in FIELDS[:9]} | {"sigma_fb": s * 1e3, "err_fb": e * 1e3})
        else:
            print("FALLÓ:", r["name"], "ver", log, flush=True)
    return res


def main():
    G = groups()
    sel = sys.argv[1:] or list(G)
    have = load_raw()
    # recuperar corridas terminadas en logs anteriores
    import glob
    allruns = {r["name"]: r for g in G.values() for r in g}
    for log in glob.glob(os.path.join(HERE, "logs", "launch_*.log")) + glob.glob(os.path.join(HERE, "logs", "runs", "launch_*.log")):
        for n, (s, e) in parse(log).items():
            if n in allruns and n not in have:
                have[n] = {k2: allruns[n][k2] for k2 in FIELDS[:9]} | {"sigma_fb": s * 1e3, "err_fb": e * 1e3}
    todo = [r for g in sel for r in G[g] if r["name"] not in have]
    print(f"{len(have)} corridas ya hechas, {len(todo)} por hacer", flush=True)
    bat = []
    for proc, n in SLOTS.items():
        rs = [r for r in todo if r["proc"] == proc]
        for k in range(n):
            chunk = rs[k::n]
            if chunk:
                bat.append((proc, k, chunk))

    def write():
        with open(RAW, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(have.values())
    write()
    with cf.ThreadPoolExecutor(max_workers=sum(SLOTS.values())) as ex:
        futs = [ex.submit(exec_batch, *b) for b in bat]
        for fu in cf.as_completed(futs):
            for row in fu.result():
                have[row["name"]] = row
                print(f"{row['name']:60s} {row['sigma_fb']:10.4f} +- {row['err_fb']:.4f} fb", flush=True)
            write()


if __name__ == "__main__":
    main()
