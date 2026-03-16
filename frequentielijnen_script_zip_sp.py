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
from pathlib import PurePosixPath

from utils.readers import read_hfreq_file_new
from utils.directories import get_parameter_file_paths

from utils.plotting_settings import colors_dict, legend_dict, parameters, order_dict, annotate_BOI_higher_lower

def main_frequentielijn(files, watersysteem = None, simulation_types = None, reference_name = 'BI2023-totB2023-met', company_name = 'HKV', location_type = ['as', 'oever'], locations = None, parameter = None, colors_dict = colors_dict, save_dir = None):
    """
    Main function to read and plot hfreq data.
    
    Args:
        files (list): List of file paths to (h)freq.txt files. These can be paths inside zip files, in the format "zip_path\\internal_path".
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
    
    # data_by_location[locationname][simulation_type] = (frequency, values), e.g. data_by_location['014-01_0017_HY_km0001']['2017-fysica-zon_HBN]


    data_by_location = defaultdict(dict)

    for file in files:

        zip_index = file.lower().find(".zip")
        internal_path = file[zip_index + 5:]

        from pathlib import PurePosixPath
        p = PurePosixPath(internal_path)

        simulation_folder = p.parts[1]

        location = simulation_folder.split("_BI")[0]
        simulation_type = "BI" + simulation_folder.split("_BI")[1]

        # Remove parameter suffix (_ws, _hs, etc.)
        sim_type_base = simulation_type[:-3]

        # Apply filters safely
        if (simulation_types is None or sim_type_base in simulation_types) and \
        (locations is None or location in locations):

            print("ADDING:", location, simulation_type)
            data_by_location[location][simulation_type] = read_hfreq_file_new(file)
        # All data we want to plot has been collected, now we move on to plotting.
        #######################################################

    # Create separate plot for each location
    for location, computations in sorted(data_by_location.items()):

        #reference_name = reference_name
        #reference_name = [i for i in list(computations.keys()) if  i.split('_')[0] == reference_name]
        has_reference = bool(reference_name)
        #reference_name = reference_name[0] # Spaghetti code ten top dit

        parameter_name = list(computations.keys())[0].split('_')[-1]
        ylabel = parameters[parameter_name][0]

        # --- Create figure (1 or 2 panels depending on availability reference)
        if has_reference:
            fig, (ax, ax_diff) = plt.subplots(
                2, 1, figsize=(8, 8), sharex=True,
                gridspec_kw={'height_ratios': [3, 2]}
            )
            ax.axvspan(10, 100, alpha=0.2, color = 'gray')  # licht grijs tussen 10 en 100 jaar
            ax_diff.axvspan(10, 100, alpha=0.2, color = 'gray')  # licht grijs tussen 10 en 100 jaar

            ylabel_diff = parameters[parameter_name][1]
            ylabel_diff_unit = parameters[parameter_name][4]

            if set(['BI2017-totB2017-met','BI2023-totB2023-met', 'BI2017-totB2017-zon','BI2023-totB2023-zon']) == set(simulation_types) and reference_name == 'BI2023-totB2023-met':
                filename_addition = "totaal-boi-met"
                ylabel_plot_diff = rf"Verschil in {ylabel_diff} t.o.v. BOI-met ({ylabel_diff_unit})"
                diff_simulations = ['BI2017-totB2017-met','BI2023-totB2023-met']
            elif set(['BI2017-totB2017-met','BI2023-totB2023-met', 'BI2017-totB2017-zon','BI2023-totB2023-zon']) == set(simulation_types) and reference_name == 'BI2023-totB2023-zon':
                filename_addition = "totaal-boi-zon"
                ylabel_plot_diff = rf"Verschil in {ylabel_diff} t.o.v. BOI-zon ({ylabel_diff_unit})"
                diff_simulations = ['BI2017-totB2017-zon','BI2023-totB2023-zon']
            #elif set(['BI2017-totB2017-met','BI2023-totB2023-met']) == set(simulation_types) and reference_name == 'BI2017-totB2017-met':
            #    filename_addition = "totaal-wbi-met"
            #    ylabel_plot_diff = rf"Verschil in {ylabel_diff} t.o.v. WBI ({ylabel_diff_unit})"
            else:
                filename_addition = "detail-boi-zon"
                ylabel_plot_diff = rf"Verschil in {ylabel_diff} t.o.v. BOI-zon ({ylabel_diff_unit})"
                diff_simulations = simulation_types
        else:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax_diff = None  # no difference plot
            ax.axvspan(10, 100, alpha=0.2, color = 'gray')  # licht grijs tussen 10 en 100 jaar

        # ------------------------------------------------------------------
        # Prepare reference data (needed for difference plot)
        # ------------------------------------------------------------------
        if has_reference:
            key = f"{reference_name}_ws"
            ref_frequency, ref_wl = computations[key]
            ref_T = 1.0 / ref_frequency

            # ensure increasing order for interpolation
            sort_idx = np.argsort(ref_T)
            ref_T = ref_T[sort_idx]
            ref_wl = ref_wl[sort_idx]

        # ------------------------------------------------------------------
        # Plot all computations (TOP FIGURE)
        # ------------------------------------------------------------------
        for computation_name, (frequency, water_level) in sorted(computations.items()):
            color = colors_dict[computation_name.split('_')[0]][0]
            legend_name = legend_dict[computation_name.split('_')[0]]
            linewidth = colors_dict[computation_name.split('_')[0]][1]
            linestyle = colors_dict[computation_name.split('_')[0]][2]
            return_period = 1.0 / frequency

            ax.plot(return_period, water_level,
                    label=legend_name, linewidth=linewidth,
                    color=color, linestyle=linestyle)

            # ------------------------------------------------------------------
            # DIFFERENCE PLOT (if reference exists and not the reference itself)
            # ------------------------------------------------------------------
            if has_reference and computation_name[:-3] in diff_simulations:
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
        ax.set_xlabel("Terugkeertijd (jaar)", fontsize=11)
        ax.set_ylabel(f"{ylabel}", fontsize=11)
        ax.set_xlim(10, 10e5)
        ax.set_xscale('log')
        ax.grid(True, which='both', alpha=0.3)
        ax.yaxis.set_minor_locator(plt.MultipleLocator(0.5))

        ylimits = ax.get_ylim()
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

        ax.axvspan(10, 100, alpha=0.3, color = 'white',zorder=10)  # licht grijs tussen 10 en 100 jaar

        # ------------------------------------------------------------------
        # DIFFERENCE AXIS FORMATTING
        # ------------------------------------------------------------------
        
        if has_reference:
            #ax_diff.set_title('Verschil t.o.v. BOI', fontsize = 12)
            color = colors_dict[reference_name.split('_')[0]][0]
            linewidth = colors_dict[reference_name.split('_')[0]][1]
            linestyle = colors_dict[reference_name.split('_')[0]][2]
            ax_diff.axhline(0.0, color=color, linestyle=linestyle, linewidth=0.5)
            ax_diff.set_ylabel(ylabel_plot_diff, fontsize=11)
            ax_diff.set_xlabel("Terugkeertijd (jaar)", fontsize=11)
            ax_diff.set_xscale('log')
            ax_diff.grid(True, which='both', alpha=0.3)
            
            # Annotate BOI higher/lower
            # annotate_BOI_higher_lower(ax_diff)
            ax_diff.axvspan(10, 100, alpha=0.3, color = 'white',zorder=10)  # licht grijs tussen 10 en 100 jaar
            ax_diff.yaxis.set_minor_locator(plt.MultipleLocator(0.1))

        # ------------------------------------------------------------------
        # TITLE (unchanged logic)
        # ------------------------------------------------------------------
        if location.startswith("as_") or location.startswith("as"):
            loc_type = "as"
        elif "-" in location:
            loc_type = "oever"
        else:
            loc_type = None

        title = f"Locatie: {location}"
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

        legend = ax.legend(sorted_handles, sorted_labels, loc='upper left', fontsize=7)
        legend.set_zorder(11)

        plt.tight_layout()

        filename = f"{location}_{parameter_name}_{filename_addition}.png"
        
        # Create directory if it does not exist
        os.makedirs(save_dir, exist_ok=True)

        plt.savefig(os.path.join(save_dir, filename), dpi=150, bbox_inches='tight')
        print(f"Plot saved as '{filename}'")

        plt.close()

    # Optionally show all plots at the end
    plt.show()

if __name__ == "__main__":
    # Example usage:
    # Onderstaande regel plot terugkeertijden van de gegeven locaties en rekeninstellingen
    # main_frequentielijn(watersysteem = 'Maas', simulation_types = ["2017-fysica-zon_WS", "2023-totaal-met_WS", "2017-totaal-zon_WS"], locations = ['036-01_0050_MA_km0160'], save_dir= r"C:\Users\Molendijk\Documents\Bestanden lokaal 5542.10\Visualisaties")
    # Onderstaande regel plot terugkeertijden van waterstand ('WS') voor alle locaties van de Maas (zowel oever als as) en voor elke rekeninstelling.
    #main_frequentielijn(watersysteem = 'Maas', parameter='WS', company_name= "HKV")

    sp_base_path = r"c:\Users\BEMC\HKV\PR5542.10 - BOI - Verschilanalyse Hydraulische Belastingen - Projectuitvoering - Projectuitvoering"
    project_fase = 'WP02a Beoordelen BOR - Rijntakken'
    som_versie = 'aslocaties - concept_20260219'
    location_type = 'as'
    watersysteem = '' # leeg laten als er maar 1 watersysteem is voor dit WP, b.v. Meren kan dit MRN_Grevelingen zijn, maar Rijntakken heeft alleen de Rijntakken - dus dan leeg.
    zip_file_name = "HydraNL_BI2023_BOR_Rijn_as.zip" # naam van het zip bestand waarin de data staat, b.v. "HydraNL_BI2023_BOR_Rijn_as.zip" of "HydraNL_BI2023_BOR_Meren.zip"

    parameter = 'ws'
    locations = None # maar kan ook individuele locaties hebben in een lijst b.v. ['vk204b_0234_MM_hm0526']
    #simulation_types = ['BI2017-totB2017-zon','BI2017-totB2017-met','BI2023-totB2023-zon','BI2023-totB2023-met','BI2023-fysB2017-zon', 'BI2023-stkB2017-zon'] # welke simulatie types we willen hebbem
    simulation_types = ['BI2017-totB2017-met','BI2023-totB2023-met','BI2017-totB2017-zon','BI2023-totB2023-zon'] # welke simulatie types we willen hebbem
    
    #Bestanden ophalen
    files = get_parameter_file_paths(sp_base_path = sp_base_path, project_fase = project_fase, som_versie = som_versie, watersysteem = watersysteem, zip_file_name = zip_file_name, parameter = parameter) 

    save_dir = os.path.join(sp_base_path, project_fase, "Visualisaties", som_versie, watersysteem, "frequentielijnen_new", location_type) # opslaan in een submap van de map 

    main_frequentielijn(files, watersysteem = watersysteem, simulation_types = simulation_types, reference_name = 'BI2023-totB2023-met',
                        parameter = parameter, location_type = location_type, locations = ['as_0061_RH_km0854'], save_dir = save_dir)

    main_frequentielijn(files, watersysteem = watersysteem, simulation_types = simulation_types, reference_name = 'BI2023-totB2023-zon',
                        parameter = parameter, location_type = location_type, locations = ['as_0061_RH_km0854'], save_dir = save_dir)

    simulation_types = ['BI2023-totB2023-zon','BI2023-fysB2017-zon', 'BI2023-stkB2017-zon'] # welke simulatie types we willen hebbem
    main_frequentielijn(files, watersysteem = watersysteem, simulation_types = simulation_types, reference_name = 'BI2023-totB2023-zon',
                            parameter = parameter, location_type = location_type, locations = ['as_0061_RH_km0854'], save_dir = save_dir)
