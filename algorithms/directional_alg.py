from utils import Point, LayoutAlgorithm, FlowPathsT, LayoutOutput, SLOTS, count_intersections, total_overlap_ratio, \
    combination_to_coordinates
from path_slot_configuration_generator import generate_configuration
import math
import re

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

    list_of_dict = []

    for key, value in dict_of_paths.items():
        split_key =re.findall('[A-Z][^A-Z]*', key)
        new_dict = {}

        for i in split_key:
            new_dict[i] = value
        list_of_dict.append(new_dict)
    return list_of_dict




def convert_to_list_of_tuples(input_data):
    output_data = []
    for item in input_data:
        new_item = [(k, v) for k, v in item.items()]
        output_data.append(new_item)
    return output_data

def obtain_points_from_keys(combinations, slot_coordinates):
    list_of_paths = []
    for path in combinations:
        list_of_points = []
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
                    # top right
                    max_y_pair_pos_x = max(SLOT_OFFSETS.items(), key=lambda item: item[1][1] if item[1][0] > 0 else float("-inf"))
                    value = SLOT_OFFSETS.pop(max_y_pair_pos_x[0])
                    slot_assigned[key] = max_y_pair_pos_x[0]
                    # print(f"Angle {angle} for key {key} is between 0 and 0.5*pi")

                elif angle > 0.5 * math.pi and angle <= math.pi:
                    #top left
                    max_y_pair_neg_x = max(SLOT_OFFSETS.items(), key=lambda item: item[1][1] if item[1][0] < 0 else float("-inf"))
                    value = SLOT_OFFSETS.pop(max_y_pair_neg_x[0])
                    slot_assigned[key] = max_y_pair_neg_x[0]
                    # print(f"Angle {angle} for key {key} is between 0.5*pi and pi")

                elif angle < 0 and angle >= -0.5 * math.pi:
                    #bot right
                    min_y_pair_pos_x = min(SLOT_OFFSETS.items(), key=lambda item: item[1][1] if item[1][0] > 0 else float("-inf"))
                    value = SLOT_OFFSETS.pop(min_y_pair_pos_x[0])
                    slot_assigned[key] = min_y_pair_pos_x[0]
                    # print(f"Angle {angle} for key {key} is between 0 and -0.5*pi")

                elif angle < -0.5 * math.pi and angle >= -math.pi:
                    #bot left
                    min_y_pair_neg_x = min(SLOT_OFFSETS.items(), key=lambda item: item[1][1] if item[1][0] < 0 else float("-inf"))
                    value = SLOT_OFFSETS.pop(min_y_pair_neg_x[0])
                    slot_assigned[key] = min_y_pair_neg_x[0]
                    # print(f"Angle {angle} for key {key} is between -0.5*pi and -pi")    

        best_stations_with_slots = map_path_keys_to_stations(slot_assigned)
        combination_merged = convert_to_list_of_tuples(best_stations_with_slots)

        combinations_points = obtain_points_from_keys(combination_merged,slot_coordinates)

        intersections = count_intersections(combination_to_coordinates(combination_merged, slot_coordinates))
        overlap = total_overlap_ratio(combination_merged, flow_paths, slot_coordinates)

        layout = list(map(lambda x: (1, x), combinations_points))

        return LayoutOutput(
            number_of_intersections=intersections, 
            area_of_overlap=overlap,
            layout = layout
        )

