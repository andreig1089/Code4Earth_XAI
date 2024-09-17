from .grib_file_config import VARIABLES, LEVELS, VALID_VARIABLES_DICT
from . import logger
import pygrib

def validate_grib_file(grib_file_path):
    valid_grib = True

    grbs = pygrib.open(grib_file_path)

    invalid_columns = dict()
    invalid_levels = dict()
    time_levels = set()
    columns = set()

    all_time_columns_levels = dict()

    for grb in grbs:

        column_name = grb.shortName
        column_level = grb.level
        column_time = grb.dataTime

        all_columns_levels = all_time_columns_levels.get(column_time, {})

        if column_name not in VARIABLES:
            time_invalid_columns = invalid_columns.get(column_time, [])
            time_invalid_columns.append(column_name)
        
        if column_level not in LEVELS:
            time_invalid_levels = invalid_levels.get(column_time, [])
            time_invalid_levels.append(column_name)

        time_levels.add(column_time)
        columns.add(column_name)

        col = all_columns_levels.get(grb.shortName, list())
        col.append(grb.level)
        all_columns_levels[grb.shortName] = col

        all_time_columns_levels[column_time] = all_columns_levels

    grbs.close()
    
    # sort dict
    sorted_level_3 = {
        k1: {
            k2: sorted(v2)
            for k2, v2 in v1.items()
        }
        for k1, v1 in all_time_columns_levels.items()
    }

    sorted_level_2 = {
        k1: dict(sorted(v1.items()))
        for k1, v1 in sorted_level_3.items()
    }

    all_time_columns_levels = dict(sorted(sorted_level_2.items()))

    if invalid_columns:
        logger.info(f"invalid grib:\nextra columns found:\n{invalid_columns}")
        valid_grib = False

    if invalid_levels:
        print(f"invalid grib:\nextra levels found:\n{invalid_levels}")
        valid_grib = False

    for (k,v) in all_time_columns_levels.items():
        if v != VALID_VARIABLES_DICT:
            print(f"{k} time does not have all the variables and levels")
            valid_grib = False
    
    return valid_grib