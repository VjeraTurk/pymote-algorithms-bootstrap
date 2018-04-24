# -*- coding: utf-8 -*-
#from pymote.sensor import Sensor
from pymote.algorithms.tinagojak.saturation import Saturation
from pymote.message import Message


class Eccentricities(Saturation):
    #required_params = ('dataKey',) 
    default_params = {'distKey': 'Distance', 'eccKey': 'Eccentricity'}

    def processing(self,node,message):
        Saturation.processing(self, node, message)

        if message.header=="Resolution":
            self.resolve(node, message)

    def done(self, node):
        pass
           
    def initialize(self, node):
        node.memory[self.distKey] = {}
        for n in node.memory[self.neighborsKey]:
            node.memory[self.distKey][node] = 0
    
    def prepare_message(self,node):
        maxDist = 1 + max(node.memory[self.distKey].values())
        return maxDist
  
    def process_message(self,node,message):
        node.memory[self.distKey][message.source] = message.data
    
    def resolve(self,node, message):
        self.process_message(node, message)
        self.calculate_eccentricity(node, message)

        nodes = list(node.memory[self.neighborsKey])
        nodes.remove(node.memory[self.parentKey])
        for n in nodes:
            distances = dict(node.memory[self.distKey])
            del distances[n]
            maxdist = 1 + max(distances.values())
            node.send(Message(header='Resolution', data=maxdist, destination=n))    

        node.status = 'DONE'

                                                 
    def calculate_eccentricity(self,node,message):
        node.memory[self.eccKey] = max(node.memory[self.distKey].values())            #eccentricity cvora

    
    STATUS = {
              'DONE' : done,
              'AVAILABLE': Saturation.STATUS.get('AVAILABLE'),
              'ACTIVE': Saturation.STATUS.get('ACTIVE'),
              #'PROCESSING':Saturation.STATUS.get('PROCESSING'), #staje u saturated
              'PROCESSING': processing, #ide u maximum/lower
              'SATURATED': Saturation.STATUS.get('SATURATED'),
    }