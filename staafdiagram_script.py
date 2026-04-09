import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import scipy.interpolate
from pathlib import PurePosixPath

from utils.readers import read_hfreq_file, read_hfreq_file_new
from utils.directories import get_directories, get_parameter_file_paths
from utils.readers import read_hfreq_file_new

from utils.plotting_settings import colors_dict, legend_dict, parameters, order_dict, annotate_BOI_higher_lower

def staafdiagram_script(files,
                        save_dir,
                        watersysteem,
                        parameter,
                        locations = None,
                        simulation_types = ['2017-totB2017-met_ws', '2023-totB2023-met_ws'],
                        diagram_name = '',
                        TT = 10000):
    TT_prob = 1/TT
                          
    diff_unit = parameters[parameter][4]

    # Base path to the project drive
    if watersysteem == 'HollandscheIJssel':
        prefix = 'BER'
    else:
        prefix = 'BOR'

    # Save all frequency, values of the chosen HydraNL outputs in a dictionary.
    # data_by_location[locationname][simulation_type] = (frequency, values), e.g. data_by_location['014-01_0017_HY_km0001']['2017-fysica-zon_HBN]
    data_by_location = defaultdict(dict)

    for file in files:

        zip_index = file.lower().find(".zip")
        internal_path = file[zip_index + 5:]

        p = PurePosixPath(internal_path)
        simulation_folder = str(p).split('\\')[1] # p.parts[1]
        # print(simulation_folder)
        location = simulation_folder.split("_BI")[0]
        simulation_type = "BI" + simulation_folder.split("_BI")[1]

        # Remove parameter suffix (_ws, _hs, etc.)
        sim_type_base = simulation_type

        # Apply filters safely
        if (simulation_types is None or sim_type_base in simulation_types) and \
        (locations is None or location in locations):
            probs, vals = read_hfreq_file_new(file)
            temp_interp = scipy.interpolate.interp1d(np.log(probs), vals, kind='linear', fill_value='extrapolate')
            data_by_location[location][simulation_type] = temp_interp(np.log(TT_prob))
            
        # All data we want to plot has been collected, now we move on to plotting.

    diff_lst = []
    for key, value in data_by_location.items():
        keys_lst = list(value.keys())
        if len(keys_lst) == len(simulation_types):
            diff = value[keys_lst[0]] - value[keys_lst[1]]
            diff_lst.append(diff)

    # Categorize into bins
    up = 0.50
    lo = -0.50
    hoger = sum(1 for x in diff_lst if x > up)/len(diff_lst)
    lager = sum(1 for x in diff_lst if x < lo)/len(diff_lst)
    gelijk = sum(1 for x in diff_lst if lo <= x <= up)/len(diff_lst)

    # Bins every 10cm between lo and up
    bin_40_50  = sum(1 for x in diff_lst if  0.40 <= x <= up)  / len(diff_lst)
    bin_30_40  = sum(1 for x in diff_lst if  0.30 <= x <  0.40) / len(diff_lst)
    bin_20_30  = sum(1 for x in diff_lst if  0.20 <= x <  0.30) / len(diff_lst)
    bin_10_20  = sum(1 for x in diff_lst if  0.10 <= x <  0.20) / len(diff_lst)
    bin_00_10  = sum(1 for x in diff_lst if  0.00 <= x <  0.10) / len(diff_lst)
    bin_n10_00 = sum(1 for x in diff_lst if -0.10 <= x <  0.00) / len(diff_lst)
    bin_n20_n10 = sum(1 for x in diff_lst if -0.20 <= x < -0.10) / len(diff_lst)
    bin_n30_n20 = sum(1 for x in diff_lst if -0.30 <= x < -0.20) / len(diff_lst)
    bin_n40_n30 = sum(1 for x in diff_lst if -0.40 <= x < -0.30) / len(diff_lst)
    bin_n50_n40 = sum(1 for x in diff_lst if    lo <= x < -0.40) / len(diff_lst)


    # Create bar plot
    # categories = [f'BOI {int(up*100)}cm hoger dan WBI', r'$$' , f'BOI {int(up*100)}cm lager dan WBI']
    categories = [
    f'< -{int(up*100)}cm',
    '-50 tot -40cm',
    '-40 tot -30cm',
    '-30 tot -20cm',
    '-20 tot -10cm',
    '-10 tot 0cm',
    '0 tot 10cm',
    '10 tot 20cm',
    '20 tot 30cm',
    '30 tot 40cm',
    '40 tot 50cm',
    f'> {int(abs(lo)*100)}cm']
    counts = [lager, bin_n50_n40, bin_n40_n30, bin_n30_n20, bin_n20_n10, bin_n10_00, bin_00_10, bin_10_20, bin_20_30, bin_30_40, bin_40_50, hoger]

    # get color from colors_dict based on simulation_types
    color_key = next((key for key in colors_dict if diagram_name in key), None)
    color = colors_dict[color_key][0] if color_key else 'gray'

    plt.figure(figsize=(8, 6))
    plt.bar(categories, counts, color=color, edgecolor='black')
    if len(watersysteem)>0:
        plt.ylabel(f'Fractie locaties in {watersysteem}')
    else: 
        plt.ylabel(f'Fractie locaties')
    plt.xlabel(f'Verschil WBI minus BOI [{diff_unit}]')
    plt.title(f'Verschil in {parameters[parameter][1]} bij T = {TT} jaar \n {simulation_types[0]} - {simulation_types[1]}')
    plt.grid(True, alpha=0.3, axis='y')
    # add vertical line at 0
    x_zero_line = len(categories) / 2 - 0.5
    plt.axvline(x_zero_line, color='black', linestyle='--', linewidth=2)
    #annotate_BOI_higher_lower(plt.gca(), x_zero_line, orientation='horizontal')
    plt.xticks(rotation=30,fontsize=9)
    plt.tight_layout()
    
    # naam maken en directory controlerenen aanmaken indien nodig
    filename = f"Staafdiagram_{watersysteem}_{parameter}_{diagram_name}.png"
    os.makedirs(save_dir, exist_ok=True)

    plt.savefig(os.path.join(save_dir, filename), dpi=150, bbox_inches='tight')
    print(f"Plot saved as '{filename}'")
    plt.close()


if __name__ == "__main__":
    # Example usage:
    # 0.1 instellingen voor dit script
    sp_base_path = r"c:\Users\BEMC\HKV\PR5542.10 - BOI - Verschilanalyse Hydraulische Belastingen - Projectuitvoering - Projectuitvoering"
    project_fase = 'WP02a Beoordelen Kust (dijken)'
    som_versie = 'aslocaties - concept_20260320'
    watersysteem = '' # leeg laten als er maar 1 watersysteem is voor dit WP, b.v. Meren kan dit MRN_Grevelingen zijn, maar Rijntakken heeft alleen de Rijntakken - dus dan leeg.
    zip_file_name = "HydraNL_BI2023_KST_Dijken_as.zip" # naam van het zip bestand waarin de data staat, b.v. "HydraNL_BI2023_BOR_Rijn_as.zip" of "HydraNL_BI2023_BOR_Meren.zip"

    parameter = 'ws' # parameter waarvoor we de frequentielijnen willen plotten, b.v. 'ws' of 'hs'
    locations = None # maar kan ook individuele locaties hebben in een lijst b.v. ['vk204b_0234_MM_hm0526'], ['as_0061_RH_km0854']

    # locatie van opslaan van figuren    
    save_dir = os.path.join(sp_base_path, project_fase, "Visualisaties", som_versie, watersysteem, "st") # opslaan in een submap van de map 

    # 0.2 Bestanden ophalen, we listen gewoon alle bestanden uit de zip met een bepaalde parameter
    files = get_parameter_file_paths(sp_base_path = sp_base_path, project_fase = project_fase, som_versie = som_versie, watersysteem = watersysteem, zip_file_name = zip_file_name, parameter = parameter)
    files = [f.replace('/', '\\') for f in files] # Toegevoegd door Thomas omdat het pad anders niet werkte bij mij

    diagrams = {'totB2017-zon': [f'BI2017-totB2017-zon_{parameter}', f'BI2023-totB2023-zon_{parameter}'], 
                #'totB2017-met': [f'BI2017-totB2017-met_{parameter}', f'BI2023-totB2023-met_{parameter}'],
                #'fysB2017-zon': [f'BI2023-fysB2017-zon_{parameter}', f'BI2023-totB2023-zon_{parameter}'],
                #'stkB2017-zon': [f'BI2023-stkB2017-zon_{parameter}', f'BI2023-totB2023-zon_{parameter}'],
                #'rknB2017-zon': [f'BI2023-rknB2017-zon_{parameter}', f'BI2023-totB2023-zon_{parameter}']
                }

    for diagram_name, simulation_types in diagrams.items():
        staafdiagram_script(files,
                            save_dir = save_dir,
                            diagram_name = diagram_name,
                            watersysteem = watersysteem,
                            parameter = parameter,
                            locations = None,
                            simulation_types = simulation_types,
                            TT = 10000)