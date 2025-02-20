import ROOT
import numpy as np

ns = 1
# Constant value dependant only on the ETROC configuration 
T3 = 3.125* ns
# Constant value dependant on the clock configuration 40MHZ --> 12.5 ns
T_WINDOW = 12.5 * ns
def get_max_cal(df: ROOT.RDataFrame):
    """
    Get the most repeated cal value in the dataframe
    Args:
        df: ROOT.RDataFrame
    Returns:
        max_cal: int
    """
    hist = df.Histo1D(("cal", "cal", 1024, -0.5, 1023.5), "cal")
    # -1 Added because the bin number starts at 1 and the cal value at 0
    max_cal = hist.GetMaximumBin()-1
    return max_cal


def compute_tbin(df):
    """
    Compute the t_bin for each event as a new column in the dataframe
    Args:
        df: ROOT.RDataFrame
    Returns:
        df: ROOT.RDataFrame
    """

    df = df.Define("t_bin", f"{T3}/cal")
    return df

def compute_ToA(df):
    """
    Compute the ToA for each event as a new column in the dataframe
    Args:
        df: ROOT.RDataFrame
    Returns:
        df: ROOT.RDataFrame
    """
    # Check if the t_bin column is already in the dataframe
    if "t_bin" not in df.GetColumnNames():
        df = compute_tbin(df)

    df = df.Define("ToA", f"{T_WINDOW}-t_bin*toa_code")
    return df

def compute_ToT(df):
    """
    Compute the ToT for each event as a new column in the dataframe
    Args:
        df: ROOT.RDataFrame
    Returns:
        df: ROOT.RDataFrame
    """
    # Check if the ToA column is already in the dataframe
    if "t_bin" not in df.GetColumnNames():
        df = compute_tbin(df)

    df = df.Define("ToT", f"(2*tot_code - floor(tot_code/32))*t_bin")
    return df


def get_ToA_histograms_limits(t_bin, size = 14):
    """
    Get the limits for the histograms

    Delta ToA is t_bin
    
    Args:
        t_bin (float)
        size (int): Maximum ToA value. Default value is 14
    Returns:
        min_toa (float)
        max_toa (float)
        bin_number (int)
    """
    bin_size = 2*np.mean(np.array(t_bin))
    min_toa = -bin_size/2
    max_toa = size+bin_size/2
    bin_number = int((max_toa-min_toa)/bin_size)
    return min_toa, max_toa, bin_number


def get_ToT_histograms_limits(t_bin, size = 7):
    """
    Get the limits for the histograms

    Delta ToT depends on the floor of the ToT_CODE, 
    it can be 2*t_bin or t_bin, in most of the cases it is 2*t_bin
    
    Args:
        t_bin (float)
        size (int): Maximum ToT value. Default value is 7
    Returns:
        min_tot (float)
        max_tot (float)
        bin_number (int)
    """
    bin_size = 2*np.mean(np.array(t_bin))
    min_tot = -bin_size/2
    max_tot = size+bin_size/2
    bin_number = int((max_tot-min_tot)/bin_size)
    return min_tot, max_tot, bin_number

