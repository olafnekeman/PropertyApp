# ---------------------
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import json
import pandas as pd

from support.constants import MAPKEY, BASEPATH
from support.functions import col_to_str
from data.interface import data
from ui.runtime_vars import RuntimeVars
from ui.side_bar import Subplot
from ui.choromap import ChoroMap

token = MAPKEY

# --- Server ---- #
# DO NOT TOUCH!!! #

app = dash.Dash(__name__)

server = app.server

# --- END ---- #

# --- RUNTIME VARIABLES --- #

vars = RuntimeVars()

choromap = ChoroMap(runtime_vars=vars)
sub_plot_1 = Subplot(data=data, runtime_vars=vars, show_legend=True)
sub_plot_2 = Subplot(data=data, runtime_vars=vars)
sub_plot_3 = Subplot(data=data, runtime_vars=vars)

# --- TEXTS ---- #

intro_text = "Intro, welcome!"
# Options
# --- LOADING DATA --- #

df = data.data_by_county(year=vars.year)
map_var_options = [dict(label=col_to_str(i), value=i) for i in
                   data.data.columns[4: 200]]

var_options = [dict(label=col_to_str(i), value=i) for i in
               data.data.columns[4: 200]]
year_options = [dict(label=i, value=i) for i in
                data.data['Perioden'].unique()]
# --- LAYOUT --- #

app.layout = html.Div(
    children=[
        dcc.Store(id="cluster-data-store", data={}),
        # Banner

        html.Div(
            [
                html.Div(
                    children=[
                        html.P("Housing data"),
                        html.Hr(),
                        html.Div(
                            children=[
                                dcc.Dropdown(
                                    id="map_year",
                                    options=year_options,
                                    value=year_options[-2]['value'],
                                    className="four columns named-card",
                                ),
                                dcc.Dropdown(
                                    id='map_var',
                                    options=map_var_options,
                                    value=map_var_options[0]['value'],
                                    className="four columns named-card",
                                ),
                            ],
                        ),
                        dcc.Graph(id="choropleth",
                                  figure=choromap.fig,
                                  className="twelve columns named-card",
                                  ),
                    ],
                    className="eight columns named-card",
                ),

                # Side bar with yearly graphs.
                html.Div(
                    children=[
                        html.P("Data by year"),
                        html.Hr(),
                        dcc.Dropdown(
                            id="side_bar_var_1",
                            options=var_options,
                            value=var_options[0]['value'],
                            className="eight columns named-card",
                        ),
                        dcc.Graph(
                            id="yearly_data_1",
                            figure=sub_plot_1.fig,
                            className="twelve columns named-card",),
                        html.Hr(),
                        dcc.Dropdown(
                            id="side_bar_var_2",
                            options=var_options,
                            value=var_options[0]['value'],
                            className="eight columns named-card",
                        ),
                        dcc.Graph(
                            id="yearly_data_2",
                            figure=sub_plot_2.fig,
                            className="twelve columns named-card",),
                        html.Hr(),
                        dcc.Dropdown(
                            id="side_bar_var_3",
                            options=var_options,
                            value=var_options[0]['value'],
                            className="eight columns named-card",
                        ),
                        dcc.Graph(
                            id="yearly_data_3",
                            figure=sub_plot_3.fig,
                            className="twelve columns named-card",
                        ),
                    ],
                    className="four columns named-card",
                ),

            ],
            className="twelve columns",
        ),
    ],
    className="container twelve columns",
)


# --- CALLBACKS --- #
@app.callback(
    Output("choropleth", "figure"),
    [Input("map_var", "value"),
     Input("map_year", "value"),
     Input("choropleth", "clickData")])
def display_choropleth(map_var, map_year, clickData):
    if map_var != vars.map_var:
        # Update the variable on the map
        vars.map_var = map_var
    elif map_year != vars.year:
        vars.year = map_year
    elif clickData:
        # Update the selected regions
        if clickData is not None:
            location = clickData['points'][0]['location']

            if location not in vars.selections:
                vars.selections.add(location)
            else:
                vars.selections.remove(location)
        choromap.update_selection()
    choromap.update_map_data()

    return choromap.fig


@app.callback(
    Output("yearly_data_1", "figure"),
    [Input("side_bar_var_1", "value"),
     Input("choropleth", "clickData")]
)
def update_side_bar_plot_1(side_bar_var_1, clickData):
    if side_bar_var_1 != sub_plot_1.subplot_var:
        sub_plot_1.subplot_var = side_bar_var_1
    else:
        pass
        # sub_plot_1.update_traces()
    return sub_plot_1.plot()


@app.callback(
    Output("yearly_data_2", "figure"),
    [Input("side_bar_var_2", "value"),
     Input("choropleth", "clickData")]
)
def update_side_bar_plot_2(side_bar_var_2, clickData):
    if side_bar_var_2 != sub_plot_2.subplot_var:
        sub_plot_2.subplot_var = side_bar_var_2
    else:
        pass
        # sub_plot_2.update_traces()
    return sub_plot_2.plot()


@app.callback(
    Output("yearly_data_3", "figure"),
    [Input("side_bar_var_3", "value"),
     Input("choropleth", "clickData")]
)
def update_side_bar_plot_3(side_bar_var_3, clickData):
    if side_bar_var_3 != sub_plot_3.subplot_var:
        sub_plot_3.subplot_var = side_bar_var_3
    else:
        pass
        # sub_plot_3.update_traces()
    return sub_plot_3.plot()


if __name__ == "__main__":
    app.run_server(debug=True)
