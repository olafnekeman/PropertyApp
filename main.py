# ---------------------
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import collections

from support.constants import MAPKEY
from support.functions import col_to_str
from data.interface import db
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

current_map_var, current_map_year, regions = 0, 0, {}


choromap = ChoroMap(runtime_vars=vars)
sub_plot_1 = Subplot(data=data, runtime_vars=vars, show_legend=True)
sub_plot_2 = Subplot(data=data, runtime_vars=vars)
sub_plot_3 = Subplot(data=data, runtime_vars=vars)

# --- TEXTS ---- #

intro_text = "Intro, welcome!"
# Options
# --- LOADING DATA --- #

df = db.data_by_county(year=vars.year)
map_var_options = [dict(label=col_to_str(i), value=i) for i in
                   db.data.columns[4: 200]]

var_options = [dict(label=col_to_str(i), value=i) for i in
               db.data.columns[4: 200]]
year_options = [dict(label=i, value=i) for i in
                db.data['Perioden'].unique()]
# --- LAYOUT --- #

app.layout = html.Div(
    children=[
        dcc.Store(id="session-data", data={}),
        # Banner

        html.Div(
            [
                html.Div(
                    children=[
                        html.P("Housing data"),
                        html.Hr(),
                        dcc.Dropdown(id='memory-countries', options=[
                            {'value': x, 'label': x} for x in regions
                        ], multi=True, value=['GM0503', 'GM0505']),

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

#
# # --- CALLBACKS --- #
# @app.callback(Output('session-data', 'data'),
#               Input('memory-countries', 'value'))
# def filter_countries(countries_selected):
#     if not countries_selected:
#         # Return all the rows on initial load/no country selected.
#         return df.to_dict('records')
#
#     filtered = df.query('country in @countries_selected')
#
#     return filtered.to_dict('records')
#
# @app.callback(Output('memory-table', 'data'),
#               Input('session-data', 'data'))
# def on_data_set_table(data):
#     if data is None:
#         raise PreventUpdate
#
#     return data
#
#
# @app.callback(Output('memory-graph', 'figure'),
#               Input('session-data', 'data'),
#               Input('memory-field', 'value'))
# def on_data_set_graph(data, field):
#     if data is None:
#         raise PreventUpdate
#
#     aggregation = collections.defaultdict(
#         lambda: collections.defaultdict(list)
#     )
#
#     for row in data:
#
#         a = aggregation[row['country']]
#
#         a['name'] = row['country']
#         a['mode'] = 'lines+markers'
#
#         a['x'].append(row[field])
#         a['y'].append(row['year'])
#
#     return {
#         'data': [x for x in aggregation.values()]
#     }
#
#
# @app.callback(
#     Output("choropleth", "figure"),
#     [Input("map_var", "value"),
#      Input("map_year", "value"),
#      Input("choropleth", "clickData")])
# def display_choropleth(map_var, map_year, clickData):
#     if map_var != current_map_var:
#         # Update the variable on the map
#         current_map_var = map_var
#     elif map_year != current_map_year:
#         current_year = map_year
#     elif clickData:
#         # Update the selected regions
#         if clickData is not None:
#             location = clickData['points'][0]['location']
#
#             if location not in current_selections:
#                 current_selections.add(location)
#             else:
#                 current_selections.remove(location)
#         choromap.update_selection()
#     choromap.update_map_data()
#
#     return choromap.fig


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
