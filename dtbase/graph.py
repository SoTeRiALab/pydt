from collections import defaultdict
from itertools import combinations
from pandas import DataFrame

class dtbase:
    """
    Defines the DT-BASE causal model in a graph structure.

    Attributes
    ----------
        nodes : dict
            a map of unique node id strings onto a node object
        links : dict
            a map of unique link id strings onto a link object
        adj_list : defaultdict
            a modified adjacency list mapping a node onto all parent nodes that
            have a directed edge to it.
    """
    class node:
        """
        Defines a node in the graph for the DT-BASE model.
        """
        def __init__(self, name: str, keywords: list):
            """
            Constructs all necessary attributes for a node.

            Parameters
            ----------
                name : str  
                    the name of the node.
                keywords : str
                    a list of keywords associated with this node.
            """
            assert name, 'name cannot be an empty string'
            self.name = name
            self.keywords = keywords


    class link:
        """
        Defines a link between two nodes in the graph for the DT-BASE model.
        """
        def __init__(self, child_id: str, parent_id: str, m1: float, m2: float, m3: float,
            m1_memo: str = None, m2_memo: str = None, m3_memo: str = None,
            reference: ref = None):
            """
            Constructs all necessary attributes for a causal link.

            Parameters
            ----------
                child_id : str
                    the unique id of the child (effect) node in the link.
                parent_id : str
                    the unique id of the parent (cause) node in the link.
                reference : ref
                    a ref object storing the necessary metadata for the reference justifying the causal link.
                m1 : float
                    the credibility of the reference source on a scale of 0 to 1, with 0
                    being the least credible and 1 being the most credible.
                m1_memo : str
                    an explanation of the reasoning behind the choice of the m1 value.
                m2 : float
                    the weight between the parent and child node indicated in the evidence, with 0 being
                    the least weight, and 1 being the highest weight.
                m2_memo : str
                    an explanation of the reasoning behind the choice of the m2 value.
                m3 : float
                    the analyst's level of confidence on the subject matter on a scale of 0 to 1, with 0
                    being the least confidence and 1 being the highest confidence.
                m3_memo : str
                    an explanation of the reasoning behind the choice of the m3 value.

            """
            assert 0.0 <= m1 <= 1.0 and 0.0 <= m2 <= 1.0 and 0 <= m3 <= 1.0, 'm1, m2, and m3 must be floats between 0 and 1'
            self.child_id = child_id
            self.parent_id = parent_id
            self.m1 = m1
            self.m1_memo = m1_memo
            self.m2 = m2
            self.m2_memo = m2_memo
            self.m3 = m3
            self.m3_memo = m3_memo
            self.reference = reference
    
    def __init__(self):
        """
        Constructs an empty graph for the DT-BASE causal model.
        """
        self.links = dict()
        self.nodes = dict()
        self.adj_list = defaultdict(lambda: [])
    
    def add_node(self, id: str, name: str, keywords: str = None):
        """
        Adds a node to the graph with the given parameters.

        Parameters
        ----------
            id : str
                a unique short id for the node.
            name : str
                the full name of the node.
            keywords : list
                a list of keywords associated with the node
        """
        assert id and len(id) <= 5, 'id must have a length of 5 or fewer characters'
        assert id not in self.nodes and id not in self.links, f'id: {id} already exists. Please choose a unique id.'
        self.nodes[id] = self.node(name, keywords)