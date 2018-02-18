import unittest

from main import Arena, Player, ScoreGrid


class ArenaTestCase(unittest.TestCase):
    def test_creation(self):
        arena = Arena(7, 5, 2, 0)
        self.assertIsNotNone(arena)
        self.assertIsInstance(arena.players[1], Player)

    def test_player_update(self):
        arena = Arena(7, 5, 2, 0)
        arena.update_player(1, 2, 3, 4)
        player = arena.players[1]
        self.assertEqual((player.x, player.y, player.walls_left), (2, 3, 4))


class ScoreGridTestCase(unittest.TestCase):
    def test_creation(self):
        arena = Arena(7, 5, 2, 0)
        score_grid = ScoreGrid(arena.grid, arena.players[0].goal)
        a_start_node = arena.grid.nodes[(0, 2)]
        an_end_node = arena.grid.nodes[(6, 3)]
        for y in range(5):
            line = [str(score_grid.get_distance_at_xy((x, y))) for x in range(7)]
            print("\t".join(line))
        self.assertEqual(score_grid.distances[a_start_node.position], 6)
        self.assertEqual(score_grid.distances[an_end_node.position], 0)