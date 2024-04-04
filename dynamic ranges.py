import random
import pandas as pd

def create_combination(paths, slots):
    """
    Creates a random combination of order and slots with the paths
    """

    combination = []

    # Pick a random path and a random slot and add it to combinations
    for c in range(len(paths)):
        path = random.choice(paths)
        paths.remove(path)
        slot = random.choice(slots)
        slots.remove(slot)
        combination.append([(station, slot) for station in path])

    return combination

def dynamic_ranges(coordinates, slots, paths):
    """
    Takes the coordinates of a station, the paths between computes the optimal arrangement
    """
    #TODO: keep track of used combinations
    #TODO: compute intersection value
    #TODO: make the iteration dependend on the search space

    # Initialize iteration counter
    iteration = 0
    
    # Initialize dictionary with lowest scores
    amount_of_lower_scores = 100
    lowest_scores = {key: 1000 for key in range(amount_of_lower_scores)}

    # Initialize score ranges
    score_range = 0

    # Initialize decreasing rates
    rate_lowest_scores = 10
    rate_score_range = 10

    # Compute score range
    search_space = len(slots) * len(paths) * len(paths)

    # Find the lowest score while ranges don't match
    while lowest_scores[max(lowest_scores, key = lowest_scores.get)] > score_range and len(lowest_scores) > 1:

        combinations = create_combination(paths, slots)
        intersection_value = 10

        if intersection_value < max(lowest_scores.values()):
            key = ""
            for combo in combinations:
                combo = dict(combo)
                key = "".join(combo.keys()) + list(combo.values())[0] + key
            lowest_scores.update({key: intersection_value})

        if iteration % rate_lowest_scores == 0:
            lowest_scores.pop(max(lowest_scores, key = lowest_scores.get))

        if iteration % rate_score_range == 0:
            score_range += 1

        iteration += 1

    return min(lowest_scores, key = lowest_scores.get), lowest_scores[min(lowest_scores, key = lowest_scores.get)]

dynamic_ranges([], ['s1', 's2', 's3'], [['Root', 'A', 'B', 'C', 'D', 'E'], ['Root', 'A'], ['Root', 'B', 'E']])
