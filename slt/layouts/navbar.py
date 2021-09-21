from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from ..config import _assets_path

# Open the readme for use in the context info
with open(_assets_path / "Howto.md", "r") as f:
    # Using .read rather than .readlines because dcc.Markdown
    # joins list of strings with newline characters
    howto = f.read()

# Buttons
button_gh = dbc.Button(
    "Learn more",
    id="howto-open",
    outline=True,
    color="secondary",
    # Turn off lowercase transformation for class .button in stylesheet
    style={"textTransform": "none"},
)

button_howto = dbc.Button(
    "View Code on github",
    outline=True,
    color="primary",
    href="https://github.com/CHMI-satellite-department/Satellite-labelling-tool",
    id="gh-link",
    style={"text-transform": "none"},
)

# Modal
modal_overlay = dbc.Modal(
    [
        dbc.ModalBody(html.Div([dcc.Markdown(howto, id="howto-md")])),
        dbc.ModalFooter(dbc.Button("Close", id="howto-close", className="howto-bn",)),
    ],
    id="modal",
    size="lg",
    style={"font-size": "small"},
)


# Layout - Navbar
def get_layout(app):
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.A(
                                html.Img(
                                    src=app.get_asset_url("dash-logo-new.png"),
                                    height="30px",
                                ),
                                href="https://plot.ly",
                            )
                        ),
                    ],
                    align="center",
                ),
                dbc.Row(
                    [

                        dbc.Col(dbc.NavbarBrand("Satellite labelling tool", className="ml-2")),
                    ],
                    align="right",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.A(
                                html.Img(
                                    src=app.get_asset_url("CHMI-logo.png"),
                                    height="30px",
                                ),
                                href="https://www.chmi.cz/?l=en",
                            )
                        ),
                        dbc.Col(
                            [
                                dbc.NavbarToggler(id="navbar-toggler"),
                                dbc.Collapse(
                                    dbc.Nav(
                                        [dbc.NavItem(button_howto), dbc.NavItem(button_gh)],
                                        className="ml-auto",
                                        navbar=True,
                                    ),
                                    id="navbar-collapse",
                                    navbar=True,
                                ),
                                modal_overlay,
                            ]
                        ),
                    ],

                ),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-5",
    )


def activate_callbacks(app):
    # TODO comment the dbc link
    # we use a callback to toggle the collapse on small screens
    @app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("modal", "is_open"),
        [Input("howto-open", "n_clicks"), Input("howto-close", "n_clicks")],
        [State("modal", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
