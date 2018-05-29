from pymote import NetworkGenerator
from pymote.npickle import write_pickle, read_pickle
from pymote.simulation import Simulation
from networkx import minimum_spanning_tree

net_gen = NetworkGenerator(5)
net = net_gen.generate_random_network()
#graph_tree = minimum_spanning_tree(net)
#net.adj = graph_tree.adj

#from pymote.algorithms.turk2018.megamerge_p import MegaMerger
from pymote.algorithms.turk2018.megamerge import MegaMerger

#read_pickle(net,'mrezaLanac.gz')
#write_pickle(net,'mreza.tar.gz')
net.algorithms = (MegaMerger, )
write_pickle(net,'mreza.tar.gz')

#net.show()

sim = Simulation(net)
sim.run()

exclude = list()
exclude.append('Neighbors')

for node in net.nodes():

    print node.id
    print node.status       
    for key in node.memory:
        print key, ':',node.memory[key]
        
        #for value in node.memory[key]:
         #   print value
 
    print  "\n"
        
    #print [value for key, value in node.memory.items() if key not in exclude]
	#print (node.id, node.status, node.memory['Eccentricity'], node.memory['Distance'])	
	#print (node.id, node.status, node.memory['Parent'])