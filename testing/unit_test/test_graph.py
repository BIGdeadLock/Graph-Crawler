import unittest

from src.data_structure.graph.callbacks.callback import CallbackResult
from src.data_structure.graph.graph import WebGraph
from src.utils.config import Config


class TestGraph(unittest.TestCase):

    def setUp(self):
        config = Config()
        self.graph1 = WebGraph(config=config)
        self.graph2 = WebGraph(config=config)

    def test_graph_merge(self):
        # Add the url nodes to the graph
        self.graph1.add(CallbackResult(domain="test.com",url="http://www.test.com/welcome",
                                      data="http://www.test.com/hello", type="url"))
        self.graph1.add(CallbackResult(domain="test.com",url="http://www.test.com/hello",
                                        data="fake.email@gmail.com", type="email"))
        self.graph2.add(CallbackResult(domain="nice-website.com",url="nice-website.com/fake",
                                        data="nice-website.com/fake", type="url"))
        self.graph2.add(CallbackResult(domain="nice-website.com",url="nice-website.com/fake",
                                        data="bigemai@gmail.com", type="email"))
        # Merge the graphs
        self.graph1.merge_graph(self.graph2)
        # Check that the nodes were added to the graph
        self.assertEqual(len(self.graph1.nodes), 5)
        self.assertEqual(len(self.graph1.edges), 4)
        # Check that the caches were merged
        self.assertEqual(len(self.graph1.cache['url']), 2)
        self.assertEqual(len(self.graph1.cache['email']), 2)
