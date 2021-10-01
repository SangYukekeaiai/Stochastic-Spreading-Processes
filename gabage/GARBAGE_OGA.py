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
    sumOfProb += math.pow(neighborNumber,-3)

  distribution = [None]*(MAXNEIGHBORCOUNT+1)
  distribution[0] = 0
  distribution[1] = 0
  distribution[2] = 0
  for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
    distribution[neighborNumber] = int(math.pow(neighborNumber,-3)/sumOfProb * NUMBEROFNODE)
  RESTNUMBER = NUMBEROFNODE - sum(distribution)
  distribution[3] = distribution[3]+RESTNUMBER

  nodeid = 0
  for neighborNum in range(len(distribution)):
    while distribution[neighborNum] > 0:
      maxDist = (len(list(G.neighbors(nodeid))))
      if (neighborNum-maxDist) >= 1 and (neighborNum-maxDist+nodeid) < NUMBEROFNODE:
        for neighborDist in range(1,neighborNum+1-maxDist):
          G.add_edge(nodeid,nodeid+neighborDist)
      elif(neighborNum-maxDist) >= 1 and (1+nodeid) < NUMBEROFNODE:
        for neighborDist in range(1,NUMBEROFNODE-nodeid):
          G.add_edge(nodeid,nodeid+neighborDist)
      distribution[neighborNum] = distribution[neighborNum] - 1
      nodeid = nodeid + 1

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
  global c1
  c1 = mu*len(ListI)+lam*SumOfEdge

 

def chooseEvent(mu,lam,ListI,G):
  while c1 != 0:
    biChoice = np.random.binomial(1,mu*len(ListI)/c1,1)
    if biChoice == 1:
      GET_S_EVENT(G,ListI,mu,lam)
      break
    else:
      GET_I_EVENT(G,ListI,mu,lam)
      break

def GET_S_EVENT(G,ListI,mu,lam):
  node = random.choice(ListI)
  global c1
  c1 = c1 - mu - lam*node[1]
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
            global c1
        c1 = c1 + mu + lam*(new_node[1]-1)
        global tGlobal
        tGlobal = tGlobal + 0.0025


G = nx.Graph()
ListI = []
lam = 0.6
mu = 1.0
tGlobal = 0
c1 = 0
start =time.perf_counter()
Init_Data(G,ListI)
Init_Neighbor(G,ListI)
Init_Edge(G,ListI,mu,lam)
while True:
  if c1 == 0:
    break
  if len(ListI) == 0:
    break
  if tGlobal > 2.0:
    break
  chooseEvent(mu,lam,ListI,G)
end = time.perf_counter()
print('Running time: %s Seconds'%(end-start))