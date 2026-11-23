# Shared helpers for the phase-3A configs. Parameters come from environment variables set by run_chunk.sh:
#   LW_IN (input file), LW_OUT (output file), LW_N (max events, -1 = all), LW_FIRST (first EventID.event),
#   LW_SEED (master seed: identical for the causal and acausal job of the same chunk -> common random numbers)
import os, random
import FWCore.ParameterSet.Config as cms
P = dict(IN=os.environ['LW_IN'], OUT=os.environ['LW_OUT'], N=int(os.environ.get('LW_N', '-1')),
         FIRST=int(os.environ.get('LW_FIRST', '1')), SEED=int(os.environ['LW_SEED']))

def set_seeds(process, seed):
    """Deterministic, distinct seeds for every engine, derived from one master seed.
    (RandomNumberServiceHelper.populate() uses random.SystemRandom, i.e. NOT reproducible, so we draw the
    seeds ourselves with random.Random(seed): the causal and acausal job of a chunk get identical seeds.)"""
    from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
    h = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
    rng = random.Random(seed)
    h.insertSeeds(*[rng.randint(1, 900000000) for i in range(h.countSeeds())])

def conditions(process):
    """START53_V27::All read through Frontier (cms-frontier.openhtc.io, from the container's site-local-config).
    The container's /opt/cms-opendata-conddb/START53_V27 extract only holds the ~37 analysis-level tags,
    not the full SIM/DIGI/HLT/RECO set, so it cannot be used for production."""
    from Configuration.AlCa.GlobalTag import GlobalTag
    process.GlobalTag = GlobalTag(process.GlobalTag, 'START53_V27::All', '')

def common_io(process, outmod):
    process.maxEvents.input = P['N']
    getattr(process, outmod).fileName = 'file:' + P['OUT']
    # keep the original HepMC record (module label 'source') through all steps
    getattr(process, outmod).outputCommands.append('keep edmHepMCProduct_source_*_*')
    process.MessageLogger.cerr.FwkReport.reportEvery = 1
