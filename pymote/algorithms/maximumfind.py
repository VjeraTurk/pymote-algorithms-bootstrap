# -*- coding: utf-8 -*-
from pymote.sensor import TempSensor
from pymote.message import Message
from pymote.algorithms.saturation import Saturation

class MaxFind(Saturation):
    #required_params = ('dataKey',) 

    default_params = {'temperatureKey':'Temperature','maxKey':'Max'}

    def processing(self,node,message):
        
        if message.header=="M":
            print "MMM"
        
        if message.header=="Notification":
            destination_nodes = list(node.memory[self.neighborsKey])
            destination_nodes.remove(node.memory[self.parentKey])
            node.send(Message(header='Notification', data='Notification'))
            if node.memory[self.TempKey]==message.data:
                node.status="MAXIMUM"
            else:
                node.status="SMALLER"
    
    def initialize(self, node):
        node.compositeSensor=(TempSensor,'Temperature')
        node.memory[self.temperatureKey]=node.compositeSensor.read()['Temperature']
        node.memory[self.maxKey]=node.memory[self.temperatureKey]   
        #return node.memory[self.maxKey] is not None    
        print node.memory[self.maxKey]
    
    def prepare_message(self,node):
        return node.memory[self.maxKey]
                   
    def process_message(self,node,message):
        if message.data>node.memory[self.maxKey]:
            node.memory[self.maxKey] = message.data
    
    def resolve(self,node):
        destination_nodes = list(node.memory[self.neighborsKey])
        destination_nodes.remove(node.memory[self.parentKey])
        node.send(Message(header='Resolution', data=node.memory[self.maxKey]), destination=destination_nodes)
        
        if node.memory[self.temperatureKey] == node.memory[self.maxKey]:
            node.status='MAXIMUM'
        else :
            node.status='SMALL'
                                                 
    def mini():
        print "MAXIMUM"
    def larger():
        print "SMALLER"
    
    STATUS = {
              'MAXIMUM' : mini,
              'SMALLER' : larger,
              'AVAILABLE': Saturation.STATUS.get('AVAILABLE'),
              'ACTIVE': Saturation.STATUS.get('ACTIVE'),
              'PROCESSING':processing, #redefinirali smo processing
              'SATURATED':Saturation.STATUS.get('SATURATED'),
             }    