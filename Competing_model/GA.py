import networkx as nx
import random
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import math
import time
import sys


def Init_Data(G, ListI, ListJ, numberofnode, MAXNEIGHBORCOUNT):
    biState = np.random.binomial(1, 0.96, numberofnode)
    for node in range(numberofnode):
        G.add_node(node)
        if biState[node] == 0:
            biState[node] = np.random.binomial(1, 0.5, 1)
            if biState[node] == 0:
                ListI.append(node)
            else:
                ListJ.append(node)
        

def Init_ListEdge(G, ListI, ListJ, ListSI, ListSJ, numberofnode, MAXNEIGHBORCOUNT, gamma, mu1, mu2, lam1, lam2):
    sumOfProb = 0
    for neighborNumber in range(3, MAXNEIGHBORCOUNT + 1):
        sumOfProb += math.pow(neighborNumber, gamma)

    distribution = [None]*(MAXNEIGHBORCOUNT + 1)
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
            if node == numberofnode - 1:
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
                if node in ListI and neighborNew not in ListI and neighborNew not in ListJ:
                    ListSI.append([node, neighborNew])
                if node in ListJ and neighborNew not in ListI and neighborNew not in ListJ:
                    ListSJ.append([node, neighborNew])
    c = mu1 * len(ListI) + mu2 * len(ListJ) + lam1 * len(ListSI) + lam2 * len(ListSJ)
    return c

def chooseEvent(G, lam1, lam2, mu1, mu2, ListI, ListJ, ListSI, ListSJ, c, tGlobal):
    while c != 0:
        biChoice = np.random.binomial(1, mu1 * len(ListI)/c, 1)
        if biChoice == 1:
            ls = I_TO_S_EVENT(G, ListI, ListJ, ListSI, ListSJ, mu1, mu2, lam1, lam2, tGlobal)
            return ls
        else:
            p = 1 - mu1 * len(ListI) / c
            biChoice = np.random.binomial(1, mu2 * len(ListJ) / c / p, 1)
            if biChoice == 1:
                ls = J_TO_S_EVENT(G, ListI, ListJ, ListSI, ListSJ, mu1, mu2, lam1, lam2, tGlobal)
                return ls
            else:
                p = 1 - mu2 * len(ListJ) / c / p
                biChoice = np.random.binomial(1, lam1 * len(ListSI) / c / p, 1)
                if biChoice == 1:
                    ls = GET_I_EVENT(G, ListI, ListJ, ListSI, ListSJ, mu1, mu2, lam1, lam2, tGlobal)
                    return ls
                else:
                    ls = GET_J_EVENT(G, ListI, ListJ, ListSI, ListSJ, mu1, mu2, lam1, lam2, tGlobal)
                    return ls

def I_TO_S_EVENT(G, ListI, ListJ, ListSI, ListSJ, mu1, mu2, lam1, lam2, tGlobal):
    node = random.choice(ListI)
    ListI.remove(node)
    for edge in ListSI:
        if edge[0] == node:
            ListSI.remove(edge)
    c = mu1 * len(ListI) + mu2 * len(ListJ) + lam1 * len(ListSI) + lam2 * len(ListSJ)
    tGlobal = tGlobal + 0.0025
    return [tGlobal,c]

def J_TO_S_EVENT(G, ListI, ListJ, ListSI, ListSJ, mu1, mu2, lam1, lam2, tGlobal):
    node = random.choice(ListJ)
    ListJ.remove(node)
    for edge in ListSJ:
        if edge[0] == node:
            ListSJ.remove(edge)
    c = mu1 * len(ListI) + mu2 * len(ListJ) + lam1 * len(ListSI) + lam2 * len(ListSJ)
    tGlobal = tGlobal + 0.0025
    return [tGlobal,c]

def GET_I_EVENT(G, ListI, ListJ, ListSI, ListSJ, mu1, mu2, lam1, lam2, tGlobal):
    edge = random.choice(ListSI)
    ListSI.remove(edge)
    ListI.append(edge[1])
    for node in list(G.neighbors(edge[1])):
        ListSI.append([edge[1], node])
    c = mu1 * len(ListI) + mu2 * len(ListJ) + lam1 * len(ListSI) + lam2 * len(ListSJ)
    tGlobal = tGlobal + 0.0025
    return [tGlobal,c]

def GET_J_EVENT(G, ListI, ListJ, ListSI, ListSJ, mu1, mu2, lam1, lam2, tGlobal):
    edge = random.choice(ListSJ)
    ListSJ.remove(edge)
    ListJ.append(edge[1])
    for node in list(G.neighbors(edge[1])):
        ListSJ.append([edge[1], node])
    c = mu1 * len(ListI) + mu2 * len(ListJ) + lam1 * len(ListSI) + lam2 * len(ListSJ)
    tGlobal = tGlobal + 0.0025
    return [tGlobal,c]

def trans_data_list():
    node_numberlist = range(10000,110000,10000)
    gamma_list = [-2,-3]
    timelist = []
    for gamma in gamma_list:
        for numberofnode in node_numberlist:
            G = nx.Graph()
            ListI = []
            ListJ = []
            ListSI = []
            ListSJ = []
            lam1 = 0.6
            lam2 = 0.63
            mu1 = 0.6
            mu2 = 0.7
            tGlobal = 0
            tmax = 2
            tstep = 0.0025
            MAXNEIGHBORCOUNT = 100
            Init_Data(G, ListI, ListJ, numberofnode, MAXNEIGHBORCOUNT)
            c = Init_ListEdge(G, ListI, ListJ, ListSI, ListSJ, numberofnode, MAXNEIGHBORCOUNT, gamma, mu1, mu2, lam1, lam2)
            start =time.perf_counter()
            while c != 0 and (len(ListI) != 0 or len(ListJ) != 0):
                if tGlobal > tmax:
                    break
                ls = chooseEvent(G, lam1, lam2, mu1, mu2, ListI, ListJ, ListSI, ListSJ, c, tGlobal)
                tGlobal = ls[0]
                c = ls[1]
            end = time.perf_counter()
            timelist.append((end - start)/(tmax/tstep))
            print('%s node Running time in gamma %s : %s Seconds' %(numberofnode, gamma, ((end-start)/(tmax/tstep))))
    return timelist


def main(argv=None):
    if argv is None:
        argv = sys.argv


    G = nx.Graph()
    ListI = []
    ListJ = []
    ListSI = []
    ListSJ = []
    lam1 = 0.6
    lam2 = 0.63
    mu1 = 0.6
    mu2 = 0.7
    tGlobal = 0
    gamma = -3
    tmax = 2
    tstep = 0.0025
    numberofnode = int(1e4)
    MAXNEIGHBORCOUNT = 100
    Init_Data(G, ListI, ListJ, numberofnode, MAXNEIGHBORCOUNT)
    c = Init_ListEdge(G, ListI, ListJ, ListSI, ListSJ, numberofnode, MAXNEIGHBORCOUNT, gamma, mu1, mu2, lam1, lam2)
    start =time.perf_counter()
    while c != 0 and (len(ListI) != 0 or len(ListJ) != 0):
        if tGlobal > tmax:
            break
        ls = chooseEvent(G, lam1, lam2, mu1, mu2, ListI, ListJ, ListSI, ListSJ, c, tGlobal)
        tGlobal = ls[0]
        c = ls[1]
    end = time.perf_counter()
    print('Running time: %s Seconds'%((end - start)/(tmax/tstep)))

    return 0

if __name__ == '__main__':
    sys.exit(main())
