import pathlib
import pickle
from typing import Literal, Union, List, Tuple

SlotPosition = str
AVAILABLE_SLOTS: list[str] = ["S1", "S2", "S3", "S4", "S5"]


def load_paths() -> dict[tuple[SlotPosition, ...], list[list[tuple[str, SlotPosition]]]]:
    with open("assets/generated-path.pkl", "rb") as f:
        return pickle.load(f)


def generate_combinations(paths_reminder: tuple) -> list[list[tuple[str, SlotPosition]]]:
    if not paths_reminder:
        return [[]]

    result = []
    current_station_name, new_paths_reminder = paths_reminder[0], paths_reminder[1:]
    for slot in AVAILABLE_SLOTS:
        reminder = generate_combinations(new_paths_reminder)
        result.extend([
            [(current_station_name, slot)] + r for r in reminder
        ])

    return result


def generate_paths(paths: list[Union[tuple[str, ...], list[str, ...]]]):
    # Convert the paths to tuple if they are not
    # So we can use them as dictionary keys
    if any(isinstance(path, list) for path in paths):
        paths = [tuple(path) for path in paths]

    # Variant A: Starting slot is same as ending slot
    # Generate all possible paths from the start to the end for each slot at given station
    generated_paths = {}
    for path in paths:
        generated_paths[path] = []
        for slot in AVAILABLE_SLOTS:
            path_with_slots = []
            for station in path:
                path_with_slots.append((station, slot))

            generated_paths[path].append(path_with_slots)

    return generated_paths
    # for path, slots in generated_paths.items():
    #     print(f"Path {path}: {slots}")

    # Variant B: Starting slot is might different from ending slot
    # Generate all possible paths from the start to the end for each slot at given station
    # Really slow -> it's better to increase the number of available slots
    # for path in paths:
    #     generated_paths = generate_combinations(path)
    #     print(f"Generated paths: {paths[-1]} - {generated_paths}")


def main():
    # paths = [
    #     ('Root', 'A', 'C'),
    #     ('Root', 'A', 'C', 'F', 'G'),
    #     ('Root', 'A', 'C', 'F', 'H'),
    #     ('Root', 'B'),
    #     ('Root', 'D', 'E'),
    #     ('Root', 'D', 'G', 'F')
    # ]

    paths = [
        ['Root', 'A', 'C'],
        ['Root', 'A', 'C', 'F', 'G'],
        ['Root', 'A', 'C', 'F', 'H'],
        ['Root', 'B'],
        ['Root', 'D', 'E'],
        ['Root', 'D', 'G', 'F']
    ]

    generated_paths = generate_paths(paths)

    this_file = pathlib.Path(__file__).resolve().parent
    with open(this_file / "assets/generated-path.pkl", "wb") as f:
        pickle.dump(generated_paths, f)
        print("💾 Generated paths are saved to assets/generated-path.pkl")

    loaded_paths = load_paths()
    assert loaded_paths == generated_paths  # Check if the loaded paths are the same as the generated paths

    print(loaded_paths)


if __name__ == "__main__":
    main()
