""" This file holds the choropleth map and its functions. """

import json
import plotly.express as px
import plotly.graph_objects as go

from data.interface import data
from support.constants import BASEPATH
from ui.runtime_vars import RuntimeVars


class ChoroMap:
    def __init__(self, runtime_vars: RuntimeVars):
        self.vars = runtime_vars
        self.__year = self.vars.year
        self.__geo_json = self.get_geojson(year=self.vars.year)
        self.__data = data.data_by_county(year=self.vars.year)
        self.__district_lookup = self.get_district_lookup()
        self.fig = go.FigureWidget(px.choropleth_mapbox())
        self.fig.update_layout(mapbox_style="carto-positron",
                          mapbox_zoom=6,
                          mapbox_center={"lat": 52.09, "lon": 5.12},
                          margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          uirevision='constant')

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, val: int):
        self.__geo_json = self.get_geojson(year=val)
        self.__data = data.data_by_county(year=val)
        self.__district_lookup = self.get_district_lookup()

    @property
    def geo_json(self):
        return self.__geo_json

    @property
    def data(self):
        return self.__data

    def get_district_lookup(self):
        return {feature['properties']['statcode']: feature for feature in
                self.__geo_json['features']}

    def get_geojson(self, year: int):
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
            locations=self.data["KoppelvariabeleRegioCode_306"],
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
                locations=self.data["KoppelvariabeleRegioCode_306"],
                featureidkey="properties.statcode",
                marker=dict(opacity=0.8)
            )
        self.add_custom_data()

    def add_custom_data(self):
        """ Adds the custom data for the hover info. """
        customdata_df = self.data[['TotaleBevolking_1',
                                   'GemiddeldeWoningwaarde_99']].copy()
        customdata_df['Gemeente'] = customdata_df.index
        self.fig.update_traces(customdata=customdata_df,
                          hovertemplate="Gemeente: %{customdata[2]}<br>" +
                                        "Inwoners: %{customdata[0]}<br>" + \
                                        "Gem. Woningwaarde: %{customdata[1]}<extra></extra>")


    # function to get the geojson file for highlighted area
    def get_highlights(self):
        geojson_highlights = dict()
        for k in self.geo_json.keys():
            if k != 'features':
                geojson_highlights[k] = self.geo_json[k]
            else:
                geojson_highlights[k] = [self.district_lookup[selection] for
                                         selection
                                         in self.vars.selections]
        return geojson_highlights


if __name__ == "__main__":
    rvars = RuntimeVars()
    rvars.selections.add("GM0503")
    rvars.selections.add("GM0505")

    choromap = ChoroMap(runtime_vars=rvars)
    choromap.update_map_data()
