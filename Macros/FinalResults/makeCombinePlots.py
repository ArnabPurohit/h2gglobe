#!/usr/bin/env python

import os
import sys
import shlex

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--datfile",dest="datfile",help="Read from datfile")
parser.add_option("-f","--file",dest="files",default=[],action="append",help="Add a file")
parser.add_option("-o","--outname",dest="outname",help="Name of output pdf/png/C")
parser.add_option("-c","--color",dest="colors",default=[],action="append",help="Set color")
parser.add_option("-s","--style",dest="styles",default=[],action="append",help="Set style")
parser.add_option("-w","--width",dest="widths",default=[],action="append",help="Set width")
parser.add_option("-n","--name",dest="names",default=[],action="append",help="Set name")
parser.add_option("-g","--gname",dest="groupnames",default=[],action="append",help="Set (group) name -for channel compat")
parser.add_option("","--groups",dest="groups",default=1,type="int",help="Set Number of groups")
parser.add_option("-t","--text",dest="text",type="string",default="",help="Add Text")
parser.add_option("","--MHtext",dest="MHtext",type="string",default="",help="Add more text (eg mh=XXX for chan-compat plots etc). Modify NDC position by ruing  X:Y:text")

parser.add_option("","--xlab",dest="xlab",type="string",default="",help="Label for x-axis")
parser.add_option("","--xvar",dest="xvar",type="string",default=[],action="append",help="Branch in TTree to pick up as 'x'")
parser.add_option("-e","--expected",dest="expected",default=False,action="store_true",help="Expected only")
parser.add_option("-m","--method",dest="method",type="string",help="Method to run")
parser.add_option("-l","--legend",dest="legend",type="string",help="Legend position - x1,y1,x2,y2")
parser.add_option("-x","--xaxis",dest="xaxis",type="string",help="x-axis range - x1,x2")
parser.add_option("-y","--yaxis",dest="yaxis",type="string",help="y-axis range - y1,y2")
parser.add_option("","--xbinning",dest="xbinning",type="string",help="force x binning (b,l,h)")
parser.add_option("","--ybinning",dest="ybinning",type="string",help="force y binning (b,l,h)")
parser.add_option("","--canv",dest="canv",type="string",default="700,700",help="Canvas size x,y")
parser.add_option("","--chcompLine",dest="chcompLine",type="int",help="For ChannelComp plot put line here splitting two year")
parser.add_option("","--chcompShift",dest="chcompShift",type="float",help="For ChannelComp Asimov - shift to this value")
parser.add_option("","--chcomp1sig",dest="chcomp1sig",default=False,action="store_true",help="For ChannelComp plot only 1 sigma errors")
parser.add_option("","--noComb",dest="noComb",default=False,action="store_true",help="Don't assume the first line is the combined one")
parser.add_option("","--smoothNLL",dest="smoothNLL",default=False,action="store_true",help="Smooth 1D likelihood scans")
parser.add_option("","--shiftNLL",dest="shiftNLL",type="float",help="Correct NLL to this value")
parser.add_option("","--correctNLL",dest="correctNLL",default=False,action="store_true",help="Correct NLL (occasionally required for failed jobs)")
parser.add_option("","--cleanNLL",dest="cleanNll",default=False,action="store_true",help="Try to remove pike from NLL curve")
parser.add_option("","--limit",dest="limit",default=False,action="store_true",help="Do limit plot")
parser.add_option("","--pval",dest="pval",default=False,action="store_true",help="Do p-value plot")
parser.add_option("","--maxlh",dest="maxlh",default=False,action="store_true",help="Do best fit mu plot")
parser.add_option("","--mh",dest="mh",default=False,action="store_true",help="Do NLL mass scan plot")
parser.add_option("","--mu",dest="mu",default=False,action="store_true",help="Do NLL mu scan plot")
parser.add_option("","--rv",dest="rv",default=False,action="store_true",help="Do NLL rv scan plot")
parser.add_option("","--rf",dest="rf",default=False,action="store_true",help="Do NLL rf scan plot")
parser.add_option("","--draw2dhist",dest="draw2dhist",default=False,action="store_true",help="Ue 2D hist drawing for the 2D NLL")
parser.add_option("","--mumh",dest="mumh",default=False,action="store_true",help="Do NLL mu vs mh scan plot")
parser.add_option("","--rvrf",dest="rvrf",default=False,action="store_true",help="Do NLL rv vs rf scan plot")
parser.add_option("","--mpdfchcomp",dest="mpdfchcomp",default=False,action="store_true",help="Do MultiPdf channel compatbility plot")
parser.add_option("","--mpdfmaxlh",dest="mpdfmaxlh",default=False,action="store_true",help="Do MultiPdf best fit mu as a function of MH plot")
parser.add_option("-v","--verbose",dest="verbose",default=False,action="store_true")
parser.add_option("-b","--batch",dest="batch",default=False,action="store_true")
(options,args)=parser.parse_args()

# Required for back compatbility:
if options.limit: options.method='limit'
if options.pval: options.method='pval'
if options.maxlh: options.method='maxlh'
if options.mh: options.method='mh'
if options.mu: options.method='mu'
if options.rv: options.method='rv'
if options.rf: options.method='rf'
if options.mumh: options.method='mumh'
if options.rvrf: options.method='rvrf'
if options.mpdfchcomp: options.method='mpdfchcomp'
if options.mpdfmaxlh: options.method='mpdfmaxlh'
if not options.outname: options.outname=options.method

allowed_methods=['pval','limit','maxlh','mh','mu','mumh','rv','rf','rvrf','mpdfchcomp','mpdfmaxlh']
if not options.datfile and options.method not in allowed_methods:
  print 'Invalid method. Must set one of: ', allowed_methods
  sys.exit()

import ROOT as r
outf = r.TFile('CombinePlotCanvases.root','RECREATE')

if options.batch: r.gROOT.SetBatch()
r.gStyle.SetOptStat(0)

# set defaults for colors etc.
if len(options.colors):
  for i in range(len(options.colors)): 
  	if "r.k" not in options.colors[i]: options.colors[i]=int(options.colors[i])
	else :
	  lcolst = options.colors[i].split(".")[1]
	  add = 0
	  if "+" in lcolst: 
	  	add=int(lcolst.split("+")[1])
		lcolst = lcolst.split("+")[0]
	  if "-" in lcolst: 
	  	add=int(lcolst.split("-")[1])
		lcolst = lcolst.split("-")[0]
	  lcol = int(getattr(r,lcolst))
	  options.colors[i]=lcol+add
while len(options.files)>len(options.colors): options.colors.append(1)
while len(options.files)>len(options.styles): options.styles.append(1)
while len(options.files)>len(options.widths): options.widths.append(1)
while len(options.files)>len(options.names): options.names.append('')
while len(options.files)>len(options.xvar): options.xvar.append("")
while len(options.files)>len(options.groupnames): options.groupnames.append("")

# mh text options
mhTextX = 0.67
mhTextY = 0.6
if ":" in options.MHtext: 
  mhtextoptions = options.MHtext.split(":")
  options.MHtext = mhtextoptions[2]
  mhTextX = float(mhtextoptions[0])
  mhTextY = float(mhtextoptions[1])

# make canvas and dummy hist
canv = r.TCanvas("c","c",int(options.canv.split(',')[0]),int(options.canv.split(',')[1]))
canv.SetGrid(True)

if not options.xaxis: dummyHist = r.TH1D("dummy","",1,110,150)
else: dummyHist =  r.TH1D("dummy","",1,float(options.xaxis.split(',')[0]),float(options.xaxis.split(',')[1]))
dummyHist.GetXaxis().SetTitle('m_{H} (GeV)')
dummyHist.SetTitleSize(.05,"X")
dummyHist.SetTitleOffset(0.75,"X")
dummyHist.SetTitleSize(.05,"Y")
dummyHist.SetTitleOffset(0.75,"Y")
# make text box
lat = r.TLatex()
lat.SetNDC()
lat.SetTextSize(0.03)
lat.SetTextFont(42)

if options.draw2dhist :
  r.gROOT.ProcessLine(".L scanLH2D.C")
  from ROOT import scanLH2D as r_scanLH2D


def cleanSpikes1D(rfix):

 # cindex is where deltaNLL = 0 (pre anything)
 MAXDER = 1.0
 for i,r in enumerate(rfix):
   if abs(r[1]) <0.001: cindex = i

 lhs = rfix[0:cindex]; lhs.reverse()
 rhs= rfix[cindex:-1]
 keeplhs = []
 keeprhs = []

 for i,lr in enumerate(lhs): 
   if i==0: 
   	prev = lr[1]
	idiff = 1
   if abs(lr[1]-prev) > MAXDER :
   	idiff+=1
   	continue 
   keeplhs.append(lr)
   prev = lr[1]
   idiff=1
 keeplhs.reverse()

 for i,rr in enumerate(rhs):
   if i==0: 
   	prev = rr[1]
	idiff = 1
   if abs(rr[1]-prev) > MAXDER : 
   	idiff+=1
   	continue 
   keeprhs.append(rr)
   prev = rr[1]
   idiff=1
 
 rfix = keeplhs+keeprhs
 
 rkeep = []
 #now try to remove small jagged spikes
 for i,r in enumerate(rfix):
   if i==0 or i==len(rfix)-1: 
   	rkeep.append(r)
   	continue
   tres = [rfix[i-1][1],r[1],rfix[i+1][1]]
   mean = float(sum(tres))/3.
   mdiff = abs(max(tres)-min(tres))
   if abs(tres[1] - mean) > 0.6*mdiff :continue
   rkeep.append(r)
 return rkeep

def Make2DHistFromTree(tree,x,y):
  print "Generating 2D hist from ", tree  
  mhist = (r_scanLH2D(tree,x,y)).Clone()
  print " ... Done"
  return mhist 
  


def pvalPlot(allVals):
  
  canv.Clear()
  canv.SetLeftMargin(0.1)
  if options.verbose: print 'Plotting pvalue...'
  canv.SetLogy(True)
  mg = r.TMultiGraph()
  if not options.legend: leg = r.TLegend(0.6,0.12,0.89,0.4)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  leg.SetFillColor(0)

  # make graphs from values
  for k, values in enumerate(allVals):
    graph = r.TGraph()
    for j in range(len(values)):
      graph.SetPoint(j,values[j][0],values[j][1])
      if options.verbose or values[j][0]==125: print '\t', j, values[j][0], values[j][1], r.RooStats.PValueToSignificance(values[j][1])
    
    graph.SetLineColor(int(options.colors[k]))
    graph.SetLineStyle(int(options.styles[k]))
    graph.SetLineWidth(int(options.widths[k]))
    if options.names[k]!="-1": leg.AddEntry(graph,options.names[k],'L')
    mg.Add(graph)
 
  # draw dummy hist and multigraph
  dummyHist.GetYaxis().SetTitle('Local p-value')
  dummyHist.GetYaxis().SetTitleOffset(0.95)
  mg.Draw("A")
  if not options.yaxis:
    dummyHist.SetMinimum(mg.GetYaxis().GetXmin())
    dummyHist.SetMaximum(mg.GetYaxis().GetXmax())
  else:
    dummyHist.SetMinimum(float(options.yaxis.split(',')[0]))
    dummyHist.SetMaximum(float(options.yaxis.split(',')[1]))
    
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  mg.Draw("L")
  dummyHist.Draw("AXIGSAME")

  # draw sigma lines
  sigmas=[1,2,3,4,5,6]
  lines=[]
  labels=[]
  for i,sig in enumerate(sigmas):
    y = r.RooStats.SignificanceToPValue(sig)
    if options.verbose: print sig, y
    if not options.xaxis:  lines.append(r.TLine(110,y,150,y))
    else : 
        axmin = float(options.xaxis.split(',')[0])
        axmax = float(options.xaxis.split(',')[1])
    	lines.append(r.TLine(axmin,y,axmax,y))

    lines[i].SetLineWidth(2)
    lines[i].SetLineStyle(2)
    lines[i].SetLineColor(r.kRed)
    labels.append(r.TLatex(110 + 2, y * 1.1, "%d #sigma" % (i+1)))
    labels[i].SetTextAlign(11);
    if not options.yaxis:
      if y<=mg.GetYaxis().GetXmax() and y>=mg.GetYaxis().GetXmin():
        lines[i].Draw('SAME')
        labels[i].Draw('SAME')
    else:
      if y<=float(options.yaxis.split(',')[1]) and y>=float(options.yaxis.split(',')[0]):
        lines[i].Draw('SAME')
        labels[i].Draw('SAME')

  # draw text
  lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
  lat.DrawLatex(0.67,0.94,options.text)
  
  if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)
  # draw legend
  leg.Draw()
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()

def maxlhPlot(allVals):

  canv.Clear()
  canv.SetLogy(False)
  if options.verbose: print 'Plotting maxlh...'
  mg = r.TMultiGraph()
  if not options.legend: leg = r.TLegend(0.6,0.8,0.89,0.89)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  leg.SetFillColor(0)
 
  # make graph from values
  for k, values in enumerate(allVals):
    graph = r.TGraphAsymmErrors()
    point_counter=0
    for j in range(len(values)):
      if (j%4==0):
        mh = values[j][0]
        fit = values[j][1]
        low = values[j+1][1]
        high = values[j+2][1]
        graph.SetPoint(point_counter,mh,fit)
        graph.SetPointError(point_counter,0,0,abs(fit-low),abs(high-fit))
        point_counter+=1
        if options.verbose: print mh, fit, low, high
    
    graph.SetMarkerStyle(21)
    graph.SetMarkerSize(0.5)
    graph.SetLineColor(1)
    graph.SetLineWidth(2)
    graph.SetFillColor(r.kGreen)
    leg.AddEntry(graph,'68% CL Band','F')
    mg.Add(graph)
  
  # draw dummy hist and multigraph
  dummyHist.GetYaxis().SetTitle('Best fit #sigma/#sigma_{SM}')
  mg.Draw("A")
  if not options.yaxis:
    dummyHist.SetMinimum(mg.GetYaxis().GetXmin())
    dummyHist.SetMaximum(mg.GetYaxis().GetXmax())
  else:
    dummyHist.SetMinimum(float(options.yaxis.split(',')[0]))
    dummyHist.SetMaximum(float(options.yaxis.split(',')[1]))
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  mg.Draw("3")
  mg.Draw("LPX")
  dummyHist.Draw("AXIGSAME")
  
  # draw line at y=1 
  if options.xaxis:
        axmin = float(options.xaxis.split(',')[0])
        axmax = float(options.xaxis.split(',')[1])
  else: 
  	axmin = 110
	axmax = 150
  l = r.TLine(axmin,1.,axmax,1.)
  l.SetLineColor(r.kBlue)
  l.SetLineStyle(r.kDashed)
  l.SetLineWidth(2)
  l.Draw()
  
  # draw line at y=0 
  l2 = r.TLine(axmin,0.,axmax,0.)
  l2.SetLineColor(r.kRed)
  l2.SetLineStyle(r.kDashed)
  l2.SetLineWidth(2)
  l2.Draw()
  
  # draw text
  lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
  lat.DrawLatex(0.67,0.94,options.text)
  
  if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)
  # draw legend
  leg.Draw()
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()

def limitPlot(allVals):

  # figure out many entries per mass point
  # so we now if expected or not
  for vals in allVals: list_of_masses = [x[0] for x in vals]
  ents_per_mass = list_of_masses.count(list_of_masses[0])
  
  canv.Clear()
  canv.SetLogy(False)
  if options.verbose: print 'Plotting limit...'
  mg = r.TMultiGraph()
  if not options.legend: leg = r.TLegend(0.6,0.7,0.89,0.89)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  leg.SetFillColor(0)

  # make graph from values
  for k, values in enumerate(allVals):
    graph = r.TGraphAsymmErrors()
    exp = r.TGraphAsymmErrors()
    oneSigma = r.TGraphAsymmErrors()
    twoSigma = r.TGraphAsymmErrors()
    point_counter=0
    for j in range(len(values)):
      if (j%ents_per_mass==0):
        mh = values[j][0]
        down95 = values[j][1]
        down68 = values[j+1][1]
        median = values[j+2][1]
        up68 = values[j+3][1]
        up95 = values[j+4][1]
        if not options.expected: 
          obs = values[j+5][1]
          graph.SetPoint(point_counter,mh,obs)
        exp.SetPoint(point_counter,mh,median)
        oneSigma.SetPoint(point_counter,mh,median)
        oneSigma.SetPointError(point_counter,0,0,abs(median-down68),abs(up68-median))
        twoSigma.SetPoint(point_counter,mh,median)
        twoSigma.SetPointError(point_counter,0,0,abs(median-down95),abs(up95-median))
        point_counter+=1
        if options.verbose: 
          print mh, median, down68, up68, down95, up95, 
          if not options.expected: print obs
          else: print ''
    
    graph.SetMarkerStyle(21)
    graph.SetMarkerSize(0.5)
    graph.SetLineColor(1)
    graph.SetLineWidth(2)
    exp.SetLineColor(1)
    exp.SetLineStyle(2)
    oneSigma.SetLineStyle(2)
    twoSigma.SetLineStyle(2)
    oneSigma.SetFillColor(r.kGreen)
    twoSigma.SetFillColor(r.kYellow)
    if len(allVals)>1:
      exp.SetLineColor(int(options.colors[k]))
      exp.SetLineStyle(2)
      exp.SetLineWidth(int(options.widths[k]))
      graph.SetMarkerColor(int(options.colors[k]))
      graph.SetLineColor(int(options.colors[k]))
      leg.AddEntry(graph,options.names[k],'L')
    else:
      exp.SetLineColor(1)
      exp.SetLineStyle(2)
      exp.SetLineWidth(2)
      if not options.expected: leg.AddEntry(graph,'Observed','L')
      #leg.AddEntry(exp,'Expected','L')
      leg.AddEntry(oneSigma,'Expected #pm 1#sigma','FL') 
      leg.AddEntry(twoSigma,'Expected #pm 2#sigma','FL') 
    
    if len(allVals)==1:
      mg.Add(twoSigma)
      mg.Add(oneSigma)
    mg.Add(exp)
    if not options.expected: mg.Add(graph)
  
  # draw dummy hist and multigraph
  dummyHist.GetYaxis().SetTitle("\sigma(H#rightarrow #gamma #gamma)_{95%%CL} / \sigma(H#rightarrow #gamma #gamma)_{SM}")
  mg.Draw("A")
  if not options.yaxis:
    dummyHist.SetMinimum(mg.GetYaxis().GetXmin())
    dummyHist.SetMaximum(mg.GetYaxis().GetXmax())
  else:
    dummyHist.SetMinimum(float(options.yaxis.split(',')[0]))
    dummyHist.SetMaximum(float(options.yaxis.split(',')[1]))
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  mg.Draw("3")
  mg.Draw("LPX")
  dummyHist.Draw("AXIGSAME")
 
  # draw line at y=1
  if options.xaxis:
        axmin = float(options.xaxis.split(',')[0])
        axmax = float(options.xaxis.split(',')[1])
  else: 
  	axmin = 110
	axmax = 150
  l = r.TLine(axmin,1.,axmax,1.)
  l.SetLineColor(r.kRed)
  l.SetLineWidth(2)
  l.Draw()

  # draw text
  lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
  lat.DrawLatex(0.67,0.94,options.text)
  
  if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)
  # draw legend
  leg.Draw()
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()

def runStandard():
  config = []
  for k, f in enumerate(options.files):
    tf = r.TFile(f)
    tree = tf.Get('limit')
    values=[]
    for i in range(tree.GetEntries()):
      tree.GetEntry(i)
      values.append([tree.mh, tree.limit])
    values.sort(key=lambda x: x[0])
    config.append(values)

  if options.method=='pval': pvalPlot(config)
  elif options.method=='limit': limitPlot(config)
  elif options.method=='maxlh': maxlhPlot(config)

def read1D(file,x,i,xtitle):
  tree = file.Get('limit')
  tree.Draw('2*deltaNLL:%s'%x,'','')
  gr = r.gROOT.FindObject('Graph').Clone('gr_%s_%d'%(x,i))
  gr.SetTitle("")
  gr.GetXaxis().SetTitle(xtitle)
  gr.GetYaxis().SetTitle("-2 #Delta LL")

  gr.Sort()
  last = None
  for i in range(gr.GetN(),0,-1):
    if gr.GetX()[i-1] == last:
      gr.RemovePoint(i-1)
    last = gr.GetX()[i-1]
  return gr

def findQuantile(pts,cl):

	#gr is a list of r,nll
	# start by walking along the variable and check if crosses a CL point
  
	if cl<=0:  
	 min=pts[0][0]
	 mincl=pts[0][1]
	 for pt in pts: 
		if pt[1]<mincl: 
			mincl=pt[1]
			min = pt[0]
     
	 return min,min

	crossbound = [ pt[1]<=cl for pt in pts ]
	rcrossbound = crossbound[:]
	rcrossbound.reverse()

	minci = 0
	maxci = len(crossbound)-1
	min = pts[0][0]
	max = pts[maxci][0]

	for c_i,c in enumerate(crossbound): 
		if c : 
			minci=c_i
			break
	
	for c_i,c in enumerate(rcrossbound): 
		if c : 
			maxci=len(rcrossbound)-c_i-1
			break

	if minci>0: 
		y0,x0 = pts[minci-1][0],pts[minci-1][1]
		y1,x1 = pts[minci][0],pts[minci][1]
		min = y0+((cl-x0)*y1 - (cl-x0)*y0)/(x1-x0)
		
	if maxci<len(crossbound)-1: 
		y0,x0 = pts[maxci][0],pts[maxci][1]
		y1,x1 = pts[maxci+1][0],pts[maxci+1][1]
		max = y0+((cl-x0)*y1 - (cl-x0)*y0)/(x1-x0)

	return min,max

def smoothNLL(gr,res):

  minVal = min([re[0] for re in res])
  maxVal = max([re[0] for re in res])
  sp = r.TSpline3('sp_%s'%gr.GetName(),gr,"",minVal,maxVal)
  for p in range(100):
    x = minVal+p*((maxVal-minVal)/100.)
    y = sp.Eval(x)
    gr.SetPoint(p,x,y)

def shiftNLL(gr,bf):
  
  shift = options.shiftNLL - bf
  for p in range(gr.GetN()):
    x = r.Double()
    y = r.Double()
    gr.GetPoint(p,x,y)
    gr.SetPoint(p,x+shift,y)

def plot1DNLL(returnErrors=False,xvar="", ext=""):

  if options.method=='mh':
    x = 'MH'
    xtitle = 'm_{H} (GeV)'
  elif options.method=='mu':
    x = 'r'
    xtitle = '#sigma / #sigma_{SM}'
    if options.xlab: 
      xtitle = options.xlab
    if xvar:
      x = xvar
  elif options.method=='rv':
    x = 'RV'
    xtitle = '#mu_{qqH+VH}'
  elif options.method=='rf':
    x = 'RF'
    xtitle = '#mu_{ggH+ttH}'
  else:
    sys.exit('Method not recognised for 1D scan %s'%options.method)

  if not options.legend: leg  = r.TLegend(0.35,0.65,0.65,0.79)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  leg.SetLineColor(0)
  leg.SetFillColor(0)

  clean_graphs=[]

  for k, f in enumerate(options.files):
    ntitle = options.names[k]
    tf = r.TFile(f)
    tree = tf.Get('limit')
    gr = r.TGraph()
    gr.SetName('gr_%d_%s'%(k,x))
    gr.SetLineColor((options.colors[k]))
    gr.SetLineStyle(int(options.styles[k]))
    gr.SetLineWidth(int(options.widths[k]))
    leg.AddEntry(gr,options.names[k],'L')
    
    res=[]
    for i in range(tree.GetEntries()):
      tree.GetEntry(i)
      xv = getattr(tree,x)
      # tree.quantileExpected==1: continue
      if tree.deltaNLL<0 and options.verbose: print "Warning, found -ve deltaNLL = ",  tree.deltaNLL, " at ", xv 
      if xv in [re[0] for re in res]: continue
      if 2*tree.deltaNLL < 100:
        res.append([xv,2*tree.deltaNLL])
    res.sort()

    # remove weird points again
    rfix = []
    for re in res: 
      if re[1]<100: rfix.append(re) 
    
    # clean out spikes :(
    if options.cleanNll: rfix = cleanSpikes1D(rfix)

    res = rfix[:] 

    minNLL = min([re[1] for re in res])

    for re in res: 
      if options.correctNLL and re[1]==0.: re[1]=-1
      re[1]-=minNLL
  
    p=0
    for re, nll in res: 
      if nll>=0.:
        gr.SetPoint(p,re,nll)
        if options.verbose: print '\t', p, re, nll
        p+=1

    m,m1 = findQuantile(res,0);
    #m = 1.
    #m1 = 1.
    l,h  = findQuantile(res,1);
    l2,h2  = findQuantile(res,4);

    if options.shiftNLL:
      shiftNLL(gr,m)
      shift = options.shiftNLL - m
      m += shift
      m1 += shift
      l += shift
      l2 += shift
      h += shift
      h2 += shift

    if options.smoothNLL:
      smoothNLL(gr,res)
      clean_graphs.append(gr)
    else:
      clean_graphs.append(gr)

    xmin = m
    eplus = h-m
    eminus = m-l
    eplus2 = h2-m
    eminus2 = m-l2

    print "%15s : %4.3f +%4.3g -%4.3g" % ( ntitle+" "+ext, xmin, eplus , eminus )
    #print "%s : %1.4f +%1.3g -%1.3g (2sig) +%1.3g -%1.3g" % ( options.names[k], xmin, eplus , eminus, eplus2, eminus2 )

    if returnErrors:
      return [xmin,eplus,eminus,eplus2,eminus2]
    
    if k==0:
      fit = xmin
      err = (abs(eplus)+abs(eminus))/2.
      eplus0 = eplus
      eminus0 = eminus

      axmin,axmax = findQuantile(res,6)
      if options.xaxis:
        axmin = float(options.xaxis.split(',')[0])
        axmax = float(options.xaxis.split(',')[1])
      lines = [ r.TLine(axmin, 0, axmax, 0),
                r.TLine(axmin, 1, axmax, 1), r.TLine(xmin-eminus,  0, xmin-eminus,  1), r.TLine(xmin+eplus,  0, xmin+eplus,  1), 
                r.TLine(axmin, 4, axmax, 4), r.TLine(xmin-eminus2, 0, xmin-eminus2, 4), r.TLine(xmin+eplus2, 0, xmin+eplus2, 4) ]
    
  dH = r.TH1D("dH","",1,axmin,axmax)
  dH.GetXaxis().SetTitle(xtitle)
  dH.SetTitleSize(.04,"X")
  dH.SetTitleOffset(0.95,"X")
  dH.SetTitleSize(.04,"Y")
  dH.SetTitleOffset(0.85,"Y")
  if options.method=='mh': dH.GetXaxis().SetNdivisions(505)
  dH.GetYaxis().SetTitle('-2 #Delta LL')
  if not options.yaxis: dH.GetYaxis().SetRangeUser(0.,6)
  else: dH.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))
  dH.SetLineColor(0)
  dH.SetStats(0)
  dH.Draw("AXIS")
    
  for gr in clean_graphs:
    gr.GetXaxis().SetRangeUser(axmin,axmax)
    gr.GetXaxis().SetNdivisions(505)
    if not options.yaxis: gr.GetYaxis().SetRangeUser(0.,6)
    else: gr.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))
    #gr.SetMarkerSize(2)
    #gr.SetMarkerStyle(r.kOpenCircle)
    gr.Draw("L")

  # draw legend
  if len(options.files)>1:
    leg.Draw('same')
        
  # draw intersection lines
  for l in lines:
    l.SetLineWidth(2)
    l.SetLineColor(r.kRed)
    l.Draw('same')
  
  # draw text
  lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
  lat.DrawLatex(0.67,0.94,options.text)
  if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)

  # draw fit value
  lat2 = r.TLatex()
  lat2.SetNDC()
  lat2.SetTextSize(0.04)
  lat2.SetTextAlign(22)
  if options.method=='mh': lat2.DrawLatex(0.5,0.85,"m_{H} = %6.3f #pm %4.3f"%(fit,err))
  elif options.method=='mu': lat2.DrawLatex(0.5,0.85,"#sigma/#sigma_{SM} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))
  elif options.method=='rv': lat2.DrawLatex(0.5,0.85,"#mu_{qqH+VH} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))
  elif options.method=='rf': lat2.DrawLatex(0.5,0.85,"#mu_{ggH+ttH} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))

  canv.Update()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()


def OBSOLETEplot1DNLLOld(returnErrors=False):
 
  if options.method=='mh':
    x = 'MH'
    xtitle = 'm_{H} (GeV)'
  elif options.method=='mu':
    x = 'r'
    xtitle = '#sigma / #sigma_{SM}'
  elif options.method=='rv':
    x = 'RV'
    xtitle = '#mu_{qqH+VH}'
  elif options.method=='rf':
    x = 'RF'
    xtitle = '#mu_{ggH+ttH}'
  else:
    sys.exit('Method not recognised for 1D scan %s'%options.method)

  canv = r.TCanvas(x,x,500,500)
  if not options.legend: leg  = r.TLegend(0.35,0.65,0.65,0.79)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  leg.SetLineColor(0)
  leg.SetFillColor(0)

  mg = r.TMultiGraph()
  objs = []
  graphs = []
  clean_graphs = []
  for k, f in enumerate(options.files):
    tf = r.TFile(f)
    
    graph = read1D(tf,x,k,xtitle)
    graph.SetLineColor((options.colors[k]))
    graph.SetLineStyle(int(options.styles[k]))
    graph.SetLineWidth(int(options.widths[k]))
    clean_graph = graph.Clone()
    clean_graphs.append(clean_graph)
    leg.AddEntry(clean_graph,options.names[k],'L')

    # convert graph into function
    sp = r.GraphToTF1('mygraph%d'%k,graph)
    func = r.TF1("myfunc%d" %k,sp,graph.GetX()[0],graph.GetX()[graph.GetN()-1],1,"GraphToTF1")
    #func.SetParameter(0,0.)
    func.SetLineColor(0)
    func.SetLineStyle(0)
    graphs.append(graph)
    objs.append(sp)
    objs.append(func)
    objs.append(graph)
  
    xmin = func.GetMinimumX()
    eminus = xmin - func.GetX(1.,func.GetXmin(),xmin)
    eplus  = func.GetX(1.,xmin,func.GetXmax()) - xmin
    eminus2 = xmin - func.GetX(4.,func.GetXmin(),xmin)
    eplus2  = func.GetX(4.,xmin,func.GetXmax()) - xmin
    print "%s : %1.4f +%1.3g -%1.3g (2sig) +%1.3g -%1.3g" % ( graph.GetName(), xmin, eplus , eminus, eplus2, eminus2 )

    if returnErrors:
      return [xmin,eplus,eminus,eplus2,eminus2]

    # for the first passed file only get the intersection lines
    if k==0:
      rng = 6
      axmin = 999.
      axmax = -999.
      fit = xmin
      err = (abs(eplus)+abs(eminus))/2.
      eminusR = xmin - func.GetX(rng,func.GetXmin(),xmin)
      eplusR  = func.GetX(rng,xmin,func.GetXmax()) - xmin
      axmin = min(axmin,xmin - eminusR)
      axmax = max(axmax,xmin + eplusR)
      lines = [ r.TLine(axmin, 0, axmax, 0),
                r.TLine(axmin, 1, axmax, 1), r.TLine(xmin-eminus,  0, xmin-eminus,  1), r.TLine(xmin+eplus,  0, xmin+eplus,  1), 
                r.TLine(axmin, 4, axmax, 4), r.TLine(xmin-eminus2, 0, xmin-eminus2, 4), r.TLine(xmin+eplus2, 0, xmin+eplus2, 4) ]
    
  dH = r.TH1D("dH","",1,axmin,axmax)
  dH.GetXaxis().SetTitle(xtitle)
  dH.SetTitleSize(.04,"X")
  dH.SetTitleOffset(0.95,"X")
  dH.SetTitleSize(.04,"Y")
  dH.SetTitleOffset(0.85,"Y")
  if options.method=='mh': dH.GetXaxis().SetNdivisions(505)
  dH.GetYaxis().SetTitle('-2 #Delta LL')
  if not options.yaxis: dH.GetYaxis().SetRangeUser(0.,rng)
  else: dH.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))
  dH.SetLineColor(0)
  dH.SetStats(0)
  dH.Draw("AXIS")
    
  for gr in clean_graphs:
    gr.GetXaxis().SetRangeUser(axmin,axmax)
    gr.GetXaxis().SetNdivisions(505)
    if not options.yaxis: gr.GetYaxis().SetRangeUser(0.,rng)
    else: gr.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))
    gr.Draw("L")

  # draw legend
  if len(options.files)>1:
    leg.Draw('same')
        
  # draw intersection lines
  for l in lines:
    l.SetLineWidth(2)
    l.SetLineColor(r.kRed)
    l.Draw('same')
  
  # draw text
  lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
  lat.DrawLatex(0.67,0.94,options.text)
  if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)

  # draw fit value
  lat2 = r.TLatex()
  lat2.SetNDC()
  lat2.SetTextSize(0.04)
  lat2.SetTextAlign(22)
  if options.method=='mh': lat2.DrawLatex(0.5,0.85,"m_{H} = %6.2f #pm %4.2f"%(fit,err))
  elif options.method=='mu': lat2.DrawLatex(0.5,0.85,"#sigma/#sigma_{SM} = %4.2f"%(fit,eplus,eminus))
  elif options.method=='rv': lat2.DrawLatex(0.5,0.85,"#mu_{qqH+VH} = %4.2f"%(fit,eplus,eminus))
  elif options.method=='rf': lat2.DrawLatex(0.5,0.85,"#mu_{ggH+ttH} = %4.2f"%(fit,eplus,eminus))

  canv.Update()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()

def plot2DNLL(xvar="RF",yvar="RV",xtitle="#mu_{ggH+ttH}",ytitle="#mu_{qqH+VH}"):
  
  #if len(options.files)>1:  sys.exit('Just one file for 2D scans please')
  canv = r.TCanvas("%s_%s"%(xvar,yvar),"%s_%s"%(xvar,yvar),750,750)
  BFgrs		= []
  CONT1grs	= []
  CONT2grs 	= []
  COLgrs	= []
  
  if not options.legend: leg = r.TLegend(0.7,0.7,0.88,0.88)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  leg.SetFillColor(0)

  mems = []
  for fi,file in enumerate(options.files):
    tf = r.TFile(file)
    tree = tf.Get('limit')
    xmin = tree.GetMinimum(xvar)
    xmax = tree.GetMaximum(xvar)
    ymin = tree.GetMinimum(yvar)
    ymax = tree.GetMaximum(yvar)

    mems.append(tf)

    if options.draw2dhist: 
      th2 = Make2DHistFromTree(tree,xvar,yvar)
      if options.xaxis :
	xmin = float(options.xaxis.split(',')[0])
	xmax = float(options.xaxis.split(',')[1])
      	th2.GetXaxis.SetRangeUser(xmin,xmax)
      if options.yaxis :
	ymin = float(options.yaxis.split(',')[0])
	ymax = float(options.yaxis.split(',')[1])
      	th2.GetYaxis.SetRangeUser(ymin,ymax)

    else:

      tree.Draw("%s>>h%d%s(10000,%1.4f,%1.4f)"%(xvar,fi,xvar,xmin,xmax),"deltaNLL>0.","goff")
      tempX = r.gROOT.FindObject('h%d%s'%(fi,xvar))
      tree.Draw("%s>>h%d%s(10000,%1.4f,%1.4f)"%(yvar,fi,yvar,ymin,ymax),"deltaNLL>0.","goff")
      tempY = r.gROOT.FindObject('h%d%s'%(fi,yvar))
    
      # x binning
      if options.xbinning: 
	xbins = int(options.xbinning.split(',')[0])
	xmin = float(options.xbinning.split(',')[1])
	xmax = float(options.xbinning.split(',')[2])
      else:
	xbins=0
	xmin = tree.GetMinimum(xvar)
	xmax = tree.GetMaximum(xvar)
	if options.xaxis:
	  xmin = float(options.xaxis.split(',')[0])
	  xmax = float(options.xaxis.split(',')[1])
	tree.Draw("%s>>h%d%s(10000,%1.4f,%1.4f)"%(xvar,fi,xvar,xmin,xmax),"deltaNLL>0.","goff")
	tempX = r.gROOT.FindObject('h%d%s'%(fi,xvar))
	for bin in range(1,tempX.GetNbinsX()+1):
	  if tempX.GetBinContent(bin)!=0: xbins+=1
    
      # y binning
      if options.ybinning: 
	ybins = int(options.ybinning.split(',')[0])
	ymin = float(options.ybinning.split(',')[1])
	ymax = float(options.ybinning.split(',')[2])
      else:
	ybins=0
	ymin = tree.GetMinimum(yvar)
	ymax = tree.GetMaximum(yvar)
	if options.yaxis:
	  ymin = float(options.yaxis.split(',')[0])
	  ymax = float(options.yaxis.split(',')[1])
	tree.Draw("%s>>h%d%s(10000,%1.4f,%1.4f)"%(yvar,fi,yvar,ymin,ymax),"deltaNLL>0.","goff")
	tempY = r.gROOT.FindObject('h%d%s'%(fi,yvar))
	for bin in range(1,tempY.GetNbinsX()+1):
	  if tempY.GetBinContent(bin)!=0: ybins+=1

      tree.Draw("2.*deltaNLL:%s:%s>>h%d%s%s(%d,%1.4f,%1.4f,%d,%1.4f,%1.4f)"%(yvar,xvar,fi,yvar,xvar,xbins,xmin,xmax,ybins,ymin,ymax),"deltaNLL>0.","prof")
      th2 = r.gROOT.FindObject('h%d%s%s'%(fi,yvar,xvar))

    gBF = r.TGraph()
    printedOK = False
    for ev in range(tree.GetEntries()):
      tree.GetEntry(ev)
      if tree.deltaNLL==0:
        if not printedOK : 
          print "Best Fit (%s) : "%(options.names[fi]),xvar,"=%.4f"%getattr(tree,xvar),", ",yvar,"=%.4f"%getattr(tree,yvar)
          printedOK=True
        gBF.SetPoint(0,getattr(tree,xvar),getattr(tree,yvar))
      if tree.deltaNLL<0: continue


    th2.SetTitle("")
    th2.SetMinimum(-0.0001)
    th2.SetMaximum(10.)
    th2.GetXaxis().SetTitle(xtitle)
    th2.GetYaxis().SetTitle(ytitle)
    th2.GetYaxis().SetTitleSize(0.04)
    th2.GetXaxis().SetTitleSize(0.04)
    th2.GetYaxis().SetTitleOffset(1.2)
    if options.xaxis: th2.GetXaxis().SetRangeUser(float(options.xaxis.split(',')[0]),float(options.xaxis.split(',')[1]))
    if options.yaxis: th2.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))

    cont_1sig = th2.Clone('cont_1_sig')
    cont_1sig.SetContour(2)
    cont_1sig.SetContourLevel(1,2.3)
    cont_1sig.SetLineColor((options.colors[fi]))
    cont_1sig.SetLineWidth(3)
    cont_1sig.SetLineStyle(1)
    cont_2sig = th2.Clone('cont_2_sig')
    cont_2sig.SetContour(2)
    cont_2sig.SetContourLevel(1,6.18)
    cont_2sig.SetLineColor((options.colors[fi]))
    cont_2sig.SetLineWidth(3)
    cont_2sig.SetLineStyle(2)

    gBF.SetMarkerStyle(34)
    gBF.SetMarkerSize(2.0)
    gBF.SetMarkerColor((options.colors[fi]))
    gBF.SetLineColor((options.colors[fi]))

    COLgrs.append(th2.Clone())
    BFgrs.append(gBF.Clone())
    CONT1grs.append(cont_1sig.Clone())
    CONT2grs.append(cont_2sig.Clone())

    #mems.append(tree)
    #mems.append(tempY)
    #mems.append(tempX)

    r.gStyle.SetOptStat(0)

    if len(options.files)==1 :
    	leg.AddEntry(gBF,"Best Fit","P"),
    	leg.AddEntry(cont_1sig,"1#sigma","L")
    	leg.AddEntry(cont_2sig,"2#sigma","L")
    else :
    	leg.AddEntry(BFgrs[-1],options.names[fi],"P")
   
  # Now Draw them 
  print COLgrs
  if len(options.files)==1:
    for fi in range(len(options.files)):
    	th2.Draw("colz")
  	gBF.Draw("Psame")
    	cont_1sig.Draw("cont3same")
    	cont_2sig.Draw("cont3same")
    leg.Draw()
 	 # draw text
    if options.text:
      lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
      lat.DrawLatex(0.67,0.94,options.text)
  
    if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)

    canv.Modified()
    canv.Update()

    if not options.batch: raw_input("Looks ok?")
    if not options.outname: options.outname = '%s_%s'%(xvar,yvar)
    canv.Print('%s_col.pdf'%options.outname)
    canv.Print('%s_col.png'%options.outname)
    canv.Print('%s_col.C'%options.outname)
    canv.SetName('%s_col'%options.outname)

  # Now the main one
  #canv.Clear()
  for fi in range(len(options.files)):
    print "HMM ok "
    th2 = COLgrs[fi]
    gBF = BFgrs[fi]
    cont_1sig = CONT1grs[fi]
    cont_2sig = CONT2grs[fi]
    r.gStyle.SetOptStat(0)
    if fi==0: th2.Draw("axis")
    gBF.Draw("Psame")
    cont_1sig.Draw("cont3same")
    cont_2sig.Draw("cont3same")

  print "Still ok "
  leg.Draw()
  print "Still ok "
  # draw text
  if options.text:
    lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
    lat.DrawLatex(0.67,0.94,options.text)
  if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)
  print "Still ok "
  #canv.Modified()
  #canv.Update()
  print "Still ok "

  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname) 
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()
  mems = []
def plotMPdfChComp():

  print 'plotting mpdf ChannelComp'
  if not options.noComb: print '\t will assume first file is the global best fit'
  
  points = []
  loffiles = options.files

  k=0

  ppergraph = len(loffiles)/options.groups
  if not options.noComb:  ppergraph = (len(loffiles)-1)/options.groups

  while len(loffiles)>0:
    ext=''
    if options.groups>1: 
    	gr=k/ppergraph
    	ext = options.groupnames[gr]

    options.files = [loffiles[0]]
    options.method = 'mu'
    r.gROOT.SetBatch()
    print '%15s'%options.names[k],
    ps = plot1DNLL(True,options.xvar[k],ext)
    ps.insert(0,options.names[k])
    points.append(ps)
    k+=1
    loffiles.pop(0)
  
  rMin=1000.
  rMax=-1000.
  r.gROOT.SetBatch(options.batch)
  for point in points:
    if options.chcomp1sig:
      if point[1]+point[2]>rMax: rMax=point[1]+point[2]
      if point[1]-point[3]<rMin: rMin=point[1]-point[3]
    else:
      if point[1]+point[4]>rMax: rMax=point[1]+point[4]
      if point[1]-point[5]<rMin: rMin=point[1]-point[5]
    if options.verbose:
      print point[0], ':', point[1:]
  
  rMin = rMin - 0.7*r.TMath.Abs(rMin)
  rMax = rMax + 0.5*r.TMath.Abs(rMax)
  if options.xaxis: 
    rMin = float(options.xaxis.split(',')[0])
    rMax = float(options.xaxis.split(',')[1])
  if options.verbose:
    print 'ChComp PlotRange: ', rMin, '-', rMax

  bestFit = points[0]
  catFits = points[1:]
  if options.noComb: catFits = points[0:] # dont assume a combined fit
  ppergraph = len(catFits)/options.groups

  if options.verbose:
    print bestFit
    print catFits


  dummyHist = r.TH2F("dummy",";#sigma/#sigma_{SM};",1,rMin,rMax,ppergraph,0,ppergraph)
  dummyHist.GetYaxis().SetLabelFont(62)
  dummyHist.GetYaxis().SetLabelSize(0.038)
  catGraph1sig = [r.TGraphAsymmErrors() for gr in range(options.groups)]
  catGraph2sig = [r.TGraphAsymmErrors() for gr in range(options.groups)]

  runningChi2 = 0
  ndof = 0 # should be number of categories - 1
  for p, point in enumerate(catFits):
    grIndex = p//ppergraph
    pIndex  = p%ppergraph
    if options.groups==1: yshift=0.5

    elif options.groups%2==0 : # Even
      if grIndex+0.5 > float(options.groups)/2: yshift = 0.5 + (grIndex)*(0.2/options.groups)
      else: yshift = 0.5 - (grIndex+1)*(0.2/options.groups)
    else :
      if grIndex == (options.groups-1)/2 :yshift=0.5
      elif grIndex > float(options.groups)/2: yshift = 0.5 + grIndex*0.2/options.groups
      else :yshift = 0.5 - (grIndex+1)*0.2/options.groups
    if options.chcompShift:
      catGraph1sig[grIndex].SetPoint(pIndex,options.chcompShift,pIndex+yshift)
      catGraph2sig[grIndex].SetPoint(pIndex,options.chcompShift,pIndex+yshift)
    else:
      catGraph1sig[grIndex].SetPoint(pIndex,point[1],pIndex+yshift)
      catGraph2sig[grIndex].SetPoint(pIndex,point[1],pIndex+yshift)


    catGraph1sig[grIndex].SetPointError(pIndex,point[3],point[2],0.,0.)
    catGraph2sig[grIndex].SetPointError(pIndex,point[5],point[4],0.,0.)
    
    if point[0]=='': binlabel = 'cat%d'%p
    else: binlabel = point[0]
    dummyHist.GetYaxis().SetBinLabel(p+1,binlabel)

    catGraph1sig[grIndex].SetLineColor(int(options.colors[grIndex]))
    catGraph1sig[grIndex].SetLineWidth(2)
    catGraph1sig[grIndex].SetMarkerStyle(21)
    catGraph1sig[grIndex].SetMarkerColor(int(options.colors[grIndex]))
    catGraph1sig[grIndex].SetMarkerSize(1.5)
  
    catGraph2sig[grIndex].SetLineColor(int(options.colors[grIndex]))
    catGraph2sig[grIndex].SetLineWidth(2)
    catGraph2sig[grIndex].SetLineStyle(2)
    catGraph2sig[grIndex].SetMarkerStyle(21)
    catGraph2sig[grIndex].SetMarkerColor(int(options.colors[grIndex]))
    catGraph2sig[grIndex].SetMarkerSize(1.5)

    # for chi2 
    pcen   = bestFit[1]
    ppoint = point[1]
    if options.chcompShift: ppoint = options.chcompShift
    if options.noComb : pcen = 1.
    chierr = 0
    if ppoint > pcen : chierr = point[3]
    else : chierr = point[2]
    additive = 0
    if chierr != 0 and  (ppoint<rMax and ppoint>rMin): 
    	ndof+=1
    	runningChi2 += ((ppoint-pcen)/chierr)**2
	additive = ((ppoint-pcen)/chierr)**2
	

  if not options.noComb:
  	print "Compatibility Chi2 (ndof) = ", runningChi2, ndof-1, " p-val = ", r.TMath.Prob(runningChi2,ndof-1)

  dummyHist.SetLineColor(r.kBlack)
  dummyHist.SetFillColor(r.kGreen+2)

  dummyHist2 = dummyHist.Clone('%s2'%dummyHist.GetName())
  dummyHist2.SetFillColor(r.kGreen)

  if not options.legend: 
    leg = r.TLegend(0.68,0.7,0.94,0.88)

  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  leg.SetFillColor(0)
  if not options.noComb: leg.AddEntry(dummyHist,"Combined #pm 1#sigma","LF")
  if not options.chcomp1sig and not options.noComb: leg.AddEntry(dummyHist2,"Combined #pm 2#sigma","LF")
  if not options.noComb: leg.AddEntry(catGraph1sig[0],"Per category #pm 1#sigma","LP");
  if not options.chcomp1sig and not options.noComb: leg.AddEntry(catGraph2sig[0],"Per category #pm 2#sigma","LP");

  if options.groups>1: 
    for gr in range(options.groups):
      leg.AddEntry(catGraph1sig[gr],options.groupnames[gr],"L")

  bestFitBand1 = r.TBox(bestFit[1]-bestFit[3],0.,bestFit[1]+bestFit[2],len(catFits))
  bestFitBand1.SetFillColor(r.kGreen+2)
  bestFitBand1.SetLineStyle(0)

  bestFitBand2 = r.TBox(bestFit[1]-bestFit[5],0.,bestFit[1]+bestFit[4],len(catFits))
  bestFitBand2.SetFillColor(r.kGreen)
  bestFitBand2.SetLineStyle(0)

  bestFitLine = r.TLine(bestFit[1],0.,bestFit[1],len(catFits))
  bestFitLine.SetLineWidth(2)
  bestFitLine.SetLineColor(r.kBlack)

  r.gStyle.SetOptStat(0)
  cacheErrSize = r.gStyle.GetEndErrorSize()
  cachePadLeft = canv.GetLeftMargin()
  cachePadRight = canv.GetRightMargin()
  r.gStyle.SetEndErrorSize(8.)
  canv.SetLeftMargin(0.18);
  canv.SetRightMargin(0.05);
  canv.SetGridx(False)
  canv.SetGridy(False)

  dummyHist.Draw()
  if not options.noComb:
    if not options.chcomp1sig: bestFitBand2.Draw()
    bestFitBand1.Draw()
    bestFitLine.Draw()

  for gr in range(options.groups):
    if not options.chcomp1sig: catGraph2sig[gr].Draw("EPsame")
    catGraph1sig[gr].Draw("EPsame")

  if options.chcompLine:
    line = r.TLine(rMin,options.chcompLine,rMax,options.chcompLine)
    line.SetLineWidth(3)
    line.SetLineStyle(r.kDashed)
    line.Draw("same")
    label1=r.TText()
    label1.SetNDC()
    label1.SetText(0.26,0.23,"8TeV")
    label1.SetTextFont(62)
    label1.SetTextSize(.07)
    label1.SetTextAngle(90)
    label2=r.TText()
    label2.SetNDC()
    label2.SetText(0.26,0.65,"7TeV")
    label2.SetTextFont(62)
    label2.SetTextSize(.07)
    label2.SetTextAngle(90)
    label1.Draw("same")
    label2.Draw("same")

  if options.groups>1 or not options.noComb: leg.Draw("same")

  # draw text
  if options.text:
    lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
    lat.DrawLatex(0.72,0.94,options.text)

  if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)
  canv.Modified()
  canv.Update()

  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()
  
  r.gStyle.SetEndErrorSize(cacheErrSize)
  canv.SetLeftMargin(cachePadLeft);
  canv.SetRightMargin(cachePadRight);

def plotMPdfMaxLH():

  points = []
  loffiles = options.files

  k=0
  while len(loffiles)>0:
    options.files = [loffiles[0]]
    tf = r.TFile(options.files[0])
    print tf.GetName()
    tree = tf.Get('limit')
    tree.GetEntry(0)
    mh = tree.mh
    tf.Close()
    options.method = 'mu'
    r.gROOT.SetBatch()
    ps = plot1DNLL(True,options.xvar[k])
    ps.insert(0,mh)
    points.append(ps)
    k+=1
    loffiles.pop(0)

  points.sort(key=lambda x: x[0])

  bestFit = r.TGraph()
  oneSigma = r.TGraphAsymmErrors()
  twoSigma = r.TGraphAsymmErrors()
  
  for p,point in enumerate(points):
    bestFit.SetPoint(p,point[0],point[1])
    oneSigma.SetPoint(p,point[0],point[1])
    twoSigma.SetPoint(p,point[0],point[1])
    oneSigma.SetPointError(p,0.,0.,point[3],point[2])
    twoSigma.SetPointError(p,0.,0.,point[5],point[4])
  
  bestFit.SetLineColor(r.kBlack)
  bestFit.SetLineWidth(3)
  bestFit.SetLineStyle(r.kDashed)

  twoSigma.SetLineColor(r.kBlack)
  twoSigma.SetLineStyle(r.kDashed)
  twoSigma.SetLineWidth(3)
  twoSigma.SetFillColor(r.kGreen)

  oneSigma.SetLineColor(r.kBlack)
  oneSigma.SetLineStyle(r.kDashed)
  oneSigma.SetLineWidth(3)
  oneSigma.SetFillColor(r.kGreen+2)

  if not options.legend: leg = r.TLegend(0.6,0.7,0.88,0.88)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  leg.SetFillColor(0)
  leg.AddEntry(bestFit,"Best Fit","L")
  leg.AddEntry(oneSigma,"#pm 1 #sigma","FL")
  leg.AddEntry(twoSigma,"#pm 2 #sigma","FL")

  dummyHist.SetStats(0)
  dummyHist.GetYaxis().SetTitle("#sigma/#sigma_{SM}")

  dummyHist.GetYaxis().SetRangeUser(twoSigma.GetMinimum(),twoSigma.GetMaximum())

  if options.xaxis: dummyHist.GetXaxis().SetRangeUser(float(options.xaxis.split(',')[0]),float(options.xaxis.split(',')[1]))
  if options.yaxis: dummyHist.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))

  dummyHist.Draw("AXISG")
  twoSigma.Draw("LE3same")
  oneSigma.Draw("LE3same")
  if options.xaxis:
        axmin = float(options.xaxis.split(',')[0])
        axmax = float(options.xaxis.split(',')[1])
  else:
  	axmin = 110
	axmax = 150
  line = r.TLine(axmin,1.,axmax,1.)
  line.SetLineColor(r.kRed)
  line.SetLineWidth(3)
  line.Draw("same")
  bestFit.Draw("Lsame")

  # draw text
  lat.DrawLatex(0.12,0.92,"CMS VERY Preliminary")
  lat.DrawLatex(0.67,0.94,options.text)
  
  if options.MHtext: lat.DrawLatex(mhTextX,mhTextY,options.MHtext)
  # draw legend
  leg.Draw()
  canv.SetGrid()
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()

def run():
  if options.verbose:
    print options.method
    print options.files
    print options.colors
    print options.styles
    print options.widths
    print options.names

  if options.method=='pval' or options.method=='limit' or options.method=='maxlh':
    runStandard()
  elif options.method=='mh' or options.method=='mu' or options.method=='rv' or options.method=='rf' or options.method=='mpdfchcomp' or options.method=='mpdfmaxlh':
    path = os.path.expandvars('$CMSSW_BASE/src/h2gglobe/Macros/FinalResults/rootPalette.C')
    if not os.path.exists(path):
      sys.exit('ERROR - Can\'t find path: '+path) 
    r.gROOT.ProcessLine(".x "+path)
    path = os.path.expandvars('$CMSSW_BASE/src/h2gglobe/Macros/ResultScripts/GraphToTF1.C')
    if not os.path.exists(path):
      sys.exit('ERROR - Can\'t find path: '+path) 
    r.gROOT.LoadMacro(path)
    if options.method=='mpdfchcomp':
      plotMPdfChComp()
    elif options.method=='mpdfmaxlh':
      plotMPdfMaxLH()
    else:
      plot1DNLL(False,options.xvar[0])
  elif options.method=='mumh':
    plot2DNLL("MH","r","m_{H} (GeV)","#sigma/#sigma_{SM}")
  elif options.method=='rvrf':
    plot2DNLL("RF","RV","#mu_{ggH+ttH}","#mu_{qqH+VH}")

# __MAIN__

if options.datfile:
  d = open(options.datfile)
  for line in d.readlines():
    if line.startswith('#'): continue
    if line=='\n': continue
    config={}
    line = line.replace('\=','EQUALS')
    for opt in line.split(':'):
      config[opt.split('=')[0]] = opt.split('=')[1].replace('EQUALS','=').split(',')
    for opt in ['colors','styles','widths']:
      if opt in config.keys():
        config[opt] = [int(x) for x in config[opt]]
    
    for key, item in config.items():
      if len(item)==1 and key in ['method','text','outname','legend','yaxis']:
        item=item[0].strip('\n')
      setattr(options,key,item)

    if options.verbose: print options
    run()

else:
  run()

print 'All canvases written to:', outf.GetName()
outf.Close()
