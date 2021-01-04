import csv
import dtbase.model as model
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import tempfile
import shutil

class dtbasemodel:
    def __init__(self, file_path: str):
        self.graph = nx.MultiDiGraph()
        self.db = model.db(file_path)
        self.build_graph()

    def build_graph(self):
        self.graph.clear()
        for node_id in self.nodes():
            self.graph.add_node(node_id)
        for link_id in self.links():
            link = self.get_link(link_id)
            self.graph.add_edge(link.parent_id, link.child_id, key=link.edge_key, link_id=link.link_id)

    def draw(self, file_path: str) -> None:
        nx.draw_spring(self.graph, with_labels=True, node_size=750)
        plt.savefig(file_path)

    def add_node(self, node: model.node) -> None:
        if self.db.get_node(node.node_id):
            raise ValueError(f'[{node.node_id}] already exists in the model.')
        elif not isinstance(node, model.node):
            raise TypeError(f'expected [dtbase.node], found [{type(node)}]')
        self.db.add_node(node=node)
        self.graph.add_node(node.node_id)
    
    def add_link(self, link: model.link) -> None:
        if self.db.get_link(link.link_id):
            raise ValueError(f'[{link.link_id}] already exists in the model.')
        elif not isinstance(link, model.link):
            raise TypeError(f'expected [dtbase.link], found [{type(link)}]')
        elif not self.get_node(link.child_id):
            raise ValueError(f'Node [{link.child_id}] does not exist in the model.')
        elif not self.get_node(link.child_id):
            raise ValueError(f'Node [{link.parent_id}] does not exist in the model.')
        link.edge_key = self.graph.new_edge_key(link.parent_id, link.child_id)
        self.graph.add_edge(link.parent_id, link.child_id, key=link.edge_key, link_id=link.link_id)
        self.db.add_link(link)
    
    def add_reference(self, reference: model.reference) -> None:
        if self.db.get_reference(reference.ref_id):
            raise ValueError(f'[{reference.ref_id}] already exists in the model..')
        elif not isinstance(reference, model.reference):
            raise TypeError(f'link expected [dtbase.reference], found [{type(reference)}]')
        self.db.add_reference(reference)

    def get_node(self, node_id: str) -> model.node:
        node = self.db.get_node(node_id)
        if not node:
            raise KeyError(f'Node [{node_id}] does not exist in the model.')
        return node

    def get_link(self, link_id: str) -> model.link:
        link = self.db.get_link(link_id)
        if not link:
            raise KeyError(f'Link [{link_id}] does not exist in the model.')
        return link

    def get_reference(self, ref_id: str) -> model.reference:
        ref = self.db.get_reference(ref_id)
        if not ref:
            raise KeyError(f'Reference [{ref_id}] does not exist in the model.')
        return ref

    def remove_node(self, node_id: str) -> None:
        if self.db.get_node(node_id):
            self.graph.remove_node(node_id)
            self.db.remove_node(node_id)
            return
        raise KeyError(f'Node [{node_id}] does not exist in the model.')

    def remove_link(self, link_id: str) -> None:
        link = self.db.get_link(link_id)
        if link:
            self.graph.remove_edge(link.parent_id, link.child_id, link.edge_key)
            self.db.remove_link(link_id)
            return
        raise KeyError(f'Link [{link_id}] does not exist in the model.')

    def remove_reference(self, ref_id: str) -> None:
        if self.db.get_reference(ref_id):
            self.db.remove_reference(ref_id)
            return
        raise KeyError(f'Reference [{ref_id}] does not exist in the model..')

    def nodes(self) -> list:
        return self.db.nodes()
    
    def links(self) -> list:
        return self.db.links()

    def references(self) -> list:
        return self.db.references()

    def clear(self):
        self.db.clear()
        self.graph.clear()

    def export_model(self, file_path: str) -> None:
        if not file_path.endswith('.tar.gz') and not file_path.endswith('.zip'):
            raise ValueError('The provided file path must be a valid zip, \
                tar, gztar, bztar, or xztar file')
        tmp_path = Path(tempfile.mkdtemp())
        self.db.export_data_files(tmp_path)
        self.draw(tmp_path.joinpath('model.png'))
        shutil.make_archive(tmp_path, 'zip', file_path, 'root')