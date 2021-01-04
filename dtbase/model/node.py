class Node:
    def __init__(self, node_id: str, name: str=None, keywords: str=None):
        self.name = name
        self.keywords = keywords
        self.node_id = node_id

    def to_tuple(self):
        return (self.node_id, self.name, self.keywords)

    def __hash__(self):
        return hash((self.name, self.keywords))