# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 13:16:29 2013

@author: gonga
"""
import numpy as np


min_speed = 1
max_speed = 5

global distOffset
distOffset = 20


Xmin_GRID = distOffset
Xmax_GRID = 100-distOffset
Ymin_GRID = Xmin_GRID
Ymax_GRID = Xmax_GRID

pos = np.arange(distOffset, Xmax_GRID, 5)

xco = np.arange(0, 101, 0.1)
yco = np.arange(0, 101, 0.1)

G0Pos0XMin = 45
G0Pos0XMax = 55

G0Pos0YMin = 0
G0Pos0YMax = 10

G1Pos1XMin = 45
G1Pos1XMax = 55

G1Pos1YMin = 90
G1Pos1YMax = 100


G12Pos2XMin = 45
G12Pos2XMax = 55
G12Pos2YMin = 45
G12Pos2YMax = 55

class Node:
    def __init__(self, nodeId):
        self.id = nodeId
        self.X  = 0
        self.Y  = 0
        xx = 0
        yy = 0
        if self.id in range(0,13):
            xx = [i for i in xco if i >=0 and i <= 10]
            yy = [i for i in xco if i >=0  and i <= 10]
        else:
            xx = [i for i in xco if i >=90 and i <= 100]
            yy = [i for i in xco if i >=90  and i <= 100]
            
        self.X = np.random.choice(yy)
        self.Y = np.random.choice(xx)
        
        self.points = 1
        self.path   = []
        
        pstr = str(nodeId)+' 0.0 '+str(self.X)+' '+str(self.Y)+'\n'
        self.path.append(pstr)
        
    def addpath(self, path_str):
        self.path.append(path_str)
        
        
    def addCentralCoord(self, t):
        x = np.random.randint(40,60) + np.random.random(1)[0]
        y = np.random.randint(40,60) + np.random.random(1)[0]
        
        #10412:260300
        pstr = str(self.id)+' '+str(t)+' '+str(x)+' '+str(y)+'\n'
        self.path.append(pstr)        
        
    def set_coornidates(self, decision):
        tmp_x =  0
        tmp_y =  0
        
        if decision == 0: 
            self.X  = self.X
            self.Y  = self.Y
        if decision == 1:
            self.X  = self.X
            tmp_y   = self.Y - distOffset
            if tmp_y >= Ymin_GRID:
                self.Y = tmp_y
        if decision == 2:
            tmp_y   = self.Y - distOffset
            tmp_x   = self.X + distOffset
            if tmp_y >= Ymin_GRID:
                self.Y = tmp_y
            if tmp_x <= Xmax_GRID:
                self.X = tmp_x
        if decision == 3:            
            tmp_x   = self.X + distOffset
            if tmp_x <= Xmax_GRID:
                self.X = tmp_x 
        if decision == 4:
            tmp_y   = self.Y + distOffset
            tmp_x   = self.X + distOffset
            if tmp_y <= Ymax_GRID:
                self.Y = tmp_y
            if tmp_x <= Xmax_GRID:
                self.X = tmp_x   
        if decision == 5:
            tmp_y   = self.Y + 5
            if tmp_y <= Ymax_GRID:
                self.Y = tmp_y
        if decision == 6:
            tmp_y   = self.Y + distOffset
            tmp_x   = self.X - distOffset
            if tmp_y <= Ymax_GRID:
                self.Y = tmp_y
            if tmp_x >= Xmin_GRID:
                self.X = tmp_x            
        if decision == 7:
            tmp_x   = self.X - distOffset
            if tmp_x >= Xmin_GRID:
                self.X = tmp_x            
        if decision == 8:
            tmp_y   = self.Y - distOffset
            tmp_x   = self.X - distOffset
            if tmp_y >= Ymin_GRID:
                self.Y = tmp_y
            if tmp_x >= Xmin_GRID:
                self.X = tmp_x            
        
    def move(self, simul_time):
        decision = np.random.randint(0, 9)        
        self.set_coornidates(decision)
        
        pstr = str(self.id)+' '+str(simul_time)+' '+str(self.X)+' '+str(self.Y)+'\n'
        
        self.addpath(pstr)

def path_generator(num_nodes, vecTimes):
    nodesList = {}
    for id in range(num_nodes):
        nodesList[id] = Node(id)

    for t in vecTimes:
        for node in nodesList.values():
            node.addCentralCoord(t)
            
    return nodesList

def create_file(fname):
    csv_file = open(fname, 'wb')        
    return csv_file
    
if __name__ == '__main__':
    
     fileName = './positions.dat'  
     csvFd = create_file(fileName)   
        
     node_speed = 5
     num_nodes  = 25
     num_points = 2
     
     distOffset = 20

     vecTimes=[260,480]
     
     nodesL = path_generator(num_nodes, vecTimes)
     
     #vecTimes=[10,20,30,40]
     
     for idx in range(len(vecTimes)+1):
         for node in nodesL.values():
             val = node.path[idx]
             print val,
             csvFd.write(val)
             csvFd.flush()
     
     csvFd.close()