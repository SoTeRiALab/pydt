import csv
from pathlib import Path
from .reference import reference
from .node import node
from .link import link
from .reference import reference
import sqlite3
import shutil
import tempfile

class db:
    def __init__(self, file_path: str):
        self.con = sqlite3.connect(file_path)
        self.cursor = self.con.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''create table if not exists nodes(
                                    node_id text primary key,
                                    name text not null, 
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
                                    m1 real not null,
                                    m2 real not null,
                                    m3 real not null,
                                    m1_memo text,
                                    m2_memo text, 
                                    m3_memo text, 
                                    ref_id text,
                                    edge_key integer not null,
                                    foreign key(parent_id) references nodes(node_id),
                                    foreign key(child_id) references nodes(node_id),
                                    foreign key(ref_id) references sources(ref_id),
                                    unique(link_id),
                                    unique(link_id, edge_key),
                                    unique(parent_id, child_id))''')
        self.con.commit()
            
    def __del__(self):
        self.con.close()

    def add_node(self, node: node):
        self.cursor.execute('insert into nodes values (?, ?, ?)', 
            node.__tuple__())
        self.con.commit()

    def remove_node(self, node_id: str):
        self.cursor.execute('delete from nodes where node_id = ?', (node_id,))
        self.cursor.execute('delete from links where child_id = ? or parent_id = ?', 
            (node_id, node_id))
        self.con.commit()

    def get_node(self, node_id: str):
        node_tup = self.cursor.execute('select * from nodes where node_id = ?', 
            (node_id,)).fetchone()
        if not node_tup:
            return None
        return node(*node_tup)

    def add_link(self, link: link):
        self.cursor.execute('insert into links values (?, ?, ?, ?,\
            ?, ?, ?, ?, ?, ?, ?)', link.__tuple__())
        self.con.commit()

    def remove_link(self, link_id: str):
        self.cursor.execute('delete from links where link_id = ?', (link_id,))
        self.con.commit()

    def get_link(self, link_id: str):
        link_tup = self.cursor.execute('select * from links where link_id = ?', 
            (link_id,)).fetchone()
        if not link_tup:
            return None
        return link(*link_tup)

    def add_reference(self, reference: reference):
        self.cursor.execute('insert into sources values(?, ?, ?, ?, ?, ?)', 
            reference.__tuple__())
        self.con.commit()

    def remove_reference(self, ref_id: str):
        self.cursor.execute('delete from sources where ref_id = ?', (ref_id,))
        self.cursor.execute('delete from links where ref_id = ?', (ref_id,))
        self.con.commit()

    def get_reference(self, ref_id: str):
        ref_tup = self.cursor.execute('select * from sources where ref_id = ?', 
            (ref_id,)).fetchone()
        if not ref_tup:
            return None
        return reference(*ref_tup)

    def nodes(self) -> set:
        return { tup[0] for tup in self.cursor.execute('select node_id from nodes').fetchall() }

    def links(self) -> set:
        return { tup[0] for tup in self.cursor.execute('select link_id from links').fetchall() }
  
    def references(self) -> set:
        return { tup[0] for tup in self.cursor.execute('select ref_id from sources').fetchall() }

    def export_data(self):
        tmp_path = Path(tempfile.mkdtemp())
        with open(tmp_path.joinpath('nodes.csv'), 'w') as f:
            writer = csv.writer()
            self.cursor('select * from nodes')
            nodes = self.cursor.fetchall()
            for node in nodes:
                writer.writerow(node)

    def clear(self):
        self.cursor.execute('drop table if exists nodes')
        self.cursor.execute('drop table if exists links')
        self.cursor.execute('drop table if exists sources')
        self.create_tables()