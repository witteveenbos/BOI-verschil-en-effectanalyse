'''
Docstring for directories
function to set paths depending on the company folder structure
BOI verschil en effectanalyse
Witteveen+Bos & HKV 2026
'''

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