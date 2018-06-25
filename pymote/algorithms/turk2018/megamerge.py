# -*- coding: utf-8 -*-
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from random import random
import collections
import sys
#reload(sys)  
#sys.setdefaultencoding('utf8')
"""
u terminated stanju radio bi isto sto i u find/found?!
"""
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
reject message; this reduces the communication complexity slihaltghtly.

If the node receiving a test message has a different identity from that of the
test message, and if the receiving node's fragment level is greater than or
equal to that of the test message, then the message Accept is sent back to the
sending node, certifying that the edge is an outgoing edge from the sending 
node's fragment. If, on the other hand, the receiving node's fragment level is
less than that of the test message, then the receiving node delays making any 
response until its own level increases sufficiently. 

UNUSED
INTERNAL
EXTERNAL
"""

class MegaMerger(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors', 'weightKey': 'Weight', 
                      'linkStatusKey':'LinkStatus', 'levelKey': 'Level', 
                      'nameKey': 'Name', 'inBranchKey': 'InBranch', 
                      'testEdgeKey':'TestEdge','findCountKey':'FindCount', 
                      'bestWtKey':'BestWeight','bestEdgeKey':'BestEdge',
                      'queueKey':'Queue', 'haltKey':'Halt','debugKey': 'DEBUG',
                      'finalState':'State'}

    def initializer(self):
        ini_nodes = []
        
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']                        
            self.initialize(node)
            node.status = 'SLEEPING'
            # 30% inicijatora
            if random()<0.3:                #random initializers
                ini_nodes.append(node)
        #jedan inicijator
        #ini_nodes.append(self.network.nodes()[0])

        net = self.network
        for node,neighbors in net.adjacency_iter():
            for neighbor,eattr in neighbors.items():
                weight=eattr['weight']
                node.memory[self.weightKey][neighbor][0]=weight
              
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))  # to je spontani impuls
        print("inicijatori",ini_nodes)       
        
    def sleeping(self, node, message):
        
        if message.header == NodeAlgorithm.INI: #Spontaneously
            self.wake_up(node) 
        
        ###100%
        if message.header=="Connect":
            j=message.source
            self.wake_up(node)
            
            #True: j.memory[self.levelKey]> || == node.memory[self.levelKey]       
            if node.memory[self.linkStatusKey][j]=='BASIC':
                #then place received message on end of queue
                node.memory[self.queueKey].append(message)
                self.network.outbox.       insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                #u data šalje novo ime i link!, ne treba si ga sam postavljati!
                #njemu će postaviti Initiate poruka koju ce primiti na svom merge linku
                if node.id<j.id : 
                    new_name=node.id
                else:
                    new_name=j.id
                    
                l=[node.memory[self.levelKey]+1,new_name,'FIND']
                node.send(Message(header="Initiate", data=l, destination=j))
                print("frendly-merge ", node.memory[self.nameKey], "  se zeli mergat sa ", j.memory[self.nameKey] )                
                #Frendly merge
                                
        ###100%
        if message.header=="Test":
            self.wake_up(node)# posljedica node.status='FOUND'
            j=message.source
            #when a node recieves sush a test message, it checks weather or not its own fragment identity agrees with that of the test message...
            if j.memory[self.nameKey] != node.memory[self.nameKey]:
                node.send(Message(header="Accept", data=0, destination=j))
                #when a node a sends an Accept message in response to 
                #B's Test message, then the fragment identity of A differs and 
                #will continue to differ, from B's current fragment identity
            else:
                if node.memory[self.linkStatusKey][j]=='BASIC':
                   node.memory[self.linkStatusKey][j]='REJECTED'
                   #...if the identites agree, then the node sends the message Reject back to the sender, and both nodes put the edge in the Rejected stage
                   if node.memory[self.testEdgeKey]!=j or node.memory[self.testEdgeKey]==None:
                       node.send(Message(header="Reject", data=0, destination=j))
                   else:
                       self.test(node)                                 
  
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
                 
                 l=[node.memory[self.levelKey],node.memory[self.nameKey],node.status]
                 node.send(Message(header="Initiate", data=l , destination=j))
                 node.memory[self.findCountKey]=node.memory[self.findCountKey]+1
                 #Due to our strategy of never making a low level fragment wait, node n' (reciever) immediatly 
                 #sends an Initiate message with identity and level parameteters of F' and L' to n                 
                 print("absorbtion ", node.memory[self.nameKey], " apsorbira ", j.memory[self.nameKey] )
                 #If node n' has not yet sent its report message at the given level, 
                 #fragment F simpley joins fragment F' and participates in finding the minimum-weight outgoing edge from the enlarged fragment...
            
            elif node.memory[self.linkStatusKey][j]=='BASIC':
			 #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
                node.memory[self.queueKey].append(message)
                self.network.outbox.       insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
                self.network.outbox.       insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                #node.memory[self.levelKey]=node.memory[self.levelKey]+1
                #node.status='FIND' ##ne znam dal seta sebi status ili samo nodu kojem salje
                if node.id<j.id : 
                    new_name=node.id
                else:
                    new_name=j.id
                l=[node.memory[self.levelKey]+1,new_name,'FIND']
                node.send(Message(header="Initiate", data=l , destination=j))                                
                print("frendly-merge ", node.memory[self.nameKey], "  se zeli mergat sa ", j.memory[self.nameKey] )
                #frendly merge
                
        if message.header=="Initiate":
            j=message.source
            node.memory[self.levelKey]=message.data[0]
            #node.memory[self.nameKey]=j.memory[self.nameKey]
            node.memory[self.nameKey]=message.data[1]
            print(node.id, "iz",node.status,"u",message.data[2])
            node.status=message.data[2]
            
            node.memory[self.inBranchKey]=j
            node.memory[self.bestEdgeKey]=None
            node.memory[self.bestWtKey]=[sys.maxint,sys.maxint,sys.maxint]
            destination_nodes=list()
   
            for i in  node.memory[self.linkStatusKey]:
                if i!=j and node.memory[self.linkStatusKey][i]=='BRANCH':
                    destination_nodes.append(i)
                    if(node.status=='FIND'):
                        node.memory[self.findCountKey]=node.memory[self.findCountKey]+1
            node.send(Message(header="Initiate", data=0, destination=destination_nodes)) #broadcast po svom stablu
            print("broadcast Initiate ")            
            if node.status=='FIND':
                # When a node recieves this initiate message it starts to find its minimum-weight outgoing edge                
                self.test(node)

        if message.header=="Test":
            j=message.source
            if j.memory[self.levelKey]>node.memory[self.levelKey]:
                #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source)) 
                node.memory[self.queueKey].append(message)
                self.network.outbox.       insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
            elif j.memory[self.nameKey] != node.memory[self.nameKey]:
                node.send(Message(header="Accept", data=0, destination=j))
                #when a node a sends an Accept message in response to B's Test message, then the fragment identity of A differs and will continue to differ, from B's current fragment identity
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
                node.memory[self.linkStatusKey][j] = 'REJECTED' #..both nodes put the edge state in the Rejected state
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
                #if m==w : ##compare lista pitanje dal radi, što ako je m!=[sys.maxint,sys.maxint,sys.maxint]?!
#                if m!=None and m==w and m!=[sys.maxint,sys.maxint,sys.maxint]:                
                if m!=None and m==w:                
                    node.memory[self.bestWtKey]=w
                    node.memory[self.bestEdgeKey]=j
                self.report(node)
                                
            elif node.status=='FIND':
                #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=w,destination=node, source=message.source))                 
                node.memory[self.queueKey].append(message)
                self.network.outbox.       insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
                #pass
            elif m==node.memory[self.bestWtKey]:
                self.change_root(node)
                print("NIKADA TU?")
            elif w==node.memory[self.bestWtKey]:
                print("NIKADA TU?")
                print("HALT")
                if w==node.memory[self.bestWtKey] and node.memory[self.bestWtKey]==[sys.maxint,sys.maxint,sys.maxint]:
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
                 l=[node.memory[self.levelKey],node.memory[self.nameKey],node.status]
                 node.send(Message(header="Initiate", data=l , destination=j))
                 #...if on the other hand node n' (receiver) has allready sent its report message, 
                 #then we can deduce that outgoing edge from node n' (receiver) 
                 #has a lower weight than minimum-weight outgoing edge from F (sender of Connect)
                 #this eliminates the necessity for F to join the search for the minimum-weight outgoing edge
                 print("absorbtion ", node.memory[self.nameKey], " apsorbira ", j.memory[self.nameKey] )
                 
            elif node.memory[self.linkStatusKey][j]=='BASIC':
			 #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
                node.memory[self.queueKey].append(message)
                self.network.outbox.       insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
            else:
                #send Initiate(LN + 1, w(j), Find) on edge j
                #node.memory[self.levelKey]=node.memory[self.levelKey]+1
                #node.status='FIND'
                if node.id<j.id : 
                    new_name=node.id
                else:
                    new_name=j.id
                    
                l=[node.memory[self.levelKey]+1,new_name,'FIND']
                node.send(Message(header="Initiate", data=l , destination=j)) 
                #frendly merge
                print("frendly-merge ", node.memory[self.nameKey], "  se zeli mergat sa ", j.memory[self.nameKey] )
                
        if message.header=="Initiate":
            j=message.source
            node.memory[self.levelKey]=message.data[0]
            #node.memory[self.nameKey]=j.memory[self.nameKey]
            node.memory[self.nameKey]=message.data[1]          
            print(node.id, "iz",node.status,"u",message.data[2])            
            node.status=message.data[2]  #ili FIND ili FOUND
            
            node.memory[self.inBranchKey]=j
            node.memory[self.bestEdgeKey]=None
            node.memory[self.bestWtKey]=[sys.maxint,sys.maxint,sys.maxint]
            destination_nodes=list()
            
            for i in  node.memory[self.linkStatusKey]:
                if i!=j and node.memory[self.linkStatusKey][i]=='BRANCH':
                    destination_nodes.append(i)
                    if(node.status=='FIND'):
                        node.memory[self.findCountKey]=node.memory[self.findCountKey]+1
                        
            node.send(Message(header="Initiate", data=0, destination=destination_nodes))
            print("broadcast Initiate ")           
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
                self.network.outbox.       insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
                #..if the recieving node's fragment level is less than that of the test message
                #then the recieving node delays any response until its own level increasses sufficiently
            elif j.memory[self.nameKey] != node.memory[self.nameKey]: 
                # if the node recieving node has a different identity from the test message 
                # and if the recieving node's fragment level is greather than or equal to that of the test message
                # then the Accept message is sent back to the sending node
                node.send(Message(header="Accept", data=0, destination=j))
                #when a node a sends an Accept message in response to B's Test message, then the fragment identity of A differs and will continue to differ, from B's current fragment identity
            else:
                if node.memory[self.linkStatusKey][j]=='BASIC':
                   node.memory[self.linkStatusKey][j]='REJECTED'
                   if node.memory[self.testEdgeKey]!=j or node.memory[self.testEdgeKey]==None:
                       node.send(Message(header="Reject", data=0, destination=j))
                   else:
                       self.test(node)
                       
        if message.header=="Report":
            #Eventualy, the teo nodes adjacent to the core send Report on the core branch itself, 
            #allowing each of these nodes to determine both the weight o the minimum outgoing edge and the side of the core on which this edge lies
            j=message.source
            w=message.data
            print("Report message.data ",w,"node bestWt ",node.memory[self.bestWtKey])
            print("compare",node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
            m=self.min_weight_two_lists(node.memory[self.weightKey][j],node.memory[self.bestWtKey])            
            print("smaller", m )
            if j!=node.memory[self.inBranchKey]:
                node.memory[self.findCountKey]=node.memory[self.findCountKey]-1
                print(m,w)
                print("m==w",m==w)
                #if m==w : ##compare lista pitanje dal radi, što ako je m!=[sys.maxint,sys.maxint,sys.maxint]?!
#                if m!=None and m==w and m!=[sys.maxint,sys.maxint,sys.maxint]:
                if m!=None and m==w:
                    node.memory[self.bestWtKey]=w
                    node.memory[self.bestEdgeKey]=j
                self.report(node)
            elif node.status=='FIND':
                #then place received message on end of queue
                #self.network.outbox.insert(0, Message(header=message.header,data=w,destination=node, source=message.source))                 
                print("NIKADA TU?")
                node.memory[self.queueKey].append(message)
                self.network.outbox.       insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
                #pass
            elif m==node.memory[self.bestWtKey]:
                self.change_root(node)
                #After the two core nodes have exchanged Report message, the bestEdge saved by the fragment nodes makes it posible to trace the path from core to the node having minimum waight
            elif w==node.memory[self.bestWtKey]:
                print("HALT")
                if w==node.memory[self.bestWtKey] and node.memory[self.bestWtKey]==[sys.maxint,sys.maxint,sys.maxint]:
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

        node.memory[self.bestWtKey] = None #[sys.maxint,sys.maxint,sys.maxint]
        node.memory[self.testEdgeKey] = None   
        node.memory[self.bestEdgeKey] = None   
        
        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [0,min(node.id, neighbor.id),max(node.id, neighbor.id)]
            
            node.memory[self.linkStatusKey][neighbor] = 'BASIC'
            
        node.memory[self.queueKey]=list()
        node.memory[self.haltKey]=False
    
    ###(2)   
    def wake_up(self,node):
        #when a sleeping node either spontaneously awakens or is awakened by the recipt of any algorithm message from another node, 
        #the node first chooses it's minimum-weight adjcent edge...
        m = self.adjacent_node_of_minimum_weight(node.memory[self.weightKey])
        #...marks this edge as branch...        
        node.memory[self.linkStatusKey][m]='BRANCH'
        
        node.memory[self.levelKey]=0 #mozda u initialize()?
        node.memory[self.findCountKey]=0
        
        #...sends a message called Connect and goes into the state Found
        #Jer na početku je on sam root
        node.send(Message(header="Connect", data=0, destination=m))
        node.status='FOUND'
        #print(node.id, "min in wake_up", m)         
                     
    def test(self,node):
        test_nodes={}        
        
        for key in node.memory[self.linkStatusKey]:
            if node.memory[self.linkStatusKey][key]=='BASIC':              
                #test_nodes[key]=node.memory[self.linkStatusKey][key]
                test_nodes[key]=node.memory[self.weightKey][key]
                  
        if len(test_nodes)!=0:
            test_node=self.adjacent_node_of_minimum_weight(test_nodes)
            node.memory[self.testEdgeKey]=test_node
            node.send(Message(header="Test", data=0, destination=test_node))
            print(node.id,"min in test", test_node) #edge prestaje biti basic, postaje rejected ili branch, tako se izbjegava da ponovno bude odabran
        else :
            node.memory[self.testEdgeKey]=None #danas
            self.report(node)
    
    def report(self,node):
        if node.memory[self.findCountKey]==0 and node.memory[self.testEdgeKey]==None:
            #node.status='FOUND' #when a node sends a Report Message if also goes to the state FOUND
            node.send(Message(header="Report", data=node.memory[self.bestWtKey], destination=node.memory[self.inBranchKey]))            
            print(node.id, "saljem report", "data=",node.memory[self.bestWtKey] )
            node.status='FOUND'
            
            if node.memory[self.bestWtKey] == [sys.maxint,sys.maxint,sys.maxint]:
                print (node.id, "moj bestWtKey je infinity!")
            #valjda nije bitno prije ili poslije
            
            #In particular, each leaf node of the fragment, that is
            #each node adjicent to only one fragment branch, 
            # sends the Report(W) on its inbound branch
            # W is the weight of the minimum-weight outgoing edge from the node and
            # W is infinity if there are no outgoing edges
            
            #Similarly each interior node of the fragment waits until it has both found it's own minimum-weighted outgoing edge
            # and received message on all outbound fragment branches

            
    def change_root(self,node):
        #!=None?             
        if node.memory[self.bestEdgeKey]!=None and node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]=='BRANCH':
            node.send(Message(header="Change Root", data=0, destination=node.memory[self.bestEdgeKey]))
        else:
            node.send(Message(header="Connect", data=0, destination=node.memory[self.bestEdgeKey])) ##Connect==Let us Merge
            node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]='BRANCH'
            #when this message reaches the node with minimum-weight outgoing edge, 
            #the inbound edge form a rooted tree, rooted at this node
            #Finally this node sends the message Connect(L) over the minimum-weighted outgoing edge
            
    def dequeue_and_process_message(self,node):
        m=node.memory[self.queueKey].pop()
        node.inbox        
        print(m.header)
        
        
        
    def adjacent_node_of_minimum_weight(self,d):
        
        orderedDict = collections.OrderedDict(sorted(d.iteritems(), key=lambda (k,v):v[0]))            
        min_1= orderedDict.values()[0][0]        
        uzi_izbor={}              
        for o in orderedDict:
            if orderedDict[o][0] == min_1:
                uzi_izbor.update({o:orderedDict[o]})    
        
        orderedDict = collections.OrderedDict(sorted(uzi_izbor.iteritems(), key=lambda (k,v):v[1]))       

        min_2= orderedDict.values()[0][1]        
        uzi_izbor={}              
        for o in orderedDict:
            if orderedDict[o][1] == min_2:
                uzi_izbor.update({o:orderedDict[o]})    
        
        orderedDict = collections.OrderedDict(sorted(uzi_izbor.iteritems(), key=lambda (k,v):v[2]))               
        
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
        elif b[2]>a[2]: 
            return b
        elif a[2]>b[2]:
            return a

        else:
            return None # ==

    STATUS = {
              'SLEEPING': sleeping,
              'FIND':find,
              'FOUND':found,

             }