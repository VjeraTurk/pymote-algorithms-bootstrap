# -*- coding: utf-8 -*-
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from random import random
import collections
import sys

"""
link status

REJECTED  Rejected, if the edge is not a branch but has been discovered to join
two nodes of the fragment
BRANCH    Branch, if the edge is a branch in the current fragment
BASIC     Basic if the edge is neither a branch nor rejected.


Test message == Outside
When a node receives such a test message, it checks whether or not its own 
fragment identity agrees with that of the test message. 

If the identities agree, then (subject to a slight exception) 
the node sends the message Reject back to the sender of the test message, and 
both nodes put the edge in the Rejected state. The node sending the test 
message then continues by testing its next-best edge.
The exception above is that, if a node sends and then receives a test message 
with the same identity on the same edge, it simply rejects the edge without the
reject message; this reduces the communication complexity slightly. (INTERNAL?) 

If the node receiving a test message has a different identity from that of the
test message, and if the receiving node's fragment level is greater than or equal 
to that of the test message, then the message Accept is sent back to the sending
node, certifying that the edge is an outgoing edge from the sending node's
fragment. If, on the other hand, the receiving node's fragment level is less than
that of the test message, then the receiving node delays making any response
until its own level increases sufficiently. (EXTERNAL?)

UNUSED
INTERNAL
EXTERNAL
"""

class MegaMerger(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors', 'weightKey': 'Weight', 'linkStatusKey':'LinkStatus', 
                       'levelKey': 'Level', 'nameKey': 'Name', 'inBranchKey': 'InBranch', 
                      'testEdgeKey':'TestEdge','findCountKey':'FindCount', 'bestWtKey':'BestWeight','bestEdgeKey':'BestEdge',
                      'queueKey':'Queue', 'haltKey':'Halt','debugKey': 'DEBUG'}

    def initializer(self):
        ini_nodes = []
       
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']                        
            self.initialize(node)
            node.status = 'SLEEPING'
#            if random()<0.3:                #random initializers
#                ini_nodes.append(node)
        ini_nodes.append(self.network.nodes()[0])

        print("Inicijatori: ", ini_nodes)                
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))  # to je spontani impuls
            
        
    def sleeping(self, node, message):

        if message.header == NodeAlgorithm.INI: #Spontaneously
            self.wake_up(node) 
        
        ###100%
        if message.header=="Connect":
            j=message.source
            self.wake_up(node)
            
            if j.memory[self.levelKey]<node.memory[self.levelKey]:
                 node.memory[self.linkStatusKey][j]='BRANCH'
                 #send Initiate(LN, FN, SN) on edge j; ja mislim da je to sve sadržano u message.source
                 #node.send(Message(header="Initiate", data=node.memory[self.weightKey][j], destination=j))                   
                 node.send(Message(header="Initiate", data=0, destination=j))                   
            elif node.memory[self.linkStatusKey][j]=='BASIC':
                #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
                node.memory[self.queueKey].append(message)
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                node.memory[self.levelKey]=node.memory[self.levelKey]+1
                node.status='FIND' 
                node.send(Message(header="Initiate", data=node.memory[self.weightKey][j], destination=j))
        ###100%
        if message.header=="Test":
            self.wake_up(node)# posljedica node.status='FOUND'
            j=message.source
            if j.memory[self.levelKey]>node.memory[self.levelKey]:
                #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
                node.memory[self.queueKey].append(message)
                
            elif j.memory[self.nameKey] != node.memory[self.nameKey]:
                node.send(Message(header="Accept", data=0, destination=j))
            else:
                if node.memory[self.linkStatusKey][j]=='BASIC':
                   node.memory[self.linkStatusKey][j]='REJECTED'
                   if node.memory[self.testEdgeKey]!=j or node.memory[self.testEdgeKey]==None:
                       node.send(Message(header="Reject", data=0, destination=j))
                   else:
                       self.test(node)                                 
        #if message.header=="Initiate":
        #if message.header=="Report":
        #if message.header=="Accept":
        #if message.header=="Reject":

  
    def find(self,node,message):

        if message:
            print(node.id, " In find", message.header)
        ###100%
        if message.header=="Connect":
            j=message.source
            if j.memory[self.levelKey] < node.memory[self.levelKey]:
                 node.memory[self.linkStatusKey][j]='BRANCH'
                 #send Initiate(LN, FN, SN) on edge j; ja mislim da je to sve sadržano u message.source
                 #Ime neka nije od prvog koji pošalje Initiate nego svaki za sebe izračuna
                 node.send(Message(header="Initiate", data=0, destination=j))
                 node.memory[self.findCountKey]=node.memory[self.findCountKey]+1
            elif node.memory[self.linkStatusKey][j]=='BASIC':
				#then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
                node.memory[self.queueKey].append(message)
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                node.memory[self.levelKey]=node.memory[self.levelKey]+1
                node.status='FIND' ##ne znam dal seta sebi status ili samo nodu kojem salje
                node.send(Message(header="Initiate", data=node.memory[self.weightKey][j], destination=j))

        if message.header=="Initiate":
            j=message.source
            node.memory[self.levelKey]=j.memory[self.levelKey]
            node.memory[self.nameKey]=j.memory[self.nameKey]
            node.status=j.status #ili FIND ili FOUND
            node.memory[self.inBranchKey]=j
            node.memory[self.bestEdgeKey]=None
            node.memory[self.bestWtKey]=[sys.maxint,sys.maxint]
            destination_nodes=list()
            
            for i in  node.memory[self.linkStatusKey]:
                if i!=j and node.memory[self.linkStatusKey][i]=='BRANCH':
                    destination_nodes.append(i)
                    if(node.status=='FIND'):
                        node.memory[self.findCountKey]=node.memory[self.findCountKey]+1
            node.send(Message(header="Initiate", data=0, destination=destination_nodes))
            if node.status=='FIND':
                self.test(node)

        if message.header=="Test":
            j=message.source
            if j.memory[self.levelKey]>node.memory[self.levelKey]:
                #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 
                node.memory[self.queueKey].append(message)
            elif j.memory[self.nameKey] != node.memory[self.nameKey]:
                node.send(Message(header="Accept", data=0, destination=j))
            else:
                if node.memory[self.linkStatusKey][j]=='BASIC':
                   node.memory[self.linkStatusKey][j]='REJECTED'
                   if node.memory[self.testEdgeKey]!=j or node.memory[self.testEdgeKey]==None:
                       node.send(Message(header="Reject", data=0, destination=j))
                   else:
                       self.test(node)

        if message.header=="Accept":
            j=message.source
            node.memory[self.testEdgeKey]=None
            print("compare",node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
            m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
            print("smaller", m )
            print("m==node.memory[self.bestWtKey]", m==node.memory[self.bestWtKey])
            
            if m!=None and m==node.memory[self.bestWtKey]: ## !=m
                node.memory[self.bestEdgeKey]=j
                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
                
            self.report(node) 

        if message.header=="Reject":
            j=message.source
            if node.memory[self.linkStatusKey][j] == 'BASIC':   
                node.memory[self.linkStatusKey][j] = 'REJECTED'
            self.test(node) #Test next

        ###100% in Find
        if message.header=="Report":
            j=message.source
            w=message.data
            print("message.data ",w,"node bestWt ",node.memory[self.bestWtKey])

            print("compare",node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
            m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
            print("smaller", m )
            
            if j!=node.memory[self.inBranchKey]:
                node.memory[self.findCountKey]=node.memory[self.findCountKey]-1
                print(m,w)
                print("m==w",m==w)
                #if m==w : ##compare lista pitanje dal radi, što ako je m!=[sys.maxint,sys.maxint]?!
                if m!=None and m==w and m!=[sys.maxint,sys.maxint]:
                    node.memory[self.bestWtKey]=w
                    node.memory[self.bestEdgeKey]=j
                    node.memory[self.debugKey]="m!=[sys.maxint,sys.maxint]"
                self.report(node)
            elif node.status=='FIND':
                #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=w,destination=node, source=message.source))                 
                node.memory[self.queueKey].append(message)
                #pass
            elif m==node.memory[self.bestWtKey]:
                self.change_root(node)
            elif w==node.memory[self.bestWtKey]:
                print("HALT")
                if w==node.memory[self.bestWtKey] and node.memory[self.bestWtKey]==[sys.maxint,sys.maxint]:
                    node.memory[self.debugKey]='HALT'
                    node.memory[self.haltKey]=True

        if message.header=="Change Root":
            self.change_root(node)

    def found(self,node,message):
        
        if message.header=="Connect":
            j=message.source
            if j.memory[self.levelKey] < node.memory[self.levelKey]:
                 node.memory[self.linkStatusKey][j]='BRANCH'
                 #send Initiate(LN, FN, SN) on edge j; ja mislim da je to sve sadržano u message.source
                 #Ime neka nije od prvog koji pošalje Initiate nego svaki za sebe izračuna
                 node.send(Message(header="Initiate", data=0, destination=j))
            elif node.memory[self.linkStatusKey][j]=='BASIC':
				#then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
                node.memory[self.queueKey].append(message)
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                node.memory[self.levelKey]=node.memory[self.levelKey]+1
                node.status='FIND'
                node.send(Message(header="Initiate", data=node.memory[self.weightKey][j], destination=j))

        if message.header=="Initiate":
            j=message.source
            node.memory[self.levelKey]=j.memory[self.levelKey]
            node.memory[self.nameKey]=j.memory[self.nameKey]
            node.status=j.status #ili FIND ili FOUND
            print(node.id, "iz","FIND","u",j.status)
            node.memory[self.inBranchKey]=j
            node.memory[self.bestEdgeKey]=None
            node.memory[self.bestWtKey]=[sys.maxint,sys.maxint]
            destination_nodes=list()
            
            for i in  node.memory[self.linkStatusKey]:
                if i!=j and node.memory[self.linkStatusKey][i]=='BRANCH':
                    destination_nodes.append(i)
                    if(node.status=='FIND'):
                        node.memory[self.findCountKey]=node.memory[self.findCountKey]+1
            node.send(Message(header="Initiate", data=0, destination=destination_nodes))
            if node.status=='FIND':
                self.test(node)
#The nodes in fragment F go into state Find or Found depending on this parameter 
#of the initiate message, and they send Test messages only in the Find state.
        if message.header=="Test":
            j=message.source
            if j.memory[self.levelKey]>node.memory[self.levelKey]:
                #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 
                node.memory[self.queueKey].append(message)
            elif j.memory[self.nameKey] != node.memory[self.nameKey]:
                node.send(Message(header="Accept", data=0, destination=j))
            else:
                if node.memory[self.linkStatusKey][j]=='BASIC':
                   node.memory[self.linkStatusKey][j]='REJECTED'
                   if node.memory[self.testEdgeKey]!=j or node.memory[self.testEdgeKey]==None:
                       node.send(Message(header="Reject", data=0, destination=j))
                   else:
                       self.test(node)
                       
        if message.header=="Report":
            j=message.source
            w=message.data
            print("message.data ",w,"node bestWt ",node.memory[self.bestWtKey])
            print("compare",node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
            m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
            print("smaller", m )
            if j!=node.memory[self.inBranchKey]:
                node.memory[self.findCountKey]=node.memory[self.findCountKey]-1
                print(m,w)
                print("m==w",m==w)
                #if m==w : ##compare lista pitanje dal radi, što ako je m!=[sys.maxint,sys.maxint]?!
                if m!=None and m==w and m!=[sys.maxint,sys.maxint]:
                    node.memory[self.bestWtKey]=w
                    node.memory[self.bestEdgeKey]=j
                self.report(node)
            elif node.status=='FIND':
                #then place received message on end of queue
                self.network.outbox.insert(0, Message(header=message.header,data=w,destination=node, source=message.source))                 
                node.memory[self.queueKey].append(message)
                #pass
            elif m==node.memory[self.bestWtKey]:
                self.change_root(node)
            elif w==node.memory[self.bestWtKey]:
                print("HALT")
                if w==node.memory[self.bestWtKey] and node.memory[self.bestWtKey]==[sys.maxint,sys.maxint]:
                    node.memory[self.debugKey]='HALT'
                    node.memory[self.haltKey]=True
        
        if message.header=="Change Root":
            self.change_root(node)
        #if message.header=="Accept":      
        #if message.header=="Reject":

 
    def initialize(self, node):

        node.memory[self.levelKey] = 0
        node.memory[self.nameKey] = node.id
        
        node.memory[self.neighborsKey] = sorted(node.memory[self.neighborsKey], key = lambda node: node.id)
        #node.memory[self.parentKey] = node   #danas     
        node.memory[self.inBranchKey] = None
        node.memory[self.linkStatusKey] = {}        
        node.memory[self.weightKey] = {}

        node.memory[self.bestWtKey] = None #[sys.maxint,sys.maxint]
        node.memory[self.testEdgeKey] = None   
        node.memory[self.bestEdgeKey] = None   
        
        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [min(node.id, neighbor.id),max(node.id, neighbor.id)]
            node.memory[self.linkStatusKey][neighbor] = 'BASIC'
            
        node.memory[self.queueKey]=list()
        node.memory[self.haltKey]=False
    
    ###(2)   
    def wake_up(self,node):       
        m = self.min_weight_in_dict(node.memory[self.weightKey])
        node.memory[self.linkStatusKey][m]='BRANCH'
        
        node.memory[self.levelKey]=0
        node.status='FOUND'          
        node.memory[self.findCountKey]=0
        node.send(Message(header="Connect", data=0, destination=m)) ##Connect==Let us Merge
                     
    def test(self,node):
        test_nodes={}        
        
        for key in node.memory[self.linkStatusKey]:
            if node.memory[self.linkStatusKey][key]=='BASIC':              
                #test_nodes[key]=node.memory[self.linkStatusKey][key]
                test_nodes[key]=node.memory[self.weightKey][key]
                

        print("len(test_nodes)", len(test_nodes))
        print ("test_nodes",test_nodes)        
        
        if len(test_nodes)!=0:
            test_node=self.min_weight_in_dict(test_nodes)
            node.memory[self.testEdgeKey]=test_node
            node.send(Message(header="Test", data=0, destination=test_node))
        else :
            node.memory[self.testEdgeKey]=None #danas
            self.report(node)
    
    def report(self,node):
        if node.memory[self.findCountKey]==0 and node.memory[self.testEdgeKey]==None:
            node.status='FOUND'
            node.send(Message(header="Report", data=node.memory[self.bestWtKey], destination=node.memory[self.inBranchKey]))

            
    def change_root(self,node):
        #!=None?             
        if node.memory[self.bestEdgeKey]!=None and node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]=='BRANCH':
            node.send(Message(header="Change Root", data=0, destination=node.memory[self.bestEdgeKey]))
        else:
            node.send(Message(header="Connect", data=0, destination=node.memory[self.bestEdgeKey])) ##Connect==Let us Merge
            node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]='BRANCH'

    def min_weight_in_dict(self,d):
        
        orderedDict = collections.OrderedDict(sorted(d.iteritems(), key=lambda (k,v):v[0]))            
        min_1= orderedDict.values()[0][0]        
        uzi_izbor={}              
        for o in orderedDict:
            if orderedDict[o][0] == min_1:
                uzi_izbor.update({o:orderedDict[o]})    
        orderedDict = collections.OrderedDict(sorted(uzi_izbor.iteritems(), key=lambda (k,v):v[1]))       
        
        print ("ordered values uzi izbor!!:")
        print orderedDict.values()
        print ("minimum value:")
        print orderedDict.keys()[0]
        
        return orderedDict.keys()[0]       
    
        
    def min_weight_two_lists(self,a,b):  
        
        if a[0]<b[0]:
            return a
        elif a[0]>b[0]:   
            return b
        elif a[1]<b[1]:
            return a
        elif b[1]>a[1]: 
            return b
        else:
            return None # ==

    STATUS = {
              'SLEEPING': sleeping,
              'FIND':find,
              'FOUND':found,

             }