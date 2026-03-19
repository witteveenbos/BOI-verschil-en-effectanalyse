'''
Docstring for directories
function to set paths depending on the company folder structure
BOI verschil en effectanalyse 
Witteveen+Bos & HKV 2026
'''
import os
import zipfile
from pathlib import Path

def get_directories(company_name):
    '''
    Docstring for load_data
    
    company_name: 'HKV' or 'W+B', to set the directory paths based on the company folder structure.
    '''

    if company_name == "HKV":
        directory_path = Path("R:\\pr\\5542_10\\Verschilanalyse\\sommen\\")
        save_dir = Path("R:\\pr\\5542_10\\Verschilanalyse\\sommen\\Visualisaties")

    elif company_name == "W+B":
        directory_path = Path("z:\\149287_BOI_verschil_en_effectanalyse\\data\\sommen\\")
        save_dir = Path("z:\\149287_BOI_verschil_en_effectanalyse\\data\\visualisaties\\")
    else:
        print("Error: Invalid company_name. Please choose either 'HKV' or 'W+B'.")
        return None, None
    
    return directory_path, save_dir


def get_parameter_file_paths(sp_base_path, project_fase, som_versie, watersysteem, zip_file_name, parameter):
    """
    Returns a list of full paths (zip_path + internal path)
    to the requested parameter files inside zip archives.
    """

    # Map parameter to required filename
    parameter_map = {
        "ws": "hfreq.txt",
        # Add more parameters here later if needed
        # "wl": "wlfreq.txt",
    }

    if parameter not in parameter_map:
        raise ValueError(f"Unknown parameter: {parameter}")

    target_filename = parameter_map[parameter]

    # Construct folder path to 'sommen'
    sommen_path = os.path.join(
        sp_base_path,
        project_fase,
        "Rekenplan",
        som_versie,
        watersysteem,
        "uitvoer",
        "sommen"
    )

    found_files = []

    # Loop over zip files
    zip_path = os.path.join(sommen_path, zip_file_name)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for name in zip_ref.namelist():
            if name.endswith(target_filename):
                # Store full virtual path
                full_virtual_path = f"{zip_path}\\{name}"
                found_files.append(full_virtual_path)

    return found_files
