#include "FWCore/PluginManager/interface/ModuleDef.h"
#include "FWCore/Framework/interface/InputSourceMacros.h"
#include "LWSim/HepMCSource/plugins/LWMCFileSource.h"
using edm::LWMCFileSource;
DEFINE_FWK_INPUT_SOURCE(LWMCFileSource);
