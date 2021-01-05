import csv, shutil, tempfile
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
from dtbase.data import DB
from dtbase.model.estimate import Estimate, EstimateTypes
from dtbase.model.link import Link
from dtbase.model.node import Node
from dtbase.model.reference import Reference

class Model:
    '''
    Defines the structure of the DT-BASE causal model.

    Attributes
    ----------
    graph (nx.MultiDiGraph) : a directed acyclic graph representing the causal model.
    db (model.db) : a db object to access and modify the database.
    '''
    def __init__(self, file_path: str=None):
        '''
        Constructs a DTBase model object.

        Parameters
        ----------
        file_path (str) : a file path for the database file.
        '''
        self.graph = nx.MultiDiGraph()
        if not file_path:
            file_path = ':memory'
        self.db = DB(file_path)
        self.build_graph()

    def build_graph(self):
        '''
        Builds a graph from the links and nodes database contents.
        '''
        self.graph.clear()
        for node_id in self.nodes():
            self.graph.add_node(node_id)
        for link_id in self.links():
            link = self.get_link(link_id)
            self.graph.add_edge(link.parent_id, link.child_id, key=link.edge_key, link_id=link.link_id)

    def draw(self) -> None:
        '''
        Draws a visual representation of the graph.
        '''
        nx.draw_spring(self.graph, with_labels=True, node_size=750)

    def add_node(self, node: Node) -> None:
        '''
        Adds a Node to the model.

        Parameters
        ----------
        node (Node) : the node to add to the model.
        '''
        if self.db.get_node(node.node_id):
            raise ValueError(f'[{node.node_id}] already exists in the model.')
        elif not isinstance(node, Node):
            raise TypeError(f'expected [dtbase.node], found [{type(node)}]')
        self.db.add_node(node=node)
        self.graph.add_node(node.node_id)
    
    def add_link(self, link: Link) -> None:
        '''
        Adds a Link between two Nodes to the model.

        Parameters
        ----------
        link (Link) : the Link to add to the model.
        '''
        if self.db.get_link(link.link_id):
            raise ValueError(f'[{link.link_id}] already exists in the model.')
        elif not isinstance(link, Link):
            raise TypeError(f'expected [dtbase.link], found [{type(link)}]')
        elif not self.get_node(link.child_id):
            raise ValueError(f'Node [{link.child_id}] does not exist in the model.')
        elif not self.get_node(link.child_id):
            raise ValueError(f'Node [{link.parent_id}] does not exist in the model.')
        link.edge_key = self.graph.new_edge_key(link.parent_id, link.child_id)
        self.graph.add_edge(link.parent_id, link.child_id, key=link.edge_key, link_id=link.link_id)
        self.db.add_link(link)
    
    def add_reference(self, reference: Reference) -> None:
        '''
        Adds a Reference to the model.

        Parameters
        ----------
        reference (Reference) : the Reference to add to the model.
        '''
        if self.db.get_reference(reference.ref_id):
            print(self.db.get_reference(reference.ref_id))
            raise ValueError(f'[{reference.ref_id}] already exists in the model.')
        elif not isinstance(reference, Reference):
            raise TypeError(f'link expected [dtbase.reference], found [{type(reference)}]')
        self.db.add_reference(reference)

    def get_node(self, node_id: str) -> Node:
        '''
        Returns a Node with a given id from the model if it exists. Otherwise, raises a KeyError.

        Parameters
        ----------
        node_id (str) : the node_id of the Node to retrieve from the model.
        '''
        node = self.db.get_node(node_id)
        if not node:
            raise KeyError(f'Node [{node_id}] does not exist in the model.')
        return node

    def get_link(self, link_id: str) -> Link:
        '''
        Returns a Link with a given id from the model if it exists. Otherwise, raises a KeyError.

        Parameters
        ----------
        link_id (str) : the link_id of the Link to retrieve from the model.
        '''
        link = self.db.get_link(link_id)
        if not link:
            raise KeyError(f'Link [{link_id}] does not exist in the model.')
        return link

    def get_reference(self, ref_id: str) -> Reference:
        '''
        Returns a Reference with a given id from the model if it exists. Otherwise, raises a KeyError.

        Parameters
        ----------
        ref_id (str) : the ref_id of the Reference to retrieve from the model.
        '''
        ref = self.db.get_reference(ref_id)
        if not ref:
            raise KeyError(f'Reference [{ref_id}] does not exist in the model.')
        return ref

    def remove_node(self, node_id: str) -> None:
        '''
        Removes a Node with a given id from the model if it exists. Otherwise, raises a KeyError.

        Parameters
        ----------
        node_id (str) : the node_id of the Node to remove from the model.
        '''
        if self.db.get_node(node_id):
            self.graph.remove_node(node_id)
            self.db.remove_node(node_id)
            return
        raise KeyError(f'Node [{node_id}] does not exist in the model.')

    def remove_link(self, link_id: str) -> None:
        '''
        Removes a Link with a given id from the model if it exists. Otherwise, raises a KeyError.

        Parameters
        ----------
        link_id (str) : the link_id of the Link to remove from the model.
        '''
        link = self.db.get_link(link_id)
        if link:
            self.graph.remove_edge(link.parent_id, link.child_id, link.edge_key)
            self.db.remove_link(link_id)
            return
        raise KeyError(f'Link [{link_id}] does not exist in the model.')

    def remove_reference(self, ref_id: str) -> None:
        '''
        Removes a Reference with a given id from the model if it exists. Otherwise, raises a KeyError.

        Parameters
        ----------
        ref_id (str) : the ref_id of the Reference to remove from the model.
        '''
        if self.db.get_reference(ref_id):
            self.db.remove_reference(ref_id)
            return
        raise KeyError(f'Reference [{ref_id}] does not exist in the model.')

    def nodes(self) -> set:
        '''
        Returns the set of all the node_ids in the model.
        '''
        return self.db.nodes()
    
    def links(self) -> set:
        '''
        Returns the set of all the link_ids in the model.
        '''
        return self.db.links()

    def references(self) -> set:
        '''
        Returns the set of all the ref_ids in the model.
        '''
        return self.db.references()

    def clear(self):
        '''
        Clears the entire model, including all Nodes, Links, and References.
        '''
        self.db.clear()
        self.graph.clear()

    def export_model(self, name: str) -> None:
        '''
        Creates a .zip file with all the model data
        '''
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            self.db.export_data_files(path)
            self.draw()
            plt.savefig(path.joinpath(Path('model.png')))
            shutil.make_archive(name, 'zip', path)

    def import_nodes(self, file_path: str) -> None:
        '''
        Imports a .csv file of nodes.

        Parameters
        ----------
        file_path (str) : a file path that points to a properly formatted .csv file.
        '''
        with open (file_path, 'r') as f:
            reader = csv.reader(f)
            for node in reader:
                self.add_node(Node(*node))

    def import_refs(self, file_path: str) -> None:
        '''
        Imports a .csv file of refs.

        Parameters
        ----------
        file_path (str) : a file path that points to a properly formatted .csv file.
        '''
        with open (file_path, 'r') as f:
            reader = csv.reader(f)
            for node in reader:
                try:
                    self.add_reference(Reference(*node))
                except KeyError:
                    continue

    def import_links(self, file_path: str) -> None:
        '''
        Imports a .csv file of links.

        Parameters
        ----------
        file_path (str) : a file path that points to a properly formatted .csv file.
        '''
        with open (file_path, 'r') as f:
            reader = csv.reader(f)
            for link in reader:
                # read estimates
                i = 3
                m = []
                while i < 12:
                    m.append(Estimate(EstimateTypes(link[i]), float(link[i + 1]), float(link[i + 2])))
                    i += 3
                self.add_link(Link(*link[0:3], *m, *link[12:]))
