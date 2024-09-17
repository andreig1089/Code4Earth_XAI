from .helper_functions import *
from . import validate_grib_file

def perturb_specific_location(
        grib_file,
        variable,
        level,
        lat,
        lon,
        zmul=1,
        zadd=0,
        output_grib_file=None,):

    if not validate_grib_file(grib_file):
        return False

    if (lat < LAT_MIN_LIM and \
        lat > LAT_MAX_LIM and \
        lon < LON_MIN_LIM and \
        lon > LON_MAX_LIM):
        
        print(f"coordinates out of range limit lat",
              f"({LAT_MIN_LIM}, {LAT_MAX_LIM})",
              f"lon ({LON_MIN_LIM}, {LON_MAX_LIM})")
        return False
    
    path, file = os.path.split(grib_file)
    filename, extension = os.path.splitext(file)

    input_grib_file = grib_file

    u_id = uuid4().hex[-8:]

    if not output_grib_file:
        output_grib_file = os.path.join(OUTPUT_GRIB_PATH, f"{filename}_coord_point__{variable}_perturbed_{u_id}{extension}")

    with open(os.path.join(path, f"{filename}_coord_point_{variable}_perturbed_{u_id}_cfg.json"), "w") as f:
        f.write(json.dumps({ 
            "lat": lat,
            "lon": lon,
            "variable": variable,
            "level": level,
            "zadd": zadd,
            "zmul": zmul,
        }))

    grbs = pygrib.open(input_grib_file)

    with open(output_grib_file, 'wb') as out_file:
        found_variable = False
        # Loop through all messages in the GRIB file
        for (_i, grb) in enumerate(grbs):
            # Get the data, latitudes, and longitudes
            grb.expand_grid(False)
            data, lats, lons = grb.data()

            if grb.shortName == variable and grb.level == level:
                grb.expand_grid(False)

                found_variable = True
                unique_lons = np.unique(lons.flatten())
                unique_lats = np.unique(lats.flatten())

                # (np.abs(np.unique(unique_lats) - lat_s)).min() + lat_s

                lat = np.abs(np.unique(unique_lats) - lat).min() + lat
                lon = np.abs(np.unique(unique_lons) - lon).min() + lon
                                                
                # Create a mask based on the latitude and longitude range
                lat = float(lat)
                lon = float(lon)

                mask = (lats == lat) & (lons == lon)

                # Modify the data where the mask is True
                data[mask] = data[mask] * float(zmul) + float(zadd)

                data = apply_thresh_to_temp_data(data, variable)

                # Flatten the data to 1D if required by the grid type
                grb.values = data.flatten()

            # Write the modified message to the new GRIB file
            out_file.write(grb.tostring())

    grbs.close()
    
    if not found_variable:
        print(f"{variable} column does not exist in the grib file.")
        return False
    else:
        return True