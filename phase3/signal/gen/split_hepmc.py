#!/usr/bin/env python3
"""split_hepmc.py IN.hepmc OUTDIR NPER [--first K --count C]
Split a HepMC2 IO_GenEvent ASCII file into chunks of NPER events (chunk_000.hepmc, ...), each with the
original header/footer, so that CMSSW MCFileSource jobs can run in parallel.  Event i of the input goes to
chunk i//NPER; the job for that chunk sets firstEvent = i0+1 so that EventID.event = HepMC index + 1."""
import os, sys
inp, outd, nper = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(outd, exist_ok=True)
head = []; out = None; iev = -1
for line in open(inp):
    if line.startswith('E '):
        iev += 1
        if iev % nper == 0:
            if out: out.write('HepMC::IO_GenEvent-END_EVENT_LISTING\n'); out.close()
            out = open(os.path.join(outd, 'chunk_%03d.hepmc' % (iev // nper)), 'w'); out.writelines(head)
    if iev < 0:
        head.append(line); continue
    if line.startswith('HepMC::IO_GenEvent-END'): continue
    out.write(line)
out.write('HepMC::IO_GenEvent-END_EVENT_LISTING\n'); out.close()
print('%d events -> %d chunks of %d in %s' % (iev + 1, iev // nper + 1, nper, outd))
