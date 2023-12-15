from EventQueue import EventQueue
from simInit import InitializeSimulation
from TxnEvent import TxnEvent
import random
# params={}
# @click.command()

# @click.option('--T_mean', '-a', type=(int))
# @click.option('--num_nodes',type=(int))
# @click.option('--slow_percent',type=(int))
# @click.option('--low_cpu',type=(int))
# def cli(num_nodes,slow_percent,low_cpu,T_mean)
#     params["T_mean"]=T_mean
#     params["num_nodes"]=num_nodes
#     params["slow_percent"]=slow_percent
#     params["low_cpu"]=low_cpu
if __name__=="__main__":
    # cli()
    # simulator =InitializeSimulation(params)
    simulator = InitializeSimulation('config.txt')
    random.seed(73)
    
    while(simulator.termination_time > simulator.global_time):
        event = simulator.q.pop()   ## both Blckevent and txn event can be addded to the simulator queue
        simulator.global_time = event.eventTime
        if isinstance(event,TxnEvent):
            #print("Inside Txn event")
            new_events = simulator.nodes[event.at].receiveTransaction(event,simulator.global_time)
            if event.at == event.fromID:
                new_events.append(simulator.nodes[event.at].generateTransaction(simulator.N, simulator.global_time))
        else:
            #print("Inside block event")
            if event.at==event.fromID:
                new_events = simulator.nodes[event.at].generateBlock(event,simulator.global_time)
            else:
                new_events = simulator.nodes[event.at].receiveBlock(event,simulator.global_time)
        for each_event in new_events:
            simulator.q.push(each_event)
        # print(simulator.global_time)
    print("Node","Non_ver_Tnx","Total_Tnx","Total_block_in_tree","Blockchain_len","Total_block_seen",sep="\t")
    count=0
    mpu_node_avg = -1
    mpu_node_ov = -1
    for node in simulator.nodes:
        
        print(count,len(node.non_verfied_transaction), len(node.all_transaction), len(node.block_tree), node.longest_chain[1], len(node.all_block_ids.keys()),sep='\t\t')
        #print(node.genesis_block.id)
        node.visualize()
        node.saveTime()
        if node.uid==0:
            if node.my_blk!=0:
                mpu_node_avg = node.my_blk_in_lc/node.my_blk 
                  
            if node.total_block_count!=0:
                mpu_node_ov = node.block_in_lc/node.total_block_count
                
               
        count+=1

    if mpu_node_avg!=-1:
        print(f"MPU_node_avg: {mpu_node_avg}")
    else:
        print("no blocks broadcasted by the adversary")
    if mpu_node_ov!=-1:
        print(f"MPU_node_overall: {mpu_node_ov}")
        
    else:
        print("no blocks created")

    
