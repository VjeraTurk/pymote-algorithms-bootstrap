# -*- coding: utf-8 -*-
#%load_ext autoreload
#%autoreload 2
#%reload_ext autoreload
"""
Created on Fri Jun 22 14:53:54 2018

@author: admin
"""
from pymote import NetworkGenerator
from pymote.npickle import read_pickle, write_pickle
from pymote.network import Network
from networkx import minimum_spanning_tree, prim_mst_edges, prim_mst, draw, Graph,  draw_networkx_edges, spring_layout, draw_networkx_edge_labels, draw_networkx_nodes,draw_networkx_labels

from pylab import show, figure
import random


#Generate random weighted network
"""
net_gen = NetworkGenerator(7)
net = net_gen.generate_random_network()

net.show()
print(net.nodes())
g = Graph()
g.adj=net.adj
#definirati l da se osigura količina ponavljanja istih weightova
l=len(net.nodes())-1

for node,neighbors in net.adjacency_iter():
    for neighbor,eattr in neighbors.items():
        print(neighbor)        
        g.add_edge(node,neighbor, weight=random.randrange(1,l,1)) 
        
net.adj=g.adj
write_pickle(net, 'RandomBezAlg.tar.gz')

"""
#### Primjer mreze sa sva tri slucaja-  Absorbtion, Friendly Merge i Suspenssion
"""
net = Network()
node= net.add_node(pos=[200,300])
node= net.add_node(pos=[300,300])
node= net.add_node(pos=[100,200])
node= net.add_node(pos=[400,200])
node= net.add_node(pos=[200,100])
node= net.add_node(pos=[300,100])

g = Graph()
g.add_edge(net.nodes()[0],net.nodes()[1],weight=1.1)
g.add_edge(net.nodes()[0],net.nodes()[2],weight=1.7)
g.add_edge(net.nodes()[0],net.nodes()[4],weight=2.6)
g.add_edge(net.nodes()[1],net.nodes()[3],weight=3.1)
g.add_edge(net.nodes()[2],net.nodes()[4],weight=3.8)
g.add_edge(net.nodes()[3],net.nodes()[5],weight=3.7)
g.add_edge(net.nodes()[4],net.nodes()[5],weight=2.1)
net.adj=g.adj
net.show()

write_pickle(net, 'allCasesBezAlg.tar.gz')
"""

### Primjer mreze sa worst-case slučajem

net = Network()
node= net.add_node(pos=[100,50])
node= net.add_node(pos=[150,50])
node= net.add_node(pos=[100,200])
node= net.add_node(pos=[400,200])
node= net.add_node(pos=[250,300])
node= net.add_node(pos=[350,50])

g = Graph()
g.add_edge(net.nodes()[0],net.nodes()[1],weight=0.5)

g.add_edge(net.nodes()[1],net.nodes()[2],weight=1.414)
g.add_edge(net.nodes()[1],net.nodes()[3],weight=2.414)
g.add_edge(net.nodes()[1],net.nodes()[4],weight=3.414)
g.add_edge(net.nodes()[1],net.nodes()[5],weight=4.414)

g.add_edge(net.nodes()[2],net.nodes()[3],weight=1)
g.add_edge(net.nodes()[3],net.nodes()[4],weight=2)
g.add_edge(net.nodes()[4],net.nodes()[5],weight=3)


g.add_edge(net.nodes()[2],net.nodes()[4],weight=2.5)
g.add_edge(net.nodes()[2],net.nodes()[5],weight=3.66)
g.add_edge(net.nodes()[3],net.nodes()[5],weight=3.33)



net.adj=g.adj
net.show()
write_pickle(net, 'WorstCaseBezAlg.tar.gz')


#nacrtaj s težinama, 
#pozicija nodova nije uredu?! Kako izvući poziciju?

pos=spring_layout(net.pos)
#pos=get_node_attributes(g,net.pos)
figure(2)
#draw(g,pos)
# specifiy edge labels explicitly
edge_labels=dict([((u,v,),d['weight'])
             for u,v,d in g.edges(data=True)])
#pos=net.pos #Ako pos nije izvuceno iz net.pos rasporede se tako da se bolje vide
draw_networkx_nodes(g,pos=net.pos, node_size=500)
draw_networkx_edges(g,pos=net.pos)
draw_networkx_labels(g,pos=net.pos,labels=net.labels)
draw_networkx_edge_labels(g,pos=net.pos,edge_labels=edge_labels)

# show graphs
show()

#Prsina mreza za test
"""
net = read_pickle("poslati.txt")
g = Graph()
g.add_edge(net.nodes()[0],net.nodes()[1],weight=1)
g.add_edge(net.nodes()[0],net.nodes()[2],weight=2)
g.add_edge(net.nodes()[0],net.nodes()[5],weight=3)
g.add_edge(net.nodes()[2],net.nodes()[6],weight=4)
g.add_edge(net.nodes()[3],net.nodes()[5],weight=5)
g.add_edge(net.nodes()[4],net.nodes()[6],weight=6)
g.add_edge(net.nodes()[6],net.nodes()[7],weight=7)
#dodatni, da naprave razliku između mreze i MST
g.add_edge(net.nodes()[3],net.nodes()[4],weight=8)
g.add_edge(net.nodes()[5],net.nodes()[7],weight=9)
g.add_edge(net.nodes()[1],net.nodes()[2],weight=10)

labels = get_node_attributes(g, 'weight')
net.adj=g.adj
net.show()
write_pickle(net, 'PrsaBezAlg.tar.gz')

#draw(net,labels=labels, pos=spring_layout(g), node_size=1000)
#show()
"""