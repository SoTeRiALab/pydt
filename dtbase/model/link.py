from .uncertainty import Estimate

class Link:
    '''
    Defines a causal Link (directed edge) between two Nodes in the DT-BASE causal model.

    Attributes
    ----------
    link_id (str) : the unique id for a Link.
    parent_id (str) : the unique id of the parent Node of the Link.
    child_id (str) : the unique id of the child Node of the Link.
    m1 (Estimate) : an Estimate object representing an analyst Estimate for the m1 value.
    m2 (Estimate) : an Estimate object representing an analyst Estimate for the m2 value.
    m3 (Estimate) : an Estimate object representing an analyst Estimate for the m3 value.
    m1_memo (str) : an explanation of the reasoning behind the analyst's estimate of the m1 value.
    m2_memo (str) : an explanation of the reasoning behind the analyst's estimate of the m2 value.
    m3_memo (str) : an explanation of the reasoning behind the analyst's estimate of the m3 value.
    ref_id (str) : the unique id of the Reference which supports the claim of a causal link.
    edge_key (int) : the integer key used internally to handle multiple edges between nodes.
    '''
    def __init__(self, link_id: str, parent_id: str, child_id: str, 
            m1: Estimate, m2: Estimate, m3: Estimate,
            m1_memo: str = None, m2_memo: str = None, m3_memo: str = None,
            ref_id: str = None, edge_key: int=None):
        '''
        Constructs a Link object.
        '''
        if not isinstance(m1, Estimate):
            raise TypeError('m1 must be an Estimate object.')
        if not isinstance(m2, Estimate):
            raise TypeError('m1 must be an Estimate object.')
        if not isinstance(m2, Estimate):
            raise TypeError('m1 must be an Estimate object.')

        self.link_id = link_id
        self.parent_id = parent_id
        self.child_id = child_id
        self.m1 = m1
        self.m1_memo = m1_memo
        self.m2 = m2
        self.m2_memo = m2_memo
        self.m3 = m3
        self.m3_memo = m3_memo
        self.ref_id = ref_id
        self.edge_key = edge_key

    def to_tuple(self) -> tuple:
        '''
        Returns a tuple representation of a Link.
        '''
        return (self.link_id, self.parent_id, self.child_id, 
                *self.m1.to_tuple(), *self.m2.to_tuple(), *self.m3.to_tuple(),
                self.m1_memo, self.m2_memo, self.m3_memo, self.ref_id, self.edge_key)
    
    def __hash__(self) -> int:
        '''
        Returns a hash of a Link based on the parent_id, child_id and edge_key.
        '''
        return hash((self.child_id, self.parent_id, self.edge_key))