from pathlib import Path
from defs import Transaction,Node,Network,Block
from random import random, randrange,randint
from BlockEvent import  BlockEvent
from TxnEvent import TxnEvent
from EventQueue import EventQueue
import numpy as np

class InitializeSimulation():
    
    def __init__(self, path):
      
        
        self.nodes = []
        self.global_time = 0
        self.q = EventQueue()
        self.N = None
        self.z = None
        self.z1 =None
        self.Tmean = []
        self.Kmean = []
        self.termination_time = None

        #get the parameters from the command line
        #self.N=params["num_nodes"]
        #self.z1=params["low_percent"]
        #self.z=params['slow_percent']
        #self.Tmean=params["T_mean"]

        #reading the parameters from the path specified by us

        self.config_file_path = path
        file=open(path,"r")
        line_num=1
        for line in file:

            if line_num==1:
                self.N = int(line)
                line_num +=1
                continue

            elif line_num==2:
                self.z = int(line)
                # print(self.z)
                line_num +=1
                continue

            elif line_num==3:
                self.z1 = int(line)
                line_num +=1
                continue    

            elif line_num==4:
                self.conn = int(line)
                line_num +=1
                continue
            elif line_num==5:
                self.termination_time = int(line)
                break

        self.Tmean = [50000 for x in range(self.N)]
        #calculate total slow nodes passed as the percentage of the total nodes 
        slow_count = self.z
        #print(slow_count)
        slow_nodes = []
        #generating the slow nodes out of the n nodes
        # print(slow_count)
        for i in range(slow_count):

            # only adding the randomly generated peers whch are not  already in the slow_nodes (No duplicates)
            slow_node= randint(1,self.N-1)
            while(slow_node in slow_nodes):
                 slow_node= randint(1,self.N-1)

            slow_nodes.append(slow_node)

        # print(f"Slow Nodes: {slow_nodes}") 

        #Create Initial Money/Transaction to each Node
        initial_btc=np.random.randint(1,101,self.N)
        # print(initial_btc)
        print( f"Initial Bitcoin Balance for each Node: {initial_btc}")

        init_Txn = []
        for id in range(self.N):
            #1 init 10 BTC
            Txn_msg = str(id)+" init "+str(initial_btc[id])+" BTC"
            init_Txn.append(Transaction("coinbase",id,initial_btc[id],Txn_msg,self.global_time))


       
        

        #calculate total low cpu nodes passed as the percentage of the total nodes 
        low_count = int((self.z1*self.N)/100)
        #print(slow_count)
        low_nodes = []
        #generating the low cpu nodes out of the n nodes
        # print(low_count)
        for i in range(low_count):

            # only adding the randomly generated peers whch are not  already in the low_nodes (No duplicates)
            low_node= randint(1,self.N-1)
            while(low_node in low_nodes):
                 low_node= randint(1,self.N-1)

            low_nodes.append(low_node)
        print(f"low CPU nodes count: {low_count}")
        print(f"low CPU  Nodes: {low_nodes}") 
        print(f"slow nodes count: {slow_count}")
        print(f"slow Nodes: {slow_nodes}") 



        # hashing power of the low cpu (z1) in percentage
        attacktype = "stubborn"

        #creating the nodes with corresposding hashing power and btc balance
        y=0.33
        x = (1- y)/((100-self.z1-1)*10 + self.z1)
        genesis_block =Block(createrid=id,prev_hash=0,transactions=init_Txn,timestamp=self.global_time)
        node=Node(uid=0,speed="fast",genesis_block=genesis_block,transaction_meantime=self.Tmean[0],Kmean_time=600/y)
        node.attacktype=attacktype
        node.cpu_type="Low"
        self.nodes.append(node)
        for i in range(1,self.N):
            if i in slow_nodes :
                if i in low_nodes:
                    genesis_block =Block(createrid=id,prev_hash=0,transactions=init_Txn,timestamp=self.global_time)
                    node=Node(uid=i,speed="slow",genesis_block=genesis_block,transaction_meantime=self.Tmean[i],Kmean_time=600/x)
                    node.attacktype=attacktype
                    node.cpu_type="Low"
                    self.nodes.append(node)
                else:
                    genesis_block =Block(createrid=id,prev_hash=0,transactions=init_Txn,timestamp=self.global_time)
                    node=Node(uid=i,speed="slow",genesis_block=genesis_block,transaction_meantime=self.Tmean[i],Kmean_time=60/x)
                    node.cpu_type="High"
                    node.attacktype=attacktype
                    self.nodes.append(node)
            else:       
                if i in low_nodes:
                    genesis_block =Block(createrid=id,prev_hash=0,transactions=init_Txn,timestamp=self.global_time)
                    node=Node(uid=i,speed="fast",genesis_block=genesis_block,transaction_meantime=self.Tmean[i],Kmean_time=600/x)
                    node.cpu_type="Low"
                    node.attacktype=attacktype
                    self.nodes.append(node)   
                else:                
                    genesis_block =Block(createrid=id,prev_hash=0,transactions=init_Txn,timestamp=self.global_time)
                    node=Node(uid=i,speed="fast",genesis_block=genesis_block,transaction_meantime=self.Tmean[i],Kmean_time=60/x)
                    node.cpu_type="High"
                    node.attacktype=attacktype
                    self.nodes.append(node) 
        
        #Now we create the graph
        # print("before graph creation")

        Graph = Network(set(self.nodes))

        Graph.create_net(self.conn)
        Graph.visualize_network()
        # print("after graph creation")
        while not Graph.isconnected():
            Graph.reset_net()
            Graph.create_net()
        Graph.visualize_network()
       
        print("graph created")

        #Create Initial Tnx Event for each Node

        for id in range(self.N):
            # txn_time = self.global_time+np.random.exponential(self.nodes[id].Kmean_time,1)
            self.q.push(self.nodes[id].generateTransaction(self.N,self.global_time))

        #create initial Block Event
        for id in range(self.N):
            mining_time = self.global_time+np.random.exponential(self.nodes[id].Kmean_time,1)
            #create New mining event for the node as per current mining time
            self.q.push(BlockEvent(mining_time,id,"all",None,id,-1))
            self.nodes[id].curr_mining_time = mining_time
        
        Path("blocktree").mkdir(parents=True, exist_ok=True)
        Path("sim").mkdir(parents=True, exist_ok=True)
       