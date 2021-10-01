from queue import PriorityQueue
# import networkx as nx
# import matplotlib.pyplot as plt
import time


class Event(object):
  def __init__(self,state,time,point):
    self.state = state
    self.time = time
    self.point = point
    print('Event: ',state,time,point)

  def __lt__(self,other):
    return self.time < other.time

EventQ = PriorityQueue()
e1 = Event('S',0.1,2)
e2 = Event('I',0.6,4)
e3 = Event('S',0.9,6)
e4 = Event('I',1.2,3)
EventQ.put(e1)
EventQ.put(e2)
EventQ.put(e3)
EventQ.put(e4)



for e in EventQ.queue:
  if e.state == 'S':
    e.point += 1
    print(e.point)



# ##### Algorithm 1 : Graph Initialization
# def InitGraph(G,mu,lam,eventQ):
#   for node in list(G.nodes):
