""" This file holds the choropleth map and its functions. """

import json
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame

from data.interface import db
from support.constants import BASEPATH
from ui.runtime_vars import RuntimeVars


class ChoroMap:

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, val: int):
        self.__geo_json = self.get_geojson(year=val)
        self.__data = db.get_region_data(columns=self.vars.map_var,
                                         year=val)
        self.__district_lookup = self.get_district_lookup()

    @property
    def geo_json(self):
        return self.__geo_json

    @property
    def data(self):
        return self.__data

    @staticmethod
    def get_geojson(year: int):
        fp = BASEPATH + "/data/geodata/gemeentegrenzen_{}.geojson".format(
            year)
        with open(fp) as f:
            geo_json = json.load(f)
        return geo_json

    @property
    def district_lookup(self):
        """ Prepare a lookup dictionary for selecting highlight areas in
        geojson. """
        return self.__district_lookup

    def update_map_data(self):
        """ Sets the year and variable on the map. """
        self.fig.data = ()
        self.year = self.vars.year
        self.fig.add_choroplethmapbox(
            geojson=self.geo_json,
            z=self.data[self.vars.map_var],
            locations=self.data["koppelvariabele_regio_code_306"],
            featureidkey="properties.statcode",
            marker=dict(opacity=0.3)
        )

        self.update_selection()

    def update_selection(self):
        """ Changes the selection of counties on the map. """
        if len(self.vars.selections) > 0:
            # highlights contain the geojson information for only
            # the selected districts
            highlights = self.get_highlights()
            if len(self.fig.data) > 1:
                self.fig.data = tuple([self.fig.data[0]])
            self.fig.add_choroplethmapbox(
                geojson=highlights,
                z=self.data[self.vars.map_var],
                locations=self.data["koppelvariabele_regio_code_306"],
                featureidkey="properties.statcode",
                marker=dict(opacity=0.8)
            )
        self.add_custom_data()

    def add_custom_data(self):
        """ Adds the custom data for the hover info. """
        customdata_df = db.get_region_data(
            columns=['totale_bevolking_1', 'gemiddelde_woningwaarde_99',
                     self.vars.map_var],
            year=self.vars.map_var)
        customdata_df['gemeente'] = customdata_df.index
        self.fig.update_traces(customdata=customdata_df,
                               hovertemplate="Gemeente: %{customdata[2]}<br>" +
                                             "Inwoners: %{customdata[0]}<br>" + \
                                             "Waarde: %{customdata[1]}<extra></extra>")

    # function to get the geojson file for highlighted area
    def get_highlights(self, geo_json, regions):
        geojson_highlights = dict()
        for k in geo_json.keys():
            if k != 'features':
                geojson_highlights[k] = geo_json[k]
            else:
                geojson_highlights[k] = [self.district_lookup[selection] for
                                         selection in regions]
        return geojson_highlights

    def get_district_lookup(self, geo_json):
        return {feature['properties']['statcode']: feature for feature in
                geo_json['features']}

    def geojson_highlights(self, geo_json, regions):
        highlights = dict()
        for k in geo_json.keys():

            if k != 'features':
                highlights[k] = geo_json[k]
            else:
                highlights[k] = [f for f in geo_json[k] if
                                 f['properties']['statcode'] in regions]
        return highlights

    def show_figure(self, geo_json, data: DataFrame, map_var: str, regions):
        """ Shows a choropleth map. """
        fig = go.FigureWidget(px.choropleth_mapbox())

        fig.add_choroplethmapbox(
            geojson=geo_json,
            z=data[map_var],
            locations=data["koppelvariabele_regio_code_306"],
            featureidkey="properties.statcode",
            coloraxis='coloraxis',
            marker=dict(opacity=0.3)
        )

        fig.update_layout(mapbox_style="carto-positron",
                          mapbox_zoom=6,
                          mapbox_center={"lat": 52.09, "lon": 5.12},
                          margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          uirevision='constant')

        if regions:
            # Add the highlights
            highlights=self.geojson_highlights(geo_json=geo_json, regions=regions)

            print(len(highlights['features']))
            data_highlights = data.loc[
                data['koppelvariabele_regio_code_306'].isin(regions)]

            fig.add_choroplethmapbox(
                geojson=highlights,
                z=data_highlights[map_var],
                locations=data["koppelvariabele_regio_code_306"],
                featureidkey="properties.statcode",
                coloraxis='coloraxis',
                marker=dict(opacity=1)
            )

        return fig


if __name__ == "__main__":
    choromap = ChoroMap()
    df = db.get_region_data(col_str="gemiddelde_woningwaarde_99", year=2020)
    choromap.show_figure(data=df, map_var='gemiddelde_woningwaarde_99',
                         year=2020)
