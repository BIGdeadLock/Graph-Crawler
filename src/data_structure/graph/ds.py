import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
import pandas as pd
from src.crawler.scraper.scraper import ScraperResult
from src.utils.tools import load_pickle, save_pickle, is_valid_url, EMAIL_REGEX
import logging as log
import jsonpickle
from jinja2 import Template
import src.utils.constants as consts
from src.utils.tools import extract_base_url
from networkx.readwrite.json_graph import node_link_data

class WebGraph(nx.Graph):

    def __init__(self):
        super().__init__()
        self._corpus = []
        self._urls = []
        self._emails = []
        self._urls_tf_idf_index = {}

    def add_scraped_data(self, scraped_res: ScraperResult):
        """
        Add the scraped data to the graph. The graph will know how to handle the data.
        :param scraped_res: ScraperResult. The scraped data to add
        :return:
        """
        for data in scraped_res.data:
            v = extract_base_url(scraped_res.url)
            self.add_node(v, domain=scraped_res.domain, type=consts.URL_TYPE_TOKEN)

            if scraped_res.type == consts.EMAIL_TYPE_TOKEN:
                u = data
                self._emails.append(u)
                self.add_node(u, domain=scraped_res.domain, type=consts.EMAIL_TYPE_TOKEN)
            else:
                u = extract_base_url(data)
                self._urls.append(u)
                self.add_node(u, domain=scraped_res.domain, type=consts.URL_TYPE_TOKEN)

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
        if not self._corpus:
            self._build_corpus()

        tfidf_matrix = vectorizer.fit_transform(self._corpus)
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        # add tf-idf scores to the edge weights between emails and urls
        for url, idx in self._urls_tf_idf_index.items():
            for email in self.neighbors(url):
                try:
                    self.edges[url, email]['weight'] = tfidf_df.loc[idx, email].item()
                except KeyError:
                    # The neighbor is an url and not an email
                    pass

    def _build_corpus(self):
        self._urls = [n for n, data in self.nodes(data=True) if data and data['type'] == consts.URL_TYPE_TOKEN]
        idx = 0 # The index of the url in the corpus
        for url in self._urls:
            # Get all the neighbors for that url and check for emails
            url_emails = [n for n in self.neighbors(url) if self.nodes[n]['type'] == consts.EMAIL_TYPE_TOKEN]
            if url_emails:
                # Some urls are connected to only other urls meaning that no emails were found in the url
                self._corpus.append(" ".join(url_emails))
                # Save the index of the url in the corpus
                self._urls_tf_idf_index[url] = idx
                idx += 1 # Increment the index only for email urls


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
    Combine the graphs from the different processes into one graph
    :param graphs: list of graphs
    :return: combined graph
    """
    combined_graph = WebGraph()
    for graph in graphs:
        combined_graph = nx.compose(combined_graph, graph)

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
    nx.write_gml(graph, path)
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
