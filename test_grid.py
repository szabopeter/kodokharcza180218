import unittest

from main import Grid


class GridTestCase(unittest.TestCase):
    def test_creation(self):
        grid = Grid(6, 4)
        self.assertIsNotNone(grid)

    def test_every_node_should_have_some_siblings(self):
        grid = Grid(7, 5)
        for node in grid.nodes.values():
            self.assertGreaterEqual(len(node.siblings), 2)
            self.assertLessEqual(len(node.siblings), 4)