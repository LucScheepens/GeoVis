import dataclasses
import random
from pathlib import Path

import pydeck as pdk
import pandas as pd
from pydeck import View, ViewState
from pydeck.types import String

from utils import Point, LayoutOutput


def flow_path_template(width: int, points: [Point]) -> dict:
    color = "%06x" % random.randint(0, 0xFFFFFF)
    return {
        "name": str(points),
        "color": str(color),
        "width": width,
        "path": [[point.x, point.y] for point in points]
    }


# STATIONS = [
#     [0, 0, 'Amsterdam'],  # Point 1
#     [10, 10, 'Bosssing'],  # Point 2
#     [20, 10, 'Chiki'],  # Point 3
# ]
#
# # DIJKSTRA_OUTPUT = [
# #     [Point(x=-1, y=1), Point(x=9, y=11), Point(x=19, y=21), Point(x=29, y=31), Point(x=39, y=41)],
# #     [Point(x=1, y=1), Point(x=11, y=11), Point(x=21, y=21), Point(x=31, y=31), Point(x=51, y=51)],
# #     [Point(x=0, y=0), Point(x=10, y=10), Point(x=20, y=20)],
# # ]
# # DIJKSTRA_OUTPUT = [[Point(x=0, y=0), Point(x=10, y=10), Point(x=20, y=20)], [Point(x=-1, y=1), Point(x=9, y=11), Point(x=19, y=21), Point(x=29, y=31), Point(x=39, y=41)], [Point(x=1, y=-1), Point(x=11, y=9), Point(x=21, y=19), Point(x=31, y=29), Point(x=51, y=49)]]
# # DIJKSTRA_OUTPUT = [[Point(x=0, y=0), Point(x=10, y=10), Point(x=20, y=20)], [Point(x=-1, y=1), Point(x=9, y=11), Point(x=19, y=21), Point(x=29, y=31), Point(x=39, y=41)], [Point(x=1, y=-1), Point(x=11, y=9), Point(x=21, y=19), Point(x=31, y=29), Point(x=51, y=49)]]
# # PATHS = [path_template(str(i), path) for i, path in enumerate(DIJKSTRA_OUTPUT)]


def render_stations(stations: dict[str, Point]) -> [pdk.Layer]:
    stations = map(lambda x: [x[0], x[1].x, x[1].y], stations.items())

    # Create a data frame
    data = pd.DataFrame(stations, columns=['station_name', 'x', 'y'])

    return [
        pdk.Layer(
            'ScatterplotLayer',
            data,
            get_position='[x, y]',
            get_radius=0.5,
            get_fill_color=[255, 255, 0],
            pickable=True,
        ),
        pdk.Layer(
            'TextLayer',
            data,
            get_position='[x, y]',
            get_text='station_name',
            get_size=12,  # Increase text size
            get_color=[0, 0, 0, 255],  # Set color to black
            get_angle=0,
            get_text_anchor=String("middle"),
            get_alignment_baseline=String("center"),
        )
    ]


def render_flow_paths(data: LayoutOutput) -> pdk.Layer:
    flow_paths = map(lambda x: flow_path_template(x[0], x[1]), data.layout)

    # Create a data frame
    df = pd.DataFrame.from_records(flow_paths)
    df["color"] = df["color"].apply(hex_to_rgb)

    # Define a line layer
    layer = pdk.Layer(
        type="PathLayer",
        data=df,
        pickable=True,
        get_color="color",
        width_unit='"pixels"',
        width_min_pixels="width",
        width_max_pixels="width",
        get_width="width",
    )

    return layer


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i: i + 2], 16) for i in (0, 2, 4))


def render(data: LayoutOutput, stations: dict[str, Point], output_path: Path = None):
    if output_path is None:
        output_path = Path("assets/render.html")


    # Define the initial viewport
    view_state = ViewState(target=[0, 0, 0], zoom=2)

    # Render the flow paths
    flow_paths_layer = render_flow_paths(data)

    # Render the deck
    [stations_circle, stations_text] = render_stations(stations)

    view = View(
        type="OrthographicView",
        controller=True
    )

    r = pdk.Deck(layers=[
        flow_paths_layer,
        stations_circle,
        stations_text,
    ], views=[view], initial_view_state=view_state,  map_provider=None)
    r.to_html(output_path)


# if __name__ == "__main__":
    # main()

    # points = ['A', 'B', 'C', 'D']
    #
    # all_pairs = []
    # pairs = []
    # for i in range(len(points)):
    #     for j in range(i + 1, len(points)):
    #         pairs.append((f"{points[i]}1", f"{points[j]}1"))
    #         pairs.append((f"{points[i]}1", f"{points[j]}2"))
    #
    #     for j in range(i + 1, len(points)):
    #         pairs.append((f"{points[i]}2", f"{points[j]}1"))
    #         pairs.append((f"{points[i]}2", f"{points[j]}2"))
    #
    #     print(f"{pairs} => {len(pairs)}")
    #     all_pairs += pairs
    #     pairs = []
    #
    # print("Total pairs:", len(all_pairs))
    # print("Pairs:", all_pairs)