# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 15:14:29 2018

@author: admin
"""
from pymote.algorithms.turk2018.saturation import Saturation
from pymote.algorithm import Message

class FindEccentricities(Saturation):

    default_params = {'distKey':'Distance','eccKey':'eccentricity'}

    def processing(self,node,message):
        Saturation.processing(self, node, message)            
        if message.header=="Resolution":
            self.resolve(node, message)
            
  
    def initialize(self, node):
        node.memory[self.distKey]={}
        
        for n in node.memory[self.neighborsKey]: #Distances[x]
            node.memory[self.distKey][n]=0               
        #print node.memory[self.distKey].values()

    def prepare_message(self,node):
        return 1+max(node.memory[self.distKey].values())
   
    def resolve(self,node,message):
        self.process_message(node, message)
        self.calculate_eccentricity(node,message)
        
        #ys = list(node.memory[self.neigbourKey]).remove(message.source)
        ys = list(node.memory[self.neighborsKey])
        ys.remove(node.memory[self.parentKey])
        for y in ys:
            z = dict(node.memory[self.distKey])
            del z[y]
            node.send(Message(header='Resolution', data=1+max(z.values()), destination=y))
        
        node.status = 'DONE'
        
        #destination_nodes = list(node.memory[self.neighborsKey]) ##list() kao ključna izmjena?!
        #destination_nodes.remove(node.memory[self.parentKey])
        #node.send(Message(header='Resolution', data=node.memory[self.maxDist], destination=destination_nodes))        
                
    def process_message(self,node,message):
        node.memory[self.distKey][message.source]=message.data
  
    def calculate_eccentricity(self,node,message):
        node.memory[self.eccKey]=max(node.memory[self.distKey].values())
    
    def done():
        pass
    
    STATUS = {
              'AVAILABLE': Saturation.STATUS.get('AVAILABLE'),
              'ACTIVE': Saturation.STATUS.get('ACTIVE'),
              #'PROCESSING':Saturation.STATUS.get('PROCESSING'), #staje u saturated
              'PROCESSING': processing, #ide u maximum/lower
              'DONE': done,
             }        