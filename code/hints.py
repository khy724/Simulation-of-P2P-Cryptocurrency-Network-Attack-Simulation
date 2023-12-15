import random
import simpy

def peer(env, id, peers, transaction_rate, block_time, coins):
    """
    A peer in a P2P cryptocurrency network.
    """
    # Create a list to store blocks and transactions
    blocks = []
    transactions = []
    
    while True:
        # Generate a transaction
        transaction = 1
        transactions.append(transaction)
        
        # Wait for the interarrival time between transactions
        interarrival_time = random.expovariate(transaction_rate)
        yield env.timeout(interarrival_time)
        
        # Choose a random number of peers to send the transactions to
        num_peers = random.randint(4, 8)
        for i in range(num_peers):
            peer = random.choice(peers)
            # Send the transaction to a peer
            env.process(peer.send_transaction(env, transaction))
    
    while True:
        # Wait for a block to arrive
        block = yield block_queue.get()
        
        # Validate the transactions in the block
        valid = True
        for transaction in block['transactions']:
            if transaction not in transactions:
                valid = False
                break
        if not valid:
            continue
        
        # Add the block to the list of blocks
        blocks.append(block)
        
        # If the received block creates a new longest chain, mine a new block
        if len(blocks) > len(peer.longest_chain):
            peer.longest_chain = blocks
            new_block = {
                'prev_block': block['id'],
                'transactions': transactions,
                'id': env.now
            }
            # Wait for the PoW mining time
            yield env.timeout(block_time)
            # Broadcast the new block
            for p in peers:
                env.process(p.receive_block(env, new_block))
            # Reset the transactions list
            transactions = []
            
            # Increase the coin balance
            coins += 50

def send_transaction(env, transaction):
    """
    Send a transaction to another peer.
    """
    yield env.timeout(1)
    
def receive_block(env, block):
    """
    Receive a block from another peer.
    """
    yield env.timeout(1)
    
# Set the random seed for reproducibility
random.seed(0)

# Create an environment for the simulation
env = simpy.Environment()

# Create the peers
peers = [peer(env, i, peers, 1, 1, 0) for i in range(n)]

# Run the simulation
env.run(until=100)



# ########## chatgpt functions v2
import random
import time

def send_transaction(peer_id, peers, transactions, size=1):
    # Generate a random interarrival time between transactions
    interarrival = random.expovariate(1 / 10)
    time.sleep(interarrival)

    # Add a new transaction to the list of transactions
    transactions.append({
        'peer_id': peer_id,
        'timestamp': time.time(),
        'size': size
    })

    # Choose a random peer to send the transaction to
    recipient_peer_id = random.choice(peers[peer_id])
    peers[recipient_peer_id].receive_block(transactions)

def receive_block(peer_id, peers, blocks, transactions):
    # Validate the transactions in the block
    validated_transactions = []
    for transaction in transactions:
        # Check if the transaction has already been validated
        if transaction not in blocks:
            validated_transactions.append(transaction)

    # Add the validated transactions to the block
    blocks.append({
        'peer_id': peer_id,
        'timestamp': time.time(),
        'transactions': validated_transactions
    })

    # Check if the received block creates a new longest chain
    longest_chain = 0
    for block in blocks:
        if len(block['transactions']) > longest_chain:
            longest_chain = len(block['transactions'])

    # If the received block creates a new longest chain, simulate PoW mining
    if longest_chain == len(validated_transactions):
        time.sleep(random.expovariate(1 / 10))
        block_id = len(blocks)
        peers[peer_id].broadcast_block(block_id, validated_transactions)




#######chatgpt gyaan $######
# One way to handle invalid transactions without using UTXO (Unspent Transaction Output) is by using digital signatures. In this method, each transaction will include the sender's public key, a digital signature, and the receiver's public key. When a peer receives a transaction, it can verify the signature using the sender's public key and the transaction data. If the signature is valid, the transaction is considered valid, and the peer can add it to its block. If the signature is invalid, the peer will reject the transaction and not add it to the block. Additionally, peers can keep a record of all the valid transactions they have received, and check if a transaction is double-spent before adding it to the block. This can help prevent invalid transactions from being added to the block.


#######chatgpt code 2.0 handling invalid transactions

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        
class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        # Implement a hash function to return the hash value of the block
        # Example: hashlib.sha256(str(self).encode()).hexdigest()
        pass
        
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



###chatgpt gyaan 2.0

# This code defines a basic blockchain class with methods for adding transactions, validating transactions, calculating the balance of a given address, and mining pending transactions. The validate_transaction method checks if the sender of a transaction has enough balance to complete the transaction by iterating through the blockchain and adding up the balance of the sender. If the balance is insufficient, the transaction is considered invalid and removed from the list of pending transactions


###chatgpt code for genesis block,mine block 
import hashlib

def create_genesis_block():
  block = {
    'index': 0,
    'previous_hash': '0',
    'timestamp': 0,
    'transactions': [],
    'hash': '0'
  }
  return block

def add_transaction(block, transaction):
  block['transactions'].append(transaction)

def hash_block(block):
  block_string = str(block['index']) + block['previous_hash'] + str(block['timestamp']) + str(block['transactions'])
  return hashlib.sha256(block_string.encode()).hexdigest()

def validate_transaction(transaction):
  # To be implemented in a later step
  pass

def mine_block(block, difficulty_level):
  while True:
    block['hash'] = hash_block(block)
    if block['hash'][:difficulty_level] == '0' * difficulty_level:
      break
    block['index'] += 1


###In this code, create_genesis_block returns a dictionary with all the necessary data to represent a block in the blockchain. The add_transaction function takes a block and a transaction as input and appends the transaction to the list of transactions in the block. The hash_block function takes a block as input and returns the SHA-256 hash of the block, calculated by concatenating the string representation of its index, previous_hash, timestamp, and transactions. Finally, validate_transaction is a placeholder function that will be used to validate incoming transactions, and mine_block takes a block and a difficulty level as input, and mines a new block by incrementing its index until the hash of the block starts with difficulty_level zeros.