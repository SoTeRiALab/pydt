import csv
from pathlib import Path
import shutil
import sqlite3
import tempfile
from dtbase.model.estimate import Estimate, EstimateTypes
from dtbase.model.link import Link
from dtbase.model.node import Node
from dtbase.model.reference import Reference

class DB:
    '''
    Handles database operations for the model.

    Attributes
    ----------
    file_path (str) : the file path to write the database to.
    con (sqlite3.Connection) : sqlite3 Connection object to connect to the database.
    cursor (sqlite3.Cursor) : sqlite3 Curor object to manipulate the database.
    '''
    def __init__(self, file_path: str):
        '''
        Constructs a db instance and connects to the database in memory.

        Parameters
        ----------
        file_path (str) : the file path to write the db file to.
        '''
        self.file_path = Path(file_path)
        self.con = sqlite3.connect(self.file_path)
        self.cursor = self.con.cursor()
        self.create_tables()

    def create_tables(self) -> None:
        '''
        Creates the nodes, sources, and links database tables if they have not
        yet been created.
        '''
        self.cursor.execute('''create table if not exists nodes(
                                    node_id text primary key,
                                    name text, 
                                    keywords text)''')
        self.cursor.execute('''create table if not exists sources(
                                    ref_id text primary key, 
                                    title text not null, 
                                    authors text, 
                                    year text,
                                    publication_type text, 
                                    publisher text)''')
        self.cursor.execute('''create table if not exists links(
                                    link_id text primary key,
                                    parent_id text not null, 
                                    child_id text not null,
                                    m1_type text not null,
                                    m1_a real not null,
                                    m1_b real not null,
                                    m2_type text not null,
                                    m2_a real not null,
                                    m2_b real not null,
                                    m3_type text not null,
                                    m3_a real not null,
                                    m3_b real not null,
                                    m1_memo text,
                                    m2_memo text, 
                                    m3_memo text, 
                                    ref_id text,
                                    edge_key integer not null,
                                    foreign key(parent_id) references nodes(node_id),
                                    foreign key(child_id) references nodes(node_id),
                                    foreign key(ref_id) references sources(ref_id),
                                    unique(link_id),
                                    unique(parent_id, child_id, edge_key))''')
        self.con.commit()
            
    def __del__(self):
        '''
        Closes the database connection on deletion of the object.
        '''
        self.con.close()

    def add_node(self, node: Node) -> None:
        '''
        Adds a node to the database.

        Parameters
        ----------
        node (Node) : a Node object to be added to the database.
        '''
        self.cursor.execute('insert into nodes values (?, ?, ?)', 
            node.to_tuple())
        self.con.commit()

    def remove_node(self, node_id: str) -> None:
        '''
        Removes a Node with a given id and all adjacent Links from the database.

        Parameters
        ----------
        node_id (str) : the id of the Node to remove.
        '''
        self.cursor.execute('delete from nodes where node_id = ?', (node_id,))
        self.cursor.execute('delete from links where child_id = ? or parent_id = ?', 
            (node_id, node_id))
        self.con.commit()

    def get_node(self, node_id: str) -> Node:
        '''
        Returns the Node object with the given node_id from the database.

        Parameters
        ----------
        node_id (str) : the id of the Node to retrieve.
        '''
        node_tup = self.cursor.execute('select * from nodes where node_id = ?', 
            (node_id,)).fetchone()
        if not node_tup:
            return None
        return Node(*node_tup)

    def add_link(self, link: Link) -> None:
        '''
        Adds a Link between two Nodes to the database.

        Parameters
        ----------
        link (Link) : the Link object to add to the database.
        '''
        self.cursor.execute('')
        self.cursor.execute('insert into links values (?, ?, ?, ?,\
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', link.to_tuple())
        self.con.commit()

    def remove_link(self, link_id: str) -> None:
        '''
        Removes a link with the given link_id from the database.

        Parameters
        ----------
        link_id (str) : removes the link with id link_id from the database.
        '''
        self.cursor.execute('delete from links where link_id = ?', (link_id,))
        self.con.commit()

    def get_link(self, link_id: str) -> Link:
        '''
        Returns the Link object with the given link_id from the database.

        Parameters
        ----------
        link_id (str) : the id of the Link to retrieve.
        '''
        link_tup = self.cursor.execute('select * from links where link_id = ?', 
            (link_id,)).fetchone()
        if not link_tup:
            return None
        m1 = Estimate(EstimateTypes(link_tup[3]), link_tup[4], link_tup[5])
        m2 = Estimate(EstimateTypes(link_tup[6]), link_tup[7], link_tup[8])
        m3 = Estimate(EstimateTypes(link_tup[9]), link_tup[10], link_tup[11])
        return Link(*link_tup[0:3], m1, m2, m3, *link_tup[12:])

    def add_reference(self, reference: Reference) -> None:
        '''
        Adds a Reference to the database.

        Parameters
        ----------
        reference (Reference) : the Reference to add to the database.
        '''
        self.cursor.execute('insert into sources values(?, ?, ?, ?, ?, ?)', 
            reference.to_tuple())
        self.con.commit()

    def remove_reference(self, ref_id: str) -> None:
        '''
        Removes a Reference with the given ref_id from the database.

        Parameters
        ----------
        ref_id (str) : the ref_id of the Reference to remove from the database.
        '''
        self.cursor.execute('delete from sources where ref_id = ?', (ref_id,))
        self.cursor.execute('delete from links where ref_id = ?', (ref_id,))
        self.con.commit()

    def get_reference(self, ref_id: str) -> Reference:
        '''
        Returns the Reference with the given ref_id from the database.

        Parameters
        ----------
        reference (Reference) : the ref_id of the Reference to retrieve from the database.
        '''
        ref_tup = self.cursor.execute('select * from sources where ref_id = ?', 
            (ref_id,)).fetchone()
        if not ref_tup:
            return None
        return Reference(*ref_tup)

    def nodes(self) -> set:
        '''
        Returns the set of all node_ids in the database.
        '''
        return { tup[0] for tup in self.cursor.execute('select node_id from nodes').fetchall() }

    def links(self) -> set:
        '''
        Returns the set of all link_ids in the database.
        '''
        return { tup[0] for tup in self.cursor.execute('select link_id from links').fetchall() }
  
    def references(self) -> set:
        '''
        Returns the set of all ref_ids in the database.
        '''
        return { tup[0] for tup in self.cursor.execute('select ref_id from sources').fetchall() }

    def export_data_files(self, tmp_path: Path):
        '''
        Writes the model data files to .csv files in the tmp_path folder.
        '''
        with open(tmp_path.joinpath('nodes.csv'), 'w') as f:
            writer = csv.writer(f)
            nodes = self.cursor.execute('select * from nodes').fetchall()
            for node in nodes:
                writer.writerow(node)
        with open(tmp_path.joinpath('links.csv'), 'w') as f:
            writer = csv.writer(f)
            links = self.cursor.execute('select * from links').fetchall()
            for link in links:
                writer.writerow(link)
        with open(tmp_path.joinpath('references.csv'), 'w') as f:
            writer = csv.writer(f)
            refs = self.cursor.execute('select * from sources').fetchall()
            for ref in refs:
                writer.writerow(ref)
        shutil.copyfile(self.file_path, tmp_path.joinpath(self.file_path.name))

    def clear(self):
        '''
        Clears the database of all Nodes, Links and References.
        '''
        self.cursor.execute('drop table if exists nodes')
        self.cursor.execute('drop table if exists links')
        self.cursor.execute('drop table if exists sources')
        self.create_tables()