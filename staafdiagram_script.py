import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import scipy.interpolate

from utils.readers import read_hfreq_file
from utils.directories import get_directories

from utils.plotting_settings import colors_dict, legend_dict, parameters, order_dict

def staafdiagram_script(watersysteem,
                        parameter,
                        location_type,
                        locations = None,
                        company_name = 'HKV',
                        simulation_types = ['2017-totB2017-met_ws', '2023-totB2023-met_ws'],
                        TT = 10000):
    TT_prob = 1/TT

    mapname_dict = {'Europoort' : 'BER_Eprt', 'Hollandsche IJssel' : 'BER_HollandscheIJssel', 'Benedenmaas': 'BER_Maas',
                'Rijntakken':'BER_Rijn', 'VolkerakZoommeer' : 'BER_VolkerakZoommeer', 'Bovenmaas' : 'BOR_Maas',
                'Maas_hk' : 'BOR_MaasHK', 'Rijn':'BOR_Rijn', 'Kust-Dijken':'KST-Dijken', 'Kust duinen':'KST_Duinen', 
                'Oosterschelde':'KST_Oosterschelde', 'Grevelingen':'MRN_Grevelingen', 'IJsselmeer':'MRN_IJsselmeer', 
                'Markermeer':'MRN_Markermeer', 'Veluwerandmeren':'MRN_Veluwerandmeren', 'IJsseldelta':'YVD_IJsseldelta',
                'Vechtdelta':'YVD_Vechtdelta'}
    mapname = mapname_dict[watersysteem]

    # Base path to the project drive
    if watersysteem == 'HollandscheIJssel':
        prefix = 'BER'
    else:
        prefix = 'BOR'

    # Set directory paths based on company folder structure


    # setting base path and testing if it exists
    directory_path, save_dir = get_directories(company_name)
    base_path = rf"{directory_path}\HydraNL_BI2023_{mapname}"

    # Save all frequency, values of the chosen HydraNL outputs in a dictionary.
    # data_by_location[locationname][simulation_type] = (frequency, values), e.g. data_by_location['014-01_0017_HY_km0001']['2017-fysica-zon_HBN]
    data_by_location = defaultdict(dict)

    # Iterate over location_type, produce plots of all locations in input 'locations', of the calculation in input 'simulation_types'
    for loc_type in location_type:
        path = Path(rf"{base_path}_{loc_type}")
        # For-loop checkt of één van de gewenste locaties in deze map zitten
        for item in path.iterdir():
            if item.name.endswith('.bat'): # Sla deze file over
                continue
            else:
                if locations == None or item.name.split('_BI')[0] in locations:
                    # Als we een gewenste locatie gevonden hebben, checken we of de map de juiste rekeninstellingen heeft
                    if (simulation_types == None and item.name.endswith(parameter)) or (simulation_types != None and item.name.split('_BI')[-1] in simulation_types):
                        # Look in the uitvoer-map of this location, find the .txt file which contains the output of HydraNL
                        uitvoer_loc_path = path / item.name / 'uitvoer'
                        for file in uitvoer_loc_path.iterdir():
                            if file.name.endswith('.txt'):
                                temp_path = uitvoer_loc_path / file.name
                                probs, vals = read_hfreq_file(rf"{temp_path}")
                                temp_interp = scipy.interpolate.interp1d(np.log(probs), vals, kind='linear', fill_value='extrapolate')
                                data_by_location[item.name.split('_BI')[0]]['BI'+item.name.split('_BI')[-1]] = temp_interp(np.log(TT_prob))

    diff_lst = []
    for key, value in data_by_location.items():
        keys_lst = list(value.keys())
        if len(keys_lst) == len(simulation_types):
            diff = value[keys_lst[1]] - value[keys_lst[0]]
            diff_lst.append(diff)

    # Categorize into bins
    up = 0.05
    lo = -0.05
    hoger = sum(1 for x in diff_lst if x > up)
    gelijk = sum(1 for x in diff_lst if lo <= x <= up)
    lager = sum(1 for x in diff_lst if x < lo)

    # Create bar plot
    categories = ['Verlaging', 'Gelijk', 'Verhoging']
    counts = [lager, gelijk, hoger]

    plt.figure(figsize=(8, 6))
    plt.bar(categories, counts, color=['green', 'gray', 'red'])
    plt.ylabel(f'Aantal locaties in {watersysteem}')
    plt.title(f'Waarde bij T={TT} van {simulation_types[1]} t.o.v. {simulation_types[0]}')
    plt.grid(True, alpha=0.3, axis='y')

    # Save with unique filename for each location
    filename = f"Staafdiagram_{watersysteem}_{parameter}.png"
    plt.savefig(rf"{save_dir}\{filename}", dpi=150, bbox_inches='tight')
    print(f"Plot saved as '{filename}'")

if __name__ == "__main__":
    staafdiagram_script(watersysteem = 'Rijn',
                        parameter='ws',
                        location_type=["as"],
                        locations = None,
                        company_name= "HKV",
                        simulation_types = ['2017-totB2017-zon_ws', '2023-totB2023-zon_ws'],
                        TT = 10000)
