import collections
import dash
import pandas as pd

from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

import dash_html_components as html
import dash_core_components as dcc
import dash_table

from data.interface import db
from support.functions import col_to_str
from support.settings import map_columns

app = dash.Dash(__name__)

df = db.get_region_data(col_str=", ".join(map_columns))

countries = set(df['regio_s'])

map_var_options = [dict(label=col_to_str(i), value=i) for i in
                   map_columns]

app.layout = html.Div([
    dcc.Store(id='memory-output'),
    dcc.Dropdown(id='memory-countries', options=[
        {'value': x, 'label': x} for x in countries
    ], multi=True, value=['Canada', 'United States']),
    dcc.Dropdown(id='memory-field', options=map_var_options, value=map_var_options[-1]['value']),
    html.Div([
        dcc.Graph(id='memory-graph'),
        dash_table.DataTable(
            id='memory-table',
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),
    ])
])


@app.callback(Output('memory-output', 'data'),
              Input('memory-countries', 'value'))
def filter_countries(countries_selected):
    if not countries_selected:
        # Return all the rows on initial load/no country selected.
        return df.to_dict('records')

    filtered = df.query('regio_s in @countries_selected')
    return filtered.to_dict('records')


@app.callback(Output('memory-table', 'data'),
              Input('memory-output', 'data'))
def on_data_set_table(data):
    if data is None:
        raise PreventUpdate

    return data


@app.callback(Output('memory-graph', 'figure'),
              Input('memory-output', 'data'),
              Input('memory-field', 'value'))
def on_data_set_graph(data, field):
    if data is None:
        raise PreventUpdate

    aggregation = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    data = [dict(
        type='choropleth',
        locationmode='country names',
        locations=df['Country'],
        z=df['HappinessScore'],
        autocolorscale=False,
        colorscale='Portland',
        reversescale=True,
        transforms=[dict(
            type='aggregate',
            groups=df['Country'],
            aggregations=[dict(
                target='z', func='sum', enabled=True)
            ]
        )]
    )]


    for row in data:

        a = aggregation[row['regio_s']]

        a['name'] = row['regio_s']
        a['mode'] = 'lines+markers'

        a['x'].append(row[field])
        a['y'].append(row['perioden'])

    return {
        'data': [x for x in aggregation.values()]
    }


if __name__ == '__main__':
    app.run_server(debug=True, threaded=True, port=10450)