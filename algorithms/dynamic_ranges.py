from utils import Point, LayoutAlgorithm, LayoutOutput, count_intersections, \
    combination_to_coordinates, total_overlap_ratio, combination_to_coordinates_with_width_and_color, bin_frequencies
import numpy as np
import random
import pandas as pd


def generate_slots(test_paths):
    """
    Generates slots given the paths
    """
    max_length = int(len(test_paths) / 2) + 1
    list_of_list = [[(i,i), (i, -i), (-i, i), (-i, -i)] for i in range (1, max_length)]

    flattened_list = [(0, 0)]

    for sublist in list_of_list:
        for tuple_item in sublist:
            flattened_list.append(tuple_item)
    slot_names = ['s{}'.format(i) for i in range(0, len(flattened_list))]
    return list(zip(slot_names, flattened_list))


def calculate_intersections(flow_paths, stations):
    """
    Takes a station, the flowpaths with frequencies and computes the optimal arrangement
    """

    slots = generate_slots(flow_paths)

    data_paths = {
        'Paths': [n[1] for n in flow_paths],
        'Frequency': [n[0] for n in flow_paths],
        'Slot offsets': random.sample(slots, len(flow_paths))
    }

    df_paths = pd.DataFrame(data_paths)

    # Transform offsets to a dictionary
    OFFSETS = df_paths['Slot offsets']
    offset_dict = dict()
    for offset in OFFSETS:
        offset_dict.update({offset[0]: offset[1]})

    # Get slot names
    slot_names = list(offset_dict.keys())

    SLOT_OFFSETS = offset_dict
    SLOTS = slot_names

    # Get slot names
    slot_coordinates = {}

    #Transforms the slot to a location
    for station_name, point in stations.items():
        for slot in SLOTS:
            offset_x, offset_y = SLOT_OFFSETS[slot]
            slot_coordinates[(station_name, slot)] = Point(point.x + offset_x, point.y + offset_y)

    combination_merged = []

    # For each path in the dataframe, it takes the slot offset and takes the name.
    # Then for each element of the path it creates a tuple with both.
    for path in df_paths.iterrows():
        path_list = []
        slot = path[1]['Slot offsets'][0]
        for station in path[1]['Paths']:
            path_list.append((station, slot))
        combination_merged.append(path_list)
    intersections = count_intersections(combination_to_coordinates(combination_merged, slot_coordinates))

    # layout = list(map(lambda x: (1, x), combination_to_coordinates(combination_merged, slot_coordinates)))
    layout = combination_to_coordinates_with_width_and_color(combination_merged, flow_paths, slot_coordinates)

    overlap = total_overlap_ratio(combination_merged, flow_paths, slot_coordinates)

    return intersections, combination_merged, layout, overlap


def dynamic_ranges(flow_paths, stations):
    """
    Takes the coordinates of a station, the paths between computes the optimal arrangement
    """
    #TODO: keep track of used combinations

    paths = flow_paths
    # Initialize iteration counter
    iteration = 0

    # Initialize dictionary with lowest scores
    amount_of_lower_scores = 100
    lowest_scores = {key: 10 for key in range(1000, (1000 + amount_of_lower_scores))}

    # Initialize score ranges
    score_range = 0

    # Compute score range
    search_space = len(paths) * len(paths) * 2 * len(paths)

    # Find the lowest score while ranges don't match
    while max(lowest_scores) > score_range and len(lowest_scores) > 1:

        # Calculate intersections
        intersection_value, combinations, layout, overlap = calculate_intersections(flow_paths, stations)

        # Calculate overlap
        if intersection_value < max(lowest_scores.keys()):
            lowest_scores.pop(max(lowest_scores))
            lowest_scores.update({intersection_value: (combinations, layout)})

        # Decrease size of lowest scores list -> max(lowest scores) becomes smaller
        if iteration in [round(x) for x in np.linspace(1, search_space)]:
            lowest_scores.pop(max(lowest_scores))

        # Increase the score_range
        if iteration in [round(x) for x in np.linspace(1, search_space)]:
            score_range += 1

        iteration += 1

    best_score = min(lowest_scores, key = lowest_scores.get), lowest_scores[min(lowest_scores, key = lowest_scores.get)]
    return best_score[0], best_score[1][0], best_score[1][1], overlap


class DynamicRanges(LayoutAlgorithm):
    @property
    def name(self):
        return 'DynamicRanges'

    def find_optimal_layout(self, flow_paths, stations):
        flow_paths = bin_frequencies(flow_paths, 3)
        intersections_test, paths_dummy, layout, total_overlap = dynamic_ranges(flow_paths, stations)
        return LayoutOutput(
            number_of_intersections=intersections_test,
            area_of_overlap=total_overlap,
            layout=layout
        )