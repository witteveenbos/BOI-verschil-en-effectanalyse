"""
Docstring for langsfiguren_script.py
Contains main function for langsfiguren
BOI verschil en effectanalyse
Witteveen+Bos & HKV 2026

Script to read HydraNL/Riskeer computation results and plot along the thalweg
from .csv file that were produced by the HKV viewer.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
import matplotlib.pyplot as plt

import re
import pandas as pd
import matplotlib.pyplot as plt
import contextily as cx
import matplotlib.patheffects as pe
from utils.plotting_settings import parameters

def get_parameter_settings(csv_path: str):
    """
    Determines parameter settings based on csv file name.
    """
    for key, values in parameters.items():
        if key in csv_path:
            return values

    raise ValueError("Cannot determine parameter from file name.")

def plot_waterstand_series_with_difference(csv_path: str) -> pd.DataFrame:
    """
    Plots:
    Top subplot:
        Waterstand vs river km for all Serie categories

    Bottom subplot:
        Difference relative to reference (Serie containing 'Defintf') - TODO: aanpassen naar naamgeving BOI:
        Δ (parameter) = BOI totaal - serie

    Returns dataframe of csv file, plots in the process.
    """
    #based on the name of the csv file, we can determine the used parameter (voelt nog wat omslachtig)
    parameter, parameter_name, parameter_unit, parameter_short, parameter_diff_unit = get_parameter_settings(csv_path)
    
    # TODO: check of datum van csv klopt met verwachte datum (namelijk 'jonger' dan de laatste bijbehorende HydraNL/Riskeer run)

    # Reading CSV
    df = pd.read_csv(csv_path, sep=r"\s*,\s*", engine="python")
    df.columns = df.columns.str.strip()

    # Extract river km
    df["km"] = (
        df["Locatie (-)"]
        .str.extract(r"km(\d+)", expand=False)
        .astype(float)
    )

    # Sort high to low (is dit eigenlijk nodig?)
    df = df.sort_values("km", ascending=False)

    series_names = df["Serie"].unique()

    # Create consistent color mapping per series
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    color_map = {
        serie: colors[i % len(colors)]
        for i, serie in enumerate(series_names)
    }

    # Find reference TODO: aanpassen naar naamgeving BOI
    ref_candidates = [s for s in series_names if "NoWd" in s]

    if not ref_candidates:
        raise ValueError("No Serie containing 'NoWd' found as reference.") #TODO: aanpassen naar naamgeving BOI

    ref_name = ref_candidates[0]

    # Plot setup
    fig = plt.figure(figsize=(9, 9))

    gs = fig.add_gridspec(3, 1, height_ratios=[2, 2, 2])

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax3 = fig.add_subplot(gs[2])

    # Plot all series
    for serie, group in df.groupby("Serie"):
        group = group.sort_values("km", ascending=False)

        ax1.plot(
            group["km"],
            group[parameter],
            label=serie,
            lw=2,
            color=color_map[serie],
        )

    ax1.tick_params(labelbottom=True)
    ax1.set_xlabel("Rivierkilometer (km)")
    ax1.set_ylabel(f"{parameter_name} ({parameter_unit})")
    ax1.grid(True)
    ax1.legend()

    # Difference subplot
    ref = df[df["Serie"] == ref_name][["km", parameter]]
    ref = ref.rename(columns={parameter: "ref_" + parameter_short})

    for serie, group in df.groupby("Serie"):
        if serie == ref_name:
            continue

        other = group[["km", parameter]]
        other = other.rename(columns={parameter: parameter_short})

        merged = ref.merge(other, on="km", how="inner")
        merged["diff"] = merged["ref_" + parameter_short] - merged[parameter_short]

        ax2.plot(
            merged["km"],
            merged["diff"],
            label=serie,
            lw=2,
            color=color_map[serie],
        )

    ax2.set_xlabel("Rivierkilometer (km)")
    ax2.set_ylabel(f"Δ {parameter_name} ({parameter_diff_unit})")
    ax2.set_title(f"Verschil (BOI - serie)")
    ax2.grid(True)
    ax2.legend()

    # Reverse axis for river convention
    ax1.invert_xaxis()

    # Map subplot (plan view, 2:1 zoom if vertical)
    line_df = df.sort_values("km", ascending=False)

    x = line_df["X (EPSG:28992)"].values
    y = line_df["Y (EPSG:28992)"].values
    km_vals = line_df["km"].values

    # Plot thalweg
    ax3.plot(x, y, color="black", lw=2, zorder=3)

    # Select 5 points: first, 3 evenly spaced intermediate, last
    indices = np.linspace(0, len(line_df)-1, 5, dtype=int)

    for idx in indices:
        # Add first and last km labels
        ax3.text(x[idx], y[idx], f"km {int(km_vals[idx])}", fontsize=8,color='black',
                path_effects=[pe.withStroke(linewidth=4, foreground="white")],alpha=0.7)

    # Compute bounding box
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()

    dx = xmax - xmin
    dy = ymax - ymin

    # Padding: 10% of max dimension
    pad = max(max(dx, dy) * 0.1, 5000)

    xcenter = (xmax + xmin) / 2
    ycenter = (ymax + ymin) / 2

    if dy > dx:
        # Vertical river: fix Y-span, X-span = 2 * Y-span
        yspan = dy + 2*pad
        xspan = 2 * yspan
    else:
        # Normal river: span with padding
        xspan = dx + 2*pad
        yspan = dy + 2*pad

    ax3.set_xlim(xcenter - xspan/2, xcenter + xspan/2)
    ax3.set_ylim(ycenter - yspan/2, ycenter + yspan/2)

    ax3.set_aspect("equal")

    # Add basemap
    cx.add_basemap(
        ax3,
        crs="EPSG:28992",
        source=cx.providers.OpenStreetMap.Mapnik
    )

    ax3.set_axis_off()
    ax3.set_title("Locaties langs thalweg")

    plt.tight_layout()
    plt.savefig(csv_path.replace(".csv", "_langsfiguur.png"), dpi=300)

    #plt.show()

    return df

if __name__ == "__main__":
    df = plot_waterstand_series_with_difference("z:\\149287_BOI_verschil_en_effectanalyse\\data\\viewer_export\\B2035_Wind_BER-RIJN_B2035_MxWd_WS.csv")
    #TODO: pas hier het pad aan naar de juiste csv file