from .helper_functions import *
from . import validate_grib_file

def perturbation_phase(
        grib_file, 
        output_grib_file=None, 
        phase_shift="both"):
    """
    Perturb the phase of a GRIB file based on the phase_shift variable.
    
    Args:
        grib_file (str): The input GRIB file.
        output_grib_file (str, optional): The output GRIB file. If not provided, it will create one.
        phase_shift (str): "future" to replicate values from 1800 to 0000, "past" to replicate values from 0000 to 1800, or "both" to swap the values.
    """
    if not validate_grib_file(grib_file):
        return False

    # Set the output GRIB file name if not provided
    path, file = os.path.split(grib_file)
    filename, extension = os.path.splitext(file)
    
    u_id = uuid4().hex[-8:]
    
    if not output_grib_file:
        output_grib_file = os.path.join(OUTPUT_GRIB_PATH, f"{filename}_phase_perturbed_{u_id}{extension}")
    
    with open(os.path.join(path, f"{filename}_phase_perturbed_{u_id}_cfg.json"), "w") as f:
        f.write(json.dumps({
            "grib_file": grib_file,
            "phase_shift": str(phase_shift),
        }))

    # Open the GRIB file
    grbs = pygrib.open(grib_file)

    # Dictionaries to store data for times 0 and 1800
    zero_time_data = {}
    eighteen_time_data = {}

    # Step 1: Store data for dataTime == 0 and dataTime == 1800
    for grb in grbs:
        grb.expand_grid(False)
        key = (grb.shortName, grb.level)
        if grb.dataTime == 0:
            zero_time_data[key] = grb.data()  # Store data for time 0
        elif grb.dataTime == 1800:
            eighteen_time_data[key] = grb.data()  # Store data for time 1800

    # Rewind the GRIB file to iterate again
    grbs.seek(0)

    # Step 2: Create the output file and apply the phase shift
    with open(output_grib_file, 'wb') as out_file:
        for grb in grbs:
            grb.expand_grid(False)
            key = (grb.shortName, grb.level)
            
            if phase_shift == "future":
                if grb.dataTime == 0 and key in eighteen_time_data:
                    # Copy values from time 1800 to time 0
                    grb.values = eighteen_time_data[key][0]  # Set the data from time 1800
                    grb.dataTime = 0  # Keep the time at 0
                # Keep time 1800 messages unchanged
            elif phase_shift == "past":
                if grb.dataTime == 1800 and key in zero_time_data:
                    # Copy values from time 0 to time 1800
                    grb.values = zero_time_data[key][0]  # Set the data from time 0
                    grb.dataTime = 1800  # Keep the time at 1800
                # Keep time 0 messages unchanged
            elif phase_shift == "both":
                if grb.dataTime == 0 and key in eighteen_time_data:
                    # Swap values: Copy data from time 1800 to time 0
                    grb.values = eighteen_time_data[key][0]
                    grb.dataTime = 0
                elif grb.dataTime == 1800 and key in zero_time_data:
                    # Swap values: Copy data from time 0 to time 1800
                    grb.values = zero_time_data[key][0]
                    grb.dataTime = 1800

            # Write the modified or unchanged message to the output file
            out_file.write(grb.tostring())

    grbs.close()

    print(f"Output GRIB file saved as: {output_grib_file}")
    return True