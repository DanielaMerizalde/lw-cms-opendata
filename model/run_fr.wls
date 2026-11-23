(* run_fr.wls -- build & validate the LW-electron model, write UFO.
   Usage: wolframscript -file run_fr.wls   (from the model/ directory)  *)
FR$Parallelize = False;
$FeynRulesPath = "/Users/danielamerizalde/Downloads/lee-wick/feynrules-patched";
modelDir = DirectoryName[$InputFileName];
If[modelDir === "", modelDir = Directory[]];
SetDirectory[$FeynRulesPath]; << FeynRules`;
FR$Parallelize = False;
SetDirectory[modelDir];
LoadModel[FileNameJoin[{$FeynRulesPath, "Models", "SM", "SM.fr"}], FileNameJoin[{modelDir, "LWElectron.fr"}]];

hdr[s_] := Print["\n==================== ", s, " ===================="];
fields[v_] := v[[1, All, 1]];
crea = Function[x, !FreeQ[x, _Symbol?(StringMatchQ[SymbolName[#], "crea*"] &)]];

hdr["SANITY: SM e e A vertex"];
vsm = FeynmanRules[LFermions, FlavorExpand -> True];
veeA = Select[vsm, Sort[fields[#]] === Sort[{e, ebar, A}] &];
vSMeeZ = Select[vsm, Sort[fields[#]] === Sort[{e, ebar, Z}] &];
Print["SM eeA: ", InputForm[veeA]];
Print["SM eeZ: ", InputForm[vSMeeZ]];
Print["SANITY eeA found: ", Length[veeA] == 1 && !crea[vsm]];

hdr["HERMITICITY"];
Print["CheckHermiticity[LLW] (model as implemented):"];
hLW = CheckHermiticity[LLW];
Print["  -> ", InputForm[hLW]];
Print["CheckHermiticity[LMixLiteral] (Eq.1 literal form X - X^dagger):"];
hLit = CheckHermiticity[LMixLiteral];
Print["  -> ", InputForm[hLit]];
Print["CheckHermiticity[LSM + LLW]:"];
hAll = CheckHermiticity[LSM + LLW];
Print["  -> ", InputForm[hAll]];

hdr["KINETIC / MASS"];
Print["CheckKineticTermNormalisation[LLWKin]: ", CheckKineticTermNormalisation[LLWKin]];
Print["CheckMassSpectrum[LLWKin]: ", CheckMassSpectrum[LLWKin]];

hdr["NEW VERTICES"];
vLW = FeynmanRules[LLWGauge + LMix, FlavorExpand -> True];
Print["crea-type corruption in LW vertices: ", crea[vLW]];
Do[Print[InputForm[v]], {v, vLW}];
Print["elw elw A : ", InputForm[Select[vLW, Sort[fields[#]] === Sort[{elw, elwbar, A}] &]]];
Print["elw elw Z : ", InputForm[Select[vLW, Sort[fields[#]] === Sort[{elw, elwbar, Z}] &]]];
Print["elw e Z   : ", InputForm[Select[vLW, MemberQ[fields[#], Z] && (MemberQ[fields[#], e] || MemberQ[fields[#], ebar]) &]]];

hdr["EW INPUTS (SM.fr default scheme aEWM1, Gf, MZ)"];
Print["aEWM1=", NumericalValue[aEWM1], " Gf=", NumericalValue[Gf], " MZ=", NumericalValue[MZ]];
Print["MW=", NumericalValue[MW], " sw2=", NumericalValue[sw2], " cw=", NumericalValue[cw], " ee=", NumericalValue[ee],
      " g/cW=ee/(sw cw)=", NumericalValue[ee/(sw cw)], " gw=", NumericalValue[gw]];

hdr["WIDTHS (FeynRules ComputeWidths)"];
dec = ComputeWidths[vLW];
Print["Decay channels: ", InputForm[dec[[All, 1]]]];
totW = TotWidth[elw];
Print["TotWidth[elw] symbolic: ", InputForm[totW]];
Print["BR(elw -> e Z): ", InputForm[Simplify[BranchingRatio[{elw, e, Z}]]]];
expand = {gMixLW -> (gZeLLW - gZeRLW) MeLW/MLW, gZeLLW -> ee/(sw cw) (-1/2 + sw^2), gZeRLW -> ee/(sw cw) sw^2};
totWexp = totW //. expand;
hbarc = 1.97327*^-13;
res = Flatten[Table[{me, m, NumericalValue[totWexp /. {MLW -> m, MeLW -> me}]}, {me, {5.0*^-4, 5.11*^-4}}, {m, {200., 300., 400., 500.}}], 1];
Do[Print["MeLW=", r[[1]], "  M=", r[[2]], "  Gamma_FR=", ScientificForm[r[[3]], 8], " GeV   ctau0=", ScientificForm[hbarc/r[[3]], 8], " mm"], {r, res}];
Export[FileNameJoin[{modelDir, "logs", "widths_fr.csv"}], Prepend[res, {"MeLW_GeV", "M_GeV", "Gamma_FR_GeV"}], "CSV"];
Print["Analytic check: Gamma - c^2 M^3/(32 Pi MZ^2)(1-x)^2(1+2x) (Me->0) = ",
  Simplify[(totWexp /. Me -> 0) - (ee/(sw cw) MeLW/(2 MLW))^2 MLW^3/(32 Pi MZ^2) (1 - MZ^2/MLW^2)^2 (1 + 2 MZ^2/MLW^2), MLW > MZ > 0]];

hdr["WRITE UFO"];
If[DirectoryQ[FileNameJoin[{modelDir, "LWElectron_UFO"}]], DeleteDirectory[FileNameJoin[{modelDir, "LWElectron_UFO"}], DeleteContents -> True]];
WriteUFO[LSM + LLW, Output -> FileNameJoin[{modelDir, "LWElectron_UFO"}], AddDecays -> False];
Print["UFO written."];
