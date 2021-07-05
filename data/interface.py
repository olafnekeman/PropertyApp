""" This file is the interface between the raw data and processed data. """
import pandas as pd

from data.pg_connect import Database
from support.constants import BASEPATH
from sqlalchemy import select


class DatabaseInterface(Database):
    def __init__(self):
        super(DatabaseInterface, self).__init__()
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
        cols = ['RegioS', 'Perioden', variable]
        return self.data[cols].loc[
            (self.data['KoppelvariabeleRegioCode_306'] == county_code)]

    def get_columns(self, col_str: str, year: int = None, region: str = None,
                    distinct: bool = False):
        """ Returns the columns from the regionale_kerncijfers table. """

        # Build start query
        query = """
        SELECT {column}
        FROM regionale_kerncijfers 
        WHERE type='region' """

        # Add columns
        if distinct:
            col_str = "DISTINCT " + col_str

        query = query.format(column=col_str)

        # Add year or region if variable is passed
        if year:
            query += "AND perioden={year}".format(year=year)
        if region:
            query += "AND regio_s='{region}'".format(region=region)
        query += ";"

        data = self.get_df_from_query(query=query)

        return data

    def get_region_data(self, col_str: str , year: int = None, region: str = None,
                        distinct: bool = False):
        """ returns a DataFrame of the selected columns. """
        base_columns = 'id, regio_s, perioden, {cols}, koppelvariabele_regio_code_306'

        to_retrieve = base_columns.format(cols=col_str)

        data = self.get_columns(col_str=to_retrieve, year=year, region=region,
                                distinct=distinct)

        return data


db = DatabaseInterface()

if __name__ == "__main__":
    df1 = db.get_region_data(columns="gemiddelde_woningwaarde_99", year=2020)
    df2 = db.get_region_data(
        columns=["gemiddelde_woningwaarde_99", "oud_papier_en_karton_238"],
        region="Aa en Hunze")
