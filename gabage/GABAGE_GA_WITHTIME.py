import networkx as nx
import random
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import math
import time
import sys


G = nx.Graph()
ListI = []
ListSI = []
lam = 0.6
mu = 1.0
global tGlobal
tGlobal = 0
c = 0
NUMBEROFNODE = int(1e4)
MAXNEIGHBORCOUNT = 100


def Init_Data(G,ListI):
    biState = np.random.binomial(1, 0.95,NUMBEROFNODE)
    for node in range(NUMBEROFNODE):
        G.add_node(node)
        if biState[node] == 0:
            ListI.append(node)
        

def Init_ListSI(G,ListI,ListSI):
    sumOfProb = 0
    for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
        sumOfProb += math.pow(neighborNumber,-2)

    distribution = [None]*(MAXNEIGHBORCOUNT+1)
    distribution[0] = 0
    distribution[1] = 0
    distribution[2] = 0
    for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
        distribution[neighborNumber] = int(math.pow(neighborNumber,-2)/sumOfProb * NUMBEROFNODE)
    RESTNUMBER = NUMBEROFNODE - sum(distribution)
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
            if node == NUMBEROFNODE-1:
                break
            for i in range(neighborNumberToChoose):
                neighborNew = random.choice(range(node+1,NUMBEROFNODE))
                if (G.nodes[neighborNew]['neighborNumber'] <= len(list(G.neighbors(neighborNew)))):
                    continue
                # neighborNew = random.choice(range(node+1,NUMBEROFNODE))
                G.add_edge(node,neighborNew)
                if node in ListI and neighborNew not in ListI:
                    ListSI.append([node,neighborNew])
    global c
    c = mu*len(ListI)+lam*len(ListSI)
    # print(c)

def chooseEvent(lam,mu,ListI,ListSI):
    global c    
    while c != 0:
        biChoice = np.random.binomial(1,mu*len(ListI)/c,1)
        if biChoice == 1:
            GET_S_EVENT(G,ListI,ListSI)
            break
        else:
            GET_I_EVENT(G,ListI,ListSI)
            break

def GET_S_EVENT(G,ListI,ListSI):
    node = random.choice(ListI)
    ListI.remove(node)
    for edge in ListSI:
        if edge[0] == node:
            ListSI.remove(edge)
    global c
    c = mu*len(ListI)+lam*len(ListSI)
    global tGlobal
    tGlobal = tGlobal + 0.0025
    

def GET_I_EVENT(G,ListI,ListSI):
    edge = random.choice(ListSI)
    ListSI.remove(edge)
    ListI.append(edge[1])
    for node in list(G.neighbors(edge[1])):
        ListSI.append([edge[1],node])
    global c
    c = mu*len(ListI)+lam*len(ListSI)
    global tGlobal
    tGlobal = tGlobal + 0.0025




def main(argv=None):
    if argv is None:
        argv = sys.argv

    IPercent = []
    SPercent = []
    Tlist = []
    start =time.perf_counter()
    c = 0
    Init_Data(G,ListI)
    Init_ListSI(G,ListI,ListSI)
    while True:
        if c == 0:
            break
        if len(ListI) == 0:
            break
        if tGlobal > 10.0:
            break
        chooseEvent(lam,mu,ListI,ListSI)
        IPercent.append(len(ListI)/NUMBEROFNODE)
        SPercent.append(1-len(ListI)/NUMBEROFNODE)
        Tlist.append(tGlobal)
    end = time.perf_counter()
    print('Running time: %s Seconds'%(end-start))

    # print(Tlist)
    plt.plot(Tlist,IPercent)
    plt.plot(Tlist,SPercent)

    plt.show()
    return 0


if __name__ == '__main__':
    sys.exit(main())
