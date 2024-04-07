from utils import SlotPosition, FlowPathsT, FlowPathsWithSlotsT


def generate_combinations_variant_b(paths_reminder: tuple, slots: [str]) -> list[list[tuple[str, SlotPosition]]]:
    if not paths_reminder:
        return [[]]

    result = []
    current_station_name, new_paths_reminder = paths_reminder[0], paths_reminder[1:]
    for slot in slots:
        reminder = generate_combinations_variant_b(new_paths_reminder)
        result.extend([
            [(current_station_name, slot)] + r for r in reminder
        ])

    return result


def generate_configuration(paths: FlowPathsT, slots: [str]) -> FlowPathsWithSlotsT:
    # Convert the paths to tuple if they are not
    # So we can use them as dictionary keys
    # if any(isinstance(path, list) for path in paths):
    #     paths = [tuple(path) for path in paths]

    # Variant A: Starting slot is same as ending slot
    # Generate all possible paths from the start to the end for each slot at given station
    result: FlowPathsWithSlotsT = []
    for frequency, path, color in paths:
        intermediate_res = []
        for slot in slots:
            path_with_slots = []
            for station in path:
                path_with_slots.append((station, slot))

            intermediate_res.append((frequency, path_with_slots, color))

        result.append(intermediate_res)

    return result
    # for path, slots in generated_paths.items():
    #     print(f"Path {path}: {slots}")

    # Variant B: Starting slot is might different from ending slot
    # Generate all possible paths from the start to the end for each slot at given station
    # Really slow -> it's better to increase the number of available slots
    # for path in paths:
    #     generated_paths = generate_combinations(path)
    #     print(f"Generated paths: {paths[-1]} - {generated_paths}")
