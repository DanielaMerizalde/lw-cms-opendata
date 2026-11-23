import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import FWCore.PythonUtilities.LumiList as LumiList

opts = VarParsing.VarParsing('analysis')
opts.register('isData', 1, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, '1=data, 0=MC')
opts.register('fileList', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, 'text file with input files')
opts.register('json', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, 'certified-lumi JSON (data)')
opts.register('gtConnect', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, 'override GlobalTag.connect')
opts.register('globalTag', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, 'override global tag')
opts.register('out', 'wdvqcd.root', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, 'output file')
opts.register('slim', 1, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, 'drop unused branches on input')
opts.register('cache', -1, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, 'TTreeCache size (bytes), -1 = default')
opts.register('trigMatch', 1, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, 'TO via trigger-object matching')
opts.register('rule5', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, 'Table 2.1 row 5: 0 = all pairs dR<4, 1 = some pair dR>4')
opts.register('levelAOnly', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, 'pass 1: stop before the SV step and do not read generalTracks/particleFlow')
opts.register('selList', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, 'pass 1: text file for the run:event list of events reaching the SV step')
opts.register('evList', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, 'pass 2: process only the run:event entries of this file')
opts.register('lazyHQ', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, 'single fast pass: HQ (generalTracks) only for events reaching the SV step')
opts.register('skip', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, 'events to skip')
opts.parseArguments()
isData = bool(opts.isData)

process = cms.Process('WDV')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(opts.maxEvents))

files = list(opts.inputFiles)
if opts.fileList:
    files += [l.strip() for l in open(opts.fileList) if l.strip() and not l.startswith('#')]
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(*files),
                            skipEvents=cms.untracked.uint32(opts.skip))
if opts.slim:
    process.source.inputCommands = cms.untracked.vstring(
        'drop *', 'keep *_TriggerResults_*_HLT', 'keep *_hltTriggerSummaryAOD_*_HLT', 'keep *_gsfElectrons_*_*', 'keep *_gsfElectronCores_*_*',
        'keep *SuperCluster*_*_*_*', 'keep *_electronGsfTracks_*_*', 'keep *_generalTracks_*_*',
        'keep *_ak5PFJets_*_*', 'keep *_particleFlow_*_*', 'keep *_kt6PFJets_rho_*',
        'keep *_offlinePrimaryVertices_*_*', 'keep *_allConversions_*_*', 'keep *_fixedGridRhoAll_*_*', 'keep *_offlineBeamSpot_*_*',
        'keep *_generator_*_*', 'keep *_addPileupInfo_*_*', 'keep *_genParticles_*_*')
    if opts.levelAOnly:   # pass 1: the heavy collections are only used in the SV step
        process.source.inputCommands += ['drop *_generalTracks_*_*', 'drop *_particleFlow_*_*']
    process.source.dropDescendantsOfDroppedBranches = cms.untracked.bool(False)
if opts.evList:
    evs = [l.strip() for l in open(opts.evList) if l.strip()]
    process.source.eventsToProcess = cms.untracked.VEventRange(*['%s-%s' % (e, e) for e in evs])
if opts.cache >= 0:
    process.source.cacheSize = cms.untracked.uint32(opts.cache)
if isData and opts.json:
    process.source.lumisToProcess = LumiList.LumiList(filename=opts.json).getVLuminosityBlockRange()

# conditions, geometry, field
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('JetMETCorrections.Configuration.DefaultJEC_cff')

gt = opts.globalTag or ('FT53_V21A_AN6' if isData else 'START53_V27')
if opts.gtConnect:
    process.GlobalTag.connect = cms.string(opts.gtConnect)
process.GlobalTag.globaltag = gt + '::All'

process.wdv = cms.EDAnalyzer('WDVQCDAnalyzer',
    isData=cms.bool(isData),
    # thesis (Sec. 2.2.2): OR of four diphoton paths; extra: the combined OR path (flag only)
    hltThesis=cms.vstring('HLT_Photon36_CaloId10_Iso50_Photon22_CaloId10_Iso50_v',
                          'HLT_Photon36_CaloId10_Iso50_Photon22_R9Id85_v',
                          'HLT_Photon36_R9Id85_Photon22_CaloId10_Iso50_v',
                          'HLT_Photon36_R9Id85_Photon22_R9Id85_v'),
    hltExtra=cms.vstring('HLT_Photon36_R9Id85_OR_CaloId10_Iso50_Photon22_R9Id85_OR_CaloId10_Iso50_v'),
    jecName=cms.string('ak5PFL1FastL2L3Residual' if isData else 'ak5PFL1FastL2L3'),
    # TF
    tfElePt=cms.double(20.), tfJetPt=cms.double(15.), tfNJets=cms.int32(4),
    # TO
    useTrigMatch=cms.bool(bool(opts.trigMatch)), trigMatchDR=cms.double(0.2),
    eleLeadPt=cms.double(40.), eleSubPt=cms.double(25.), eleEta=cms.double(2.5),
    # JetS
    jetPt=cms.double(20.), jetEta=cms.double(2.5), jetMinConst=cms.int32(2),
    jetNHEF=cms.double(0.9), jetNEMEF=cms.double(0.9), jetMEF=cms.double(0.8), jetEMF=cms.double(0.6),
    nJetsMin=cms.int32(4),
    # DRC
    dRdiff=cms.double(0.2),
    # SVRA
    mjjLo=cms.double(80.), mjjHi=cms.double(160.),
    trkPt=cms.double(1.), trkMinHits=cms.int32(0), trkMinPix=cms.int32(0),
    chi2Max=cms.double(5.), mergeSig=cms.double(4.),
    svMinTrk=cms.int32(5), svMinTrk3=cms.int32(3), svTrkE=cms.double(3.),
    dRclose=cms.double(0.4), dRwide=cms.double(1.2), dRmax=cms.double(4.), dRmaxMode=cms.int32(opts.rule5),
    # IPP (mm, GeV)
    ippLT=cms.double(0.02), ippPT=cms.double(20.),
    # truth matching for the signal
    lwPdg=cms.int32(9000011), genMatchDR=cms.double(0.1),
    levelAOnly=cms.untracked.bool(bool(opts.levelAOnly)), selList=cms.untracked.string(opts.selList),
    lazyHQ=cms.untracked.bool(bool(opts.lazyHQ)),
)
process.TFileService = cms.Service('TFileService', fileName=cms.string(opts.out))
process.p = cms.Path(process.wdv)
