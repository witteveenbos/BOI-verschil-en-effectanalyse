
from pathlib import Path
import re
from scipy.stats import norm
from scipy.interpolate import interp1d
import pandas as pd



riskeer_output = Path(r"C:\Users\tolp2\Downloads\HydraRing_BI2023_BOR_Rijn_oever")
output_BI2023_met = Path(r"C:\Users\tolp2\Downloads\HydraRing_BI2023_BOR_Rijn_oever\BI2023_met_onz_tp.csv")
output_BI2023_zon = Path(r"C:\Users\tolp2\Downloads\HydraRing_BI2023_BOR_Rijn_oever\BI2023_zon_onz_tp.csv")
output_BI2017_met = Path(r"C:\Users\tolp2\Downloads\HydraRing_BI2023_BOR_Rijn_oever\BI2017_met_onz_tp.csv")
output_BI2017_zon = Path(r"C:\Users\tolp2\Downloads\HydraRing_BI2023_BOR_Rijn_oever\BI2017_zon_onz_tp.csv")

location_matcher = re.compile(r"INSERT INTO \[Sections\] VALUES \(1, 1, 1, 'hydraring', '(.*)', 0, 0, (\d+\.\d+), (\d+\.\d+), ")

freqs = {
    100: -1*norm.ppf(1/100),
    1000: -1*norm.ppf(1/1000),
    10000: -1*norm.ppf(1/10000),
    100000: -1*norm.ppf(1/100000),
}

results_BI2023_met = []
results_BI2023_zon = []
results_BI2017_met = []
results_BI2017_zon = []



for invoer_sql in riskeer_output.glob("./**/invoer.sql"):
    uitvoer = invoer_sql.parent.parent / "uitvoer" / "designTable_Tp.txt"
    if not uitvoer.exists():
        continue
    if not "_tp" in str(invoer_sql):
        continue
    
    # Get info on location and coordinates from invoer.sql
    invoer = invoer_sql.read_text()
    invoer_matches = location_matcher.findall(invoer)
    locatie = invoer_matches[0][0]
    x = float(invoer_matches[0][1])
    y = float(invoer_matches[0][2])


    test = pd.read_csv(uitvoer, sep=r"\s{2,}", engine="python")
    interp_func = interp1d(test["Beta"], test["Value"])

    for freq, beta in freqs.items():
        try:
            ws = interp_func(beta)
        except ValueError:
            print(f"Warning: Beta value {beta} for frequency {freq} is out of bounds for location {locatie}. Skipping this frequency.")
            continue
        if "B2023" in str(invoer_sql):
            if "met_tp" in str(invoer_sql):
                results_BI2023_met.append(
                    f"{locatie}, {x}, {y}, {freq}, {ws}"
                )
            elif "zon_tp" in str(invoer_sql):
                results_BI2023_zon.append(
                    f"{locatie}, {x}, {y}, {freq}, {ws}"
                )
            else:
                print(f"Error: Could not determine if file is met or zon for {invoer_sql}")
        elif "B2017" in str(invoer_sql):
            if "met_tp" in str(invoer_sql):
                results_BI2017_met.append(
                    f"{locatie}, {x}, {y}, {freq}, {ws}"
                )
            elif "zon_tp" in str(invoer_sql):
                results_BI2017_zon.append(
                    f"{locatie}, {x}, {y}, {freq}, {ws}"
                )
            else:
                print(f"Error: Could not determine if file is met or zon for {invoer_sql}")
        else:
            print(f"Error: Could not determine if file is from BI2017 or BI2023 for {invoer_sql}")
    

with open(output_BI2023_met, "w") as f:
    f.write("Locatie, X-coördinaat, Y-coördinaat, Terugkeertijd [jaar], Belastingniveau [m+NAP]/Golfparameter [m]/[s]/Sterkte bekleding [-]\n")
    for line in results_BI2023_met:
        f.write(line + "\n")

with open(output_BI2023_zon, "w") as f:
    f.write("Locatie, X-coördinaat, Y-coördinaat, Terugkeertijd [jaar], Belastingniveau [m+NAP]/Golfparameter [m]/[s]/Sterkte bekleding [-]\n")
    for line in results_BI2023_zon:
        f.write(line + "\n")

with open(output_BI2017_met, "w") as f:
    f.write("Locatie, X-coördinaat, Y-coördinaat, Terugkeertijd [jaar], Belastingniveau [m+NAP]/Golfparameter [m]/[s]/Sterkte bekleding [-]\n")
    for line in results_BI2017_met:
        f.write(line + "\n")

with open(output_BI2017_zon, "w") as f:
    f.write("Locatie, X-coördinaat, Y-coördinaat, Terugkeertijd [jaar], Belastingniveau [m+NAP]/Golfparameter [m]/[s]/Sterkte bekleding [-]\n")
    for line in results_BI2017_zon:
        f.write(line + "\n")
