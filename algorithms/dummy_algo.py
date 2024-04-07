from itertools import product

from algorithms.dynamic_ranges import generate_slots
from path_slot_configuration_generator import generate_configuration
from utils import Point, LayoutAlgorithm, FlowPathsT, LayoutOutput, count_intersections, total_overlap_ratio, \
    combination_to_coordinates

# Done: Output must include the frequency of each path
# TODO: Number of slots should be calculated dynamically
#       => Another objective is to minimize the number of slots?
# TODO: Slot offsets should be calculated dynamically
# Done: What is the lines overlap? How to calculate it?
# TODO: Optimize the path to minimize the overlap
#  -> E.g. by putting the thick line to side or by changing the slot offset


def contains_equals(route1, route2):
    """A function that checks for two segments if they use the same slot at the same node"""
    for node1, slot1 in route1:
        for node2, slot2 in route2:
            if node1 == node2 and slot1 == slot2:
                return True

    return False


def select_valid_configurations(dot_product) -> list:
    """filter out combinations that have paths use the same slot at the same node"""
    # to_reject = set()
    to_keep = []
    for configuration in dot_product:
        for i in range(len(configuration)):
            for j in range(i+1, len(configuration)):
                if not contains_equals(configuration[i], configuration[j]):
                    to_keep.append(configuration)

    return to_keep


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
        # slot_coordinates = {}
        # for station_name, point in stations.items():
        #     for slot in SLOTS:
        #         offset_x, offset_y = SLOT_OFFSETS[slot]
        #         slot_coordinates[(station_name, slot)] = Point(point.x + offset_x, point.y + offset_y)

        # Generate the slots
        slots_with_coordinates = generate_slots(flow_paths)

        # Extract the slot names
        slots = list(map(lambda x: x[0], slots_with_coordinates))

        # Generate the slot offsets
        slot_coordinates = {}
        for station_name, point in stations.items():
            for slot_name, slot_pos in slots_with_coordinates:
                slot_coordinates[(station_name, slot_name)] = Point(point.x + slot_pos[0], point.y + slot_pos[1])

        # Generate the configurations
        config = generate_configuration(flow_paths, slots)

        # remove the frequency from the flow paths
        pos_comb = list(map(lambda x: list(map(lambda y: y[1],x)), config))

        configuration_dot_product = list(product(*pos_comb))
        valid_configurations = select_valid_configurations(configuration_dot_product)

        best_combination = min(valid_configurations, key=lambda x: score_combination(x, flow_paths, slot_coordinates))

        return LayoutOutput(
            number_of_intersections=count_intersections(combination_to_coordinates(best_combination, slot_coordinates)),
            area_of_overlap=total_overlap_ratio(best_combination,flow_paths,slot_coordinates),
            layout=list(map(lambda x: (1, x), combination_to_coordinates(best_combination, slot_coordinates)))
        )