import dash
from dash import html
import dash_bootstrap_components as dbc
import numpy as np
import os
from scipy import interpolate

from satdl.datasets import StaticImageFolderDataset

from .utils import dl2np

from .config import _data_path
from .config import _georef
from .config import _image_file_mask

from .layouts import navbar
from .layouts import selection_card
from .layouts import image_annotation_card
from .layouts import annotated_data_card

image_dataloader = StaticImageFolderDataset(
    _data_path,
    file_mask=_image_file_mask,
    georef=_georef,
    max_cache=100
).groupby('datetime', sortby=['datetime', 'product'])


external_stylesheets = [dbc.themes.BOOTSTRAP, os.environ.get('SLT_PREFIX', '') + "assets/image_annotation_style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, url_base_pathname=os.environ.get('SLT_PREFIX'))

server = app.server


data_h, lat_2d, lon_2d = dl2np(image_dataloader[0])
lat_2d_interpolator = interpolate.RectBivariateSpline(
    np.arange(lat_2d.shape[0]),
    np.arange(lat_2d.shape[1]),
    lat_2d,
    kx=1, ky=1  # linear interpolation
)
lon_2d_interpolator = interpolate.RectBivariateSpline(
    np.arange(lon_2d.shape[0]),
    np.arange(lon_2d.shape[1]),
    lon_2d,
    kx=1, ky=1  # linear interpolation
)

app.layout = html.Div(
    [
        navbar.get_layout(app),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(image_annotation_card.get_layout(image_dataloader), md=10),
                        dbc.Col(selection_card.get_layout(image_dataloader=image_dataloader), md=2),
                    ],
                    no_gutters=True, justify="start"
                ),
                dbc.Row(
                    dbc.Col(annotated_data_card.get_layout(image_dataloader), md=10),
                    justify="start"),

            ],
            fluid=True,
        ),
    ]
)

image_annotation_card.activate_callbacks(app, image_dataloader)
annotated_data_card.activate_callbacks(app, image_dataloader, lon_2d_interpolator, lat_2d_interpolator)
selection_card.activate_callbacks(app, image_dataloader)
navbar.activate_callbacks(app)


def run_dev_app(**kwargs):
    app.run_server(debug=True, **kwargs)
