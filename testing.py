import os
import shutil
import time
from pathlib import Path

import pandas as pd

from algorithms.dummy_algo import DummyAlgorithm
from algorithms.dynamic_ranges import DynamicRanges
from algorithms.directional_alg import DirectionalAlg
from render import render
from test_data_generator import generate_fake_metro, plot_metro_layout
from utils import LayoutAlgorithm

pd.set_option('display.max_columns', None)
ASSET_PATH = Path(__file__).parent / "assets"


def main(
        test_id: str,
        num_of_iterations: int, station_count: int,
        flow_path_count: int,
        max_flow_path_length: int
):
    algorithms: [LayoutAlgorithm] = [
        DynamicRanges(),
        DirectionalAlg(),
        DummyAlgorithm(),
    ]

    test_dir = ASSET_PATH / test_id
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    os.mkdir(test_dir)

    statistics = []

    for n in range(num_of_iterations):
        print(f"🔄 Running iteration {n}...")
        flow_paths, stations, df = generate_fake_metro(
            station_count=station_count,
            flow_path_count=flow_path_count,
            max_flow_path_length=max_flow_path_length,
            min_flow_path_frequency=1,
            max_flow_path_frequency=100
        )

        # Save the metro layout to the file
        plot_metro_layout(df).savefig(test_dir / f"metro-layout-{n}.png")

        print(f"🏃‍ Running algorithms on the generated metro system...")
        for algorithm in algorithms:
            print(f"- Running algorithm {algorithm.name}...", end=" ")
            (test_dir / algorithm.name).mkdir(exist_ok=True)

            # time the algorithm
            start_time = time.time_ns()
            output = algorithm.find_optimal_layout(flow_paths, stations)
            delta_time_ms = (time.time_ns() - start_time) / 1_000_000

            render(output, stations, test_dir / algorithm.name / f"{algorithm.name}-{n}.html")
            statistics.append({
                "algorithm": algorithm.name,
                "iteration": n,
                "intersections": output.number_of_intersections,
                "covered_area": output.area_of_overlap,
                "time_ms": delta_time_ms
            })
            print("✅")

    df = pd.DataFrame(statistics, columns=["algorithm", "iteration", "intersections", "covered_area", "time_ms"])

    # calculate the average of the statistics per algorithm
    avg_df = df.groupby("algorithm").mean()
    avg_df['time_seconds'] = avg_df['time_ms'] / 1_000
    avg_df['time_minutes'] = avg_df['time_seconds'] / 60

    print(avg_df)

    df.to_csv(test_dir / "statistics.csv")


if __name__ == "__main__":
    main(
        "test-2x",
        1,
        15,
        5,
        7
    )
