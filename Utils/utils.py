import ROOT
import numpy as np
import ctypes

from . import plot_functions as pf


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

def get_Cal_relation(df: ROOT.RDataFrame):
    """
    Get the relation between the number of hits in the cal = -1,0,1 bins
    Args:
        df: ROOT.RDataFrame
    Returns:
        rel01: float
        rel0m1: float
        rel01m1: float
    """

    max_cal = get_max_cal(df)
    # Filter to the max cal
    select_bin = 0
    filter = f"abs(cal-({max_cal}+{select_bin}))<0.5"
    hits_0 = df.Filter(filter).Count().GetValue()
    select_bin = 1
    filter = f"abs(cal-({max_cal}+{select_bin}))<0.5"
    hits_1 = df.Filter(filter).Count().GetValue()
    select_bin = -1
    filter = f"abs(cal-({max_cal}+{select_bin}))<0.5"
    hits_m1 = df.Filter(filter).Count().GetValue()

    rel01 = hits_0/hits_1
    rel0m1 = hits_0/hits_m1
    rel01m1 = hits_0/(hits_1+hits_m1)
    return rel01, rel0m1, rel01m1

def get_mean_cal(df: ROOT.RDataFrame):
    """
    Get the mean cal value in the dataframe
    Args:
        df: ROOT.RDataFrame
    Returns:
        mean_cal: float
        error_mean: float. Sigma of the gaussian distribution
    """
    max_cal = get_max_cal(df)
    # Filter to the max cal +-2 bins
    filter = f"abs(cal-{max_cal})<2.5"
    df = df.Filter(filter)
    # Plot cal histogram
    hist = pf.plot_cal(df, omit_plots=True)

    # Fit histogram to a gaussian in the range max cal -2, max cal +2
    c = ROOT.TCanvas()
    hist.GetXaxis().SetRangeUser(max_cal-2, max_cal+2)
    fit = hist.Fit("gaus", "S", "", max_cal-2, max_cal+2)
    mean_cal = fit.Parameter(1)
    error_mean = fit.Parameter(2)
    c.Draw()
    input("Press Enter to continue...")

    return mean_cal, error_mean
    
def compute_tbin(df, cal = None):
    """
    Compute the t_bin for each event as a new column in the dataframe
    Args:
        df: ROOT.RDataFrame
        cal: float. Value of Cal used to compute the t_bin. If None, the cal of each event is used
    Returns:
        df: ROOT.RDataFrame
    """
    if cal is None:
        df = df.Define("t_bin", f"{T3}/cal")
    else:
        df = df.Define("t_bin", f"{T3}/{cal}")
    return df

def compute_ToA(df, cal=None):
    """
    Compute the ToA for each event as a new column in the dataframe
    Args:
        df: ROOT.RDataFrame
        cal: float. Value of Cal used to compute the ToA. If None, the cal of each event is used
    Returns:
        df: ROOT.RDataFrame
    """
    # Check if the t_bin column is already in the dataframe
    if "t_bin" not in df.GetColumnNames():
        df = compute_tbin(df, cal)

    df = df.Define("ToA", f"{T_WINDOW}-t_bin*toa_code")
    return df

def compute_ToT(df, cal=None):
    """
    Compute the ToT for each event as a new column in the dataframe
    Args:
        df: ROOT.RDataFrame
        cal: float. Value of Cal used to compute the ToT. If None, the cal of each event is used
    Returns:
        df: ROOT.RDataFrame
    """
    # Check if the ToA column is already in the dataframe
    if "t_bin" not in df.GetColumnNames():
        df = compute_tbin(df, cal)

    df = df.Define("ToT", f"(2*tot_code - floor(tot_code/32))*t_bin")
    return df


def get_ToA_histograms_limits(t_bin, size = 12.5):
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
    # If binning not working try to add/remove 1 unit
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
    bin_number = (max_tot-min_tot)/bin_size
    bin_number = int(np.ceil(bin_number))
    max_tot = min_tot + bin_number*bin_size

    return min_tot, max_tot, bin_number

def get_most_hit_pixel(df):
    """
    Get the pixel with the highest number of hits in the hit map.

    Args:
        df: ROOT.RDataFrame    
    Returns:
        col (int): Column of the pixel
        row (int): Row of the pixel
    """
    hit_map = pf.hit_map(df, omit_plots=True)
    # Get the global bin number of the max value
    max_bin = hit_map.GetMaximumBin()  
    
    # Use ctypes to store integer values that can be modified by ROOT
    binx, biny, binz = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0)
    # Get bin indices
    hit_map.GetBinXYZ(max_bin, binx, biny, binz)
    # Convert ctypes values to Python integers
    binx_val = binx.value
    biny_val = biny.value
    col, row = (binx_val - 1, biny_val - 1)  # Convert ROOT bins (1-based) to matrix indices (0-based)
    return col, row