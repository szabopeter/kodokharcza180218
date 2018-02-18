import unittest

from main import Arena, Player


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