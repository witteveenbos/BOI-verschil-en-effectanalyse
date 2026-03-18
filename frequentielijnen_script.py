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

from utils.plotting_settings import colors_dict, legend_dict, parameters, order_dict, annotate_BOI_higher_lower

<<<<<<< Updated upstream
def main_frequentielijn(watersysteem = None, simulation_types = None, company_name = 'HKV', location_type = ['as', 'oever'], locations = None, parameter = None, colors_dict = colors_dict):
=======
def get_group(name):
    if 'met' in name:
        return 'met'
    elif 'zon' in name:
        return 'zon'
    else:
        return None

def main_frequentielijn(files, watersysteem = None, simulation_types = None, reference_name = 'BI2023-totB2023-met', locations = None, colors_dict = colors_dict, save_dir = None, add_bars = False, select_return_period = None):
>>>>>>> Stashed changes
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
    base_path = rf"{directory_path}\HydraNL_BI2023_{prefix}_{watersysteem}"

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
                    if (simulation_types == None and item.name.endswith(parameter)) or (simulation_types != None and 'BI'+item.name.split('_BI')[-1][:-3] in simulation_types): #-3 omdat we de laatste 3 tekens van de naam moeten afhalen om bij de rekeninstelling te komen (bijv. '_ws') - geen geweldige oplossing
                        # Look in the uitvoer-map of this location, find the .txt file which contains the output of HydraNL
                        uitvoer_loc_path = path / item.name / 'uitvoer'
                        for file in uitvoer_loc_path.iterdir():
                            if file.name.endswith('.txt'):
                                temp_path = uitvoer_loc_path / file.name
                                data_by_location[item.name.split('_BI')[0]]['BI'+item.name.split('_BI')[-1]] = read_hfreq_file(rf"{temp_path}")

    # All data we want to plot has been collected, now we move on to plotting.
    #######################################################

<<<<<<< Updated upstream
    # Create separate plot for each location
=======
        p = PurePosixPath(internal_path)

        simulation_folder = p.parts[1]

        location = simulation_folder.split("_BI")[0]
        simulation_type = "BI" + simulation_folder.split("_BI")[1]

        # Remove parameter suffix (_ws, _hs, etc.)
        sim_type_base = simulation_type[:-3]

        # Apply filters safely
        if (simulation_types is None or sim_type_base in simulation_types or add_bars) and \
        (locations is None or location in locations):

            print("ADDING:", location, simulation_type)
            data_by_location[location][simulation_type] = read_hfreq_file_new(file)
        # All data we want to plot has been collected, now we move on to plotting.

    ## 2. Create separate plot for each location
>>>>>>> Stashed changes
    for location, computations in sorted(data_by_location.items()):

        reference_name = 'BI2023-totB2023-met'
        reference_name = [i for i in list(computations.keys()) if  i.split('_')[0] == reference_name]
        has_reference = bool(reference_name)
        reference_name = reference_name[0] # Spaghetti code ten top dit

        parameter_name = list(computations.keys())[0].split('_')[1]
        ylabel = parameters[parameter_name][0]

        # --- Create figure (1 or 2 panels depending on availability reference)
        if has_reference:
<<<<<<< Updated upstream
            fig, (ax, ax_diff) = plt.subplots(
                2, 1, figsize=(8, 8), sharex=True,
                gridspec_kw={'height_ratios': [3, 2]}
            )
            ax.axvspan(10, 100, alpha=0.2, color = 'gray')  # licht grijs tussen 10 en 100 jaar
            ax_diff.axvspan(10, 100, alpha=0.2, color = 'gray')  # licht grijs tussen 10 en 100 jaar
=======
            if add_bars:
                fig = plt.figure(figsize=(8, 12))
                gs = fig.add_gridspec(3, 1, height_ratios=[3, 2, 2])

                ax = fig.add_subplot(gs[0])
                ax_diff = fig.add_subplot(gs[1], sharex=ax)   # deelt x-as met ax
                ax_bar = fig.add_subplot(gs[2])               # onafhankelijk
                ylabel_bar = parameters[parameter_name][1]
                ylabel_bar_unit = parameters[parameter_name][4]
            else:
                fig, (ax, ax_diff) = plt.subplots(
                    2, 1, figsize=(8, 8), sharex=True,
                    gridspec_kw={'height_ratios': [3, 2]}
                )
            ax.axvspan(10, 100, alpha=0.1, color = 'gray')  # licht grijs tussen 10 en 100 jaar
            ax_diff.axvspan(10, 100, alpha=0.1, color = 'gray')  # licht grijs tussen 10 en 100 jaar
>>>>>>> Stashed changes

            ylabel_diff = parameters[parameter_name][1]
            ylabel_diff_unit = parameters[parameter_name][4]

        else:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax_diff = None  # no difference plot
            ax.axvspan(10, 100, alpha=0.2, color = 'gray')  # licht grijs tussen 10 en 100 jaar

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

<<<<<<< Updated upstream
        # ------------------------------------------------------------------
        # Plot all computations (TOP FIGURE)
        # ------------------------------------------------------------------
=======
            for ref in reference_name:

                # Determine group
                group = get_group(ref)

                key = f"{ref}_{parameter_name}"
                if key not in computations:
                    continue

                ref_frequency, ref_wl = computations[key]
                ref_T = 1.0 / ref_frequency

                sort_idx = np.argsort(ref_T)
                ref_T = ref_T[sort_idx]
                ref_wl = ref_wl[sort_idx]

                # Store reference curve AND its style
                color = colors_dict[ref][0]
                linewidth = colors_dict[ref][1]
                linestyle = colors_dict[ref][2]
                order = order_dict[legend_dict[ref]]

                group_references[group] = (ref_T, ref_wl, color, linestyle, linewidth, order)

        ## 2.3 Prepare contributions for bar chart (OPTIONAL)
        if add_bars:
            contributions = {}

            # Calculate water level at desired return period
            for computation_name, (frequency, water_level) in computations.items():
                computation_name = computation_name.split('_')[0]
                if computation_name in ['BI2023-fysB2017-zon', 'BI2023-stkB2017-zon', 'BI2023-rknB2017-zon', 'BI2017-totB2017-zon', 'BI2017-totB2017-met', 'BI2023-totB2023-zon', 'BI2023-totB2023-met']:
                    T = 1.0 / frequency
                    wl_interp = np.interp(np.log(select_return_period), np.log(T), water_level) # logaritmic interpolation
                    contributions[computation_name] = wl_interp

            # Calculate contributions 
            fys_contr = contributions['BI2023-fysB2017-zon'] - contributions['BI2023-totB2023-zon']
            stk_contr = contributions['BI2023-stkB2017-zon'] - contributions['BI2023-totB2023-zon']
            rkn_contr = contributions['BI2023-rknB2017-zon'] - contributions['BI2023-totB2023-zon']
            tot_zon_contr = contributions['BI2017-totB2017-zon'] - contributions['BI2023-totB2023-zon']
            tot_met_contr = contributions['BI2017-totB2017-met'] - contributions['BI2023-totB2023-met']
            riskeer_contr = contributions['BI2017-totB2017-met'] - contributions['BI2023-totB2023-met'] + 0.05  # nog niet bepaald, voorlopig 5 cm erbij

            # Save contributions to a dictionary for later use in plotting
            contributions_dict = {
                'Fysica': {'value': fys_contr, 'color': colors_dict['BI2023-fysB2017-zon'][0]},
                'Statistiek': {'value': stk_contr, 'color': colors_dict['BI2023-stkB2017-zon'][0]},
                'Rekeninstellingen': {'value': rkn_contr, 'color': colors_dict['BI2023-rknB2017-zon'][0]},
                'Totaal zonder ': {'value': tot_zon_contr, 'color': colors_dict['BI2017-totB2017-zon'][0]},
                'Totaal met': {'value': tot_met_contr, 'color': colors_dict['BI2017-totB2017-met'][0]},
                'Riskeer': {'value': riskeer_contr, 'color': 'purple'}
            }


        ## 2.4 Plotting routine loop over all computations for this location
>>>>>>> Stashed changes
        for computation_name, (frequency, water_level) in sorted(computations.items()):
            color = colors_dict[computation_name.split('_')[0]][0]
            legend_name = legend_dict[computation_name.split('_')[0]]
            linewidth = colors_dict[computation_name.split('_')[0]][1]
            linestyle = colors_dict[computation_name.split('_')[0]][2]
            return_period = 1.0 / frequency

<<<<<<< Updated upstream
            ax.plot(return_period, water_level,
                    label=legend_name, linewidth=linewidth,
                    color=color, linestyle=linestyle)

            # ------------------------------------------------------------------
            # DIFFERENCE PLOT (if reference exists and not the reference itself)
            # ------------------------------------------------------------------
            if has_reference and computation_name != reference_name:
=======
            # 2.4.1 top as
            if computation_name.split('_')[0] in simulation_types:
                ax.plot(return_period, water_level,
                        label=legend_name, linewidth=linewidth,
                        color=color, linestyle=linestyle, zorder=order)

            # 2.4.2 bottom as
            if has_reference and computation_name.split('_')[0] in simulation_types:
>>>>>>> Stashed changes

                # sort for interpolation
                sort_idx = np.argsort(return_period)
                T_sorted = return_period[sort_idx]
                wl_sorted = water_level[sort_idx]

                # interpolate this computation onto reference T-grid
                wl_interp = np.interp(ref_T, T_sorted, wl_sorted)

                diff = ref_wl - wl_interp

                ax_diff.plot(ref_T, diff,
                            color=color, linestyle=linestyle,
                            linewidth=linewidth, label=legend_name)

<<<<<<< Updated upstream
        # ------------------------------------------------------------------
        # TOP AXIS FORMATTING  (your original styling)
        # ------------------------------------------------------------------
=======
                    sort_idx = np.argsort(return_period)
                    T_sorted = return_period[sort_idx]
                    wl_sorted = water_level[sort_idx]

                    wl_interp = np.interp(ref_T, T_sorted, wl_sorted)
                    diff = wl_interp - ref_wl

                    ax_diff.plot(ref_T, diff,
                                color=color,
                                linestyle=linestyle,
                                linewidth=linewidth,
                                label=legend_name,
                                zorder=order)
        
        # 2.4.3 add bar chart for contributions at selected return period (OPTIONAL)
        if add_bars:
            ax_bar.bar(contributions_dict.keys(), [contributions_dict[key]['value'] for key in contributions_dict.keys()],
                       color=[contributions_dict[key]['color'] for key in contributions_dict.keys()], 
                       edgecolor="black", linewidth = 0.8, width = 0.55, zorder = 2)

        # 2.4.4 top as formatting
>>>>>>> Stashed changes
        ax.set_xlabel("Terugkeertijd (jaar)", fontsize=11)
        ax.set_ylabel(f"{ylabel}", fontsize=11)
        ax.set_xlim(10, 10e5)
        ax.set_xscale('log')
        ax.grid(True, which='both', alpha=0.3)
        ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

<<<<<<< Updated upstream
        # ylim logic unchanged
=======
        # 2.4.5 ylim logic 
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
        ax.axvspan(10, 100, alpha=0.3, color = 'white',zorder=10)  # licht grijs tussen 10 en 100 jaar

        # ------------------------------------------------------------------
        # DIFFERENCE AXIS FORMATTING
        # ------------------------------------------------------------------
=======
        ## 2.4.6 bottom as plotting of difference lines and formatting of difference axis
>>>>>>> Stashed changes
        if has_reference:
            #ax_diff.set_title('Verschil t.o.v. BOI', fontsize = 12)
            ax_diff.axhline(0.0, color='red', linewidth=1.5)
            ax_diff.set_ylabel(rf"Verschil in {ylabel_diff} t.o.v. BOI ({ylabel_diff_unit})", fontsize=11)
            ax_diff.set_xlabel("Terugkeertijd (jaar)", fontsize=11)
            ax_diff.set_xscale('log')
            ax_diff.grid(True, which='both', alpha=0.3)
<<<<<<< Updated upstream

            # Annotate BOI higher/lower
            annotate_BOI_higher_lower(ax_diff)
            ax_diff.axvspan(10, 100, alpha=0.3, color = 'white',zorder=10)  # licht grijs tussen 10 en 100 jaar


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
=======
            
            # Annotate BOI higher/lower
            # annotate_BOI_higher_lower(ax_diff) - staat nu uit
            ax_diff.yaxis.set_minor_locator(plt.MultipleLocator(0.1))
        
        # 2.4.7 bar chart formatting
        if add_bars:
            ax_bar.axhline(0.0, color='black', linewidth=1.5, zorder=0)
            ax_bar.set_ylabel(rf"Verschil in {ylabel_bar} t.o.v. BOI ({ylabel_bar_unit})", fontsize=11)
            ax_bar.grid(True, axis='y', alpha=0.3, zorder = 0)

            labels = list(contributions_dict.keys())
            import textwrap
            wrapped_labels = [textwrap.fill(label, width=20) for label in labels]
            ax_bar.set_xticklabels(wrapped_labels)
            ax_bar.set_title(f"Individuele bijdrage bij T = {select_return_period} jaar", fontsize=12, fontweight='bold')
            # ax_diff.set_xticklabels(ax_diff.get_xticks())  # Zorg dat labels zichtbaar blijven
            # ax_diff.set_xlabel("Terugkeertijd (jaar)", fontsize=11)

        # 2.4.6 titel met locatie en/of watersysteem
        title = f"Locatie: {location}"
>>>>>>> Stashed changes
        if watersysteem:
            title += f" - {watersysteem}"

        ax.set_title(title, fontsize=12, fontweight='bold')

<<<<<<< Updated upstream
        # ------------------------------------------------------------------
        # LEGEND (only once, on top plot)
        # ------------------------------------------------------------------
=======
        # 2.4.7 legenda, iets ingewikkelder dan normaal, we willen een specifieke volgorde van legenda items
>>>>>>> Stashed changes
        handles, labels = ax.get_legend_handles_labels()
        items = [(order_dict.get(label, 999), label, handle)
                for label, handle in zip(labels, handles)]
        items.sort(key=lambda x: x[0])

        sorted_labels = [item[1] for item in items]
        sorted_handles = [item[2] for item in items]

        legend = ax.legend(sorted_handles, sorted_labels, loc='upper left', fontsize=7)
        legend.set_zorder(11)

<<<<<<< Updated upstream
=======
        ## 2.5 plot afronden en opslaan
>>>>>>> Stashed changes
        plt.tight_layout()

        filename = f"TT_{watersysteem}_{location}_{parameter_name}.png"
        plt.savefig(rf"{save_dir}\{filename}", dpi=150, bbox_inches='tight')
        print(f"Plot saved as '{filename}'")

        plt.close()

    # Optionally show all plots at the end
    plt.show()

if __name__ == "__main__":
    # Example usage:
<<<<<<< Updated upstream
    # Onderstaande regel plot terugkeertijden van de gegeven locaties en rekeninstellingen
    # main_frequentielijn(watersysteem = 'Maas', simulation_types = ["2017-fysica-zon_WS", "2023-totaal-met_WS", "2017-totaal-zon_WS"], locations = ['036-01_0050_MA_km0160'], save_dir= r"C:\Users\Molendijk\Documents\Bestanden lokaal 5542.10\Visualisaties")
    # Onderstaande regel plot terugkeertijden van waterstand ('WS') voor alle locaties van de Maas (zowel oever als as) en voor elke rekeninstelling.
    #main_frequentielijn(watersysteem = 'Maas', parameter='WS', company_name= "HKV")
    main_frequentielijn(watersysteem = 'Rijn', simulation_types = ['BI2017-totB2017-zon','BI2017-totB2017-met','BI2023-totB2023-zon','BI2023-totB2023-met','BI2023-fysB2017-zon', 'BI2023-stkB2017-zon'], parameter='ws', location_type=["as"],locations = ['as_0061_RH_km0854'],company_name= "W+B")

=======
    # 0.1 instellingen voor dit script
    sp_base_path = r"c:\Users\BEMC\HKV\PR5542.10 - BOI - Verschilanalyse Hydraulische Belastingen - Projectuitvoering - Projectuitvoering"
    sp_base_path = r"c:\Users\Kuiper\OneDrive - HKV\PR5542.10 - BOI - Verschilanalyse Hydraulische Belastingen - Projectuitvoering - Projectuitvoering"
    project_fase = 'WP02a Beoordelen BOR - Rijntakken'
    som_versie = 'aslocaties - concept_20260219'
    watersysteem = '' # leeg laten als er maar 1 watersysteem is voor dit WP, b.v. Meren kan dit MRN_Grevelingen zijn, maar Rijntakken heeft alleen de Rijntakken - dus dan leeg.
    zip_file_name = "HydraNL_BI2023_BOR_Rijn_as.zip" # naam van het zip bestand waarin de data staat, b.v. "HydraNL_BI2023_BOR_Rijn_as.zip" of "HydraNL_BI2023_BOR_Meren.zip"

    parameter = 'ws' # parameter waarvoor we de frequentielijnen willen plotten, b.v. 'ws' of 'hs'
    locations = None # maar kan ook individuele locaties hebben in een lijst b.v. ['vk204b_0234_MM_hm0526'], ['as_0061_RH_km0854']

    # locatie van opslaan van figuren    
    save_dir = os.path.join(sp_base_path, project_fase, "Visualisaties", som_versie, watersysteem, "test") #"fl2", opslaan in een submap van de map 

    # 0.2 Bestanden ophalen, we listen gewoon alle bestanden uit de zip met een bepaalde parameter
    files = get_parameter_file_paths(sp_base_path = sp_base_path, project_fase = project_fase, som_versie = som_versie, watersysteem = watersysteem, zip_file_name = zip_file_name, parameter = parameter) 

    # 1. eerste frequentielijn plot actie met totaal BOI WBI vergelijking, zowel met als zonder modelonzekerheid
    simulation_types = ['BI2017-totB2017-met','BI2023-totB2023-met','BI2017-totB2017-zon','BI2023-totB2023-zon'] # welke simulatie types we willen hebbem
    main_frequentielijn(files, watersysteem = watersysteem, simulation_types = simulation_types, reference_name = ['BI2023-totB2023-zon','BI2023-totB2023-met'],
                        locations = ['as_0171_BR_km0865'], save_dir = save_dir, add_bars = True, select_return_period = 10000)

    # 2. tweede frequentielijn plot actie met detail BOI vergelijking, waarbij we de verschillende BOI simulaties vergelijken met elkaar (dus zonder de WBI2017 referentie)
    simulation_types = ['BI2023-totB2023-zon','BI2023-fysB2017-zon', 'BI2023-stkB2017-zon'] # welke simulatie types we willen hebben voor de detail-boi-zon vergelijking, alleen de zon simulaties omdat we vergelijken met de zon referentie
    main_frequentielijn(files, watersysteem = watersysteem, simulation_types = simulation_types, reference_name = 'BI2023-totB2023-zon',
                        locations = ['as_0171_BR_km0865'], save_dir = save_dir)
>>>>>>> Stashed changes
