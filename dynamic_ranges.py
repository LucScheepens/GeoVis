from test_data_generator import generate_fake_metro, plot_metro_layout
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

from algo import combination_to_coordinates, count_intersections
from utils import Point, LayoutAlgorithm, FlowPathsT, LayoutOutput, SLOTS

def calculate_intersections(flow_paths, stations):
    """
    Takes a station, the flowpaths with frequencies and computes the optimal arrangement
    """

    slots = generate_slots(flow_paths)

    data_paths = {
    'Paths': [n[1] for n in flow_paths],
    'Frequency': [n[0] for n in flow_paths],
    'Slot offsets': random.sample(slots, 10)
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
    layout = list(map(lambda x: (1, x), combination_to_coordinates(combination_merged, slot_coordinates)))
    return intersections, df_paths, layout



