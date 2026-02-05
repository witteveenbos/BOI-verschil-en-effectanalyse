'''
Docstring for default settings plot colors and labels
BOI verschil en effectanalyse
Witteveen+Bos & HKV 2026
'''

parameters = {
    "WS":  ("Waterstand (m+NAP)", "waterstand", "m+NAP", "ws", "m"),
    "HBN": ("HBN (m+NAP)",       "HBN",        "m+NAP", "hbn", "m"),
    "Hs":  ("Hs (m)",            "Hs",         "m",     "hs",  "m"),
    "Tp":  ("Tp (s)",            "Tp",         "s",     "tp",  "s"),
}

colors_dict = {
            '2017-totaal-zon': 'lightblue', 
            '2017-fysica-zon': 'hotpink', 
            '2017-sttstk-zon': 'lightgreen', 
            '2017-rknnst-zon': 'purple', 
            '2023-totaal-zon': 'orange', 
            '2017-totaal-met': 'darkblue', 
            '2017-onzkrh-met': 'darkgreen', 
            '2023-totaal-met': 'red'
        }

legend_dict = {
            '2017-totaal-zon': 'WBI2017 (totaal, zonder modelonzekerheid)', 
            '2017-fysica-zon': 'BOI2023 (met WBI2017 fysica, zonder modelonzekerheid)', 
            '2017-sttstk-zon': 'BOI2023 (met WBI2017 statistiek, zonder modelonzekerheid)', 
            '2017-rknnst-zon': 'BOI2023 (met WBI2017 rekeninstellingen, zonder modelonzekerheid)', 
            '2023-totaal-zon': 'BOI2023 (totaal, zonder modelonzekerheid)', 
            '2017-totaal-met': 'WBI2017 (totaal, met modelonzekerheid)', 
            '2017-onzkrh-met': 'BOI2023 (met WBI2017 onzekerheid, met modelonzekerheid)', 
            '2023-totaal-met': 'BOI2023 (totaal, met modelonzekerheid)'
        }

ylabel_dict = {
    'WS' : 'Waterstand (m+NAP)',
    'HBN' : 'HBN (m+NAP)',
    'Tp' : 'Golfperiode (s)',
    'Hs' : 'Significante golfhoogte (m)'
}

order_dict = {
        legend_dict['2017-totaal-zon']: 4, 
        legend_dict['2017-fysica-zon']: 1, 
        legend_dict['2017-sttstk-zon']: 2, 
        legend_dict['2017-rknnst-zon']: 3, 
        legend_dict['2023-totaal-zon']: 0, 
        legend_dict['2017-totaal-met']: 7, 
        legend_dict['2017-onzkrh-met']: 6, 
        legend_dict['2023-totaal-met']: 5
    }