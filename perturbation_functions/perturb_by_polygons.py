from .helper_functions import *
from . import validate_grib_file

def perturb_by_polygons(
        grib_file, 
        variable, 
        level, 
        lonw_list, 
        lone_list, 
        lats_list, 
        latn_list, 
        zmul_list, 
        zadd_list,
        thresx=274.5, 
        thresn=270., 
        thresfix=274.5, 
        output_grib_file=None):
    
    if not validate_grib_file(grib_file):
        return False

    # Set output file name if not provided
    path, file = os.path.split(grib_file)
    filename, extension = os.path.splitext(file)

    u_id = uuid4().hex[-8:]

    if not output_grib_file:
        output_grib_file = os.path.join(
            OUTPUT_GRIB_PATH, 
            f"{filename}_{variable}_{level}_perturbed_by_polygons{extension}")
        
    with open(os.path.join(path, f"{filename}_regional_{variable}_perturbed_{u_id}_cfg.json"), "w") as f:
        f.write(json.dumps({
            "input_grib": grib_file,
            "variable": variable,
            "level": level,
            "lonw_list": lonw_list, 
            "lone_list": lone_list,
            "lats_list": lats_list,
            "latn_list": latn_list,
            "zmul_list": zmul_list,
            "zadd_list": zadd_list,
            "thresx": thresx,
            "thresn": thresn,
            "thresfix": thresfix
        }))

    # Open the GRIB file
    grbs = pygrib.open(grib_file)

    with open(output_grib_file, 'wb') as out_file:
        found_variable = False

        # Loop through all GRIB messages
        for grb in grbs:
            if grb.shortName == variable and grb.level == level:
                grb.expand_grid(False)  # Ensure the grid is expanded (for reduced grids)

                found_variable = True
                print(f"Perturbing {grb.shortName} - {grb.level} at time {grb.dataTime}")
                
                # Get the data, latitudes, and longitudes
                data, lats, lons = grb.data()

                unique_lons = np.unique(lons.flatten())
                unique_lats = np.unique(lats.flatten())

                # Loop through each polygon (defined by lists of coordinates)
                for lon_w, lon_e, lat_s, lat_n, zmul, zadd in zip(lonw_list, lone_list, lats_list, latn_list, zmul_list, zadd_list):
                    lat_s, lat_n = (np.abs(np.unique(unique_lats) - lat_s)).min() + lat_s, (np.abs(np.unique(unique_lats) - lat_n)).min() + lat_n
                    lon_w, lon_e = (np.abs(np.unique(unique_lons) - lon_w)).min() + lon_w, (np.abs(np.unique(unique_lons) - lon_e)).min() + lon_e

                    lat_s = float(lat_s)
                    lat_n = float(lat_n)
                    lon_w = float(lon_w)
                    lon_e = float(lon_e)

                    # Create a mask for the polygon (points within the polygon's bounds)
                    mask = (lats >= lat_s) & (lats <= lat_n) & (lons >= lon_w) & (lons <= lon_e)

                    data = apply_thresh_to_temp_data(data, variable, thresx=thresx, thresn=thresn, thresfix=thresfix)
                    
                    # Apply perturbation (multiplication and addition) within the polygon
                    data[mask] = data[mask] * float(zmul) + float(zadd)

                # Update the GRIB message with the perturbed data
                grb.values = data.reshape(-1)

            # Write the modified (or unmodified) GRIB message to the output file
            out_file.write(grb.tostring())

    grbs.close()

    if not found_variable:
        print(f"Variable {variable} at level {level} does not exist in the GRIB file.")
        return False

    print(f"Output GRIB file saved as: {output_grib_file}")
    return True