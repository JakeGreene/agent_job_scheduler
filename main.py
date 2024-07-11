import numpy as np
from collections import defaultdict

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

    # TODO create a string repr of the grid and the objects in it. Requires objects to have a single char repr



def main():
    n_rows, n_columns = 10, 10
    env = Environment(n_rows, n_columns)
    test_bounds_points = [(0, 0), (-1, 0), (0, -1), (0, n_columns-1), (n_rows-1, 0), (n_rows-1, n_columns-1), (n_rows, n_columns-1), (n_rows-1, n_columns), (n_rows, n_columns)]
    for l in test_bounds_points:
        print(f"Is {l} in bounds?", env.in_bounds(l))

    # d = Dummy(name="Dummy", passable=False)
    # l = (0, 0)
    # print("Adding Dummy", env.add(d, l))
    # print("Is Dummy there?", env.get(l))
    # print("Removing Dummy", env.remove(d))
    # print("Is Dummy there?", env.get(l))
    # print("Adding Dummy", env.add(d, l))
    # l2 = (l[0]+1, l[1]+1)
    # print("Moving Dummy", env.move(d, l2))
    # print("Is Dummy where it started?", env.get(l))
    # print("Is Dummy where it was moved to?", env.get(l2))

    # d1 = Dummy(name="Dummy1", passable=True)
    # l = (0, 0)
    # print("Adding Dummy1", env.add(d1, l))
    # d2 = Dummy(name="Dummy2", passable=True)
    # print("Adding Dummy2", env.add(d2, l))
    # print("Who is at the location?", env.get(l))
    # # print("Is Dummy there?", env.get(l))
    # # print("Removing Dummy", env.remove(d))
    # l2 = (1, 1)
    # print("Moving d1", env.move(d1, l2))
    # print(f"Who is at {l}?", env.get(l))
    # print(f"Who is at {l2}?", env.get(l2))

    # mid_row = n_rows // 2
    # mid_col = n_columns // 2
    # test_spots = [(0, 0), (0, n_columns-1), (n_rows-1, 0), (n_rows-1, n_columns-1), (mid_row, mid_col), (mid_row, 0), (0, mid_col)]
    # for loc in test_spots:
    #     print(f"Neighbouts of {loc}", env.neighbours(loc))

if __name__ == "__main__":
    main()
