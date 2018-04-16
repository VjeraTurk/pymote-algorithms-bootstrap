# -*- coding: utf-8 -*-
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message

class Saturation(NodeAlgorithm): 
    
    #required_params = ('informationKey', 'treeKey',) # must have ','
    required_params = ('informationKey',) # must have ','
    default_params = {'neighborsKey': 'Neighbors', 'treeNeighbors': 'Neighbors','parentKey' : 'Parent', 'treeKey': 'Tree'}

    #TODO: treeKey now serves as treeNeighbors, and treeNeighbors as treeKey - necessary to SWAP them
    #      should treeKey be in required_params?!
    
    def initializer(self):
        ini_nodes = []
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.memory[self.treeNeighbors] = node.compositeSensor.read()['Neighbors']
            node.memory[self.treeKey]= list(node.memory[self.treeNeighbors])
            self.initialize(node)
            node.status = 'AVAILABLE'
            if self.informationKey in node.memory:
                node.status = 'AVAILABLE'
                ini_nodes.append(node)
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))  # to je spontani impuls   

        
    def available(self, node, message):

        #inicijatori
        if message.header == NodeAlgorithm.INI: #Spontaneously
            node.send(Message(header='Activate', data='Activate'))
            #initialize() mislim da ipak treba biti u initalizeru
            if len(node.memory[self.treeNeighbors])==1 : #ako je čvor list
                node.memory[self.parentKey] = list(node.memory[self.treeNeighbors])
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data = updated_data, destination = node.memory[self.parentKey]))
                node.status = 'PROCESSING'
            else:
                node.status = 'ACTIVE' #izvrši se
                
        if message.header == 'Activate':
            destination_nodes = list(node.memory[self.treeNeighbors])
            print "message.source:"
            print type(message.source)
            print message.source
            
            node.send(Message(header='Activate', data='Activate', destination=destination_nodes.remove(message.source)))
            #initialize() mislim da ipak treba biti u initalizeru            
            if len(node.memory[self.treeNeighbors])==1 :
                node.memory[self.parentKey] = list(node.memory[self.treeNeighbors])                
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
                #dal prepare?
                node.status = 'PROCESSING'
            else:
                node.status='ACTIVE' #izvrši se
    
    def active(self, node, message):  
        

        if message.header=='M':
            self.process_message(node,message)
            ###ključno
            node.memory[self.treeNeighbors].remove(message.source) # ne radi?

            ##izgleda da neki ostanu bez susjeda kao posljedica ovoga, ne, trebali bi uci u processing jopš u availabele
            
            if len(node.memory[self.treeNeighbors])==1 :
                node.memory[self.parentKey] = list(node.memory[self.treeNeighbors])                
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
                node.status = 'PROCESSING'

    def processing(self, node, message):
        if message.header=="M":           
            self.process_message(node,message)
            #self.resolve(node)
            node.status='SATURATED'
        #if message.header=="Notification":
            #print "Nebi smio biti tu"
            
    def prepare_message(self,node):
        raise NotImplementedError
        
    def process_message(self, node, message):
        raise NotImplementedError

    def initialize(self, node):
        raise NotImplementedError
                
    def resolve(self,node):
        raise NotImplementedError
        
    STATUS = {
              'AVAILABLE': available,
              'ACTIVE': active,
              'PROCESSING': processing,
              'SATURATED': resolve,
             }
