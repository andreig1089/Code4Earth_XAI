import sys, os, json

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add dir2 to the Python path
sys.path.append(ROOT_PATH)

import logger
from .grib_file_config import *
from .validate_grib_file import *

# grib files list
GRIB_ROOT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
GRIB_DIR_PATH = os.path.join(GRIB_ROOT_DIR_PATH, 'experiments_grib_files')
TEST_GRIB_DIR_PATH = os.path.join(GRIB_ROOT_DIR_PATH, '_test_grib_file')

grib_files_paths = dict()
grib_pert_cfgs = dict()

for file in os.listdir(GRIB_DIR_PATH):
    filename = os.path.splitext(file)
    if filename[1] in [".grib", ".grb"]:
        grib_files_paths[filename[0]] = os.path.join(GRIB_DIR_PATH, file)
    
    if filename[1] in [".json"] and "_cfg" in filename[0]:
        with open(os.path.join(GRIB_DIR_PATH, file), "r") as f:
            grib_pert_cfgs[filename[0]] = json.load(f)

test_grib_files = list()

for file in os.listdir(TEST_GRIB_DIR_PATH):
    filename = os.path.splitext(file)
    if filename[1] == ".grib":
        test_grib_files.append(os.path.join(TEST_GRIB_DIR_PATH, file))