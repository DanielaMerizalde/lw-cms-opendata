#!/usr/bin/env python3
"""Production driver: runs WDVAnalyzer (one cmsRun per input file) inside the container
lw3b-main with N concurrent jobs.  Resumable: files listed in done/<sample>.txt are skipped.

Usage: python3 prod.py plan.json --njobs 10
plan.json: {"sample": {"isData": 0/1, "files": [url, ...]}, ...}
"""
import json, os, subprocess, sys, threading, time, argparse
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CONTAINER = 'lw3b-main'
CONTAINERS = {}
lock = threading.Lock()
stats = dict(done=0, failed=0, events=0, t0=time.time())

def base(u):
    return os.path.basename(u).replace('.root', '')

def done_set(sample):
    p = os.path.join(HERE, 'done', sample + '.txt')
    return set(l.strip() for l in open(p)) if os.path.exists(p) else set()

def run_one(sample, isdata, url, ntot):
    b = base(url)
    os.makedirs(os.path.join(HERE, 'out', sample), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs', 'prod', sample), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'lists', sample), exist_ok=True)
    lst = os.path.join(HERE, 'lists', sample, b + '.txt')
    open(lst, 'w').write(url + '\n')
    log = os.path.join(HERE, 'logs', 'prod', sample, b + '.log')
    for attempt in range(3):
        t = time.time()
        cmd = ['docker', 'exec', CONTAINERS.get(sample, CONTAINER), 'bash', '/work/run_wdv.sh', str(isdata),
               '/work/lists/%s/%s.txt' % (sample, b), '/work/out/%s/%s.root' % (sample, b), '-1']
        with open(log, 'w') as lf:
            rc = subprocess.call(cmd, stdout=lf, stderr=subprocess.STDOUT)
        txt = open(log, errors='replace').read()
        ok = rc == 0 and 'TrigReport Events total' in txt
        if ok:
            nev = int(txt.split('TrigReport Events total = ')[1].split()[0])
            with lock:
                open(os.path.join(HERE, 'done', sample + '.txt'), 'a').write(b + '\n')
                stats['done'] += 1; stats['events'] += nev
                el = time.time() - stats['t0']
                print('%s OK %s/%s %d ev in %.0fs | total %d files %d ev %.1f ev/s (%d/%d)' % (
                    time.strftime('%H:%M:%S'), sample, b, nev, time.time() - t, stats['done'], stats['events'],
                    stats['events'] / el, stats['done'] + stats['failed'], ntot), flush=True)
            return True
        time.sleep(30)
    with lock:
        stats['failed'] += 1
        open(os.path.join(HERE, 'done', 'failed.txt'), 'a').write('%s %s\n' % (sample, url))
        print('%s FAILED %s/%s' % (time.strftime('%H:%M:%S'), sample, b), flush=True)
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan'); ap.add_argument('--njobs', type=int, default=8)
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, 'done'), exist_ok=True)
    plan = json.load(open(a.plan))
    for s_, d_ in plan.items():
        if 'container' in d_: CONTAINERS[s_] = d_['container']
    tasks = []
    # interleave samples so that partial results are balanced
    queues = []
    for s, d in plan.items():
        ds = done_set(s)
        queues.append([(s, d['isData'], u) for u in d['files'] if base(u) not in ds])
    while any(queues):
        for q in queues:
            if q: tasks.append(q.pop(0))
    tasks.sort(key=lambda t: t[0] == 'data')   # signal and MC first
    print('tasks:', len(tasks), flush=True)
    with ThreadPoolExecutor(a.njobs) as ex:
        for t in tasks:
            ex.submit(run_one, t[0], t[1], t[2], len(tasks))
    print('ALL DONE', stats, flush=True)

if __name__ == '__main__':
    main()
