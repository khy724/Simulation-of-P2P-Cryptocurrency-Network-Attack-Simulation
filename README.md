# Simulation-of-a-P2P-Cryptocurrency-Network

This assignment has been done by -   
Anushka (200050011)  
Khyati Patel (200050102)  
Shrey Bavishi (200050132)  

### How to run?

install the dependencies from requirements.txt  
run simulation.py  using command- python simulation.py  
parameters can be set in config.txt  
(using conda is recommended)  

### config.txt

1.) number of nodes  (fixed to 100)
2.) % of slow nodes  (fixed to 50)
3.) % of low cpu nodes  
4.) % connectivity of adversary with honest nodes  

### Simulation output

sim/ - contains files the block and transaction logs for each node  
blocktree/ - contains files for blocktrees formed at each node
terminal output contains the following information:  
Non_ver_Tnx  
Total_Tnx  
Total_block_in_tree  
Blockchain_len  
Total_block_seen  

### References

hints.py  
visual.py  
https://researchbank.swinburne.edu.au/items/3af7943b-0240-42f1-9422-72c3df1d5e5a/1/
https://www.cs.cornell.edu/~ie53/publications/btcProcFC.pdf


