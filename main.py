import sys
# import math


def log(msg):
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    print(msg, file=sys.stderr)


class Orientation:
    def __init__(self, as_char, vector):
        self.as_char, self.vector = as_char, vector

    def __str__(self):
        return self.as_char

    def __repr__(self):
        return str(self)


class CONSTS:
    WALL_SIZE = 2
    WALL_ORIENTATION_VERTICAL = Orientation('V', (0, 1))
    WALL_ORIENTATION_HORIZONTAL = Orientation('H', (1, 0))


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

    to_out = {
        WEST: 'LEFT',
        EAST: 'RIGHT',
        NORTH: 'UP',
        SOUTH: 'DOWN'
    }


class Wall:
    def __init__(self, position, orientation, size=CONSTS.WALL_SIZE):
        self.x, self.y = position
        self.orientation = orientation
        self.size = size

    def signature(self):
        return self.x, self.y, self.orientation, self.size

    def __repr__(self):
        return "Wall: " + str(self.signature())

    def __eq__(self, other):
        return self.signature() == other.signature()

    def __hash__(self):
        return hash(self.signature())

    def prevents(self):
        x, y = self.x, self.y
        xv, yv = self.orientation.vector
        prevented = [Wall((x+i*xv, y+i*yv), self.orientation, CONSTS.WALL_SIZE)
                     for i in range(CONSTS.WALL_SIZE + 1)]
        return prevented


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

    def has_connection(self, label):
        return label in self.labels

    def is_connected(self, other):
        return other in self.siblings

    def __str__(self):
        return "N(%s,%s)" % self.position

    def __repr__(self):
        return str(self)


class Connection:
    CONNECTED = 1
    DISCONNECTED = 0

    def __init__(self, node1, node2):
        # assert connected in (Connection.CONNECTED, Connection.DISCONNECTED)
        # self.connected = connected
        self.nodes = (node1, node2)
        self.nodeset = {node1, node2}

    def signature(self):
        return self.nodes

    def __hash__(self):
        return hash(self.signature())

    def __eq__(self, other):
        return self.nodeset == other.nodeset


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.nodes = {}
        self.connections = {}

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
                        connection = Connection(this_node, sibling_node)
                        self.connections[connection] = Connection.CONNECTED

        self.walls = []
        self.possible_walls = self.all_possible_walls()

    def register_wall(self, wall):
        if wall in self.walls:
            return

        self.walls.append(wall)
        made_impossible = [prevented for prevented in self.possible_walls[wall]]
        for prevented in made_impossible:
            del self.possible_walls[prevented]

        if wall.orientation == CONSTS.WALL_ORIENTATION_VERTICAL:
            self.register_west_wall(wall.position)
        elif wall.orientation == CONSTS.WALL_ORIENTATION_HORIZONTAL:
            self.register_north_wall(wall.position)
        else:
            raise NotImplemented

    def register_wall_segments(self, position, direction, size=2):
        x, y = position
        xo, yo = DIR.offsets[direction]
        for i in range(size):
            this_node = self.nodes[(x + xo * i, y + yo * i)]
            other_node = this_node.labels[direction]
            this_node.disconnect_label(direction)
            self.connections[Connection(this_node, other_node)] = Connection.DISCONNECTED

    def register_west_wall(self, position, size=2):
        self.register_wall_segments(position, DIR.WEST)

    def register_north_wall(self, position, size=2):
        self.register_wall_segments(position, DIR.NORTH)

    def can_pass(self, position, direction):
        return direction in self.nodes[position].labels

    def is_free(self, direction, *positions):
        for position in positions:
            if position not in self.nodes:
                return False
            if not self.nodes[position].has_connection(direction):
                return False
        return True

    def can_build_north_wall(self, position):
        x, y = position
        return self.is_free(DIR.NORTH, (x, y), (x+1, y))

    def can_build_west_wall(self, position):
        x, y = position
        return self.is_free(DIR.WEST, (x, y), (x, y+1))

    def possible_block(self, position, direction):
        # TODO: use list of possible walls
        # gen blocking walls, check if possible

        x, y = position
        if direction == DIR.EAST:
            if self.can_build_west_wall((x+1, y)):
                return (x+1, y), CONSTS.WALL_ORIENTATION_VERTICAL
            if self.can_build_west_wall((x+1, y-1)):
                return (x+1, y-1), CONSTS.WALL_ORIENTATION_VERTICAL
        if direction == DIR.WEST:
            if self.can_build_west_wall((x, y)):
                return (x, y), CONSTS.WALL_ORIENTATION_VERTICAL
            if self.can_build_west_wall((x, y-1)):
                return (x, y-1), CONSTS.WALL_ORIENTATION_VERTICAL
        return None

    def all_possible_walls(self):
        walls = {}
        for y in range(self.h):
            for x in range(self.w):
                position = (x, y)
                if self.can_build_west_wall(position):
                    walls[Wall(position, CONSTS.WALL_ORIENTATION_VERTICAL)] = None
                if self.can_build_north_wall(position):
                    walls[Wall(position, CONSTS.WALL_ORIENTATION_HORIZONTAL)] = None

        for w in walls.keys():
            walls[w] = w.prevents()

        return walls


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
            log('WTF: %s not in %s' % (position, list(self.distances.keys())))
            return 12
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
        wall = Wall((x, y), orientation)
        self.grid.register_wall(wall)
        return

    def player_move(self, player):
        scoregrid = ScoreGrid(self.grid, player.goal)
        node = self.grid.nodes[(player.x, player.y)]
        options = [(direction, scoregrid.get_distance_at_xy(sibling.position))
                   for (sibling, direction) in node.siblings.items()]
        options.sort(key=lambda pair: pair[1])
        return options[0]

    def decide(self):
        my_id, yo_id = self.my_id, 1 - self.my_id
        me = self.players[my_id]
        yo = self.players[yo_id]
        my_move, my_dist = self.player_move(self.players[my_id])
        yo_move, yo_dist = self.player_move(self.players[yo_id])

        need_no_wall = my_dist < yo_dist or (my_dist == yo_dist and my_id < yo_id)
        need_wall = not need_no_wall
        if need_wall and me.walls_left > 0:
            ex, ey = yo.x, yo.y
            block = self.grid.possible_block((ex, ey), yo_move)
            if block is not None:
                wall_pos, wall_orientation = block
                wx, wy = wall_pos
                return "%s %s %s" % (wx, wy, wall_orientation)

        return DIR.to_out[my_move]


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
            log("Wall %s at %s, %s" % (wall_orientation, wall_x, wall_y))

        # action: LEFT, RIGHT, UP, DOWN or "putX putY putOrientation" to place a wall
        print(arena.decide())


if __name__ == '__main__':
    main()
