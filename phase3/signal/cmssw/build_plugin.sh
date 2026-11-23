#!/bin/bash
# Build the LWMCFileSource plugin (MCFileSource clone flagged as MC, not real data) in a persistent CMSSW area on /work.
set -e
source /opt/cms/cmsset_default.sh
cd /work/cmssw
[ -d CMSSW_5_3_32 ] || scramv1 project CMSSW CMSSW_5_3_32
P=CMSSW_5_3_32/src/LWSim/HepMCSource/plugins; mkdir -p $P
R=$CMSSW_RELEASE_BASE
R=/opt/cms/slc6_amd64_gcc472/cms/cmssw/CMSSW_5_3_32/src/IOMC/Input
sed -e 's/IOMC_Input_HepMCFileReader_h/LW_HepMCFileReader_h/g' -e 's/HepMCFileReader/LWHepMCFileReader/g' $R/interface/HepMCFileReader.h > $P/LWHepMCFileReader.h
sed -e 's#IOMC/Input/interface/HepMCFileReader.h#LWSim/HepMCSource/plugins/LWHepMCFileReader.h#' -e 's/HepMCFileReader/LWHepMCFileReader/g' $R/src/HepMCFileReader.cc > $P/LWHepMCFileReader.cc
sed -e 's/IOMC_Input_MCFileSource_h/LW_MCFileSource_h/g' -e 's/MCFileSource/LWMCFileSource/g' -e 's/HepMCFileReader/LWHepMCFileReader/g' $R/interface/MCFileSource.h > $P/LWMCFileSource.h
sed -e 's#IOMC/Input/interface/HepMCFileReader.h#LWSim/HepMCSource/plugins/LWHepMCFileReader.h#' \
    -e 's#IOMC/Input/interface/MCFileSource.h#LWSim/HepMCSource/plugins/LWMCFileSource.h#' \
    -e 's/HepMCFileReader/LWHepMCFileReader/g' -e 's/MCFileSource/LWMCFileSource/g' \
    -e 's/ExternalInputSource(pset, desc),/ExternalInputSource(pset, desc, false),  \/\/ LW: Monte Carlo, not real data/' \
    $R/src/MCFileSource.cc > $P/LWMCFileSource.cc
cat > $P/module.cc <<'EOF'
#include "FWCore/PluginManager/interface/ModuleDef.h"
#include "FWCore/Framework/interface/InputSourceMacros.h"
#include "LWSim/HepMCSource/plugins/LWMCFileSource.h"
using edm::LWMCFileSource;
DEFINE_FWK_INPUT_SOURCE(LWMCFileSource);
EOF
sed -i "s/LWLW/LW/g" $P/*.cc $P/*.h
cp $R/BuildFile.xml $P/BuildFile.xml
grep -n "ExternalInputSource(pset" $P/LWMCFileSource.cc
cd CMSSW_5_3_32/src; eval `scramv1 runtime -sh`; scram b -j4 2>&1 | tail -5
