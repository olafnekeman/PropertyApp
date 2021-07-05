""" This file holds all helper functions. """
import re


def col_to_str(colname: str):
    """ Transform a CBS column name to a readable string.
    e.g. koppelvariabele_regio_code_306 -> Koppelvariable Regio Code. """
    los = colname.split("_")[:-1]
    return " ".join([s.capitalize() for s in los])
