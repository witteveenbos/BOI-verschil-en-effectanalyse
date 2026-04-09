'''
Docstring for default settings plot colors and labels
BOI verschil en effectanalyse
Witteveen+Bos & HKV 2026
'''

import matplotlib.transforms as mtransforms

parameters = {
    "ws":  ("Waterstand (m+NAP)", "waterstand", "m+NAP", "ws", "m"),
    "go": ("HBN (m+NAP)",       "HBN",        "m+NAP", "hbn", "m"),
    "hs":  ("Hs (m)",            "Hs",         "m",     "hs",  "m"),
    "tp":  ("Tp (s)",            "Tp",         "s",     "tp",  "s"),
    "ts":  ("Tm (s)",            "Tm",         "s",     "ts",  "s"),
}

colors_dict = {
            'BI2017-totB2017-zon': ('dodgerblue', 1.5, 'dashed'), 
            #'BI2023-fysB2017-zon': ('hotpink', 1.5, 'solid'), 
            'BI2023-fysB2017-zon': ('lightgreen', 1.5, 'solid'), 
            #'BI2023-stkB2017-zon': ('lightgreen', 1.5, 'solid'), 
            'BI2023-stkB2017-zon': ('hotpink', 1.5, 'solid'), 
            'BI2023-rknB2017-zon': ('purple', 1.5, 'dotted'), 
            'BI2023-totB2023-zon': ('orange', 1.5, 'dashed'), 
            'BI2017-totB2017-met': ('darkblue', 2, 'solid'), 
            'BI2023-onzB2017-met': ('darkgreen', 2, 'solid'), 
            'BI2023-totB2023-met': ('red', 2, 'solid')
        }

legend_dict = {
            'BI2017-totB2017-zon': 'WBI2017 (totaal, zonder modelonzekerheid)', 
            #'BI2023-fysB2017-zon': 'BOI2023 (met WBI2017 fysica, zonder modelonzekerheid)', 
            'BI2023-fysB2017-zon': 'WBI2017 met BOI2023 statistiek (zonder modelonzekerheid)', 
            #'BI2023-stkB2017-zon': 'BOI2023 (met WBI2017 statistiek, zonder modelonzekerheid)', 
            'BI2023-stkB2017-zon': 'WBI2017 met BOI2023 fysica (zonder modelonzekerheid)', 
            'BI2023-rknB2017-zon': 'BOI2023 (met WBI2017 rekeninstellingen, zonder modelonzekerheid)', 
            'BI2023-totB2023-zon': 'BOI2023 (totaal, zonder modelonzekerheid)', 
            'BI2017-totB2017-met': 'WBI2017 (totaal, met modelonzekerheid)', 
            'BI2023-onzB2017-met': 'BOI2023 (met WBI2017 onzekerheid, met modelonzekerheid)', 
            'BI2023-totB2023-met': 'BOI2023 (totaal, met modelonzekerheid)'
        }

ylabel_dict = {
    'ws' : 'Waterstand (m+NAP)',
    'go' : 'HBN (m+NAP)',
    'tp' : 'Golfperiode (s)',
    'hs' : 'Significante golfhoogte (m)',
    'ts' : 'Gemiddelde golfperiode (s)'
}

order_dict = {
        legend_dict['BI2017-totB2017-zon']: 5, 
        legend_dict['BI2023-fysB2017-zon']: 3, 
        legend_dict['BI2023-stkB2017-zon']: 4, 
        legend_dict['BI2023-rknB2017-zon']: 6, 
        legend_dict['BI2023-totB2023-zon']: 1, 
        legend_dict['BI2017-totB2017-met']: 0, 
        legend_dict['BI2023-onzB2017-met']: 7, 
        legend_dict['BI2023-totB2023-met']: 2
    }

def annotate_BOI_higher_lower(ax, x_zero_line, orientation='vertical'):
    """
    Add annotations showing BOI vs WBI comparison.
    
    Parameters:
    -----------
    ax : matplotlib axis
        The axis to annotate
    x_zero_line : float
        The position of the zero line
    orientation : str
        'vertical' (default): arrows above/below, placed right of figure
        'horizontal': arrows left/right, placed above figure
    """
    
    y_min, y_max = ax.get_ylim()
    x_min, x_max = ax.get_xlim()

    if orientation == 'vertical':
        # Blend: x in axes coords, y in data coords
        trans = mtransforms.blended_transform_factory(
            ax.transAxes, ax.transData
        )
        x_pos = 1.05

        # Up arrow
        ax.annotate(
            '',
            xy=(x_pos, y_max/2),
            xytext=(x_pos, 0),
            xycoords=trans,
            textcoords=trans,
            arrowprops=dict(arrowstyle='->', linewidth=1.2),
            annotation_clip=False
        )
        ax.text(x_pos, y_max/2, 'BOI\nhoger', transform=trans, va='bottom', ha='center')

        # Down arrow
        ax.annotate(
            '',
            xy=(x_pos, y_min/2),
            xytext=(x_pos, 0),
            xycoords=trans,
            textcoords=trans,
            arrowprops=dict(arrowstyle='->', linewidth=1.2),
            annotation_clip=False
        )
        ax.text(x_pos, y_min/2, 'BOI\nlager', transform=trans, va='top', ha='center')

    elif orientation == 'horizontal':
        # Blend: x in data coords, y in axes coords
        trans = mtransforms.blended_transform_factory(
            ax.transData, ax.transAxes
        )
        y_pos = 0.90

        ax.text((x_zero_line + x_max) / 2, y_pos, 'WBI\ngroter', transform=trans, ha='center', va='bottom')

        ax.text((x_zero_line + x_min) / 2, y_pos, 'WBI\nkleiner', transform=trans, ha='center', va='bottom')
