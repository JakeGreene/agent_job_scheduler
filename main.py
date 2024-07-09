import numpy as np

class Object:
    pass


class EmptySpace(Object):
    pass


class Environment():
    def __init__(self, rows, columns) -> None:
        self.grid = np.array((rows, columns)) # XXX Every entry should be EmptySpace()
        self.location_of = {}
    

    def add(self, o: Object, row: int, column: int) -> bool:
        if o not in self.location_of and row >= 0 and row < self.grid.shape[0] and column >= 0 and column <= self.grid.shape[1] and self.grid[row][column].isinstance(EmptySpace):
            self.grid[row][column] = o
            self.location_of[o] = (row, column)
            return True
        return False # XXX Raise an error if this happens instead of using booleans


    def remove(self, o: Object) -> bool:
        if o in self.location_of:
            r,c = self.location_of[o]
            self.grid[r][c] = EmptySpace() # TODO consider a singleton
            del self.location_of[o]
            return True
        return False


    def move(self, o: Object, row: int, column: int) -> bool:
        removed = self.remove(o)
        if removed:
            return self.add(o, row, column)
        return False


    def get(self, row: int, column: int) -> Object:
        return self.grid[row][column]
    

    # TODO create a string repr of the grid and the objects in it. Requires objects to have a single char repr



def main():
    env = Environment(10, 10)
    print(env)

if __name__ == "__main__":
    main()
