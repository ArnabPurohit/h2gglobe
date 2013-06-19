#!/bin/env python

import sys
import numpy
from math import sqrt, log
import json
json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')

from optparse import OptionParser, make_option
from  pprint import pprint

objs = []

# -----------------------------------------------------------------------------------------------------------
def loadSettings(cfgs,dest):
    for cfg in cfgs.split(","):
        cf = open(cfg)
        settings = json.load(cf)
        for k,v in settings.iteritems():
            attr  = getattr(dest,k,None)
            if attr and type(attr) == list:
                attr.extend(v)
                v = attr
            setattr(dest,k,v)
        cf.close()

def getBoundaries(ncat,optimizer, summary):
    boundaries = numpy.array([0. for i in range(ncat+1) ])
    selections = numpy.array([0. for i in range(optimizer.nOrthoCuts()) ])
    if len(selections) > 0: 
        z = optimizer.getBoundaries(ncat,boundaries,selections)
    else:
        z = optimizer.getBoundaries(ncat,boundaries,numpy.array([0.]))
    print z, boundaries, selections
    if not ncat in summary or summary[ncat]["fom"] < z: 
        summary[ncat] =  { "fom" : z, "boundaries" : list(boundaries), "ncat": ncat }
        if len(selections) > 0: 
            summary[ncat]["selections"]=list(selections)
        

# -----------------------------------------------------------------------------------------------------------
def optmizeCats(optimizer,ws,rng,args,readBack=False,reduce=False,refit=False):
    
    summary = {}
    if readBack:
        try:
            sin = open("cat_opt.json","r")
            summary = json.loads(sin.read())
            sin.close()
        except:
            summary = {}
        
    for iter in rng:
        optimizer.optimizeNCat(iter,*args)
        getBoundaries(iter, optimizer, summary )

    for ncat,val in summary.iteritems():
        printBoundaries(val["boundaries"],val["fom"],val.get("selections",None))

    if reduce:
        maxncat = 0
        for ncat,val in summary.iteritems():
            boundaries = numpy.array([float(b) for b in val["boundaries"]])
            ## setSelections(optimizer,summary)
            optimizer.reduce(int(ncat)+1, boundaries, numpy.array([0. for i in range(len(boundaries))]) )
            maxncat = max(int(ncat),maxncat)
        rng = range(1,maxncat+1)
        summary = {}

    if refit:
        for ncat,val in summary.iteritems():
            boundaries = numpy.array([float(b) for b in val["boundaries"]])
            ncat=int(ncat)
            ## setSelections(optimizer,summary)
            eargs = [a for a in args]
            eargs.append(boundaries)
            rng.append(ncat)
            optimizer.optimizeNCat(ncat,*eargs)
        rng = sorted( set(rng) )
        summary = {}
        
    for iter in rng:
        getBoundaries(iter, optimizer, summary )
        
    for ncat,val in summary.iteritems():
        printBoundaries(val["boundaries"],val["fom"],val.get("selections",None))

    print summary
        
    sout = open("cat_opt.json","w+")
    sout.write( json.dumps(summary,sort_keys=True, indent=4) )

    return summary

# -----------------------------------------------------------------------------------------------------------
def printBoundaries(boundaries, maxval,selections):
    
    print "---------------------------------------------"
    print "ncat: ", len(boundaries)-1
    print "max: %1.5f" % ( maxval )
    print "boundaries: ",
    for b in boundaries:
        print "%1.3g" % b,
    print
    if selections:
        print "selections: ",
        for s in selections:
            print "%1.3g" % s,
        print
    print 


alltrees = []

# -----------------------------------------------------------------------------------------------------------
def mergeTrees(tfile,sel,outname,trees,aliases):
    tlist = ROOT.TList()
    for name,selection in trees:
        print "Reading tree %s" % name        
        tree=tfile.Get(name)
        if sel != "":
            selection = str(TCut(selection)*TCut(sel))
        if selection != "":
            clone = tree.CopyTree(selection)
            tree = clone
        tlist.Add(tree)
    out=ROOT.TTree.MergeTrees(tlist)
    out.SetName(outname)
    for name, definition in aliases:
        out.SetAlias( name,definition )
    return out

objs = []

# -----------------------------------------------------------------------------------------------------------
def defineVariables(variables):

    arglist = ROOT.RooArgList()
    aliases = []
    
    for var in variables:
        name = str(var[0])
        if ":=" in name:
            name, definition = [ tok.lstrip(" ").rstrip(" ") for tok in name.split(":=") if tok != "" ]
            print name, definition
            aliases.append( (name,definition) )
        xmin,xmax,nbins = var[1]
        default = xmin
        if len(var) == 3:
            default = float(var[2])
        if type(nbins) == float:
            nbins = int( (xmax-xmin)/nbins )
        var = ROOT.RooRealVar(name,name,default,xmin,xmax)
        var.setBins(nbins)
        objs.append(var)
        arglist.add( var )

    return arglist,aliases
        
# -----------------------------------------------------------------------------------------------------------
def modelBuilders(trees, type, obs, varlist, sellist, weight):
    builders=[]
    for tree in trees:
        modelName = "%sModel" % tree.GetName()
        modelBuilder = ROOT.SecondOrderModelBuilder(type, modelName, obs, tree, varlist, sellist, weight)
        ### modelBuilder = ROOT.SecondOrderModelBuilder(type, modelName, obs, tree, varlist, weight)
        builders.append(modelBuilder)
    return builders

# -----------------------------------------------------------------------------------------------------------
def optimizeMultiDim(options,args):


    signals = options.signals
    backgrounds = options.backgrounds

    variables = options.variables
    observable = options.observable
    selection = options.selection
    cutoff = options.cutoff

    selectioncuts = options.selectioncuts
    
    ndim = len(variables)
    ws = None

    cutoffs = numpy.array([cutoff]*ndim)
    
    obs,obsalias = defineVariables( [observable] )
    obs = obs[0]
    mu = ROOT.RooRealVar("mu","mu",1.,0.,10.)
    
    varlist,aliases = defineVariables( variables )
    sellist,selaliases = defineVariables( selectioncuts )
    
    print "Observables "
    obs.Print("")

    print "Variables"
    varlist.Print("V")

    print "Selection cuts"
    sellist.Print("V")

    aliases.extend(obsalias+selaliases)
    print "Aliases"
    print aliases
        
    if options.infile == "":
        options.infile = args[0]
    fin = ROOT.TFile.Open(options.infile)

    tmp = ROOT.TFile.Open(options.outfile,"recreate")
    tmp.cd()

    ### ##########################################################################################################
    ### Minimizer and optimizer
    ###
    minimizer = ROOT.TMinuitMinimizer("Minimize")
    minimizer.SetStrategy(2)
    ## minimizer.SetPrintLevel(999)
    ## minimizer = ROOT.Minuit2.Minuit2Minimizer()
    optimizer = ROOT.CategoryOptimizer( minimizer, ndim )
    for isel in range(sellist.getSize()):
        sel = sellist[isel]
        optimizer.addFloatingOrthoCut(sel.GetName(),sel.getVal(),(sel.getMax()-sel.getMin())/sel.getBins(),sel.getMin(),sel.getMax())
        ### optimizer.addFixedOrthoCut(sel.GetName(),sel.getVal())
    
    ### ##########################################################################################################
    ### Model builders
    ###
    sigTrees = [ mergeTrees(fin,selection,name,trees,aliases) for name,trees in signals.iteritems() ]
    bkgTrees = [ mergeTrees(fin,selection,name,trees,aliases) for name,trees in backgrounds.iteritems() ]

    for tree in sigTrees+bkgTrees:
        tree.Write()
        
    fin.Close()
    signals = modelBuilders( sigTrees, ROOT.AbsModel.sig, obs, varlist, sellist, "weight" )
    backgrounds = modelBuilders( bkgTrees, ROOT.AbsModel.bkg, obs, varlist, sellist, "weight" )

    if options.saveCompactTree:
        for model in signals+backgrounds:
            model.getTree().Write()
        
    normTF1s = []
    sumxTF1s = []
    sumx2TF1s = []
    for model in backgrounds:
        norm = model.getTF1N() 
        x    = model.getTF1X()
        x2   = model.getTF1X2() 
        norm.SetLineColor(ROOT.kRed)
        x.SetLineColor(ROOT.kRed)
        x2.SetLineColor(ROOT.kRed)
        normTF1s.append(norm)
        sumxTF1s.append(x)
        sumx2TF1s.append(x2)

    for model in signals:
        norm = model.getTF1N()
        x    = model.getTF1X()
        x2   = model.getTF1X2() 
        norm.SetLineColor(ROOT.kBlue)
        x.SetLineColor(ROOT.kBlue)
        x2.SetLineColor(ROOT.kBlue)
        normTF1s.append(norm)
        sumxTF1s.append(x)
        sumx2TF1s.append(x2)
    
        
    canv2 = ROOT.TCanvas("canv2","canv2")
    canv2.cd()
    normTF1s[0].Draw("")
    for tf1 in normTF1s[1:]:
        tf1.Draw("SAME")
    canv2.SaveAs("cat_opt_cdf.png")

    ### canv3 = ROOT.TCanvas("canv3","canv3")
    ### canv3.cd()
    ### hbkgMass.SetLineColor(ROOT.kRed)
    ### hbkgMass.Draw("hist")
    ### for hsigMass in hsigsMass:
    ###     hsigMass.SetLineColor(ROOT.kBlue)
    ###     hsigMass.Draw("hist SAME")
    ### canv3.SaveAs("cat_opt_mass.png")
    
    canv4 = ROOT.TCanvas("canv4","canv4")
    canv4.cd()
    sumxTF1s[0].Draw("hist")
    for tf1 in sumxTF1s[1:]:
        tf1.Draw("hist SAME")
    canv4.SaveAs("cat_opt_sum_mass.png")

    canv5 = ROOT.TCanvas("canv5","canv5")
    canv5.cd()
    sumx2TF1s[0].Draw("hist")
    for tf1 in sumx2TF1s[1:]:
        tf1.Draw("hist SAME")
    canv5.SaveAs("cat_opt_sum_mass2.png")

    objs.append( signals )
    objs.append( backgrounds )
    objs.append( normTF1s )
    objs.append( sumxTF1s )
    objs.append( sumx2TF1s )
    
    ### #########################################################################################################
    ### Figure of merit for optimization
    ###

    ### Simple counting
    ## fom       = ROOT.NaiveCutAndCountFomProvider()
    ## fom       = ROOT.PoissonCutAndCountFomProvider()

    ### ### Likelihood ratio using asymptotic approx.
    fom       = ROOT.SimpleShapeFomProvider()
    for sigModel in signals:
        sigModel.getModel().setMu(mu)
    fom.addPOI(mu)
    fom.minStrategy(2)
    ## fom.minimizer("Minuit2")
    ## fom.useRooSimultaneous()
    
    ### #########################################################################################################
    ### Run optimization
    ###
        
    for sigModel in signals:
        optimizer.addSignal( sigModel, True )
        ## optimizer.addSignal( sigModel )
    for bkgModel in backgrounds:
        optimizer.addBackground( bkgModel )
    optimizer.setFigureOfMerit( fom )
    optimizer.absoluteBoundaries()  ## Float absolut boundaries instead of telescopic ones
    for opt in options.settings:
        if type(opt) == str:
            getattr(optimizer,opt)()
        else:
            name, args = opt
            getattr(optimizer,opt)(*args)
    
    summary = optmizeCats( optimizer, ws, options.range, (cutoffs,options.dry,True,), options.cont, options.reduce, options.refit )
    
    ### #########################################################################################################
    ### Some plots
    ###
    
    grS = ROOT.TGraph()
    grS.SetName("zVsNcat")
    grS.SetTitle(";n_{cat};f.o.m [A.U.]")
    for ncat,val in summary.iteritems():
        if( val["fom"] < 0. ) :
            grS.SetPoint( grS.GetN(), float(ncat), -val["fom"] )
    grS.Sort()
    mincat = grS.GetX()[0]
    maxcat = grS.GetX()[grS.GetN()-1]
    ncat = int(maxcat - mincat)

    for idim in range(ndim):
        var = varlist[idim]
        name = var.GetName()
        minX = var.getMin()
        maxX = var.getMax()
        nbinsX = var.getBinning().numBoundaries()-1
        hbound = ROOT.TH2F("hbound_%s" % name,"hbound_%s" % name,nbinsX+3,minX-1.5*(maxX-minX)/nbinsX,maxX+1.5*(maxX-minX)/nbinsX,ncat+3,mincat-1.5,maxcat+1.5)
        for jcat,val in summary.iteritems():
            for ib in range(len(val["boundaries"])):
                if (ib % ndim) == idim:
                    bd = float(val["boundaries"][ib])
                    ## hbound.Fill(float(jcat),bd)
                    hbound.Fill(bd,float(jcat))
        cbound = ROOT.TCanvas( "cat_opt_%s" % hbound.GetName(), "cat_opt_%s" % hbound.GetName() )
        cbound.cd()
        hbound.Draw("box")

        cbound_pj = ROOT.TCanvas( "cat_opt_%s_pj" % hbound.GetName(),  "cat_opt_%s_pj" %  hbound.GetName() )
        cbound_pj.cd()
        hbound_pj = hbound.Clone()
        ### hbound_pj = hbound.ProjectionY()
        ### hbound_pj.Draw()
        hbound_pj.Draw("box")
        hbound_pj.SetFillColor(ROOT.kBlack)
        hbound_pj.SetLineColor(ROOT.kBlack)
        objs.append(hbound)
        objs.append(hbound_pj)
        objs.append(cbound)
        objs.append(cbound_pj)
        maxy = 0.
        pdfs = []
        for sig in signals:
            pdf = sig.getPdf(idim)
            pdf.SetLineColor(ROOT.kBlue)
            pdfs.append(pdf)
            maxy = max(maxy,pdf.GetMaximum())
            objs.append(pdf)
        for bkg in backgrounds:
            pdf = bkg.getPdf(idim)
            pdf.SetLineColor(ROOT.kRed)
            pdfs.append(pdf)
            maxy = max(maxy,pdf.GetMaximum())
            objs.append(pdf)
            
        ### hbound_pj.Scale(maxy*hbound_pj.GetMaximum())
        ### hbound_pj.GetYaxis().SetRangeUser(0.,1.1*maxy)
        ### cbound_pj.RedrawAxis()
        ### cbound_pj.Update()
        for pdf in pdfs:
            pdf.Scale( ncat/maxy )
            pdf.Draw("l same")
        hbound_pj.GetYaxis().SetNdivisions(500+ncat+3)
        cbound_pj.SetGridy()
        hbound_pj.Draw("box same")
        
        for fmt in "png", "C":
            cbound.SaveAs("%s.%s" % (cbound.GetName(),fmt) )
            cbound_pj.SaveAs("%s.%s" % (cbound_pj.GetName(),fmt) )
            
            
    canv9 = ROOT.TCanvas("canv9","canv9")
    canv9.SetGridx()
    canv9.SetGridy()
    canv9.cd()
    grS.SetMarkerStyle(ROOT.kFullCircle)
    grS.Draw("AP")
    
    canv9.SaveAs("cat_opt_fom.png")
    canv9.SaveAs("cat_opt_fom.C")

    ## tmp.Close()
    return ws

# -----------------------------------------------------------------------------------------------------------
def main(options,args):
    
    ROOT.gSystem.SetIncludePath("-I$ROOTSYS/include -I$ROOFITSYS/include")
    ROOT.gSystem.Load("../../libLoopAll.so")

    ROOT.gStyle.SetOptStat(0)

    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)
    ROOT.RooMsgService.instance().setSilentMode(True)
    ws = optimizeMultiDim(options,args)
    
    return ws

    
if __name__ == "__main__":

    parser = OptionParser(option_list=[
            make_option("-i", "--infile",
                        action="store", type="string", dest="infile",
                        default="",
                        help="input file",
                        ),
            make_option("-o", "--outfile",
                        action="store", type="string", dest="outfile",
                        default=sys.argv[0].replace(".py",".root"),
                        help="output file",
                        ),
            make_option("-l", "--load",
                        action="store", dest="settings", type="string",
                        default="",
                        help="json file containing settings"
                        ),
            make_option("-c", "--continue",
                        action="store_true", dest="cont",
                        default=False,
                        help="read-back the previous optimization step",
                        ),
            make_option("-r", "--reduce",
                        action="store_true", dest="reduce",
                        default=False,
                        help="collapse higher category orders to lower ones",
                        ),
            make_option("-s", "--settings",
                        action="store", dest="settings",
                        default=[],
                        help="append string to optimizer setting",
                        ),
            make_option("-n", "--ncat",
                        action="append", dest="range", type="int",
                        default=[],
                        help="collapse higher category orders to lower ones",
                        ),
            make_option("-d", "--dryrun",
                        action="store_true", dest="dry",
                        default=False,
                        help="do not run the optimization only find equidistant boundaries"
                        "\n  useful in conjunction with reduce and refit",
                        ),
            make_option("-R", "--refit",
                        action="store_true", dest="refit",
                        default=False,
                        help="refit the best point after reduction"
                        ),
            make_option("-S", "--splitreduce",
                        action="store_true", dest="splitreduce",
                        default=False,
                        help="search minimum by splitting and merging categories (equivalent to -r -R -d)"
                        ),
            make_option("--savecmpact",
                        action="store_true", dest="saveCompactTree",
                        default=False,
                        help="save the 2nd order models as TTrees"
                        ),
            make_option("-x", "--show-plots",
                        action="store_true", dest="showplots",
                        default=sys.flags.interactive,
                        help="json file containing settings"
                        ),
            ])

    (options, args) = parser.parse_args()
    loadSettings(options.settings, options)

    if not options.showplots:
        sys.argv.append("-b")

    if options.splitreduce:
        options.dry = True
        options.refit = True
        options.reduce = True
        
    pprint(options)

    import ROOT
    print ROOT.gROOT.IsBatch()
    

    ws=main(options,args)
