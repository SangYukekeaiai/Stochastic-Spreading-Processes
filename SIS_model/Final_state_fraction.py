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
    mu = 1.0
    lam = 0.04
    eventNumber = 0
    eventItoS = 0
    eventIStoII = 0
    stateI = 0
    stateS = 0
    Ilist = []
    Slist = []
    tlist = []
    start =time.perf_counter()
    tGlobal = 0
    Reject_model.InitGraph(G, mu, lam, EventQ)
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'I':
            stateI += 1
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
            G.nodes[e.srcNode]['state'] = 'S'
            stateS += 1 
            stateI -= 1
            Ilist.append(stateI / numberofnode)
            Slist.append(stateS / numberofnode)
            tlist.append(tGlobal)
            eventNumber += 1
            eventItoS += 1
        else:
            if G.nodes[e.targetNode]['state'] =='S':
                G.nodes[e.targetNode]['state'] = 'I'
                eventNumber += 1
                eventIStoII += 1
                stateS -= 1 
                stateI += 1
                Ilist.append(stateI / numberofnode)
                Slist.append(stateS / numberofnode)
                tlist.append(tGlobal)
                Reject_model.GenerateRecoveryEvent(e.targetNode, mu, tGlobal, EventQ, G)
                Reject_model.GenerateInfectionEvent(e.srcNode, lam, tGlobal, EventQ, G)
                Reject_model.GenerateInfectionEvent(e.targetNode, lam, tGlobal, EventQ, G)
            else:
                Reject_model.GenerateInfectionEvent(e.srcNode, lam, tGlobal, EventQ, G)
    end = time.perf_counter()
    print("Curing events number is: %s"%eventItoS)
    print("Infected events number is: %s"%eventIStoII)
    print('Running time: %s Seconds'%((end-start)/eventNumber))
    print("Recovered node number is: %s"%stateS)
    print("Infected node number is: %s"%stateI)
    plt.figure() 
    I = plt.plot(tlist, Ilist, label = 'I')
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
