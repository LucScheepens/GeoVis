import dataclasses
import pickle
from itertools import product

from path_slot_configuration_generator import generate_configuration
from utils import Point, LayoutAlgorithm, FlowPathsT, LayoutOutput, SLOTS

# TODO: Output must include the frequency of each path
# TODO: Number of slots should be calculated dynamically
#       => Another objective is to minimize the number of slots?
# TODO: Slot offsets should be calculated dynamically
# TODO: What is the lines overlap? How to calculate it? -> Optimize the path to minimize the overlap
#  -> E.g. by putting the thick line to side or by changing the slot offset

# TODOL: Add input -> path coordinates

# SLOT_POSITIONS = ['S1', 'S2', 'S3', 'S4', 'S5']
# NODE_COORDINATES = {
#     'Root': Point(0, 0),
#     'A': Point(10, 10),
#     'C': Point(20, 20),
#     'F': Point(30, 30),
#     'G': Point(40, 40),
#     'H': Point(50, 50)
# }
#
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
    # some chatGPT razzle dazzle that calculates the intervals??????
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

    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    if o4 == 0 and on_segment(p2, q1, q2):
        return True

    return False


def on_segment(p, q, r):
    """Function that checks if a point is on a segment"""
    return max(p.x, r.x) >= q.x >= min(p.x, r.x) and max(p.y, r.y) >= q.y >= min(p.y, r.y)


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


def main(path: str = "assets/generated-path.pkl"):
    with open(path, "rb") as f:
        paths = pickle.load(f)

    paths = {('Root', 'A', 'C'): [[('Root', 'S1'), ('A', 'S1'), ('C', 'S1')], [('Root', 'S2'), ('A', 'S2'), ('C', 'S2')], [('Root', 'S3'), ('A', 'S3'), ('C', 'S3')], [('Root', 'S4'), ('A', 'S4'), ('C', 'S4')], [('Root', 'S5'), ('A', 'S5'), ('C', 'S5')]], ('Root', 'A', 'C', 'F', 'G'): [[('Root', 'S1'), ('A', 'S1'), ('C', 'S1'), ('F', 'S1'), ('G', 'S1')], [('Root', 'S2'), ('A', 'S2'), ('C', 'S2'), ('F', 'S2'), ('G', 'S2')], [('Root', 'S3'), ('A', 'S3'), ('C', 'S3'), ('F', 'S3'), ('G', 'S3')], [('Root', 'S4'), ('A', 'S4'), ('C', 'S4'), ('F', 'S4'), ('G', 'S4')], [('Root', 'S5'), ('A', 'S5'), ('C', 'S5'), ('F', 'S5'), ('G', 'S5')]], ('Root', 'A', 'C', 'F', 'H'): [[('Root', 'S1'), ('A', 'S1'), ('C', 'S1'), ('F', 'S1'), ('H', 'S1')], [('Root', 'S2'), ('A', 'S2'), ('C', 'S2'), ('F', 'S2'), ('H', 'S2')], [('Root', 'S3'), ('A', 'S3'), ('C', 'S3'), ('F', 'S3'), ('H', 'S3')], [('Root', 'S4'), ('A', 'S4'), ('C', 'S4'), ('F', 'S4'), ('H', 'S4')], [('Root', 'S5'), ('A', 'S5'), ('C', 'S5'), ('F', 'S5'), ('H', 'S5')]]}

    # configuration_dot_product = list(product(*paths.values()))
    # wrong_combos = identify_wrong_combos(configuration_dot_product)
    #
    # valid_configurations = [element for element in configuration_dot_product if element not in wrong_combos]
    #
    # best_combination = sorted(valid_configurations, key=lambda x: count_intersections(combination_to_coordinates(x)))[0]
    # return combination_to_coordinates(best_combination)


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
        flow_paths = generate_configuration(flow_paths)

        # remove the frequency from the flow paths
        flow_paths = list(map(lambda x: list(map(lambda y: y[1],x)), flow_paths))

        configuration_dot_product = list(product(*flow_paths))
        wrong_combos = identify_wrong_combos(configuration_dot_product)

        valid_configurations = [element for element in configuration_dot_product if element not in wrong_combos]

        best_combination = sorted(valid_configurations, key=lambda x: count_intersections(combination_to_coordinates(x, slot_coordinates)))[0]
        return LayoutOutput(
            number_of_intersections=count_intersections(combination_to_coordinates(best_combination, slot_coordinates)),
            area_of_overlap=0.0, # TODO: Calculate the area of overlap
            layout=list(map(lambda x: (1, x), combination_to_coordinates(best_combination, slot_coordinates)))
        )


if __name__ == "__main__":
    print(main())
