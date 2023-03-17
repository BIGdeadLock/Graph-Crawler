import networkx as nx
from src.utils.tools import load_pickle, save_pickle
import logging as log
import jsonpickle
from jinja2 import Template
import src.utils.constants as consts


class WebGraph(nx.DiGraph):

    def __init__(self):
        super().__init__()
        self._node_counter = 0
        self._edge_counter = 0

    def add_domain_attr_to_node(self, node: str, domain: str):
        """
        Add the domain attribute to the node
        :param node: string. The node to add the attribute to
        :param domain: string. The domain to add
        :return:
        """
        nx.set_node_attributes(self, {node: domain}, 'domain')

    def add_type_attr_to_node(self, node: str, type: str):
        """
        Add the type attribute to the node
        :param node: string. The node to add the attribute to
        :param type: string. The type to add
        :return:
        """
        nx.set_node_attributes(self, {node: type}, 'type')

    def get_top_n_for_each_domain(self, n=5):
        """
        Get the top n most important nodes in each domain
        :param n: int. The number of nodes to return
        :return: list of dict: {domain: List of nodes and their rank in the domain}
        """
        ranking = self._get_ranking()
        clusters = self._get_domains_cluster()
        top_n = []
        for domain in clusters:
            top_n.append({domain: sorted(clusters[domain], key=lambda x: ranking[x], reverse=True)[:n]})

        return top_n

    def _get_ranking(self) -> dict:
        """
        Get the ranking of the nodes
        :return: dict: {node: rank}
        """
        return nx.eigenvector_centrality(self, weight='weight', max_iter=50000)

    def _get_domains_cluster(self) -> dict:
        """
        Get the domain cluster
        :return: dict of dict: {node: List of nodes in the cluster}
        """
        clusters = {}
        for node in self.nodes:
            if "domain" in self.nodes[node]:
                clusters.setdefault(self.nodes[node]['domain'], set()).add(node)

        return clusters


def combine_graphs(graphs: list) -> WebGraph:
    """
    Combine the graphs from the different processes into one graph
    :param graphs: list of graphs
    :return: combined graph
    """
    combined_graph = WebGraph()
    for graph in graphs:
        combined_graph = nx.compose(combined_graph, graph)

    return combined_graph

def serialize_graph(graph):
    return nx.adjacency_data(graph)

def load_graph(path: str) -> WebGraph:
    """
    Load the graph from the path
    :param path: string. The path to load the graph from
    :return: Graph object
    """
    return load_pickle(path)


def save_graph(path: str, graph: WebGraph):

    """
    Save the graph to the path
    :param path:
    :param graph:
    :return:
    """
    save_pickle(path, graph)
    create_html_for_graph(graph, consts.TEMPLATE_PATH)

def create_html_for_graph(graph: WebGraph, template_str: str):
    """
    Create the html for the graph
    :param graph: Graph object
    :param template_str: string. The html template
    :return: string. The html for the graph
    """
    data = nx.readwrite.json_graph.node_link_data(graph)

    # serialize the JSON data
    json_str = jsonpickle.encode(data)

    with open(template_str, 'r') as f:
        template_str = f.read()

    # create a Jinja2 template
    template = Template(template_str)

    # render the template with the JSON data
    html_str = template.render(json_str=json_str)

    log.info(f"Saving graph to {consts.GRAPH_TEMPLATE_PATH}")
    with open(consts.GRAPH_TEMPLATE_PATH, 'w') as f:
        f.write(html_str)