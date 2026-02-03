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

PARAMETERS = {
    "WS":  ("Waterstand (m+NAP)", "waterstand", "m+NAP", "ws", "m"),
    "HBN": ("HBN (m+NAP)",       "HBN",        "m+NAP", "hbn", "m"),
    "Hs":  ("Hs (m)",            "Hs",         "m",     "hs",  "m"),
    "Tp":  ("Tp (s)",            "Tp",         "s",     "tp",  "s"),
}

def get_parameter_settings(csv_path: str):
    """
    Determines parameter settings based on csv file name.
    """
    for key, values in PARAMETERS.items():
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

    # Find reference TODO: aanpassen naar naamgeving BOI
    ref_candidates = [s for s in series_names if "Defintf" in s]

    if not ref_candidates:
        raise ValueError("No Serie containing 'Defintf' found as reference.") #TODO: aanpassen naar naamgeving BOI

    ref_name = ref_candidates[0]

    # Plot setup
    fig, (ax1, ax2) = plt.subplots(
        2, 1, sharex=True, figsize=(9, 6)
    )

    # Plot all series
    for serie, group in df.groupby("Serie"):
        group = group.sort_values("km", ascending=False)

        ax1.plot(
            group["km"],
            group[parameter],
            marker="o",
            label=serie,
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
            marker="o",
            label=serie,
        )

    ax2.set_xlabel("Rivierkilometer (km)")
    ax2.set_ylabel(f"Δ {parameter_name} ({parameter_diff_unit})")
    ax2.set_title(f"Verschil (BOI - serie)")
    ax2.grid(True)
    ax2.legend()

    # Reverse axis for river convention
    ax1.invert_xaxis()

    plt.tight_layout()
    plt.show()

    return df

if __name__ == "__main__":
    df = plot_waterstand_series_with_difference("z:\\149287_BOI_verschil_en_effectanalyse\\data\\viewer_export\\B2035_OnMt_BER-RIJN_B2035_OnMt_WS.csv")
    #TODO: pas hier het pad aan naar de juiste csv file