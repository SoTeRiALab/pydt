from dtbase.reference.ref import ref
from RISparser import readris

class ris:
    """
    Parses ris files into ref objects:
    """
    def __init__(self, file_path: str):
        """
        Constructs the necessary attributes of a risparser.

        Parameters
        ----------
            file_path : str
                the file path of the .RIS file.
        """
        self.file_path = file_path
        self.refs = self.parse()

    def __iter__(self):
        return iter(self.refs)
    
    def parse(self) -> list:
        """
        Parses a .RIS file into a list of ref objects, one for each entry.

        Returns
        -------
            a list of ref objects
        """
        out = []
        with open (self.file_path, 'r') as ris:
            entries = readris(ris)
            for entry in entries:
                type_ = entry['type_of_reference'] if 'type_of_reference' in entry else None
                title_ = entry['title'] if 'title' in entry \
                    else entry['primary_title'] if 'primary_title' in entry \
                    else None
                authors_= entry['authors'] if 'authors' in entry \
                    else entry['first_authors'] if 'first_authors' in entry \
                    else None
                publisher_ = entry['publisher'] if 'publisher' in entry \
                    else entry['journal_name'] if 'journal_name' in entry \
                    else entry['original_publication'] if 'original_publication' in entry \
                    else None
                year_ = entry['year'] if 'year' in entry \
                    else entry['publication_year'] if 'publication_year' in entry \
                    else None
                out.append(ref(title_, year_ , authors_, type_, publisher_))
        return out