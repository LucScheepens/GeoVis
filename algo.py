import dataclasses
import pickle
from itertools import product
import numpy as np

from path_slot_configuration_generator import generate_configuration
from utils import Point, LayoutAlgorithm, FlowPathsT, LayoutOutput, SLOTS

# Done: Output must include the frequency of each path
# TODO: Number of slots should be calculated dynamically
#       => Another objective is to minimize the number of slots?
# TODO: Slot offsets should be calculated dynamically
# Done: What is the lines overlap? How to calculate it?
# TODO: Optimize the path to minimize the overlap
#  -> E.g. by putting the thick line to side or by changing the slot offset

# TODOL: Add input -> path coordinates

SLOT_POSITIONS = ['S1', 'S2', 'S3', 'S4', 'S5']
NODE_COORDINATES = {
    'Root': Point(0, 0),
    'A': Point(0, 10),
    'C': Point(10, 10),
    'F': Point(30, 10),
    'G': Point(40, 10),
    'H': Point(30, 20)
}

SLOT_OFFSETS = {
    'S1': (0, 0),
    'S2': (-1, 1),
    'S3': (1, 1),
    'S4': (-1, -1),
    'S5': (1, -1)
}

# SLOT_COORDINATES = {}
# for node, point in NODE_COORDINATES.items():
#     for slot in SLOT_POSITIONS:
#         offset_x, offset_y = SLOT_OFFSETS[slot]
#         SLOT_COORDINATES[(node, slot)] = Point(point.x + offset_x, point.y + offset_y)


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


def combination_to_coordinates(configuration, slot_coordinates):
    """Function that translates a combination to their corresponding coordinates"""
    coordinates_for_configuration = []
    for route in configuration:
        coordinates_for_route = []
        for point_on_route in route:
            coordinates_for_route.append(slot_coordinates[point_on_route])

        coordinates_for_configuration.append(coordinates_for_route)

    return coordinates_for_configuration


def orientation(p, q, r):
    """Uses the cross product to determine if q lies to the left or right of the line formed by p and r.
    If the value is 0, it means the points are collinear. If it's positive, q lies to the left, otherwise to the right."""
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val == 0:
        return 0
    return 1 if val > 0 else 2


def do_intersect(x1, y1, x2, y2):
    """Function that checks if two lines intersect"""
    o1 = orientation(x1, y1, x2)
    o2 = orientation(x1, y1, y2)
    o3 = orientation(x2, y2, x1)
    o4 = orientation(x2, y2, y1)

    if o1 != o2 and o3 != o4: #if x1 and y1 are not oriented the same against line 2, they intersect.
        return True
    
    if o1 == 0 or o2 == 0 or o3 == 0 or o4 == 0: #if a point is collinear with the other line
        return True

    return False


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


# FUNCTIONS FOR THE RECTANGLES

def coords_widths(combination, flow_paths,slot_coordinates):
    """Transforms a combination into a tuple with its coordinates and width"""
    coords_widths = []
    for width, path_list in flow_paths:
        coords = combination_to_coordinates(combination,slot_coordinates)
        for i,sublist in enumerate(combination):
            path_in_comb = []
            for item in sublist:
                path_in_comb.append(item[0])
            if path_list == path_in_comb:
                coords_widths.append((coords[i],width))
    return coords_widths


def perpendicular_vector(v):
    return np.array([-v[1], v[0]], dtype=float)


def get_rectangle_corners(point1, point2, width):
    """Turns one segment of a line into a rectangle"""
    v = np.array([point2.x - point1.x, point2.y - point1.y], dtype=float)
    perpendicular = perpendicular_vector(v)
    perpendicular /= np.linalg.norm(perpendicular)
    offset = perpendicular * width / 2

    #points are stored clock wise: left bottom, left up, right up, right bottom
    p1 = Point(point1.x + offset[0], point1.y + offset[1])
    p2 = Point(point2.x + offset[0], point2.y + offset[1])
    p3 = Point(point2.x - offset[0], point2.y - offset[1])
    p4 = Point(point1.x - offset[0], point1.y - offset[1])

    return p1, p2, p3, p4


def line_to_rectangles(line, width):
    """Turns an entire line into a list of rectangles
    A line with three points returns two rectangles"""
    rectangles = []
    for i in range(len(line) - 1):
        p1, p2, p3, p4 = get_rectangle_corners(line[i], line[i+1], width)
        rectangles.append([p1, p2, p3, p4])
    return rectangles


def rectangle_intersection_area(rect1, rect2):
    """Calculate the intersection area between two rectangles."""
    x_overlap = max(0, min(rect1[1].x, rect2[1].x) - max(rect1[0].x, rect2[0].x))
    y_overlap = max(0, min(rect1[1].y, rect2[1].y) - max(rect1[0].y, rect2[0].y))
    return x_overlap * y_overlap


def line_overlap(lines):
    """Calculates how much all the lines overlap"""
    overlaps = 0
    for i, line1 in enumerate(lines):
        total_overlap = 0
        for j, line2 in enumerate(lines):
            if i != j:  # Avoid comparing a line with itself
                for rect1 in line1:
                    for rect2 in line2:
                        total_overlap += rectangle_intersection_area(rect1, rect2)
        overlaps += total_overlap
    return overlaps


def total_area(rectangles):
    """Function that returns the total area of a set of rectangles"""
    tot_area = 0
    for rect in rectangles:
        # Find min and max x and y coordinates
        min_x = min(point.x for point in rect)
        max_x = max(point.x for point in rect)
        min_y = min(point.y for point in rect)
        max_y = max(point.y for point in rect)
        
        # Calculate width and height
        width = max_x - min_x
        height = max_y - min_y
        
        # Calculate area
        area = width * height
        tot_area += area
    return tot_area


def total_overlap_ratio(combination,flow_paths,slot_coordinates):
    """Calculate the ratio of total overlap""" 
    comb_width = coords_widths(combination,flow_paths,slot_coordinates)
    rect_comb = [] # a list of lists with rectangles, representing the lines
    total_overlap = 0
    for line, width in comb_width:
        rectangles = line_to_rectangles(line, width)
        rect_comb.append(rectangles)
        total_overlap += total_area(rectangles)
    return line_overlap(rect_comb) / total_overlap


# may be more interesting to do this differently than just adding them
def score_combination(combination, flow_paths, slot_coordinates):
    """Function that adds up our two constraints to find the combination that minimizes both"""
    intersections = count_intersections(combination_to_coordinates(combination, slot_coordinates))
    overlap_ratio = total_overlap_ratio(combination, flow_paths, slot_coordinates)
    
    score = intersections + overlap_ratio
    return score


def main(path: str = "assets/generated-path.pkl"):
    with open(path, "rb") as f:
        paths = pickle.load(f)

    da = DummyAlgorithm()
    result = da.find_optimal_layout([(2,['Root','A','C']),(1,['Root','A','C','F','G']),(3,['Root','A','C','F','H'])],NODE_COORDINATES)
    print("Right now uses imaginary data (extra imaginary then our generated data)")
    return result


class DummyAlgorithm(LayoutAlgorithm):
    @property
    def name(self) -> str:
        return "dummy"

    def find_optimal_layout(self, flow_paths: FlowPathsT, stations: dict[str, Point]) -> LayoutOutput:
        # Generate slot coordinates
        slot_coordinates = {}
        for station_name, point in stations.items():
            for slot in SLOTS:
                offset_x, offset_y = SLOT_OFFSETS[slot]
                slot_coordinates[(station_name, slot)] = Point(point.x + offset_x, point.y + offset_y)

        # Generate the configurations
        config = generate_configuration(flow_paths)

        # remove the frequency from the flow paths
        pos_comb = list(map(lambda x: list(map(lambda y: y[1],x)), config))

        configuration_dot_product = list(product(*pos_comb))
        wrong_combos = identify_wrong_combos(configuration_dot_product)

        valid_configurations = [element for element in configuration_dot_product if element not in wrong_combos]

        # # for testing
        # print()
        # for comb in valid_configurations:
        #     print("number_of_intersections",count_intersections(combination_to_coordinates(comb, slot_coordinates)))
        #     print("area_of_overlap", total_overlap_ratio(comb,flow_paths,slot_coordinates))
        #     print("layout", list(map(lambda x: (1, x), combination_to_coordinates(comb, slot_coordinates))))
        # print()

        # determines the best combination using the score_combination function
        best_combination = sorted(valid_configurations, key=lambda x: score_combination(x,flow_paths,slot_coordinates))[0]
        return LayoutOutput(
            number_of_intersections=count_intersections(combination_to_coordinates(best_combination, slot_coordinates)),
            area_of_overlap=total_overlap_ratio(best_combination,flow_paths,slot_coordinates),
            layout=list(map(lambda x: (1, x), combination_to_coordinates(best_combination, slot_coordinates)))
        )


if __name__ == "__main__":
    print(main())
