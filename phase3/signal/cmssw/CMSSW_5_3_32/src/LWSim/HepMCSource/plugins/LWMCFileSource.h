#ifndef LW_LWMCFileSource_h
#define LW_LWMCFileSource_h

/** \class LWMCFileSource
 *
 * Reads in HepMC events
 * Joanna Weng & Filip Moortgat 08/2005 
 ***************************************/

#include "FWCore/Sources/interface/ExternalInputSource.h"

class LWHepMCFileReader;

namespace HepMC{
  class GenEvent;
}

namespace edm {
  class Event;
  struct InputSourceDescription;
  class ParameterSet;

  class LWMCFileSource : public ExternalInputSource {
  public:
    LWMCFileSource(const ParameterSet& pset, const InputSourceDescription& desc);
    virtual ~LWMCFileSource();

  private:
    virtual bool produce(Event &e);
    void clear();
    
    LWHepMCFileReader *reader_;
    HepMC::GenEvent *evt_;
    bool useExtendedAscii_;
  };
} 

#endif
