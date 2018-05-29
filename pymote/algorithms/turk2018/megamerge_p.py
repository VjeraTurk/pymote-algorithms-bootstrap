# -*- coding: utf-8 -*-
#18:17
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from random import random
import collections
from sys import maxint

class MegaMerger(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors', 'treeKey': 'TreeNeighbors', 'parentKey' : 'Parent', 'weightKey': 'Weight',
    'levelKey': 'Level', 'nameKey': 'Name', 'debugKey': 'DEBUG' , 'linkStatusKey':'LinkStatus', 'nodeEdgeKey': 'MinimumEdgeNode',
    'reportCounterKey': 'ReportCounter', 'numberOfInternalNodesKey': 'NumberOfInternalNodes'}

    def initializer(self):
        ini_nodes = []
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
           #node.memory[self.treeKey] = list(node.memory[self.neighborsKey])
            self.initialize(node)
            node.status = 'AVAILABLE'
            '''if random()<0.3:                #random initializers
                node.status = 'AVAILABLE'
                ini_nodes.append(node)'''

        # just for testing purposes
        '''node = self.network.nodes()[0]
        node.memory[self.levelKey] = 3
        node2 = self.network.nodes()[1]
        node2.memory[self.levelKey] = 1
        node2.memory[self.numberOfInternalNodesKey] = 1
        node4 = self.network.nodes()[3]
        node4.memory[self.levelKey] = 1
        node4.memory[self.parentKey] = node2
        node4.memory[self.nameKey] = node2.memory[self.nameKey]
        node4.memory[self.numberOfInternalNodesKey] = 1
        node4.memory[self.linkStatusKey][node2] = 'INTERNAL'
        node2.memory[self.linkStatusKey][node4] = 'INTERNAL'
        node4.status = 'PROCESSING'''

        node = self.network.nodes()[0]
        node.memory[self.levelKey] = 4
        node.memory[self.numberOfInternalNodesKey] = 2
        #for (k,v in node.memory[self.linkStatusKey])
        node2 = self.network.nodes()[1]
        node2.memory[self.levelKey] = 4
        node2.memory[self.numberOfInternalNodesKey] = 1
        node6 = self.network.nodes()[5]
        node6.memory[self.levelKey] = 4
        node6.memory[self.numberOfInternalNodesKey] = 2
        node4 = self.network.nodes()[3]
        node4.memory[self.levelKey] = 4
        node4.memory[self.numberOfInternalNodesKey] = 1
        node2.memory[self.parentKey] = node
        node6.memory[self.parentKey] = node4
        node.memory[self.parentKey] = node6
        node2.memory[self.nameKey] = node4.memory[self.nameKey]
        node6.memory[self.nameKey] = node4.memory[self.nameKey]
        node.memory[self.nameKey] = node4.memory[self.nameKey]
        node.memory[self.linkStatusKey][node2] = 'INTERNAL'
        node.memory[self.linkStatusKey][node6] = 'INTERNAL'
        node2.memory[self.linkStatusKey][node] = 'INETRNAL'
        node6.memory[self.linkStatusKey][node] = 'INTERNAL'
        node6.memory[self.linkStatusKey][node4] = 'INTERNAL'
        node4.memory[self.linkStatusKey][node6] = 'INTERNAL'
        node3 = self.network.nodes()[2]
        node3.memory[self.levelKey] = 6
        node2.status = 'PROCESSING'
        node6.status = 'PROCESSING'
        node4.status = 'PROCESSING'

        # starting node has lover lvl for absorpton to work
        
        ini_nodes.append(self.network.nodes()[0])
        
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))  # to je spontani impuls
        
        
        # ne znam kako radi ovaj ini_nodes YOLO
        #ini_node = self.network.nodes()[1]                                                         ### 0. ili 1. imalvl 1? odluci se
        #self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))

    def available(self, node, message):

        #inicijatori
        if message.header == NodeAlgorithm.INI: #Spontaneously
            # koristimo za test absorptiona
            #prepared_data = self.prepare_message_data_concatenate(node)
            #for testing send Let us merge to the first neighbor.
            #node.send(Message(header='Let Us Merge', data=0, destination=node.memory[self.neighborsKey][0]))
            #node.send(Message(header='Let Us Merge', data=0, destination=node.memory[self.neighborsKey][1])) 
            ## Iskljucivo inicijatori, bilo jedan ili svi poslat ce svom prvom i drugm susjedu Let Us Merge


            '''node.memory[self.nodeEdgeKey] = self.min_weight(node)
            node.send(Message(header='Outside?', data=0, destination=node.memory[self.nodeEdgeKey]))'''

            node.memory[self.nodeEdgeKey] = node.memory[self.weightKey].keys()[0]
            node.send(Message(header='Outside?', data=0, destination=node.memory[self.nodeEdgeKey]))

        if message.header=='Outside?':
            if message.source.memory[self.nameKey]==node.memory[self.nameKey]:
                node.send(Message(header='Internal', data=0, destination=message.source))
                self.change_link_status_key_internal(node, message.source)
            elif node.memory[self.levelKey] >= message.source.memory[self.levelKey]:
                node.send(Message(header='External', data=0, destination=message.source))
                self.change_link_status_key_external(node, message.source)
            else:
                # TODO internal external suspension
                pass

        # ja ne kuzim kako rade ovi statusi stvarno
        if message.header=="Let Us Merge":
            #self.process_message_check_levels(node,message)
            #self.resolve(node, message)
            pass

        node.status = 'PROCESSING'

        '''node.send(Message(header='Activate', data='Activate'))
        if len(node.memory[self.neighborsKey])==1 : #ako je čvor list
            node.memory[self.parentKey] = list(node.memory[self.neighborsKey])[0]
            updated_data=self.prepare_message(node)
            node.send(Message(header='M', data = updated_data, destination = node.memory[self.parentKey]))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE' #izvrši se

    if message.header == 'Activate':
        destination_nodes = list(node.memory[self.treeKey])

        destination_nodes.remove(message.source)
        node.send(Message(header='Activate', data='Activate', destination=destination_nodes))
        if len(node.memory[self.treeKey])==1 :
            node.memory[self.parentKey] = list(node.memory[self.treeKey])[0]
            updated_data=self.prepare_message(node)
            node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
            node.status = 'PROCESSING'
        else:
            node.status='ACTIVE' #izvrši se'''

    def active(self, node, message):
        '''if message.header=='M':
            self.process_message(node,message)
            node.memory[self.treeKey].remove(message.source)
            if len(node.memory[self.treeKey])==1 :
                node.memory[self.parentKey] = list(node.memory[self.treeKey])[1]
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
                node.status = 'PROCESSING' '''
        pass

    def processing(self, node, message):
        #TODO add Outside? for other nodes, not just INI_NODES
        if message.header=="Let_us_merge":
            # izradi novu funkciju!
            self.process_message_check_levels(node,message)
            #self.resolve(node, message)

        if message.header=="absorption+orientation_of_roads" or message.header=="absorption":
            
            node.memory[self.nameKey] = message.source.memory[self.nameKey]
            node.memory[self.levelKey] = message.source.memory[self.levelKey]
            self.absorption(node, message)
            if message.header=="absorption+orientation_of_roads":
                #REDOSLJED FUNKCIJA MORA BITI OVAKAV. Prvo posaljemo parentu poruku, onda maknemo parenta.
                self.absorption(node, message, False, True)
                node.memory[self.parentKey] = message.source

        #TODO or internal external suspension
        if message.header=="Internal":
            self.change_link_status_key_internal(node, message.source)
        elif message.header=="External":
            self.change_link_status_key_external(node, message.source)
            if node.memory[self.parentKey]!=None:
                node.send(Message(header='Report', data=0, destination=node.memory[self.parentKey]))
            else:
                #when merging egde is also downtown
                node.send(Message(header="Let_us_merge" ,data=0, destination=message.source))
                pass

        if message.header=="Report":
            node.memory[self.reportCounterKey] += 1
            node.memory[self.nodeEdgeKey] = self.min_weight_two_nods(node.memory[self.nodeEdgeKey], message.source.memory[self.nodeEdgeKey])
            # -1 is for parent node
            if (node.memory[self.reportCounterKey]==node.memory[self.NumberOfInternalNodes]-1):
                if node.memory[self.parentKey]==None:
                    pass
                    #TODO Let us Merge send to merging edge/node from Downtown
                else:
                    node.send(Message(header='Report', data=0, destination=node.memory[self.parentKey]))
                node.memory[self.reportCounterKey] = 0

    def saturated(self, node):
        pass

    def prepare_message(self,node):
        pass

    '''def prepare_message_data_concatenate(self, node):
      
        args = {self.nameKey: node.memory[self.nameKey], self.levelKey: node.memory[self.levelKey]}
        #data = ",".join(args)
        return args'''

    def process_message(self, node, message):
        pass

    def process_message_check_levels(self, node, message):
        node.memory[self.debugKey] = "tu sam"
        if message.source.memory[self.levelKey] < node.memory[self.levelKey]:
            self.absorption(node, message, True)

    def change_link_status_key_internal(self, node, message_source):
        node.memory[self.linkStatusKey][message_source] = "INTERNAL"
        node.memory[self.numberOfInternalNodesKey] += 1
    def change_link_status_key_external(self, node, message_source):
        node.memory[self.linkStatusKey][message_source] = "EXTERNAL"

    def absorption(self, node, message, param_begining=False, orientation_of_roads=False):
        if node.memory[self.linkStatusKey][message.source]=='EXTERNAL':
            self.change_link_status_key_internal(node, message.source)
        if param_begining==True:
            node.send(Message(header="absorption+orientation_of_roads", data=0, destination=message.source))
        else:
            if orientation_of_roads==True:
                if node.memory[self.parentKey]!=None:
                    node.send(Message(header="absorption+orientation_of_roads", data=0, destination=node.memory[self.parentKey]))
                else:
                    # DEBUG
                    node.memory[self.debugKey] = "Nemam parenta"
            else:
                #TODO mising internal, exernal
                destination_nodes = list(filter(lambda neighbor:  neighbor != node.memory[self.parentKey] and neighbor != message.source, node.memory[self.neighborsKey])) 
                node.send(Message(header="absorption", data=0, destination=destination_nodes))

    def initialize(self, node):
        node.memory[self.weightKey] = {}
        node.memory[self.linkStatusKey] = {}
        node.memory[self.levelKey] = 0
        node.memory[self.nameKey] = node.id
        node.memory[self.parentKey] = None
        node.memory[self.reportCounterKey] = 0
        node.memory[self.numberOfInternalNodesKey] = 0
        # definirati nobi vbor sa -id em
        node.memory[self.nodeEdgeKey] = {"INFINITE":[maxint, maxint]}
        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [min(node.id, neighbor.id),
            max(node.id, neighbor.id)]

        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [min(node.id, neighbor.id),max(node.id, neighbor.id)]
            node.memory[self.linkStatusKey][neighbor] = "UNUSED"


    def min_weight(self,node): 
        orderedDict = collections.OrderedDict(sorted(node.memory[self.weightKey].iteritems(), key=lambda (k,v):v[0]))            
        min_1= orderedDict.values()[0][0]
        print(min_1)        
        uzi_izbor={}

#        print("sortirano 1 ")               
        for o in orderedDict:
            #print orderedDict[o]
            if orderedDict[o][0] == min_1:
                uzi_izbor.update({o:orderedDict[o]})
    
        orderedDict = collections.OrderedDict(sorted(uzi_izbor.iteritems(), key=lambda (k,v):v[1]))       
#        print("sortirano 2")
#        for o in orderedDict:
#            print orderedDict[o]
        return orderedDict.keys()[0]    

    def min_weight_two_nods(self, weight_node_a, weight_node_b):
        if weight_node_a[0]<weight_node_b[0]:
            return weight_node_a
        elif weight_node_a>weight_node_b[0]:
            return weight_node_b
        elif weight_node_a[1]<weight_node_b[1]:
            return weight_node_a
        else:
            return weight_node_b

    STATUS = {
              'AVAILABLE': available,
              'PROCESSING': processing,
              'SATURATED': saturated,
             }