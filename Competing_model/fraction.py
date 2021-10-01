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
    mu1 = 1.2
    mu2 = 2.1
    lam1 = 0.04
    lam2 = 0.05
    eventNumber = 0
    eventItoS = 0
    eventJtoS = 0
    eventSItoII = 0
    eventSJtoJJ = 0
    stateI = 0
    stateJ = 0
    stateS = 0
    Ilist = []
    Jlist = []
    Slist = []
    tlist = []
    start =time.perf_counter()
    tGlobal = 0
    Reject_model.InitGraph(G, lam1, lam2, mu1, mu2, EventQ)
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'I':
            stateI += 1
        elif G.nodes[node]['state'] == 'J':
            stateJ += 1
        else:
            stateS += 1 

    while True:
        if EventQ.empty():
            break
        e = EventQ.get()
        tGlobal = e.time
        if tGlobal > 10.0:
            break
        if e.state == 'RI':
            G.nodes[e.srcNode]['state'] = 'S'
            G.nodes[e.srcNode]['recoveryTime'] = 0
            stateS += 1 
            stateI -= 1
            Ilist.append(stateI / numberofnode)
            Slist.append(stateS / numberofnode)
            Jlist.append(stateJ / numberofnode)
            tlist.append(tGlobal)
            eventNumber += 1
            eventItoS += 1
        elif e.state == 'RJ':
            G.nodes[e.srcNode]['state'] = 'S'
            G.nodes[e.srcNode]['recoveryTime'] = 0
            stateS += 1
            stateJ -= 1
            Ilist.append(stateI / numberofnode)
            Slist.append(stateS / numberofnode)
            Jlist.append(stateJ / numberofnode)
            tlist.append(tGlobal)
            eventNumber += 1
            eventJtoS += 1
        elif e.state == 'I_Infection':
            if G.nodes[e.targetNode]['state'] == 'S':
                stateI += 1
                Ilist.append(stateI / numberofnode)
                stateS -= 1
                Slist.append(stateS / numberofnode)
                Jlist.append(stateJ / numberofnode)
                tlist.append(tGlobal)
                G.nodes[e.targetNode]['state'] = 'I'
                eventNumber += 1
                Reject_model.R_FROM_I_EVENT(e.targetNode, mu1, tGlobal, EventQ, G)
                Reject_model.GET_I_EVENT(e.srcNode, lam1, tGlobal, EventQ, G)
                Reject_model.GET_I_EVENT(e.targetNode, lam1, tGlobal, EventQ, G) 
                eventSItoII += 1               
            else:
                Reject_model.GET_I_EVENT(e.srcNode, lam1, tGlobal, EventQ, G)
        elif e.state == 'J_Infection':
            if G.nodes[e.targetNode]['state'] == 'S':
                stateJ += 1
                Jlist.append(stateJ / numberofnode)
                stateS -= 1
                Slist.append(stateS / numberofnode)
                Ilist.append(stateI / numberofnode)
                tlist.append(tGlobal)
                G.nodes[e.targetNode]['state'] = 'J'
                eventNumber += 1
                Reject_model.R_FROM_J_EVENT(e.targetNode, mu2, tGlobal, EventQ, G)
                Reject_model.GET_J_EVENT(e.srcNode, lam2, tGlobal, EventQ, G)
                Reject_model.GET_J_EVENT(e.targetNode, lam2, tGlobal, EventQ, G)
                eventSJtoJJ += 1
            else:
                Reject_model.GET_J_EVENT(e.srcNode, lam2, tGlobal, EventQ, G)
        else:
            raise ValueError("Unplanned Event")
    end = time.perf_counter()
    print("Curing from I events number is: %s"%eventItoS)
    print("Infected events from I number is: %s"%eventSItoII)
    print("Curing from I events number is: %s"%eventJtoS)
    print("Infected events from J number is: %s"%eventSJtoJJ)
    print('Running time: %s Seconds'%((end-start)/eventNumber))
    print("Recovered node number is: %s"%stateS)
    print("Infected I node number is: %s"%stateI)
    print("Infected J node number is: %s"%stateJ)
    plt.figure() 
    I = plt.plot(tlist, Ilist, label = 'I')
    J = plt.plot(tlist, Jlist, label = 'J')
    S = plt.plot(tlist, Slist, label = 'S')

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
