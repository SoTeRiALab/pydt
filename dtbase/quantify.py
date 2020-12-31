from .dtbase import dtbasemodel
from itertools import combinations
from pandas import DataFrame
from enum import Enum

class AggregationMethod(Enum):
    ARITHMETIC=0,
    GEOMETRIC=1

class Quantify:
    def __init__(self, model: dtbasemodel, target_node: str):
        self.model = model
        self.target_node = target_node
        if not self.model.graph.has_node(target_node):
            raise ValueError(f'Node [{target_node}] does not exist in the model.')
        self.predecessors = set(self.model.graph.predecessors(self.target_node))
        self.normalized_link_weights = None
        self.aggregated_cp = None
        self.cpt = None
        self.quant = False

    def calculate(self, ag_method: AggregationMethod):
        self.normalized_link_weights = self.normalize_weights()
        if ag_method == AggregationMethod.ARITHMETIC:
            self.aggregated_cp = self.calc_cp_arithmetic()
        elif ag_method == AggregationMethod.GEOMETRIC:
            self.aggregated_cp = self.calc_cp_geometric()
        self.cpt = self.calc_cpt()
        self.quant = True

    def normalize_weights(self) -> DataFrame:
        links = set()
        Z = { node_id : 0 for node_id in self.predecessors }
        for parent_id in Z:    
            for edge in self.model.graph.get_edge_data(parent_id, self.target_node).values():
                link = self.model.get_link(edge['link_id'])
                Z[parent_id] += link.m1 * link.m3
                links.add(link)
        weights = DataFrame(index=[link.link_id for link in links], columns=['edge_key', 'parent_id', 'child_id', 'weight'])
        for link_id in weights.index:
            link = self.model.get_link(link_id)
            weights.loc[link_id, 'edge_key'] = link.edge_key
            weights.loc[link_id, 'parent_id'] = link.parent_id
            weights.loc[link_id, 'child_id'] = link.child_id
            weights.loc[link_id, 'weight'] = (link.m1 * link.m3) / Z[link.parent_id]
        return weights

    def calc_cp_arithmetic(self) -> DataFrame:
        cp = DataFrame([0.0] * len(self.predecessors), index=[link_id for link_id in self.predecessors], 
            columns=['conditional_probability'])
        for parent_id in cp.index:         
            for edge in self.model.graph.get_edge_data(parent_id, self.target_node).values():
                link = self.model.get_link(edge['link_id'])
                cp.loc[parent_id, 'conditional_probability'] += self.normalized_link_weights.loc[link.link_id, 
                    'weight'] * link.m2
        return cp

    def calc_cp_geometric(self) -> DataFrame:
        cp = DataFrame([1.0] * len(self.predecessors), index=[link_id for link_id in self.predecessors], 
            columns=['conditional_probability'])
        for parent_id in cp.index:         
            for edge in self.model.graph.get_edge_data(parent_id, self.target_node).values():
                link = self.model.get_link(edge['link_id'])
                cp.loc[parent_id, 'conditional_probability'] *= link.m2 ** l
        return cp

    def calc_noisy_or(self, parent_ids: tuple) -> float:
        prod = 1
        for parent_id in parent_ids:
            prod *= 1 - self.aggregated_cp.loc[parent_id, 'conditional_probability']
        return 1 - prod

    def calc_cpt(self):
        cpt = {}
        for i in range(1, len(self.predecessors) + 1):
            for combo in combinations(self.predecessors, i):
                cpt[combo] = self.calc_noisy_or(combo)
        return DataFrame(cpt.values(), index=[tuple(key) for key in cpt], columns=['conditional_probability'])

    def export_results(self, file_path: str):
        if not self.quant:
            raise RuntimeError('run calculate() before exporting the results.')
        self.cpt.to_csv(file_path)