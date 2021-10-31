from queue import PriorityQueue
import networkx as nx
import random
import numpy as np
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


def Init_G(numberofnode, G):
    biState = np.random.binomial(1,  0.96,  numberofnode)
    for i in range(numberofnode):
        if biState[i] == 0:
            biState[i] = np.random.binomial(1, 0.5, 1)
            if biState[i] == 0:
                state = 'J'
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


def InitGraph(G, lam1, lam2, mu1, mu2, EventQ):
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'I':
            R_FROM_I_EVENT(node, mu1, 0, EventQ, G)
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'J':
            R_FROM_J_EVENT(node, mu2, 0, EventQ, G)    
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'I':
            GET_I_EVENT(node, lam1, 0, EventQ, G)
    for node in G.__iter__():
        if G.nodes[node]['state'] == 'J':
            GET_J_EVENT(node, lam2, 0, EventQ, G)

def R_FROM_I_EVENT(node, mu1, tGlobal, EventQ, G):
    tEvent = tGlobal + np.random.exponential(mu1)
    e = Event(state = 'RI' ,  time = tEvent,  srcNode = node,  targetNode = None)
    G.nodes[node]['recoveryTime'] = tEvent
    EventQ.put(e)

def R_FROM_J_EVENT(node, mu2, tGlobal, EventQ, G):
    tEvent = tGlobal + np.random.exponential(mu2)
    e = Event(state = 'RJ' ,  time = tEvent,  srcNode = node,  targetNode = None)
    G.nodes[node]['recoveryTime'] = tEvent
    EventQ.put(e)

def GET_I_EVENT(node, lam1, tGlobal, EventQ, G):
    tEvent = tGlobal
    rate = lam1*G.nodes[node]['neighborNumber']
    while True:
        tEvent += np.random.exponential(rate)
        if G.nodes[node]['recoveryTime'] < tEvent:
            break
        attackedNode = random.choice(list(G.neighbors(node)))
        if G.nodes[attackedNode]['state'] == 'S' or G.nodes[attackedNode]['recoveryTime'] < tEvent:
            e = Event(state = 'I_Infection' ,  time = tEvent,  srcNode = node,  targetNode = attackedNode)
            EventQ.put(e)
            break

def GET_J_EVENT(node, lam2, tGlobal, EventQ, G):
    tEvent = tGlobal
    rate = lam2*G.nodes[node]['neighborNumber']
    while True:
        tEvent += np.random.exponential(rate)
        if G.nodes[node]['recoveryTime'] < tEvent:
            break
        attackedNode = random.choice(list(G.neighbors(node)))
        if G.nodes[attackedNode]['state'] == 'S' or G.nodes[attackedNode]['recoveryTime'] < tEvent:
            e = Event(state = 'J_Infection' ,  time = tEvent,  srcNode = node,  targetNode = attackedNode)
            EventQ.put(e)
            break

def trans_data_list():
    node_numberlist = range(10000,110000,10000)
    gamma_list = [-2,-3]
    timelist = []
    for gamma in gamma_list:
        for numberofnode in node_numberlist:
            G = nx.Graph()
            EventQ = PriorityQueue()
            mu1 = 0.6
            mu2 = 0.7
            lam1 = 0.6
            lam2 = 0.63 
            MAXNEIGHBORCOUNT = 100
            Init_G(numberofnode, G)
            InitNeighbor(MAXNEIGHBORCOUNT, numberofnode, gamma, G)
            eventNumber = 0
            start =time.perf_counter()
            InitGraph(G, lam1, lam2, mu1, mu2, EventQ)
            tGlobal = 0

            while True:
                if EventQ.empty():
                    break
                e = EventQ.get()
                tGlobal = e.time
                if tGlobal > 2.0:
                    break
                if e.state == 'RI':
                    G.nodes[e.srcNode]['state'] = 'S'
                    eventNumber += 1
                    G.nodes[e.srcNode]['recoveryTime'] = 0
                elif e.state == 'RJ':
                    G.nodes[e.srcNode]['state'] = 'S'
                    eventNumber += 1
                    G.nodes[e.srcNode]['recoveryTime'] = 0
                elif e.state == 'I_Infection':
                    if G.nodes[e.targetNode]['state'] == 'S':
                        G.nodes[e.targetNode]['state'] = 'I'
                        eventNumber += 1
                        R_FROM_I_EVENT(e.targetNode, mu1, tGlobal, EventQ, G)
                        GET_I_EVENT(e.srcNode, lam1, tGlobal, EventQ, G)
                        GET_I_EVENT(e.targetNode, lam1, tGlobal, EventQ, G)
                    else:
                        GET_I_EVENT(e.srcNode, lam1, tGlobal, EventQ, G)
                elif e.state == 'J_Infection':
                    if G.nodes[e.targetNode]['state'] == 'S':
                        G.nodes[e.targetNode]['state'] = 'J'
                        eventNumber += 1
                        R_FROM_J_EVENT(e.targetNode, mu2, tGlobal, EventQ, G)
                        GET_J_EVENT(e.srcNode, lam2, tGlobal, EventQ, G)
                        GET_J_EVENT(e.targetNode, lam2, tGlobal, EventQ, G)
                    else:
                        GET_J_EVENT(e.srcNode, lam2, tGlobal, EventQ, G)
                else:
                    raise ValueError("Unplanned Event")

            end = time.perf_counter()
            timelist.append((end-start)/eventNumber)
            print('%s node Running time in gamma %s : %s Seconds' %(numberofnode, gamma, ((end-start)/eventNumber)))
    return timelist

# def fraction():
#     G = nx.Graph()
#     EventQ = PriorityQueue()
#     mu1 = 0.6
#     mu2 = 0.7
#     lam1 = 0.03
#     lam2 = 0.04 
#     numberofnode = int(1e4)
#     MAXNEIGHBORCOUNT = 100
#     gamma = -3
#     Icount = 0
#     Ilist = []
#     Jcount = 0
#     Jlist = []
#     Scount = 0
#     Slist = []
#     tlist = []
#     Init_G(numberofnode, G)
#     for node in G.__iter__():
#         if G.nodes[node]['state'] == 'I':
#             Icount += 1
#         elif G.nodes[node]['state'] == 'J':
#             Jcount += 1
#         else:
#             Scount += 1
    
#     InitNeighbor(MAXNEIGHBORCOUNT, numberofnode, gamma, G)
#     eventNumber = 0
#     start =time.perf_counter()
#     InitGraph(G, lam1, lam2, mu1, mu2, EventQ)
#     tGlobal = 0

#     while True:
#         if EventQ.empty():
#             break
#         e = EventQ.get()
#         tGlobal = e.time
#         if tGlobal > 10.0:
#             break
#         if e.state == 'RI':
#             Icount -= 1
#             Ilist.append(Icount)
#             Scount += 1
#             Slist.append(Scount)
#             Jlist.append(Jcount)
#             tlist.append(tGlobal)
#             G.nodes[e.srcNode]['state'] = 'S'
#             eventNumber += 1
#             G.nodes[e.srcNode]['recoveryTime'] = 0
#         elif e.state == 'RJ':
#             Jcount -= 1
#             Jlist.append(Icount)
#             Scount += 1
#             Slist.append(Scount)
#             Ilist.append(Icount)
#             tlist.append(tGlobal)
#             G.nodes[e.srcNode]['state'] = 'S'
#             eventNumber += 1
#             G.nodes[e.srcNode]['recoveryTime'] = 0
#         elif e.state == 'I_Infection':
#             if G.nodes[e.targetNode]['state'] == 'S':
#                 Icount += 1
#                 Ilist.append(Icount)
#                 Scount -= 1
#                 Slist.append(Scount)
#                 Jlist.append(Jcount)
#                 tlist.append(tGlobal)
#                 G.nodes[e.targetNode]['state'] = 'I'
#                 eventNumber += 1
#                 R_FROM_I_EVENT(e.targetNode, mu1, tGlobal, EventQ, G)
#                 GET_I_EVENT(e.srcNode, lam1, tGlobal, EventQ, G)
#                 GET_I_EVENT(e.targetNode, lam1, tGlobal, EventQ, G)
#             else:
#                 GET_I_EVENT(e.srcNode, lam1, tGlobal, EventQ, G)
#         elif e.state == 'J_Infection':
#             if G.nodes[e.targetNode]['state'] == 'S':
#                 Jcount += 1
#                 Jlist.append(Jcount)
#                 Scount -= 1
#                 Slist.append(Scount)
#                 Ilist.append(Icount)
#                 tlist.append(tGlobal)
#                 G.nodes[e.targetNode]['state'] = 'J'
#                 eventNumber += 1
#                 R_FROM_J_EVENT(e.targetNode, mu2, tGlobal, EventQ, G)
#                 GET_J_EVENT(e.srcNode, lam2, tGlobal, EventQ, G)
#                 GET_J_EVENT(e.targetNode, lam2, tGlobal, EventQ, G)
#             else:
#                 GET_J_EVENT(e.srcNode, lam2, tGlobal, EventQ, G)
#         else:
#             raise ValueError("Unplanned Event")
    
#     print(Icount)
#     print(Jcount)
#     print(Scount)
#     plt.figure() 
    
#     J = plt.plot(tlist, Jlist, label = 'J')
#     I = plt.plot(tlist, Ilist, label = 'I')
#     S = plt.plot(tlist, Slist, label = 'S')

#     plt.legend()
#     plt.xlabel("time(S)")
#     plt.ylabel("Fraction")
#     plt.show()

# fraction()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    G = nx.Graph()
    EventQ = PriorityQueue()
    mu1 = 0.6
    mu2 = 0.7
    lam1 = 0.6
    lam2 = 0.63 
    numberofnode = int(1e4)
    MAXNEIGHBORCOUNT = 100
    gamma = -3
    Init_G(numberofnode, G)
    InitNeighbor(MAXNEIGHBORCOUNT, numberofnode, gamma, G)
    eventNumber = 0
    start =time.perf_counter()
    InitGraph(G, lam1, lam2, mu1, mu2, EventQ)
    tGlobal = 0

    while True:
        if EventQ.empty():
            break
        e = EventQ.get()
        tGlobal = e.time
        if tGlobal > 2.0:
            break
        if e.state == 'RI':
            G.nodes[e.srcNode]['state'] = 'S'
            eventNumber += 1
            G.nodes[e.srcNode]['recoveryTime'] = 0
        elif e.state == 'RJ':
            G.nodes[e.srcNode]['state'] = 'S'
            eventNumber += 1
            G.nodes[e.srcNode]['recoveryTime'] = 0
        elif e.state == 'I_Infection':
            if G.nodes[e.targetNode]['state'] == 'S':
                G.nodes[e.targetNode]['state'] = 'I'
                eventNumber += 1
                R_FROM_I_EVENT(e.targetNode, mu1, tGlobal, EventQ, G)
                GET_I_EVENT(e.srcNode, lam1, tGlobal, EventQ, G)
                GET_I_EVENT(e.targetNode, lam1, tGlobal, EventQ, G)
            else:
                GET_I_EVENT(e.srcNode, lam1, tGlobal, EventQ, G)
        elif e.state == 'J_Infection':
            if G.nodes[e.targetNode]['state'] == 'S':
                G.nodes[e.targetNode]['state'] = 'J'
                eventNumber += 1
                R_FROM_J_EVENT(e.targetNode, mu2, tGlobal, EventQ, G)
                GET_J_EVENT(e.srcNode, lam2, tGlobal, EventQ, G)
                GET_J_EVENT(e.targetNode, lam2, tGlobal, EventQ, G)
            else:
                GET_J_EVENT(e.srcNode, lam2, tGlobal, EventQ, G)
        else:
            raise ValueError("Unplanned Event")

    end = time.perf_counter()
    print('Running time: %s Seconds'%((end-start)/eventNumber))

    return 0

if __name__ == '__main__':
    sys.exit(main())
