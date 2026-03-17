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

import zipfile
import io
import os


def read_hfreq_file_new(filepath):
    """
    Read hfreq.txt file (supports files inside zip archives).

    Args:
        filepath (str): Full path including zip + internal path

    Returns:
        tuple: (frequency array, water_level array) or (None, None)
    """
    try:
        # Check if file is inside a zip archive
        if ".zip" in filepath.lower():
            zip_index = filepath.lower().find(".zip")
            zip_path = filepath[:zip_index + 4]
            internal_path = filepath[zip_index + 5:].replace("\\", "/")

            with zipfile.ZipFile(zip_path, 'r') as z:
                with z.open(internal_path) as f:
                    text = io.TextIOWrapper(f)
                    data = np.loadtxt(text, skiprows=1)

        else:
            # Normal file
            data = np.loadtxt(filepath, skiprows=1)

        if data.ndim == 1:
            data = data.reshape(1, -1)

        if data.shape[1] >= 2:
            water_level = data[:, 0]
            frequency = data[:, 1]
            return frequency, water_level

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return None, None
