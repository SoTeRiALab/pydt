import csv
from pathlib import Path
from .reference import Reference
from .node import Node
from .link import Link
from .uncertainty import Estimate
import shutil
import sqlite3
import tempfile

class db:
    def __init__(self):
        self.con = sqlite3.connect(':memory')
        self.cursor = self.con.cursor()
        self.create_tables()

    def create_tables(self):
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
                                    m1_a real not null,
                                    m1_b real not null,
                                    m1_sample_size real not null,
                                    m2_a real not null,
                                    m2_b real not null,
                                    m2_sample_size real not null,
                                    m3_a real not null,
                                    m3_b real not null,
                                    m3_sample_size real not null,
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

    def add_node(self, node: Node):
        self.cursor.execute('insert into nodes values (?, ?, ?)', 
            node.to_tuple())
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
        return Node(*node_tup)

    def add_link(self, link: Link):
        self.cursor.execute('')
        self.cursor.execute('insert into links values (?, ?, ?, ?,\
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', link.to_tuple())
        self.con.commit()

    def remove_link(self, link_id: str):
        self.cursor.execute('delete from links where link_id = ?', (link_id,))
        self.con.commit()

    def get_link(self, link_id: str):
        link_tup = self.cursor.execute('select * from links where link_id = ?', 
            (link_id,)).fetchone()
        if not link_tup:
            return None
        m1 = Estimate(*link_tup[3:6])
        m2 = Estimate(*link_tup[6:9])
        m3 = Estimate(*link_tup[9:12])
        print(*link_tup[0:3], m1, m2, m3, *link_tup[12:])
        return Link(*link_tup[0:3], m1, m2, m3, *link_tup[12:])

    def add_reference(self, reference: Reference):
        self.cursor.execute('insert into sources values(?, ?, ?, ?, ?, ?)', 
            reference.to_tuple())
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
        return Reference(*ref_tup)

    def nodes(self) -> set:
        return { tup[0] for tup in self.cursor.execute('select node_id from nodes').fetchall() }

    def links(self) -> set:
        return { tup[0] for tup in self.cursor.execute('select link_id from links').fetchall() }
  
    def references(self) -> set:
        return { tup[0] for tup in self.cursor.execute('select ref_id from sources').fetchall() }

    def export_data_files(self, tmp_path: Path):
        with open(tmp_path.joinpath('nodes.csv'), 'w') as f:
            writer = csv.writer(f)
            nodes = self.cursor('select * from nodes').fetchall()
            for node in nodes:
                writer.writerow(node)
        with open(tmp_path.joinpath('links.csv'), 'w') as f:
            writer = csv.writer(f)
            links = self.cursor('select * from links').fetchall()
            for link in links:
                writer.writerow(link)
        with open(tmp_path.joinpath('references.csv'), 'w') as f:
            writer = csv.writer(f)
            refs = self.cursor('select * from sources').fetchall()
            for ref in refs:
                writer.writerow(ref)

    def clear(self):
        self.cursor.execute('drop table if exists nodes')
        self.cursor.execute('drop table if exists links')
        self.cursor.execute('drop table if exists sources')
        self.create_tables()