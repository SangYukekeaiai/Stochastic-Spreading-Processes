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

# NUMBEROFNODE = int(1e5)
MAXNEIGHBORCOUNT = 100
tGlobal0 = 0
tGlobal1 = 0
c1 = 0
c = 0

def SIS_MODEL(NUMBEROFNODE,gamma):
  global n
  n = 0
  G = nx.Graph()
  EventQ = PriorityQueue()
  # start =time.perf_counter()
  biState = np.random.binomial(1, 0.95, NUMBEROFNODE)
  for i in range(NUMBEROFNODE):
    if biState[i] == 0:
      state = 'I'
    elif biState[i] == 1:
      state = 'S'
    else:
      raise ValueError("State out of bound")
    G.add_nodes_from([
      (i,{'state':state,'degree': 0,'recoveryTime':0})
    ])
  # print(G.nodes.data())
    # print(i)

  # print(G[0])
  sumOfProb = 0
  for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
    sumOfProb += math.pow(neighborNumber,gamma)

  distribution = [None]*(MAXNEIGHBORCOUNT+1)
  distribution[0] = 0
  distribution[1] = 0
  distribution[2] = 0
  for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
    distribution[neighborNumber] = int(math.pow(neighborNumber,gamma)/sumOfProb * NUMBEROFNODE)
  RESTNUMBER = NUMBEROFNODE - sum(distribution)
  distribution[3] = distribution[3]+RESTNUMBER
  # print(distribution)
  # print(G.nodes.data())

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
  end =time.perf_counter()
  # print('Running time: %s Seconds'%(end-start))
  # print(G.nodes.data())
  # print(G.number_of_nodes())


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
    rate = lam*G.nodes[node]['degree']
    while True:
      tEvent += np.random.exponential(rate)
      if G.nodes[node]['recoveryTime'] < tEvent:
        break
      attackedNode = random.choice(list(G.neighbors(node)))
      if G.nodes[attackedNode]['state'] == 'S' or G.nodes[attackedNode]['recoveryTime'] < tEvent:
        e = Event(state = 'Infection' , time = tEvent, srcNode = node, targetNode = attackedNode)
        EventQ.put(e)
        break


  start =time.perf_counter()
  InitGraph(G,1.0,0.6,EventQ)
  tGlobal = 0
  while True:
    if EventQ.empty():
      break
    e = EventQ.get()
    tGlobal = e.time
    if tGlobal > 2.0:
      break
    if e.state == 'Recovery':
      n = n + 1
      G.nodes[e.srcNode]['state'] = 'S'
    else:
      if G.nodes[e.targetNode]['state'] =='S':
        n = n + 1
        G.nodes[e.targetNode]['state'] = 'I'
        GenerateRecoveryEvent(e.targetNode,1.0,tGlobal,EventQ)
        GenerateInfectionEvent(e.srcNode,0.6,tGlobal,EventQ)
        GenerateInfectionEvent(e.targetNode,0.6,tGlobal,EventQ)
      else:
        GenerateInfectionEvent(e.srcNode,0.6,tGlobal,EventQ)
  end = time.perf_counter()
  print('Event based model Running time: %s Seconds'%((end-start)/n))
  return (end-start)/n
  # print(n)

def GA(NUMBEROFNODE,gamma):
  G = nx.Graph()
  ListI = []
  ListSI = []
  lam = 0.6
  mu = 1.0
  tGlobal = 0

  def Init_Data(G,ListI):
    biState = np.random.binomial(1, 0.95,NUMBEROFNODE)
    for node in range(NUMBEROFNODE):
      G.add_node(node)
      if biState[node] == 0:
        ListI.append(node)
      

  def Init_ListSI(G,ListI,ListSI):
    sumOfProb = 0
    for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
      sumOfProb += math.pow(neighborNumber,gamma)

    distribution = [None]*(MAXNEIGHBORCOUNT+1)
    distribution[0] = 0
    distribution[1] = 0
    distribution[2] = 0
    for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
      distribution[neighborNumber] = int(math.pow(neighborNumber,gamma)/sumOfProb * NUMBEROFNODE)
    RESTNUMBER = NUMBEROFNODE - sum(distribution)
    distribution[3] = distribution[3]+RESTNUMBER

    nodeid = 0
    for neighborNum in range(len(distribution)):
      while distribution[neighborNum] > 0:
        maxDist = (len(list(G.neighbors(nodeid))))
        if (neighborNum-maxDist) >= 1 and (neighborNum-maxDist+nodeid) < NUMBEROFNODE:
          for neighborDist in range(1,neighborNum+1-maxDist):
            G.add_edge(nodeid,nodeid+neighborDist)
            if nodeid in ListI and (nodeid+neighborDist) not in ListI:
              ListSI.append([nodeid,nodeid+neighborDist])
        elif(neighborNum-maxDist) >= 1 and (1+nodeid) < NUMBEROFNODE:
          for neighborDist in range(1,NUMBEROFNODE-nodeid):
            G.add_edge(nodeid,nodeid+neighborDist)
            if nodeid in ListI and (nodeid+neighborDist) not in ListI:
              ListSI.append([nodeid,nodeid+neighborDist])
        distribution[neighborNum] = distribution[neighborNum] - 1
        nodeid = nodeid + 1
    global c
    c = mu*len(ListI)+lam*len(ListSI)
    

  def chooseEvent(lam,mu,ListI,ListSI):
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
    global tGlobal0
    global n
    tGlobal = tGlobal0 + 1/n
    

  def GET_I_EVENT(G,ListI,ListSI):
    edge = random.choice(ListSI)
    ListSI.remove(edge)
    ListI.append(edge[1])
    for node in list(G.neighbors(edge[1])):
      ListSI.append([edge[1],node])
    global c
    c = mu*len(ListI)+lam*len(ListSI)
    global tGlobal0
    global n
    tGlobal0 = tGlobal0 + 1/n


  start =time.perf_counter()
  c = 0
  Init_Data(G,ListI)
  Init_ListSI(G,ListI,ListSI)
  while True:
    if c == 0:
      break
    if len(ListI) == 0:
      break
    if tGlobal0 > 2.0:
      break
    chooseEvent(lam,mu,ListI,ListSI)
  end = time.perf_counter()
  print('GA Running time: %s Seconds'%((end-start)/n))
  return (end-start)/n

def OGA(NUMBEROFNODE,gamma):
  def Init_Data(G,ListI):
    biState = np.random.binomial(1, 0.95,NUMBEROFNODE)
    for node in range(NUMBEROFNODE):
      G.add_node(node)
      if biState[node] == 0:
        ListI.append([node,0])

  def Init_Neighbor(G,ListI):
    sumOfProb = 0
    for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
      sumOfProb += math.pow(neighborNumber,gamma)

    distribution = [None]*(MAXNEIGHBORCOUNT+1)
    distribution[0] = 0
    distribution[1] = 0
    distribution[2] = 0
    for neighborNumber in range(3,MAXNEIGHBORCOUNT+1):
      distribution[neighborNumber] = int(math.pow(neighborNumber,gamma)/sumOfProb * NUMBEROFNODE)
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
    global tGlobal1
    global n
    tGlobal1 = tGlobal1 + 1/n

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
          global tGlobal1
          global n
          tGlobal1 = tGlobal1 + 1/n


  G = nx.Graph()
  ListI = []
  lam = 0.6
  mu = 1.0
  tGlobal1 = 0
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
    if tGlobal1 > 2.0:
      break
    chooseEvent(mu,lam,ListI,G)
  end = time.perf_counter()
  print('OGA Running time: %s Seconds'%((end-start)/n))  
  return (end-start)/n



ListNumber = np.linspace(10000,100000,10)
Event_Based_List2 = []
Event_Based_List3 = []
Ga_List2 = []
Ga_List3 = []
Oga_List2 = []
Oga_List3 = []
for NUMBEROFNODE in ListNumber:
  Event_Based_List2.append(SIS_MODEL(int(NUMBEROFNODE),-2))
  Event_Based_List3.append(SIS_MODEL(int(NUMBEROFNODE),-3))
  Ga_List2.append(GA(int(NUMBEROFNODE),2))
  Ga_List3.append(GA(int(NUMBEROFNODE),3))
  Oga_List2.append(OGA(int(NUMBEROFNODE),2))
  Oga_List3.append(OGA(int(NUMBEROFNODE),3))
plt.scatter(ListNumber,Ga_List2,c = 'blue',marker='v')
plt.legend("GA,gamma = 2.0")
plt.scatter(ListNumber,Ga_List3,c = 'yellow',marker='^')
plt.legend("GA,gamma = 3.0")
plt.scatter(ListNumber,Oga_List2,c = 'green',marker='>')
plt.legend("OGA,gamma = 2.0")
plt.scatter(ListNumber,Oga_List3,c = 'orange',marker='<')
plt.legend("OGA,gamma = 3.0")
plt.scatter(ListNumber,Event_Based_List2,c = 'red',marker='+')
plt.legend("reject,gamma = 2.0")
plt.scatter(ListNumber,Event_Based_List3,c = 'black',marker='x')
plt.legend("reject,gamma = 3.0")
plt.xlabel("Number of Nodes")
plt.ylabel("CPU Time per Step(s)")
plt.show()