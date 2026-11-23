#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TLeaf.h"
#include "TObjArray.h"
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <cstdio>
void branch_sizes(const char* fn) {
  TFile* f = TFile::Open(fn); TTree* t = (TTree*)f->Get("Events");
  Long64_t n = t->GetEntries();
  std::map<std::string,double> m; double tot = 0;
  TObjArray* all = t->GetListOfLeaves();
  std::map<TBranch*,bool> seen;
  for (int i = 0; i < all->GetEntries(); ++i) {
    TBranch* b = ((TLeaf*)all->At(i))->GetBranch(); if (seen[b]) continue; seen[b] = true;
    double z = b->GetZipBytes(); tot += z; m[b->GetMother()->GetName()] += z;
  }
  std::vector<std::pair<double,std::string> > v;
  for (std::map<std::string,double>::iterator it = m.begin(); it != m.end(); ++it) v.push_back(std::make_pair(it->second, it->first));
  std::sort(v.rbegin(), v.rend());
  printf("entries %lld  file %.0f kB/ev  sum %.1f kB/ev\n", n, f->GetSize()/1024./n, tot/n/1024.);
  for (int i = 0; i < 45 && i < (int)v.size(); ++i) printf("%7.2f kB/ev  %s\n", v[i].first/n/1024., v[i].second.c_str());
}
