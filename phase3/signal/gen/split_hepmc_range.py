#!/usr/bin/env python3
"""split_hepmc_range.py IN.hepmc[.gz] OUTDIR NPER SKIP KFIRST [NMAX]
Like split_hepmc.py, but skips the first SKIP events of IN (already simulated) and numbers the chunks
from KFIRST: input event SKIP + j goes to chunk_{KFIRST + j//NPER}.hepmc. At most NMAX events are written
(default: all remaining). Each chunk keeps the original HepMC header and footer.
Used for the 2000-event causal extension (bloques de 50, b020...): see phase3/signal/PROGRESS.md."""
import gzip, os, sys
inp, outd, nper, skip, kfirst = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
nmax = int(sys.argv[6]) if len(sys.argv) > 6 else -1
os.makedirs(outd, exist_ok=True)
op = gzip.open if inp.endswith('.gz') else open
head = []; out = None; iev = -1; nw = 0; written = []
for line in op(inp, 'rt'):
    if line.startswith('E '):
        iev += 1
        if iev >= skip:
            j = iev - skip
            if 0 <= nmax <= j:
                break
            if j % nper == 0:
                if out: out.write('HepMC::IO_GenEvent-END_EVENT_LISTING\n'); out.close()
                name = os.path.join(outd, 'chunk_%03d.hepmc' % (kfirst + j // nper))
                if os.path.exists(name):
                    sys.exit('refuse to overwrite ' + name)
                out = open(name, 'w'); out.writelines(head); written.append(name)
            nw += 1
    if iev < 0:
        head.append(line); continue
    if iev < skip or line.startswith('HepMC::IO_GenEvent-END'):
        continue
    out.write(line)
if out: out.write('HepMC::IO_GenEvent-END_EVENT_LISTING\n'); out.close()
print('%s: skipped %d, wrote %d events -> %d chunks of %d (chunk_%03d..chunk_%03d) in %s'
      % (inp, skip, nw, len(written), nper, kfirst, kfirst + len(written) - 1, outd))
