""" This file holds the choropleth map and its functions. """

import json
import plotly.express as px

from data.interface import data
from support.constants import BASEPATH


class Map:
    def __init__(self, year):
        self.__year = year
        self.__geo_json = self.get_geojson(year=year)
        self.__data = data.data_by_county(year=year)
        self.__district_lookup = self.get_district_lookup()
        self.selections = set()

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, val: int):
        self.__geo_json = self.get_geojson(year=val)
        self.__data = data.data_by_county(year=val)
        self.__district_lookup = self.get_district_lookup()
        self.__year = val

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
        fp = BASEPATH + "/database/geodata/gemeentegrenzen_{}.geojson".format(
            year)
        with open(fp) as f:
            geo_json = json.load(f)
        return geo_json

    @property
    def district_lookup(self):
        """ Prepare a lookup dictionary for selecting highlight areas in
        geojson. """
        return self.__district_lookup

    def get_map(self, year: int = 2020):
        """ Returns a choropleth map of the netherlands with the specified
        data. """
        self.year = year
        # Base choropleth layer --------------#
        fig = px.choropleth_mapbox(self.data, geojson=self.geo_json,
                                   color="TotaleBevolking_1",
                                   locations="KoppelvariabeleRegioCode_306",
                                   featureidkey="properties.statcode",
                                   opacity=0.5)

        # Second layer - Highlights ----------#
        if len(self.selections) > 0:
            # highlights contain the geojson information for only
            # the selected districts
            highlights = self.get_highlights()

            fig.add_trace(
                px.choropleth_mapbox(self.data, geojson=highlights,
                                     color="TotaleBevolking_1",
                                     locations="KoppelvariabeleRegioCode_306",
                                     featureidkey="properties.statcode",
                                     opacity=1).data[0]
            )

        # ------------------------------------#
        fig.update_layout(mapbox_style="carto-positron",
                          mapbox_zoom=6,
                          mapbox_center={"lat": 52.09, "lon": 5.12},
                          margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          uirevision='constant')

        return fig

    # function to get the geojson file for highlighted area
    def get_highlights(self):
        geojson_highlights = dict()
        for k in self.geo_json.keys():
            if k != 'features':
                geojson_highlights[k] = self.geo_json[k]
            else:
                geojson_highlights[k] = [self.district_lookup[selection] for
                                         selection
                                         in self.selections]
        return geojson_highlights


if __name__ == "__main__":
    map = Map(year=2020)
    fig = map.get_map()
