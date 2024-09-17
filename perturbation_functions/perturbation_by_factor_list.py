from .helper_functions import *
from . import validate_grib_file

def perturbation_by_factor_list(
        grib_file,
        perturbation_dict = {"u": {300: 0.6}, "v": {300: 0.6}},
        output_grib_file=None,
        ):
    """
    perturbatio_dict contains tuples {variable_name: {variables_level: perturbation_factor}}
    """
    if not validate_grib_file(grib_file):
        return False
    
    path, file = os.path.split(grib_file)
    filename, extension = os.path.splitext(file)

    input_grib_file = grib_file

    u_id = uuid4().hex[-8:]

    if not output_grib_file:
        output_grib_file = os.path.join(path, f"{filename}_perturbed_{u_id}{extension}")

    with open(os.path.join(path, f"{filename}_perturbed_{u_id}_cfg.json"), "w") as f:
        f.write(json.dumps(dict(perturbation_dict, **{"grib_file": grib_file})))

    # Open the GRIB file
    grbs = pygrib.open(input_grib_file)

    # this will be used to track if the variables to perturb exist in the grib file
    variables_levels_check = list()
    _ = [variables_levels_check.extend([(k, int(k0)) for k0 in v.keys()]) for (k,v) in perturbation_dict.items()]

    perturbation_list = list()
    _ = [perturbation_list.extend([(k, int(k1), float(v1)) for (k1, v1) in v.items()]) for (k,v) in perturbation_dict.items()]

    variables_list = [v[0] for v in perturbation_list]
    levels_list = [v[1] for v in perturbation_list]

    with open(output_grib_file, 'wb') as out_file:
        variables_levels = list()
        for grb in grbs:
            grb.expand_grid(False)
            
            if grb.level in levels_list and grb.shortName in variables_list:
                for _pert in perturbation_list:
                    if _pert[0] == grb.shortName and _pert[1] == grb.level:    
                        grb.expand_grid(False)
                        print(f"perturbing {grb.shortName} - {grb.level} @ Time: {grb.dataTime}")
                        data, latitudes, longitudes = grb.data()

                        modified_data = data * _pert[2]

                        grb.values = modified_data
                        
                        variables_levels.append((grb.shortName, grb.level))

            out_file.write(grb.tostring())
    
    variables_diff = set(variables_levels_check) - set(variables_levels)

    if variables_diff:
        print(f"these variables were not found in the grib file:\n{variables_diff}")

    grbs.close()

    return True    