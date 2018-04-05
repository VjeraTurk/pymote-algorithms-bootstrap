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
        node.memory[self.maxKey]=node.memory[self.temperatureKey]      
        #trenutna najveća je njegova, jedina koju ima    
        return node.memory[self.maxKey] is not None

    def initiator_data(self, node):
        return node.memory[self.maxKey]
        #ovdje ne smije biti read, jer bi svaki puta očitao drugačiju temperaturu
                      
    def handle_flood_message(self, node, message):
        
        if message.data > node.memory[self.maxKey]:
            node.memory[self.maxKey]=message.data
            return message.data


    STATUS = {'FLOODING':FloodingUpdate.STATUS.get('FLOODING'),  # init,term
              }