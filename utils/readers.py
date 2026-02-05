'''
Docstring for utils.readers
Contains read functions for various file types.
BOI verschil en effectanalyse
Witteveen+Bos & HKV 2026
'''
import numpy as np

def read_hfreq_file(filepath):
    """
    Read hfreq.txt file.
    
    Args:
        filepath (str): Path to hfreq.txt file
        
    Returns:
        tuple: (frequency array, water_level array) or (None, None) if file invalid
    """
    try:
        data = np.loadtxt(filepath, skiprows=1)
        if data.ndim == 1:
            # Only one data point
            data = data.reshape(1, -1)
        if data.shape[1] >= 2:
            water_level = data[:, 0]
            frequency = data[:, 1]
            return frequency, water_level
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return None, None