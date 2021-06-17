""" This file holds all helper functions. """
import re


def col_to_str(colname: str):
    """ Transform a CBS column name to a readable string.
    e.g. KoppelvariabeleRegioCode_306 -> Koppelvariable Regio Code. """
    s = colname.split("_")[0]
    los = re.sub(r"([A-Z])", r" \1", s).split()
    return " ".join([s.lower() if i!=0 else s for i, s in enumerate(los)])