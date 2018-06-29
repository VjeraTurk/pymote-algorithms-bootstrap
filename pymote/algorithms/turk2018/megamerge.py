# -*- coding: utf-8 -*-
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from random import random,randrange
import collections
import sys
#reload(sys)  
#sys.setdefaultencoding('utf8')
"""
VAŽNO!
Nekako čitaju poruku dvaput O.o
-ispitati i ispraviti tko je root u novoformiranom fragmentu (drugačije u pseudokodu -core edge)
-u terminated stanju radio bi isto sto i u find/found
-ovako napisan kod, zasto je siguran da je posljednji else nakon primitka  
    Connect friendly bez da provjeri da su leveli isti ?
-staviti isti kod u procedure da je jednostavnije 
    ispravljati greške samo na jednom mjestu

"""
"""
link status

REJECTED/INTERNAL  Rejected, if the edge is not a branch but has been discovered to join
                   two nodes of the fragment

BRANCH/EXTERNAL    Branch, if the edge is a branch in the current fragment

BASIC/UNUSED       Basic if the edge is neither a branch nor rejected.


Test/Outside?
l=[node.memory[self.levelKey],node.memory[self.nameKey]]

Connect/Let us merge

Initiate/(broadcast information)Notification
message.data=[node.memory[self.levelKey]+1,new_name,'FIND']

Change Root

"""

class MegaMerger(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors', 'weightKey': 'Weight', 
                      'linkStatusKey':'LinkStatus', 'levelKey': 'Level', 
                      'nameKey': 'Name', 'inBranchKey': 'InBranch', 
                      'testEdgeKey':'TestEdge','findCountKey':'FindCount', 
                      'bestWtKey':'BestWeight','bestEdgeKey':'BestEdge',
                      'queueKey':'Queue', 'haltKey':'Halt','debugKey': 'DEBUG',
                      'finalState':'State', 'queueLenKey':'QueueLen'}
                      
    def initializer(self):
        ini_nodes = []
        
        #jedan SIGURAN inicijator
        #one_initiator=self.network.nodes()[randrange(1,len(self.network.nodes()),1)]        
        #ini_nodes.append(one_initiator)
        
        #inicijator node 0
        initiator_1=self.network.nodes()[0]
        ini_nodes.append(initiator_1)

        
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']                        
            self.initialize(node)
            node.status = 'SLEEPING'
            # 30% inicijatora
            #if random()<0.3 and node!=one_initiator:  #random initiators
            #    ini_nodes.append(node)

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

        if message.header!=NodeAlgorithm.INI:
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], " primio ", " in ", node.status  , message.header, " od ", message.source.id)
       
        if message.header=="Connect":
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "budi me", message.source.id)
            self.wake_up(node)
            self.receipt_of_connect(node,message)                        
            #True: j.memory[self.levelKey]> || == node.memory[self.levelKey]       
    
        if message.header=="Test":
            self.wake_up(node) # posljedica node.status='FOUND' i poslana porka 'Connect'      
            self.receipt_of_test(node,message)                                 
  
    def find(self,node,message):

        if message:
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], " primio ", " in ", node.status  , message.header, " od ", message.source.id)       
        
#        if message:
#            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey],"obraduje", " in ", node.status , message.header, " od ", message.source.id)
                   
        if message.header=="Connect":
            self.receipt_of_connect(node,message)
                
        if message.header=="Initiate":
            
            old_level=node.memory[self.levelKey]
            self.receipt_of_initiate(node,message)
            new_level=node.memory[self.levelKey]            
            
            if new_level>old_level and len(node.memory[self.queueKey])>0:
                m=node.memory[self.queueKey].pop() ##Mozda tu?
                print(node.id, "Tu sam")
                if node.status=="FIND": 
                    self.find(node,m)
                else:
                    self.found(node,m)
        
        if message.header=="Report":
            self.receipt_of_report(node,message)

        if message.header=="Test":
            self.receipt_of_test(node,message)

        if message.header=="Accept":
            j=message.source
            node.memory[self.testEdgeKey]=None
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "compare after Accept", node.memory[self.weightKey][j], node.memory[self.bestWtKey])           
            w=node.memory[self.weightKey][j]
            if w[0]<node.memory[self.bestWtKey][0] or (w[0]==node.memory[self.bestWtKey][0] and w[1]<node.memory[self.bestWtKey][1]) or ( w[0]==node.memory[self.bestWtKey][0] and w[1]==node.memory[self.bestWtKey][1] and w[2]<node.memory[self.bestWtKey][2]):
                node.memory[self.bestEdgeKey]=j
                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
                print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey],"azuriram svoj bestWt i Edge")
            self.report(node) 

        if message.header=="Reject":
            j=message.source
            if node.memory[self.linkStatusKey][j] == 'BASIC':   
                node.memory[self.linkStatusKey][j] = 'REJECTED' #..both nodes put the edge state in the Rejected state
            self.test(node) #Test next # Uvuci za jedan ili ne?

        if message.header=="Change Root":
            self.change_root(node)
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "change root")
    
        if len(node.memory[self.queueKey])>0:
            print(node.id, "ima poruka u queue")
            print(node.memory[self.queueKey])

    def found(self,node,message):

        if message:
           print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], " primio " , " in ", node.status, message.header, " od ",message.source.id)

#        if message:
#            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey],"obraduje", " in ", node.status , message.header, " od ", message.source.id)

        if message.header=="Connect":
            self.receipt_of_connect(node,message)
            
        if message.header=="Initiate":
            
            old_level=node.memory[self.levelKey]
            self.receipt_of_initiate(node,message)
            new_level=node.memory[self.levelKey]   
            
            if new_level>old_level and len(node.memory[self.queueKey])>0:
                                
                m=node.memory[self.queueKey].pop() ##Mozda tu?
                print(node.id, "Tu sam")
                if node.status=="FIND": 
                    self.find(node,m)
                else:
                    self.found(node,m)

        if message.header=="Test":
            self.receipt_of_test(node,message)        
                      
        if message.header=="Report":
            self.receipt_of_report(node,message)
        
        if message.header=="Change Root":
            self.change_root(node)
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "change root")
            
        if message.header=="Accept":
            j=message.source
            node.memory[self.testEdgeKey]=None
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "compare after Accept", node.memory[self.weightKey][j], node.memory[self.bestWtKey])           
            w=node.memory[self.weightKey][j]
            if w[0]<node.memory[self.bestWtKey][0] or (w[0]==node.memory[self.bestWtKey][0] and w[1]<node.memory[self.bestWtKey][1]) or ( w[0]==node.memory[self.bestWtKey][0] and w[1]==node.memory[self.bestWtKey][1] and w[2]<node.memory[self.bestWtKey][2]):
                node.memory[self.bestEdgeKey]=j
                node.memory[self.bestWtKey]=node.memory[self.weightKey][j]
                print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey],"azuriram svoj bestWt i Edge")
            self.report(node) 
            print("NIKADA TU?")
            
        if message.header=="Reject":
            j=message.source
            if node.memory[self.linkStatusKey][j] == 'BASIC':   
                node.memory[self.linkStatusKey][j] = 'REJECTED' #..both nodes put the edge state in the Rejected state
            self.test(node) #Test next # Uvuci za jedan ili ne?
            print("NIKADA TU?")
        
        if len(node.memory[self.queueKey])>0:
            print(node.id, "ima poruka u queue")
            print(node.memory[self.queueKey])
        
                
    def terminated(self,node,message):
        pass
        
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
        print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey],"budim se")        
        #when a sleeping node either spontaneously awakens or is awakened by the recipt of any algorithm message from another node, 
        #the node first chooses it's minimum-weight adjcent edge...
        m = self.adjacent_node_of_minimum_weight(node.memory[self.weightKey])
        print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey]," najlaksi link je prema ", m.id)        
        #...marks this edge as branch...        
        #node.memory[self.bestEdgeKey]=m?!?! 
        node.memory[self.linkStatusKey][m]='BRANCH' #edge prestaje biti basic, postaje rejected ili branch, tako se izbjegava da ponovno bude odabran         
        node.memory[self.levelKey]=0 
        node.status='FOUND' 
        node.memory[self.findCountKey]=0
        #node.memory[self.bestEdgeKey]=m #ja dodala
        
        #...sends a message called Connect and goes into the state Found
        #Jer na početku je on sam root
        node.send(Message(header="Connect", data=0, destination=m))
        print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "Zelim se mergati sa", m.id, "!")        
   
    def receipt_of_connect(self, node, message):
        j=message.source
        L=message.data
        
        # In Sleeping True: j.memory[self.levelKey]> || == node.memory[self.levelKey]       
        if L < node.memory[self.levelKey]:
             node.memory[self.linkStatusKey][j]='BRANCH'#Ne moram mu slati Test/Outside?
             #send Initiate(LN, FN, SN) on edge j; ja mislim da je to sve sadržano u message.source
             #Ime neka nije od prvog koji pošalje Initiate nego svaki za sebe izračuna

             #If node n' has not yet sent its report message at the given level, 
             #fragment F simpley joins fragment F' and participates in finding the minimum-weight outgoing edge from the enlarged fragment...

             #...if on the other hand node n' (receiver) has allready sent its report message, 
             #then we can deduce that outgoing edge from node n' (receiver) 
             #has a lower weight than minimum-weight outgoing edge from F (sender of Connect)
             #this eliminates the necessity for F to join the search for the minimum-weight outgoing edge
             
             l=[node.memory[self.levelKey],node.memory[self.nameKey],node.status]
             
             node.send(Message(header="Initiate", data=l , destination=j))         
             node.memory[self.findCountKey]=node.memory[self.findCountKey]+1
             #Due to our strategy of never making a low level fragment wait, node n' (reciever) immediatly 
             #sends an Initiate message with identity and level parameteters of F' and L' to n                 
             print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "absorbtion ", node.memory[self.nameKey], " apsorbira grad", j.memory[self.nameKey], "preko noda", j.id )
        
        elif node.memory[self.linkStatusKey][j]=='BASIC': #UNUSED
			 #then place received message on end of queue
            node.memory[self.queueKey].append(message)
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "stavljam poruku",message.header,"od", j.id ,"u red")
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "jos cekam odgovor od svog merge linka?")
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey]," ne odgovaram nepoznatima, moj je level manji?!", j.id)      
            #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
        else:                
            #print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "svi link statusi", node.memory[self.linkStatusKey]) 
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], node.memory[self.linkStatusKey][j],"je status linka prema", j.id)
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], " in ", node.status," usporedujem levele", node.memory[self.levelKey], j.memory[self.levelKey])                
        
            if node.id<j.id : 
                new_name=node.id
            else:
                new_name=j.id
            l=[node.memory[self.levelKey]+1,new_name,'FIND']
            node.send(Message(header="Initiate", data=l , destination=j))                                
            #u data šalje novo ime i link!, ne treba si ga sam postavljati!
            #njemu će postaviti Initiate poruka koju ce primiti na svom merge linku                    
            print( node.memory[self.nameKey], " friendly-merge ",  j.memory[self.nameKey], "  se zeli mergat sa mnom " )
            #friendly merge
            
    def receipt_of_initiate(self,node,message):
        j=message.source
        old_level=node.memory[self.levelKey]
        node.memory[self.levelKey]=message.data[0]
        new_level=node.memory[self.levelKey]         
        
        node.memory[self.nameKey]=message.data[1]
        
        print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "iz",node.status,"u",message.data[2])
        node.status=message.data[2]  #ili FIND ili FOUND
        
        node.memory[self.inBranchKey]=j #To je upitno, razlika sa knjigom!!
        node.memory[self.bestEdgeKey]=None
        node.memory[self.bestWtKey]=[sys.maxint,sys.maxint,sys.maxint]
        destination_nodes=list()
   
        for i in  node.memory[self.linkStatusKey]:
            if i.id!=j.id and node.memory[self.linkStatusKey][i]=='BRANCH': #i != j
                destination_nodes.append(i)
                if(node.status=='FIND'):
                    node.memory[self.findCountKey]=node.memory[self.findCountKey]+1               
        l=message.data
        node.send(Message(header="Initiate", data=l, destination=destination_nodes)) #broadcast po svom stablu
        print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "broadcast Initiate ", destination_nodes)            
        #if new_level>old_level and len(node.memory[self.queueKey])>0:
            #self.dequeue_and_process_message(node)
            #pass
        if node.status=='FIND':                       
            # When a node recieves this initiate message it starts to find 
            # its minimum-weight outgoing edge
            # moze li ovdje pop iz queue?!    
            #The nodes in fragment F go into state Find or Found depending on this parameter 
            #of the initiate message, and they send Test messages only in the Find state.
            self.test(node)
            
    def receipt_of_test(self,node,message):
            
            j=message.source
            L=message.data[0] # 0 je level - kasnije pretvoriti u dictionary da bude razumljivije
            N=message.data[1]
            #when a node recieves sush a test message, it checks weather or not its own fragment identity agrees with that of the test message...            
            if L>node.memory[self.levelKey]:
                #..if the recieving node's fragment level is less than that of 
                #the test message then the recieving node delays any response 
                #until its own level increasses sufficiently                
                node.memory[self.queueKey].append(message)#then place received message on end of queue
                print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "ja sada ne mogu odgovoriti jer je moj level manji od posiljatelja ", j.id)
                #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))                
            elif N != node.memory[self.nameKey]:
                # if the node recieving node has a different identity from the test message 
                # and if the recieving node's fragment level is greather than or equal to that of the test message
                # then the Accept message is sent back to the sending node                    

                #Ali to je staro ime? Prije absporba?
                print("posiljatelj, primatelj", N , node.memory[self.nameKey])
                node.send(Message(header="Accept", data=0, destination=j))
                print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "Accepting", j.id)                 
                #Zasto on sebi ne postavlja node u status BRANCH?

                #when a node a sends an Accept message in response to B's Test message, 
                #then the fragment identity of A differs and will continue to differ,
                #from B's current fragment identity
                #Zasto on sebi ne postavlja node u status BRANCH?
                
            else:
                if node.memory[self.linkStatusKey][j]=='BASIC': #UNUSED
                   node.memory[self.linkStatusKey][j]='REJECTED'
                   #if node.memory[self.testEdgeKey]!=j or node.memory[self.testEdgeKey]==None:
                   print(node.id, "mijenjam status linka prema ", j)
                if node.memory[self.testEdgeKey]!=j: #id!!!
                   node.send(Message(header="Reject", data=0, destination=j))
                   print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "Rejecting", j.id) 
                else:
                   print("Test!") 
                   self.test(node)
                   

    def test(self,node):
        test_nodes={}        
        
        for key in node.memory[self.linkStatusKey]:
            if node.memory[self.linkStatusKey][key]=='BASIC': #mozda ne radi?!              
                #test_nodes[key]=node.memory[self.linkStatusKey][key]
                test_nodes[key]=node.memory[self.weightKey][key]
                  
        if len(test_nodes)!=0:
            test_node=self.adjacent_node_of_minimum_weight(test_nodes)
            node.memory[self.testEdgeKey]=test_node
            l=[node.memory[self.levelKey],node.memory[self.nameKey]] #SHIT
            
            node.send(Message(header="Test", data=l, destination=node.memory[self.testEdgeKey]))
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey]," najlaksi link je prema ", test_node.id, "saljem Test") #edge prestaje biti basic, postaje rejected ili branch, tako se izbjegava da ponovno bude odabran
        else:
            node.memory[self.testEdgeKey]=None
            self.report(node)
                   
    def receipt_of_report(self,node,message):
        #Eventualy, the nodes adjacent to the core send Report on the core branch itself, 
        #allowing each of these nodes to determine both the weight o the minimum
        #outgoing edge and the side of the core on which this edge lies
        j=message.source
        w=message.data
        #tko je kome parent!!!
        if j!=node.memory[self.inBranchKey]: 
            node.memory[self.findCountKey]=node.memory[self.findCountKey]-1
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "compare",w,node.memory[self.bestWtKey])    
            if w[0]<node.memory[self.bestWtKey][0] or (w[0]==node.memory[self.bestWtKey][0] and w[1]<node.memory[self.bestWtKey][1]) or ( w[0]==node.memory[self.bestWtKey][0] and w[1]==node.memory[self.bestWtKey][1] and w[2]<node.memory[self.bestWtKey][2]):
                node.memory[self.bestWtKey]=w
                node.memory[self.bestEdgeKey]=j
                print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey],"azuriram svoj bestWt i Edge")
            self.report(node)
        elif node.status=='FIND':
            #then place received message on end of queue
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "ne mogu proslijediti jer jos uvijek trazim (FIND)?!")
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "nisam dobio odgovor na Test")            
            node.memory[self.queueKey].append(message)
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "stavljam poruku",message.header,"od", j.id ,"u red")
            #print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey])
            #self.network.outbox.insert(0, Message(header=message.header,data=message.data,destination=node, source=message.source))
        elif w[0]>node.memory[self.bestWtKey][0] or (w[0]==node.memory[self.bestWtKey][0] and w[1]>node.memory[self.bestWtKey][1]) or ( w[0]==node.memory[self.bestWtKey][0] and w[1]==node.memory[self.bestWtKey][1] and w[2]>node.memory[self.bestWtKey][2]):
            self.change_root(node)
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "change root")
            #After the two core nodes have exchanged Report message, 
            #the bestEdge saved by the fragment nodes makes it posible to 
            #trace the path from core to the node having minimum waight
        elif w==node.memory[self.bestWtKey]:
            print("HALT")
            if w==node.memory[self.bestWtKey] and node.memory[self.bestWtKey]==[sys.maxint,sys.maxint,sys.maxint]:
                node.memory[self.debugKey]='HALT'
                node.memory[self.haltKey]=True  
                 

    
    def report(self,node):
        if node.memory[self.findCountKey]==0 and node.memory[self.testEdgeKey]==None:
            #node.status='FOUND' #when a node sends a Report Message 
            #it also goes to the state FOUND
            node.status='FOUND'
            node.send(Message(header="Report", data=node.memory[self.bestWtKey], destination=node.memory[self.inBranchKey]))            
            print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "saljem report tezine svog najlakseg linka ", node.memory[self.bestWtKey], "svome parentu:", node.memory[self.inBranchKey].id)

#            if node.memory[self.bestWtKey] == [sys.maxint,sys.maxint,sys.maxint]:
#                print (node.id, "moj bestWtKey je infinity!")
#                node.memory[self.debugKey]='TERMINATED'

            #In particular, each leaf node of the fragment, that is
            #each node adjacent to only one fragment branch, 
            # sends the Report(W) on its inbound branch
            # W is the weight of the minimum-weight outgoing edge from the node 
            #and W is infinity if there are no outgoing edges
            
            #Similarly each interior node of the fragment waits until it has both found it's own minimum-weighted outgoing edge
            # and received message on all outbound fragment branches

            
    def change_root(self,node):
        #!=None?             
#        if node.memory[self.bestEdgeKey]!=None and node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]=='BRANCH':
        print(node.id, "lvl:", node.memory[self.levelKey],"n:",node.memory[self.nameKey], "best-edge link status", node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]])        
        if node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]=='BRANCH':
            node.send(Message(header="Change Root", data=0, destination=node.memory[self.bestEdgeKey]))
            print("Radi li change root?")
        else:
            node.send(Message(header="Connect", data=node.memory[self.levelKey], destination=node.memory[self.bestEdgeKey]))
            node.memory[self.linkStatusKey][node.memory[self.bestEdgeKey]]='BRANCH'
            print("IKAD?")            
            #when this message reaches the node with minimum-weight outgoing edge, 
            #the inbound edge form a rooted tree, rooted at this node
            #Finally this node sends the message Connect(L) over the minimum-weighted outgoing edge
                    
        
    def adjacent_node_of_minimum_weight(self,d):
        
        orderedDict = collections.OrderedDict(sorted(d.iteritems(), key=lambda (k,v):v[0]))            
        
        min_1= orderedDict.values()[0][0]        
        uzi_izbor={}              

        for o in orderedDict:
            if orderedDict[o][0] == min_1:
                uzi_izbor.update({o:orderedDict[o]})            
        orderedDict = collections.OrderedDict(sorted(uzi_izbor.iteritems(), key=lambda (k,v):v[1]))       
        min_2= orderedDict.values()[0][1]        

        #KRIVO!
        uzi_izbor={}              
        for o in orderedDict:
            if orderedDict[o][1] == min_2:
                uzi_izbor.update({o:orderedDict[o]})         
        orderedDict = collections.OrderedDict(sorted(uzi_izbor.iteritems(), key=lambda (k,v):v[2]))               
        
        return orderedDict.keys()[0]       
    
            
    def min_weight_two_lists(self,a,b):  
        
        if a[0]<b[0]:
            return a
        elif b[0]<a[0]:   
            return b
        elif a[1]<b[1]:
            return a
        elif b[1]<a[1]: 
            return b
        elif a[2]<b[2]:
            return a
        elif b[2]<a[2]: 
            return b
        else:
            return None # ==

    STATUS = {
              'SLEEPING': sleeping,
              'FIND':find,
              'FOUND':found,
              #'TERMINATED':terminated,
             }