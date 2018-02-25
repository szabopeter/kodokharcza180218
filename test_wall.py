import unittest

from main import Wall, CONSTS


class WallTestCase(unittest.TestCase):
    def test_equality(self):
        w1 = Wall((1,2), "o1", 3)
        w2 = Wall((1,2), "o1", 3)
        self.assertEqual(w1, w2)

        # noinspection PyDictCreation
        d = {w1: 1}
        d[w2] = 2

        self.assertEqual(d[w1], d[w2])

    def test_prevents(self):
        w1 = Wall((5,2), CONSTS.WALL_ORIENTATION_HORIZONTAL, 3)
        prevented = set(w1.prevents())
        expected_prevented = set([Wall(position, CONSTS.WALL_ORIENTATION_HORIZONTAL)
                                  for position in ((5, 2), (6, 2), (7, 2))])
        self.assertSetEqual(prevented, expected_prevented)
        # self.assertEqual(len(prevented), 2)
