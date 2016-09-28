#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 13:29:35 2015

@author: gonga
"""

import matplotlib as mpl
import matplotlib.pyplot  as plt
from pylab import *

import math
import numpy as np


from Node import *


class SimUtils:
    
    def __init__(self):
        self.xpto = 0
        #print 'HEREEEEE'
    
    def confidence_interval(self, data, confidence=0.95):
        a = 1.0*np.array(data)
        n = len(a)
        m, se = np.mean(a), sp.stats.stderr(a)
        h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
        return m-h, m, m+h
    #---------------------------------------------------------------------------
    def mean_confidence_interval(self, data, confidence=0.95):
        a = 1.0*np.array(data)
        n = len(a)
        m, se = np.mean(a), sp.stats.sem(a)
        h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
        return m-h, m, m+h
    #---------------------------------------------------------------------------
    def funcProbOf(self, C, N):
        a = N
        b = 2*C+N-1
        c = C
        f2 = (b - np.sqrt(math.pow(b,2)-4*a*c))/(1.0*2*a)
        return f2
    #--------------------------------------------------------------------------
    def loss_p(self, p, n):
        a = 1.0
        for i in range(n):
            a = a*(1-p)
    
        return a
    #---------------------------------------------------------------------------
    def addTopology(self, Xmax, Ymax, Nodes):
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
    def nodesAddCoordinates(self, network, lnodes):
        Lnodes={}
        if len(network) < len(lnodes):
            print 'WARNING:::: COORDINATES VECTOR SMALLER THAN SIZE OF THE NETWORK'
            exit(0)
        print '''==>downloading network topology.....'''
        
        
        plt.axes()
        
        for node, coord in zip(lnodes.values(), network):
                x, y = coord
                #lnodes[node.id].addCoordinates(x,y) 
                #Lnodes[node.id] = lnodes[node.id]
                node.addCoordinates(x,y) 
                Lnodes[node.id] = node
                
        '''add neighbors based on X and Y'''
        print '==>computing neighborhood...'
        
        for nodei in Lnodes.values():
            
            for nodej in lnodes.values():
                if nodei.isNeighbor(nodej):
                    #nodei.neighbors.append(nodej)
                    nodei.neighbors[nodej.id] = nodej
            
            '''PLOT NODE LOCATION'''
            x, y = nodei.xc0, nodei.yc0
            #mpl.patches.Circle(x,y, radius=3, color='red')
            circxy = plt.Circle((x, y), radius = 2, fc='k')#,
            plt.gca().add_patch(circxy)
            plt.text(x-0.5*2, y-0.5*2, str(nodei.id), fontsize=10, color='white')
            
            '''PLOT LINKS'''
            for neighNode in nodei.neighbors.values():
                x = (nodei.xc0, neighNode.xc0)
                y = (nodei.yc0, neighNode.yc0)
                plot(x,y, color='b', linestyle='-', linewidth=0.2)
        
    
        
        xlim([0,100])
        ylim([0,100])
        
    
        
        plt.grid(True)
        title('[100m x 100m]::::::RANDOM NETWORK TOPOLOGY::::::')
        xlabel('X-$axis$ (m)')
        ylabel('Y-$axis$ (m)')            
        #plt.show()
        plt.savefig('n50Topology.pdf', dpi=300, bbox_inches='tight')
    
        return Lnodes    
    #--------------------------------------------------------------------------- 
    def networkUpdate(self, lnodes):
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
            for neighNode in nodei.neighbors1Hop.values():
                
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
        #plt.show()    
        
        #plt.savefig('n50Topology.pdf', dpi=300, bbox_inches='tight')
    #--------------------------------------------------------------------------- 
    def saveTopology(self, fname, listNodes):
        with open(fname, 'w') as fw:
            for ii, node in enumerate(listNodes.values()):
                if ii+1 < len(listNodes):
                    fw.write(str(node.xc0)+',')
                    fw.write(str(node.yc0)+':')
                else:
                    fw.write(str(node.xc0)+',')
                    fw.write(str(node.yc0))                                          
    #---------------------------------------------------------------------------         
    #def readTopology(fname):
    #    with open(fname,'r') as fr:
    #        dt = fr.read().split(':')
    #        #print dt
    #        xx = [(float(x.split(',')[0]),float(x.split(',')[1])) for x in dt]
    #
    #        return xx    
    #---------------------------------------------------------------------------        
    def getLenXhops(self, nodeL, hopCount):
            
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
    def OpenFile(self, fname):
        fd = open(fname, 'w')
        
        return fd        
    #---------------------------------------------------------------------------
    def writeOutputFile(self, fdc, node, channel, iterCount, currTime, operation):
       
       #print 'NODE_ID:', node.id, ' is Writing to file OP:', operation
       ##dc1, dc2 = dutycycle
       if operation == 0:
           energyPeriod = node.getEnergyNode()-node.energyPeriod
           dir1hop,ind1hop,sum1hop = self.getLenXhops(node,1)
           str2Write='>:'+str(iterCount)+','+str(node.id)+','+str(channel)+','
           str2Write+=str(sum1hop)+','+str(dir1hop)+','+str(ind1hop)+',' 
           str2Write+=str(currTime)+','+str(node.getEnergyNode())+','
           str2Write+=str(energyPeriod)+','
           instEnergy = node.getEnergyNode()/currTime
           if instEnergy < 2./node.nodePeriod:
               instEnergy = 2./node.nodePeriod
           str2Write+=str(100.*instEnergy)+','
           str2Write+=str(node.nodePeriod)+'\n'
           '''WRITE 2 FILE'''
           fdc.write(str2Write)
           fdc.flush()
           
       if operation == 2:
           energyPeriod = node.getEnergyNode()-node.energyPeriod
           dir1hop,ind1hop,sum1hop = self.getLenXhops(node,1)
           str2Write='EN>:'+str(iterCount)+','+str(node.id)+','+str(channel)+','
           str2Write+=str(sum1hop)+','+str(dir1hop)+','+str(ind1hop)+',' 
           str2Write+=str(currTime)+','+str(node.getEnergyNode())+','
           str2Write+=str(energyPeriod)+','
           instEnergy = node.getEnergyNode()/currTime
           if instEnergy < 2./node.nodePeriod:
               instEnergy = 2./node.nodePeriod
           str2Write+=str(100.*instEnergy)+','
           str2Write+=str(node.nodePeriod)+'\n'
           '''WRITE 2 FILE'''
           fdc.write(str2Write)
           fdc.flush()           
           
       if operation == 1:
            dir1hop,ind1hop,sum1hop = self.getLenXhops(node,1)
            str2Write='ID:'+str(node.id)+'.'+str(sum1hop)+'->'
            for nj in node.neighbors1Hop.values():
                t0 = node.tKnown[nj.id]
                t1 = node.tConfirmed[nj.id]
                if (t1-t0) > 0:
                    str2Write+='|'+str(nj.id)+','+str(t0)+','+str(t1)
            str2Write+='|\n'
            '''WRITE 2 FILE'''
            fdc.write(str2Write)
            fdc.flush()        
    #--------------------------------------------------------------------------- 
    def writeEnergyFile(self, node, interCount, currTime):
        ''''''
    #---------------------------------------------------------------------------             
    '''Create all nodes in the Network'''
    def createNodes(self, n, channelLen, dcycle):
        lnodes={}
        for i in range(1, n+1):
            
            node = Node(i,n, dcycle)
            #channel = rsObj.randint(channelLen) #i%channelLen
            channel = i%channelLen
            #ownSlot = 1 + i%(T_period-1)
            node.addChannel(channel)
                    
            lnodes[i]= node
            
        return lnodes
    #---------------------------------------------------------------------------
    def flushIds(self, Lnodes):
        for i, node in enumerate(Lnodes.values()):
           Lnodes[node.id].flushNeighbors()
           #Lnodes[node.id].networkVec    = []    
           #Lnodes[node.id].notKnownNeigh = []
           #Lnodes[node.id].neighbors1Hop = []  
           
           #Lnodes[node.id].networkVec.append(node)
    #---------------------------------------------------------------------------
    def printNeighbors(self, Lnodes):
        print 'GONGAAAAA'
        for node in Lnodes.values():
            print 'NodeID:', node.id, 'Neighbors: ',
            #for n in node.neighbors1Hop:
            if 1:
                #print n.id,
                a = [nh.id for nh in node.neighbors.values()]
                print a
                #print self.getLenXhops(node, 1), len(node.networkVec)
               
        #print '\n'
    #---------------------------------------------------------------------------
    '''returns True if every node have discovered all its neighbors '''
    def all2allComplete(self, Lnodes):
        for node in Lnodes.values():
            if node.allNetworkDiscovered() == False:
                return False
        return True
    #---------------------------------------------------------------------------
    def allNeighborsDiscovered(self, Lnodes):
        #vec90pComplete=[]
        for node in Lnodes.values():
            if node.allNeighborsDiscovered() == False:
                return False
        return True

    #---------------------------------------------------------------------------    
    def plot_cdf(self, a):
        a.sort()
        yvals=np.arange(len(a))/float(len(a))
        plt.plot(a, yvals )  
        
        grid(True)
        #plt.close()
        ylabel('CDF')
        xlabel('Worst case Latency (slots)')
        plt.show()
    #---------------------------------------------------------------------------
    def write_file(self, fname, a):
        with open(fname,'w') as fw:
            for i, val in enumerate(a):
                if i+1 < len(a):
                    fw.write(str(val)+',')
                else:
                    fw.write(str(val))
    #---------------------------------------------------------------------------
    def read_file(self, fname):
        with open(fname,'r') as fr:    
            dt = fr.read().split(',')
            xx =[int(x) for x in dt]
            return xx                                       
    #---------------------------------------------------------------------------         
    def readTopology(self, fname):
        with open(fname,'r') as fr:
            dt = fr.read().split(':')
            #print dt
            xx = [(float(x.split(',')[0]),float(x.split(',')[1])) for x in dt]
    
            return xx
    #---------------------------------------------------------------------------                  
    #---------------------------------------------------------------------------  
    def isAnchorSlot(self, node, t):
            retVal = False
            retVal = (node.T0 + t)%node.nodePeriod == 0 
            #retVal = retVal or (node.T0 + t-1)%node.nodePeriod == 0   
            return retVal
    #---------------------------------------------------------------------------         