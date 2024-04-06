import dataclasses
import pickle
from itertools import product
import math

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
        # return valid_configurations

        best_combination = sorted(valid_configurations, key=lambda x: count_intersections(combination_to_coordinates(x, slot_coordinates)))[0]
        return LayoutOutput(
            number_of_intersections=count_intersections(combination_to_coordinates(best_combination, slot_coordinates)),
            area_of_overlap=0.0, # TODO: Calculate the area of overlap
            layout=list(map(lambda x: (1, x), combination_to_coordinates(best_combination, slot_coordinates)))
        )

   
def calc_angles(flow_paths, station_coords):
    list_of_angles_pos = {}
    list_of_angles_neg = {}
    for path in flow_paths:
        start_point = station_coords[path[1][0]]
        end_point = station_coords[path[1][-1]]
        angle_between_start_end = start_point.angle_with(end_point)
        path_key = ''.join(path[1])

        if angle_between_start_end >= 0: 
            list_of_angles_pos[path_key] = angle_between_start_end
        else:
            list_of_angles_neg[path_key] = angle_between_start_end
            
    return [list_of_angles_pos, list_of_angles_neg]

def generate_slots(list_of_angles):
    max_length = 0
    SLOT_OFFSETS = {}

    for angle in list_of_angles:
        if len(angle) >= max_length:
            max_length = len(angle)
    list_of_list = [[(i,i), (i, -i), (-i, i), (-i, -i)] for i in range (1,max_length)]
    flattened_list = [(0,0)]

    for sublist in list_of_list:
        for tuple_item in sublist:
            flattened_list.append(tuple_item)

    for i in range(2*max_length):
        SLOT_OFFSETS[f'S{i}'] = flattened_list[i]

    return SLOT_OFFSETS

def generate_slots_labels(N):
    return [f"S{i}" for i in range(1, N+1)]

def map_path_keys_to_stations(dict_of_paths):
    import re

    list_of_dict = []

    for key, value in dict_of_paths.items():
        split_key =re.findall('[A-Z][^A-Z]*', key)
        new_dict = {}

        for i in split_key:
            new_dict[i] = value
        list_of_dict.append(new_dict)
    return list_of_dict

import random
import pandas as pd


def convert_to_list_of_tuples(input_data):
    output_data = []
    for item in input_data:
        new_item = [(k, v) for k, v in item.items()]
        output_data.append(new_item)
    return output_data

def obtain_points_from_keys(combinations, slot_coordinates):
    list_of_points, list_of_paths = [],[]
    for path in combinations:
        for slot in path:
            list_of_points.append(slot_coordinates[slot])
        list_of_paths.append(list_of_points)
    return list_of_paths

class DirectionalAlg(LayoutAlgorithm):
    @property
    def name(self) -> str:
        return "directional"
    
    def find_optimal_layout(self, flow_paths: FlowPathsT, stations: dict[str, Point]):
        station_coords = {}
        slot_coordinates = {}

        for name_station, point in stations.items():
            station_coords[name_station] = Point(point.x, point.y)
        list_of_angles = calc_angles(flow_paths, station_coords)

        SLOT_OFFSETS = generate_slots(list_of_angles)

        for station_name, point in stations.items():
            for slot, offset in SLOT_OFFSETS.items():
                offset_x, offset_y = SLOT_OFFSETS[slot]
                slot_coordinates[(station_name, slot)] = Point(point.x + offset_x, point.y + offset_y)
        # return slot_coordinates
        slot_assigned = {}
        # print(list_of_angles)
        for i in range(2):
            my_dict = list_of_angles[i]
            sorted_dict = dict(sorted(my_dict.items(), key=lambda item: item[1], reverse=True))

            for key, angle in sorted_dict.items():
                    if angle >= 0 and angle <= 0.5 * math.pi:
                        max_y_pair_pos_x = max(SLOT_OFFSETS.items(), key=lambda item: item[1][1] if item[1][0] > 0 else float("-inf"))
                        value = SLOT_OFFSETS.pop(max_y_pair_pos_x[0])
                        slot_assigned[key] = max_y_pair_pos_x[0]
                        # print(f"Angle {angle} for key {key} is between 0 and 0.5*pi")

                    elif angle >= 0.5 * math.pi and angle <= math.pi:
                        max_y_pair_neg_x = max(SLOT_OFFSETS.items(), key=lambda item: item[1][1] if item[1][0] < 0 else float("-inf"))
                        value = SLOT_OFFSETS.pop(max_y_pair_neg_x[0])
                        slot_assigned[key] = max_y_pair_neg_x[0]
                        # print(f"Angle {angle} for key {key} is between 0.5*pi and pi")

                    elif angle < 0 and angle >= -0.5 * math.pi:
                        min_y_pair_pos_x = min(SLOT_OFFSETS.items(), key=lambda item: item[1][1] if item[1][0] > 0 else float("-inf"))
                        value = SLOT_OFFSETS.pop(min_y_pair_pos_x[0])
                        slot_assigned[key] = min_y_pair_pos_x[0]
                        # print(f"Angle {angle} for key {key} is between 0 and -0.5*pi")

                    elif angle < -0.5 * math.pi and angle >= -math.pi:
                        min_y_pair_neg_x = min(SLOT_OFFSETS.items(), key=lambda item: item[1][1] if item[1][0] < 0 else float("-inf"))
                        value = SLOT_OFFSETS.pop(min_y_pair_neg_x[0])
                        slot_assigned[key] = min_y_pair_neg_x[0]
                        # print(f"Angle {angle} for key {key} is between -0.5*pi and -pi")    

        best_stations_with_slots = map_path_keys_to_stations(slot_assigned)
        combination_merged = convert_to_list_of_tuples(best_stations_with_slots)
        print(combination_merged)

        #TODO fix deze functie call, hij maakt teveel punten, kut python
        combinations_points = obtain_points_from_keys(combination_merged,slot_coordinates)
        print(combinations_points)
        intersections = count_intersections(combination_to_coordinates(combination_merged, slot_coordinates))

        layout = list(map(lambda x: (1, x), combinations_points))
        print(f'layout is equal to {layout}')
        # return combination_merged
        return LayoutOutput(
            number_of_intersections=intersections, 
            area_of_overlap=0,
            layout = layout
        )


if __name__ == "__main__":
    print(main())
