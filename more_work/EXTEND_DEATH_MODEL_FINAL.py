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

NUMBEROFNODE = int(1e5)
MAXNEIGHBORCOUNT = 100
start =time.perf_counter()
biState = np.random.binomial(1, 0.96, NUMBEROFNODE)
for i in range(NUMBEROFNODE):
  if biState[i] == 0:
    biState[i] = np.random.binomial(1,0.5,1)
    if biState[i] == 0:
      biState[i] = np.random.binomial(1,0.5,1)
      if biState[i] == 0:
        state = 'RI'
      else:
        state = 'RJ'
    else:
      biState[i] = np.random.binomial(1,0.5,1)
      if biState[i] == 0:
        state = 'I'
      else:
        state = 'J'
  elif biState[i] == 1:
    state = 'S'
  else:
    raise ValueError("State out of bound")
  G.add_nodes_from([
    (i,{'state':state,'degree': 0,'Time':0})
  ])


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
for nodeid in range(NUMBEROFNODE):
  G.nodes[nodeid]['degree'] = len(list(G.neighbors(nodeid)))
end = time.perf_counter()

print('Running time: %s Seconds'%(end-start))

def InitGraph(G,mu1,mu2,mu3,mu4,mu5,mu6,mu7,lam1,lam2,EventQ):
  for node in G.__iter__():
    if G.nodes[node]['state'] == 'I':
      FROM_I_TO_Event(node,mu1,mu2,mu6,tGlobal,EventQ)
    if G.nodes[node]['state'] == 'J':
      FROM_J_TO_Event(node,mu3,mu7,tGlobal,EventQ)
    if G.nodes[node]['state'] == 'RI':
      RI_TO_S_Event(node,mu4,0,EventQ)
    if G.nodes[node]['state'] == 'RJ':
      RJ_TO_S_Event(node,mu5,0,EventQ)
  for node in G.__iter__():
    if G.nodes[node]['state'] == 'I':
      GET_I_Event(node,lam1,0,EventQ)
    if G.nodes[node]['state'] == 'J':
      GET_J_Event(node,lam2,0,EventQ)
    

def FROM_I_TO_Event(node,mu1,mu2,mu6,tGlobal,EventQ):
  tEvent_ri = tGlobal + np.random.exponential(mu1)
  tEvent_j = tGlobal + np.random.exponential(mu2)
  tEvent_d = tGlobal + np.random.exponential(mu6)
  tMin = min(tEvent_d,tEvent_j,tEvent_ri)
  if tEvent_ri == tMin:
    e = Event(state = 'I_TO_RI',time = tEvent_ri,srcNode = node, targetNode = None)
    G.nodes[node]['Time'] = tEvent_ri
  elif tEvent_j == tMin:
    e = Event(state = 'I_TO_J',time = tEvent_j,srcNode = node, targetNode = None)
    G.nodes[node]['Time'] = tEvent_j
  else:
    e = Event(state = 'I_TO_D',time = tEvent_d,srcNode = node, targetNode = None)
    G.nodes[node]['Time'] = tEvent_d
  EventQ.put(e)

def FROM_J_TO_Event(node,mu3,mu7,tGlobal,EventQ):
  tEvent_rj = tGlobal + np.random.exponential(mu3)
  tEvent_d = tGlobal + np.random.exponential(mu7)
  if tEvent_rj > tEvent_d:
    e = Event(state = 'J_TO_D',time = tEvent_d,srcNode = node, targetNode = None)
    G.nodes[node]['Time'] = tEvent_d
  else:
    e = Event(state = 'J_TO_RJ',time = tEvent_rj,srcNode = node, targetNode = None)
    G.nodes[node]['Time'] = tEvent_rj
  EventQ.put(e)

def RI_TO_S_Event(node,mu4,tGlobal,EventQ):
  tEvent = tGlobal + np.random.exponential(mu4)
  e = Event(state = 'RI_TO_S',time = tEvent,srcNode = node, targetNode = None)
  G.nodes[node]['Time'] = tEvent
  EventQ.put(e)
  
def RJ_TO_S_Event(node,mu5,tGlobal,EventQ):
  tEvent = tGlobal + np.random.exponential(mu5)
  e = Event(state = 'RJ_TO_S',time = tEvent,srcNode = node, targetNode = None)
  G.nodes[node]['Time'] = tEvent
  EventQ.put(e)

def GET_I_Event(node,lam1,tGlobal,EventQ):
  tEvent = tGlobal
  rate = lam1*G.nodes[node]['degree']
  while True:
    tEvent += np.random.exponential(rate)
    if G.nodes[node]['Time'] < tEvent:
      break    
    attackedNode = random.choice(list(G.neighbors(node)))
    if G.nodes[attackedNode]['state'] == 'J':
      break
    if G.nodes[attackedNode]['state'] == 'I':
      break
    if G.nodes[attackedNode]['state'] == 'D':
      break
    if G.nodes[attackedNode]['state'] == 'S' or G.nodes[attackedNode]['Time']<tEvent:
      e = Event(state = 'GET_I' , time = tEvent, srcNode = node, targetNode = attackedNode)
      EventQ.put(e)
      break  

def GET_J_Event(node,lam2,tGlobal,EventQ):
  tEvent = tGlobal
  rate = lam2*G.nodes[node]['degree']
  while True:
    tEvent += np.random.exponential(rate)
    if G.nodes[node]['Time'] < tEvent:
      break   
    attackedNode = random.choice(list(G.neighbors(node)))
    if G.nodes[attackedNode]['state'] == 'I' and G.nodes[attackedNode]['Time']>tEvent:
      break
    if G.nodes[attackedNode]['state'] == 'J':
      break
    if G.nodes[attackedNode]['state'] == 'D':
      break
    if G.nodes[attackedNode]['state'] == 'S' or G.nodes[attackedNode]['Time']<tEvent:
      e = Event(state = 'GET_J' , time = tEvent, srcNode = node, targetNode = attackedNode)
      EventQ.put(e)
      break  


mu1 = 1.0
mu2 = 0.6
mu3 = 0.63
mu4 = 0.3
mu5 = 0.5
mu6 = 0.4
mu7 = 0.8
lam1 = 0.6
lam2 = 0.6
tGlobal = 0
start =time.perf_counter()
InitGraph(G,mu1,mu2,mu3,mu4,mu5,mu6,mu7,lam1,lam2,EventQ)

while True:
  if EventQ.empty():
    break
  e = EventQ.get()
  tGlobal = e.time
  if tGlobal > 2.0:
    break
  if e.state == 'I_TO_J':
    G.nodes[e.srcNode]['state'] = 'J'
    FROM_J_TO_Event(e.srcNode,mu3,mu7,tGlobal,EventQ)
    GET_J_Event(e.srcNode,lam2,tGlobal,EventQ)
  elif e.state == 'I_TO_RI':
    G.nodes[e.srcNode]['state'] = 'RI'
    RI_TO_S_Event(e.srcNode,mu4,tGlobal,EventQ)
  elif e.state == 'J_TO_RJ':
    G.nodes[e.srcNode]['state'] = 'RJ'
    RJ_TO_S_Event(e.srcNode,mu5,tGlobal,EventQ)
  elif e.state == 'RI_TO_S':
    G.nodes[e.srcNode]['state'] = 'S'
    G.nodes[e.srcNode]['Time'] = 0
  elif e.state == 'RJ_TO_S':
    G.nodes[e.srcNode]['state'] = 'S'
    G.nodes[e.srcNode]['Time'] = 0
  elif e.state =='I_TO_D':
    G.nodes[e.srcNode]['state'] = 'D'
    G.nodes[e.srcNode]['Time'] = 0
  elif e.state =='J_TO_D':
    G.nodes[e.srcNode]['state'] = 'D'
    G.nodes[e.srcNode]['Time'] = 0
  elif e.state == 'GET_I':
    if G.nodes[e.targetNode]['state'] == 'S':
      G.nodes[e.targetNode]['state'] = 'I'
      FROM_I_TO_Event(e.targetNode,mu1,mu2,mu6,tGlobal,EventQ)
      GET_I_Event(e.srcNode,lam1,tGlobal,EventQ)
      GET_I_Event(e.targetNode,lam1,tGlobal,EventQ)
    else:
      GET_I_Event(e.srcNode,lam1,tGlobal,EventQ)
  else:
    if G.nodes[e.targetNode]['state'] == 'S' or G.nodes[e.targetNode]['state'] == 'RI':
      G.nodes[e.targetNode]['state'] = 'J'
      FROM_J_TO_Event(e.targetNode,mu3,mu7,tGlobal,EventQ)
      GET_J_Event(e.srcNode,lam2,tGlobal,EventQ)
      GET_J_Event(e.targetNode,lam2,tGlobal,EventQ)
    else:
      GET_J_Event(e.srcNode,lam2,tGlobal,EventQ)
end = time.perf_counter()
print('Running time: %s Seconds'%(end-start))
# print(G.nodes.data())
