from .uncertainty import Estimate

class Link:
    def __init__(self, link_id: str, parent_id: str, child_id: str, 
            m1: Estimate, m2: Estimate, m3: Estimate,
            m1_memo: str = None, m2_memo: str = None, m3_memo: str = None,
            ref_id: str = None, edge_key=None):
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

    def to_tuple(self):
        """
        Returns a tuple representation of a Link.
        """
        return (self.link_id, self.parent_id, self.child_id, 
                *self.m1.to_tuple(), *self.m2.to_tuple(), *self.m3.to_tuple(),
                self.m1_memo, self.m2_memo, self.m3_memo, self.ref_id, self.edge_key)
    
    def __hash__(self):
        return hash((self.child_id, self.parent_id, self.edge_key))