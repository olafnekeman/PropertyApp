""" With the CBSData class, CBS data can be downloaded and saved in the postgres database.

Current table in database:

table_code | table_name
70072NED     regionale_kerncijfers
             tussen_gemeenten_verhuisde_personen
"""
import cbsodata
from pandas import DataFrame

from data.pg_connect import Database


class CBSData(Database):

    def __init__(self):
        super(CBSData, self).__init__()

    def store_regionale_kerncijfers_data(self) -> None:
        """ Downloads preprocesses and stores the regionale kerncijfers table from CBS. """
        # df = self.download_table(table_code="70072NED")
        query = "SELECT * FROM regionale_kerncijfers"
        df = self.get_df_from_query(query)

        # Cleaning the database
        # Set column names from camelcase to PEP style
        import re
        columns = []
        for i in df.columns:
            if i == 'ID':
                columns.append('id')
            else:
                columns.append(re.sub(r'(?<!^)(?=[A-Z])', '_', i).lower())
        df.columns = columns

        # Stripping whitespaces
        def strip_val(val):
            try:
                return str(val).strip()
            except:
                return val

        for col in df.columns:
            if str(df[col].dtype) == 'object':
                df[col] = df[col].apply(strip_val)

        # Try to set dtype of 'regios'
        df['regio_s'] = df['regio_s'].astype('str')

        # Set type of region
        def set_type(name: str):
            if name == 'Nederland':
                return 'country'
            elif name[-4:] == '(LD)':
                return 'country_part'
            elif name[-4:] == '(CR)':
                return 'corop'
            elif name[-4:] == '(PV)':
                return 'province'
            else:
                return "region"

        df['type'] = df['regio_s'].apply(set_type)

        # Set 'perioden' to int
        df['perioden'] = df['perioden'].astype('int')

        # Store the dataframe
        self.store_cbs_data(df=df)

    def download_table(self, table_code: str) -> DataFrame:
        """ Downloads a table from the CBSodata portal. """
        # Print table metadata
        info = cbsodata.get_info(table_code)
        print("Downloading table: {name}".format(name=info['Title']))

        # Get data
        df = DataFrame(cbsodata.get_data(table_code))

        return df

    def store_cbs_data(self, df: DataFrame, check: bool = True):
        """ Downloads and stores a table from the CBS to the postgres database.
        table_code: str = """

        # Connect to Heroku Postgre DB
        conn = self.connect_alchemy()

        # Name the table
        self.list_tables()
        name = input("Set name for database: ")

        # Write to DB
        print("\nWriting to database ...")
        try:
            df.to_sql(name=name, con=conn, if_exists='replace')
            print("Succes!")
        except:
            print("Error occurred. ")

        if check:
            print('Checking ...')
            print(conn.execute("SELECT * FROM {}".format(name)).fetchall())

        conn.dispose()


if __name__ == "__main__":
    cbs = CBSData()
    cbs.store_regionale_kerncijfers_data()
