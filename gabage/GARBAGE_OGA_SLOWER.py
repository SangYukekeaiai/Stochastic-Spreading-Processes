import networkx as nx
import random
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import math
import time

NUMBEROFNODE = int(1e5)
MAXNEIGHBORCOUNT = 100

def Init_Data(G,ListI):
  biState = np.random.binomial(1, 0.95,NUMBEROFNODE)
  for node in range(NUMBEROFNODE):
    G.add_node(node)
    if biState[node] == 0:
      ListI.append([node,0])

def Init_Neighbor(G,ListI):
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
        while (G.nodes[neighborNew]['neighborNumber'] <= len(list(G.neighbors(neighborNew)))):
          neighborNew = random.choice(range(node+1,NUMBEROFNODE))
          # continue
        G.add_edge(node,neighborNew)


def Init_Edge(G,ListI,mu,lam):
  SumOfEdge = 0
  for node in ListI:
    count = 0
    for neighbor in list(G.neighbors(node[0])):
      PureListI_ID = []
      for node in ListI:
        PureListI_ID.append(node[0])
      if neighbor not in PureListI_ID:
        count+= 1
    SumOfEdge += count
  global c
  c = mu*len(ListI)+lam*SumOfEdge

 

def chooseEvent(mu,lam,ListI,G):
  while c != 0:
    biChoice = np.random.binomial(1,mu*len(ListI)/c,1)
    if biChoice == 1:
      GET_S_EVENT(G,ListI,mu,lam)
      break
    else:
      GET_I_EVENT(G,ListI,mu,lam)
      break

def GET_S_EVENT(G,ListI,mu,lam):
  node = random.choice(ListI)
  global c
  c = c - mu - lam*node[1]
  ListI.remove(node)
  global tGlobal
  tGlobal = tGlobal + 0.0025

def GET_I_EVENT(G,ListI,mu,lam):
  count = 0
  Percent = []
  for node in ListI:
    count = count + (len(list(G.neighbors(node[0]))))
    Percent.append(count)
  number = random.uniform(1,count+1)
  for i in range(len(Percent)):
    if number < Percent[i]:
      srcNode = ListI[i][0]
      attacked_node = random.choice(list(G.neighbors(srcNode)))
      PureListI_ID = []
      for node in ListI:
        PureListI_ID.append(node[0])
      if attacked_node not in PureListI_ID:
        new_node = [attacked_node,0]
        ListI.append(new_node)
        PureListI_ID.append(attacked_node)
        for node in list(G.neighbors(attacked_node)):
          if node not in PureListI_ID:
            # G.nodes[attacked_node]['edgeNumber'] += 1
            new_node[1] += 1
            global c
        c = c + mu + lam*(new_node[1]-1)
        global tGlobal
        tGlobal = tGlobal + 0.0025


G = nx.Graph()
ListI = []
lam = 0.6
mu = 1.0
tGlobal = 0
c = 0

Init_Data(G,ListI)
Init_Neighbor(G,ListI)
Init_Edge(G,ListI,mu,lam)
start =time.perf_counter()
while True:
  if c == 0:
    break
  if len(ListI) == 0:
    break
  if tGlobal > 2.0:
    break
  chooseEvent(mu,lam,ListI,G)
end = time.perf_counter()
print('Running time: %s Seconds'%((end-start)/800))
    
