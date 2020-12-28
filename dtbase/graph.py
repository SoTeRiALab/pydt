from collections import defaultdict
import csv
from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx
from dtbase.reference.ref import ref

class model:
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
        
        def __dict__(self):
            """
            Returns a dict representation of a node.
            """
            return { 'name' : self.name, 'keywords' : self.keywords }
        
        def __str__(self):
            """
            Returns a str representation of a node.
            """
            return str(self.__dict__())

        def __hash__(self):
            return hash((self.name, self.keywords))

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
        
        def __dict__(self):
            """
            Returns a dict representation of a link.
            """
            out = ({ 'child_id': self.child_id, 'parent_id': self.parent_id, 'm1': self.m1, 
                'm2': self.m2, 'm3': self.m3,
                'm1_memo': self.m1_memo, 'm2_memo': self.m2_memo, 'm3_memo': self.m3_memo })
            out.update({ dict(self.reference) })
            return out
    
        def __str__(self):
            """
            Returns a str representation of a link.
            """
            return str(self.__dict__())
        
        def __hash__(self):
            return hash((self.child_id, self.parent_id, self.reference))
    
    def __init__(self):
        """
        Constructs an empty graph for the DT-BASE causal model.
        """
        self.graph = nx.MultiDiGraph()
        self.link_ids = set()
    
    def add_node(self, id: str, name: str, keywords: list = None):
        """
        Adds a node to the graph with the given parameters.

        Parameters
        ----------
            id : str
                a unique short id for the node.
            
            other parameters defined in the node class
        """
        if self.graph.has_node(id):
            raise ValueError(f'Node [{id}] already exists. Please choose a unique id.')
        self.graph.add_node(id, node=self.node(name, keywords))

    def get_node(self, id: str) -> node:
        """
        Returns the node with the given id.
        """
        if self.graph.has_node(id):
            return self.graph.nodes[id]
        raise KeyError(f'Node [{id}] was not found.')

    def remove_node(self, id: str) -> None:
        """
        Removes the node and all assoicated links with the given id.

        Parameters
        ----------
            id : str
                a unique short id for the node.
        """
        self.graph.remove_node(id)


    def add_link(self, link_id: str, child_id: str, parent_id: str, m1: float, m2: float, m3: float,
            m1_memo: str = None, m2_memo: str = None, m3_memo: str = None,
            reference: ref = None) -> None:
        """
        Adds a link from a parent to a child node in the graph with the given parameters.

        Parameters
        ----------
            id : str
                a unique short id for the link
            
            other parameters defined in the link class
        """
        if self.graph.has_node(id) or link_id in self.link_ids:
            raise ValueError(f'[{id}] already exists in the model. Please use a unique id.')
        if not self.graph.has_node(child_id):
            raise ValueError(f'Node [{child_id}] does not exist in the model.')
        if not self.graph.has_node(parent_id):
            raise ValueError(f'Node [{parent_id}] does not exist in the model.')
        self.graph.add_edge(parent_id, child_id, link_id=link_id,
            link=self.link(child_id, parent_id, m1, m2, m3, m1_memo, m2_memo, m3_memo, reference))
        self.link_ids.add(link_id)

    def _find_link_helper(self, link_id: str) -> tuple:
        for edge in self.graph.edges:
            for key, link in self.graph.get_edge_data(edge[0], edge[1]).items():
                if link['link_id'] == link_id:
                    return key, link['link']
        return None

    def get_link(self, link_id: str) -> link:
        if link_id not in self.link_ids:
            raise KeyError(f'Link [{link_id}] does not exist in the model.')
        return self._find_link_helper(link_id)[1]

    def remove_link(self, link_id: str) -> None:
        """
        Removes a link with the given id from the model..

        Parameters
        ----------
            id : str
                a unique short id for the link.
        """
        if link_id not in self.link_ids:
            raise KeyError(f'Link [{link_id}] does not exist in the model.')
        key, link = self._find_link_helper(link_id)
        self.graph.remove_edge(link.parent_id, link.child_id, key)
        self.link_ids.remove(link_id)

    def nodes(self) -> list:
        return self.graph.nodes

    def links(self) -> list:
        return list(self.link_ids)
    
    
    '''def calc_normalized_weights(self, target_id: str):
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
        return cpt '''

    def draw(self, file_path: str):
        """
        Exports a visualization of the graph as an image file.
        
        Parameters
        ----------
            file_path : str
                the intended file path to save the image.
        """
        nx.draw_spring(self.graph, with_labels=True, node_size=500)
        plt.savefig(file_path)
    
    def export_data(self, file_path: str):
        """
        Exports the model data to a CSV file.
        
        Parameters
        ----------
            file_path : str
                the intended file path to save the model.
        """
        assert file_path.endswith('.csv'), 'A valid .csv file path must be provided'
        with open(file_path, 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='\'', quoting=csv.QUOTE_NONNUMERIC)
            # Spreadsheet headings
            writer.writerow(['Link ID', 'Child ID', 'Child Name', 'Child Keywords',
                'Parent ID', 'Parent Name', 'Parent Keywords',
                'Title', 'Authors', 'Year', 'Type', 'Publisher',
                'M1', 'M1 Memo', 'M2', 'M2 Memo', 'M3', 'M3 Memo'])
            """ for edge in self.graph.edges:
                writer.writerow([id, edge.link.child_id, self.nodes[edge.link.child_id].name, 
                    self.nodes[edge.link.child_id].keywords, link.parent_id, self.nodes[link.parent_id].name, 
                    self.nodes[link.parent_id].keywords, 
                    link.reference.title if link.reference else None, 
                    link.reference.year if link.reference else None,
                    link.reference.type if link.reference else None,
                    link.reference.publisher if link.reference else None,
                    link.m1, link.m1_memo, 
                    link.m2, link.m2_memo, link.m3, link.m3_memo]) """

    def import_data(self, file_path: str):
        """
        Imports the model data from a CSV file.
        
        Parameters
        ----------
            file_path : str
                the intended file path to save the model.
        """
        assert file_path.endswith('.csv'), 'A valid .csv file path must be provided'
        # Clear all data
        self.graph.clear()
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            # Spreadsheet headings
            next(reader)
            for row in reader:
                child_id = row[1]
                parent_id = row[4]
                if not self.graph.has_node(child_id):
                    self.add_node(child_id, row[2], row[3])
                if not self.graph.has_node(parent_id):
                    self.add_node(parent_id, row[5], row[6])
                self.add_link(row[0], row[1], row[4], float(row[12]), float(row[14]), float(row[16]),
                    row[13], row[15], row[17])
                

    '''def export_cpt(self, file_path: str, target_id: str, arithmetic: bool = True):
        """
        Calculates and exports  the conditional probability table to a CSV file.
        
        Parameters
        ----------
            file_path : str
                the intended file path to save the model.
            target_id : str
                the id of the target node.
            arithmetic : bool
                True if using the arithmetic mean, False if using the geometric mean.
        """
        assert file_path.endswith('.csv'), 'A valid .csv file path must be provided'
        self.calc_normalized_weights(target_id)
        d = self.calc_cpt(target_id) if arithmetic else self.calc_cpt(target_id)

        with open(file_path, 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='\'', quoting=csv.QUOTE_NONNUMERIC)
            # Spreadsheet headings
            writer.writerow(['Parents', 'Child'])
            for parents, p in d.items():
                writer.writerow([str(parents), target_id, p])'''