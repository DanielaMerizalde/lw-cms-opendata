(* Sanity test: patched FeynRules on MMA 15 must find the SM e-e-A vertex *)
FR$Parallelize = False;
$FeynRulesPath = "/Users/danielamerizalde/Downloads/lee-wick/feynrules-patched";
SetDirectory[$FeynRulesPath]; << FeynRules`;
FR$Parallelize = False;
LoadModel[FileNameJoin[{$FeynRulesPath, "Models", "SM", "SM.fr"}]];
vall = FeynmanRules[LFermions, FlavorExpand -> True];
Print["Total fermion vertices: ", Length[vall]];
v = Select[vall, Sort[#[[1, All, 1]]] === Sort[{e, ebar, A}] || Sort[#[[1, All, 1]]] === Sort[{e, -e, A}] &];
If[v === {}, v = Select[vall, MemberQ[#[[1, All, 1]], A] && (MemberQ[#[[1, All, 1]], e] || MemberQ[#[[1, All, 1]], l]) &]];
Print["eeA vertices: ", InputForm[v]];
bad = !FreeQ[v, _Symbol?(StringMatchQ[SymbolName[#], "crea*"] &)];
Print["SANITY: ", If[Length[v] == 1 && !bad && !FreeQ[v, ee], "PASS", "FAIL"]];
