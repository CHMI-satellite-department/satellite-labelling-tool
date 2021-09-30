import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import re

from ..utils import frame_timestamp, time_passed

from ..config import annotation_types, columns
from ..config import color_dict
from ..config import download_columns
from ..config import type_dict


def get_layout(image_dataloader):
    return dbc.Card(
        [
            dbc.CardHeader(html.H2("Annotated data")),
            dbc.CardBody(
                [
                    dbc.Row(dbc.Col(html.H3("Coordinates of annotations"))),
                    dbc.Row(
                        dbc.Col(
                            [
                                dash_table.DataTable(
                                    id="annotations-table",
                                    columns=[
                                        dict(
                                            name=n,
                                            id=n,
                                            presentation=(
                                                "dropdown" if n == "label" else "input"
                                            )
                                        ) if isinstance(n, str) else n
                                        for n in columns
                                    ],
                                    editable=False,
                                    style_data={"height": 40},
                                    style_cell={
                                        "overflow": "hidden",
                                        "textOverflow": "ellipsis",
                                        "maxWidth": 0,
                                    },
                                    dropdown={
                                        "label": {
                                            "options": [
                                                {"label": o, "value": o}
                                                for o in annotation_types
                                            ],
                                            "clearable": False,
                                        }
                                    },
                                    style_cell_conditional=[
                                        {"if": {"column_id": "label"}, "textAlign": "left", 'width': '20%'}
                                    ],
                                    fill_width=True,
                                ),
                                dcc.Store(
                                    id="annotations-store",
                                    data=dict(
                                        **{
                                            frame_timestamp(image_dataloader, i): {"shapes": []}
                                            for i in range(len(image_dataloader))
                                        },
                                        **{"starttime": time_passed()}
                                    ),
                                ),
                                dcc.Store(
                                    id="download-store",
                                    data=dict(
                                        **{
                                            frame_timestamp(image_dataloader, i): {"shapes": []}
                                            for i in range(len(image_dataloader))
                                        }
                                    ),
                                ),
                                dcc.Store(
                                    id="image-files",
                                    data={"current": 0, "n_files": len(image_dataloader)},
                                ),
                            ],
                        ),
                    ),

                ]
            ),

        ],
    )


def activate_callbacks(app, image_dataloader, lon_interpolator, lat_interpolator):
    @app.callback(
        Output("download-store", "data"),
        Input("annotations-store", "data")
    )
    def convert_download_data(annotations_data):
        def filter_download_fields(fields):
            return [{k: v for k, v in field.items() if k in download_columns}
                    for field in fields]
        return {k: filter_download_fields(v.get('shapes', [])) for k, v in annotations_data.items() if k != "starttime"}

    # set the download url to the contents of the annotations-store (so they can be
    # downloaded from the browser's memory)
    app.clientside_callback(
        """
    function(the_store_data) {
        let s = JSON.stringify(the_store_data);
        let b = new Blob([s],{type: 'text/plain'});
        let url = URL.createObjectURL(b);
        return url;
    }
    """,
        Output("download", "href"),
        [Input("download-store", "data")],
    )

    # click on download link via button
    app.clientside_callback(
        """
    function(download_button_n_clicks)
    {
        let download_a=document.getElementById("download");
        download_a.click();
        return '';
    }
    """,
        Output("dummy", "children"),
        [Input("download-button", "n_clicks")],
    )

    @app.callback(
        [Output("annotations-table", "data"), Output("image-files", "data")],
        [
            Input("previous", "n_clicks"),
            Input("next", "n_clicks"),
            Input("graph", "relayoutData"),
        ],
        [
            State("annotations-table", "data"),
            State("image-files", "data"),
            State("annotations-store", "data"),
            # State("annotation-type-dropdown", "value"),
            State("annotator-name-input", "value"),
        ],
    )
    def modify_table_entries(
            previous_n_clicks,
            next_n_clicks,
            graph_relayout_data,
            annotations_table_data,
            image_files_data,
            annotations_store_data,
            # annotation_type,
            annotator_name,
    ):
        cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
        if cbcontext == "graph.relayoutData":
            if "shapes" in graph_relayout_data.keys():
                # this means all the shapes have been passed to this function via
                # graph_relayout_data, so we store them
                annotations_table_data = [
                    shape_to_table_row(sh, annotator_name,
                                       lon_interpolator=lon_interpolator,
                                       lat_interpolator=lat_interpolator)
                    for sh in graph_relayout_data["shapes"]
                ]
                # add annotator
            elif re.match(r"shapes\[[0-9]+\].x0", list(graph_relayout_data.keys())[0]):
                # this means a shape was updated (e.g., by clicking and dragging its
                # vertices), so we just update the specific shape
                annotations_table_data = annotations_table_shape_resize(
                    annotations_table_data, graph_relayout_data,
                    lon_interpolator=lon_interpolator,
                    lat_interpolator=lat_interpolator
                )
            if annotations_table_data is None:
                return dash.no_update
            else:
                return annotations_table_data, image_files_data
        image_index_change = 0
        if cbcontext == "previous.n_clicks":
            image_index_change = -1
        if cbcontext == "next.n_clicks":
            image_index_change = 1
        image_files_data["current"] += image_index_change
        image_files_data["current"] %= image_files_data["n_files"]
        if image_index_change != 0:
            # image changed, update annotations_table_data with new data
            annotations_table_data = []
            for sh in annotations_store_data[frame_timestamp(image_dataloader, image_files_data["current"])]["shapes"]:
                annotations_table_data.append(shape_to_table_row(sh,
                                                                 annotator_name,
                                                                 lon_interpolator=lon_interpolator,
                                                                 lat_interpolator=lat_interpolator))
            return annotations_table_data, image_files_data
        else:
            return dash.no_update


def coord_to_tab_column(coord):
    return coord.upper()


def annotations_table_shape_resize(annotations_table_data, fig_data, lon_interpolator, lat_interpolator):
    """
    Extract the shape that was resized (its index) and store the resized
    coordinates.
    """
    shapes = {}
    for key in fig_data.keys():
        shape_nb, coord = key.split(".")
        # shape_nb is for example 'shapes[2].x0': this extracts the number
        shape_nb = int(shape_nb.split(".")[0].split("[")[-1].split("]")[0])
        # this should correspond to the same row in the data table
        # we have to format the float here because this is exactly the entry in
        # the table
        # (no need to compute a time stamp, that is done for any change in the
        # table values, so will be done later)
        shapes.setdefault(shape_nb, {v: annotations_table_data[shape_nb][coord_to_tab_column(v)]
                                     for v in ['x0', 'y0', 'x1', 'y1', 'xref', 'yref']})
        shapes[shape_nb]['line'] = {'color': color_dict[annotations_table_data[shape_nb]['label']]}
        shapes[shape_nb][coord] = fig_data[key]
    for index, shape in shapes.items():
        annotations_table_data[index] = shape_to_table_row(
            shape,
            annotator_name=shape.get('annotator', ''),
            lon_interpolator=lon_interpolator,
            lat_interpolator=lat_interpolator
        )
    return annotations_table_data


def shape_to_table_row(sh, annotator_name, lon_interpolator, lat_interpolator):
    x0, y0, x1, y1 = (float(sh[key]) for key in ['x0', 'y0', 'x1', 'y1'])
    xc = (x0 + x1)/2
    yc = (y0 + y1)/2

    return {
        "label": type_dict[sh["line"]["color"]],
        "XREF": sh["xref"],
        "YREF": sh["yref"],
        "X0": x0,
        "Y0": y0,
        "X1": x1,
        "Y1": y1,
        "Xcenter": xc,
        "Ycenter": yc,
        "annotator": annotator_name,
        "lon0": lon_interpolator(y0, x0)[0][0],
        "lat0": lat_interpolator(y0, x0)[0][0],
        "lon1": lon_interpolator(y1, x1)[0][0],
        "lat1": lat_interpolator(y1, x1)[0][0],
        "lon_center": lon_interpolator(yc, xc)[0][0],
        "lat_center": lat_interpolator(yc, xc)[0][0]
    }
