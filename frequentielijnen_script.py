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
from collections import defaultdict
from pathlib import PurePosixPath
import textwrap

from utils.readers import read_hfreq_file_new
from utils.directories import get_parameter_file_paths

from utils.plotting_settings import colors_dict, legend_dict, parameters, order_dict, annotate_BOI_higher_lower

def get_group(name):
    if 'met' in name:
        return 'met'
    elif 'zon' in name:
        return 'zon'
    else:
        return None

def safe_diff(dict_obj, key_a, key_b):
    """Return difference if both keys exist, otherwise None"""
    if key_a in dict_obj and key_b in dict_obj:
        return dict_obj[key_a] - dict_obj[key_b]
    return None

def add_interpolated_return_period_point(return_period, values, target_return_period):
    """Insert an interpolated point at the requested return period for plotting."""
    sort_idx = np.argsort(return_period)
    T_sorted = return_period[sort_idx]
    values_sorted = values[sort_idx]

    if target_return_period is None:
        return T_sorted, values_sorted

    if np.any(np.isclose(T_sorted, target_return_period, rtol=0.0, atol=1e-9)):
        return T_sorted, values_sorted

    if target_return_period <= T_sorted[0] or target_return_period >= T_sorted[-1]:
        return T_sorted, values_sorted

    interpolated_value = np.interp(
        np.log(target_return_period),
        np.log(T_sorted),
        values_sorted
    )
    insert_idx = np.searchsorted(T_sorted, target_return_period)

    T_with_target = np.insert(T_sorted, insert_idx, target_return_period)
    values_with_target = np.insert(values_sorted, insert_idx, interpolated_value)

    return T_with_target, values_with_target

def main_frequentielijn(files, watersysteem = None, simulation_types = None, reference_name = 'BI2023-totB2023-met', locations = None, colors_dict = colors_dict, save_dir = None, add_bars = False, select_return_period = 10000):
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
        colors_dict (dict) : Maps simulation_type to a plotting color.
                                If none is given, a standard template is used which is read from utils.plotting_settings.

    """
    ## 1. Prepare data structure for storing data by location and simulation type
    data_by_location = defaultdict(dict)

    for file in files:

        zip_index = file.lower().find(".zip")
        internal_path = file[zip_index + 5:]

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
    for location, computations in sorted(data_by_location.items()):

        has_reference = bool(reference_name)
        parameter_name = list(computations.keys())[0].split('_')[-1]
        ylabel = parameters[parameter_name][0]

        ## 2.1 Prepare figure and axes
        if has_reference:
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

            ylabel_diff = parameters[parameter_name][1]
            ylabel_diff_unit = parameters[parameter_name][4]

            if set(['BI2017-totB2017-met','BI2023-totB2023-met', 'BI2017-totB2017-zon','BI2023-totB2023-zon']) == set(simulation_types) and set(reference_name) == set(['BI2023-totB2023-met', 'BI2023-totB2023-zon']):
                filename_addition = "totaal-boi"
                ylabel_plot_diff = rf"Verschil in {ylabel_diff} t.o.v. BOI ({ylabel_diff_unit})"
                diff_simulations = ['BI2017-totB2017-met','BI2023-totB2023-met']
            # elif set(['BI2017-totB2017-met','BI2023-totB2023-met', 'BI2017-totB2017-zon','BI2023-totB2023-zon']) == set(simulation_types) and reference_name == 'BI2023-totB2023-zon':
            #     filename_addition = "totaal-boi-zon"
            #     ylabel_plot_diff = rf"Verschil in {ylabel_diff} t.o.v. BOI-zon ({ylabel_diff_unit})"
            #     diff_simulations = ['BI2017-totB2017-zon','BI2023-totB2023-zon']
            else:
                filename_addition = "detail-boi-zon"
                ylabel_plot_diff = rf"Verschil in {ylabel_diff} t.o.v. BOI ({ylabel_diff_unit})"
                diff_simulations = simulation_types

        else:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax_diff = None  # no difference plot
            ax.axvspan(10, 100, alpha=0.2, color = 'gray')  # licht grijs tussen 10 en 100 jaar

        ## 2.2 Prepare reference data (grouped by 'met' and 'zon')
        group_references = {}  # {'met': (ref_T, ref_wl, color, linestyle, linewidth)}
        
        if has_reference:

            # Always treat reference_name as list
            if isinstance(reference_name, str):
                reference_name = [reference_name]

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
                    sort_idx = np.argsort(T)
                    T_sorted = T[sort_idx]
                    wl_sorted = water_level[sort_idx]
                    wl_interp = np.interp(np.log(select_return_period), np.log(T_sorted), wl_sorted) # logaritmic interpolation

                    contributions[computation_name] = wl_interp

            fys_contr = safe_diff(contributions, 'BI2023-fysB2017-zon', 'BI2023-totB2023-zon')
            stk_contr = safe_diff(contributions, 'BI2023-stkB2017-zon', 'BI2023-totB2023-zon')
            rkn_contr = safe_diff(contributions, 'BI2023-rknB2017-zon', 'BI2023-totB2023-zon')
            tot_zon_contr = safe_diff(contributions, 'BI2017-totB2017-zon', 'BI2023-totB2023-zon')
            tot_met_contr = safe_diff(contributions, 'BI2017-totB2017-met', 'BI2023-totB2023-met')

            # Riskeer set to none
            riskeer_contr = None

            # --------------------------------------------------
            # Build dictionary only with available contributions
            # --------------------------------------------------

            contributions_dict = {}

            if fys_contr is not None:
                contributions_dict['WBI fysica'] = {
                    'value': fys_contr,
                    'color': colors_dict['BI2023-fysB2017-zon'][0]
                }

            if stk_contr is not None:
                contributions_dict['WBI statistiek'] = {
                    'value': stk_contr,
                    'color': colors_dict['BI2023-stkB2017-zon'][0]
                }

            if rkn_contr is not None:
                contributions_dict['WBI rekeninstellingen'] = {
                    'value': rkn_contr,
                    'color': colors_dict['BI2023-rknB2017-zon'][0]
                }

            if tot_zon_contr is not None:
                contributions_dict['Totaal zonder'] = {
                    'value': tot_zon_contr,
                    'color': colors_dict['BI2017-totB2017-zon'][0]
                }

            if tot_met_contr is not None:
                contributions_dict['Totaal met'] = {
                    'value': tot_met_contr,
                    'color': colors_dict['BI2017-totB2017-met'][0]
                }

            if riskeer_contr is not None:
                contributions_dict['Riskeer'] = {
                    'value': riskeer_contr,
                    'color': 'purple'
                }


        ## 2.4 Plotting routine loop over all computations for this location
        for computation_name, (frequency, water_level) in sorted(computations.items()):
            color, linewidth, linestyle = colors_dict.get(computation_name.split('_')[0])
            legend_name = legend_dict[computation_name.split('_')[0]]
            order = order_dict[legend_dict[computation_name.split('_')[0]]]

            return_period = 1.0 / frequency

            # 2.4.1 top as
            if computation_name.split('_')[0] in simulation_types:
                return_period_plot, water_level_plot = add_interpolated_return_period_point(return_period, water_level, select_return_period)

                ax.plot(return_period_plot, water_level_plot,
                        label=legend_name, linewidth=linewidth,
                        color=color, linestyle=linestyle, zorder=order)

            # 2.4.2 bottom as
            if has_reference and computation_name.split('_')[0] in simulation_types:

                # Determine group of this computation
                group = get_group(computation_name)

                # Only compute difference if this group has a reference
                if group in group_references:

                    ref_T, ref_wl, _, _, _, _ = group_references[group]

                    # Skip plotting difference for the reference itself
                    if computation_name.startswith(tuple(reference_name)):
                        continue

                    sort_idx = np.argsort(return_period)
                    T_sorted = return_period[sort_idx]
                    wl_sorted = water_level[sort_idx]

                    # bepaal ref_T_log en T_sorted_log en if select_return_period exists
                    ref_T_plot, ref_wl_plot = add_interpolated_return_period_point(ref_T, ref_wl, select_return_period)
                    T_sorted_plot, wl_sorted_plot = add_interpolated_return_period_point(T_sorted, wl_sorted, select_return_period)
                    wl_interp = np.interp(np.log(ref_T_plot), np.log(T_sorted_plot), wl_sorted_plot) # logaritmic interpolation
                    diff = wl_interp - ref_wl_plot

                    ax_diff.plot(ref_T_plot, diff,
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
        ax.set_xlabel("Terugkeertijd (jaar)", fontsize=11)
        ax.set_ylabel(f"{ylabel}", fontsize=11)
        ax.set_xlim(10, 10e5)
        ax.set_xscale('log')
        ax.grid(True, which='both', alpha=0.3)
        ax.yaxis.set_minor_locator(plt.MultipleLocator(0.5))

        # 2.4.5 ylim logic 
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

        ## 2.4.6 bottom as plotting of difference lines and formatting of difference axis
        if has_reference:
            #ax_diff.set_title('Verschil t.o.v. BOI', fontsize = 12)
            for group, (ref_T, ref_wl, color, linestyle, linewidth, order) in group_references.items():
                ax_diff.axhline(
                    0.0,
                    color=color,
                    linestyle=linestyle,
                    linewidth=linewidth,
                    zorder=order                    
                )
            ax_diff.set_ylabel(ylabel_plot_diff, fontsize=11)
            ax_diff.set_xlabel("Terugkeertijd (jaar)", fontsize=11)
            ax_diff.set_xscale('log')
            ax_diff.grid(True, which='both', alpha=0.3)
            
            # Annotate BOI higher/lower
            # annotate_BOI_higher_lower(ax_diff) - staat nu uit
            ax_diff.yaxis.set_minor_locator(plt.MultipleLocator(0.1))
        
        # 2.4.7 bar chart formatting
        if add_bars:
            ax_bar.axhline(0.0, color='black', linewidth=1.5, zorder=0)
            ax_bar.set_ylabel(rf"Verschil in {ylabel_bar} t.o.v. BOI ({ylabel_bar_unit})", fontsize=11)
            ax_bar.grid(True, axis='y', alpha=0.3, zorder = 0)

            labels = list(contributions_dict.keys())
            wrapped_labels = [textwrap.fill(label, width=20) for label in labels]
            ax_bar.set_xticklabels(wrapped_labels)
            ax_bar.set_title(f"Individuele bijdrage bij T = {select_return_period} jaar", fontsize=11)
            # ax_diff.set_xticklabels(ax_diff.get_xticks())  # Zorg dat labels zichtbaar blijven
            # ax_diff.set_xlabel("Terugkeertijd (jaar)", fontsize=11)

        # 2.4.6 titel met locatie en/of watersysteem
        title = f"Locatie: {location}"
        if watersysteem:
            title += f" - {watersysteem}"

        ax.set_title(title, fontsize=12, fontweight='bold')

        # 2.4.7 legenda, iets ingewikkelder dan normaal, we willen een specifieke volgorde van legenda items
        handles, labels = ax.get_legend_handles_labels()
        items = [(order_dict.get(label, 999), label, handle)
                for label, handle in zip(labels, handles)]
        items.sort(key=lambda x: x[0])

        sorted_labels = [item[1] for item in items]
        sorted_handles = [item[2] for item in items]

        legend = ax.legend(sorted_handles, sorted_labels, loc='upper left', fontsize=7)
        legend.set_zorder(11)

        ## 2.5 plot afronden en opslaan
        plt.tight_layout()

        # naam maken en directory controlerenen aanmaken indien nodig
        filename = f"{location}_{parameter_name}_{filename_addition}.png"
        os.makedirs(save_dir, exist_ok=True)

        plt.savefig(os.path.join(save_dir, filename), dpi=150, bbox_inches='tight')
        print(f"Plot saved as '{filename}'")

        plt.close()

    # Optionally show all plots at the end
    # plt.show()

if __name__ == "__main__":
    # Example usage:
    # 0.1 instellingen voor dit script
    sp_base_path = r"c:\Users\BEMC\HKV\PR5542.10 - BOI - Verschilanalyse Hydraulische Belastingen - Projectuitvoering - Projectuitvoering"
    sp_base_path = r"c:\Users\Kuiper\OneDrive - HKV\PR5542.10 - BOI - Verschilanalyse Hydraulische Belastingen - Projectuitvoering - Projectuitvoering"
    project_fase = 'WP02a Beoordelen Meren'
    som_versie = 'aslocaties - concept_20260316'
    watersysteem = 'MRN_Grevelingen' # leeg laten als er maar 1 watersysteem is voor dit WP, b.v. Meren kan dit MRN_Grevelingen zijn, maar Rijntakken heeft alleen de Rijntakken - dus dan leeg.
    zip_file_name = "HydraNL_BI2023_MRN_Grevelingen_as.zip" # naam van het zip bestand waarin de data staat, b.v. "HydraNL_BI2023_BOR_Rijn_as.zip" of "HydraNL_BI2023_BOR_Meren.zip"

    parameter = 'ws' # parameter waarvoor we de frequentielijnen willen plotten, b.v. 'ws' of 'hs'
    locations = None # maar kan ook individuele locaties hebben in een lijst b.v. ['vk204b_0234_MM_hm0526'], ['as_0061_RH_km0854']

    # locatie van opslaan van figuren    
    save_dir = os.path.join(sp_base_path, project_fase, "Visualisaties", som_versie, watersysteem, "test") #"fl2", opslaan in een submap van de map 

    # 0.2 Bestanden ophalen, we listen gewoon alle bestanden uit de zip met een bepaalde parameter
    files = get_parameter_file_paths(sp_base_path = sp_base_path, project_fase = project_fase, som_versie = som_versie, watersysteem = watersysteem, zip_file_name = zip_file_name, parameter = parameter) 

    # 1. eerste frequentielijn plot actie met totaal BOI WBI vergelijking, zowel met als zonder modelonzekerheid
    simulation_types = ['BI2017-totB2017-met','BI2023-totB2023-met','BI2017-totB2017-zon','BI2023-totB2023-zon'] # welke simulatie types we willen hebbem
    main_frequentielijn(files, watersysteem = watersysteem, simulation_types = simulation_types, reference_name = ['BI2023-totB2023-zon','BI2023-totB2023-met'],
                        locations = ['extra_0071_GR'], save_dir = save_dir, add_bars = True, select_return_period = 10000)

    # 2. tweede frequentielijn plot actie met detail BOI vergelijking, waarbij we de verschillende BOI simulaties vergelijken met elkaar (dus zonder de WBI2017 referentie)
    simulation_types = ['BI2023-totB2023-zon','BI2023-fysB2017-zon', 'BI2023-stkB2017-zon'] # welke simulatie types we willen hebben voor de detail-boi-zon vergelijking, alleen de zon simulaties omdat we vergelijken met de zon referentie
    main_frequentielijn(files, watersysteem = watersysteem, simulation_types = simulation_types, reference_name = 'BI2023-totB2023-zon',
                        locations = ['extra_0071_GR'], save_dir = save_dir)
