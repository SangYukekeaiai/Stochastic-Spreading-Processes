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
    G.nodes[node]['edgeNumber'] = 0
    if biState[node] == 0:
      ListI.append(node)

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
  # print(ListI)
  # for node in ListI:
  #   print(node)
  #   print(list(G[node]))

def Init_Edge(G,ListI,mu,lam):
  SumOfEdge = 0
  for node in ListI:
    count = 0
    for neighbor in list(G.neighbors(node)):
      if neighbor not in ListI:
        count+= 1
    G.nodes[node]['edgeNumber'] = count
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
  ListI.remove(node)
  global c
  c = c - mu - lam*G.nodes[node]['edgeNumber']
  G.nodes[node]['edgeNumber'] = 0
  global tGlobal
  tGlobal = tGlobal + 0.0025

def GET_I_EVENT(G,ListI,mu,lam):
  count = 0
  Percent = []
  for node in ListI:
    count = count + (len(list(G.neighbors(node))))
    Percent.append(count)
  number = random.uniform(1,count+1)
  for i in range(len(Percent)):
    if number < Percent[i]:
      srcNode = ListI[i]
      attacked_node = random.choice(list(G.neighbors(srcNode)))
      if attacked_node not in ListI:
        ListI.append(attacked_node)
        for node in list(G.neighbors(attacked_node)):
          if node not in ListI:
            G.nodes[attacked_node]['edgeNumber'] += 1
        global c
        c = c + mu + lam*(G.nodes[attacked_node]['edgeNumber']-1)
        global tGlobal
        tGlobal = tGlobal + 0.0025


G = nx.Graph()
ListI = []
lam = 0.6
mu = 1.0
tGlobal = 0
c = 0
start =time.perf_counter()
Init_Data(G,ListI)
Init_Neighbor(G,ListI)
Init_Edge(G,ListI,mu,lam)
while True:
  if c == 0:
    break
  if len(ListI) == 0:
    break
  if tGlobal > 2.0:
    break
  chooseEvent(mu,lam,ListI,G)
end = time.perf_counter()
print('Running time: %s Seconds'%(end-start))
    
