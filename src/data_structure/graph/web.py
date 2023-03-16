import networkx


class WebGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self._node_counter = 0
        self._edge_counter = 0

def combine_graphs(graphs: list) -> WebGraph:
    """
    Combine the graphs from the different processes into one graph
    :param graphs: list of graphs
    :return: combined graph
    """
    combined_graph = WebGraph()
    for graph in graphs:
        combined_graph = networkx.compose(combined_graph, graph)

    return combined_graph

