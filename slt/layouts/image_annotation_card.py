import dash
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px

from ..config import _projection
from ..config import color_dict
from ..config import DEFAULT_ATYPE
from ..config import SHAPE_PRECISION

from ..utils import dl2np
from ..utils import time_passed
from ..utils import frame_timestamp


# Cards
def get_layout(image_dataloader, **kwargs):
    return dbc.Card(
        id="imagebox",
        children=[
            # dbc.CardHeader(html.H3("Annotation area")),
            dbc.CardBody(
                [

                    dbc.ButtonGroup(
                        [
                            dbc.Button("Previous", id="previous", outline=True),
                            dbc.Button("Next", id="next", outline=True),
                        ],
                        size="sm",
                        # style={"width": "100%"},
                    ),

                    dcc.Graph(
                        id="graph",
                        figure=make_facet_fig(image_dataloader, 0),
                        config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
                        style={'width': '100%', 'height': '85vh'}
                    ),

                ]
            ),
        ], style={"horizontalAlign": "left"}
    )


def activate_callbacks(app, image_dataloader):
    @app.callback(
        [Output("graph", "figure"), Output("annotations-store", "data"), ],
        [Input("annotations-table", "data"), Input("annotation-type-dropdown", "value")],
        [State("image-files", "data"), State("annotations-store", "data")],
    )
    def send_figure_to_graph(
            annotations_table_data, annotation_type, image_files_data, annotations_store
    ):
        if annotations_table_data is not None:
            timestamp = frame_timestamp(image_dataloader, image_files_data["current"])
            # convert table rows to those understood by fig.update_layout
            fig_shapes = [table_row_to_shape(sh) for sh in annotations_table_data]
            # find the shapes that are new
            new_shapes_i = []
            old_shapes_i = []
            for i, sh in enumerate(fig_shapes):
                if not shape_in(annotations_store[timestamp]["shapes"])(sh):
                    new_shapes_i.append(i)
                else:
                    old_shapes_i.append(i)
            # add timestamps to the new shapes
            for i in new_shapes_i:
                fig_shapes[i]["timestamp"] = time_passed(annotations_store["starttime"])
            # find the old shapes and look up their timestamps
            for i in old_shapes_i:
                old_shape_i = index_of_shape(
                    annotations_store[timestamp]["shapes"], fig_shapes[i]
                )
                fig_shapes[i]["timestamp"] = annotations_store[timestamp]["shapes"][
                    old_shape_i
                ]["timestamp"]
            shapes = fig_shapes

            fig = make_facet_fig(image_dataloader, image_files_data["current"], shapes=shapes,
                                 annotation_type=annotation_type)

            annotations_store[timestamp]["shapes"] = shapes
            return (fig, annotations_store)
        return dash.no_update


def make_facet_fig(image_dataloader, i: int, shapes=None, annotation_type=DEFAULT_ATYPE):
    data, lat, lon = dl2np(image_dataloader[i])
    fig = px.imshow(data, facet_col=0, binary_string=True,
                    facet_col_wrap=2, facet_row_spacing=0.0001, facet_col_spacing=0.01,
                    origin="lower", aspect='auto')
    for anno in fig['layout']['annotations']:
        anno['text'] = ''
        anno['height'] = 1.01

    fig['layout'].update(margin=dict(l=0, r=0, b=0, t=30))

    if shapes is not None:
        fig.update_layout(
            shapes=[shape_data_remove_not_shape_parameters(sh) for sh in shapes]
        )
    fig.update_layout(
        # reduce space between image and graph edges
        newshape_line_color=color_dict[annotation_type],
        yaxis=dict(
            title_text="",
            titlefont=dict(size=1),
        ),
        xaxis=dict(
            title_text="",
            titlefont=dict(size=1),
        ),
        xaxis2=dict(
            title_text="",
            titlefont=dict(size=1),
        ),
        yaxis3=dict(
            title_text="",
            titlefont=dict(size=1),
        )
        # dragmode="drawrect",
    )
    fig['layout']['uirevision'] = 'some-constant'

    return fig


def shape_data_remove_not_shape_parameters(shape):
    """
    go.Figure complains if we include the 'timestamp' key when updating the
    figure
    """
    new_shape = dict()
    for k in shape.keys() - set(["timestamp", "x_center", "y_center", "annotator", "lon0", "lon1", "lat0", "lat1",
                                 "lon_center", "lat_center", "label", "projection"]):
        new_shape[k] = shape[k]
    return new_shape


def table_row_to_shape(tr):
    return {
        "editable": True,
        "xref": tr["XREF"],
        "yref": tr["YREF"],
        "layer": "above",
        "opacity": 1,
        "line": {"color": color_dict[tr["label"]], "width": 4, "dash": "solid"},
        "fillcolor": "rgba(0, 0, 0, 0)",
        "fillrule": "evenodd",
        "type": "rect",
        "x0": tr["X0"],
        "y0": tr["Y0"],
        "x1": tr["X1"],
        "y1": tr["Y1"],
        "x_center": tr["Xcenter"],
        "y_center": tr["Ycenter"],
        "annotator": tr["annotator"],
        "lon0": tr["lon0"],
        "lat0": tr["lat0"],
        "lon1": tr["lon1"],
        "lat1": tr["lat1"],
        "lon_center": tr["lon_center"],
        "lat_center": tr["lat_center"],
        "label": tr["label"],
        "projection": _projection
    }


def shape_cmp(s0, s1):
    """ Compare two shapes """
    return (
            (round(s0["x0"], SHAPE_PRECISION) == round(s1["x0"], SHAPE_PRECISION))
            and (round(s0["x1"], SHAPE_PRECISION) == round(s1["x1"], SHAPE_PRECISION))
            and (round(s0["y0"], SHAPE_PRECISION) == round(s1["y0"], SHAPE_PRECISION))
            and (round(s0["y1"], SHAPE_PRECISION) == round(s1["y1"], SHAPE_PRECISION))
            and (s0["line"]["color"] == s1["line"]["color"])
    )


def shape_in(se):
    """ check if a shape is in list (done this way to use custom compare) """
    return lambda s: any(shape_cmp(s, s_) for s_ in se)


def index_of_shape(shapes, shape):
    for i, shapes_item in enumerate(shapes):
        if shape_cmp(shapes_item, shape):
            return i
    raise ValueError  # not found
