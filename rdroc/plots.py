from dash import Dash, dcc, html, Input, Output
import plotly.express as px

from rdroc.models import StarCluster


def dash_plot(input_dict: dict[str, StarCluster]) -> Dash:

    cluster_names = list(input_dict.keys())

    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div(
                [
                    dcc.Dropdown(
                        cluster_names, "NGC_2360", id="cluster-selection-dropdown"
                    )
                ],
            ),
            html.Div(
                [
                    dcc.Graph(id="spatial-graphic", style={"height": "45vh"}),
                    dcc.Graph(id="pm-graphic", style={"height": "45vh"}),
                ],
                style={"width": "40vw", "display": "inline-block"},
            ),
            html.Div(
                [
                    dcc.Graph(id="cmd-graphic", style={"height": "90vh"}),
                ],
                style={"width": "58vw", "height": "90vh", "display": "inline-block"},
            ),
        ]
    )

    @app.callback(
        Output("spatial-graphic", "figure"),
        Input("cluster-selection-dropdown", "value"),
    )
    def update_figure(selected_cluster: str):
        cluster = input_dict[selected_cluster]
        df = cluster.datatable.to_pandas()
        fig = px.scatter(df, x="RA_ICRS", y="DE_ICRS", hover_name="Gaia")
        fig.update_layout(transition_duration=100)
        return fig

    @app.callback(
        Output("pm-graphic", "figure"),
        Input("cluster-selection-dropdown", "value")
    )
    def update_figure_pm(selected_cluster: str):
        cluster = input_dict[selected_cluster]
        df = cluster.datatable.to_pandas()
        fig = px.scatter(df, x="pmRA_", y="pmDE")
        fig.update_layout(transition_duration=100)
        return fig

    @app.callback(
        Output("cmd-graphic", "figure"),
        Input("cluster-selection-dropdown", "value")
    )
    def update_figure_cmd(selected_cluster: str):
        cluster = input_dict[selected_cluster]
        df = cluster.datatable.to_pandas()
        fig = px.scatter(df, x="BP-RP", y="Gmag")
        fig["layout"]["yaxis"]["autorange"] = "reversed"
        fig.update_layout(transition_duration=100)
        return fig

    return app
