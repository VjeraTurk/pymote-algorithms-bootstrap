# -*- coding: utf-8 -*-
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from random import random
import collections
import sys

class MegaMerger(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors', 'inBranchKey': 'InBranch', 'parentKey' : 'Parent', 'weightKey': 'Weight',
                       'linkStatusKey':'LinkStatus','levelKey': 'Level', 'nameKey': 'Name', 
                      'testEdgeKey':'TestEdge','findCountKey':'FindCount', 'debugKey': 'DEBUG','bestWtKey':'BestWeight'}
                      
    def initializer(self):
        ini_nodes = []
        
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']                        
            self.initialize(node)
            node.status = 'SLEEPING'
            if random()<0.3:                #random initializers
                ini_nodes.append(node)
        #ini_nodes.append(self.network.nodes()[5])
        
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))  # to je spontani impuls
            
        
    def sleeping(self, node, message):
        #inicijatori
        ###(1)
        if message.header == NodeAlgorithm.INI: #Spontaneously
            self.wake_up(node)
            
        ###100%        
        if message.header=="Connect":
            j=message.source      
            self.wake_up(node)
            
            if j.memory[self.levelKey]<node.memory[self.levelKey]:
                 node.memory[self.linkStatusKey][j]='INTERNAL'
                 #send Initiate(LN, FN, SN) on edge j; ja mislim da je to sve sadržano u message.source
                 node.send(Message(header="Initiate", data=node.memory[self.weightKey][j], destination=j)) ##tu smo           
            
            elif node.memory[self.linkStatusKey][j]=='UNUSED':
                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                node.memory[self.levelKey]=node.memory[self.levelKey]+1
                node.status='FIND' #???
                node.send(Message(header="Initiate", data=node.memory[self.weightKey][j], destination=j))
        ###100%
        if message.header=="Test":
            j=message.source            
            self.wake_up(node)

            if j.memory[self.levelKey]>node.memory[self.levelKey]:
                #then place received message on end of queue
                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 
                
            elif node.memory[self.nameKey]!= j.memory[self.nameKey]:
                node.send(Message(header="Accept", data=0, destination=j))
            else:
                if node.memory[self.linkStatusKey][j]=='UNUSED':
                   node.memory[self.linkStatusKey][j]='EXTERNAL'
                   if node.memory[self.testEdgeKey]!=j or node.memory[self.testEdgeKey]==None:
                       node.send(Message(header="Reject", data=0, destination=j))
                   #else :
                       #self.test(node) Tehy send messages only in Find State
                                  
        if message.header=="Initiate":
            self.wake_up(node)      #ja dod                  
            j=message.source
            node.memory[self.levelKey]=j.memory[self.levelKey]            
            node.memory[self.nameKey]=j.memory[self.nameKey]
            node.status=j.status
            print("j.status FIND or FOUND",j.status)
            node.memory[self.inBranchKey]=j
#            node.memory[self.bestEdgeKey]=None
            node.memory[self.bestWtKey]=[sys.maxint,sys.maxint]

            destination_nodes=list()            
            for i in  node.memory[self.linkStatusKey]:
                if i!=j and node.memory[self.linkStatusKey][i]=='INTERNAL':
                    destination_nodes.append(i)
            node.send(Message(header="Initiate", data=0, destination=destination_nodes))
            
            if j=='FIND':
                node.status='FIND'

#        if message.header=="Report":
#            j=message.source
#            if node.memory[self.inBranchKey]!=j:
#                node.memory[self.findCountKey]=node.memory[self.findCountKey]-1
#                if message.data < node.memory[self.bestWtKey]:
#                    node.memory[self.bestWtKey]=message.data
#                    
#                    node.memory[self.bestEdgeKey]=j
#                self.report(node)
#                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 


        if message.header=="Accept":
            j=message.source
            node.memory[self.testEdgeKey]=None
            
            m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])            

            if m==node.memory[self.bestWtKey]:
                node.memory[self.bestEdgeKey]=j
                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
            self.report(node)                
            
#            if node.memory[self.weightKey][j]>node.memory[self.bestWtKey]:
#                node.memory[self.bestEdgeKey]=j
#                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
#            self.report(node)
        
#        if message.header=="Reject":
#            j=message.source
#            if node.memory[self.linkStatusKey][j] == 'UNUSED':  
#                node.memory[self.linkStatusKey][j]='EXTERNAL'
#            self.test(node)

        
    def find(self,node,message):

        ###100%
        if message.header=="Connect":
            j=message.source
            
            if j.memory[self.levelKey]<node.memory[self.levelKey]:
                 node.memory[self.linkStatusKey][j]='INTERNAL'
                 #send Initiate(LN, FN, SN) on edge j; ja mislim da je to sve sadržano u message.source
                 node.send(Message(header="Initiate", data=0, destination=j))
                 node.memory[self.findCountKey]=node.memory[self.findCountKey]+1

            elif node.memory[self.linkStatusKey][j]=='UNUSED':
                #then place received message on end of queue   
                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                node.memory[self.levelKey]=node.memory[self.levelKey]+1
                #node.status='FIND' ##ne znam dal seta sebi status ili samo nodu kojem salje
                node.send(Message(header="Initiate", data=node.memory[self.weightKey][j], destination=j))

        ###100%
        if message.header=="Report":
            j=message.source
            if node.memory[self.inBranchKey]!=j:
                node.memory[self.findCountKey]=node.memory[self.findCountKey]-1
                
                m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
                
                if m==message.data:
                    node.memory[self.bestWtKey]=message.data
                    node.memory[self.bestEdgeKey]=j
                self.report(node)
                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 
                    
            
#                if message.data < node.memory[self.bestWtKey]:
#                    node.memory[self.bestWtKey]=message.data
#                    node.memory[self.bestEdgeKey]=j
#                self.report(node)
#                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 
 

        if message.header=="Initiate":                        
            j=message.source
            node.memory[self.levelKey]=j.memory[self.levelKey]            
            node.memory[self.nameKey]=j.memory[self.nameKey]
            node.status=j.status
            node.memory[self.inBranchKey]=j
            
            #node.memory[self.bestEdgeKey]=None
            node.memory[self.bestWtKey]=[sys.maxint,sys.maxint]

            destination_nodes=list()            
            for i in  node.memory[self.linkStatusKey]:              
                if i!=j and node.memory[self.linkStatusKey][i]=='INTERNAL':
                    
                    destination_nodes.append(i)
                    node.memory[self.findCountKey]=node.memory[self.findCountKey]+1
             
            node.send(Message(header="Initiate", data=0, destination=destination_nodes))
            self.test(node)
        
        if message.header=="Accept":
            j=message.source
            node.memory[self.testEdgeKey]=None

            print("compare",node.memory[self.weightKey][j],node.memory[self.bestWtKey])
            
            m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])            

            if m==node.memory[self.bestWtKey]:
                node.memory[self.bestEdgeKey]=j
                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
            self.report(node) 

#            if node.memory[self.weightKey][j]>node.memory[self.bestWtKey]:
#                node.memory[self.bestEdgeKey]=j
#                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
#            self.report(node)
        
        if message.header=="Reject":
            j=message.source
            if node.memory[self.linkStatusKey][j] == 'UNUSED':   
                node.memory[self.linkStatusKey][j]='EXTERNAL'
            self.test(node)
        
        if message.header=="Test":
            j=message.source
            if j.memory[self.levelKey]>node.memory[self.levelKey]:
                #then place received message on end of queue
                ##veliko pitanje dal ovo radi:
                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 
            elif node.memory[self.nameKey]!= j.memory[self.nameKey]:
                node.send(Message(header="Accept", data=0, destination=j))
            else:
                if node.memory[self.linkStatusKey][j]=='UNUSED':
                   node.memory[self.linkStatusKey][j]='EXTERNAL'
                   if node.memory[self.testEdgeKey]!=j:
                       node.send(Message(header="Reject", data=0, destination=j))
                   else :
                       self.test(node)
           
    def found(self,node,message):
##beskonacan broj koraka ako se odkomentira
        if message.header=="Connect":
            j=message.source      
            
            if j.memory[self.levelKey] < node.memory[self.levelKey]:
                 node.memory[self.linkStatusKey][j]='INTERNAL'
                 #send Initiate(LN, FN, SN) on edge j; ja mislim da je to sve sadržano u message.source
                 node.send(Message(header="Initiate", data=0, destination=j))           
            
            elif node.memory[self.linkStatusKey][j]=='UNUSED':
                #then place received message on end of queue   
                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                node.memory[self.levelKey]=node.memory[self.levelKey]+1
                node.status='FIND'
                node.send(Message(header="Initiate", data=node.memory[self.weightKey][j], destination=j))
                #node.status='FOUND'

        if message.header=="Initiate":                        
            j=message.source
            node.memory[self.levelKey]=j.memory[self.levelKey]
            node.memory[self.nameKey]=j.memory[self.nameKey]
            node.memory[self.inBranchKey]=j
            
#            node.memory[self.bestEdgeKey]=None
            node.memory[self.bestWtKey]=[sys.maxint,sys.maxint]

            destination_nodes=list()            
            for i in  node.memory[self.linkStatusKey]:
                if i!=j and node.memory[self.linkStatusKey][i]=='INTERNAL':
                    destination_nodes.append(i)             
            node.send(Message(header="Initiate", data=0, destination=destination_nodes))

            if message.source.status=='FIND':
                node.status='FIND'
                print ("tezt")
            

        if message.header=="Test":
            j=message.source
            if j.memory[self.levelKey]>node.memory[self.levelKey]:
                #then place received message on end of queue
                ##veliko pitanje dal ovo radi:
                self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 
            elif node.memory[self.nameKey]!= j.memory[self.nameKey]:
                node.send(Message(header="Accept", data=0, destination=j))
            else:
                if node.memory[self.linkStatusKey][j]=='UNUSED':
                   node.memory[self.linkStatusKey][j]='EXTERNAL'
                   if node.memory[self.testEdgeKey]!=j or node.memory[self.testEdgeKey]==None : ##or == None
                       node.send(Message(header="Reject", data=0, destination=j))
#                   else :
#                       self.test(node) Only in the Find state

        if message.header=="Report":
            j=message.source
            if node.memory[self.inBranchKey]!=j:
                node.memory[self.findCountKey]=node.memory[self.findCountKey]-1
                m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])
                
                if m==message.data:
                    node.memory[self.bestWtKey]=message.data
                    node.memory[self.bestEdgeKey]=j
                self.report(node)
                
                
#                if message.data < node.memory[self.bestWtKey]:
#                    node.memory[self.bestWtKey]=message.data
#                    node.memory[self.bestEdgeKey]=j
#                self.report(node)   
#            if message.data > node.memory[self.bestWtKey]:
#                self.change_root(node)
                
            elif message.data==node.memory[self.bestWtKey] and node.memory[self.bestWtKey][0]==sys.maxint:
                print("HALT") #ima drugu poruku?
        
        if message.header=="Accept":
            j=message.source
            node.memory[self.testEdgeKey]=None

            m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])            

            if m==node.memory[self.bestWtKey]:
                node.memory[self.bestEdgeKey]=j
                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
            self.report(node)
                        
#            if node.memory[self.weightKey][j]>node.memory[self.bestWtKey]:
#                node.memory[self.bestEdgeKey]=j
#                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
#            self.report(node)
        
        if message.header=="Reject":
            j=message.source
            if node.memory[self.linkStatusKey][j] == 'UNUSED': ## Basic == Unused?  
                node.memory[self.linkStatusKey][j]='EXTERNAL'
            self.test(node)

 
    def initialize(self, node):

        node.memory[self.levelKey] = 0
        node.memory[self.nameKey] = node.id
        
        node.memory[self.neighborsKey]= sorted(node.memory[self.neighborsKey], key = lambda node: node.id)
        node.memory[self.parentKey] = node        

        node.memory[self.linkStatusKey] = {}        
        node.memory[self.weightKey] = {}

        node.memory[self.bestWtKey]=[sys.maxint,sys.maxint]
        node.memory[self.testEdgeKey]=None        
        
        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [min(node.id, neighbor.id),max(node.id, neighbor.id)]
            node.memory[self.linkStatusKey][neighbor] = 'UNUSED' ## Basic == Unused?  
                
    ###(2)   
    def wake_up(self,node):       
        m = self.min_weight_in_dict(node.memory[self.weightKey])
        node.memory[self.linkStatusKey][m]='INTERNAL' #kako zašto
        
        node.memory[self.levelKey]=0
        node.status='FOUND'        
        node.memory[self.findCountKey]=0
        node.send(Message(header="Connect", data=0, destination=m)) ##Connect==Let us Merge
                     
    def test(self,node):
        test_nodes={}        
        
        for key in node.memory[self.linkStatusKey]:
            if node.memory[self.linkStatusKey][key]=='UNUSED':              
                test_nodes[key]=node.memory[self.linkStatusKey][key]

        if len(test_nodes)!=0:
            test_node=self.min_weight_in_dict(test_nodes)
            
            node.memory[self.testEdgeKey]=test_node
            node.send(Message(header="Test", data=0, destination=test_node))
        else :
            self.report(node)
    
    def report(self,node):
        if node.memory[self.findCountKey]==0 and node.memory[self.testEdgeKey]==None:
            node.send(Message(header="Report", data=node.memory[self.bestWtKey], destination=node.memory[self.inBranchKey]))
            node.status='FOUND'
            
    def change_root(self,node):
        
        if node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]=='INTERNAL':
            node.send(Message(header="Change Root", data=0, destination=node.memory[self.bestEdgeKey]))
        else:
            node.send(Message(header="Connect", data=0, destination=node.memory[self.bestEdgeKey])) ##Connect==Let us Merge
            node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]='INTERNAL'

    def min_weight_in_dict(self,d):
        orderedDict = collections.OrderedDict(sorted(d.iteritems(), key=lambda (k,v):v[0]))            
        min_1= orderedDict.values()[0][0]        
        uzi_izbor={}              
        for o in orderedDict:
            if orderedDict[o][0] == min_1:
                uzi_izbor.update({o:orderedDict[o]})    
        orderedDict = collections.OrderedDict(sorted(uzi_izbor.iteritems(), key=lambda (k,v):v[1]))       
        return orderedDict.keys()[0]       
    
        
    def min_weight_two_lists(self,a,b):  
        if a[0]<b[0]:
            return a
        elif a[0]>b[0]:   
            return b
        elif a[1]<b[1]:
            return a
        else: 
            return b

    STATUS = {
              'SLEEPING': sleeping,
              'FIND':find,
              'FOUND':found,

             }