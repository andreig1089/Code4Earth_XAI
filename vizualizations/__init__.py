import sys, os

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add dir2 to the Python path
sys.path.append(ROOT_PATH)

from grib_files import grib_files_paths