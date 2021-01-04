class Reference:
    """
    Object representing a Reference in the DT-BASE model.
    """
    def __init__(self, ref_id:str, title: str, year: str = None, authors: list = None,
        publication_type: str = None, publisher: str = None):
        """
        Constructs a ref object representing a single reference for a causal link.

        Parameters
        ----------
            title : str 
                the title of the paper/article.
            year : str
                the year the publication was written in.
            authors : str
                a str with all the author names.
            publication_type : str
                the type of publication. Must be a valid .ris "TY" tag value.
            publisher : str 
                the name of the publisher.
        """
        assert title, 'A valid title must be provided'
        self.title = title
        self.year = year
        self.authors = authors
        self.publication_type = publication_type
        self.publisher = publisher
    
    def to_tuple(self):
        return (self.title, self.year, self.authors, self.publication_type, self.publisher)

    def __hash__(self):
        return hash((self.title, self.authors))