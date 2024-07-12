import numpy as np
from collections import defaultdict
from queue import PriorityQueue
import typing
import math

class Object:
    def passable(self) -> bool:
        '''Can another object move through a space containing this object?'''
        pass

    def add_to_slot(self, slot: 'EnvSlot') -> bool:
        pass

    def remove_from_slot(self, slot: 'EnvSlot') -> None:
        pass
    

class Wall(Object):
    def __init__(self):
        pass

    def passable(self) -> bool:
        return False
    
    def add_to_slot(self, slot: 'EnvSlot') -> bool:
        return slot.add_wall(self)
    
    def remove_from_slot(self, slot: 'EnvSlot') -> None:
        slot.remove_wall()


class Resource(Object):
    def __init__(self):
        pass

    def passable(self) -> bool:
        return True
    
    def add_to_slot(self, slot: 'EnvSlot') -> bool:
        return slot.add_resource(self)
    
    def remove_from_slot(self, slot: 'EnvSlot') -> None:
        slot.remove_resource()
    
    
class Agent(Object):
    def __init__(self):
        pass

    def passable(self) -> bool:
        return True
    
    def add_to_slot(self, slot: 'EnvSlot') -> bool:
        return slot.add_agent(self)
    
    def remove_from_slot(self, slot: 'EnvSlot') -> None:
        slot.remove_agent(self)
    
    
class JobSite(Object):
    def __init__(self):
        pass

    def passable(self):
        return True
    
    def add_to_slot(self, slot: 'EnvSlot') -> bool:
        return slot.add_job_site(self)
    
    def remove_from_slot(self, slot: 'EnvSlot') -> None:
        slot.remove_jobs_site()


class EnvSlot():
    '''A space in the environment. This space is opinionated about what can be in it under different conditions'''
    def __init__(self):
        self._wall: typing.Optional[Wall] = None
        self._resource: typing.Optional[Resource] = None
        self._agents: set[Agent] = set()
        self._job_site: typing.Optional[JobSite] = None
        self._all = set()

    def is_wall(self) -> bool:
        return self._wall is not None

    def is_empty(self) -> bool:
        return self._wall is None and self._resource is None and len(self._agents) == 0 and self._job_site is None

    def add_wall(self, wall: Wall) -> bool:
        if self.is_empty():
            self._wall = wall
            self._all.add(wall)
            return True
        return False
    
    def remove_wall(self) -> None:
        self._all.remove(self._wall)
        self._wall = None
    
    def add_resource(self, resource: Resource) -> bool:
        if not self.is_wall() and self._resource is None:
            self._resource = resource
            self._all.add(resource)
            return True
        return False
    
    def remove_resource(self) -> None:
        self._all.remove(self._resource)
        self._resource = None
    
    def add_agent(self, agent: Agent) -> bool:
        if not self.is_wall():
            self._agents.add(agent)
            self._all.add(agent)
            return True
        return False
    
    def remove_agent(self, agent: Agent) -> None:
        self._all.remove(agent)
        self._agents.remove(agent)
    
    def add_job_site(self, job_site: JobSite) -> bool:
        if not self.is_wall() and self._job_site is None:
            self._job_site = job_site
            self._all.add(job_site)
            return True
        return False
    
    def remove_jobs_site(self) -> None:
        self._all.remove(self._job_site)
        self._job_site = None

    def objects(self) -> set[Object]:
        return self._all


Location = tuple[int, int]


class Environment():
    def __init__(self, n_rows, n_columns) -> None:
        self._grid = defaultdict(lambda: defaultdict(lambda: EnvSlot()))
        self.location_of = {}
        self.n_rows = n_rows
        self.n_cols = n_columns
    
    def in_bounds(self, loc: Location) -> bool:
        r, c = loc
        return 0 <= r < self.n_rows and 0 <= c < self.n_cols

    def add(self, o: Object, loc: Location) -> bool:
        row, col = loc
        if o not in self.location_of and self.in_bounds(loc):
            self.location_of[o] = loc
            return o.add_to_slot(self._grid[row][col])   
        return False # XXX Raise an error if this happens instead of using booleans

    def remove(self, o: Object) -> bool:
        if o in self.location_of:
            r,c = self.location_of[o]
            o.remove_from_slot(self._grid[r][c])
            del self.location_of[o]
            return True
        return False

    def move(self, o: Object, loc: Location) -> bool:
        removed = self.remove(o)
        if removed:
            # XXX Should I add it back to the previous location if it fails to be added to the new location?
            return self.add(o, loc)
        return False

    def get(self, loc: Location) -> EnvSlot:
        row, col = loc
        # XXX Should I check if loc is in bounds?
        return self._grid[row][col]

    def neighbours(self, loc: Location) -> list[Location]:
        r, c = loc
        locs = [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]
        locs = list(filter(self.in_bounds, locs))
        return locs  

    def passable(self, loc: Location):
        # XXX Should all locations out of bounds be impassable?
        objects = self.get(loc).objects()
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
    n_rows, n_columns = 2, 5
    env = Environment(n_rows, n_columns)
    # w = Wall()
    # print("Adding a wall", env.add(w, (1, 1)))
    # print("Is it there?", env.get((1,1)).is_wall())
    # print("Is it there?", env.get((1,1)).objects())
    # print("Removing Wall", env.remove(w))
    # print("Is it there?", env.get((1,1)).is_wall())

    # r = Resource()
    # print("Adding a resource", env.add(r, (1, 1)))
    # print("Is it there?", env.get((1,1)).objects())
    # print("Removing resource", env.remove(r))
    # print("Is it there?", env.get((1,1)).objects())

    # j = JobSite()
    # print("Adding a site", env.add(j, (1, 1)))
    # print("Is it there?", env.get((1,1)).objects())
    # print("Removing site", env.remove(j))
    # print("Is it there?", env.get((1,1)).objects())

    # a = Agent()
    # print("Adding an agent", env.add(a, (1, 1)))
    # print("Is it there?", env.get((1,1)).objects())
    # print("Removing agent", env.remove(a))
    # print("Is it there?", env.get((1,1)).objects())

    # w1 = Wall()
    # print("Adding a wall", env.add(w1, (1, 1)))
    # print("Is it there?", env.get((1,1)).is_wall())
    # print("Is it there?", env.get((1,1)).objects())
    # w2 = Wall()
    # print("Trying to add another wall", env.add(w2, (1,1)))
    # print("What is there?", env.get((1,1)).objects())

    # a1 = Agent()
    # print("Adding an agent a1", env.add(a1, (1, 1)))
    # print("Is it there?", env.get((1,1)).objects())
    # a2 = Agent()
    # print("Adding an agent a2", env.add(a2, (1, 1)))
    # print("Are they there?", env.get((1,1)).objects())
    # print("Removing agent a1", env.remove(a1))
    # print("What is there?", env.get((1,1)).objects())
    # print("Removing agent a2", env.remove(a2))
    # print("What is there?", env.get((1,1)).objects())


if __name__ == "__main__":
    main()
