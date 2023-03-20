import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pandas as pd
from src.data_structure.graph.callbacks.callback import CallbackResult
from src.utils.tools import EMAIL_REGEX
import logging as log
import jsonpickle
from jinja2 import Template
import src.utils.constants as consts
from src.utils.tools import extract_base_url
from networkx.readwrite.json_graph import node_link_data
from src.data_structure.graph.utils import Normalizer
from src.utils.tools import save_pickle, load_pickle

class WebGraph(nx.Graph):

    def __init__(self, callbacks = None, alpha = 0.8):
        super().__init__()
        self._name_corpus, self._type_corpus = [], []
        self._cache = {}
        self._urls_tf_idf_index = {}
        self._callbacks = callbacks or []
        self._proba = None
        self._alpha = alpha

    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, value):
        self._cache = value

    @Normalizer()
    def add(self, new_data: CallbackResult):
        """
        Add the scraped data to the graph. The graph will know how to handle the data.
        :param scraped_res: ScraperResult. The scraped data to add
        :return:
        """
        data = new_data.data
        v = extract_base_url(new_data.url)
        u = data
        self.add_node(v, domain=new_data.domain, type=consts.URL_TYPE_TOKEN)
        self.add_node(u, domain=new_data.domain, type=new_data.type)
        self._cache.setdefault(new_data.type, set()).add(u)
        self.add_edge(u, v, weight=0)

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
        self._add_weights_scores()
        ranking = self.get_ranking()
        clusters = self._get_domains_cluster()
        top_n = []
        for domain in clusters:
            top_n.append({domain: sorted(clusters[domain], key=lambda x: ranking[x], reverse=True)[:n]})

        return top_n

    def merge_graph(self, graph):
        """
        Merge the graph with the current graph. The cache will be merged as well
        :param graph: WebGraph. The graph to merge with
        :return:
        """
        self.add_nodes_from(graph.nodes(data=True))
        self.add_edges_from(graph.edges(data=True))
        self._cache = {**self._cache, **graph.cache}

    def get_ranking(self) -> dict:
        """
        Generate the ranking scores for each node in the graph. The score is the pagerank score
        :return: dict: {node: rank}
        """
        return nx.pagerank(self, weight='weight')

    def _add_weights_scores(self):
        """
        Add the weights to the edges. The score is the tf-idf score of the email address in the url
        :return:
        """
        vectorizer = TfidfVectorizer(use_idf=True, lowercase=False, smooth_idf=True, token_pattern=EMAIL_REGEX)  # No lowercase to preserve the emails
        if not self._name_corpus:
            self._build_corpus()

        tfidf_matrix = vectorizer.fit_transform(self._name_corpus)
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        # add tf-idf scores to the edge weights between emails and urls
        for url, idx in self._urls_tf_idf_index.items():
            for neighbor in self.neighbors(url):
                try:
                    node_type = self.nodes[neighbor]['type']
                    proba_score = 0
                    if node_type != consts.URL_TYPE_TOKEN:
                        proba_score = self._proba[neighbor]

                    total_score = tfidf_df.loc[idx, neighbor].item() * self._alpha + proba_score * (1 - self._alpha)
                    self.edges[url, neighbor]['weight'] = total_score
                except KeyError:
                    # The neighbor is an url and not an email
                    pass

    def _build_corpus(self):
        urls = self._cache[consts.URL_TYPE_TOKEN]
        idx = 0  # The index of the url in the corpus
        for url in urls:
            # Get all the neighbors for that url that are not of type URL
            neighbors = [n for n in self.neighbors(url) if self.nodes[n]['type'] != consts.URL_TYPE_TOKEN]
            if neighbors:
                # Some urls are connected to only other urls meaning that no emails were found in the url
                self._name_corpus.append(" ".join([n.split("@")[0] for n in neighbors]))  # Add the name of the email to the corpus
                self._type_corpus.append(" ".join([n.split("@")[1] for n in neighbors]))  # Add the type of the email to the corpus
                # Save the index of the url in the corpus
                self._urls_tf_idf_index[url] = idx
                idx += 1 # Increment the index only for email urls

    def _create_email_type_probabilities_distribution(self) -> pd.Series:
        """
        Build the probability distribution for the email types
        :return:
        """
        vectorizer = CountVectorizer(token_pattern="[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        count_matrix = vectorizer.fit_transform(self._type_corpus)
        count_df = pd.DataFrame(count_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        self._proba = count_df.sum() / count_df.sum().sum()

    def _get_domains_cluster(self) -> dict:
        """
        Get the domain cluster
        :return: dict of dict: {node: List of nodes in the cluster}
        """
        clusters = {}
        for node in self.nodes:
            if "domain" in self.nodes[node] and self.nodes[node]['type'] == consts.URL_TYPE_TOKEN:
                clusters.setdefault(self.nodes[node]['domain'], set()).add(node)

        return clusters


def combine_graphs(graphs: list) -> WebGraph:
    """
    Combine the graphs from the different processes into one graph. The cache will be the union of all the caches
    :param graphs: list of graphs
    :return: WebGraph: combined graph
    """
    combined_graph = WebGraph()
    for graph in graphs:
        combined_graph.merge_graph(graph)

    return combined_graph


def serialize_graph(graph):
    return node_link_data(graph)


def load_graph(path: str) -> WebGraph:
    """
    Load the graph from the path
    :param path: string. The path to load the graph from
    :return: Graph object
    """
    return load_pickle(path)


def save_graph(path: str, graph: WebGraph):
    """
    Save the graph to the path and create a html file for the graph
    :param path: string. The path to save the graph to
    :param graph: Graph object
    :return:
    """
    nx.write_gml(graph, path.replace(".pkl", ".gml"))
    save_pickle(path, graph)
    create_html_for_graph(graph, consts.TEMPLATE_PATH)


def create_html_for_graph(graph: WebGraph, template_str: str):
    """
    Create the html for the graph
    :param graph: Graph object
    :param template_str: string. The html template
    :return: string. The html for the graph
    """
    # If the graph is too big it will take too long to render it. We will only render the top 20 nodes
    if len(graph.nodes) > 20:
        ranking = graph.get_ranking()
        top_20 = sorted(ranking, key=ranking.get, reverse=True)[:10]
        graph = graph.subgraph(top_20)

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
