"""Tests for managing ArangoDB edges."""

import unittest

from arango import Arango
from arango.exceptions import *
from arango.tests.test_utils import (
    get_next_graph_name,
    get_next_col_name,
    get_next_db_name
)

class EdgeManagementTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arango = Arango()
        cls.db_name = get_next_db_name(cls.arango)
        cls.db = cls.arango.add_database(cls.db_name)

    @classmethod
    def tearDownClass(cls):
        #cls.arango.remove_database(cls.db_name)
        pass

    def setUp(self):
        self.col_name = get_next_col_name(self.db)
        self.col = self.db.add_collection(self.col_name)
        # Create the vertex collection
        self.vertex_col_name = get_next_col_name(self.db)
        self.vertex_col = self.db.add_collection(self.vertex_col_name)
        # Create the edge collection
        self.edge_col_name = get_next_col_name(self.db)
        self.edge_col = self.db.add_collection(
            self.edge_col_name, is_edge=True
        )
        # Create the graph
        self.graph_name = get_next_graph_name(self.db)
        self.graph = self.db.add_graph(
            name=self.graph_name,
            edge_definitions=[{
                "collection" : self.edge_col_name,
                "from" : [self.vertex_col_name],
                "to": [self.vertex_col_name]
            }],
        )
        # Add a few test vertices
        self.graph.add_vertex(
            self.vertex_col_name,
            key="vertex01",
            data={"value": 1}
        )
        self.graph.add_vertex(
            self.vertex_col_name,
            key="vertex02",
            data={"value": 2}
        )
        self.graph.add_vertex(
            self.vertex_col_name,
            key="vertex03",
            data={"value": 3}
        )

    def tearDown(self):
        self.db.remove_graph(self.graph_name)
        self.db.remove_collection(self.vertex_col_name)
        self.db.remove_collection(self.edge_col_name)

    def test_add_edge(self):
        self.graph.add_edge(
            edge_collection_name=self.edge_col_name,
            from_vertex_id="{}/{}".format(self.vertex_col_name, "vertex01"),
            to_vertex_id="{}/{}".format(self.vertex_col_name, "vertex01"),
            key="edge01",
            data={"value": "foobar"}
        )
        self.assertEqual(self.edge_col.count, 1)
        self.assertEqual(
            self.graph.get_edge(self.edge_col_name, "edge01")["value"],
            "foobar"
        )
        self.assertEqual(
            self.graph.get_edge(self.edge_col_name, "edge01")["_from"],
            "{}/{}".format(self.vertex_col_name, "vertex01")
        )
        self.assertEqual(
            self.graph.get_edge(self.edge_col_name, "edge01")["_to"],
            "{}/{}".format(self.vertex_col_name, "vertex01")
        )

    def test_update_edge(self):
        self.graph.add_edge(
            edge_collection_name=self.edge_col_name,
            from_vertex_id="{}/{}".format(self.vertex_col_name, "vertex01"),
            to_vertex_id="{}/{}".format(self.vertex_col_name, "vertex01"),
            key="edge01",
            data={"value": 10}
        )
        self.graph.update_edge(
            edge_collection_name=self.edge_col_name,
            key="edge01",
            data={"value": 20, "new_value": 30}
        )
        self.assertEqual(
            self.graph.get_edge(
                self.edge_col_name,
                key="edge01",
            )["value"],
            20
        )
        self.assertEqual(
            self.graph.get_edge(
                self.edge_col_name,
                key="edge01",
            )["new_value"],
            30
        )

    def test_replace_edge(self):
        self.graph.add_edge(
            edge_collection_name=self.edge_col_name,
            from_vertex_id="{}/{}".format(self.vertex_col_name, "vertex01"),
            to_vertex_id="{}/{}".format(self.vertex_col_name, "vertex01"),
            key="edge01",
            data={"value": 10}
        )
        self.graph.replace_edge(
            edge_collection_name=self.edge_col_name,
            key="edge01",
            data={"new_value": 20}
        )
        self.assertNotIn(
            "value",
            self.graph.get_edge(
                self.edge_col_name,
                key="edge01",
            )
        )
        self.assertEqual(
            self.graph.get_edge(
                self.edge_col_name,
                key="edge01",
            )["new_value"],
            20
        )

    def test_remove_edge(self):
        self.graph.add_edge(
            edge_collection_name=self.edge_col_name,
            from_vertex_id="{}/{}".format(self.vertex_col_name, "vertex01"),
            to_vertex_id="{}/{}".format(self.vertex_col_name, "vertex01"),
            key="edge01",
            data={"value": 10}
        )
        self.graph.remove_edge(
            edge_collection_name=self.edge_col_name,
            key="edge01",
        )
        self.assertNotIn("edge01", self.edge_col)
        self.assertEqual(len(self.edge_col), 0)


if __name__ == "__main__":
    unittest.main()
