# -*- coding: utf-8 -*-
from pymote.sensor import Sensor
from pymote.algorithms.saturation import Saturation
from pymote.message import Message
import random

class TempSensor(Sensor):

    """Provides measured temperature on node."""

    def read(self, node):
        '''return {'Temperature': round(random.uniform(0, 100), 2)}'''
        return {'Temperature': round(random.uniform(0, 100), 2)}


class MaxFind(Saturation):
    #required_params = ('dataKey',) 
    default_params = {'temperatureKey':'Temperature','maxKey':'Max'}

    def processing(self,node,message):
        # if message.header=="M":
        #     self.process_message(node,message)
        #     #node.status = 'SATURATED'
        #     self.resolve(node)
        Saturation.processing(self, node, message)
            
        if message.header=="Notification":
            self.resolve(node, message)

            # destination_nodes = list(node.memory[self.neighborsKey])
           
            # self.process_message(node,message)
            # destination_nodes.remove(node.memory[self.parentKey])            
           
            
            # node.send(Message(header='Notification', data=node.memory[self.maxKey], destination=destination_nodes))
            
            # #if node.memory[self.temperatureKey]==message.data:
            # if node.memory[self.temperatureKey] == node.memory[self.maxKey]:
            #     node.status="MAX"
            # else:
            #     node.status="LOWER"
    
    def initialize(self, node):
        node.compositeSensor=(TempSensor,'Temperature')
        node.memory[self.temperatureKey]=node.compositeSensor.read()['Temperature']
        node.memory[self.maxKey]=node.memory[self.temperatureKey]   
    
    def prepare_message(self,node):
        return node.memory[self.maxKey]
                   
    def process_message(self,node,message):
        if message.data>node.memory[self.maxKey]:
            node.memory[self.maxKey] = message.data
    
    def resolve(self,node, message):
        
        destination_nodes = list(node.memory[self.neighborsKey])
        destination_nodes.remove(node.memory[self.parentKey]) #garantira topologiju 

        self.process_message(node, message)
        node.send(Message(header='Notification', data=node.memory[self.maxKey], destination=destination_nodes))        
        print ('DATA', node.memory[self.maxKey])
        if node.memory[self.temperatureKey] == node.memory[self.maxKey]:
            node.status='MAX'
        else :
            node.status='LOWER'
    
                                                 
    def maximum(self,node,message):
        pass
    def lower(self,node,message):
        pass
    
    STATUS = {
              'MAX' : maximum,
              'LOWER' : lower,
              'AVAILABLE': Saturation.STATUS.get('AVAILABLE'),
              'ACTIVE': Saturation.STATUS.get('ACTIVE'),
              #'PROCESSING':Saturation.STATUS.get('PROCESSING'), #staje u saturated
              'PROCESSING': processing, #ide u maximum/lower
              'SATURATED': Saturation.STATUS.get('SATURATED'),
    }