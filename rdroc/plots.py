from dash import Dash, dcc, html, Input, Output, dash_table
import numpy as np
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
                        cluster_names, "NGC_2360", id="cluster-selection-dropdown", style={"width": "70vw"}
                    ),
                ],
            ),
            html.Div(
                [
                    dcc.Graph(id="spatial-graphic", style={"height": "40vh"}),
                    dcc.Graph(id="pm-graphic", style={"height": "40vh"}),
                ],
                style={"width": "40vw", "display": "inline-block"},
            ),
            html.Div(
                [
                    dcc.Graph(id="cmd-graphic", style={"height": "80vh"}),
                ],
                style={"width": "58vw", "height": "80vh", "display": "inline-block"},
            ),
            html.Div(
                [
                    html.Button("Download Plots", id="btn-download-plots", style={"width": "10vw"}),
                    dcc.Download(id="download-plots")
                ]
            ),
            html.Div(id="table-cluster-params", style={"overflow": "scroll"}),
        ]
    )

    def get_figure(df, x_col, y_col, selectedpoints, selectedpoints_local):
        """Get figure based on selected points. Extracted from https://dash.plotly.com/interactive-graphing"""

        fig = px.scatter(df, x=df[x_col], y=df[y_col])
        fig.update_traces(
            selectedpoints=selectedpoints,
            customdata=df.index,
            marker={"opacity": 0.9},
            unselected={
                "marker": {"opacity": 0.1},
            },
        )

        return fig

    @app.callback(
        Output("spatial-graphic", "figure"),
        Output("pm-graphic", "figure"),
        Output("cmd-graphic", "figure"),
        Output("table-cluster-params", "children"),
        Input("cluster-selection-dropdown", "value"),
        Input("spatial-graphic", "selectedData"),
        Input("pm-graphic", "selectedData"),
        Input("cmd-graphic", "selectedData"),
    )
    def update_figure(
        selected_cluster, spatial_selected_data, pm_selected_data, cmd_selected_data
    ):
        cluster = input_dict[selected_cluster]
        df = cluster.datatable.to_pandas()
        df = df.rename(columns={"pmRA": "pmRA_", "GaiaDR2": "Gaia", "GaiaEDR3": "Gaia"})
        selectedpoints = df.index
        for selected_data in [
            spatial_selected_data,
            pm_selected_data,
            cmd_selected_data,
        ]:
            if selected_data and selected_data["points"]:
                selectedpoints = np.intersect1d(
                    selectedpoints, [p["customdata"] for p in selected_data["points"]]
                )

        # Reverse axis for CMD plot
        fig3 = get_figure(df, "BP-RP", "Gmag", selectedpoints, spatial_selected_data)
        fig3["layout"]["yaxis"]["autorange"] = "reversed"

        # Create datatable
        dfp = cluster.paramtable.to_pandas()
        dt = dash_table.DataTable(
            data=dfp.to_dict("records"),
            columns=[
                {
                    "name": i,
                    "id": i,
                }
                for i in dfp.columns
            ],
        )

        return [
            get_figure(df, "RA_ICRS", "DE_ICRS", selectedpoints, spatial_selected_data),
            get_figure(df, "pmRA_", "pmDE", selectedpoints, spatial_selected_data),
            fig3,
            dt,
        ]

    @app.callback(
        Output("download-plots", "data"),
        Input("btn-download-plots", "n_clicks"),
        prevent_initial_call=True,
    )
    def get_plots(n_clicks):
        return dict(content="TEST", filename="test.txt")

    return app
