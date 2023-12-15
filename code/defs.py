import random
import copy
import time
# from event import Event
import numpy as np
from queue import Queue
from graphviz import Graph
from pathlib import Path
from BlockEvent import BlockEvent
from TxnEvent import TxnEvent
import hashlib
import pygraphviz as pgv
def dfs(visited,node):
    if node not in visited:
        visited.add(node)
        for n in node.Neighbourlist:
            visited = dfs(visited, n[1])
    return visited

class Transaction:
    def __init__(self, sender, receiver, coins,Txn_msg, timestamp):
        self.sender = sender
        self.receiver = receiver
        self.coins = coins
        self.Txn_msg = Txn_msg
        self.timestamp = timestamp
        self.TxnID = self.computehash(Txn_msg,timestamp)
    #computing hash for the transaction using timestamp and their transaction message
    def computehash(self, Txn, timestamp):
        concat_tnx = Txn+" "+str(timestamp)
        result = hashlib.sha256(concat_tnx.encode('utf-8'))
        return result.hexdigest()
    def __repr__(self):
        data = (self.TxnID, self.sender, self.receiver, self.coins)
        return "<Txn %s: From=%s, To=%s, amount=%s>" %data
            
        
class Block:
    def __init__(self,createrid,prev_hash, transactions, timestamp):
        self.timestamp = timestamp
        self.createrid = createrid
        self.transactions = transactions
        self.previous_hash = prev_hash
        self.summary = None
        self.hash = self.calculate_hash()
        self.size = len(transactions)*1000 #calculating size of blocks derived from transaction
        
    
    #Calculates the hash of the blocks
    def calculate_hash(self):
        
        concat_transaction = self.transactions[0].Txn_msg
        for trans in self.transactions[1:-1]:
            concat_transaction += (" "+trans.Txn_msg)
        result = hashlib.sha256(concat_transaction.encode())
        self.summary = result.hexdigest()
        #Find hash of the block(previous_hash||summary)
        concat = str(self.previous_hash) + " "
        concat += str(self.summary)
        result = hashlib.sha256(concat.encode('utf-8')).hexdigest()
        # print(result)
        self.hash = result
        return result
    
        
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        
    def create_genesis_block(self):
        # Create the first block in the blockchain
        pass
    
    def add_transaction(self, transaction):
        # Add a transaction to the list of pending transactions
        self.pending_transactions.append(transaction)
        
    def validate_transaction(self, transaction):
        # Validate a transaction by checking if the sender has enough balance
        sender_balance = self.get_balance(transaction.sender)
        if sender_balance >= transaction.amount:
            return True
        else:
            return False
        
    def get_balance(self, address):
        # Calculate the balance of a given address by iterating through the blockchain
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address:
                    balance -= transaction.amount
                if transaction.receiver == address:
                    balance += transaction.amount
        return balance
    
    def mine_pending_transactions(self, miner_address):
        # Mine pending transactions by adding them to a new block and adding the block to the blockchain
        for transaction in self.pending_transactions:
            if not self.validate_transaction(transaction):
                # If a transaction is invalid, remove it from the list of pending transactions and return False
                self.pending_transactions.remove(transaction)
                return False
        
        block = Block(self.pending_transactions, self.chain[-1].hash)
        self.chain.append(block)
        self.pending_transactions = []
        return True
    

class Node:
    def __init__(self, uid, speed, genesis_block, transaction_meantime,Kmean_time):
        self.uid = uid
        self.num_neighbour=0
        self.speed = speed
        self.cpu_type = None
        # self.cpu = cpu
        # self.balance = balance
        self.coins = random.randrange(73)
        self.transaction_meantime = transaction_meantime
        self.Kmean_time = Kmean_time
        self.all_transaction = {} #max-heap???
        # self.ListofBlocks= []
        self.Neighbourlist=[]
        self.pending_transactions=[]
        self.tails={} #blockchain tail
        self.all_block_ids = {}
        # self.ListofBlocks.append(genesis_block)
        self.block_tree = {}
        self.genesis_block = genesis_block
        self.block_tree[self.genesis_block.hash] = (self.genesis_block,1)
        # self.block_tree[self.genesis_block.hash] = (self.genesis_block,0)
        self.tails[self.genesis_block.hash] = (self.genesis_block,1)
        self.curr_mining_time = None
        self.longest_chain = (self.genesis_block,1)
        self.non_verified_blocks = {}
        self.non_verfied_transaction = {}
        self.timings = {}#block_id : arrival/creation time
        self.lead = 0
        self.priv_q = []
        self.attacktype = None
        self.total_block_count = 0
        self.block_in_lc = 0
        self.my_blk_in_lc = 0
        self.my_blk = 0

    #adding neighbours, called during graph formation
    def addNeighbour(self,node):
        self.Neighbourlist.append([node.uid,node,random.randrange(10,501)]) #
        self.num_neighbour +=1
        node.Neighbourlist.append([self.uid,self,random.randrange(10,501)])
        node.num_neighbour +=1


    
    #returns an object of TransactionEvent to be added to the heap of events
    def generateTransaction(self, N,global_time):
        to = random.randrange(N)
        while(to==self.uid):
            to = random.randrange(N)
        amount = random.randrange(0,self.coins+1)
        eventTime = global_time+np.random.exponential(self.transaction_meantime,1)
        Txn_msg = f'{str(self.uid)} pays {str(to)} {str(amount)} BTC'
        Txn = Transaction(self.uid,to,amount,Txn_msg,eventTime)
        
        self.timings[f'{str(Txn.TxnID)} : {Txn.Txn_msg} :: generate at {self.uid}'] = eventTime
        return TxnEvent(eventTime,self.uid,to,Txn,self.uid,self.uid)
    
    #receiving transaction with a delay pij + 
    def receiveTransaction(self,event,global_time):
        
        Txn = event.message
        events = []
        if Txn.TxnID in self.all_transaction.keys():
            return events
        self.non_verfied_transaction[Txn.TxnID] = Txn
        self.all_transaction[Txn.TxnID] = Txn
        fromID = Txn.sender
        toID = Txn.receiver
        #broadcasting the transaction to its peers
        for nnode in self.Neighbourlist:
            if nnode[0] != event.receivedfrom:
                delay = nnode[2] #nnode [2] stores the value of pij
                c_ij = None
                if self.speed=="fast" and nnode[1].speed=="fast":
                    c_ij = 100*1e6
                else:
                    c_ij = 5*1e6
                delay += (1000/c_ij)*1000 #in milliseconds
                d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
                delay += d_ij
                events.append(TxnEvent(global_time+delay,fromID,toID,Txn,nnode[0],self.uid))
                self.timings[f'{str(Txn.TxnID)} : ' + Txn.Txn_msg + f' : arrival at {self.uid}'] = global_time+delay
        return events
    
    def verify(self, block,global_time):
        under_verification_tnx = {} 
        events = []
        at = block
        while True:
            Txns = at.transactions
            # print(Txns)
            for Txn in Txns:
                if Txn.sender!="coinbase":
                    if Txn.sender in under_verification_tnx.keys():
                        under_verification_tnx[Txn.sender] -= Txn.coins
                    else:
                        under_verification_tnx[Txn.sender] = 0-Txn.coins  
                if Txn.receiver in under_verification_tnx.keys():
                        under_verification_tnx[Txn.receiver] += Txn.coins
                else:
                    under_verification_tnx[Txn.receiver] = Txn.coins
           
            if at.previous_hash==0:
                break
            at = self.block_tree[at.previous_hash][0]
        #Verification Process
        # print("under_verification_tnx")
        # print(under_verification_tnx)
        for amount in under_verification_tnx.values():
            # print(amount)
            if amount<0:
                #Illegal Block
                return ([],False)
        #delete all transactions present in the block from non_verified list
        for txn in block.transactions:
            if txn.TxnID in self.non_verfied_transaction.keys():
                del self.non_verfied_transaction[txn.TxnID]
        #add the block in the block_tree
        self.block_tree[block.hash] = (block, self.block_tree[block.previous_hash][1]+1)

        #If previous_hash is present in tails then
        #replace the tail with block 
        #else create new branch and add block to the leaf
        self.tails[block.hash] = (block,self.block_tree[block.previous_hash][1]+1)
        if block.previous_hash in self.tails.keys():
            del self.tails[block.previous_hash]
        #If longest_chain has been changed by adding current block
        if self.longest_chain[1]<self.tails[block.hash][1]:
            #Create new mining_time in both false and true mining event
            self.curr_mining_time = global_time+np.random.exponential(self.Kmean_time,1)
            #create New mining event for the node as per current mining time
            events.append(BlockEvent(self.curr_mining_time,self.uid,"all",None,self.uid,self.uid))
            self.longest_chain = self.tails[block.hash]
        #Now broadcast the block to the neighbours 
        return (events,True)  
    
    def receive_block(env, block,userid):
        #Receive a block from another peer.
        # isvalid = validate_transactions(block)
        # if isvalid:
        #     add_block_to_tree(block)
        #     for node in self.Neighbourlist:
        #         send_block(env, block)
        # else
        yield env.timeout(1)

    def send_transaction(peer_id, peers, transactions, size=1):
        # Generate a random interarrival time between transactions
        interarrival = random.expovariate(1 / 10)
        time.sleep(interarrival)

    #     # Add a new transaction to the list of transactions
    #     transactions.append({
    #         'peer_id': peer_id,
    #         'timestamp': time.time(),
    #         'size': size
    #     })

    #     # Choose a random peer to send the transaction to
    #     recipient_peer_id = random.choice(peers[peer_id])
    #     peers[recipient_peer_id].receive_block(transactions)

    #handling cases:
    #parent not present
    #suppose child block reaches the node before parent block, in this case if the node discards this block considering it invalid then it might increase the 
    #chances of forking and hence increasing the chances of the new block mined at this node to be orphaned
    #thus optimal strategy would be to save these blocks locally and wait for their parent to be found
    def receiveBlock(self,event,global_time):
        
        #If block already seen, prevent loop
        #made changes according to the conditions as mentioned in design document to accomodate 
        # attacks
        #Note: the changes made are also in accordance with handling the cases where child block received before the parent block
        block = event.message
        events=[]
        if block.hash in self.all_block_ids.keys():
            return []
        self.all_block_ids[block.hash] = 1
        self.timings[block.hash + f' arrival at {self.uid}'] = global_time
        #Check if parent of the block is in the block tree or not
        parent_hash = block.previous_hash
        if parent_hash not in self.block_tree.keys():
            if parent_hash not in self.non_verified_blocks.keys():
                self.non_verified_blocks[parent_hash] = {}
            self.non_verified_blocks[parent_hash][block.hash] = block
            #return empty event list
            # if self.uid==0:
            #     if block.createrid !=0 and self.lead>0:
            #         self.lead -=1
            # if self.uid!=0 or (block.createrid==0):
            #     fromID = block.createrid
            #     toID = "all"
            #     for nnode in self.Neighbourlist:
                    
            #         delay = nnode[2]
            #         c_ij = None
            #         if self.speed=="fast" and nnode[1].speed=="fast":
            #             c_ij = 100*1e6
            #         else:
            #             c_ij = 5*1e6
            #         delay += (1000000/c_ij)*1000 #in milliseconds
            #         d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
            #         # print(d_ij,c_ij)
            #         delay += d_ij
            #         # print(delay)
            #         events.append(BlockEvent(global_time+delay,fromID,toID,block,nnode[0]))
            return events
        num_blocks = 0
        q = Queue()
        q.put(block)
        num_blocks +=1
        events = []
        while(not q.empty()):
            curr_block = q.get()
            result = self.verify(curr_block, global_time)
            if result[1]:
                #legal
                events.extend(result[0])
                if curr_block.hash in self.non_verified_blocks.keys():
                    for child_id in self.non_verified_blocks[curr_block.hash].keys():
                        q.put(self.non_verified_blocks[curr_block.hash][child_id])
                        num_blocks +=1
                        self.lead -=1
                    if self.uid!=0 or (curr_block.createrid==0):
                        fromID = curr_block.createrid
                        toID = "all"
                        for nnode in self.Neighbourlist:
                            if nnode[0]!= event.receivedfrom: 
                                delay = nnode[2]
                                c_ij = None
                                if self.speed=="fast" and nnode[1].speed=="fast":
                                    c_ij = 100*1e6
                                else:
                                    c_ij = 5*1e6
                                delay += (1000000/c_ij)*1000 #in milliseconds
                                d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
                                # print(d_ij,c_ij)
                                delay += d_ij
                                # print(delay)
                                events.append(BlockEvent(global_time+delay,fromID,toID,block,nnode[0],self.uid))
                        
                    del self.non_verified_blocks[curr_block.hash]
        # return self.broadcastBlock(block,global_time,events)
        if self.uid==0 and block.createrid!=0:
            if block.createrid !=0 and ((self.lead==1 ) or self.lead>2):
                for _ in range(num_blocks):
                    if len(self.priv_q)!=0:
                        block = self.priv_q.pop(0)
                        self.all_block_ids[block.hash] = 1
                        fromID = block.createrid
                        toID = "all"
                        for nnode in self.Neighbourlist:
                            if nnode[0]!=event.receivedfrom:
                                delay = nnode[2]
                                c_ij = None
                                if self.speed=="fast" and nnode[1].speed=="fast":
                                    c_ij = 100*1e6
                                else:
                                    c_ij = 5*1e6
                                delay += (1000000/c_ij)*1000 #in milliseconds
                                d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
                                delay += d_ij
                                events.append(BlockEvent(global_time+delay,fromID,toID,block,nnode[0],self.uid))
                        self.block_tree[block.hash] = (block, self.block_tree[block.previous_hash][1]+1)
                self.lead-=1
                self.longest_chain = (block,self.longest_chain[1])
                self.tails[block.hash] = (block,self.block_tree[block.previous_hash][1]+1)
                if block.previous_hash in self.tails.keys():
                    del self.tails[block.previous_hash]
                # self.total_block_count +=1
            # elif block.createrid !=0 and self.lead==1 and self.attacktype=="stubborn":
            #     self.lead-=1

            elif block.createrid !=0 and self.lead==2:
                if self.attacktype=="selfish":
                    while len(self.priv_q)!=0:
                        self.all_block_ids[block.hash] = 1
                        block = self.priv_q.pop(0)
                        self.all_block_ids[block.hash] = 1
                        fromID = block.createrid
                        toID = "all"
                        for nnode in self.Neighbourlist:
                            if nnode[0] != event.receivedfrom:
                                delay = nnode[2]
                                c_ij = None
                                if self.speed=="fast" and nnode[1].speed=="fast":
                                    c_ij = 100*1e6
                                else:
                                    c_ij = 5*1e6
                                delay += (1000000/c_ij)*1000 #in milliseconds
                                d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
                                delay += d_ij
                                events.append(BlockEvent(global_time+delay,fromID,toID,block,nnode[0],self.uid))
                        # self.total_block_count +=1
                        self.block_tree[block.hash] = (block, self.block_tree[block.previous_hash][1]+1)
                    self.block_tree[block.hash] = (block, self.block_tree[block.previous_hash][1]+1)
                    self.longest_chain = (block,self.longest_chain[1]+1)
                    self.tails[block.hash] = (block,self.block_tree[block.previous_hash][1]+1)
                    if block.previous_hash in self.tails.keys():
                        del self.tails[block.previous_hash]
                    self.lead=0
                else:
                    for _ in range(num_blocks):
                        self.all_block_ids[block.hash] = 1
                        block = self.priv_q.pop(0)
                        self.all_block_ids[block.hash] = 1
                        fromID = block.createrid
                        toID = "all"
                        for nnode in self.Neighbourlist:
                            if nnode[0] != event.receivedfrom:
                                delay = nnode[2]
                                c_ij = None
                                if self.speed=="fast" and nnode[1].speed=="fast":
                                    c_ij = 100*1e6
                                else:
                                    c_ij = 5*1e6
                                delay += (1000000/c_ij)*1000 #in milliseconds
                                d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
                                delay += d_ij
                                events.append(BlockEvent(global_time+delay,fromID,toID,block,nnode[0],self.uid))
                        self.block_tree[block.hash] = (block, self.block_tree[block.previous_hash][1]+1)
                    self.longest_chain = (block,self.longest_chain[1])
                    self.tails[block.hash] = (block,self.block_tree[block.previous_hash][1]+1)
                    if block.previous_hash in self.tails.keys():
                        del self.tails[block.previous_hash]
                    self.lead-=1

            # elif block.createrid !=0 and self.lead==0: 
                
            #     while len(self.priv_q)!=0:
            #         self.all_block_ids[block.hash] = 1
            #         block = self.priv_q.pop(0)
            #         self.all_block_ids[block.hash] = 1
            #         fromID = block.createrid
            #         toID = "all"
            #         for nnode in self.Neighbourlist:
            #             if nnode[0] != event.receivedfrom:
            #                 delay = nnode[2]
            #                 c_ij = None
            #                 if self.speed=="fast" and nnode[1].speed=="fast":
            #                     c_ij = 100*1e6
            #                 else:
            #                     c_ij = 5*1e6
            #                 delay += (1000000/c_ij)*1000 #in milliseconds
            #                 d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
            #                 delay += d_ij
            #                 events.append(BlockEvent(global_time+delay,fromID,toID,block,nnode[0],self.uid))
            #         # self.total_block_count +=1
            #         self.block_tree[block.hash] = (block, self.block_tree[block.previous_hash][1]+1)
            #         self.tails[block.hash] = (block,self.block_tree[block.previous_hash][1]+1)
            #         if block.previous_hash in self.tails.keys():
            #             del self.tails[block.previous_hash]
            #     self.lead=0
            
            elif block.createrid!=0 and self.lead<=0:
                while len(self.priv_q)!=0:
                    block = self.priv_q.pop(0)
                    self.my_blk+=1
                    self.total_block_count +=1
                self.lead=0

        if self.uid!=0 or (block.createrid==0):
            fromID = block.createrid
            toID = "all"
            for nnode in self.Neighbourlist:
                if nnode[0] != event.receivedfrom:
                    delay = nnode[2]
                    c_ij = None
                    if self.speed=="fast" and nnode[1].speed=="fast":
                        c_ij = 100*1e6
                    else:
                        c_ij = 5*1e6
                    delay += (1000000/c_ij)*1000 #in milliseconds
                    d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
                    delay += d_ij
                    events.append(BlockEvent(global_time+delay,fromID,toID,block,nnode[0],self.uid))
            self.tails[block.hash] = (block,self.block_tree[block.previous_hash][1]+1)
            if block.previous_hash in self.tails.keys():
                del self.tails[block.previous_hash]
        return events
    
    def generateBlock(self,blockevent,global_time):
        #If curr_mine_time != event.eventTime then it means node recerived block before it's own mining can be finished and hence started POW again
        #In this case just return, as this is false mining event
        # made changes to accomodate where the attacker would mine based on whether the queue is empty or not
        if self.uid != 0:
            if self.curr_mining_time!=blockevent.eventTime:
                return []
        else:
            if self.curr_mining_time!=blockevent.eventTime and  self.lead<=0: 
                if self.attacktype=="selfish":
                    return []
                else:
                    if len(self.priv_q)==0:
                        return []
                    
        
            
        events = []
        #Genrate New block_mine event
        #Create new mining_time in both false and true mining event
        self.curr_mining_time = global_time+np.random.exponential(self.Kmean_time,1)
        #create New mining event for the node as per current mining time
        events.append(BlockEvent(self.curr_mining_time,self.uid,"all",None,self.uid,-1))
        #Now that it is confirmed curr Node has sucessfully mined the block
        #We verify the transactions and put in the block and call broadcast it
        verified_Txns = []
        #calculate the Transaction state till last block in the longest chain
        Txn_state = {} 
        lctxn = {}
        ind = -1
        if self.attacktype=="selfish":
            if self.lead<=0 and len(self.priv_q)==0:
                at = self.longest_chain[0]
            else:
                at = self.priv_q[-1]
                ind = -2
        else:
            if self.lead<=0 and len(self.priv_q)==0:
                at = self.longest_chain[0]
            else:
                at = self.priv_q[-1]
                ind = -2
        while True:
            Txns = at.transactions
            for Txn in Txns:
                lctxn[Txn.TxnID] = Txn
                if Txn.sender!="coinbase":
                    if Txn.sender in Txn_state.keys():
                        Txn_state[Txn.sender] -= Txn.coins
                        # print(type(Txn.coins))
                    else:
                        Txn_state[Txn.sender] = 0-Txn.coins  
                if Txn.receiver in Txn_state.keys():
                    Txn_state[Txn.receiver] += Txn.coins
                    # print(type(Txn.coins))
                else:
                    Txn_state[Txn.receiver] = Txn.coins
                    # print(type(Txn.coins))
            #Break the loop once Genesis Block reached
            if at.previous_hash==0:
                break
            if at.previous_hash in self.block_tree.keys():
                at = self.block_tree[at.previous_hash][0]
            else:
                at = self.priv_q[ind]
                ind-=1
        count = 0
        # print("Txn_state")
        # print(Txn_state)
        # Find valid transactions to put inside the block
        
        


        TxnIDs = self.all_transaction.keys()
        size = len(self.all_transaction)
        valid = 0
        for TxnID in TxnIDs:
            if TxnID not in lctxn.keys():
                count += 1
                Txn = self.all_transaction[TxnID]
                if Txn.sender != "coinbase":
                    if Txn.sender  in Txn_state.keys():

                        if Txn_state[Txn.sender] < Txn.coins:
                            continue
                        Txn_state[Txn.sender] -= Txn.coins
                    

                if Txn.receiver in Txn_state.keys():

                    Txn_state[Txn.receiver] += Txn.coins
                else:
                    Txn_state[Txn.receiver] = Txn.coins

                # print(type(Txn.coins))
                verified_Txns.append(Txn)
                valid +=1
                if  count>=size or valid>=1000:
                    break
        # print("Txn_state")
        # print(Txn_state)
        for Txn in verified_Txns:
            if Txn.TxnID in self.non_verfied_transaction.keys():
                del self.non_verfied_transaction[Txn.TxnID]
            
        verified_Txns.append(Transaction("coinbase",id,50,str(self.uid)+" mines 50 BTC",global_time))
        if self.attacktype=="selfish":
            if self.lead<=0 and len(self.priv_q)==0:
                parent = self.longest_chain[0]
            else:
                parent = self.priv_q[-1]
        else:
            if self.lead<=0 and len(self.priv_q)==0:
                parent = self.longest_chain[0]
            else:
                parent = self.priv_q[-1]
        # parent = self.longest_chain[0]
        lon = self.longest_chain[1]
        
        block = Block(self.uid,parent.hash,verified_Txns,blockevent.eventTime)
        
        self.timings[block.hash + f' generated at {self.uid}'] = global_time
        
        
        
        if self.uid!=0 or (self.attacktype=="selfish" and self.lead==0):
 
            self.block_tree[block.hash] = (block, lon+1)
            self.longest_chain = (block, lon+1)
            self.tails[block.hash] = (block,self.block_tree[block.previous_hash][1]+1)
            if block.previous_hash in self.tails.keys():
                del self.tails[block.previous_hash]
            self.all_block_ids[block.hash] = 1
            fromID = block.createrid
            toID = "all"
            for nnode in self.Neighbourlist:
                
                delay = nnode[2]
                c_ij = None
                if self.speed=="fast" and nnode[1].speed=="fast":
                    c_ij = 100*1e6
                else:
                    c_ij = 5*1e6
                delay += (1000000/c_ij)*1000 #in milliseconds
                d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
                delay += d_ij
                events.append(BlockEvent(global_time+delay,fromID,toID,block,nnode[0],-1))
            # self.total_block_count +=1
        else:
            self.priv_q.append(block)
            self.lead +=1
        return events
    
    def visualize(self):
        tree = {}
        for block_id in self.block_tree.keys():
            self.total_block_count +=1
            if self.block_tree[block_id][0].createrid==0:
                self.my_blk +=1
            parent_hash = self.block_tree[block_id][0].previous_hash
            if parent_hash not in tree.keys():
                tree[parent_hash] = {}
            tree[parent_hash][block_id] = self.block_tree[block_id][0]
        queue = Queue()
        queue.put(0)
        graph = Graph('parent',filename=str(self.uid))
        graph.attr(rankdir='LR',splines='line')
        count = 0
        hash = {}
        while not queue.empty():
            size = queue.qsize()
            temp = Graph('child')
            while size>0:
                parent_hash = queue.get()
                for child_id in tree[parent_hash].keys():
                    
                    if tree[parent_hash][child_id].createrid==self.uid:
                        temp.node(str(count),color='blue')
                    else:
                        temp.node(str(count),color='red')
                    hash[child_id] = str(count)
                    if parent_hash!=0:
                        graph.edge(str(count),hash[tree[parent_hash][child_id].previous_hash])
                    count += 1
                    if child_id in tree.keys():
                        queue.put(child_id)
                size -= 1
            graph.subgraph(temp)
        graph.render('blocktree/'+str(self.uid), view=False) 
        self.block_in_lc=0
        at = self.longest_chain[0]
        while True:
            self.block_in_lc+=1
            if at.createrid==0:
                self.my_blk_in_lc +=1
            if at.previous_hash==0:
                break
            at = self.block_tree[at.previous_hash][0]


    def saveTime(self):
        file = open("sim/"+str(self.uid)+"sim.txt",'w')
        for keys in self.timings.keys():
            obj = str(keys) +": "+str(self.timings[keys])+"\n"
            file.write(obj)
        file.close()





class Network:
    def __init__(self,Nodes:set):
        self.n=len(Nodes)
        self.Nodes=Nodes
        # self.adjlist = {}

    def create_net(self,conn):
        print(conn)
        nodeset = set()
        temp_sets = [set() for _ in range(self.n)]
        attnode = None
        for node in self.Nodes:
            if node.uid!=0:
                nodeset.add(node)
                temp_sets[node.uid].add(node)
            else:
                attnode = node
        # for node in nodeset:
        a = list(nodeset)
        temp_nodes = random.sample(list(a),conn)
        for node in temp_nodes:
            attnode.addNeighbour(node)

        for node in self.Nodes:
            if node in nodeset:
                # print("laskgh")
                num=random.randint(4-node.num_neighbour,8-node.num_neighbour)
                
                if num<0:
                    num = 8-node.num_neighbour
                temp_set = temp_sets[node.uid]
                # temp_set.add(node)
                
                
                # print(type(temp_node[0]))
                while num!=0:
                    # print(temp_node[0].uid)
                    a = set(nodeset.difference(temp_set))
                    if len(a)==0:
                        if node.num_neighbour<4:
                            self.reset_net()
                            self.create_net()
                        else:
                            nodeset.remove(node)
                            break
                    temp_node = random.sample(list(a),1)
                    node.addNeighbour(temp_node[0])
                    if temp_node[0].num_neighbour==8:
                        nodeset.remove(temp_node[0])
                    if node.num_neighbour==8:
                        nodeset.remove(node)
                    # print(len(self.Nodes))
                    temp_set.add(temp_node[0])
                    num -=1

    def reset_net(self):
        for node in self.Nodes:
            node.num_neighbour=0
            node.Neighbourlist = []

    def isconnected(self):
        visited = set()
        node = list(self.Nodes)[0]
        visited = dfs(visited,node)
        if len(visited)== self.n:
            return True
        else:
            return False
        
    def visualize_network(self):
        graph = pgv.AGraph(directed=False)
        for node in self.Nodes:
            if node.cpu_type=='High':
                graph.add_node(node.uid,color='yellow')
            else:
                graph.add_node(node.uid)
        for node in self.Nodes:
            for peer in node.Neighbourlist:
                if node.speed=='slow' or peer[1].speed=='slow':
                    graph.add_edge(node.uid, peer[0],color='red')
                else:
                    graph.add_edge(node.uid, peer[0],color='green')
        graph.layout(prog='dot')
        graph.draw('network.png')



