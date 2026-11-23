// $Id: LWMCFileSource.cc,v 1.16 2009/12/01 19:23:11 fabstoec Exp $

/**  
*  See header file for a description of this class.
*
*
*  $Date: 2009/12/01 19:23:11 $
*  $Revision: 1.16 $
*  \author Jo. Weng  - CERN, Ph Division & Uni Karlsruhe
*  \author F.Moortgat - CERN, Ph Division
*/

#include <iostream>
#include <string>


#include "FWCore/Framework/interface/Event.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "LWSim/HepMCSource/plugins/LWHepMCFileReader.h" 
#include "LWSim/HepMCSource/plugins/LWMCFileSource.h"
#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"


using namespace edm;
using namespace std;


//-------------------------------------------------------------------------
LWMCFileSource::LWMCFileSource(const ParameterSet & pset, InputSourceDescription const& desc) :
  ExternalInputSource(pset, desc, false),  // LW: Monte Carlo, not real data
  reader_(LWHepMCFileReader::instance()), evt_(0)
{
  edm::LogInfo("LWMCFileSource") << "Reading HepMC file:" << fileNames()[0];
  string fileName = fileNames()[0];
  // strip the file: 
  if (fileName.find("file:") == 0){
    fileName.erase(0,5);
  }  
  
  reader_->initialize(fileName);  
  produces<HepMCProduct>();
}


//-------------------------------------------------------------------------
LWMCFileSource::~LWMCFileSource(){
}


//-------------------------------------------------------------------------
bool LWMCFileSource::produce(Event &e) {
  // Read one HepMC event and store it in the Event.

  auto_ptr<HepMCProduct> bare_product(new HepMCProduct());  

  edm::LogInfo("LWMCFileSource") << "Start Reading";
  evt_ = reader_->fillCurrentEventData(); 
  if (evt_ == 0) return false;

  bare_product->addHepMCData(evt_);
  e.put(bare_product);

  return true;
}
