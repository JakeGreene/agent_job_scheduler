import numpy as np
from collections import defaultdict
from queue import PriorityQueue
import typing
import math

class Object:
    def passable(self) -> bool:
        '''Can another object move through a space containing this object?'''
        pass


# XXX Does this need to be a first class citizen?
class EmptySpace(Object):
    def passable(self) -> bool:
        return True
    

class Dummy(Object):
    '''The Dummy class exists only to populate the environment with test objects
    '''
    def __init__(self, name, passable):
        self._name = name
        self._passable = passable

    def passable(self) -> bool:
        return self._passable
    
    def __repr__ (self) -> str:
        return self._name
    

class Wall(Object):
    def __init__(self):
        pass

    def passable(self) -> bool:
        return False


Location = tuple[int, int]


class Environment():
    def __init__(self, n_rows, n_columns) -> None:
        self._grid = defaultdict(lambda: defaultdict(set))
        self.location_of = {}
        self.n_rows = n_rows
        self.n_cols = n_columns

    
    def in_bounds(self, loc: Location) -> bool:
        r, c = loc
        return 0 <= r < self.n_rows and 0 <= c < self.n_cols


    def add(self, o: Object, loc: Location) -> bool:
        row, col = loc
        if o not in self.location_of and self.in_bounds(loc):
            self._grid[row][col].add(o)
            self.location_of[o] = (row, col)
            return True
        return False # XXX Raise an error if this happens instead of using booleans


    def remove(self, o: Object) -> bool:
        if o in self.location_of:
            r,c = self.location_of[o]
            self._grid[r][c].remove(o)
            del self.location_of[o]
            return True
        return False


    def move(self, o: Object, loc: Location) -> bool:
        removed = self.remove(o)
        if removed:
            # XXX Should I add it back to the previous location if it fails to be added to the new location?
            return self.add(o, loc)
        return False


    def get(self, loc: Location) -> set[Object]:
        row, col = loc
        # XXX Should I check if loc is in bounds?
        return self._grid[row][col]


    def neighbours(self, loc: Location) -> list[Location]:
        r, c = loc
        locs = [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]
        locs = list(filter(self.in_bounds, locs))
        return locs
    

    def passable(self, loc: Location):
        objects = self.get(loc)
        for o in objects:
            if not o.passable():
                return False
        return True

    # TODO create a string repr of the grid and the objects in it. Requires objects to have a single char repr


def manhatten_heuristic(a: Location, b: Location) -> float:
    a_row, a_col = a
    b_row, b_col = b
    return abs(a_row - b_row) + abs(a_col - b_col)


def find_path(env: Environment, start: Location, goal: Location, heuristic: typing.Callable[[Location, Location], float] = manhatten_heuristic) -> tuple[list[Location], float]:
    '''Find a path between start and goal if one exists. Uses A*'''
    # For the most part, copy pasted from https://www.redblobgames.com/pathfinding/a-star/implementation.html
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from: dict[Location, typing.Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()[1]
        if current == goal:
            break
        
        for next in env.neighbours(current):
            if env.passable(next):
                new_cost = cost_so_far[current] + 1 # env.cost(current, next) # XXX I am currently assuming the cost of movement is always 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(next, goal)
                    frontier.put((priority, next))
                    came_from[next] = current
    if goal in came_from:
        path = []
        prev = goal
        while prev:
            path.append(prev)
            prev = came_from[prev]
        path.reverse()
        return path, cost_so_far[goal]
    return ([], math.inf)


def main():
    # n_rows, n_columns = 2, 5
    # env = Environment(n_rows, n_columns)
    # path, cost = find_path(env, (0, 0), (0, 4))
    # print(path, cost)

    # n_rows, n_columns = 2, 5
    # env = Environment(n_rows, n_columns)
    # env.add(Wall(), (0, 2))
    # path, cost = find_path(env, (0, 0), (0, 4))
    # print(path, cost)

    n_rows, n_columns = 2, 5
    env = Environment(n_rows, n_columns)
    env.add(Wall(), (0, 2))
    env.add(Wall(), (1, 2)) # Completely walled off
    path, cost = find_path(env, (0, 0), (0, 4))
    print(path, cost)

if __name__ == "__main__":
    main()
