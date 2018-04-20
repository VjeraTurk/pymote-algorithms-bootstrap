# -*- coding: utf-8 -*-
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from random import random

class Saturation(NodeAlgorithm): 
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors', 'treeKey': 'TreeNeighbors', 'parentKey' : 'Parent'}

    def initializer(self):
        ini_nodes = []
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.memory[self.treeKey] = list(node.memory[self.neighborsKey])
            self.initialize(node)
            node.status = 'AVAILABLE'
            if random()<0.3: #random initializers
                ini_nodes.append(node)
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))  # to je spontani impuls   

        
    def available(self, node, message):
        #inicijatori
        if message.header == NodeAlgorithm.INI: #Spontaneously
            node.send(Message(header='Activate', data='Activate'))
            if len(node.memory[self.neighborsKey])==1 : #ako je čvor list
                node.memory[self.parentKey] = list(node.memory[self.neighborsKey])[0] ## [0]
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data = updated_data, destination = node.memory[self.parentKey]))
                node.status = 'PROCESSING'
            else:
                node.status = 'ACTIVE'
                
        if message.header == 'Activate':
            destination_nodes = list(node.memory[self.neighborsKey]) ##treeKey?
            destination_nodes.remove(message.source)
            node.send(Message(header='Activate', data='Activate', destination=destination_nodes))
            if len(node.memory[self.treeKey])==1 :
                node.memory[self.parentKey] = list(node.memory[self.treeKey])[0]
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
                node.status = 'PROCESSING'
            else:
                node.status='ACTIVE'
    
    def active(self, node, message):
        
        if message.header=='M':
            self.process_message(node,message)
            node.memory[self.treeKey].remove(message.source) #cijepa
            if len(node.memory[self.treeKey])==1 :
                node.memory[self.parentKey] = list(node.memory[self.treeKey])[0]
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
                node.status = 'PROCESSING'

    def processing(self, node, message):
        if message.header=="M":           
            self.process_message(node,message)
            self.resolve(node, message)
            #processing prima self,
            #pozvati ce se process_message i resolve primljene klase (self)

    def saturated(self, node):
        pass

    def prepare_message(self, node):
        pass
        
    def process_message(self, node, message):
        pass

    def initialize(self, node):
        pass
                
    def resolve(self, node, message):
        node.status='SATURATED'
        #pass #nuzno?
        
    STATUS = {
              'AVAILABLE': available,
              'ACTIVE': active,
              'PROCESSING': processing,
              'SATURATED': saturated,
             }