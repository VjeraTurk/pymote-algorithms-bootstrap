# -*- coding: utf-8 -*-
#%load_ext autoreload
#%autoreload 2
from pymote.networkgenerator import NetworkGenerator
from pymote.simulation import Simulation

net_gen = NetworkGenerator(5)

net = net_gen.generate_random_network()

from pymote.algorithms.UpdateMax import MaxFind 
net.algorithms = ( (MaxFind, {'dataKey':'D'}), )

#nije potrebno, po algoritmu su svi init
#for node in net.nodes():
#    node.memory['D']='init'

sim = Simulation(net)
sim.run()

for node in net.nodes():
    print node.memory
    print node.status