from collections import defaultdict
import csv
from enum import Enum
from itertools import combinations
import numpy as np
from .dtbase import DTBase

# default sample size for the Monte Carlo method
sample_size = int(1e5)

class AggregationMethod(Enum):
    '''
    Stores the possible Aggregation Methods.
    '''
    ARITHMETIC=0,
    GEOMETRIC=1

def calculate(model: DTBase, target_node: str, ag_method: AggregationMethod) -> defaultdict:
    '''
    Returns a defaultdict representing the conditional probability table for a target_node.
    Each key in the defaultdict is a tuple of parent nodes.
    Each value is P(target_node | parents).

    Parameters
    ----------
    model (DTBase) : the DTBase model to quantify
    target_node(str) : the node_id of the target node.
    ag_method (AggregationMethod) : the enum value representing the type of AggregationMethod to use.
    '''
    if ag_method == AggregationMethod.ARITHMETIC:
        aggregated_cp = calc_cp_arithmetic(model, target_node, calc_normalized_weights(model, target_node))
    elif ag_method == AggregationMethod.GEOMETRIC:
        aggregated_cp = calc_cp_geometric(model, target_node, calc_normalized_weights(model, target_node))

    cpt = defaultdict(lambda: np.zeros(sample_size))
    pred = set(model.graph.predecessors(target_node))
    for i in range(1, len(pred) + 1):
        for combo in combinations(pred, i):
            c = calc_noisy_or(aggregated_cp, combo)
            cpt[combo] = (np.mean(c), np.std(c))
    return cpt

def calc_normalized_weights(model: DTBase, target_node: str) -> defaultdict:
    '''
    Returns a defaultdict with the normalized weights for each link pointing to the target node.
    The result is a map of link_id -> weight.

    Parameters
    ----------
    model (DTBase) : the DTBase model to quantify.
    target_node(str) : the node_id of the target node.
    '''
    links = set()
    Z = { node_id : np.zeros(sample_size) for node_id in model.graph.predecessors(target_node) }
    for parent_id in Z:    
        for edge in model.graph.get_edge_data(parent_id, target_node).values():
            link = model.get_link(edge['link_id'])
            Z[parent_id] += link.m1.sample * link.m3.sample
            links.add(link)
    weights = defaultdict(lambda: np.zeros(sample_size))
    for link_id in model.links():
        link = model.get_link(link_id)
        weights[link_id] = (link.m1.sample * link.m3.sample) / Z[link.parent_id]
    return weights

def calc_cp_arithmetic(model: DTBase, target_node: str, normalized_weights: defaultdict) -> defaultdict:
    '''
    Returns a defaultdict with the aggregated weight using arithmetic mean of a link between two nodes.
    The result is a map of parent node_id -> weight.

    Parameters
    ----------
    model (DTBase) : the DTBase model to quantify.
    target_node(str) : the node_id of the target node.
    normalized_weights (defaultdict) : the normalized weights calculated using calc_normalized_weights.
    '''
    cp = defaultdict(lambda: np.zeros(sample_size))
    for parent_id in model.graph.predecessors(target_node):         
        for edge in model.graph.get_edge_data(parent_id, target_node).values():
            link = model.get_link(edge['link_id'])
            cp[parent_id] += normalized_weights[link.link_id] * link.m2.sample
    return cp

def calc_cp_geometric(model: DTBase, target_node: str, normalized_weights: defaultdict) -> defaultdict:
    '''
    Returns a defaultdict with the aggregated weight using geometric mean of a link between two nodes.
    The result is a map of parent node_id -> weight.

    Parameters
    ----------
    model (DTBase) : the DTBase model to quantify.
    target_node(str) : the node_id of the target node.
    normalized_weights (defaultdict) : the normalized weights calculated using calc_normalized_weights.
    '''
    cp = defaultdict(lambda: np.zeros(sample_size))
    for parent_id in model.graph.predecessors(target_node):         
        for edge in model.graph.get_edge_data(parent_id, target_node).values():
            link = model.get_link(edge['link_id'])
            cp[parent_id] *= link.m2.sample ** normalized_weights[link.link_id]
    return cp

def calc_noisy_or(aggregated_cp: defaultdict, parent_ids: tuple) -> np.array:
    '''
    Returns the noisy or approximating for P(target_node | parents).

    Parameters
    ----------
    aggregated_cp (DTBase) : the aggregated conditional probability map calculated using one of the aggregation methods.
    parent_ids (tuple) : a tuple of all the parents in a given combination.
    '''
    prod = np.ones(sample_size)
    for parent_id in parent_ids:
        prod *= np.ones(sample_size) - aggregated_cp[parent_id]
    return 1 - prod

def export_cpt( output: defaultdict, file_path: str):
    '''
    Exports the cpt to a csv file.
    '''
    with open(file_path, 'w') as f:
        writer = csv.writer(file_path)
        for combo, val in output:
            writer.writerow(combo, *val)