from .uncertainty import Estimate

class link:
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

        self.link_id = link_id

    def __dict__(self):
        """
        Returns a dict representation of a link.
        """
        return { 'link_id': self.link_id, 'edge_key': self.edge_key, 'parent_id': self.parent_id, 'child_id': self.child_id, 'm1': self.m1, 
            'm2': self.m2, 'm3': self.m3,
            'm1_memo': self.m1_memo, 'm2_memo': self.m2_memo, 'm3_memo': self.m3_memo,
            'ref_id': self.ref_id }

    def __str__(self):
        """
        Returns a str representation of a link.
        """
        return str(self.__dict__())
    
    def __tuple__(self):
        return (self.link_id, self.parent_id, self.child_id, self.m1, self.m2, self.m3, 
            self.m1_memo, self.m2_memo, self.m3_memo, self.ref_id, self.edge_key,)
    
    def __hash__(self):
        return hash((self.child_id, self.parent_id, self.edge_key))