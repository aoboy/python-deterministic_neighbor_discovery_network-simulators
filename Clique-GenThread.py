#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 15:37:32 2015

@author: gonga
"""

import Queue
import threading

from CliqueSimulation import *

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
                
                print 'Finished processing ',objSim.fname
                self.queue.task_done()
                
def main():
    numRuns   = 300
    Channel   = 1
    numTreads = [5]#range(5,26,5)
    #dutyCycleVec=[(1, 1), (5,5), (10,10)]
    periodsVec=[(133,200)]
    
    for i in range(len(periodsVec)):
        th = Scheduler(mainQueue)
        th.setDaemon(True)
        th.start()        
        
    for num_nodes in numTreads:
        for periods in periodsVec:
            simulation = Simulation(periods, num_nodes, numRuns, Channel)
            
            mainQueue.put(simulation)
            #print 'Queue size is:'        , mainQueue.maxsize
    
    print threading.activeCount(), 'Active Threads running'
    print 'Queue size is:'        , mainQueue.maxsize
    mainQueue.join()
    
'''MAIN Function'''
#main()
if __name__ == "__main__": 
     main()