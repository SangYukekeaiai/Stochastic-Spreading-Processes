import networkx as nx
G = nx.Graph()
### test
G.add_nodes_from([
  (1,{'state':'I','degree':0.3,'recoveryTime':0}),
  (2,{'state':'S','degree':0.3,'recoveryTime':0}),
  (3,{'state':'I','degree':0.4,'recoveryTime':0}),
  (4,{'state':'S','degree':0.3,'recoveryTime':0}),
  (5,{'state':'S','degree':0.3,'recoveryTime':0}),
])

G.add_edges_from([
  (1,2),(1,3),(1,4),(2,5),(4,5),(2,3),(3,4),(3,5),
])

print(list(G.neighbors(1)))
# for node in G.__iter__():
#   G.add_nodes_from([node], time='2pm')
# print('all nodes of Graph',G.nodes())
# print('imformation of all nodes',G.nodes.data())
# # print(G.nodes[1]['time'])