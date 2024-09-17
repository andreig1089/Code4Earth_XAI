from .helper_functions import *
from . import validate_grib_file

def perturbation_by_factor(
        grib_file,
        variable,
        level=0,
        perturbation_factor=1,
        output_grib_file=None,):
    
    if not validate_grib_file(grib_file):
        return False
    
    if perturbation_factor == 1:
        print(f"perturbation factor is {perturbation_factor}, grib file will not be perturbed")
        return False
    
    u_id = uuid4().hex[-8:]
    
    path, file = os.path.split(grib_file)
    filename, extension = os.path.splitext(file)
    
    input_grib_file = grib_file
    if not output_grib_file:
        output_grib_file = os.path.join(path, f"{filename}_perturbed_factor_{variable}_{u_id}{extension}")

    with open(os.path.join(path, f"{filename}_perturbed_factor_{variable}_{u_id}_cfg.json"), "w") as f:
        f.write(json.dumps({
            "grib_file_name": str(grib_file),
            "variable": variable,
            "level": level,
            "zmul": perturbation_factor,
        }))

    # Open the GRIB file
    grbs = pygrib.open(input_grib_file)

    with open(output_grib_file, 'wb') as out_file:
        found_variable = False
        for grb in grbs:
            # print(grb.shortName, variable, grb.level, level)
            if grb.shortName == variable and grb.level == int(level):
                grb.expand_grid(False)
                found_variable = True
                print(f"perturbing {grb.shortName} - {grb.level} @ Time: {grb.dataTime} by factor {perturbation_factor}")
                data, latitudes, longitudes = grb.data()

                modified_data = data * float(perturbation_factor)
                
                grb.values = modified_data

            out_file.write(grb.tostring())
    
    grbs.close()

    if not found_variable:
        print(f"{variable} column does not exist in the grib file.")
        return False
    else:
        return True