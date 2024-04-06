import dataclasses
import pickle
from itertools import product
import numpy as np

from path_slot_configuration_generator import generate_configuration
from utils import Point, LayoutAlgorithm, FlowPathsT, LayoutOutput, SLOTS, count_intersections, total_overlap_ratio, \
    combination_to_coordinates

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


# may be more interesting to do this differently than just adding them
def score_combination(combination, flow_paths, slot_coordinates):
    """Function that adds up our two constraints to find the combination that minimizes both"""
    intersections = count_intersections(combination_to_coordinates(combination, slot_coordinates))
    overlap_ratio = total_overlap_ratio(combination, flow_paths, slot_coordinates)
    
    score = intersections + overlap_ratio
    return score


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