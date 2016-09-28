#!/usr/bin/env python
# -*- coding: utf-8 -*-
# make a horizontal bar chart
"""
Dept. of Automatic Control
    School of Electrical Engineering
        KTH Kungliga Tekniska Högskolan (Royal Institute of Technology)
Created on Sat Feb 7 10:53:52 AM 2015

@author: gonga <gonga@kth.se>

New ideas on accerelating Deterministic Neighbor Discovery: epidemic discovery
A frame consists of: (1) anchor discovery slot at a fixed position and (3)
a probe slot that changes its position from 0 to T/2. Additionally, nodes may
use extra slots to listen to anchor slots of known Hop 2 neighbors.
The additional slots are a tradeoff between discovery speed vs energy.
"""

import matplotlib as mpl
import matplotlib.pyplot  as plt
from pylab import *

import math
import numpy as np
from numpy import mean
from scipy import stats
import scipy as sp


from matplotlib import rc
plt.rcParams['ps.useafm'] = True
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
#plt.rcParams['pdf.fonttype'] = 3 #[42 or 3]
prop = matplotlib.font_manager.FontProperties(size=8)


simSeed= 997
snapShotCounter=0
rsObj = np.random.mtrand.RandomState(simSeed)

class Node:
    def __init__(self, nodeID, avgNodeDegree, periodsVec):
      self.id          = nodeID        
      self.chId        = 0
    
      self.ownSlot     = None
      self.ownChannel  = None
      self.neighLen    = avgNodeDegree
      
      self.probeOffset = 0
      self.probeIndex  = 0 
      self.txOffset    = 0
      self.k_prob      = 0;
      
      self.nodePeriod  = periodsVec[self.id%len(periodsVec)]
      self.T0          = np.random.randint(self.nodePeriod)      
     
      self.state = False
      self.networkVec    = {}
      self.notKnownNeigh = {}
      self.neighbors     = {}
      self.neighbors1Hop = {}
      
      
      self.xc0 = 0
      self.yc0 = 0
      self.hopCount    = 0
      self.radioRadius = 30
      self.energyUsage = 0
      
      self.energyPeriod= 0
      self.energyPeriodCounter = 0
      
      
      self.t_anchor    = 0
      self.tAnchorVec  = {}

      self.jfactorVec  = {}
      self.offsetsVec  = {}
      
      self.updatedOffsets = {}   
      
      self.len1hop     = 0
      self.tKnown      = {}
      self.tConfirmed  = {}
      self.hopCountVec = {}
      self.hop2TxNumber= {}
      
      self.hop2MaxTxTries = 4

      
      '''Const related when a node starts discovery..'''
      self.active = False 
      '''Generate a random number between 0 and 200.'''
      self.startTime = 0
                
      
      #self.networkVec[self.id]=self 
      
    def isActive(self, simTime):        
        
        if simTime >= self.T0:
            self.active     = True
            self.probeIndex = (self.T0 + simTime)%self.nodePeriod
            
            if self.probeIndex == 0:
                
                self.t_anchor = simTime                
                
                self.updateJfactor()
                
                self.updateTxOffsets(simTime)                
                
                self.probeOffset = 2*self.k_prob + 2               
                
                self.k_prob = self.k_prob + 1
                             
                
                if self.k_prob > self.nodePeriod/4:
                    self.k_prob  = 0

                    
                 
            return True
            
        return False
    
    def updateJfactor(self):
        for key, value in self.jfactorVec.iteritems():
            ''''''
            ta = self.timeAnchorNeighbor(self.networkVec[key]) 
            
            neigh = self.networkVec[key]
            
            if self.t_anchor > ta:
                if self.nodePeriod < neigh.nodePeriod:
                    jfactor = value + 1
                    self.jfactorVec[key] = jfactor
                else:
                    jfactor = value + int(self.nodePeriod/neigh.nodePeriod)
                    self.jfactorVec[key] = jfactor
            
            
    def updateTxOffsets(self, t):
        for key, node in self.networkVec.iteritems():
            hop = self.hopCountVec[key]
            ta = self.timeAnchorNeighbor(node) 
            if hop == 1 and node.nodePeriod != self.nodePeriod and ta > self.t_anchor:
                self.updatedOffsets[key] = ta - self.t_anchor
                
            #jfactor = self.jfactorVec[key]    
            #print str(self.id)+'('+str(self.nodePeriod)+','+str(jfactor)+') -->',
            #print str(node.id)+'('+str(node.nodePeriod)+') @ '+ str(self.updatedOffsets[key]),
            #print t, self.timeAnchorNeighbor(node)
                
            
    def timeAnchorNeighbor(self, node):
        offset     = self.offsetsVec[node.id]
        anchorTime = self.tAnchorVec[node.id]
        jfactor    = self.jfactorVec[node.id]
        
        ta = anchorTime + offset + jfactor*node.nodePeriod 
        
        return ta
        
    def isThereAnchor(self, t):
        
        for idNeigh, offset in self.offsetsVec.iteritems():
            
            txNum = self.hop2TxNumber[idNeigh]
            
            if self.hopCountVec[idNeigh] == 2 and txNum < self.hop2MaxTxTries:
                
                tAnchor = self.timeAnchorNeighbor(self.networkVec[idNeigh])
                
                if tAnchor == t or tAnchor == t-1:
                    
                    self.hop2TxNumber [idNeigh] = txNum + 1
                    
                    return True
        return False
        
    def isNeighborAnchor(self, t):

        
        for idNeigh, node in self.networkVec.iteritems():
            
            txNum = self.hop2TxNumber [idNeigh]
            
            if self.hopCountVec[idNeigh] == 2 and txNum < self.hop2MaxTxTries:
                
                tAnchor = self.timeAnchorNeighbor(node)
                vTest = [t-2, t-1, t, t+1]
                vTest2= [tAnchor-2, tAnchor-1, tAnchor, tAnchor+1]
                
                #if tAnchor == t-1 or tAnchor == t or tAnchor-1 == t or tAnchor == t-2:# or self.networkVec[idNeigh].isAnchorSlot(t):
                if tAnchor in vTest or t in vTest2: #node.isAnchorSlot(t):
                #if node.isAnchorSlot(t):
                    
                    self.hop2TxNumber [idNeigh] = txNum + 1
                    
                    #print str(self.id)+'('+str(self.nodePeriod)+')-->',
                    #print str(idNeigh)+'('+str(node.nodePeriod)+') @', 
                    #print str(t)+'/'+str(tAnchor), self.updatedOffsets[idNeigh] # str(node.t_anchor)  #
                    return True
        
        return False
        
    def isAnchorSlot(self, t):
        retVal = False
        retVal = (self.T0 + t)%self.nodePeriod == 0 
        #retVal = retVal or (self.T0 + t-1)%self.nodePeriod == 0 
        
        return retVal
    
    def isProbeSlot(self, t):
        retVal = False
        retVal =  (self.T0+t)%self.nodePeriod == self.probeOffset
        
        retVal = retVal or (self.T0+t-1)%self.nodePeriod == self.probeOffset
        
        return retVal

    def isSlotTx(self, t):
        ''''''
        if self.active:
            retVal = False
            retVal = retVal or self.isAnchorSlot(t)
            
            self.txOffset = 0
            
            if retVal == False:
                
                retVal =  self.isProbeSlot(t) 
                
                if retVal == True:
                    self.txOffset = self.probeOffset
                else:
                    ''''''
                    retVal = self.isNeighborAnchor(t)#self.isThereAnchor(t)  
                    
                    if retVal == True:
                        self.txOffset = self.probeIndex

            if retVal == True:
                self.updateEnergyUsage()
            
            return retVal
        
        return False
          
    def addCoordinates(self, x, y):
       self.xc0 = x
       self.yc0 = y
       
    def isNeighbor(self, nodeXY):
       
       if nodeXY.id != self.id:
          d = math.sqrt( (nodeXY.xc0-self.xc0)**2 + (nodeXY.yc0 -self.yc0)**2)
       
          if d < self.radioRadius:
               return True    
               
       return False
       
    def isNeighborByID(self, nID):
        if self.id != nID and nID in self.neighbors:
            return True
        return False
        
    def updateEnergyUsage(self):
        self.energyUsage = self.energyUsage + 1 
        self.energyPeriodCounter = self.energyPeriodCounter + 1
        
    def getEnergyNode(self):
        return int(round(1.*self.energyUsage*(2./3)))
        
    def setEnergyPeriod(self):
        self.energyPeriod = int(round(self.energyPeriodCounter*2./3))
        #self.energyPeriod = int(round(self.energyPeriodCounter))
        self.energyPeriodCounter = 0
    
    def flushNeighbors(self):
       ''''''
       self.len1hop       = 0
       self.tKnown        = {} 
       self.tConfirmed    = {}
       self.neighbors     = {}
       self.networkVec    = {}    
       self.notKnownNeigh = {}
       self.neighbors1Hop = {}
       self.hopCountVec   = {}
       #self.offset2Neighs = {}
       self.hop2TxNumber  = {}
       
       self.jfactorVec    = {}
       self.tAnchorVec    = {}
       self.offsetsVec    = {}
       
       self.updatedOffsets= {}
       
       self.state         = False
       self.active        = False 
       
       self.T0            = np.random.randint(self.nodePeriod)      
       self.probeIndex    = 0
       self.probeOffset   = 0
       self.energyUsage   = 0 
       
       self.energyPeriod  = 0
       self.energyPeriodCounter = 0
       
       self.txOffset      = 0
       self.k_prob        = 0

       
    def addNeighbor(self, neighId):
        if neighId not in self.neighbors1Hop.values():
            self.neighbors1Hop[neighId.id]=neighId
            
            
    def addNotKnown(self, notID):
        if notID not in self.notKnownNeigh.values():
            self.notKnownNeigh[notID.id]=notID
                  
    def allNetworkDiscovered(self):
        return len(self.networkVec) == self.neighLen-1
                  
    def allNeighborsDiscovered(self):
	 return len(self.neighbors1Hop) == self.neighLen-1
  
    def addChannel(self, chId):
        self.chId = chId        
        
    def addReceived(self, node, hopcount, elapTime, offSet2Node):
        
        if node not in self.networkVec.values():

            self.networkVec[node.id]    = node  
            
            self.hopCountVec[node.id]   = hopcount
            self.tKnown[node.id]        = elapTime
            self.tConfirmed[node.id]    = elapTime
            
            '''ADD OFFSET OF THIS NODE::'''
            self.offsetsVec[node.id]     = offSet2Node
            
            self.updatedOffsets[node.id] = offSet2Node
            
            '''Max ATTEMPT TX = 4'''
            self.hop2TxNumber [node.id]  = 0
            
            self.jfactorVec   [node.id]  = 0
                        
            self.tAnchorVec   [node.id]  = self.t_anchor
                        

            if hopcount == 1:
                self.addNeighbor(self.networkVec[node.id])
            
        else:
            hop = self.hopCountVec[node.id]
            
            if hopcount < hop:
                
                self.hopCountVec[node.id]   = hopcount
                self.tConfirmed[node.id]    = elapTime
                
                self.offsetsVec[node.id]    = offSet2Node 
                
                self.updatedOffsets[node.id]= offSet2Node
                
                self.jfactorVec   [node.id] = 0
                
                self.tAnchorVec   [node.id] = self.t_anchor
                
                if hopcount == 1:
                    self.addNeighbor(self.networkVec[node.id])
                    '''updateOffset'''
                              
                   
    def disseminate(self, node, elapsedTime):        
        
        if node.id != self.id:            
            
            ownOffset = self.getOffset() - node.getOffset()
            
            offsetH1  = ownOffset
            
            if ownOffset < 0:
                 offsetH1  = node.nodePeriod + ownOffset
            
            self.addReceived(node, 1, elapsedTime, offsetH1)
        
            '''...add overheard nodes to list...'''
            for nodej in node.networkVec.values():            
                
                if nodej.id != self.id:
                    
                    hopCount = node.hopCountVec[nodej.id] + 1              
    
                    if hopCount == 2:
 
                        offsetH2 = node.updatedOffsets[nodej.id] + ownOffset                        
                        
                        if offsetH2 < 0:
                            offsetH2 = nodej.nodePeriod + offsetH2
                        
                        self.addReceived(nodej, hopCount, elapsedTime, offsetH2)
        
    def getOffset(self):
        #return (self.T0 + t)%self.nodePeriod
        return self.txOffset
        
    def getLenXhops(self, hopCount):
        
        len1hopDirect   = 0
        len1hopIndirect = 0
        sum1hopLen      = 0
        
        for node in self.neighbors1Hop.values():
            t0 = self.tKnown[node.id]
            t1 = self.tConfirmed[node.id]

            sum1hopLen = sum1hopLen + 1
            
            if (t1-t0) > 0:
                    len1hopIndirect = len1hopIndirect + 1
            if (t1-t0) == 0:
                    len1hopDirect = len1hopDirect + 1
            
        return [len1hopDirect, len1hopIndirect, sum1hopLen]


#---------------------------------------------------------------------------    
def confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), sp.stats.stderr(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m-h, m, m+h
#---------------------------------------------------------------------------
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), sp.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m-h, m, m+h
#---------------------------------------------------------------------------
def funcProbOf(C, N):
    a = N
    b = 2*C+N-1
    c = C
    f2 = (b - np.sqrt(math.pow(b,2)-4*a*c))/(1.0*2*a)
    return f2
#--------------------------------------------------------------------------
def loss_p(p, n):
    a = 1.0
    for i in range(n):
        a = a*(1-p)

    return a
#---------------------------------------------------------------------------
def addTopology(Xmax, Ymax, Nodes):
    lnodes={}
    xco = np.arange(0, Xmax+0.25, 0.25)
    yco = np.arange(0, Ymax+0.25, 0.25)    
    '''add coordinates'''
    for node in Nodes.values():
        x = np.random.choice(xco)
        y = np.random.choice(yco)
        
        Nodes[node.id].addCoordinates(x,y)
        
        lnodes[node.id] = Nodes[node.id]
        
    '''add neighbors based on X and Y'''
    for nodei in lnodes.values():
        for nodej in lnodes.values():
            if nodei.isNeighbor(nodej):
                lnodes[nodei.id].neighbors[nodej.id] = nodej
    '''Print Coordinates'''           
    #for node in lnodes.values():
    #    print [node.id, node.xc0, node.yc0],'->',node.neighbors
    
    saveTopology('./DND_topology.dat', lnodes)
            
    return lnodes
#---------------------------------------------------------------------------                  
def nodesAddCoordinates(network, lnodes):
    Lnodes={}
    
    if len(network) < len(lnodes):
        print 'WARNING:::: COORDINATES VECTOR SMALLER THAN SIZE OF THE NETWORK'
        exit(0)
    print '''==>downloading network topology.....'''
    
    
    #plt.axes()
    
    for node, coord in zip(lnodes.values(), network):
            x, y = coord
            lnodes[node.id].addCoordinates(x,y) 
            Lnodes[node.id] = lnodes[node.id]
            
    '''add neighbors based on X and Y'''
    print '==>computing neighborhood...'
    
    for nodei in Lnodes.values():
        #print 'Node:', nodei.id,' adding',        
        for nodej in Lnodes.values():                        
            if nodei.isNeighbor(nodej):
                #print nodej.id,
                #nodei.neighbors.append(nodej)
                nodei.neighbors[nodej.id] = nodej
        
        '''PLOT NODE LOCATION'''
        x, y = nodei.xc0, nodei.yc0
        
        #print [a for a in nodei.neighbors]
        
        #circxy = plt.Circle((x, y), radius = 2, fc='r')#,

        #plt.gca().add_patch(circxy)
        
        #plt.text(x-0.5*2, y-0.5*2, str(nodei.id), fontsize=10, color='k')
        
        #'''PLOT LINKS'''
        #for neighNode in nodei.neighbors:
        #    x = (nodei.xc0, neighNode.xc0)
        #    y = (nodei.yc0, neighNode.yc0)
            #plot(x,y, color='b', linestyle='-', linewidth=0.2)
    

    
    #xlim([0,100])
    #ylim([0,100])
    

    
    #plt.grid(True)
    #title('[100m x 100m]::::::RANDOM NETWORK TOPOLOGY::::::')
    #xlabel('X-$axis$ (m)')
    #ylabel('Y-$axis$ (m)')            
    #plt.show()

    return Lnodes    
#--------------------------------------------------------------------------- 
def networkUpdate(lnodes):
    plt.clf()
    
    plt.axes()        
        
    '''PLOT NODE LOCATION'''
    for nodei in lnodes.values():
        x, y = nodei.xc0, nodei.yc0
        #mpl.patches.Circle(x,y, radius=3, color='red')
        circxy = plt.Circle((x, y), radius = 2, fc='k')#,
        plt.gca().add_patch(circxy)
        plt.text(x-0.5*2, y-0.5*2, str(nodei.id), fontsize=10, color='white')
        
        '''PLOT LINKS'''
        for neighNode in nodei.neighbors1Hop:
            
            x = (nodei.xc0, neighNode.xc0)
            y = (nodei.yc0, neighNode.yc0)
            plot(x,y, color='b', linestyle='-', linewidth=0.2)
    
    '''RESTORE GRID AND AXIS NAMES'''
    xlim([0,100])
    ylim([0,100])
    
    plt.grid(True)
    title('[100m x 100m]:::::: [Snapshot] NETWORK TOPOLOGY::::::')
    xlabel('X-$axis$ (m)')
    ylabel('Y-$axis$ (m)')            
    plt.show()      

#--------------------------------------------------------------------------- 
def networkDraw(lnodes):
    #base_FigDir = '/home/gonga/Dropbox/Research/dcoss-ieee-2015/Figures/'
    plt.clf()
    
    plt.axes()   

    selectedNodes=[3,13, 15,25,26,39, 41]#[9,15,26, 41,44]
        
    '''PLOT NODE LOCATION'''
    for nodei in lnodes.values():
        
        x, y = nodei.xc0, nodei.yc0
        
        circxy = []
        
        if nodei.id in selectedNodes:
            circxy = plt.Circle((x, y), radius = 3, fc='r')#,
        else:
            circxy = plt.Circle((x, y), radius = 2, fc='k')#,
            
        plt.gca().add_patch(circxy)
        
        if nodei.id in selectedNodes:
            plt.text(x-0.5*2, y-0.5*2, str(nodei.id), fontsize=10, color='white') 
        else:
            plt.text(x-0.5*2, y-0.5*2, str(nodei.id), fontsize=10, color='white')
        
        '''PLOT LINKS'''
        for neighNode in nodei.neighbors.values():
            
            x = (nodei.xc0, neighNode.xc0)
            y = (nodei.yc0, neighNode.yc0)
            plot(x,y, color='b', linestyle='-', linewidth=0.2)
    
    '''RESTORE GRID AND AXIS NAMES'''
    xlim([0,100])
    ylim([0,100])
    
    plt.grid(True)
    title(' Network Topology                   ')
    xlabel('X-$axis$ (m)')
    ylabel('Y-$axis$ (m)')            
    plt.show()
    #plt.savefig(base_FigDir+'NetworkTopology.pdf', dpi=120, bbox_inches='tight')      
#---------------------------------------------------------------------------     
def saveTopology(fname, listNodes):
    with open(fname, 'w') as fw:
        for ii, node in enumerate(listNodes.values()):
            if ii+1 < len(listNodes):
                fw.write(str(node.xc0)+',')
                fw.write(str(node.yc0)+':')
            else:
                fw.write(str(node.xc0)+',')
                fw.write(str(node.yc0))                                          
#---------------------------------------------------------------------------         
def readTopology(fname):
    with open(fname,'r') as fr:
        dt = fr.read().split(':')
        #print dt
        xx = [(float(x.split(',')[0]),float(x.split(',')[1])) for x in dt]

        return xx    
#---------------------------------------------------------------------------        
def getLenXhops(nodeL, hopCount):
        
        len1hopDirect   = 0
        len1hopIndirect = 0
        sum1hopLen      = 0
        
        for node in nodeL.neighbors1Hop.values():
            t0 = nodeL.tKnown[node.id]
            t1 = nodeL.tConfirmed[node.id]
            
            if 1: #node.hopCount == 1:
                sum1hopLen = sum1hopLen + 1
                
                if (t1-t0) > 0:
                        len1hopIndirect = len1hopIndirect + 1
                if (t1-t0) == 0:
                        len1hopDirect = len1hopDirect + 1
            
        return [len1hopDirect, len1hopIndirect, sum1hopLen]
#--------------------------------------------------------------------------- 
def OpenFile(fname):
    fd = open(fname, 'w')
    
    return fd        
#---------------------------------------------------------------------------  
def writeLogFile(fdc, node, iterCount, currTime, operation):
    if operation == 0:
       dir1hop,ind1hop,sum1hop = getLenXhops(node,1)
       str2Write='>:'+str(iterCount)+','+str(node.id)+','+str(1)+','
       str2Write+=str(sum1hop)+','+str(dir1hop)+','+str(ind1hop)+',' 
       str2Write+=str(currTime)+','+str(node.getEnergyNode())+','
       str2Write+=str(node.nodePeriod)+'\n'
       '''WRITE 2 FILE'''
       fdc.write(str2Write)
       fdc.flush()
    if operation == 1:
       dir1hop,ind1hop,sum1hop = getLenXhops(node,1)
       str2Write='EN>:'+str(iterCount)+','+str(node.id)+','+str(1)+','
       str2Write+=str(sum1hop)+','+str(dir1hop)+','+str(ind1hop)+',' 
       str2Write+=str(currTime)+','+str(node.getEnergyNode())+','
       str2Write+=str(node.energyPeriod)+','
       str2Write+=str(node.nodePeriod)+'\n'
       '''WRITE 2 FILE'''
       fdc.write(str2Write)
       fdc.flush()        
        
#---------------------------------------------------------------------------            
'''Create all nodes in the Network'''
def createNodes(n, channelLen, periods):
    lnodes={}
    for i in range(1, n+1):
        node = Node(i,n, periods)
        #channel = rsObj.randint(channelLen) #i%channelLen
        channel = i%channelLen
        #ownSlot = 1 + i%(T_period-1)
        node.addChannel(channel)
                
        lnodes[i]= node
        
    return lnodes
#---------------------------------------------------------------------------
def flushIds(Lnodes):
    for i, node in enumerate(Lnodes.values()):
       Lnodes[node.id].flushNeighbors()
       #Lnodes[node.id].networkVec    = []    
       #Lnodes[node.id].notKnownNeigh = []
       #Lnodes[node.id].neighbors1Hop = []  
       
       #Lnodes[node.id].networkVec.append(node)
#---------------------------------------------------------------------------
def printNeighbors(Lnodes):
    for node in Lnodes.values():
        print 'NodeID:', node.id, 'Neighbors: ',
        #for n in node.neighbors1Hop:
        if 1:
            #print n.id,
            print getLenXhops(node, 1), len(node.networkVec), node.Phase_i
           
    #print '\n'
#---------------------------------------------------------------------------
'''returns True if every node have discovered all its neighbors '''
def all2allComplete(Lnodes):
    for node in Lnodes.values():
        if node.allNetworkDiscovered() == False:
            return False
    return True
#---------------------------------------------------------------------------
def allNeighborsDiscovered(Lnodes):
    #vec90pComplete=[]
    for node in Lnodes.values():
        if node.allNeighborsDiscovered() == False:
            return False
    return True

    return False
#---------------------------------------------------------------------------    
def plot_cdf(a):
    a.sort()
    yvals=np.arange(len(a))/float(len(a))
    plt.plot(a, yvals )  
    
    grid(True)
    #plt.close()
    ylabel('CDF')
    xlabel('Worst case Latency (slots)')
    plt.show()
#---------------------------------------------------------------------------
def write_file(fname, a):
    with open(fname,'w') as fw:
        for i, val in enumerate(a):
            if i+1 < len(a):
                fw.write(str(val)+',')
            else:
                fw.write(str(val))
#---------------------------------------------------------------------------
def read_file(fname):
    with open(fname,'r') as fr:    
        dt = fr.read().split(',')
        xx =[int(x) for x in dt]
        return xx    
#--------------------------------------------------------------------------- 
#def saveTopology(fname, listNodes):
#    with open(fname, 'w') as fw:
#        for ii, node in enumerate(listNodes.values()):
#            if ii+1 < len(listNodes):
#                fw.write(str(node.xc0)+',')
#                fw.write(str(node.yc0)+':')
#            else:
#                fw.write(str(node.xc0)+',')
#                fw.write(str(node.yc0))                                          
#---------------------------------------------------------------------------         
#def readTopology(fname):
#    with open(fname,'r') as fr:
#        dt = fr.read().split(':')
#        #print dt
#        xx = [(float(x.split(',')[0]),float(x.split(',')[1])) for x in dt]
#
#        return xx
#--------------------------------------------------------------------------- 
colorNames=[name for name, hex in matplotlib.colors.cnames.iteritems()]        
#--------------------------------------------------------------------------- 
def MikaelData(lnodes):
    fname='./MJ_Hop1_and_Hop2_InformationV2.csv'
    base_FigDir = '/home/gonga/Dropbox/Research/dcoss-ieee-2015/Figures/'
    
    plt.clf()
    
    plt.axes() 

    fd = OpenFile(fname)
    nodesH2=[]
    valuesVec =[]
    idsVEc    =[]
    for node in lnodes.values():
      if 1:#node.id == 41:
        nodesH2=[]
        fd.write(str(node.id)+','+str(len(node.neighbors))+',' )
        ids=[k.id for k in node.neighbors.values()]  
        print str(node.id),',',str(len(node.neighbors)),ids 
        
        #plot(node.id, len(node.neighbors), 'r*', lw=2)
        
        if 1:#node.id == 41:
            for nhop1 in node.neighbors.values():
               tmpH2 = [neighH2.id for neighH2 in lnodes.values() if nhop1.isNeighbor(neighH2)]
                
               for k in tmpH2:
                   if k not in nodesH2 and k not in ids:
                       nodesH2.append(k)
                       #print k,
               
               nodesH2 = list(set(nodesH2))
            
            nodesH2.sort()
            
            print 'ID:', node.id, len(node.neighbors), nodesH2
            
            #plot(node.id, len(nodesH2), 'bo', lw=3)
            
            valuesVec.append((len(node.neighbors),len(nodesH2)))
            idsVEc.append((node.id, node.id))
            
            fd.write(str(len(nodesH2))+'\n')
            #break
    """"""
    fd.close()  
    #xlim([0,100])
    #ylim([0,100])
    selectedNodes=[3,13, 15,25,26,39, 41]
    clIdx=0
    for x, y in zip (idsVEc, valuesVec):
        found = 0
        for kId in selectedNodes:        
            if kId in x:
                found = 1
                lblStr= 'ID:'+str(kId)+'-['+str(y[0])+','+str(y[1])+']'
                plot(x, y, 'o-', lw=4, label=lblStr)
                break
            
        if found == 0:
            plot(x, y, 'k+-', lw=2)
            
        ####
        clIdx = clIdx + 1            
    
   #lgN=[str('ID:')+str(nodeID) for nodeID in selectedNodes]
    plt.grid(True)
    title('Number of Hop1 and Hop 2 neighbors')
    xlabel('nodeIDs')
    ylabel('Number of H1 and H2 neighbors')            
    
    plt.legend(loc='best', ncol=1, prop={'size':10})
    
    #plt.show()
    
    plt.savefig(base_FigDir+'NetworkH1_H2_Neighbors.pdf', dpi=120, bbox_inches='tight')  
                                                    
#---------------------------------------------------------------------------          
#---------------------------------------------------------------------------            
def runSim():
  
  global csvFd, CSize, KSize  
  
  global maxHopCount, T_period, vec_periods
  

  numRepeat = 200
  XMAX, YMAX  = (100, 100)
  
  vec_periods = [(40, 200)]
  
  nodes    = [2]#[5,10,15,20,25,30]#[2,5,10,15,20,25,30]#range(60, 101,10)
  channels = [1]#[4,8]
  
  #fileDesc = OpenFile('./DND_Output.csv')
  
  
  print '----------------------------------------------'
  
  #networkCoord=readTopology('./DND_topology.dat')
  
  for periods in vec_periods:
      
      for num_nodes in nodes: 
          
          fname = './sim-data/ASL-Clique_N'+str(num_nodes)+'_T'
          
          strName2=''
          for p in periods:
              strName2+=str(p)+'_'
         
          fname = fname + strName2 + '.csv'
          
          print fname 
          
          #exit(0)
          '''Open Output File'''
          #fileDesc = OpenFile(fname)          
          
          for channel in channels:
              
              vec_times = []
              ##t_slot = 1
              print '==> N=',num_nodes,' K=',channel,']'
              
              Lnodes = createNodes(num_nodes, channel, periods)
              
              #addTopology(XMAX, YMAX, Lnodes)          
              
              
              #Lnodes = nodesAddCoordinates(networkCoord, Lnodes)
              
              #networkDraw(Lnodes)
              
              #for node in Lnodes.values():
              #    print str(node.id-1)+' 0.0 '+str(node.xc0)+' '+str(node.yc0)
              ##MikaelData(Lnodes)
              
              #exit(0)
                        
              for iterNum  in range(numRepeat):
                  #A=np.eye(n)
                  elapsedTime = 0
                  
                  resprint = '-->r '+str(iterNum)

                  
                  #printNeighbors(Lnodes)
                  
                  Lnodes = createNodes(num_nodes, channel, periods)
                  
                  #flushIds(Lnodes)
                  
                  while all2allComplete(Lnodes) == False:
                  #while allNeighborsDiscovered(Lnodes) == False:
                  #while elapsedTime < 5200:
                        elapsedTime = elapsedTime + 1 
                                   
                        if elapsedTime%100 == 0:
                           ''''''
                           #print '**[round: ', iterNum , elapsedTime,']'  
                           #networkUpdate(Lnodes)
                               
                        for node in Lnodes.values():
                            Lnodes[node.id].isActive(elapsedTime)
                        
                        txNodes=[node for node in Lnodes.values() if node.isSlotTx(elapsedTime) == True]
                        
                        if len(txNodes) >= 2:# and len(txNodes) <= 3:
                            '''There is an Overlap..'''
                            #print 'SLOT Overlap: ', elapsedTime
                            ###break                        
                            
                            for txNo in txNodes:                                
                                for lnode in txNodes:
                                    if txNo.id != lnode.id and txNo.isNeighbor(lnode):                                        
                                        #Lnodes[lnode.id].disseminate(txNo, elapsedTime)
                                        lnode.disseminate(txNo, elapsedTime)
                                        
                        if 1:#'A' == 'B':
                              for node in Lnodes.values():
                                 if node.id == 2 or node.id == 1:
                                    if node.len1hop < len(node.neighbors1Hop):
                                       node.len1hop = len(node.neighbors1Hop)
                                       #writeLogFile(fileDesc, node, iterNum, elapsedTime, 0)
                                    if (node.T0 +elapsedTime+1)%node.nodePeriod == 0:
                                       node.setEnergyPeriod()
                                       #writeLogFile(fileDesc, node, iterNum, elapsedTime, 1) 
                                    
    
                  #end While                  
                  resprint ='['+resprint +' '+ str(elapsedTime)+' ]'   
                  
                  print resprint
                  
                  vec_times.append(elapsedTime)
                  
                  '''WRITE LOG for NODE_ID: x'''
                  #writeOutputFile(fileDesc, Lnodes[node.id], channel, iterNum, elapsedTime, 0)
                  #writeOutputFile(fileDesc, Lnodes[2], channel, iterNum, elapsedTime, 1)
    
              #end for
              '''PLOT CDF...'''
              plot_cdf(vec_times)   
              
              #vec_times.sort()
              #print vec_times
              
              #dfname='./data/AdptV1'+'K'+str(channel)+'.csv'
              
              #write_file(dfname, vec_times)              
            
              discTime = mean(vec_times)#/(1-0.2)
              
              print 'Mean for N =', num_nodes, 'K=',channel,'->', round(discTime, 2),']' 
          #End For  
          fileDesc.close()                                  
      #end for
  #for dutyCycle in dutyCycleVec:
  ###
  fileDesc.close()
  '''comment'''
  ## 
#---------------------------------------------------------------------------
'''======================================================================'''
if __name__ == '__main__':
    
    runSim()      
    
 
'''======================================================================'''
