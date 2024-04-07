import dataclasses
import random
from pathlib import Path
from urllib.parse import quote

import pydeck as pdk
import pandas as pd
from pydeck import View, ViewState
from pydeck.types import String

from utils import Point, LayoutOutput
UNIT_SCALER = 2
colors = [
    (255, 0, 0),     # Red
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Yellow
    (0, 255, 255),   # Cyan
    (255, 0, 255),   # Magenta
    (128, 0, 0),     # Maroon
    (128, 128, 0),   # Olive
    (0, 128, 0),     # Dark Green
    (128, 0, 128),   # Purple
    (0, 128, 128),   # Teal
    (0, 0, 128),     # Navy
    (255, 165, 0),   # Orange
    (255, 192, 203), # Pink
    (165, 42, 42),   # Brown
    (64, 224, 208),  # Turquoise
    (210, 105, 30),  # Chocolate
    (220, 20, 60)    # Crimson
]


def flow_path_template(width: int, points: [Point]) -> dict:
    color = random.choice(colors)
    colors.remove(color)

    return {
        "name": str(points),
        "color": color,
        "width": width,
        "path": [[point.x * UNIT_SCALER, -point.y * UNIT_SCALER] for point in points]
    }


def render_stations(stations: dict[str, Point]) -> [pdk.Layer]:
    # for each station create 2 diagonal lines that intersect at the station point and are 10 units long
    units = 4
    stations = map(lambda x: [
        # station_name, x, y, ld_x, ld_y, rd_x, rd_y
        x[0], x[1].x * UNIT_SCALER, -x[1].y * UNIT_SCALER, [x[1].x * UNIT_SCALER - units, -x[1].y * UNIT_SCALER - units], [x[1].x * UNIT_SCALER + units, -x[1].y * UNIT_SCALER + units], [x[1].x * UNIT_SCALER + units, -x[1].y * UNIT_SCALER - units], [x[1].x * UNIT_SCALER - units, -x[1].y * UNIT_SCALER + units]
    ], stations.items())


    # Create a data frame
    data = pd.DataFrame(stations, columns=['station_name', 'x', 'y', 'ld_x', 'ld_y', 'rd_x', 'rd_y'])
    return [
        pdk.Layer(
            'PathLayer',
            data,
            get_path='[ld_x, ld_y]',
            get_width=1,
            get_color=[128, 128, 128],
            rounded=True,
        ),
        pdk.Layer(
            'PathLayer',
            data,
            get_path='[rd_x, rd_y]',
            get_width=1,
            get_color=[128, 128, 128],
            rounded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data,
            get_position='[x, y]',
            get_radius=0.5,
            get_fill_color=[72, 72, 72],
        ),
        pdk.Layer(
            'TextLayer',
            data,
            get_position='[x, y]',
            get_text='station_name',
            get_size=12,  # Increase text size
            get_color=[255, 255, 255],
            get_angle=0,
            get_text_anchor=String("middle"),
            get_alignment_baseline=String("center"),
        ),
    ]


def render_flow_paths(data: LayoutOutput):
    # Data from OpenStreetMap, accessed via osmpy
    # svg = """
    #     <svg fill="#000000" height="200px" width="200px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 330 330" xml:space="preserve"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path id="XMLID_222_" d="M250.606,154.389l-150-149.996c-5.857-5.858-15.355-5.858-21.213,0.001 c-5.857,5.858-5.857,15.355,0.001,21.213l139.393,139.39L79.393,304.394c-5.857,5.858-5.857,15.355,0.001,21.213 C82.322,328.536,86.161,330,90,330s7.678-1.464,10.607-4.394l149.999-150.004c2.814-2.813,4.394-6.628,4.394-10.606 C255,161.018,253.42,157.202,250.606,154.389z"></path> </g></svg>
    # """
    #
    # svg_data = "%3Csvg%20fill%3D%22%23000000%22%20height%3D%22200px%22%20width%3D%22200px%22%20version%3D%221.1%22%20id%3D%22Layer_1%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20xmlns%3Axlink%3D%22http%3A%2F%2Fwww.w3.org%2F1999%2Fxlink%22%20viewBox%3D%220%200%20330%20330%22%20xml%3Aspace%3D%22preserve%22%3E%3Cg%20id%3D%22SVGRepo_bgCarrier%22%20stroke-width%3D%220%22%3E%3C%2Fg%3E%3Cg%20id%3D%22SVGRepo_tracerCarrier%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3C%2Fg%3E%3Cg%20id%3D%22SVGRepo_iconCarrier%22%3E%20%3Cpath%20id%3D%22XMLID_222_%22%20d%3D%22M250.606%2C154.389l-150-149.996c-5.857-5.858-15.355-5.858-21.213%2C0.001%20c-5.857%2C5.858-5.857%2C15.355%2C0.001%2C21.213l139.393%2C139.39L79.393%2C304.394c-5.857%2C5.858-5.857%2C15.355%2C0.001%2C21.213%20C82.322%2C328.536%2C86.161%2C330%2C90%2C330s7.678-1.464%2C10.607-4.394l149.999-150.004c2.814-2.813%2C4.394-6.628%2C4.394-10.606%20C255%2C161.018%2C253.42%2C157.202%2C250.606%2C154.389z%22%3E%3C%2Fpath%3E%20%3C%2Fg%3E%3C%2Fsvg%3E"
    #
    # icon_data = {
    #     "url": f'data:image/svg+xml;charset=utf-8,${svg_data}',
    #     "width": 242,
    #     "height": 242,
    #     "anchorY": 0,
    # }

    flow_paths = map(lambda x: flow_path_template(x[0], x[1]), data.layout)

    # Create a data frame
    df = pd.DataFrame.from_records(flow_paths)
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
        rounded=True,
        coodinate_system="CARTESIAN",
    )

    # Add arrow heads to the end of each path
    # end_coordinates = pd.DataFrame(df["path"].apply(lambda x: x[-1]))
    # end_coordinates["icon_data"] = None
    # for i in end_coordinates.index:
    #     end_coordinates["icon_data"][i] = icon_data

    # arrow_layer = pdk.Layer(
    #     type="IconLayer",
    #     data=end_coordinates,
    #     get_icon="icon_data",
    #     get_position="path",
    #     size_scale=15,
    #     icon_size=15,
    #     get_alignment_baseline=String("center"),
    # )


    return [layer]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i: i + 2], 16) for i in (0, 2, 4))


def render(data: LayoutOutput, stations: dict[str, Point], output_path: Path = None):
    if output_path is None:
        output_path = Path("assets/render.html")

    # Define the initial viewport
    view_state = ViewState(target=[0, 0, 0], zoom=2)

    # Root
    root_coordinates = stations["Root"]
    root_circle = pdk.Layer(
        type="ScatterplotLayer",
        data=pd.DataFrame({
            "x": [root_coordinates.x * UNIT_SCALER],
            "y": [-root_coordinates.y * UNIT_SCALER],
        }),
        get_position="[x, y]",
        get_radius=5,
        get_fill_color=(255, 242, 204, 255 * 0.7),
    )

    # Render the flow paths
    flow_paths_layer = render_flow_paths(data)

    # Render the deck
    stations_layers = render_stations(stations)

    view = View(
        type="OrthographicView",
        controller=True
    )

    r = pdk.Deck(layers=[
        root_circle,
        *flow_paths_layer,
        *stations_layers
    ], views=[view], initial_view_state=view_state,  map_provider=None)
    r.to_html(output_path)


if __name__ == "__main__":
    # main()

    points = ['A', 'B', 'C', 'D']

    all_pairs = []
    pairs = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            pairs.append((f"{points[i]}1", f"{points[j]}1"))
            pairs.append((f"{points[i]}1", f"{points[j]}2"))

        for j in range(i + 1, len(points)):
            pairs.append((f"{points[i]}2", f"{points[j]}1"))
            pairs.append((f"{points[i]}2", f"{points[j]}2"))

        print(f"{pairs} => {len(pairs)}")
        all_pairs += pairs
        pairs = []

    print("Total pairs:", len(all_pairs))
    print("Pairs:", all_pairs)