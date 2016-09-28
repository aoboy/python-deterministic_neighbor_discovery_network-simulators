#!/usr/bin/env python
# -*- coding: utf-8 -*-
# make a horizontal bar chart
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
      self.T0          = np.random.randint(self.nodePeriod**2/4)      
     
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