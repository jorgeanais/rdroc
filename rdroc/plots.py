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
                        cluster_names, "NGC_2360", id="cluster-selection-dropdown"
                    )
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
                    dcc.Dropdown(id ='cmd_xaxis_selector-dropdown', options=['BP-RP', 'Gmag'], value='BP-RP', style={"width": "40vw"}),
                    dcc.Dropdown(id ='cmd_yaxis_selector-dropdown', options=['BP-RP', 'Gmag'], value='Gmag', style={"width": "40vw"}),
                ],
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
        Output("cmd_xaxis_selector-dropdown", "options"),
        Output("cmd_yaxis_selector-dropdown", "options"),
        Input("cluster-selection-dropdown", "value"),
        Input("spatial-graphic", "selectedData"),
        Input("pm-graphic", "selectedData"),
        Input("cmd-graphic", "selectedData"),
        Input("cmd_xaxis_selector-dropdown", "value"),
        Input("cmd_yaxis_selector-dropdown", "value"),
    )
    def update_figure(
        selected_cluster, spatial_selected_data, pm_selected_data, cmd_selected_data, cmd_xaxis, cmd_yaxis
    ):
        cluster = input_dict[selected_cluster]
        df = cluster.datatable.to_pandas()
        df = df.rename(columns={"pmRA": "pmRA_"})
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
        fig3 = get_figure(df, cmd_xaxis, cmd_yaxis, selectedpoints, spatial_selected_data)
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

        # Available columns in datatable to plot
        data_columns = [{'label' :k, 'value' :k} for k in df.columns]

        return [
            get_figure(df, "RA_ICRS", "DE_ICRS", selectedpoints, spatial_selected_data),
            get_figure(df, "pmRA_", "pmDE", selectedpoints, spatial_selected_data),
            fig3,
            dt,
            data_columns,
            data_columns
        ]
    

    return app
