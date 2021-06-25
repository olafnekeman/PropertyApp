#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import the sql and connect libraries for psycopg2
from psycopg2 import connect, DatabaseError
from psycopg2.extensions import connection
import sys
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from pandas import DataFrame, read_sql


# create a global string for the PostgreSQL db name

class Database:
    def __init__(self):
        self.dbname = 'd226jg5evs5g3o'
        self.user = 'sugxbwhqwfvbgq'
        self.host = 'ec2-54-228-9-90.eu-west-1.compute.amazonaws.com'
        self.password = 'c942aa329688760e53e3b39fe0f0e48ca580b0e919378c656c7c3b441eef1bca'
        self.port = 5432

    def connect(self) -> connection:
        """ Creates a connection to the database. """
        try:
            # connect to the PostgreSQL server
            print('\n Connecting to the PostgreSQL database...') if __name__ == "__main__" else None
            conn = connect(
                dbname=self.dbname,
                user=self.user,
                host=self.host,
                password=self.password,
                port=self.port
            )

            # print the connection if successful
            print("Connection successful \n") if __name__ == "__main__" else None

        except (Exception, DatabaseError) as error:
            conn = None
            print(error)
            sys.exit(1)
        return conn

    def connect_alchemy(self) -> Engine:
        """ Connect to the database through the sqlalchemy package. """
        print('Connecting to the PostgreSQL database through sqlalchemy ...') if __name__ == "__main__" else None
        try:
            DATABASE_URL = 'postgresql://{user}:{password}@{host}:5432/{db}'.format(
                user=self.user,
                password=self.password,
                host=self.host,
                db=self.dbname
            )
            engine = create_engine(DATABASE_URL, echo=False)
            print("Connection succesfull!") if __name__ == "__main__" else None
            return engine
        except:
            print('Error connecting... ')
            return None

    def list_tables(self, print_output: bool = True) -> list:
        """ List all tables in the database. """
        query = "SELECT * FROM information_schema.tables WHERE table_schema = 'public';"
        res = self.execute_query(query=query)

        # Print tables
        if print_output:
            [print("name: {}".format(tab[2])) for tab in res]
            print("\nCurrent tables: ")

        return [tab[2] for tab in res]

    def delete_table(self):
        """ Deletes a table from the database. """
        # list tables and type a name that has to be deleted.
        tables = self.list_tables(print_output=False)
        to_delete = input("Table to be deleted: ")

        def delete_tab(name):
            print("Deleting table ...")

            try:
                query = "DROP TABLE {};".format(name)
                self.execute_query(query=query)
                print("Succes!")
                return "SUCCES"
            except:
                print("Error occurred!")

        while to_delete not in tables:
            res = delete_tab(name=to_delete)
            if res == "SUCCES":
                break
            else:
                print('Name not in database tables. Please input another name ... ')
                to_delete = input("Table to be deleted: ")

    def execute_query(self, query: str):
        """ Executes a query and closes the connection. """
        conn = self.connect_alchemy()
        with conn.connect() as connection:
            res = connection.execute(query).fetchall()
            connection.close()
        conn.dispose()
        return res

    def get_df_from_query(self, query: str):
        """ Executes a query. """
        conn = self.connect_alchemy()
        data = read_sql(sql=query, con=conn)
        conn.dispose()
        return data

    def get_table_columns(self, table_name: str):
        """ Returns the columns of a table."""
        query = """ SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{name}';""".format(
            name=table_name
        )
        return self.execute_query(query=query)


if __name__ == "__main__":
    db = Database()
    db.get_table_columns('regionale_kerncijfers')
