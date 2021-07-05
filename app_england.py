import collections
import os
import sys
import time
import json
import random
import logging
from copy import copy, deepcopy

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import plotly
import plotly.graph_objs as go
import plotly.express as px
from plotly.graph_objs import Scatter, Figure, Layout
from plotly.subplots import make_subplots
from flask_caching import Cache
from support.constants import MAPKEY
from support.functions import col_to_str
from data.interface import db
from support.settings import map_columns

import numpy as np
import pandas as pd

import warnings

from ui.choromap import ChoroMap

warnings.filterwarnings("ignore")

""" ----------------------------------------------------------------------------
 Configurations
---------------------------------------------------------------------------- """
cfg = dict()

cfg['start_year'] = 2020
cfg['end_year'] = 2021

cfg['Years'] = list(range(cfg['start_year'], cfg['end_year'] + 1))
cfg['latest date'] = "31 May 2020"

# When running in Pythonanywhere
appDataPath = '/home/olafnekeman/apps-UK_houseprice/appData'
assetsPath = '/home/olafnekeman/apps-UK_houseprice/assets'

if os.path.isdir(appDataPath):
    cfg['app_data_dir'] = appDataPath
    cfg['assets dir'] = assetsPath
    cfg['cache dir'] = 'cache'

# when running locally
else:
    cfg['app_data_dir'] = 'appData'
    cfg['assets dir'] = 'assets'
    cfg['cache dir'] = '/tmp/cache'

cfg['topN'] = 10

cfg['timeout'] = 5 * 60  # Used in flask_caching
cfg['cache threshold'] = 10000  # corresponds to ~350MB max

cfg['logging format'] = 'pid %(process)5s [%(asctime)s] ' + \
                        '%(levelname)8s: %(message)s'

# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#
logging.basicConfig(format=cfg['logging format'], level=logging.INFO)
logging.info(f"System: {sys.version}")

t0 = time.time()

""" ----------------------------------------------------------------------------
 House Price Data
---------------------------------------------------------------------------- """
data = db.get_region_data(col_str=", ".join(map_columns))

""" ----------------------------------------------------------------------------
 Geo Data
---------------------------------------------------------------------------- """
geojson = dict()
for i in range(2020, 2021):
    geojson[i] = ChoroMap.get_geojson(year=i)

regional_geojson = dict()

for feature in geojson[2020]['features']:
    fid = feature['properties']['statcode']
    regional_geojson[fid] = feature

""" --------------------------------------------------------------------------
App Options
-------------------------------------------------------------------------- """
year = 2020
var = 'gemiddelde_woningwaarde_99'

region_options = [
    dict(label=row['regio_s'], value=row['koppelvariabele_regio_code_306'])
    for i, row in data.loc[data['perioden'] == year].iterrows() if
    row['koppelvariabele_regio_code_306'] != 'None']

""" ----------------------------------------------------------------------------
 Making Graphs
---------------------------------------------------------------------------- """


def get_Choropleth(df, geo_data, arg, marker_opacity,
                   marker_line_width, marker_line_color, fig=None):
    if fig is None:
        fig = go.Figure()

    fig.add_trace(
        go.Choroplethmapbox(
            geojson=geo_data,
            locations=df['koppelvariabele_regio_code_306'],
            featureidkey="properties.statcode",
            colorscale=arg['colorscale'],
            z=df[arg['z_vec']],
            text=df[arg['text_vec']],
            hoverinfo="text",
            marker_opacity=marker_opacity,
            marker_line_width=marker_line_width,
            marker_line_color=marker_line_color,
            colorbar_title=arg['title'],
        )
    )
    return fig


# --------------------------------------------#

def get_figure(df, geo_data, geo_sectors):
    """ ref: https://plotly.com/python/builtin-colorscales/
    """
    config = {
        'doubleClickDelay': 1000}  # Set a high delay to make double click easier

    arg = dict()
    arg['z_vec'] = var
    arg['text_vec'] = 'regio_s'
    arg['colorscale'] = "Picnic"
    arg['title'] = "Avg. Price %Change"

    # -------------------------------------------#
    # Main Choropleth:
    fig = get_Choropleth(df, geo_data, arg, marker_opacity=0.4,
                         marker_line_width=1, marker_line_color='#6666cc')

    # ------------------------------------------#
    """
    mapbox_style options:
    'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter',
    'stamen-terrain', 'stamen-toner', 'stamen-watercolor'
    """
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=6,
                      autosize=True,
                      font=dict(color="#7FDBFF"),
                      paper_bgcolor="#1f2630",
                      mapbox_center={"lat": 52.09, "lon": 5.12},
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      uirevision='constant'
                      )

    # -------------------------------------------#
    # Highlight selections:
    if len(geo_sectors.keys()) > 0:
        fig = get_Choropleth(df, geo_sectors, arg, marker_opacity=1.0,
                             marker_line_width=3, marker_line_color='aqua',
                             fig=fig)

    return fig


fig_init = get_figure(df=data.loc[data['perioden'] == year],
                      geo_data=geojson[year],
                      geo_sectors=dict())

""" ----------------------------------------------------------------------------
 App Settings
---------------------------------------------------------------------------- """

colors = {
    'background': '#1F2630',
    'text': '#7FDBFF'
}

""" ----------------------------------------------------------------------------
 Dash App
---------------------------------------------------------------------------- """
# Select theme from: https://www.bootstrapcdn.com/bootswatch/

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport",
         "content": "width=device-width, initial-scale=1.0"}
    ],
    external_stylesheets=[dbc.themes.DARKLY]
    # external_stylesheets = [dbc.themes.CYBORG]
)

server = app.server  # Needed for gunicorn
cache = Cache(server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': cfg['cache dir'],
    'CACHE_THRESHOLD': cfg['cache threshold']
})
app.config.suppress_callback_exceptions = True

# --------------------------------------------------------#

app.layout = html.Div(
    id="root",

    children=[
        dcc.Store(id='memory-output'),
        # Selection control -------------------------------------#
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='postcode',
                    options=region_options,
                    # value=region_options[100],
                    clearable=True,
                    multi=True,
                    style={'color': 'black'}),
            ], style={'display': 'inline-block',
                      'padding': '0px 5px 10px 0px',
                      'width': '40%'},
                className="seven columns"
            ),
            # html.Div([
            #     dbc.RadioItems(
            #         id='graph-type',
            #         options=[{'label': i, 'value': i} for i in ['Price', 'Volume', 'Yr-to-Yr price ±%']],
            #         value='Price',
            #         inline=True)
            #     ], style={'display': 'inline-block',
            #               'textAlign': 'center',
            #               'padding': '5px 0px 10px 10px',
            #               'width': '33%'},
            #       className="two columns"
            # ),

        ], style={'padding': '5px 0px 10px 20px'},
            className="row"
        ),

        # App Container ------------------------------------------#
        html.Div(
            id="app-container",
            children=[
                # Left Column ------------------------------------#
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="choropleth-container",
                            children=[
                                html.Div([
                                    html.Div([
                                        html.H5(id="choropleth-title"),
                                    ], style={'display': 'inline-block',
                                              'width': '64%'},
                                        className="eight columns"
                                    ),
                                ]),
                                dcc.Graph(id="choropleth", figure=fig_init),
                            ],
                        ),
                    ], style={'display': 'inline-block',
                              'padding': '20px 10px 10px 40px',
                              'width': "40%"},
                    className="five columns"
                ),

                        # Right Column ------------------------------------#
                        html.Div(
                            id="graph-container",
                            children=[
                                html.Div([dcc.Graph(id='price-time-series')]),

                            ], style={'display': 'inline-block',
                                      'padding': '20px 20px 10px 10px',
                                      'width': '39%'},
                               className="five columns"
                        ),
            ],
            className="row"
        ),
    ]
)

""" ----------------------------------------------------------------------------
 Callback functions:
 Overview:
 region, year, graph-type, school -> choropleth-title
 region, year -> postcode options
 region, year, graph-type, postcode-value, school -> choropleth
 postcode-value, property-type-checklist -> price-time-series
 choropleth-clickData, choropleth-selectedData, region, postcode-State
                                                        -> postcode-value
---------------------------------------------------------------------------- """

# ----------------------------------------------------#

""" Update choropleth-graph with year, region, graph-type update & sectors
"""


@app.callback(
    Output('choropleth', 'figure'),
    Input('postcode', 'value'))  # @cache.memoize(timeout=cfg['timeout'])
def update_Choropleth(sectors):
    # Graph type selection------------------------------#
    df = data.loc[data['perioden'] == year]
    # For high-lighting mechanism ----------------------#
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    geo_sectors = dict()

    if sectors is not None:
        for k in geojson[year].keys():
            if k != 'features':
                geo_sectors[k] = geojson[year][k]
            else:
                geo_sectors[k] = [regional_geojson[sector] for sector in
                                  sectors]

    # Updating figure ----------------------------------#
    fig = get_figure(df=df, geo_data=geojson[year], geo_sectors=geo_sectors)

    return fig

@app.callback(Output('memory-output', 'data'),
              Input('postcode', 'value'))
def filter_countries(postcodes):
    if not postcodes:
        # Return all the rows on initial load/no country selected.
        return {}

    filtered = data.query('koppelvariabele_regio_code_306 in @postcodes')

    return filtered.to_dict('records')

@app.callback(
    Output('price-time-series', 'figure'),
    Input('memory-output', 'data'))
def on_data_set_graph(data):
    if len(data) == 0:
        raise PreventUpdate
    aggregation = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    field=var
    for row in data:

        a = aggregation[row['regio_s']]

        a['name'] = row['regio_s']
        a['mode'] = 'lines+markers'

        a['x'].append(row['perioden'])
        a['y'].append(row[field])

    return {
        'data': [x for x in aggregation.values()]
    }

# #----------------------------------------------------#
#
# """ Update postcode dropdown values with clickData, selectedData and region
# """
@app.callback(
    Output('postcode', 'value'),
    [Input('choropleth', 'clickData'),
     Input('choropleth', 'selectedData'),
     State('postcode', 'value')])
def update_postcode_dropdown(clickData, selectedData, postcodes):
    # Logic for initialisation or when Schoold sre selected
    if dash.callback_context.triggered[0]['value'] is None:
        return postcodes
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # --------------------------------------------#

    if 'selectedData' in changed_id:
        postcodes = [D['location'] for D in
                     selectedData['points'][:cfg['topN']]]
    elif clickData is not None and 'location' in clickData['points'][0]:
        sector = clickData['points'][0]['location']
        if postcodes is None:
            return [sector]
        elif sector in postcodes:
            postcodes.remove(sector)
        elif len(postcodes) < cfg['topN']:
            postcodes.append(sector)
    return postcodes


#
# #----------------------------------------------------#
#
# app.css.append_css({
#     'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# })

logging.info(f'Data Preparation completed in {time.time() - t0 :.1f} seconds')

# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#

if __name__ == "__main__":
    logging.info(sys.version)

    # If running locally in Anaconda env:
    if 'conda-forge' in sys.version:
        app.run_server(debug=True)

    # If running on AWS/Pythonanywhere production
    else:
        app.run_server(
            port=8050,
            host='0.0.0.0'
        )

""" ----------------------------------------------------------------------------
Terminal cmd to run:
gunicorn app:server -b 0.0.0.0:8050
---------------------------------------------------------------------------- """
