#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import the sql and connect libraries for psycopg2
from psycopg2 import sql, connect
# create a global string for the PostgreSQL db name
db_name = "d91vcqu2u3tnnj"

try:
    # declare a new PostgreSQL connection object
    conn = connect(
        dbname=db_name,
        user="xmukfffjuhnkpd",
        host="ec2-54-74-77-126.eu-west-1.compute.amazonaws.com",
        password="fa8f9d63a1edccac6ee899618064398630530f532923c311cddd61b5022f91be"
    )

    # print the connection if successful
    print("psycopg2 connection:", conn)

except Exception as err:
    print("psycopg2 connect() ERROR:", err)
    conn = None
