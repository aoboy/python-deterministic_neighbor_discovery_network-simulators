#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 15:37:32 2015

@author: gonga
"""

import Queue
import threading

from MhopSimulation import *

mainQueue = Queue.Queue()


class Scheduler(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        #print 'Thread created...'
        
    def run(self):
            #print 'Thread Running...'
            while True:
                '''Grab one task and execute it'''
                #print 'Entering Thread....'
                objSim = self.queue.get()
                print 'Processing ',objSim.fname
                objSim.runSim()
                
                #print 'Finished processing ',objSim.fname
                self.queue.task_done()
                
def main():
    numRuns   = 300
    Channel   = 1

    MaxNetworkSize = 50
    periodsVec=[(67,100)]#, (67,133),(67,167),(67,200),(100,200),(133,200), (150,200),(150, 167), (167,200)]
    periodsVec=[((67,100))]
    
    for i in periodsVec:#range(10):
        th = Scheduler(mainQueue)
        th.setDaemon(True)
        th.start()        
        
    for num_nodes in [MaxNetworkSize]:#numTreads:
        for periods in periodsVec:
            simulation = Simulation(periods, num_nodes, numRuns, Channel)
            
            mainQueue.put(simulation)
            #print 'Queue size is:'        , mainQueue.maxsize
    
    print threading.activeCount(), 'Active Threads running'
    
    mainQueue.join()
    
'''MAIN Function'''
main()
#if __name__ == "__main__": 
#     main()