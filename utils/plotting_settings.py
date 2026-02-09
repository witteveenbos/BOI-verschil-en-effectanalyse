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
            'BI2017-totaalBI-zon': 'lightblue', 
            'BI2023-fysB2017-zon': 'hotpink', 
            'BI2023-stkB2017-zon': 'lightgreen', 
            'BI2023-rknB2017-zon': 'purple', 
            'BI2023-totaalBI-zon': 'orange', 
            'BI2017-totaalBI-met': 'darkblue', 
            'BI2023-onzB2017-met': 'darkgreen', 
            'BI2023-totaalBI-met': 'red'
        }

legend_dict = {
            'BI2017-totaalBI-zon': 'WBI2017 (totaal, zonder modelonzekerheid)', 
            'BI2023-fysB2017-zon': 'BOI2023 (met WBI2017 fysica, zonder modelonzekerheid)', 
            'BI2023-stkB2017-zon': 'BOI2023 (met WBI2017 statistiek, zonder modelonzekerheid)', 
            'BI2023-rknB2017-zon': 'BOI2023 (met WBI2017 rekeninstellingen, zonder modelonzekerheid)', 
            'BI2023-totaalBI-zon': 'BOI2023 (totaal, zonder modelonzekerheid)', 
            'BI2017-totaalBI-met': 'WBI2017 (totaal, met modelonzekerheid)', 
            'BI2023-onzB2017-met': 'BOI2023 (met WBI2017 onzekerheid, met modelonzekerheid)', 
            'BI2023-totaalBI-met': 'BOI2023 (totaal, met modelonzekerheid)'
        }

ylabel_dict = {
    'WS' : 'Waterstand (m+NAP)',
    'HBN' : 'HBN (m+NAP)',
    'Tp' : 'Golfperiode (s)',
    'Hs' : 'Significante golfhoogte (m)'
}

order_dict = {
        legend_dict['BI2017-totaalBI-zon']: 4, 
        legend_dict['BI2023-fysB2017-zon']: 1, 
        legend_dict['BI2023-stkB2017-zon']: 2, 
        legend_dict['BI2023-rknB2017-zon']: 3, 
        legend_dict['BI2023-totaalBI-zon']: 0, 
        legend_dict['BI2017-totaalBI-met']: 7, 
        legend_dict['BI2023-onzB2017-met']: 6, 
        legend_dict['BI2023-totaalBI-met']: 5
    }