# -*- coding: utf-8 -*-
from pymote.sensor import Sensor
from pymote.algorithms.turk2018.saturation import Saturation
from pymote.message import Message
import random

class TempSensor(Sensor):
    
    def read(self,node):
        return{'Temperature': random.randrange(-15,40,1)}
  

class MaxFind(Saturation):
    #required_params = ('dataKey',) 
    default_params = {'temperatureKey':'Temperature','maxKey':'Max'}

    def processing(self,node,message):
        if message.header=="M":
            self.process_message(node,message)
            #node.status = 'SATURATED'
            self.resolve(node)
            
        if message.header=="Notification":
            destination_nodes = node.memory[self.treeKey]
            print destination_nodes
            print node.memory[self.parentKey]
            print type(node.memory[self.parentKey])
            print node.memory[self.parentKey][0]
            
            self.process_message(node,message)
            destination_nodes.remove(node.memory[self.parentKey][0])            
            
            node.send(Message(header='Notification', data=node.memory[self.maxKey], destination=destination_nodes))
            
            if node.memory[self.temperatureKey]==message.data:
                node.status="MAXIMUM"
            else:
                node.status="SMALLER"
    
    def initialize(self, node):
        node.compositeSensor=(TempSensor,'Temperature')
        node.memory[self.temperatureKey]=node.compositeSensor.read()['Temperature']
        node.memory[self.maxKey]=node.memory[self.temperatureKey]   
        #return node.memory[self.maxKey] is not None    
    
    def prepare_message(self,node):
        return node.memory[self.maxKey]
                   
    def process_message(self,node,message):
        #print message.data
        if message.data>node.memory[self.maxKey]:
            node.memory[self.maxKey] = message.data
    
    def resolve(self,node):
        print "TU SAM"
        destination_nodes = node.memory[self.treeKey]
        #print destination_nodes
        #print node.memory[self.parentKey]
        destination_nodes.remove(node.memory[self.parentKey][0]) #garantira topologiju        
        
        node.send(Message(header='Notification', data=node.memory[self.maxKey], destination=destination_nodes))        

        if node.memory[self.temperatureKey] == node.memory[self.maxKey]:
            node.status='MAXIMUM'
        else :
            node.status='SMALLER'
    
                                                 
    def mini(self,node,message):
        print "MAXIMUM"
    def larger(self,node,message):
        print "SMALLER"
    
    STATUS = {
              'MAXIMUM' : mini,
              'SMALLER' : larger,
              'AVAILABLE': Saturation.STATUS.get('AVAILABLE'),
              'ACTIVE': Saturation.STATUS.get('ACTIVE'),
              #'PROCESSING':Saturation.STATUS.get('PROCESSING'), #redefinirali smo processing
              'PROCESSING':processing, #redefinirali smo processing
              #'SATURATED':Saturation.STATUS.get('SATURATED'),
              'SATURATED':resolve,
        
        #svaka metoda vezana uz status mora imati self,node,message
        #procedure primaju self po defaultu kao prvi argument, 
        #ako je procedura definirana kao def procedura(self,node) 
        #krivo je zvati self.procedura(self,node), 
        #ispravno je     self.procedura(node)
             }    