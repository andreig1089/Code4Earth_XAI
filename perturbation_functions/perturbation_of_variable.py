from .helper_functions import *
from . import validate_grib_file

def perturbation_of_variable(
        grib_file,
        variable,
        level=0,
        zmul=1,
        zadd=0,
        output_grib_file=None,):
    
    
    if not validate_grib_file(grib_file):
        return False
    
    if zmul == 1 and zadd == 0:
        print(f"no addition term and no multiplication factor, grib file will not be perturbed")
        return False
    
    path, file = os.path.split(grib_file)
    filename, extension = os.path.splitext(file)

    u_id = uuid4().hex[-8:]

    input_grib_file = grib_file
    if not output_grib_file:
        output_grib_file = os.path.join(OUTPUT_GRIB_PATH, f"{filename}_{variable}_{level}_perturbed_{u_id}{extension}")

    with open(os.path.join(path, f"{filename}_{variable}_{level}_perturbed_{u_id}_cfg.json"), "w") as f:
        f.write(json.dumps({
            "grib_file_name": str(grib_file),
            "variable": variable,
            "level": level,
            "zadd": zadd,
            "zmul": zmul,
        }))

    # Open the GRIB file
    grbs = pygrib.open(input_grib_file)

    with open(output_grib_file, 'wb') as out_file:
        found_variable = False
        for grb in grbs:
            if grb.shortName == variable and grb.level == int(level):
                grb.expand_grid(False)

                found_variable = True
                print(f"perturbing {grb.shortName} - {grb.level} @ Time: {grb.dataTime} by factor with multiplication of {zmul} and addition of {zadd}.")
                data, latitudes, longitudes = grb.data()

                modified_data = data * float(zmul) + float(zadd)
                
                grb.values = modified_data

            out_file.write(grb.tostring())
    
    grbs.close()

    if not found_variable:
        print(f"{variable} column does not exist in the grib file.")
        return False
    else:
        return True