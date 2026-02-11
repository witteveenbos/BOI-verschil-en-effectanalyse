"""
Docstring for frequentielijnen
Contains main function for freq lijnen
BOI verschil en effectanalyse
Witteveen+Bos & HKV 2026

Script to read HydraNL/Riskeer computation results and plot frequency vs water level
from hfreq.txt files.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

from utils.readers import read_hfreq_file
from utils.directories import get_directories

from utils.plotting_settings import colors_dict, legend_dict, parameters, order_dict

def main_frequentielijn(watersysteem = None, simulation_types = None, company_name = 'HKV', location_type = ['as', 'oever'], locations = None, parameter = None, colors_dict = colors_dict):
    """
    Main function to read and plot hfreq data.
    
    Args:
        watersysteem (str): Name of the water system (e.g., "HollandscheIJssel", "Rijntakken")
                           If None, gives error
        simulation_types (list): List of simulation type filters (e.g., ["2017-totaal-zon_WS", "2023-fysica-met_HBN"])
                                If None or empty, all simulations are included
        location_type (str or list) : Type of location (oever/as) to filter by.
                                If none is given, both location types are included.
        locations (str or list): Location(s) to filter by. Can be location IDs (e.g., "as_0001")
                                or location codes from parent folder (e.g., "as" from folder ending in "_as")
                                If none is given, all locations are included
        parameter (str) : Name of the parameter of interest. This is to be used only when simulation_types is None, so that all simulation_types of a single parameter are plotted in the same figure (rather than multiple parameters' return times in a single figure).
                                Some examples of possible values: 'HBN', 'WS', 'Tp', 'Hs'
        colors_dict (dict) : Maps simulation_type to a plotting color.
                                If none is given, a standard template is used which is read from utils.plotting_settings.

    """
    # Base path to the project drive
    if watersysteem == 'HollandscheIJssel':
        prefix = 'BER'
    else:
        prefix = 'BOR'
    
    # Set directory paths based on company folder structure


    # setting base path and testing if it exists
    directory_path, save_dir = get_directories(company_name)
    base_path = rf"{directory_path}\HydraNL_Beoordelen_{prefix}_{watersysteem}"

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
                                data_by_location[item.name.split('_BI')[0]]['BI'+item.name.split('_BI')[-1]] = read_hfreq_file(rf"{temp_path}")

    # All data we want to plot has been collected, now we move on to plotting.
    #######################################################

    # Create separate plot for each location
    for location, computations in sorted(data_by_location.items()):

        reference_name = 'BI2023-totaalBI-met'
        reference_name = [i for i in list(computations.keys()) if  i.split('_')[0] == reference_name]
        has_reference = bool(reference_name)
        reference_name = reference_name[0] # Spaghetti code ten top dit

        # --- Create figure (1 or 2 panels depending on availability reference)
        if has_reference:
            fig, (ax, ax_diff) = plt.subplots(
                2, 1, figsize=(12, 9), sharex=True,
                gridspec_kw={'height_ratios': [3, 2]}
            )
        else:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax_diff = None  # no difference plot

        parameter_name = list(computations.keys())[0].split('_')[1]
        ylabel = parameters[parameter_name][0]

        # ------------------------------------------------------------------
        # Prepare reference data (needed for difference plot)
        # ------------------------------------------------------------------
        if has_reference:
            ref_frequency, ref_wl = computations[reference_name]
            ref_T = 1.0 / ref_frequency

            # ensure increasing order for interpolation
            sort_idx = np.argsort(ref_T)
            ref_T = ref_T[sort_idx]
            ref_wl = ref_wl[sort_idx]

        # ------------------------------------------------------------------
        # Plot all computations (TOP FIGURE)
        # ------------------------------------------------------------------
        for computation_name, (frequency, water_level) in sorted(computations.items()):
            color = colors_dict[computation_name.split('_')[0]]
            legend_name = legend_dict[computation_name.split('_')[0]]

            return_period = 1.0 / frequency

            if computation_name.split('-')[1] == 'totaalBI':
                linestyle = 'solid'
                linewidth = 1
            else:
                linestyle = 'dotted'
                linewidth = 2

            ax.plot(return_period, water_level,
                    label=legend_name, linewidth=linewidth,
                    color=color, linestyle=linestyle)

            # ------------------------------------------------------------------
            # DIFFERENCE PLOT (if reference exists and not the reference itself)
            # ------------------------------------------------------------------
            if has_reference and computation_name != reference_name:

                # sort for interpolation
                sort_idx = np.argsort(return_period)
                T_sorted = return_period[sort_idx]
                wl_sorted = water_level[sort_idx]

                # interpolate this computation onto reference T-grid
                wl_interp = np.interp(ref_T, T_sorted, wl_sorted)

                diff = wl_interp - ref_wl

                ax_diff.plot(ref_T, diff,
                            color=color, linestyle=linestyle,
                            linewidth=linewidth, label=legend_name)

        # ------------------------------------------------------------------
        # TOP AXIS FORMATTING  (your original styling)
        # ------------------------------------------------------------------
        ax.set_xlabel("Terugkeertijd (jaar)", fontsize=11 if not has_reference else 0)
        ax.set_ylabel(f"{ylabel}", fontsize=11)
        ax.set_xlim(10, 10e5)
        ax.set_xscale('log')
        ax.grid(True, which='both', alpha=0.3)
        ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

        # ylim logic unchanged
        max_ylim_value = -np.inf
        min_ylim_value = np.inf
        for computation_name, (frequency, water_level) in computations.items():
            return_period = 1.0 / frequency
            min_ylim_value = min(min_ylim_value, water_level[0])
            mask = return_period >= 10e4
            if np.any(mask):
                max_ylim_value = max(max_ylim_value, np.max(water_level[mask]))

        if max_ylim_value != -np.inf:
            ax.set_ylim(top=max_ylim_value + 0.1*(max_ylim_value - min_ylim_value))

        # ------------------------------------------------------------------
        # DIFFERENCE AXIS FORMATTING
        # ------------------------------------------------------------------
        if has_reference:
            ax_diff.set_title('Verschil t.o.v. BOI', fontsize = 12)
            ax_diff.axhline(0.0, color='red', linewidth=0.8)
            ax_diff.set_ylabel(rf"$\Delta${ylabel}", fontsize=11)
            ax_diff.set_xlabel("Terugkeertijd (jaar)", fontsize=11)
            ax_diff.set_xscale('log')
            ax_diff.grid(True, which='both', alpha=0.3)

        # ------------------------------------------------------------------
        # TITLE (unchanged logic)
        # ------------------------------------------------------------------
        if location.startswith("as_") or location.startswith("as"):
            loc_type = "as"
        elif "-" in location:
            loc_type = "oever"
        else:
            loc_type = None

        title = f"Location: {location}"
        if loc_type:
            title += f" ({loc_type})"
        if watersysteem:
            title += f" - {watersysteem}"

        ax.set_title(title, fontsize=12, fontweight='bold')

        # ------------------------------------------------------------------
        # LEGEND (only once, on top plot)
        # ------------------------------------------------------------------
        handles, labels = ax.get_legend_handles_labels()
        items = [(order_dict.get(label, 999), label, handle)
                for label, handle in zip(labels, handles)]
        items.sort(key=lambda x: x[0])

        sorted_labels = [item[1] for item in items]
        sorted_handles = [item[2] for item in items]

        ax.legend(sorted_handles, sorted_labels, loc='upper left', fontsize=9)

        plt.tight_layout()

        filename = f"TT_{watersysteem}_{location}_{parameter_name}.png"
        plt.savefig(rf"{save_dir}\{filename}", dpi=150, bbox_inches='tight')
        print(f"Plot saved as '{filename}'")

        plt.close()


    # Optionally show all plots at the end
    # plt.show()

# if __name__ == "__main__":
    # Example usage:
    # Onderstaande regel plot terugkeertijden van de gegeven locaties en rekeninstellingen
    # main_frequentielijn(watersysteem = 'Maas', simulation_types = ["2017-fysica-zon_WS", "2023-totaal-met_WS", "2017-totaal-zon_WS"], locations = ['036-01_0050_MA_km0160'], save_dir= r"C:\Users\Molendijk\Documents\Bestanden lokaal 5542.10\Visualisaties")
    # Onderstaande regel plot terugkeertijden van waterstand ('WS') voor alle locaties van de Maas (zowel oever als as) en voor elke rekeninstelling.
    #main_frequentielijn(watersysteem = 'Maas', parameter='WS', company_name= "HKV")
    # main_frequentielijn(watersysteem = 'Maas', parameter='WS', location_type=["oever"],locations = ['036-01_0050_MA_km0160'],company_name= "W+B")

