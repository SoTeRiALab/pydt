from collections import defaultdict
import csv
from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx
from reference import ref


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
            a modified adjacency list mapping a node onto all link ids that are
            directed to it.
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
                weight : float
                    The normalized weight of the link
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
            self.weight = 0
    
    def __init__(self):
        """
        Constructs an empty graph for the DT-BASE causal model.
        """
        self.links = dict()
        self.nodes = dict()
        self.adj_list = defaultdict(lambda: [])
    
    def add_node(self, id: str, name: str, keywords: list = None):
        """
        Adds a node to the graph with the given parameters.

        Parameters
        ----------
            id : str
                a unique short id for the node.
            
            other parameters defined in the node class
        """
        assert id and len(id) <= 5, 'id must have a length of 5 or fewer characters'
        assert id not in self.nodes and id not in self.links, f'id: {id} already exists. Please choose a unique id.'
        self.nodes[id] = self.node(name, keywords)

    def add_link(self, id: str, child_id: str, parent_id: str, m1: float, m2: float, m3: float,
            m1_memo: str = None, m2_memo: str = None, m3_memo: str = None,
            reference: ref = None):
        """
        Adds a link from a parent to a child node in the graph with the given parameters.

        Parameters
        ----------
            id : str
                a unique short id for the link
            
            other parameters defined in the link class
        """
        assert id and len(id) <= 5, 'id must have a length of 5 or fewer characters'
        assert id not in self.nodes and id not in self.links, f'id: {id} already exists. Please choose a unique id.'
        assert parent_id in self.nodes, f'{parent_id} does not exist in the graph'
        assert child_id in self.nodes, f'{child_id} does not exist in the graph'
        self.links[id] = self.link(child_id, parent_id, m1, m2, m3, m1_memo, m2_memo, m3_memo, reference)
        self.adj_list[child_id].append(id)
    
    def calc_normalized_weights(self, target_id: str):
        """
        Calculates the normalized weight of each link in the graph and populates the weight field for each link.

        Parameters
        ----------
            target_id : str
                the target child node across which the weights are normalized.
        """
        assert len(self.adj_list[target_id]), 'there are no directed edges to the given target node in the graph'
        # calculate Z, the normalization factor for the weight calculation for each parent node for the
        # given target node.
        Z = { id : 0 for id in self.nodes }
        for link_id in self.adj_list[target_id]:
            link = self.links[link_id]
            Z[link.parent_id] += link.m1 * link.m3

        # calculate the normalized weight of each link
        for link_id in self.adj_list[target_id]:
            link = self.links[link_id]
            link.weight = (link.m1 * link.m3) / Z[link.parent_id]

    def calc_cp_arithmetic(self, target_id: str) -> dict:
        """
        Calculates the aggregated conditional probability for each parent node with an edge to the target node using
        the arithmetic mean.

        Parameters
        ----------
            target_id : str
                the target child node across which the weights are normalized.
        """
        p = { self.links[link].parent_id : 0.0 for link in self.adj_list[target_id] }
        for link in self.adj_list[target_id]:
            p[self.links[link].parent_id] += self.links[link].weight * self.links[link].m2
        return p

    def calc_cp_geometric(self, target_id: str) -> dict:
        """
        Calculates the aggregated conditional probability for each parent node with an edge to the target node using
        the geometric mean.

        Parameters
        ----------
            target_id : str
                the target child node across which the weights are normalized.
        """
        p = { self.links[link].parent_id : 1.0 for link in self.adj_list[target_id] }
        for link in self.adj_list[target_id]:
            p[self.links[link].parent_id] *=  (self.links[link].m2 ** self.links[link].weight)
        return p

    def calc_noisy_or(self, target_id: str, parent_ids: tuple, p_table: dict):
        """
        Calculates the noisy or approximation for P(target | p1, p2, ... for all p in parent_ids).
        
        Parameters
        ----------
            target_id : str
                the id of the target child node.
            parent_ids : tuple
                a tuple of all parent nodes in a single combination.
            p_table : dict
                stores P(target | p) where p is a single parent node. Calculated with calc_cp_geometric
                or calc_cp_arithmetic.
        """
        prod = 1
        for parent_id in parent_ids:
            prod *= 1 - p_table[parent_id]
        return 1 - prod

    def calc_cpt(self, target_id: str, arithmetic: bool = True) -> dict:
        """
        Calculates the conditional probability table for a target node,

        Parameters
        ----------
            target_id : str
                the id of the target node.
            arithmetic : bool
                True if using the arithmetic mean, False if using the geometric mean.
        """
        cpt = dict()
        table = self.calc_cp_arithmetic(target_id) if arithmetic else self.calc_cp_geometric(target_id)
        for i in range(1, len(self.adj_list[target_id]) + 1):
            for combo in combinations(self.adj_list[target_id], i):
                c = tuple(self.links[link].parent_id for link in combo)
                cpt[c] = self.calc_noisy_or(target_id, c, table)
        return cpt

    def export_graph(self, file_path: str):
        """
        Exports a visualization of the graph as an image file.
        
        Parameters
        ----------
            file_path : str
                the intended file path to save the image.
        """
        G = nx.DiGraph()
        for link in self.links.values():
            G.add_edge(link.parent_id, link.child_id)
        nx.draw(G, with_labels=True, font_weight='bold')
        plt.savefig(file_path)
    
    def export_data(self, file_path: str):
        """
        Exports the model data to a CSV file.
        
        Parameters
        ----------
            file_path : str
                the intended file path to save the model.
        """
        assert file_path.endswith('.csv'), 'A valid .csv file path must be entered'
        with open(file_path, 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='\'')
            # Spreadsheet headings
            writer.writerow(['Link ID', 'Child ID', 'Child Name', 'Child Keywords',
                'Parent ID', 'Parent Name', 'Parent Keywords'
                'Title', 'Authors', 'Year', 'Type', 'Publisher',
                'M1', 'M1 Memo', 'M2', 'M2 Memo', 'M3', 'M3 Memo'])
            for id, link in self.links.items():
                writer.writerow([id, link.child_id, self.nodes[link.child_id].name, 
                    self.nodes[link.child_id].keywords, link.parent_id, self.nodes[link.parent_id].name, 
                    self.nodes[link.parent_id].keywords, 
                    link.reference.title if link.reference else None, 
                    link.reference.year if link.reference else None,
                    link.reference.type if link.reference else None,
                    link.reference.publisher if link.reference else None,
                    link.m1, link.m1_memo, 
                    link.m2, link.m2_memo, link.m3, link.m3_memo])
