""" This file is the interface between the raw data and processed data. """
import pandas as pd

from support.constants import BASEPATH


class DataInterface:
    def __init__(self):
        fp = BASEPATH + "/data/regionale_kerncijfers.csv"
        self.data = pd.read_csv(fp)
        self.clean_statcode(data=self.data)

    def _only_counties(self, data: pd.DataFrame) -> pd.DataFrame:
        """ Returns the dataframe with only the counties. """
        non_counties = ['CR', 'PV', 'NL', 'LD']
        codes = data['KoppelvariabeleRegioCode_306'].apply(
            lambda x: x[:2] if x else "GM")
        self.clean_statcode(data=data)
        return data.loc[~codes.isin(non_counties)]

    def clean_statcode(self, data: pd.DataFrame) -> None:
        """ Cleans the statcode columns from spaces. """
        col = 'KoppelvariabeleRegioCode_306'
        data[col] = data[col].str.strip()

    def select_year(self, year: int):
        """ Returns the county data for the specified year. """
        return self.data.loc[self.data['Perioden'] == year]

    def data_by_county(self, year: int):
        """ Returns the data with county as index. Specify the year. """
        data = self.select_year(year=year)
        return data.set_index('RegioS')

    def county_yearly(self, county_code: str, variable: str):
        """ Returns a DataFrame based on the county_code and the variable on
        over multiple years. """
        cols=['RegioS', 'Perioden', variable]
        return self.data[cols].loc[
            (self.data['KoppelvariabeleRegioCode_306'] == county_code)]


data = DataInterface()


