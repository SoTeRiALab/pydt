class node:
    def __init__(self, node_id: str, name: str=None, keywords: str=None):
        self.name = name
        self.keywords = keywords
        self.node_id = node_id

    def __dict__(self):
        return { 'node_id': self.node_id, 'name' : self.name, 'keywords' : self.keywords }
    
    def __str__(self):
        """
        Returns a str representation of a node.
        """
        return str(self.__dict__())

    def __tuple__(self):
        return (self.node_id, self.name, self.keywords)

    def __hash__(self):
        return hash((self.name, self.keywords))