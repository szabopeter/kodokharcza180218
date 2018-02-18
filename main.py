import sys
# import math


def log(msg):
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    print(msg, file=sys.stderr)


class CONSTS:
    WALL_ORIENTATION_VERTICAL = 'V'
    WALL_ORIENTATION_HORIZONTAL = 'H'


class DIR:
    WEST = 'W'
    EAST = 'E'
    NORTH = 'N'
    SOUTH = 'S'
    all = (NORTH, WEST, SOUTH, EAST)
    offsets = {
        WEST: (-1, 0),
        EAST: (1, 0),
        NORTH: (0, -1),
        SOUTH: (0, 1),
    }


class Node:
    def __init__(self, position):
        self.siblings = {}
        self.labels = {}
        self.position = position

    def connect_to(self, other, label="?"):
        if other not in self.siblings:
            self.siblings[other] = label

        self.labels[label] = other

    def disconnect_label(self, label):
        if label not in self.labels:
            return

        other = self.labels[label]
        del self.labels[label]
        del self.siblings[other]
        other.disconnect_sibling(self)

    def disconnect_sibling(self, other):
        if other not in self.siblings:
            return

        label = self.siblings[other]
        del self.labels[label]
        del self.siblings[other]
        other.disconnect_label(label)

    def __str__(self):
        return "N(%s,%s)" % self.position

    def __repr__(self):
        return str(self)


class Grid:
    def __init__(self, w, h):
        self.nodes = {}
        for y in range(h):
            for x in range(w):
                self.nodes[(x, y)] = Node((x, y))

        for y in range(h):
            for x in range(w):
                this_node = self.nodes[(x, y)]
                for direction, (xofs, yofs) in DIR.offsets.items():
                    nx, ny = x + xofs, y + yofs
                    if (nx, ny) in self.nodes:
                        sibling_node = self.nodes[(nx, ny)]
                        this_node.connect_to(sibling_node, direction)

    def register_west_wall(self, position):
        self.nodes[position].disconnect_label(DIR.WEST)

    def register_north_wall(self, position):
        self.nodes[position].disconnect_label(DIR.NORTH)

    def can_pass(self, position, direction):
        return direction in self.nodes[position].labels


class ScoreGrid:
    def __init__(self, grid, goal):
        self.distances = {}
        queue = [node for node_id, node in grid.nodes.items() if goal(node_id)]
        processed = queue[:]
        for node in queue:
            self.distances[node.position] = 0

        while queue:
            node = queue.pop(0)
            for sibling in node.siblings:
                if sibling in processed:
                    continue
                if sibling.position in self.distances:
                    continue
                self.distances[sibling.position] = self.distances[node.position] + 1
                queue.append(sibling)
            processed.append(node)

    def get_distance_at_xy(self, position):
        if position not in self.distances:
            return "?"
        return self.distances[position]


class Player:
    def __init__(self, player_id, goal):
        self.player_id = player_id
        self.x, self.y = None, None
        self.walls_left = 9999
        self.goal = goal


class Arena:
    def __init__(self, w, h, player_count, my_id):
        def goal0(node_position):
            x, y = node_position
            return x == w-1

        def goal1(node_position):
            x, y = node_position
            return x == 0

        self.w, self.h = w, h
        if player_count >= 3:
            print("KODOK HARCZA")
        self.player_count = 2
        goals = [goal0, goal1]
        self.players = [Player(i, goals[i]) for i in range(self.player_count)]
        self.my_id = my_id
        self.grid = Grid(w, h)

    def update_player(self, player_id, x, y, walls_left):
        player = self.players[player_id]
        player.x, player.y, player.walls_left = x, y, walls_left

    def register_wall(self, x, y, orientation):
        if orientation == CONSTS.WALL_ORIENTATION_VERTICAL:
            self.grid.register_west_wall((x, y))
        elif orientation == CONSTS.WALL_ORIENTATION_HORIZONTAL:
            self.grid.register_north_wall((x, y))
        else:
            raise NotImplemented

    def decide(self):
        score_grids = [ScoreGrid(self.grid, player.goal) for player in self.players]
        return "RIGHT"


def main():
    # Auto-generated code below aims at helping you parse
    # the standard input according to the problem statement.

    # w: width of the board
    # h: height of the board
    # player_count: number of players (2 or 3)
    # my_id: id of my player (0 = 1st player, 1 = 2nd player, ...)
    w, h, player_count, my_id = [int(i) for i in input().split()]
    arena = Arena(w, h, player_count, my_id)

    # game loop
    while True:
        for i in range(player_count):
            # x: x-coordinate of the player
            # y: y-coordinate of the player
            # walls_left: number of walls available for the player
            x, y, walls_left = [int(j) for j in input().split()]
            arena.update_player(i, x, y, walls_left)

        wall_count = int(input())  # number of walls on the board
        for i in range(wall_count):
            # wall_x: x-coordinate of the wall
            # wall_y: y-coordinate of the wall
            # wall_orientation: wall orientation ('H' or 'V')
            wall_x, wall_y, wall_orientation = input().split()
            wall_x = int(wall_x)
            wall_y = int(wall_y)
            arena.register_wall(wall_x, wall_y, wall_orientation)

        # action: LEFT, RIGHT, UP, DOWN or "putX putY putOrientation" to place a wall
        print(arena.decide())


if __name__ == '__main__':
    main()