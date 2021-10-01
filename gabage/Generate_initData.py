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
    print('Event: ',state,time,srcNode,targetNode)

  def __lt__(self,other):
    return self.time < other.time

G = nx.Graph()

# print (np.random.binomial(1,0.95,1000))


NUMBEROFNODE = int(1e6)
start =time.perf_counter()
biState = np.random.binomial(1, 0.95, NUMBEROFNODE)
for i in range(NUMBEROFNODE):
  if biState[i] == 0:
    state = 'I'
  elif biState[i] == 1:
    state = 'S'
  else:
    raise ValueError("State out of bound")
  G.add_nodes_from([
    (i,{'state':state,'degree': 10,'recoveryTime':0})
  ])


for node in range(NUMBEROFNODE):
  NeighborNow = list(G.neighbors(node))
  while len(NeighborNow) < 10:
    NeighborNew = random.choice(list(G.nodes))
    if NeighborNew in list(G.neighbors(node)):
      continue
    else:
      NeighborNow.append(NeighborNew)
  
  for neighbor in NeighborNow:
    G.add_edge(node,neighbor)
end =time.perf_counter()
print('Running time: %s Seconds'%(end-start))

# print(G.nodes.data())
# print(list(G.edges))
 
# list(G.neighbors(node))
# neighborNew = [random.randint(0,int(1e7)) for _ in range(30 - len(NeighborNow))]