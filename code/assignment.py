from defs import *
import sys
import argparse
import numpy as np
import random
import hashlib

parser = argparse.ArgumentParser()
parser.add_argument('--num-nodes', type=int, required=True)
parser.add_argument('--dist-mean', type=float, required=True)
parser.add_argument('--slow-percent', type=float, required=True)
parser.add_argument('--low-cpu-percent', type=float, required=True)

args = parser.parse_args()

n = args.num_nodes
tx = args.dist_mean
sp = args.slow_percent
lcp = args.low_cpu_percent


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

np.seed(0)
dij = np.random.exponential(scale=1/96,size=1) #1/kb
#cij 100 or 5mbps
pij = np.random.uniform(low=10,high=500,size=1)#ms

gen_block = create_genesis_block()

Nodeset = set()
speed = np.ones(n)
cpu = np.ones(n)
speed[:(n*sp)//100 +1]=0
cpu[:(n*sp)//100 +1]=0
np.random.shuffle(speed)
np.random.shuffle(cpu)

for i in range(n):
    node = Node(i,speed[i],cpu[i],100,gen_block)
    Nodeset.add(node)

Graph = Network(Nodeset)
Graph.create_net()

while not Graph.isconnected:
    Graph.reset_net()
    Graph.create_net()




