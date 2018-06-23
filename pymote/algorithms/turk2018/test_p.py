from pymote import NetworkGenerator
from pymote.npickle import read_pickle, write_pickle
from networkx import minimum_spanning_tree
#from pymote.algorithms.MegaMeger import MegaMerger
from pymote.algorithms.turk2018.megamerge_p import MegaMerger
from pymote.simulation import Simulation
from networkx import draw, Graph
from pylab import show


net = read_pickle("poslati.txt")
write_pickle(net, 'bezAlg.tar.gz')

#net.algorithms = (MegaMerger,)
#write_pickle(net, 'saAlg.txt')

g = Graph()
g.add_edge(net.nodes()[0],net.nodes()[1],weight=1)
g.add_edge(net.nodes()[0],net.nodes()[2],weight=2)
g.add_edge(net.nodes()[0],net.nodes()[5],weight=3)
g.add_edge(net.nodes()[2],net.nodes()[6],weight=4)
g.add_edge(net.nodes()[3],net.nodes()[5],weight=5)
g.add_edge(net.nodes()[4],net.nodes()[6],weight=6)
g.add_edge(net.nodes()[6],net.nodes()[7],weight=7)

#dodatni, da naprave razliku
g.add_edge(net.nodes()[3],net.nodes()[4],weight=8)
g.add_edge(net.nodes()[5],net.nodes()[7],weight=9)
g.add_edge(net.nodes()[1],net.nodes()[2],weight=10)

#draw(g)
#show()

net.adj=g.adj
net.show()

#Uses Kruskal’s algorithm.
#If the graph edges do not have a weight attribute 
#a default weight of 1 will be used.

mst = minimum_spanning_tree(net)

net.adj=mst.adj
net.show()
