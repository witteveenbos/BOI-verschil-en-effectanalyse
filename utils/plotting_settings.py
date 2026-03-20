'''
Docstring for default settings plot colors and labels
BOI verschil en effectanalyse
Witteveen+Bos & HKV 2026
'''

import matplotlib.transforms as mtransforms

parameters = {
    "ws":  ("Waterstand (m+NAP)", "waterstand", "m+NAP", "ws", "m"),
    "HBN": ("HBN (m+NAP)",       "HBN",        "m+NAP", "hbn", "m"),
    "Hs":  ("Hs (m)",            "Hs",         "m",     "hs",  "m"),
    "Tp":  ("Tp (s)",            "Tp",         "s",     "tp",  "s"),
}

colors_dict = {
            'BI2017-totB2017-zon': ('dodgerblue', 1.5, 'dashed'), 
            'BI2023-fysB2017-zon': ('hotpink', 1.5, 'solid'), 
            'BI2023-stkB2017-zon': ('lightgreen', 1.5, 'solid'), 
            'BI2023-rknB2017-zon': ('purple', 1.5, 'dotted'), 
            'BI2023-totB2023-zon': ('orange', 1.5, 'dashed'), 
            'BI2017-totB2017-met': ('darkblue', 2, 'solid'), 
            'BI2023-onzB2017-met': ('darkgreen', 2, 'solid'), 
            'BI2023-totB2023-met': ('red', 2, 'solid')
        }

legend_dict = {
            'BI2017-totB2017-zon': 'WBI2017 (totaal, zonder modelonzekerheid)', 
            'BI2023-fysB2017-zon': 'BOI2023 (met WBI2017 fysica, zonder modelonzekerheid)', 
            #'BI2023-fysB2017-zon': 'WBI2017 met BOI2023 statistiek (zonder modelonzekerheid)', 
            'BI2023-stkB2017-zon': 'BOI2023 (met WBI2017 statistiek, zonder modelonzekerheid)', 
            #'BI2023-stkB2017-zon': 'WBI2017 met BOI2023 fysica (zonder modelonzekerheid)', 
            'BI2023-rknB2017-zon': 'BOI2023 (met WBI2017 rekeninstellingen, zonder modelonzekerheid)', 
            'BI2023-totB2023-zon': 'BOI2023 (totaal, zonder modelonzekerheid)', 
            'BI2017-totB2017-met': 'WBI2017 (totaal, met modelonzekerheid)', 
            'BI2023-onzB2017-met': 'BOI2023 (met WBI2017 onzekerheid, met modelonzekerheid)', 
            'BI2023-totB2023-met': 'BOI2023 (totaal, met modelonzekerheid)'
        }

ylabel_dict = {
    'ws' : 'Waterstand (m+NAP)',
    'HBN' : 'HBN (m+NAP)',
    'Tp' : 'Golfperiode (s)',
    'Hs' : 'Significante golfhoogte (m)'
}

order_dict = {
        legend_dict['BI2017-totB2017-zon']: 1, 
        legend_dict['BI2023-fysB2017-zon']: 4, 
        legend_dict['BI2023-stkB2017-zon']: 5, 
        legend_dict['BI2023-rknB2017-zon']: 6, 
        legend_dict['BI2023-totB2023-zon']: 3, 
        legend_dict['BI2017-totB2017-met']: 0, 
        legend_dict['BI2023-onzB2017-met']: 7, 
        legend_dict['BI2023-totB2023-met']: 2
    }

def annotate_BOI_higher_lower(ax):

    y_min, y_max = ax.get_ylim()

    # Blend: x in axes coords, y in data coords
    trans = mtransforms.blended_transform_factory(
        ax.transAxes, ax.transData
    )

    x_pos = 1.05  # clearly outside right spine

    # Up arrow (0 → y_max)
    ax.annotate(
        '',
        xy=(x_pos, y_max/2),
        xytext=(x_pos, 0),
        xycoords=trans,
        textcoords=trans,
        arrowprops=dict(arrowstyle='->', linewidth=1.2),
        annotation_clip=False
    )

    ax.text(
        x_pos, y_max/2,
        'BOI\nhoger',
        transform=trans,
        va='bottom', ha='center'
    )

    # Down arrow (0 → y_min)
    ax.annotate(
        '',
        xy=(x_pos, y_min/2),
        xytext=(x_pos, 0),
        xycoords=trans,
        textcoords=trans,
        arrowprops=dict(arrowstyle='->', linewidth=1.2),
        annotation_clip=False
    )

    ax.text(
        x_pos, y_min/2,
        'BOI\nlager',
        transform=trans,
        va='top', ha='center'
    )
