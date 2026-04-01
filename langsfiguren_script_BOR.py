"""
Langsfiguren script
BOI verschil en effectanalyse
Witteveen+Bos & HKV 2026

Reads HydraNL/Riskeer viewer CSV export
Plots:
1) Absolute water levels along river km
2) Difference 2017 - 2023 (zon & met)
3) Map view of thalweg
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import contextily as cx
import matplotlib.patheffects as pe
from matplotlib.patches import Patch
from utils.plotting_settings import colors_dict, legend_dict, parameters, order_dict


# ============================================================
# Helpers
# ============================================================

def get_group(name):
    if "met" in name:
        return "met"
    elif "zon" in name:
        return "zon"
    return None

def find_serie(pattern, series_list):
    """Find serie name matching pattern"""
    for serie in series_list:
        if pattern in serie:
            return serie
    return None

def compute_diff(sim_a, sim_b, df, parameter_column, simulation_types):

    df_a = df[df["Serie"] == sim_a][["km", parameter_column]]
    df_b = df[df["Serie"] == sim_b][["km", parameter_column]]

    merged = df_a.merge(df_b, on="km", suffixes=("_a", "_b"))
    return merged[f"{parameter_column}_a"] - merged[f"{parameter_column}_b"]


# ============================================================
# Main function
# ============================================================

def plot_langsfiguur(csv_path: str, parameter: str, simulation_types: list, return_period=None):

    # --------------------------------------------------------
    # 1. Read CSV
    # --------------------------------------------------------
    df = pd.read_csv(csv_path, sep=r"\s*,\s*", engine="python")
    df.columns = df.columns.str.strip()

    df["km"] = (
        df["Locatie (-)"]
        .str.extract(r"km(\d+)", expand=False)
        .astype(float)
    )

    df = df.sort_values("km", ascending=False)

    parameter_column = parameters[parameter][0]

    df = df[df["Serie"].str.contains('|'.join(simulation_types), na=False)]

    # --------------------------------------------------------
    # 2. Figure setup (3 subplots)
    # --------------------------------------------------------
    fig = plt.figure(figsize=(8, 10))
    if return_period:
        fig.suptitle(f'Waterstand - Terugkeertijd {return_period} jaar', fontsize=16)
    gs = fig.add_gridspec(3, 1, height_ratios=[3, 2, 2])

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax3 = fig.add_subplot(gs[2])

    # ========================================================
    # 3. ABSOLUTE WATER LEVELS
    # ========================================================
    for serie, group in df.groupby("Serie"):
        serie_name = next((s for s in simulation_types if s in serie), None)
        if serie_name is None:
            continue
        color, linewidth, linestyle = colors_dict[serie_name]
        legend_name = legend_dict[serie_name]
        order = order_dict.get(legend_name, 10)

        group = group.sort_values("km", ascending=False)

        ax1.plot(
            group["km"],
            group[parameter_column],
            color=color,
            linewidth=linewidth,
            linestyle=linestyle,
            label=legend_name,
            zorder=order
        )

    ax1.set_ylabel(parameter_column)
    ax1.set_ylim(0, 21)  # fixed y-limits for better comparison, adjust as needed
    ax1.set_xlabel("Rivierkilometer (km)")
    ax1.grid(True)
    ax1.invert_xaxis()

    # Sorted legend
    handles, labels = ax1.get_legend_handles_labels()
    items = [(order_dict.get(label, 999), label, handle)
             for label, handle in zip(labels, handles)]
    items.sort(key=lambda x: x[0])

    ax1.legend(
        [i[2] for i in items],
        [i[1] for i in items],
        loc="upper left",
        fontsize=7
    )

    # ========================================================
    # 4. DIFFERENCE PLOT (2017 - 2023)
    # ========================================================

    ylabel_diff = parameters[parameter][1]
    ylabel_diff_unit = parameters[parameter][4]
    ax2.set_ylabel(
        rf"Verschil in {ylabel_diff} ({ylabel_diff_unit})"
    )
    ax2.set_ylim(-0.5, 0.5)  # fixed y-limits for better comparison, adjust as needed

    groups = {get_group(s) for s in simulation_types}

    for group in groups:

        series_list = df["Serie"].unique()
        sim_2017 = find_serie(f"BI2017-totB2017-{group}", series_list)
        sim_2023 = find_serie(f"BI2023-totB2023-{group}", series_list)

        df_2017 = df[df["Serie"] == sim_2017][["km", parameter_column]]
        df_2023 = df[df["Serie"] == sim_2023][["km", parameter_column]]

        merged = df_2017.merge(df_2023, on="km", suffixes=("_2017", "_2023"))

        merged["diff"] = (
            merged[f"{parameter_column}_2017"]
            - merged[f"{parameter_column}_2023"]
        )

        color, linewidth, linestyle = colors_dict[f"BI2017-totB2017-{group}"]
        legend_name = legend_dict[f"BI2017-totB2017-{group}"]

        ax2.plot(
            merged["km"],
            merged["diff"],
            color=color,
            linewidth=linewidth,
            linestyle=linestyle,
            zorder=order_dict.get(legend_name, 10)
        )

        # zero-line in new style
        color, linewidth, linestyle = colors_dict[f"BI2023-totB2023-{group}"]
        legend_name = legend_dict[f"BI2023-totB2023-{group}"]

        ax2.axhline(
            0.0,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            zorder=order_dict.get(legend_name, 10)
        )

    ax2.set_xlabel("Rivierkilometer (km)")
    ax2.grid(True)

    # ========================================================
    # 5. MAP SUBPLOT (unchanged)
    # ========================================================

    line_df = df[df['X (EPSG:28992)'] > 0].sort_values("km", ascending=False)

    x = line_df["X (EPSG:28992)"].values
    y = line_df["Y (EPSG:28992)"].values
    km_vals = line_df["km"].values

    ax3.plot(x, y, color="black", lw=2, zorder=3)

    indices = np.linspace(0, len(line_df) - 1, 5, dtype=int)

    for idx in indices:
        ax3.scatter(x[idx], y[idx], color="black", s=30)
        ax3.text(
            x[idx],
            y[idx],
            f"km {int(km_vals[idx])}",
            fontsize=8,
            path_effects=[pe.withStroke(linewidth=4, foreground="white")],
            alpha=0.8
        )

    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()

    dx = xmax - xmin
    dy = ymax - ymin
    pad = max(max(dx, dy) * 0.1, 5000)

    xcenter = (xmax + xmin) / 2
    ycenter = (ymax + ymin) / 2

    if dy > dx:
        yspan = dy + 2 * pad
        xspan = 2 * yspan
    else:
        xspan = dx + 2 * pad
        yspan = dy + 2 * pad

    ax3.set_xlim(xcenter - xspan / 2, xcenter + xspan / 2)
    ax3.set_ylim(ycenter - yspan / 2, ycenter + yspan / 2)
    ax3.set_aspect("equal")

    cx.add_basemap(
        ax3,
        crs="EPSG:28992",
        source=cx.providers.OpenStreetMap.Mapnik
    )

    ax3.set_axis_off()
    ax3.set_title("Locaties langs thalweg")

    # ========================================================
    # 6. Save figure
    # ========================================================

    plt.tight_layout()

    output_path = csv_path.replace(".csv", "_langsfiguur.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")

    return df

def plot_langsfiguur_violin(csv_path: str, parameter: str, simulation_types: list):
    """
    Violin plot of longitudinal contributions
    Categories aligned with frequentielijnen script
    """

    df = pd.read_csv(csv_path, sep=r"\s*,\s*", engine="python")
    df.columns = df.columns.str.strip()

    df["km"] = (
        df["Locatie (-)"]
        .str.extract(r"km(\d+)", expand=False)
        .astype(float)
    )

    df = df.sort_values("km", ascending=False)

    parameter_column = parameters[parameter][0]
    ylabel_diff = parameters[parameter][1]
    ylabel_diff_unit = parameters[parameter][4]

    df = df[df["Serie"].str.contains('|'.join(simulation_types), na=False)]

    # --------------------------------------------------------
    # Compute longitudinal differences per km
    # --------------------------------------------------------

    contributions = {}

    # WBI contributions - match serie names first
    series_list = df["Serie"].unique()
        
    contributions["WBI fysica"] = compute_diff(
        find_serie("BI2023-fysB2017-zon", series_list),
        find_serie("BI2023-totB2023-zon", series_list),
        df,
        parameter_column,
        simulation_types
    )

    contributions["WBI statistiek"] = compute_diff(
        find_serie("BI2023-stkB2017-zon", series_list),
        find_serie("BI2023-totB2023-zon", series_list),
        df,
        parameter_column,
        simulation_types
    )

    contributions["WBI rekeninstellingen"] = compute_diff(
        find_serie("BI2023-rknB2017-zon", series_list),
        find_serie("BI2023-totB2023-zon", series_list),
        df,
        parameter_column,
        simulation_types
    )

    contributions["Totaal zonder"] = compute_diff(
        find_serie("BI2017-totB2017-zon", series_list),
        find_serie("BI2023-totB2023-zon", series_list),
        df,
        parameter_column,
        simulation_types
    )

    contributions["Totaal met"] = compute_diff(
        find_serie("BI2017-totB2017-met", series_list),
        find_serie("BI2023-totB2023-met", series_list),
        df,
        parameter_column,
        simulation_types
    )

    # Riskeer (temporary assumption)
    tot_met = contributions["Totaal met"]
    if tot_met is not None:
        contributions["Riskeer"] = tot_met + 0.05
    else:
        contributions["Riskeer"] = None

    # --------------------------------------------------------
    # Fixed category order (ALWAYS 6)
    # --------------------------------------------------------

    categories = [
        "WBI fysica",
        "WBI statistiek",
        "WBI rekeninstellingen",
        "Totaal zonder",
        "Totaal met",
        "Riskeer",
    ]

    data = []
    colors = []

    for cat in categories:
        values = contributions.get(cat)

        if values is None:
            data.append([np.nan])  # keeps spacing
            colors.append("lightgrey")
        else:
            data.append(values.values)
            # get color from corresponding simulation
            if cat == "WBI fysica":
                colors.append(colors_dict["BI2023-fysB2017-zon"][0])
            elif cat == "WBI statistiek":
                colors.append(colors_dict["BI2023-stkB2017-zon"][0])
            elif cat == "WBI rekeninstellingen":
                colors.append(colors_dict["BI2023-rknB2017-zon"][0])
            elif cat == "Totaal zonder":
                colors.append(colors_dict["BI2017-totB2017-zon"][0])
            elif cat == "Totaal met":
                colors.append(colors_dict["BI2017-totB2017-met"][0])
            elif cat == "Riskeer":
                colors.append("purple")

    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 4))

    valid_data = []
    valid_positions = []
    valid_colors = []

    for i, cat in enumerate(categories, start=1):

        values = contributions.get(cat)

        if values is None:
            continue

        values = np.asarray(values)
        values = values[~np.isnan(values)]

        # KDE requires at least 2 values
        if len(values) < 2:
            continue

        valid_data.append(values)
        valid_positions.append(i)

        if cat == "WBI fysica":
            valid_colors.append(colors_dict["BI2023-fysB2017-zon"][0])
        elif cat == "WBI statistiek":
            valid_colors.append(colors_dict["BI2023-stkB2017-zon"][0])
        elif cat == "WBI rekeninstellingen":
            valid_colors.append(colors_dict["BI2023-rknB2017-zon"][0])
        elif cat == "Totaal zonder":
            valid_colors.append(colors_dict["BI2017-totB2017-zon"][0])
        elif cat == "Totaal met":
            valid_colors.append(colors_dict["BI2017-totB2017-met"][0])
        elif cat == "Riskeer":
            valid_colors.append("gray")
    legend_handles = []

    # Only plot if something valid exists
    if valid_data:

        parts = ax.violinplot(
            valid_data,
            positions=valid_positions,
            showmeans=True,
            showmedians=True,
            showextrema=True
        )

        for body, color, cat in zip(parts["bodies"], valid_colors, 
                                    [categories[i-1] for i in valid_positions]):
            body.set_facecolor(color)
            body.set_alpha(1)

            # Create legend entry
            legend_handles.append(
                Patch(facecolor=color, edgecolor="black", label=cat)
            )

    ax.axhline(0, color="black", linewidth=1)

    # Always show 6 category spaces
    ax.set_xticks(np.arange(1, len(categories) + 1))
    ax.set_xticklabels(categories, ha="center")

    ax.set_ylabel(
        rf"Verschil in {ylabel_diff} ({ylabel_diff_unit})"
    )

    ax.set_title("Verdeling bijdrage langs traject")

    ax.grid(True, axis="y", alpha=0.3)

    # Add legend only if we have entries
    if legend_handles:
        ax.legend(
            handles=legend_handles,
            loc="upper left",
            fontsize=8,
            frameon=True
        )

    plt.tight_layout()

    output_path = csv_path.replace(".csv", "_langsfiguur_v.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved violin figure: {output_path}")

# ============================================================
# Script execution
# ============================================================

if __name__ == "__main__":

    parameter = "ws"

    simulation_types = [
        "BI2017-totB2017-met",
        "BI2023-totB2023-met",
        "BI2017-totB2017-zon",
        "BI2023-totB2023-zon",
    ]

    for rp in [100, 1000 , 10000, 100000]:
        csv_path = f"C:\\Users\\tolp2\\Downloads\\HydraNL_BI2023_BOR_Rijn_as_BI2017-totB2017-met_ws-{rp}.csv"

        plot_langsfiguur(
            csv_path=csv_path,
            parameter=parameter,
            simulation_types=simulation_types,
            return_period=rp
        )

        simulation_types = [
            "BI2017-totB2017-met",
            "BI2023-totB2023-met",
            "BI2017-totB2017-zon",
            "BI2023-totB2023-zon",
            "BI2023-fysB2017-zon",
            "BI2023-stkB2017-zon",
            "BI2023-rknB2017-zon",
        ]

        plot_langsfiguur_violin(
            csv_path=csv_path,
            parameter=parameter,
            simulation_types=simulation_types,
        )