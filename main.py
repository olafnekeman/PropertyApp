# ---------------------
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import json
import pandas as pd

from support.constants import MAPKEY, BASEPATH
from data.interface import data

token = MAPKEY

# --- Server ---- #
# DO NOT TOUCH!!! #

app = dash.Dash(__name__)

server = app.server

# --- END ---- #
# --- LOADING DATA --- #

fp = BASEPATH + "/data/geodata/gemeentegrenzen_{}.geojson".format(2019)
with open(fp) as f:
    geojson = json.load(f)
lst = []
for i, val in enumerate(geojson['features']):
    lst.append([val['properties']['statcode'], i, i + 1, i + 2])

df = data.data_by_county(year=2019)
candidates = df.columns[98:102]

# --- TEXTS ---- #

intro_text = "Intro, welcome!"
# --- LAYOUT --- #

app.layout = html.Div(
    children=[
        dcc.Store(id="cluster-data-store", data={}),
        # Banner
        html.P("Candidate:"),
        dcc.RadioItems(
            id='candidate',
            options=[{'value': x, 'label': x}
                     for x in candidates],
            value=candidates[0],
            labelStyle={'display': 'inline-block'}
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        html.Div(id="intro-text",
                                 children=dcc.Markdown(intro_text)),
                        html.P("Housing data"),
                        html.Hr(),
                        dcc.Graph(id="choropleth",
                                  figure=px.scatter()
),
                    ],
                    className="eight columns named-card",
                ),
                # Categorical properties by cluster e.g (property type stacked bar)
                html.Div(
                    children=[
                        html.P("Data by year"),
                        html.Hr(),
                        dcc.Graph(id="housing_price", figure=px.scatter()
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
    [Input("candidate", "value")])
def display_choropleth(candidate):
    fig = px.choropleth_mapbox(
        df, geojson=geojson, color=candidate,
        locations="KoppelvariabeleRegioCode_306",
        featureidkey="properties.statcode",
        center={"lat": 52.09, "lon": 5.12}, zoom=6,
        # range_color=[0, 6500]
    )
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_accesstoken=token)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
