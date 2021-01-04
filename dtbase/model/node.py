class Node:
    '''
    Represents a Node in the DT-BASE causal model.

    Attributes
    ----------
    node_id (str) : a unique id for the Node.
    name (str) : the name of the Node.
    keywords (str) : a string of space separated keywords to tag a Node.
    '''
    def __init__(self, node_id: str, name: str=None, keywords: str=None):
        '''
        Constructs a Node object.
        '''
        self.name = name
        self.keywords = keywords
        self.node_id = node_id

    def to_tuple(self) -> tuple:
        '''
        Returns a tuple representation of a Node.
        '''
        return (self.node_id, self.name, self.keywords)

    def __hash__(self) -> int:
        '''
        Returns a hash of a Node based on its name and keywords.
        '''
        return hash((self.name, self.keywords))