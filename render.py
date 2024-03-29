import pydeck as pdk
import pandas as pd
from pydeck import View, ViewState
from pydeck.types import String


def renderStations() -> [pdk.Layer]:
    # Define a text layer for the station labels
    coordinates = [
        [0, 0, 'Amsterdam'],  # Point 1
        [10, 10, 'Bosssing'],  # Point 2
        [20, 10, 'Chiki'],  # Point 3
    ]

    # Create a data frame
    data = pd.DataFrame(coordinates, columns=['x', 'y', 'station'])

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
    paths = [
        {
            "name": "Richmond - Millbrae",
            "color": "#ed1c24",
            "width": 1,
            "path": [
                [0, 0],  # Point 1
                [10, 10],  # Point 2
                [20, 10],  # Point 3
            ]
        },
        {
            "name": "Richmond - Millbrae2",
            "color": "#4924ff",
            "width": 1,
            "path": [
                [-2, 2],  # Point 1
                [10-2, 10+2],  # Point 2
                [20+2, 10+2],  # Point 3
            ]
        }
    ]

    # Create a data frame
    df = pd.DataFrame.from_records(paths)
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
    [stations_circle, stations_text] = renderStations()
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
