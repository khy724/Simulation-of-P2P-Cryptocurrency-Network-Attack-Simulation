import pygraphviz as pgv

def visualize_network(network):
    graph = pgv.AGraph(directed=True)
    nodes = network.keys()

    # Add nodes
    for node in nodes:
        graph.add_node(node)

    # Add edges
    for node, connections in network.items():
        for connection in connections:
            graph.add_edge(node, connection)

    graph.layout(prog='dot')
    graph.draw('network.png')

# Example network representation
network = {
    'Peer 1': ['Peer 2', 'Peer 3', 'Peer 4'],
    'Peer 2': ['Peer 3', 'Peer 4', 'Peer 5'],
    'Peer 3': ['Peer 4', 'Peer 5', 'Peer 6'],
    'Peer 4': ['Peer 5', 'Peer 6', 'Peer 7'],
    'Peer 5': ['Peer 6', 'Peer 7'],
    'Peer 6': ['Peer 7'],
    'Peer 7': []
}

visualize_network(network)