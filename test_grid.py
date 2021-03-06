import unittest

from main import Grid, Node, DIR, Wall, CONSTS


class GridTestCase(unittest.TestCase):
    def test_creation(self):
        grid = Grid(6, 4)
        self.assertIsNotNone(grid)

    def test_every_node_should_have_some_siblings(self):
        grid = Grid(7, 5)
        for node in grid.nodes.values():
            self.assertGreaterEqual(len(node.siblings), 2)
            self.assertLessEqual(len(node.siblings), 4)

    def test_connect_nodes(self):
        n1 = Node((1, 1))
        n2 = Node((2, 2))
        n1.connect_to(n2, 'E')
        self.assertIn('E', n1.labels)
        self.assertEqual(n1.labels['E'], n2)
        self.assertIn(n2, n1.siblings)
        self.assertEqual(n1.siblings[n2], 'E')
        self.assertEqual(len(n2.siblings), 0)
        self.assertEqual(len(n2.labels), 0)

        n2.connect_to(n1, 'W')

    def test_disconnect_nodes(self):
        n1 = Node((1, 1))
        n2 = Node((2, 2))
        n1.connect_to(n2, 'E')
        n2.connect_to(n1, 'W')
        n1.disconnect_label('E')
        for container in n1.siblings, n2.siblings, n1.labels, n2.labels:
            self.assertEqual(len(container), 0)

    def test_disconnect(self):
        grid = Grid(7, 5)
        self.assertTrue(grid.can_pass((3, 1), DIR.SOUTH))
        self.assertTrue(grid.can_pass((3, 2), DIR.NORTH))
        grid.register_north_wall((3, 2))
        self.assertFalse(grid.can_pass((3, 1), DIR.SOUTH))
        self.assertFalse(grid.can_pass((3, 2), DIR.NORTH))

    def test_wallbuilding(self):
        grid = Grid(7, 5)
        node14 = grid.nodes[(1, 4)]
        node24 = grid.nodes[(2, 4)]
        self.assertTrue(node24.is_connected(node14))
        self.assertTrue(node14.is_connected(node24))

        grid.register_west_wall((2, 3))

        self.assertFalse(node24.is_connected(node14))
        self.assertFalse(node14.is_connected(node24))

    def test_can_build_west_wall(self):
        grid = Grid(7, 5)
        for i in (0, 1, 2, 3):
            self.assertTrue(grid.can_build_west_wall((2, i)), "Should be able to build at %s" % i)
        grid.register_west_wall((2, 1))
        for i, expected in [(0, False),
                            (1, False),
                            (2, False),
                            (3, True),
                            ]:
            actual = grid.can_build_west_wall((2, i))
            self.assertEqual(actual, expected,
                             "Got %s at %s instead of the expected %s" % (actual, i, expected))

    def test_is_free(self):
        grid = Grid(7, 5)
        self.assertTrue(grid.is_all_free(DIR.WEST, (2, 1), (2, 2)))
        grid.register_west_wall((2, 1))
        self.assertFalse(grid.is_all_free(DIR.WEST, (2, 1), (2, 2)))
        self.assertFalse(grid.is_all_free(DIR.WEST, (2, 2)))
        self.assertTrue(grid.is_all_free(DIR.WEST, (2, 3)))

    def test_possible_wall_initialization(self):
        too_small = ((1, 1), (2, 1), (1, 2))
        for w, h in too_small:
            self.assertEqual(0, len(Grid(w, h).possible_walls))

        grid = Grid(2, 2)
        possibles = grid.possible_walls.keys()
        self.assertEqual(2, len(possibles))

        self.assertIn(Wall((1, 0), CONSTS.WALL_ORIENTATION_VERTICAL), possibles)
        self.assertIn(Wall((0, 1), CONSTS.WALL_ORIENTATION_HORIZONTAL), possibles)
