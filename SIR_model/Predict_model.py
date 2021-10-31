from queue import PriorityQueue
import networkx as nx
import random
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import time
import math
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


def Init_G(numberofnode, G):
    biState = np.random.binomial(1, 0.96, numberofnode)
    for i in range(numberofnode):
        if biState[i] == 0:
            biState[i] = np.random.binomial(1, 0.5, 1)
            if biState[i] == 0:
                state = 'R'
            else:
                state = 'I'
        elif biState[i] == 1:
            state = 'S'
        else:
            raise ValueError("State out of bound")
        G.add_nodes_from([
            (i, {'state':state, 'neighborNumber': 0, 'recoveryTime':0})
        ])


def InitNeighbor(MAXNEIGHBORCOUNT, numberofnode, gamma, G):
    sumOfProb = 0
    for neighborNumber in range(3, MAXNEIGHBORCOUNT+1):
        sumOfProb += math.pow(neighborNumber, gamma)

    distribution = [None]*(MAXNEIGHBORCOUNT+1)
    distribution[0] = 0
    distribution[1] = 0
    distribution[2] = 0
    for neighborNumber in range(3, MAXNEIGHBORCOUNT+1):
        distribution[neighborNumber] = int(math.pow(neighborNumber, gamma)/sumOfProb * numberofnode)
    RESTNUMBER = numberofnode - sum(distribution)
    distribution[3] = distribution[3]+RESTNUMBER

    nodeid = 0
    for i in range(len(distribution)):
        if distribution[i] == 0:
            continue
        else:
            while(distribution[i] != 0):
                G.nodes[nodeid]['neighborNumber'] = i
                distribution[i] = distribution[i] - 1
                nodeid = nodeid + 1
    for node in G.__iter__():
        if len(list(G.neighbors(node))) >= G.nodes[node]['neighborNumber']:
            continue
        else:
            neighborNumberToChoose = G.nodes[node]['neighborNumber'] - len(list(G.neighbors(node)))
            if node == numberofnode-1:
                break
            for i in range(neighborNumberToChoose):
                neighborNew = random.choice(range(node+1, numberofnode))
                while (G.nodes[neighborNew]['neighborNumber'] <= len(list(G.neighbors(neighborNew)))):
                    if len(list(G.neighbors(node))) >= 3 and len(range(node+1, numberofnode)) <= 10:
                        neighborNew = numberofnode
                        break
                    neighborNew = random.choice(range(node+1, numberofnode))
                    # continue
                if neighborNew != numberofnode:
                    G.add_edge(node, neighborNew)


def InitGraph(G, mu1, mu2, lam, EventQ):
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'I':
            I_to_R_Event(node, mu1, 0, EventQ, G)
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'R':
            R_to_S_Event(node, mu2, 0, EventQ, G)
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'I':
            GenerateInfectionEvent(node, lam, 0, EventQ, G) 

def I_to_R_Event(node, mu1, tGlobal, EventQ, G):
    tEvent = tGlobal + np.random.exponential(mu1)
    e = Event(state = 'Recovery' ,    time = tEvent,    srcNode = node,    targetNode = None)
    G.nodes[node]['Time'] = tEvent 
    EventQ.put(e)

def R_to_S_Event(node, mu2, tGlobal, EventQ, G):
    tEvent = tGlobal + np.random.exponential(mu2)
    e = Event(state = 'Suspected' ,    time = tEvent,    srcNode = node,    targetNode = None)
    G.nodes[node]['Time'] = tEvent 
    EventQ.put(e)

def GenerateInfectionEvent(node, lam, tGlobal, EventQ, G):
    tEvent = tGlobal
    rate = lam*G.nodes[node]['neighborNumber']
    while True:
        tEvent += np.random.exponential(rate)
        if tEvent > G.nodes[node]['Time']:
            break
        attackedNode = random.choice(list(G.neighbors(node)))
        if G.nodes[attackedNode]['state'] == 'I':
            break
        if G.nodes[attackedNode]['state'] == 'S' or (G.nodes[attackedNode]['state'] == 'R' and G.nodes[attackedNode]['Time'] < tEvent):
            e = Event(state = 'Infection', time = tEvent, srcNode = node, targetNode = attackedNode)
            EventQ.put(e)
            break

def trans_data_list():
    node_numberlist = range(10000,110000,10000)
    gamma_list = [-2,-3]
    timelist = []
    mu1 = 1.1
    mu2 = 0.3
    lam = 0.6
    for gamma in gamma_list:
        for numberofnode in node_numberlist:
            G = nx.Graph()
            EventQ = PriorityQueue()
            MAXNEIGHBORCOUNT = 100
            Init_G(numberofnode, G)
            InitNeighbor(MAXNEIGHBORCOUNT, numberofnode, gamma, G)
            eventNumber = 0
            start =time.perf_counter()
            tGlobal = 0
            InitGraph(G, mu1, mu2, lam, EventQ)
    
            while True:
                if EventQ.empty():
                    break
                e = EventQ.get()
                tGlobal = e.time
                if tGlobal > 2.0:
                    break
                if e.state == 'Recovery':
                    G.nodes[e.srcNode]['state'] = 'R'
                    eventNumber += 1
                    R_to_S_Event(e.srcNode, mu2, tGlobal, EventQ, G)
                elif e.state == 'Suspected':
                    G.nodes[e.srcNode]['state'] = 'S'
                    eventNumber += 1
                    G.nodes[e.srcNode]['Time'] = 0
                else:
                    G.nodes[e.targetNode]['state'] = 'I'
                    eventNumber += 1
                    I_to_R_Event(e.targetNode, mu1, tGlobal, EventQ, G)
                    GenerateInfectionEvent(e.srcNode, lam, tGlobal, EventQ, G)
                    GenerateInfectionEvent(e.targetNode, lam, tGlobal, EventQ, G)
            end = time.perf_counter()
            timelist.append((end-start)/eventNumber)
            print('%s node Running time in gamma %s : %s Seconds' %(numberofnode, gamma, ((end-start)/eventNumber)))
    return timelist

# trans_data_list()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    G = nx.Graph()
    EventQ = PriorityQueue()
    mu1 = 1.1
    mu2 = 0.3
    lam = 0.6
    gamma = -3
    numberofnode = int(1e4)
    MAXNEIGHBORCOUNT = 100
    Init_G(numberofnode, G)
    InitNeighbor(MAXNEIGHBORCOUNT, numberofnode, gamma, G)
    eventNumber = 0
    start =time.perf_counter()
    tGlobal = 0
    InitGraph(G, mu1, mu2, lam, EventQ)
    
    while True:
        if EventQ.empty():
            break
        e = EventQ.get()
        tGlobal = e.time
        if tGlobal > 2.0:
            break
        if e.state == 'Recovery':
            G.nodes[e.srcNode]['state'] = 'R'
            eventNumber += 1
            R_to_S_Event(e.srcNode, mu2, tGlobal, EventQ, G)
        elif e.state == 'Suspected':
            G.nodes[e.srcNode]['state'] = 'S'
            eventNumber += 1
            G.nodes[e.srcNode]['Time'] = 0
        else:
            G.nodes[e.targetNode]['state'] = 'I'
            eventNumber += 1
            I_to_R_Event(e.targetNode, mu1, tGlobal, EventQ, G)
            GenerateInfectionEvent(e.srcNode, lam, tGlobal, EventQ, G)
            GenerateInfectionEvent(e.targetNode, lam, tGlobal, EventQ, G)
    
    end = time.perf_counter()
    print(eventNumber)
    print('Running time: %s Seconds'%((end-start)/eventNumber))

    return 0

if __name__ == '__main__':
    sys.exit(main())
