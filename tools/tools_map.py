import random as rd
import copy
from collections import deque


from tools.tools_constants import (
    MAP_SIZE,
    CRYSTAL_PROBABILITY,
    NUMBER_CASES_DIGGER,
    DICT_ORIENTATIONS,
    NUMBER_TRIALS,
    PRECIOUS_STONE_PROBABILITY,
    DICT_TREASURE_STONES,
    my_collection
)

def get_position_from_direction(direction, position):
    if direction == DICT_ORIENTATIONS["top"]:
        return (position[0], position[1]+1)
    if direction == DICT_ORIENTATIONS["bottom"]:
        return (position[0], position[1]-1)
    if direction == DICT_ORIENTATIONS["right"]:
        return (position[0]+1, position[1])
    if direction == DICT_ORIENTATIONS["left"]:
        return (position[0]-1, position[1])

def choose_random_direction():
    direction = rd.choice(list(DICT_ORIENTATIONS.values()))
    return direction

def check_position_valid(position, list_elements):
    if position in list_elements:
        return False
    if position[0] < 0 or position[0] >= MAP_SIZE:
        return False
    if position[1] < 0 or position[1] >= MAP_SIZE:
        return False
    return True

def dig_ways(list_elements, grid_map, number_cases_digger):
    for position in list_elements:
        for counter in range(number_cases_digger):
            counter_trials = 0
            while counter_trials < NUMBER_TRIALS:
                direction = choose_random_direction()
                new_position = get_position_from_direction(direction, position)
                if check_position_valid(new_position, list_elements):
                    grid_map[new_position[1]][new_position[0]] = "G"
                    position = new_position
                    break
                counter_trials += 1
            if counter_trials == NUMBER_TRIALS:
                break
    return grid_map

def create_new_map(list_precious_stones, has_beacon=False):
    """
    Create a map
    """

    # Initialisation with only rocks
    grid_map = []

    # Place the rocks everywhere
    for counter_y in range(MAP_SIZE):
        list_y = []
        for counter_x in range(MAP_SIZE):
            list_y.append("R")
        grid_map.append(list_y)
    
    # Where all important elements are stored
    list_elements = []
      
    # Place the crystals
    for counter_y in range(MAP_SIZE):
        for counter_x in range(MAP_SIZE):
            if rd.random() <= CRYSTAL_PROBABILITY:
                grid_map[counter_y][counter_x] = "C"
                list_elements.append((counter_x, counter_y))

    # Place the precious stones
    for counter_y in range(MAP_SIZE):
        for counter_x in range(MAP_SIZE):
            if rd.random() <= PRECIOUS_STONE_PROBABILITY:
                precious_stone_code = rd.choice(list(DICT_TREASURE_STONES.keys()))
                if precious_stone_code not in list_precious_stones and (
                    not my_collection.dict_collection[
                    DICT_TREASURE_STONES[precious_stone_code]]):
                    grid_map[counter_y][counter_x] = precious_stone_code
                    list_elements.append((counter_x, counter_y))
                    list_precious_stones.append(precious_stone_code)

    # Add all sides of the screen to unlock the ways
    list_positions_sides = [
        (MAP_SIZE//2, 0),
        (MAP_SIZE//2, MAP_SIZE-1),
        (0, MAP_SIZE//2),
        (MAP_SIZE-1, MAP_SIZE//2)
    ]
    for position in list_positions_sides:
        list_elements.append(position)
        grid_map[position[1]][position[0]] = "G"

    # Place the beacon
    if has_beacon:
        beacon_position = (MAP_SIZE//2, MAP_SIZE//2)
        list_joinable_elements = []
        grid_map[beacon_position[1]][beacon_position[0]] = "B"
        if beacon_position not in list_elements:
            list_elements.append(beacon_position)
        for side_position in list_positions_sides:
            list_joinable_elements.append([beacon_position, side_position])

        # Each case around the beacon is free
        grid_map[MAP_SIZE//2][MAP_SIZE//2 + 1] = "G"
        grid_map[MAP_SIZE//2][MAP_SIZE//2 - 1] = "C"
        list_elements.append((MAP_SIZE//2 - 1, MAP_SIZE//2))
        grid_map[MAP_SIZE//2 + 1][MAP_SIZE//2 + 1] = "G"
        grid_map[MAP_SIZE//2 - 1][MAP_SIZE//2 + 1] = "G"
        grid_map[MAP_SIZE//2 + 1][MAP_SIZE//2 - 1] = "G"
        grid_map[MAP_SIZE//2 - 1][MAP_SIZE//2 - 1] = "G"
        grid_map[MAP_SIZE//2 + 1][MAP_SIZE//2] = "G"
        grid_map[MAP_SIZE//2 - 1][MAP_SIZE//2] = "G"

    # Create the path by digging the way
    is_joinable = False
    number_cases_digger = NUMBER_CASES_DIGGER
    while not is_joinable:
        new_grid_map = dig_ways(
            list_elements=list_elements,
            grid_map=copy.deepcopy(grid_map),
            number_cases_digger=number_cases_digger)

        # Only the map with the beacon interests us
        if not has_beacon:
            break

        for element in list_joinable_elements:
            is_joinable = are_points_joinable(
                grid=new_grid_map,
                pointA=element[0],
                pointB=element[1]
            )
            if not is_joinable:
                break
        
        number_cases_digger += 1
    return new_grid_map, list_precious_stones


def are_points_joinable(grid, pointA, pointB):
    rows = len(grid)
    cols = len(grid[0])

    queue = deque()
    visited = set()

    xA, yA = pointA
    xB, yB = pointB

    queue.append((xA, yA))
    visited.add((xA, yA))

    while queue:
        x, y = queue.popleft()
        if x == xB and y == yB:
            return True
        neighbors = get_neighbors(x, y, rows, cols)
        for nx, ny in neighbors:
            if (nx, ny) not in visited and grid[nx][ny] in ('G', 'C'):
                queue.append((nx, ny))
                visited.add((nx, ny))

    return False

def get_neighbors(x, y, rows, cols):
    neighbors = []
    # Up
    if x - 1 >= 0:
        neighbors.append((x - 1, y))
    # Down
    if x + 1 < rows:
        neighbors.append((x + 1, y))
    # Left
    if y - 1 >= 0:
        neighbors.append((x, y - 1))
    # Right
    if y + 1 < cols:
        neighbors.append((x, y + 1))

    return neighbors

def grid_to_string(grid):
    rows = len(grid)
    cols = len(grid[0])

    string = ""
    for i in range(rows):
        for j in range(cols):
            string += grid[i][j] + " "
        string += "\n"

    return string
