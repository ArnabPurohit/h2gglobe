#!/bin/csh

root -b -l -q 'correlations.C("pho1_idmvaVsEta")'
root -b -l -q 'correlations.C("pho2_idmvaVsEta")'
root -b -l -q 'correlations.C("pho1_idmvaVsPtOverM_EB")'
root -b -l -q 'correlations.C("pho1_idmvaVsPtOverM_EE")'
root -b -l -q 'correlations.C("pho2_idmvaVsPtOverM_EB")'
root -b -l -q 'correlations.C("pho2_idmvaVsPtOverM_EE")'
root -b -l -q 'correlations.C("pho1_sigmaEOverEVsEta")'
root -b -l -q 'correlations.C("pho2_sigmaEOverEVsEta")'
root -b -l -q 'correlations.C("pho1_sigmaEOverEVsIdmva_EB")'
root -b -l -q 'correlations.C("pho1_sigmaEOverEVsIdmva_EE")'
root -b -l -q 'correlations.C("pho2_sigmaEOverEVsIdmva_EB")'
root -b -l -q 'correlations.C("pho2_sigmaEOverEVsIdmva_EE")'
root -b -l -q 'correlations.C("pho1_sigmaEOverEVsPtOverM_EB")'
root -b -l -q 'correlations.C("pho1_sigmaEOverEVsPtOverM_EE")'
root -b -l -q 'correlations.C("pho2_sigmaEOverEVsPtOverM_EB")'
root -b -l -q 'correlations.C("pho2_sigmaEOverEVsPtOverM_EE")'
root -b -l -q 'correlations.C("idmvaVsRho_EB")'
root -b -l -q 'correlations.C("idmvaVsRho_EE")'
root -b -l -q 'correlations.C("pfphotoniso03VsRho_EB")'
root -b -l -q 'correlations.C("pfphotoniso03VsRho_EE")'
