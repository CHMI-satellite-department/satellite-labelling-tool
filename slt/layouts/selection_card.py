from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from ..utils import frame_timestamp

from ..config import DEFAULT_ATYPE
from ..config import annotation_types


def get_layout(image_dataloader, **kwargs):
    return dbc.Card(
        [
            # dbc.CardHeader(html.H2("Annotated data")),
            dbc.CardBody(
                [
                    dbc.Row(
                        dbc.Col(
                            [
                                html.H5("Choose phenomena"),
                                dcc.Dropdown(
                                    id="annotation-type-dropdown",
                                    options=[
                                        {"label": t, "value": t} for t in annotation_types
                                    ],
                                    value=DEFAULT_ATYPE,
                                    clearable=False,
                                ),
                            ],
                            align="center",
                        )
                    ),
                ]
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        dbc.Col(
                            [
                                html.H6("Label maker"),
                                dcc.Input(id="annotator-name-input", type="text", placeholder="Type your name"
                                          ),
                            ],
                            align="center",
                        )
                    ),
                ]
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        dbc.Col(
                            [
                                html.H5("Current frame"),
                                html.Div(id="frame-description-datetime",
                                         children=frame_timestamp(image_dataloader, 0)),
                            ],
                            align="center",
                        )
                    ),
                ]
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        dbc.Col(
                            [
                                html.H6("Composites"),
                                html.Div(
                                    dash_table.DataTable(
                                        id="frame-description-composites",
                                        columns=[{'name': 'col0', 'id': 'col0'},
                                                 {'name': 'col1', 'id': 'col1'}],
                                        data=get_image_composites(image_dataloader, 0),
                                        css=[
                                            {
                                                'selector': 'tr:first-child',
                                                'rule': 'display: none',
                                            },
                                        ],
                                        style_cell={'textAlign': 'center'},
                                    ),
                                    style={'margin-top': '0.5em'}
                                )
                            ],
                            align='center'
                        )
                    ),
                ]
            ),
            dbc.CardFooter(
                [
                    html.Div(
                        [
                            # We use this pattern because we want to be able to download the
                            # annotations by clicking on a button
                            html.A(
                                id="download",
                                download="annotations.json",
                                # make invisble, we just want it to click on it
                                style={"display": "none"},
                            ),
                            dbc.Button(
                                "Download annotations", id="download-button", outline=True,
                            ),
                            html.Div(id="dummy", style={"display": "none"}),
                            dbc.Tooltip(
                                "You can download the annotated data in a .json format by clicking this button",
                                target="download-button",
                            ),
                        ],
                    )
                ]
            ),

        ]
    )


def get_image_composites(image_dataloader, i):
    composites = [im.attrs.get('product', '??') for im in image_dataloader[i]]
    return [{'col0': composites[0], 'col1': composites[1]},
            {'col0': composites[2], 'col1': composites[3]}]


def activate_callbacks(app, image_dataloader):
    @app.callback(
        Output("frame-description-datetime", "children"),
        Input("graph", "figure"),
        State("image-files", "data")
    )
    def update_datetime_label(fig, image_files_data):
        return frame_timestamp(image_dataloader, image_files_data["current"])
