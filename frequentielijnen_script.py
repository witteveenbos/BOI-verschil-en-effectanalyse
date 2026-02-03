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

def main_frequentielijn(watersysteem=None, simulation_types=None, locations=None):
    """
    Main function to read and plot hfreq data.
    
    Args:
        watersysteem (str): Name of the water system (e.g., "Hollandsche IJssel")
                           If None, will attempt to extract from folder structure
        simulation_types (list): List of simulation type filters (e.g., ["totaal-zon", "totaal-met"])
                                If None or empty, all simulations are included
        locations (str or list): Location(s) to filter by. Can be location IDs (e.g., "as_0001")
                                or location codes from parent folder (e.g., "as" from folder ending in "_as")
                                If None or empty, all locations are included
    """
    
    # Base path to the project drive
    base_path = Path(r"z:\149287_BOI_verschil_en_effectanalyse\data\sommen")
    
    if not base_path.exists():
        print(f"Warning: Base path does not exist: {base_path}")
        return
    
    # Dictionary to store data grouped by location and computation type
    # Structure: {location_id: {computation_name: (frequency, water_level)}}
    data_by_location = defaultdict(dict)
    extracted_watersysteem = None  # Will be extracted from folder structure if not provided
    
    # Determine which folders to search
    search_paths = []
    # Accept watersysteem as None, a string, or a list of strings
    if watersysteem:
        wanted = [watersysteem] if isinstance(watersysteem, str) else list(watersysteem)
        matching_dirs = []
        for w in wanted:
            matching_dirs.extend([d for d in base_path.iterdir() if d.is_dir() and w in d.name])
        # remove duplicates while preserving order
        seen = set()
        search_paths = []
        for d in matching_dirs:
            if d not in seen:
                seen.add(d)
                search_paths.append(d)
        if not search_paths:
            print(f"No folders found for watersysteem(s): {wanted}")
            return
    else:
        # Search all watersysteem folders (start from base)
        search_paths = [base_path]

    # Prepare location filters (None, string, or list)
    wanted_locations = None
    if locations:
        wanted_locations = [locations] if isinstance(locations, str) else list(locations)
    
    # Walk through directory structure
    for search_path in search_paths:
        for root, dirs, files in os.walk(search_path):
            if "hfreq.txt" in files:
                hfreq_path = Path(root) / "hfreq.txt"
                
                # Extract location ID and computation settings from path
                # Expected structure: .../HydraNL_Beoordelen_BER_HollandscheIJssel_as/as_0001_HY_km0000_BI2023-totaal-zon_WS/uitvoer/
                path_parts = Path(root).parts
                
                # Extract watersysteem and location code from parent folder if needed
                if watersysteem is None and len(path_parts) >= 4:
                    parent_system_folder = path_parts[-4]
                    # Extract watersysteem name from folder (e.g., "HydraNL_Beoordelen_BER_HollandscheIJssel_as" -> "HollandscheIJssel")
                    parts_sys = parent_system_folder.split("_")
                    if len(parts_sys) >= 4:
                        # The watersysteem is typically at index 3
                        folder_watersysteem = parts_sys[3]
                    else:
                        folder_watersysteem = None
                    
                    if extracted_watersysteem is None and folder_watersysteem:
                        extracted_watersysteem = folder_watersysteem
                
                # Extract location code from parent folder (e.g., "as" from "HydraNL_Beoordelen_BER_HollandscheIJssel_as")
                parent_location_code = None
                if len(path_parts) >= 4:
                    parent_system_folder = path_parts[-4]
                    # Get the last part after split by underscore to get location code (e.g., "as")
                    parts_sys = parent_system_folder.split("_")
                    if len(parts_sys) > 0:
                        parent_location_code = parts_sys[-1]  # e.g., "as"
                
                # Find the computation folder (parent of uitvoer)
                if len(path_parts) >= 2:
                    computation_folder = path_parts[-2]  # This is the settings folder
                    # parent_folder is the folder just above computation folder (location folder)
                    parent_folder = path_parts[-3] if len(path_parts) >= 3 else None
                    
                    # Extract location ID from computation folder name
                    # e.g., "as_0001_HY_km0000_BI2023-totaal-zon_WS" -> extract "as_0001"
                    parts = computation_folder.split("_")
                    if len(parts) >= 2:
                        location_id = f"{parts[0]}_{parts[1]}"
                    else:
                        location_id = computation_folder
                    
                    # Filter by simulation type if specified
                    if simulation_types:
                        # Extract simulation type from folder name including the BI prefix
                        # e.g., parts may contain: [..., 'BI2023-totaal-zon', 'WS'] or ['BI2023-totaal-zon']
                        sim_type = None
                        bi_index = None
                        for i, part in enumerate(parts):
                            if part.startswith("BI"):
                                bi_index = i
                                break
                        if bi_index is not None:
                            # include BI... part and any subsequent parts except trailing 'WS'
                            end_index = len(parts)
                            if parts[-1] == "WS":
                                end_index = len(parts) - 1
                            sim_parts = parts[bi_index:end_index]
                            sim_type = "_".join(sim_parts)

                        # Normalize filters and allow user to specify either full BI-prefixed types
                        # or the short suffix (e.g., 'totaal-zon') which will match BI2017 and BI2023
                        match = False
                        for filter_type in simulation_types:
                            if filter_type.upper().startswith("BI"):
                                # user supplied full BI... string: match exact
                                if sim_type == filter_type:
                                    match = True
                                    break
                            else:
                                # user supplied suffix, accept either BI2017-<suffix> or BI2023-<suffix>
                                if sim_type and (sim_type.startswith("BI2017") or sim_type.startswith("BI2023")) and filter_type in sim_type:
                                    match = True
                                    break

                        if not match:
                            continue

                        # Filter by location if specified
                        # Supports location IDs like 'as_0001' or location codes like 'as' from parent folder name
                        if wanted_locations:
                            loc_match = False
                            for want in wanted_locations:
                                # Check exact or prefix matches against location ID (e.g., "as_0001" or "036-01_0050")
                                if location_id == want or location_id.startswith(want + "_") or want in location_id:
                                    loc_match = True
                                    break
                                # Check against parent location code (e.g., "as" or "oever")
                                if parent_location_code and parent_location_code == want:
                                    loc_match = True
                                    break
                                # Check against the parent folder name (some IDs appear there)
                                if parent_folder and want in parent_folder:
                                    loc_match = True
                                    break
                            if not loc_match:
                                continue
                    
                    # Read the hfreq file
                    frequency, water_level = read_hfreq_file(str(hfreq_path))
                    
                    if frequency is not None and water_level is not None:
                        data_by_location[location_id][computation_folder] = (frequency, water_level)
                        print(f"Read {computation_folder} for {location_id}: {len(frequency)} points")
    
    if not data_by_location:
        print("No hfreq.txt files found!")
        return
    
    # Use provided watersysteem or extracted one for the title
    if isinstance(watersysteem, (list, tuple)):
        final_watersysteem = ", ".join(watersysteem)
    else:
        final_watersysteem = watersysteem if watersysteem else extracted_watersysteem
    
    # Create plots for each location
    num_locations = len(data_by_location)
    fig, axes = plt.subplots(num_locations, 1, figsize=(12, 4*num_locations))
    
    # Handle case with single location
    if num_locations == 1:
        axes = [axes]
    
    for idx, (location_id, computations) in enumerate(sorted(data_by_location.items())):
        ax = axes[idx]
        
        # Plot each computation for this location
        for computation_name, (frequency, water_level) in sorted(computations.items()):
            # Convert frequency (per year) to return period (years)
            return_period = 1.0 / frequency
            ax.plot(return_period, water_level, marker='o', label=computation_name, linewidth=2)
        
        ax.set_xlabel("Terugkeertijd (jaar)", fontsize=11)
        ax.set_ylabel("waterstand (m+NAP)", fontsize=11)
        # Determine location type label (e.g., 'as' or 'oever') to show in title
        if location_id.startswith("as_") or location_id.startswith("as"):
            loc_type = "as"
        elif "-" in location_id:
            loc_type = "oever"
        else:
            loc_type = None

        # Add watersysteem and location type to title if available
        title = f"Location: {location_id}"
        if loc_type:
            title += f" ({loc_type})"
        if final_watersysteem:
            title += f" - {final_watersysteem}"
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')  # Logarithmic scale for return period
    
    plt.tight_layout()
    plt.savefig(f"hfreq_{watersysteem}_{location_id}.png", dpi=150, bbox_inches='tight')
    print(f"Plot saved as 'hfreq_{watersysteem}_{location_id}.png'")
    plt.show()

if __name__ == "__main__":
    # Example usage:
    # main()  # Uses all simulations, extracts watersysteem from folder
    # main(watersysteem="Hollandsche IJssel")  # Specifies watersysteem
    # main(simulation_types=["totaal-zon", "totaal-met"])  # Only these simulation types
    # main(watersysteem="Hollandsche IJssel", simulation_types=["totaal-zon"])
    # main(locations="as_0001")  # Single location by ID
    # main(locations=["as_0001", "as_0002"])  # Multiple locations by ID
    # main(locations="as")  # All locations with code 'as' from parent folder
    # main(watersysteem="Maas", locations=["as_0001"], simulation_types=['BI2023-totaal-met'])
    
    main_frequentielijn(watersysteem="Maas" , locations=["036-01_0050"])
