from collections import defaultdict
from itertools import combinations
from pandas import DataFrame

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
                the name of the node
            keywords : str
                a list of keywords associated with this node.
        """
        self.name = name
        self.id = id
        self.keywords = keywords