from perturbation_functions import *

def apply_thresh_to_temp_data(data, variable, thresx=274.5, thresn=270., thresfix=274.5):
    """
    Apply thresholding to temperature-related data.

    This function modifies the input temperature data by setting values within a specified
    range to a fixed threshold value. It is applicable only to certain temperature variables.

    Parameters
    ----------
    data : numpy.ndarray
        The temperature data array to be processed. This array will be modified in place.
    variable : str
        The name of the variable to check. Thresholding is applied only if this variable
        is one of ['t', '2t', 'skt'].
    thresx : float, optional
        The upper threshold value. Data values greater than or equal to `thresn` and
        less than or equal to `thresx` will be set to `thresfix`. Default is `274.5`.
    thresn : float, optional
        The lower threshold value. Data values greater than or equal to `thresn` and
        less than or equal to `thresx` will be set to `thresfix`. Default is `270.0`.
    thresfix : float, optional
        The value to set data within the threshold range to. Default is `274.5`.

    Returns
    -------
    numpy.ndarray
        The modified temperature data array with threshold applied where applicable.

    Raises
    ------
    TypeError
        If `data` is not a numpy.ndarray.
    ValueError
        If `variable` is not one of the expected temperature variables.

    Examples
    --------
    >>> import numpy as np
    >>> data = np.array([269, 271, 275, 273])
    >>> apply_thresh_to_temp_data(data, 't')
    array([269. , 274.5, 275. , 274.5])

    >>> data = np.array([268, 270, 274, 275])
    >>> apply_thresh_to_temp_data(data, 'skt', thresfix=273.0)
    array([268. , 273. , 273. , 275. ])
    """
    if variable in ['t', '2t', 'skt']:
        temp_mask = (data >= thresn) & (data <= thresx)
        data[temp_mask] = thresfix
    return data

def load_custom_config(config_file):
    """
    Load a custom configuration file into a dictionary.

    This function reads a configuration file, parses key-value pairs, and returns
    them as a dictionary. It ignores lines that are empty, start with comments,
    or begin with specific characters indicating non-configuration lines.

    Parameters
    ----------
    config_file : str
        The path to the configuration file to be loaded. The file should contain
        key-value pairs in the format `key = value`. Lines starting with `#` or
        `$` in the first line are ignored, as well as any subsequent lines that
        are empty or start with `#`.

    Returns
    -------
    dict
        A dictionary containing the configuration parameters as key-value pairs.

    Raises
    ------
    FileNotFoundError
        If the specified `config_file` does not exist.
    PermissionError
        If there are insufficient permissions to read the `config_file`.
    ValueError
        If a line in the configuration file does not contain an `=` separator
        for key-value pairing.
    """
    config_dict = {}
    with open(config_file, 'r') as f:
        lines = f.readlines()

        # ignore the first line if it starts with # or $
        if lines and (lines[0].startswith('#') or lines[0].startswith('$')):
            lines = lines[1:]

        # parse the remaining lines
        for line in lines:
            line = line.strip()
            
            # ignore empty lines and in-line comments
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                config_dict[key.strip()] = value.strip()
    return config_dict

def parse_list(value):
    return [float(x) for x in value.split(',')]

def merge_args_with_config(args, config):
    """
    Merge command-line arguments with configuration settings.

    This function combines command-line arguments and configuration settings into a single
    dictionary. Command-line arguments take precedence over configuration settings. Only
    arguments with non-None values are included in the merged result.

    Parameters
    ----------
    args : argparse.Namespace
        An `argparse.Namespace` object containing command-line arguments. Typically obtained
        using `argparse.ArgumentParser.parse_args()`.
    config : dict, optional
        A dictionary containing configuration settings. These settings serve as default values
        and are overridden by command-line arguments if provided. If `config` is `None`, an
        empty dictionary is used.

    Returns
    -------
    dict
        A merged dictionary containing configuration settings updated with command-line
        arguments. Only arguments with non-None values are included.

    Raises
    ------
    TypeError
        If `args` is not an instance of `argparse.Namespace` or if `config` is not a dictionary
        or `None`.
    """
    merged = config.copy() if config else {}
    for key, value in vars(args).items():
        if value is not None:
            merged[key] = value
    return merged


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CLI for perturbing a AIFS grib file using command-line arguments or configuration files.",
        epilog="Example usage:\n"
               "  python3 perturbations_aifs.py perturbation_by_factor --grib_file ./grib_files/20240302_orig_init.grb --config '/path/to/config.txt' --variable 'msl' --level 0 --factor 1.1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Main argument to specify a config file
    parser.add_argument('--version', action='version', version='0.1')

    # Create a subparser object to handle subcommands
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # perturbation_by_factor
    parser_a = subparsers.add_parser('perturbation_by_factor', help='variable and level will be perturbed by the specified factor')
    parser_a.add_argument('--config', type=str, help='Path to the config file (key=value format)')
    parser_a.add_argument('--grib_file', type=str, help='Path to the GRIB file')
    parser_a.add_argument('--variable', type=str, help='Variable to perturb')
    parser_a.add_argument('--level', type=int, help='Level of the variable')
    parser_a.add_argument('--factor', type=float, help='Perturbation factor')
    parser_a.add_argument('--output_grib_file', type=str, help='Path to the output GRIB file')

    # perturbation_phase
    parser_b = subparsers.add_parser('perturbation_phase', help='perturb the grib file phases')
    parser_b.add_argument('--config', type=str, help='Path to the config file (key=value format)')
    parser_b.add_argument('--grib_file', type=str, help='Path to the GRIB file')
    parser_b.add_argument('--phase_shift', type=str, choices=["future", "past", "both"], help='Phase shift method (future, past, both)')
    parser_b.add_argument('--output_grib_file', type=str, help='Path to the output GRIB file')

    # regional perturbation
    parser_c = subparsers.add_parser('regional_perturbation', help='regionally perturb variable and level in the specified coordinates')
    parser_c.add_argument('--config', type=str, help='Path to the config file (key=value format)')
    parser_c.add_argument('--grib_file', type=str, help='Path to the GRIB file')
    parser_c.add_argument('--variable', type=str, help='Variable to perturb')
    parser_c.add_argument('--level', type=int, help='Level of the variable')
    parser_c.add_argument('--lat_min', type=float, help='Minimum latitude')
    parser_c.add_argument('--lat_max', type=float, help='Maximum latitude')
    parser_c.add_argument('--lon_min', type=float, help='Minimum longitude')
    parser_c.add_argument('--lon_max', type=float, help='Maximum longitude')
    parser_c.add_argument('--zmul', type=float, help='Multiplication factor for perturbation')
    parser_c.add_argument('--zadd', type=float, help='Addition factor for perturbation')
    parser_c.add_argument('--output_grib_file', type=str, help='Path to the output GRIB file')

    # location perturbation
    parser_d = subparsers.add_parser('location_perturbation', help='perturb variable and level in the specified location')
    parser_d.add_argument('--config', type=str, help='Path to the config file (key=value format)')
    parser_d.add_argument('--grib_file', type=str, help='Path to the GRIB file')
    parser_d.add_argument('--variable', type=str, help='Variable to perturb')
    parser_d.add_argument('--level', type=int, help='Level of the variable')
    parser_d.add_argument('--lat', type=float, help='Latitude of the location')
    parser_d.add_argument('--lon', type=float, help='Longitude of the location')
    parser_d.add_argument('--zmul', type=float, help='Multiplication factor for perturbation')
    parser_d.add_argument('--zadd', type=float, help='Addition factor for perturbation')
    parser_d.add_argument('--output_grib_file', type=str, help='Path to the output GRIB file')

    # perturbation of variable
    parser_e = subparsers.add_parser('perturbation_of_variable', help='perturb variable and level using multiplication and addition terms')
    parser_e.add_argument('--config', type=str, help='Path to the config file (key=value format)')
    parser_e.add_argument('--grib_file', type=str, help='Path to the GRIB file')
    parser_e.add_argument('--variable', type=str, help='Variable to perturb')
    parser_e.add_argument('--level', type=int, help='Level of the variable')
    parser_e.add_argument('--zmul', type=float, help='Multiplication factor for perturbation')
    parser_e.add_argument('--zadd', type=float, help='Addition factor for perturbation')
    parser_e.add_argument('--output_grib_file', type=str, help='Path to the output GRIB file')

    # perturbation_by_polygons (new CLI subcommand)
    parser_f = subparsers.add_parser('perturbation_by_polygons', help='perturb variable and level within specified polygons')
    parser_f.add_argument('--config', type=str, help='Path to the config file (key=value format)')
    parser_f.add_argument('--grib_file', type=str, help='Path to the GRIB file')
    parser_f.add_argument('--variable', type=str, help='Variable to perturb')
    parser_f.add_argument('--level', type=int, help='Level of the variable')
    parser_f.add_argument('--lonw', type=str, help='Longitude west list (comma-separated)')
    parser_f.add_argument('--lone', type=str, help='Longitude east list (comma-separated)')
    parser_f.add_argument('--lats', type=str, help='Latitude south list (comma-separated)')
    parser_f.add_argument('--latn', type=str, help='Latitude north list (comma-separated)')
    parser_f.add_argument('--zmul', type=str, help='Multiplication factor list (comma-separated)')
    parser_f.add_argument('--zadd', type=str, help='Addition factor list (comma-separated)')
    parser_f.add_argument('--output_grib_file', type=str, help='Path to the output GRIB file')

    # perturbation_by_list
    parser_g = subparsers.add_parser('perturbation_by_list', help='variables and levels will be perturbed by the specified factors')
    parser_g.add_argument('--config', type=str, help='Path to the config file (key=value format)')
    parser_g.add_argument('--grib_file', type=str, help='Path to the GRIB file')
    parser_g.add_argument('--perturbation_json', type=str, help='Variables and levels to perturb by factor')
    parser_g.add_argument('--output_grib_file', type=str, help='Path to the output GRIB file')

    args = parser.parse_args()

    # Parse the config file if it exists and merge it with command-line args
    config = load_custom_config(args.config) if args.config else {}

    final_args = merge_args_with_config(args, config)
    print(final_args)

    if args.command == "perturbation_by_factor":
        # final_args = merge_args_with_config(args, config)
        perturbation_by_factor(
            grib_file=final_args["grib_file"],
            variable=final_args["variable"],
            level=final_args["level"],
            perturbation_factor=final_args["factor"],
            output_grib_file=final_args.get("output_grib_file")
        )
    elif args.command == "perturbation_by_list":
        # final_args = merge_args_with_config(args, config)
        perturbation_dict = json.loads(final_args.get("perturbation_json"))

        perturbation_by_factor_list(
            grib_file=final_args["grib_file"],
            perturbation_dict=perturbation_dict,
            output_grib_file=final_args.get("output_grib_file")
        )
    elif args.command == "perturbation_phase":
        # final_args = merge_args_with_config(args, config)
        perturbation_phase(
            grib_file=final_args["grib_file"],
            phase_shift=final_args.get("phase_shift", "both"),
            output_grib_file=final_args.get("output_grib_file")
        )
    elif args.command == "regional_perturbation":
        # final_args = merge_args_with_config(args, config)
        perturb_regionally(
            grib_file=final_args["grib_file"],
            variable=final_args["variable"],
            level=final_args["level"],
            lat_s=final_args["lat_min"],
            lat_n=final_args["lat_max"],
            lon_w=final_args["lon_min"],
            lon_e=final_args["lon_max"],
            zmul=final_args.get("zmul", 1),
            zadd=final_args.get("zadd", 0),
            output_grib_file=final_args.get("output_grib_file")
        )
    elif args.command == "location_perturbation":
        # final_args = merge_args_with_config(args, config)
        perturb_specific_location(
            grib_file=final_args["grib_file"],
            variable=final_args["variable"],
            level=final_args["level"],
            lat=final_args["lat"],
            lon=final_args["lon"],
            zmul=final_args.get("zmul", 1),
            zadd=final_args.get("zadd", 0),
            output_grib_file=final_args.get("output_grib_file")
        )
    elif args.command == "perturbation_of_variable":
        # final_args = merge_args_with_config(args, config)
        perturbation_of_variable(
            grib_file=final_args["grib_file"],
            variable=final_args["variable"],
            level=final_args["level"],
            zmul=final_args.get("zmul", 1),
            zadd=final_args.get("zadd", 0),
            output_grib_file=final_args.get("output_grib_file")
        )
    elif args.command == "perturbation_by_polygons":
        perturb_by_polygons(
            grib_file=final_args['grib_file'],
            variable=final_args['variable'],
            level=int(final_args['level']),
            lonw_list=parse_list(final_args['lonw']),
            lone_list=parse_list(final_args['lone']),
            lats_list=parse_list(final_args['lats']),
            latn_list=parse_list(final_args['latn']),
            zmul_list=parse_list(final_args['zmul']),
            zadd_list=parse_list(final_args['zadd']),
            output_grib_file=final_args.get('output_grib_file')
        )    
    else:
        parser.print_help()