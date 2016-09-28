#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 13:32:24 2015

@author: gonga
"""

import numpy as np
from numpy import mean
from scipy import stats
import scipy as sp


import SimUtils as auxFuncs

from SimUtils import *


from Node import *

class Simulation:
    def __init__(self, periods, num_nodes, numRuns, Channel):
        
        self.periods = periods
        self.num_nodes = num_nodes
        self.fname     = './sim-data/GThdClique_N'+str(num_nodes)
        self.dc1       = 0
        self.dc2       = 0
        self.numRuns   = numRuns
        self.channel   = Channel
        
        self.utils = auxFuncs.SimUtils()        
        
        strName= 'T'
        for p in periods:
            strName=strName+'_'+str(p)
  
        self.fname = self.fname + strName+'.csv'
    
    def OpenFile(self, fname):
        fd = open(fname, 'w')
        
        return fd 
          
    def runSim(self):
           
            utils = self.utils
            
            nodePeriod = max(self.periods)
            upperBound = (nodePeriod**2)/2+ nodePeriod/4                        
            
            '''Open Output File'''
            fileDesc = self.OpenFile(self.fname)  
            
            '''Holds the worst case latencyes'''
            vec_times = []
            
            print 'running Thread for :',upperBound, 'slots' 
            
            for iterNum  in range(self.numRuns):
                '''elapsed time.. time already spent running the simulation'''                
                elapsedTime = 0
                
                '''clear old values  before next round'''
                #utils.flushIds(Lnodes)
                Lnodes  = {}
                del Lnodes
                Lnodes  = utils.createNodes(self.num_nodes, self.channel , self.periods)
                
                #while utils.all2allComplete(Lnodes) == False:
                while utils.allNeighborsDiscovered(Lnodes) == False:
                #while elapsedTime < upperBound:  
                    
                    '''increment elapsed time.. '''
                    elapsedTime = elapsedTime + 1 
                    
                    '''activate nodes..based on their random start time...'''
                    for node in Lnodes.values():
                            node.isActive(elapsedTime)

                    '''List of transmitter nodes.. '''
                    txNodes=[node for node in Lnodes.values() if node.isSlotTx(elapsedTime) == True]
                    
                    if len(txNodes) >= 2:
                        '''There are at leat two nodes that are overlaped'''
                        
                        for txNo in txNodes:                                
                            for lnode in txNodes:
                                if txNo.id != lnode.id and txNo.isNeighbor(lnode):                                        
                                    lnode.disseminate(txNo, elapsedTime)
                        
                        for node in Lnodes.values():
                            if node.id == 1 or node.id == 2:
                                if node.len1hop < len(node.neighbors1Hop):
                                    node.len1hop = len(node.neighbors1Hop)
                                    utils.writeOutputFile(fileDesc, node, self.channel, iterNum, elapsedTime, 0)
                                
                    for node in Lnodes.values():
                        if node.id == 1 or node.id == 2:
                            #isAnchor = (node.T0+elapsedTime)%node.nodePeriod == 0
                            isAnchor = utils.isAnchorSlot(node, elapsedTime)
                            
                            if isAnchor:
                                 '''Report energy usage'''
                                 node.len1hop = len(node.neighbors1Hop)
                                 utils.writeOutputFile(fileDesc, node, self.channel, iterNum, elapsedTime, 2)
                                 node.energyPeriod = node.getEnergyNode()
                    
                    #End of For node in Lnodes.values():
                #END OF WHILE   
                vec_times.append(elapsedTime)    
            #END OF FOR  iterNum  in range(self.numRuns):
            
            '''Do something else'''
            fileDesc.close()              
            
            #utils.plot_cdf(vec_times)  
            
            #vec_times.sort()
            #print vec_times
            
            discTime = mean(vec_times)
            
            print 'Mean for [N =', self.num_nodes, 'K=',self.channel,'->', round(discTime, 2),']' 
            
'''========================================================================='''                    
                    





















