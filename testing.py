import os
from pathlib import Path

import pandas as pd

from algo import DummyAlgorithm, DirectionalAlg
from render import render
from test_data_generator import generate_fake_metro, plot_metro_layout
from utils import LayoutAlgorithm, FlowPathsT, Point, LayoutOutput

ASSET_PATH = Path(__file__).parent / "assets"

def main(
        test_id: str,
        num_of_iterations: int, station_count: int,
        flow_path_count: int,
        max_flow_path_length: int
):
    algorithms: [LayoutAlgorithm] = [ # type: ignore
        DummyAlgorithm(),
        DirectionalAlg()
    ]

    test_dir = ASSET_PATH / test_id
    os.mkdir(test_dir)

    statistics = []

    for n in range(num_of_iterations):
        flow_paths, stations, df = generate_fake_metro(
            station_count=station_count,
            flow_path_count=5,
            max_flow_path_length=3,
            min_flow_path_frequency=1,
            max_flow_path_frequency=1
        )

        # Save the metro layout to the file
        plot_metro_layout(df).savefig(test_dir / f"metro-layout-{n}.png")

        for algorithm in algorithms:
            (test_dir / algorithm.name).mkdir(exist_ok=True)
            output = algorithm.find_optimal_layout(flow_paths, stations)
            render(output, stations, test_dir / algorithm.name / f"{algorithm.name}-{n}.html")
            statistics.append({
                "algorithm": algorithm.name,
                "iteration": n,
                "intersections": output.number_of_intersections,
                "covered_area": output.area_of_overlap,
            })

    df = pd.DataFrame(statistics, columns=["algorithm", "iteration", "intersections", "covered_area"])

    # calculate the average of the statistics per algorithm
    avg_df = df.groupby("algorithm").mean()
    print(avg_df)

    df.to_csv(test_dir / "statistics.csv")


if __name__ == "__main__":
    main(
        "test-4",
        1,
        26,
        10,
        5
    )
