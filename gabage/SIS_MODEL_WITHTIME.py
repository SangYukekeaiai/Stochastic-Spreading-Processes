from queue import PriorityQueue
import networkx as nx
import random
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import math
import time

class Event(object):
  def __init__(self,state,time,srcNode,targetNode):
    self.state = state
    self.time = time
    self.srcNode = srcNode
    self.targetNode = targetNode
    # print('Event: ',state,time,srcNode,targetNode)

  def __lt__(self,other):
    return self.time < other.time

G = nx.Graph()

EventQ = PriorityQueue()
ListI = []
ListS = []

# print (np.random.binomial(1,0.95,1000))


NUMBEROFNODE = int(1e5)
MAXNEIGHBORCOUNT = 1000

# start =time.perf_counter()
Inumber = 0
Snumber = 0
# def InitNodeState(G):
biState = np.random.binomial(1, 0.95, NUMBEROFNODE)
for i in range(NUMBEROFNODE):
  if biState[i] == 0:
    state = 'I'
    Inumber = Inumber + 1
  elif biState[i] == 1:
    state = 'S'
    Snumber = Snumber + 1
  else:
    raise ValueError("State out of bound")
  G.add_nodes_from([
    (i,{'state':state,'neighborNumber': 0,'recoveryTime':0})
  ])

ListI.append(Inumber/NUMBEROFNODE)
ListS.append(Snumber/NUMBEROFNODE)
# print(G.nodes.data())
  # print(i)

# print(G[0])
# def InitNeighbor(G):
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
# print(distribution)
# print(G.nodes.data())

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

def InitGraph(G,mu,lam,EventQ):
  for node in G.__iter__():
    if G.nodes[node]['state'] == 'I':
      GenerateRecoveryEvent(node,mu,0,EventQ)
  for node in G.__iter__():
    if G.nodes[node]['state'] == 'I':
      GenerateInfectionEvent(node,lam,0,EventQ) 

def GenerateRecoveryEvent(node,mu,tGlobal,EventQ):
  tEvent = tGlobal + np.random.exponential(mu)
  e = Event(state = 'Recovery' , time = tEvent, srcNode = node, targetNode = None)
  G.nodes[node]['recoveryTime'] = tEvent
  EventQ.put(e)

def GenerateInfectionEvent(node,lam,tGlobal,EventQ):
  tEvent = tGlobal
  rate = lam*G.nodes[node]['neighborNumber']
  while True:
    tEvent += np.random.exponential(rate)
    if G.nodes[node]['recoveryTime'] < tEvent:
      break
    attackedNode = random.choice(list(G.neighbors(node)))
    if G.nodes[attackedNode]['state'] == 'S' or G.nodes[attackedNode]['recoveryTime'] < tEvent:
      e = Event(state = 'Infection' , time = tEvent, srcNode = node, targetNode = attackedNode)
      EventQ.put(e)
      break


mu = 10
lam = 0.00006
tList = [0]
SEvent = 0
IEvent = 0

for timeslice in [0,2,4,6,8]:
  for node in G.__iter__():
    G.nodes[node]['recoveryTime'] ==0
  # print("timeslice is: %s"%timeslice)
  InitGraph(G,mu,lam,EventQ)
  tGlobal = 0
  while True:
    if EventQ.empty():
      break
    e = EventQ.get()
    tGlobal = e.time
    if tGlobal > 2.0:
      break
    if e.state == 'Recovery':
      G.nodes[e.srcNode]['state'] = 'S'
      G.nodes[node]['recoveryTime'] = 0
      SEvent += 1
      Snumber = Snumber + 1
      Inumber = Inumber - 1
      ListI.append(Inumber/NUMBEROFNODE)
      ListS.append(Snumber/NUMBEROFNODE)
      # print(timeslice + tGlobal)
      tList.append(tGlobal+timeslice)
    else:
      if G.nodes[e.targetNode]['state'] =='S':
        G.nodes[e.targetNode]['state'] = 'I'
        IEvent += 1
        Snumber = Snumber - 1
        Inumber = Inumber + 1
        ListI.append(Inumber/NUMBEROFNODE)
        ListS.append(Snumber/NUMBEROFNODE)
        # print(timeslice + tGlobal)
        tList.append(tGlobal+timeslice)
        GenerateRecoveryEvent(e.targetNode,mu,tGlobal,EventQ)
        GenerateInfectionEvent(e.srcNode,lam,tGlobal,EventQ)
        GenerateInfectionEvent(e.targetNode,mu,tGlobal,EventQ)
      else:
        GenerateInfectionEvent(e.srcNode,lam,tGlobal,EventQ)

# print(tList)
print(SEvent)
print(IEvent)
print(Inumber)
print(Snumber)
plt.plot(tList,ListI,label = 'I')
plt.plot(tList,ListS,label = 'S')
plt.xlabel("Times")
plt.ylabel("Fractions")
plt.legend()
plt.show()

