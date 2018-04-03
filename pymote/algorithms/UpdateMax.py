# -*- coding: utf-8 -*-
from pymote.algorithms.floodingupdate import FloodingUpdate
from pymote.sensor import TempSensor, NeighborsSensor

class MaxFind(FloodingUpdate):
    #required_params = ('dataKey',) 
    default_params = {'temperatureKey':'Temperature','neighborsKey': 'Neighbors','maxKey':'Max'}

    def initiator_condition(self, node):
#svi će biti iniciatori        
        node.compositeSensor=(TempSensor,'Temperature')
        node.memory[self.temperatureKey]=node.compositeSensor.read()['Temperature']
        return node.memory[self.temperatureKey] is not None
        
#        if self.dataKey in node.memory:
##            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbor']
##            node.compositeSensor = (TempSensor, 'Temperature', NeighborsSensor, 'Neighbor' )       
##            node.memory[self.temperatureKey] = node.compositeSensor.read()['Temperature']
#            node.compositeSensor=(TempSensor,'Temperature')            
#            node.memory[self.temperatureKey]=node.TempSensor.read()
#            return True
#        else:
#            return False

    def initiator_data(self, node):
        return node.memory[self.temperatureKey]
        #ovdije ne smije biti read, jer bi svaki puta očitao drugačiju temperaturu
               
       

    def handle_flood_message(self, node, message):
        if message.data>node.memory[self.temperatureKey]:
            node.memory[self.maxKey]=message.data
            return message.data
        #else:
        #    return node.memory[self.temperatureKey]
        
                
        #usporedi sa svojom temperaturom
        #message=veća