#!/usr/bin/env python3
"""Runs WDVQCDAnalyzer on the same inputs as v2 (lists/<sample>/*.txt: 43 data files, 1 file per MC
background, and the causal signal blocks), one cmsRun per file, inside the container lwqcd.
Resumable: files listed in qcd/done/<sample>.txt are skipped.

Usage (on the Mac):  python3 prod_qcd.py --njobs 3 [--samples data DY TT W1 W2 W3 sig_causal]
                     [--listdir qcd/lists_full] [--cache BYTES] [--extra lazyHQ=1]   (all 4331 data files; fast single pass)
Output: qcd/out/<sample>/<file>.root   (trees wdv/events, wdv/elA, wdv/lumis, cutflows)
"""
import os, glob, subprocess, sys, threading, time, argparse
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ANA = os.path.dirname(HERE)
CONTAINER = 'lwqcd'
ISDATA = {'data': 1}
lock = threading.Lock()
st = dict(done=0, failed=0, t0=time.time())

def done_set(s):
    p = os.path.join(HERE, 'done', s + '.txt')
    return set(l.strip() for l in open(p)) if os.path.exists(p) else set()

def run_one(s, lst, ntot, a):
    b = os.path.basename(lst)[:-4]
    os.makedirs(os.path.join(HERE, 'out', s), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs', s), exist_ok=True)
    log = os.path.join(HERE, 'logs', s, b + '.log')
    for attempt in range(3):
        t = time.time()
        cmd = ['docker', 'exec', CONTAINER, 'bash', '/work/qcd/run_qcd.sh', str(ISDATA.get(s, 0)),
               '/work/' + os.path.relpath(lst, ANA), '/work/qcd/out/%s/%s.tmp.root' % (s, b), '-1']
        cmd.append('' if a.cache is None else str(a.cache))
        cmd += a.extra
        with open(log, 'w') as lf:
            rc = subprocess.call(cmd, stdout=lf, stderr=subprocess.STDOUT)
        txt = open(log, errors='replace').read()
        if rc == 0 and 'TrigReport Events total' in txt:
            os.replace(os.path.join(HERE, 'out', s, b + '.tmp.root'), os.path.join(HERE, 'out', s, b + '.root'))
            nev = int(txt.split('TrigReport Events total = ')[1].split()[0])
            with lock:
                open(os.path.join(HERE, 'done', s + '.txt'), 'a').write(b + '\n')
                st['done'] += 1
                print('%s OK %s/%s %d ev en %.0f s  (%d/%d)' % (time.strftime('%H:%M:%S'), s, b, nev, time.time() - t,
                                                               st['done'] + st['failed'], ntot), flush=True)
            return
        time.sleep(30)
    with lock:
        st['failed'] += 1
        open(os.path.join(HERE, 'done', 'failed.txt'), 'a').write('%s %s\n' % (s, b))
        print('%s FALLÓ %s/%s (ver %s)' % (time.strftime('%H:%M:%S'), s, b, log), flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--njobs', type=int, default=3)
    ap.add_argument('--samples', nargs='+', default=['DY', 'TT', 'W1', 'W2', 'W3', 'data'])
    ap.add_argument('--listdir', default=os.path.join(ANA, 'lists'), help='folder with <sample>/<file>.txt lists')
    ap.add_argument('--cache', type=int, default=None, help='TTreeCache size in bytes (0 = off); default: CMSSW default')
    ap.add_argument('--extra', nargs='*', default=[], help='extra key=value options for wdvqcd_cfg.py, e.g. lazyHQ=1')
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, 'done'), exist_ok=True)
    tasks = []
    for s in a.samples:
        ds = done_set(s)
        for lst in sorted(glob.glob(os.path.join(os.path.abspath(a.listdir), s, '*.txt'))):
            if os.path.basename(lst)[:-4] not in ds: tasks.append((s, lst))
    print('archivos por procesar:', len(tasks), flush=True)
    with ThreadPoolExecutor(a.njobs) as ex:
        for s, lst in tasks: ex.submit(run_one, s, lst, len(tasks), a)
    print('TERMINADO: %d OK, %d fallidos, %.1f h' % (st['done'], st['failed'], (time.time() - st['t0']) / 3600), flush=True)

if __name__ == '__main__':
    main()
