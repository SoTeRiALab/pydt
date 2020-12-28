import unittest
from ..dtbase import model

class TestGraph(unittest.TestCase):
    def __init__(self):
        self.empty = model()
        self.imported = model()
        self.export = model()
        self.testnodes = model()
        self.testlinks = model()

    # test build empty graph
    def test_empty(self):
        self.assertFalse(len(self.empty.nodes()))
        self.assertFalse(len(self.empty.nodes()))

    # test build empty graph
    def test_add_nodes(self):
        self.testnodes.import_data()