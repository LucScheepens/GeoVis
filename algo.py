import dataclasses
import pickle
from itertools import product
import numpy as np


# TODO: Output mustpip include the width of each path DONE -> but add this to path_generation
# TODO: Number of slots should be calculated dynamically
#       => Another objective is to minimize the number of slots?
# TODO: Slot offsets should be calculated dynamically
# TODO: What is the lines overlap? How to calculate it? -> Optimize the path to minimize the overlap DONE -> check area function
#  -> E.g. by putting the thick line to side or by changing the slot offset


@dataclasses.dataclass
class Point:
    x: float
    y: float


SLOT_POSITIONS = ['S1', 'S2', 'S3', 'S4', 'S5']
NODE_COORDINATES = {
    'Root': Point(0, 0),
    'A': Point(10, 10),
    'C': Point(20, 20),
    'F': Point(30, 30),
    'G': Point(40, 40),
    'H': Point(50, 50)
}

SLOT_OFFSETS = {
    'S1': (0, 0),
    'S2': (-1, 1),
    'S3': (1, 1),
    'S4': (-1, -1),
    'S5': (1, -1)
}

SLOT_COORDINATES = {}
for node, point in NODE_COORDINATES.items():
    for slot in SLOT_POSITIONS:
        offset_x, offset_y = SLOT_OFFSETS[slot]
        SLOT_COORDINATES[(node, slot)] = Point(point.x + offset_x, point.y + offset_y)


def contains_equals(route1, route2):
    """A function that checks for two segments if they use the same slot at the same node"""
    for node1, slot1 in route1:
        for node2, slot2 in route2:
            if node1 == node2 and slot1 == slot2:
                return True

    return False


def identify_wrong_combos(dot_product):
    """filter out combinations that have paths use the same slot at the same node"""
    to_reject = []
    for configuration in dot_product:
        for i in range(len(configuration)):
            for j in range(i+1, len(configuration)):
                if contains_equals(configuration[i], configuration[j]):
                    to_reject.append(configuration)
    return to_reject


def combination_to_coordinates(configuration):
    """Function that translates a combination to their corresponding coordinates"""
    coordinates_for_configuration = []
    for route in configuration:
        coordinates_for_route = []
        for point_on_route in route:
            coordinates_for_route.append(SLOT_COORDINATES[point_on_route])

        coordinates_for_configuration.append(coordinates_for_route)

    return coordinates_for_configuration


def orientation(p, q, r):
    """Uses the cross product to determine if q lies to the left or right of the line formed by p and r.
    If the value is 0, it means the points are collinear. If it's positive, q lies to the left, otherwise to the right."""
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val == 0:
        return 0
    return 1 if val > 0 else 2


def do_intersect(p1, q1, p2, q2):
    """Function that checks if two lines intersect"""
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True

    # if they are collinear, but it still lies on the segment, then it is also intersecting
    # this is the case when lines overlap each other
    # if o1 == 0 and on_segment(p1, p2, q1):
    #     return True
    # if o2 == 0 and on_segment(p1, q2, q1):
    #     return True
    # if o3 == 0 and on_segment(p2, p1, q2):
    #     return True
    # if o4 == 0 and on_segment(p2, q1, q2):
    #     return True
    
    if o1 == 0 or o2 == 0 or o3 == 0 or o4 == 0:
        return True

    return False

# If three points are collinear then that already implies they are "on segment"
# def on_segment(p, q, r):
#     """Checks if a point q lies on the line segment pr.
#     It checks if q lies between p and r both horizontally and vertically."""
#     return max(p.x, r.x) >= q.x >= min(p.x, r.x) and max(p.y, r.y) >= q.y >= min(p.y, r.y)


def count_intersections(lines):
    """Function that counts the number of intersections between lines"""
    count = 0
    for i in range(len(lines)):
        for j in range(i+1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            for k in range(len(line1)-1):
                for l in range(len(line2)-1):
                    if do_intersect(line1[k], line1[k+1], line2[l], line2[l+1]):
                        count += 1
    return count

#HELPER FUNCTIONS FOR THE RECTANGLES
def coords_widths(combination,path_widths):
    """Function that transforms a combination to a tuple with its coordinates and width"""
    comb_widths = []
    coords = combination_to_coordinates(combination)
    for i, segment in enumerate(combination):
        path=tuple(item[0] for item in segment)
        comb_widths.append((coords[i],path_widths[path]))
    return comb_widths

def perpendicular_vector(v):
    return np.array([-v[1], v[0]], dtype=float)

def get_rectangle_corners(point1, point2, width):
    """Turns one segment of a line into a rectangle"""
    v = np.array([point2.x - point1.x, point2.y - point1.y], dtype=float)
    perpendicular = perpendicular_vector(v)
    perpendicular /= np.linalg.norm(perpendicular)
    offset = perpendicular * width / 2

    p1 = Point(point1.x + offset[0], point1.y + offset[1])
    p2 = Point(point2.x + offset[0], point2.y + offset[1])
    p3 = Point(point2.x - offset[0], point2.y - offset[1])
    p4 = Point(point1.x - offset[0], point1.y - offset[1])

    return p1, p2, p3, p4

def line_to_rectangles(line, width):
    """Turns an entire line into a list of rectangles"""
    rectangles = []
    for i in range(len(line) - 1):
        p1, p2, p3, p4 = get_rectangle_corners(line[i], line[i+1], width)
        rectangles.append([p1, p2, p3, p4])
    return rectangles

def rectangle_intersection_area(rect1, rect2):
    """Calculate the intersection area between two rectangles."""
    """DETERMINE IF THIS IS ALSO FOR DIAGONAL RECTANGLES"""
    x_overlap = max(0, min(rect1[1].x, rect2[1].x) - max(rect1[0].x, rect2[0].x))
    y_overlap = max(0, min(rect1[1].y, rect2[1].y) - max(rect1[0].y, rect2[0].y))
    return x_overlap * y_overlap

def line_overlap(lines):
    """Calculate the total overlap for each line."""
    overlaps = []
    for i, line1 in enumerate(lines):
        total_overlap = 0
        for j, line2 in enumerate(lines):
            if i != j:  # Avoid comparing a line with itself
                for rect1 in line1:
                    for rect2 in line2:
                        total_overlap += rectangle_intersection_area(rect1, rect2)
        overlaps.append(total_overlap)
    return overlaps

def total_overlap(combination,path_widths):
    """Calculate the total overlap""" 
    b_comb_width = coords_widths(combination,path_widths)
    rect_comb = []
    for line in b_comb_width:
        rectangles = line_to_rectangles(line[0], line[1])
        rect_comb.append(rectangles)
    return sum(line_overlap(rect_comb))


def main(path: str = "assets/generated-path.pkl"):
    with open(path, "rb") as f:
        paths = pickle.load(f)

    paths = {('Root', 'A', 'C'): [[('Root', 'S1'), ('A', 'S1'), ('C', 'S1')], [('Root', 'S2'), ('A', 'S2'), ('C', 'S2')], [('Root', 'S3'), ('A', 'S3'), ('C', 'S3')], [('Root', 'S4'), ('A', 'S4'), ('C', 'S4')], [('Root', 'S5'), ('A', 'S5'), ('C', 'S5')]], ('Root', 'A', 'C', 'F', 'G'): [[('Root', 'S1'), ('A', 'S1'), ('C', 'S1'), ('F', 'S1'), ('G', 'S1')], [('Root', 'S2'), ('A', 'S2'), ('C', 'S2'), ('F', 'S2'), ('G', 'S2')], [('Root', 'S3'), ('A', 'S3'), ('C', 'S3'), ('F', 'S3'), ('G', 'S3')], [('Root', 'S4'), ('A', 'S4'), ('C', 'S4'), ('F', 'S4'), ('G', 'S4')], [('Root', 'S5'), ('A', 'S5'), ('C', 'S5'), ('F', 'S5'), ('G', 'S5')]], ('Root', 'A', 'C', 'F', 'H'): [[('Root', 'S1'), ('A', 'S1'), ('C', 'S1'), ('F', 'S1'), ('H', 'S1')], [('Root', 'S2'), ('A', 'S2'), ('C', 'S2'), ('F', 'S2'), ('H', 'S2')], [('Root', 'S3'), ('A', 'S3'), ('C', 'S3'), ('F', 'S3'), ('H', 'S3')], [('Root', 'S4'), ('A', 'S4'), ('C', 'S4'), ('F', 'S4'), ('H', 'S4')], [('Root', 'S5'), ('A', 'S5'), ('C', 'S5'), ('F', 'S5'), ('H', 'S5')]]}

    # Dictionary to store width, this should perhaps be integrated in the path generation code
    # also right now i have to add this in every function that uses coords_widths bahahah
    path_widths = {
        ('Root', 'A', 'C'): 1,
        ('Root', 'A', 'C', 'F', 'G'): 2,
        ('Root', 'A', 'C', 'F', 'H'): 1.5
    }

    configuration_dot_product = list(product(*paths.values()))
    wrong_combos = identify_wrong_combos(configuration_dot_product)

    valid_configurations = [element for element in configuration_dot_product if element not in wrong_combos]

    # best_combination = sorted(valid_configurations, key=lambda x: count_intersections(combination_to_coordinates(x)))[0]

    best_combination = sorted(valid_configurations, key=lambda x: total_overlap(x,path_widths))[0]

    # return combination_to_coordinates(best_combination)
    return coords_widths(best_combination,path_widths), total_overlap(best_combination,path_widths)

if __name__ == "__main__":
    print(main())
