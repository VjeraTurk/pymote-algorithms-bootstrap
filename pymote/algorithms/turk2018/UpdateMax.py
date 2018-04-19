from pymote.algorithms.niculescu2003.floodingupdate import FloodingUpdate
#from pymote.algorithms.floodingupdate import FloodingUpdate
from pymote.sensor import TempSensor

class MaxFind(FloodingUpdate):
    #required_params = ('dataKey',) 
    default_params = {'temperatureKey':'Temperature','neighborsKey': 'Neighbors','maxKey':'Max'}
    def initiator_condition(self, node):
        #svi ce biti iniciatori        
        node.compositeSensor=(TempSensor,'Temperature')
        node.memory[self.temperatureKey]=node.compositeSensor.read()['Temperature']
        node.memory[self.maxKey]=node.memory[self.temperatureKey]      
        #trenutna najveca je njegova, jedina koju ima    
        return node.memory[self.maxKey] is not None

    def initiator_data(self, node):
        #node.memory[self.msgKey] = 1
        return node.memory[self.maxKey]
        #ovdje ne smije biti read, jer bi svaki puta ocitao drugaciju temperaturu
                      
    def handle_flood_message(self, node, message):
        
        if message.data > node.memory[self.maxKey]:
            node.memory[self.maxKey]=message.data
            #node.memory[self.msgKey]=node.memory[self.msgKey]+1
            #node.memory[self.msgKey]=node.memory[self.msgKey]+
            return message.data


    STATUS = {'FLOODING':FloodingUpdate.STATUS.get('FLOODING'),  # init,term
              
             }