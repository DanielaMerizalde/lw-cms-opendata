#!/bin/bash
# Build the Pythia8 + HepMC2 driver against MG5's HEPTools (Pythia 8.317, HepMC 2.06.09)
H=/Users/danielamerizalde/Downloads/lee-wick/MG5_aMC_v3_8_1/bin/HEPTools
cd "$(dirname "$0")"
c++ -O2 -std=c++17 -Wno-deprecated-declarations lw_pythia_hepmc.cc -o lw_pythia_hepmc \
  -I$H/pythia8/include -I$H/hepmc/include -I$H/zlib/include -DGZIP \
  -L$H/pythia8/lib -Wl,-rpath,$H/pythia8/lib -lpythia8 \
  -L$H/hepmc/lib -Wl,-rpath,$H/hepmc/lib -lHepMC \
  -L$H/zlib/lib -Wl,-rpath,$H/zlib/lib -lz -ldl
