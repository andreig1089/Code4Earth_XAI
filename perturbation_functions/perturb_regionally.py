from .helper_functions import *
from . import validate_grib_file

def perturb_regionally(
        grib_file,
        variable,
        level,
        zmul=1,
        zadd=0,
        lat_s=LAT_MIN_LIM, 
        lat_n=LAT_MAX_LIM,
        lon_w=LON_MIN_LIM,
        lon_e=LON_MAX_LIM,
        thresx=274.5, 
        thresn=270., 
        thresfix=274.5,
        output_grib_file=None,):
    
    if not validate_grib_file(grib_file):
        return False

    # arg check
    if (lat_s == LAT_MIN_LIM and \
        lat_n == LAT_MAX_LIM and \
        lon_w == LON_MIN_LIM and \
        lon_e == LON_MAX_LIM):

        print(f"will perturb {variable} on all the coordinates.")
    
    if (lat_s < LAT_MIN_LIM and \
        lat_n > LAT_MAX_LIM and \
        lon_w < LON_MIN_LIM and \
        lon_e > LON_MAX_LIM):
        
        print(f"coordinates out of range limit lat",
              f"({LAT_MIN_LIM}, {LAT_MAX_LIM})",
              f"lon ({LON_MIN_LIM}, {LON_MAX_LIM})")
        return False


    path, file = os.path.split(grib_file)
    filename, extension = os.path.splitext(file)

    input_grib_file = grib_file
    u_id = uuid4().hex[-8:]

    if not output_grib_file:
        output_grib_file = os.path.join(OUTPUT_GRIB_PATH, f"{filename}_regional_{variable}_perturbed_{u_id}{extension}")

    with open(os.path.join(path, f"{filename}_regional_{variable}_perturbed_{u_id}_cfg.json"), "w") as f:
        f.write(json.dumps({
            "grib_file": grib_file,
            "variable": variable,
            "level": level,
            "zmul": zmul,
            "zadd": zadd,
            "lat_min": lat_s, 
            "lat_max": lat_n,
            "lon_min": lon_w,
            "lon_max": lon_e,
            "thresx": thresx, 
            "thresn": thresn, 
            "thresfix": thresfix,
        }))

    grbs = pygrib.open(input_grib_file)

    with open(output_grib_file, 'wb') as out_file:
        found_variable = False
        for (_i, grb) in enumerate(grbs):
            # Get the data, latitudes, and longitudes
            # grb.expand_grid(False)
                        
            if grb.shortName == variable and grb.level == level:
                grb.expand_grid(False)
                data, lats, lons = grb.data()

                found_variable = True
                unique_lons = np.unique(lons.flatten())
                unique_lats = np.unique(lats.flatten())

                lat_s, lat_n = (np.abs(np.unique(unique_lats) - lat_s)).min() + lat_s, (np.abs(np.unique(unique_lats) - lat_n)).min() + lat_n
                lon_w, lon_e = (np.abs(np.unique(unique_lons) - lon_w)).min() + lon_w, (np.abs(np.unique(unique_lons) - lon_e)).min() + lon_e
                                                
                # Create a mask based on the latitude and longitude range
                mask = (lats >= float(lat_s)) & (lats <= float(lat_n)) & (lons >= float(lon_w)) & (lons <= float(lon_e))

                # Modify the data where the mask is True
                data[mask] = float(zmul) * data[mask] + float(zadd)

                data = apply_thresh_to_temp_data(data, variable, thresx=thresx, thresn=thresn, thresfix=thresfix)

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