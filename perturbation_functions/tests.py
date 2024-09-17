import unittest
# from unittest.mock import patch, mock_open, MagicMock
import os
import json
import pygrib

import numpy as np

from . import test_grib_files
from helper_functions import OUTPUT_GRIB_PATH
        
# Assuming the functions from your CLI script are imported here
from . import (
    validate_grib_file,
    perturbation_by_factor,
    perturbation_of_variable,
    perturbation_by_factor_list,
    perturbation_phase,
    perturb_regionally,
    perturb_specific_location,
    perturb_by_polygons
)

from logger import logger

if len(test_grib_files) > 1:
    logger.warning(f"Several test files detected. Only {test_grib_files[0]} will be used")
elif len(test_grib_files) == 0:
    TEST_GRIB_FILE = ""
else:
    TEST_GRIB_FILE = test_grib_files[0]

class TestPerturbationFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the file path for the test GRIB file
        cls.test_grib_file = TEST_GRIB_FILE
        if not os.path.exists(cls.test_grib_file):
            raise FileNotFoundError(f"Test GRIB file not found at {cls.test_grib_file}")

    def test_perturbation_by_factor(self):
        logger.info("Testing perturbation_by_factor...")
        # Step 1: Extract original data for comparison
        grbs = pygrib.open(self.test_grib_file)
        original_data = None

        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == 't' and grb.level == 500:
                original_data, original_lats, original_lons = grb.data()
                break
        grbs.close()

        # Step 2: Define the output GRIB file
        perturbed_grib_file = os.path.join(OUTPUT_GRIB_PATH, 'test_perturbed_factor.grib')

        # Step 3: Apply perturbation by factor
        zmul = 1.1
        result = perturbation_by_factor(self.test_grib_file, 't', 500, zmul, output_grib_file=perturbed_grib_file)
        self.assertTrue(result)

        # Step 4: Reopen and verify the perturbation
        grbs = pygrib.open(perturbed_grib_file)
        perturbed_data = None
        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == 't' and grb.level == 500:
                perturbed_data, perturbed_lats, perturbed_lons = grb.data()
                break
        grbs.close()

        # Check if the perturbation was correctly applied
        expected_data = original_data * zmul
        np.testing.assert_array_almost_equal(perturbed_data, expected_data, decimal=3)

        # Clean up
        os.remove(perturbed_grib_file)

    def test_perturbation_of_variable(self):
        # Step 1: Extract original data for comparison
        grbs = pygrib.open(self.test_grib_file)
        original_data = None

        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == 't' and grb.level == 500:
                original_data, original_lats, original_lons = grb.data()
                break
        grbs.close()

        # Step 2: Define the output GRIB file
        perturbed_grib_file = os.path.join(OUTPUT_GRIB_PATH, 'test_variable_perturbed.grib')

        # Step 3: Apply perturbation with zmul and zadd
        zmul = 1.2
        zadd = 1
        result = perturbation_of_variable(self.test_grib_file, 't', 500, zmul, zadd, output_grib_file=perturbed_grib_file)
        self.assertTrue(result)

        # Step 4: Reopen and verify the perturbation
        grbs = pygrib.open(perturbed_grib_file)
        perturbed_data = None
        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == 't' and grb.level == 500:
                perturbed_data, perturbed_lats, perturbed_lons = grb.data()
                break
        grbs.close()

        # Check if the perturbation was correctly applied
        expected_data = original_data * zmul + zadd
        np.testing.assert_array_almost_equal(perturbed_data, expected_data, decimal=3)

        # Clean up
        os.remove(perturbed_grib_file)

    def test_perturbation_by_factor_list(self):
        # Step 1: Extract original data for comparison
        grbs = pygrib.open(self.test_grib_file)
        original_data_u = None
        original_data_v = None

        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == 'u' and grb.level == 300:
                original_data_u, _, _ = grb.data()
            elif grb.shortName == 'v' and grb.level == 300:
                original_data_v, _, _ = grb.data()

        grbs.close()

        # Step 2: Define the output GRIB file
        perturbed_grib_file = os.path.join(OUTPUT_GRIB_PATH, 'test_perturbed_factor_list.grib')

        # Step 3: Apply perturbation by factor list
        perturbation_dict = {"u": {300: 1.1}, "v": {300: 1.2}}
        result = perturbation_by_factor_list(self.test_grib_file, perturbation_dict=perturbation_dict, output_grib_file=perturbed_grib_file)
        self.assertTrue(result)

        # Step 4: Reopen and verify the perturbation
        grbs = pygrib.open(perturbed_grib_file)
        perturbed_data_u = None
        perturbed_data_v = None
        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == 'u' and grb.level == 300:
                perturbed_data_u, _, _ = grb.data()
            elif grb.shortName == 'v' and grb.level == 300:
                perturbed_data_v, _, _ = grb.data()

        grbs.close()

        # Check if the perturbation was correctly applied
        expected_data_u = original_data_u * 1.1
        expected_data_v = original_data_v * 1.2
        np.testing.assert_array_almost_equal(perturbed_data_u, expected_data_u, decimal=2)
        np.testing.assert_array_almost_equal(perturbed_data_v, expected_data_v, decimal=2)

        # Clean up
        os.remove(perturbed_grib_file)

    def test_perturbation_phase(self):
        # Step 1: Extract original data for comparison
        grbs = pygrib.open(self.test_grib_file)

        # Dictionaries to store original data for times 0 and 1800
        original_data_zero = {}
        original_data_eighteen = {}

        # Extract original data for all variables and levels at times 0 and 1800
        for grb in grbs:
            grb.expand_grid(False)
            if grb.dataTime == 0:
                original_data_zero[(grb.shortName, grb.level)] = grb.data()
            elif grb.dataTime == 1800:
                original_data_eighteen[(grb.shortName, grb.level)] = grb.data()

        grbs.close()

        # Step 2: Define the output GRIB file
        perturbed_grib_file = os.path.join(OUTPUT_GRIB_PATH, 'test_perturbed_phase.grib')

        # Step 3: Apply perturbation phase
        result = perturbation_phase(self.test_grib_file, phase_shift="both", output_grib_file=perturbed_grib_file)
        self.assertTrue(result)

        # Step 4: Reopen and verify the phase perturbation
        grbs = pygrib.open(perturbed_grib_file)

        for grb in grbs:
            key = (grb.shortName, grb.level)
            grb.expand_grid(False)
            
            if grb.dataTime == 0:
                # Check that the data for time 0 is now equal to what was originally at 1800
                if key in original_data_eighteen:
                    original_eighteen_data, _, _ = original_data_eighteen[key]
                    perturbed_data_zero, _, _ = grb.data()
                    np.testing.assert_array_almost_equal(perturbed_data_zero, original_eighteen_data, decimal=3)
            elif grb.dataTime == 1800:
                # Check that the data for time 1800 is now equal to what was originally at 0
                if key in original_data_zero:
                    original_zero_data, _, _ = original_data_zero[key]
                    perturbed_data_eighteen, _, _ = grb.data()
                    np.testing.assert_array_almost_equal(perturbed_data_eighteen, original_zero_data, decimal=3)

        grbs.close()

        # Clean up
        os.remove(perturbed_grib_file)

    def test_perturb_regionally(self):
        # Step 1: Extract original data for comparison
        grbs = pygrib.open(self.test_grib_file)
        original_data = None
        original_lats = None
        original_lons = None

        var = "msl"
        lvl = 0

        for grb in grbs:
            if grb.shortName == var and grb.level == lvl:
                grb.expand_grid(False)
                original_data, original_lats, original_lons = grb.data()
                break
        grbs.close()

        # Step 2: Define the output GRIB file
        perturbed_grib_file = os.path.join(OUTPUT_GRIB_PATH, 'test_regionally_perturbed.grib')

        # Step 3: Apply regional perturbation
        zmul = 1.1
        zadd = 1
        lat_s, lat_n = 40, 60
        lon_w, lon_e = -10, 10
        result = perturb_regionally(self.test_grib_file, var, lvl, lat_s=lat_s, lat_n=lat_n, lon_w=lon_w, lon_e=lon_e, zmul=zmul, zadd=zadd, output_grib_file=perturbed_grib_file)
        self.assertTrue(result)

        # Step 4: Reopen and verify the regional perturbation
        grbs = pygrib.open(perturbed_grib_file)
        perturbed_data = None
        for grb in grbs:
            if grb.shortName == var and grb.level == lvl:
                grb.expand_grid(False)
                perturbed_data, perturbed_lats, perturbed_lons = grb.data()
                break
        grbs.close()

        # Step 5: Verify perturbation only in the region
        mask = (original_lats >= lat_s) & (original_lats <= lat_n) & (original_lons >= lon_w) & (original_lons <= lon_e)
        expected_data = np.copy(original_data)
        expected_data[mask] = original_data[mask] * zmul + zadd

        # np.testing.assert_array_almost_equal(perturbed_data, expected_data, decimal=0)
        np.testing.assert_allclose(perturbed_data, expected_data, rtol=0.005)

        # Clean up
        os.remove(perturbed_grib_file)

    def test_perturb_specific_location(self):
        # Step 1: Extract original data for comparison
        grbs = pygrib.open(self.test_grib_file)
        original_data = None
        original_lats = None
        original_lons = None

        var = "msl"
        lvl = 0

        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == var and grb.level == lvl:
                original_data, original_lats, original_lons = grb.data()
                break
        grbs.close()

        # Step 2: Define the output GRIB file
        perturbed_grib_file = os.path.join(OUTPUT_GRIB_PATH, 'test_location_perturbed.grib')

        # Step 3: Apply perturbation to a specific location
        zmul = 1.1
        zadd = 1
        lat, lon = 50, 10  # Specify a specific location
        result = perturb_specific_location(self.test_grib_file, var, lvl, lat, lon, zmul, zadd, output_grib_file=perturbed_grib_file)
        self.assertTrue(result)

        # Step 4: Reopen and verify the perturbation at the specific location
        grbs = pygrib.open(perturbed_grib_file)
        perturbed_data = None
        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == var and grb.level == lvl:
                perturbed_data, perturbed_lats, perturbed_lons = grb.data()
                break
        grbs.close()

        # Step 5: Create a mask for the specific location
        mask = (np.isclose(original_lats, lat, atol=0.5)) & (np.isclose(original_lons, lon, atol=0.5))
        expected_data = np.copy(original_data)
        expected_data[mask] = original_data[mask] * zmul + zadd

        # Ensure only the specific location was perturbed
        np.testing.assert_array_almost_equal(perturbed_data, expected_data, decimal=0)

        # Clean up
        os.remove(perturbed_grib_file)

    def test_perturb_by_polygons(self):
        # Step 1: Extract original data for comparison
        grbs = pygrib.open(self.test_grib_file)
        original_data = None
        original_lats = None
        original_lons = None

        var = "msl"
        lvl = 0

        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == var and grb.level == lvl:
                original_data, original_lats, original_lons = grb.data()
                break
        grbs.close()

        # Step 2: Define the output GRIB file
        perturbed_grib_file = os.path.join(OUTPUT_GRIB_PATH, 'test_polygons_perturbed.grib')

        # Step 3: Apply perturbation by polygons
        lonw_list = [295., 305.]
        lone_list = [310., 320.]
        lats_list = [40., 50.]
        latn_list = [45., 55.]
        zmul_list = [1.1, 1.2]
        zadd_list = [0.5, -0.5]
        result = perturb_by_polygons(self.test_grib_file, var, lvl, lonw_list, lone_list, lats_list, latn_list, zmul_list, zadd_list, output_grib_file=perturbed_grib_file)
        self.assertTrue(result)

        # Step 4: Reopen and verify the polygon-based perturbation
        grbs = pygrib.open(perturbed_grib_file)
        perturbed_data = None
        for grb in grbs:
            grb.expand_grid(False)
            if grb.shortName == var and grb.level == lvl:
                perturbed_data, perturbed_lats, perturbed_lons = grb.data()
                break
        grbs.close()

        unique_lons = np.unique(perturbed_lats.flatten())
        unique_lats = np.unique(perturbed_lons.flatten())

        # Step 5: Apply perturbations within specified polygons
        expected_data = np.copy(original_data)
        for lon_w, lon_e, lat_s, lat_n, zmul, zadd in zip(lonw_list, lone_list, lats_list, latn_list, zmul_list, zadd_list):
            lat_s, lat_n = (np.abs(np.unique(unique_lats) - lat_s)).min() + lat_s, (np.abs(np.unique(unique_lats) - lat_n)).min() + lat_n
            lon_w, lon_e = (np.abs(np.unique(unique_lons) - lon_w)).min() + lon_w, (np.abs(np.unique(unique_lons) - lon_e)).min() + lon_e

            mask = (original_lats >= lat_s) & (original_lats <= lat_n) & (original_lons >= lon_w) & (original_lons <= lon_e)
            expected_data[mask] = original_data[mask] * zmul + zadd

        # Ensure perturbation only in the polygons
        np.testing.assert_array_almost_equal(perturbed_data, expected_data, decimal=0)

        # Clean up
        os.remove(perturbed_grib_file)

if __name__ == "__main__":
    if TEST_GRIB_FILE:
        unittest.main()