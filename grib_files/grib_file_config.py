# aifs grib files variables
SURFACE_VARIABLES = [
    '10u', 
    '10v', 
    '2d', 
    '2t', 
    'lsm', 
    'msl', 
    'sdor', 
    'skt', 
    'slor', 
    'sp', 
    'tcw']

UPPER_VARIABLES =[
    'q', 
    't', 
    'w', 
    'z', 
    'u', 
    'v'
]

VARIABLES = sorted(SURFACE_VARIABLES + UPPER_VARIABLES)

VARIABLES_DOC = {
    'levels': 'pressure_levels in hPa',
    'q': 'Specific humidity',
    't': 'Temperature',
    'w': 'Vertical velocity',
    'z': 'Geopotential',
    'u': 'U component of wind',
    'v': 'V component of wind',
    '10u': '10 metre U wind component',
    '10v': '10 metre V wind component',
    '2d': '2 metre dewpoint temperature',
    '2t': '2 metre temperature',
    'lsm': 'Land-sea mask',
    'msl': 'Mean sea level pressure',
    'sdor': 'Standard deviation of sub-gridscale orography',
    'skt': 'Skin temperature',
    'slor': 'Slope of sub-gridscale orography',
    'sp': 'Surface pressure',
    'tcw': 'Total column water'
    }

LEVELS = sorted(set([100, 200, 1000, 300, 400, 50, 850, 500, 150, 600, 250, 700, 925]))

VALID_VARIABLES_DICT = {k: LEVELS if k in UPPER_VARIABLES else [0] for k in VARIABLES}
VALID_VARIABLES_DICT['z'] = [0] + LEVELS

# grid limits
LAT_MIN_LIM, LAT_MAX_LIM = -90, 90
LON_MIN_LIM, LON_MAX_LIM = -180, 180