# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 17:21:20 2018

@author: admin
"""

#%load_ext autoreload
#%autoreload 2
#%reload_ext autoreload
from pymote import NetworkGenerator
from pymote.npickle import read_pickle, write_pickle
from networkx import minimum_spanning_tree, prim_mst_edges, prim_mst, spring_layout
from pymote.network import Network
from pymote.simulation import Simulation
from networkx import draw, Graph,  draw_networkx_edges, draw_networkx_edge_labels, get_node_attributes
from pylab import show, figure
import random

#from pymote.algorithms.turk2018.megamerge_p import MegaMerger
from pymote.algorithms.turk2018.megamerge import MegaMerger

test_net = net = read_pickle('RandomBezAlg.tar.gz')
test_net = net = read_pickle('WorstCaseBezAlg.tar.gz')
net.show()


net.algorithms = (MegaMerger,)
write_pickle(net, 'RandomSAlg.tar.gz')
write_pickle(net, 'WorstCaseSAlg.tar.gz')
##s ovom mrezom pokretati GUI simulator

g = Graph()
g.adj=net.adj

#Uses Kruskal’s algorithm.
#If the graph edges do not have a weight attribute 
#a default weight of 1 will be used.
#test_graph = minimum_spanning_tree(net)
test_graph=prim_mst(net)
test_net.adj=test_graph.adj
test_net.show()
test_sum=test_net.size(weight='weight')
print("MST Sum %f" % (test_sum))



sim = Simulation(net)
sim.run()

exclude = list()
exclude.append('Neighbors')

for node in net.nodes():

    print node.id, node.status       
    for key in node.memory:
        print key, ':\t',node.memory[key]
        
        #for value in node.memory[key]:
         #   print value
 
    print  "\n"