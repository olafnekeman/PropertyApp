#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import the sql and connect libraries for psycopg2
from psycopg2 import sql, connect

# create a global string for the PostgreSQL db name
db_name = "de49s33kdavj49"

try:
    # declare a new PostgreSQL connection object
    conn = connect(
        dbname=db_name,
        user="kiufnyzelvojho",
        host="ec2-176-34-105-15.eu-west-1.compute.amazonaws.com",
        password="331c381b46dc08c8ac85cdf5fd022c4abbf7424baa66cbeec6589739a8ec2702"
    )

    # print the connection if successful
    print("psycopg2 connection:", conn)

except Exception as err:
    print("psycopg2 connect() ERROR:", err)
    conn = None
