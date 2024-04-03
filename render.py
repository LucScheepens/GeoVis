import dataclasses
import random

import pydeck as pdk
import pandas as pd
from pydeck import View, ViewState
from pydeck.types import String

from utils import Point


def path_template(name: str, points: [Point]) -> dict:
    color = "%06x" % random.randint(0, 0xFFFFFF)
    return {
        "name": name,
        "color": str(color),
        "width": random.randint(1, 3),
        "path": [[point.x, point.y] for point in points]
    }


STATIONS = [
    [0, 0, 'Amsterdam'],  # Point 1
    [10, 10, 'Bosssing'],  # Point 2
    [20, 10, 'Chiki'],  # Point 3
]

# DIJKSTRA_OUTPUT = [
#     [Point(x=-1, y=1), Point(x=9, y=11), Point(x=19, y=21), Point(x=29, y=31), Point(x=39, y=41)],
#     [Point(x=1, y=1), Point(x=11, y=11), Point(x=21, y=21), Point(x=31, y=31), Point(x=51, y=51)],
#     [Point(x=0, y=0), Point(x=10, y=10), Point(x=20, y=20)],
# ]
# DIJKSTRA_OUTPUT = [[Point(x=0, y=0), Point(x=10, y=10), Point(x=20, y=20)], [Point(x=-1, y=1), Point(x=9, y=11), Point(x=19, y=21), Point(x=29, y=31), Point(x=39, y=41)], [Point(x=1, y=-1), Point(x=11, y=9), Point(x=21, y=19), Point(x=31, y=29), Point(x=51, y=49)]]
DIJKSTRA_OUTPUT = [[Point(x=0, y=0), Point(x=10, y=10), Point(x=20, y=20)], [Point(x=-1, y=1), Point(x=9, y=11), Point(x=19, y=21), Point(x=29, y=31), Point(x=39, y=41)], [Point(x=1, y=-1), Point(x=11, y=9), Point(x=21, y=19), Point(x=31, y=29), Point(x=51, y=49)]]
PATHS = [path_template(str(i), path) for i, path in enumerate(DIJKSTRA_OUTPUT)]


def render_stations() -> [pdk.Layer]:
    # Create a data frame
    data = pd.DataFrame(STATIONS, columns=['x', 'y', 'station'])

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
            get_text='station',
            get_size=12,  # Increase text size
            get_color=[0, 0, 0, 255],  # Set color to black
            get_angle=0,
            get_text_anchor=String("middle"),
            get_alignment_baseline=String("center"),
        )
    ]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i: i + 2], 16) for i in (0, 2, 4))


def main():
    # Define a list of coordinates for the tube line

    # Create a data frame
    df = pd.DataFrame.from_records(PATHS)
    df["color"] = df["color"].apply(hex_to_rgb)

    # DATA_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/bart-lines.json"
    # df = pd.read_json(DATA_URL)
    # df["color"] = df["color"].apply(hex_to_rgb)

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

    # Define the initial viewport
    view_state = ViewState(target=[0, 0, 0], zoom=2)

    # Render the deck
    [stations_circle, stations_text] = render_stations()
    # view_state = pdk.ViewState(latitude=37.782556, longitude=-122.3484867, zoom=10)

    view = View(
        type="OrthographicView",
        controller=True
    )

    r = pdk.Deck(layers=[
        layer,
        stations_circle,
        stations_text,
    ], views=[view], initial_view_state=view_state,  map_provider=None)
    r.to_html('assets/render.html')


if __name__ == "__main__":
    main()

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