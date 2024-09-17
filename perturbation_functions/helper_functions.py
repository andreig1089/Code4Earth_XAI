import sys, os

import pygrib
import numpy as np
import os

import json

from uuid import uuid4

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_GRIB_PATH = os.path.join(ROOT_PATH, 'output_grib_files')

# Add dir2 to the Python path
sys.path.append(ROOT_PATH)

from grib_files import *
from logger import logger

def apply_thresh_to_temp_data(data, variable, thresx=274.5, thresn=270., thresfix=274.5):
    if variable in ['t', '2t', 'skt']:
        temp_mask = (data >= thresn) & (data <= thresx)
        data[temp_mask] = thresfix
    return data