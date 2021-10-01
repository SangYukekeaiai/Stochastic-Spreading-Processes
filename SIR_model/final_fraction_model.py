import Reject_model
from queue import PriorityQueue
import networkx as nx
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import math
import time
import sys

class Event(object):
    def __init__(self, state, time, srcNode, targetNode):
        self.state = state
        self.time = time
        self.srcNode = srcNode
        self.targetNode = targetNode
        # print('Event: ', state, time, srcNode, targetNode)

    def __lt__(self, other):
        return self.time < other.time

def percent():
    G = nx.Graph()
    EventQ = PriorityQueue()
    numberofnode = int(1e4)
    MAXNEIGHBORCOUNT = 100
    gamma = -3
    Reject_model.Init_G(numberofnode, G)
    Reject_model.InitNeighbor(MAXNEIGHBORCOUNT, numberofnode, gamma, G)
    mu1 = 0.8
    mu2 = 0.1
    lam = 0.01
    eventNumber = 0
    eventItoR = 0
    eventIStoII = 0
    eventRtoS = 0
    stateI = 0
    stateS = 0
    stateR = 0
    Ilist = []
    Slist = []
    Rlist = []
    tlist = []
    start =time.perf_counter()
    tGlobal = 0
    Reject_model.InitGraph(G, mu1, mu2, lam, EventQ)
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'I':
            stateI += 1
        elif G.nodes[node]['state'] == 'R':
            stateR += 1 
        else:
            stateS += 1

    while True:
        if EventQ.empty():
            break
        e = EventQ.get()
        tGlobal = e.time
        if tGlobal > 10.0:
            break
        if e.state == 'Recovery':
            G.nodes[e.srcNode]['state'] = 'R'
            stateR += 1 
            stateI -= 1
            Ilist.append(stateI / numberofnode)
            Rlist.append(stateR / numberofnode)
            Slist.append(stateS / numberofnode)
            tlist.append(tGlobal)
            eventNumber += 1
            eventItoR += 1
        elif e.state == 'Suspected':
            G.nodes[e.srcNode]['state'] = 'S'
            stateS += 1 
            stateR -= 1
            Ilist.append(stateI / numberofnode)
            Rlist.append(stateR / numberofnode)
            Slist.append(stateS / numberofnode)
            tlist.append(tGlobal)
            eventNumber += 1
            eventRtoS += 1
        else:
            if G.nodes[e.targetNode]['state'] =='S':
                G.nodes[e.targetNode]['state'] = 'I'
                eventNumber += 1
                eventIStoII += 1
                stateS -= 1 
                stateI += 1
                Ilist.append(stateI / numberofnode)
                Slist.append(stateS / numberofnode)
                Rlist.append(stateR / numberofnode)
                tlist.append(tGlobal)
                Reject_model.I_to_R_Event(e.targetNode, mu1, tGlobal, EventQ, G)
                Reject_model.GenerateInfectionEvent(e.srcNode, lam, tGlobal, EventQ, G)
                Reject_model.GenerateInfectionEvent(e.targetNode, lam, tGlobal, EventQ, G)
            else:
                Reject_model.GenerateInfectionEvent(e.srcNode, lam, tGlobal, EventQ, G)
    end = time.perf_counter()
    print("Curing events number is: %s"%eventItoR)
    print("Suspected events number is: %s"%eventRtoS)
    print("Infected events number is: %s"%eventIStoII)
    print('Running time: %s Seconds'%((end-start)/eventNumber))
    print("Recovered node number is: %s"%stateR)
    print("Suspected node number is: %s"%stateS)
    print("Infected node number is: %s"%stateI)
    plt.figure() 
    I = plt.plot(tlist, Ilist, label = 'I')
    S = plt.plot(tlist, Slist, label = 'S')
    R = plt.plot(tlist, Rlist, label = 'R')

    plt.legend()
    plt.xlabel("time(S)")
    plt.ylabel("Fraction")
    plt.show()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    percent()

    return 0

if __name__ == '__main__':
    sys.exit(main())