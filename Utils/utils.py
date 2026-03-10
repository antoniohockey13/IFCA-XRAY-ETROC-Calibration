import ROOT
import numpy as np
import ctypes
import os

from . import plot_functions as pf


ns = 1
# Constant value dependant only on the ETROC configuration 
T3 = 3.125* ns
# Constant value dependant on the clock configuration 40MHZ --> 12.5 ns
T_WINDOW = 12.5 * ns


def ensure_outdir(outdir):
    os.makedirs(outdir, exist_ok=True)


def write_to_fout(fout, *objs):
    if fout is None:
        return
    fout.cd()
    for obj in objs:
        if obj:
            obj.Write("", ROOT.TObject.kOverwrite)


def finalize_canvas(canvas, outdir, filename, fout=None, *objs, pause=True):
    canvas.Update()
    if pause:
        input("Press Enter to continue...")
    outpath = os.path.join(outdir, filename)
    canvas.SaveAs(outpath)
    write_to_fout(fout, *objs, canvas)
    return outpath

def circular_dt(t1, t2, T=12.5):
    dt = t1 - t2
    return (dt + 0.5 * T) % T - 0.5 * T


def apply_pixel_alignment_to_map(m, dcol0, drow0): 
    out = {} 
    for k, (toa, tot, cal, col, row) in m.items(): 
        out[k] = (toa, tot, cal, col - dcol0, row - drow0) 
    return out 

def get_max_cal(df: ROOT.RDataFrame):
    """
    Get the most repeated cal value in the dataframe
    Args:
        df: ROOT.RDataFrame
    Returns:
        max_cal: int
    """
    hist = df.Histo1D(("cal", "cal", 1024, -0.5, 1023.5), col_name)
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

def get_cal_per_pixel(df: ROOT.RDataFrame, ncols=16, nrows=16):
    """
    Get the most frequent cal value for each pixel (col,row).

    Returns:
        cal_map: dict[(col,row)] = most frequent cal
    """
    cal_map = {}

    for col in range(ncols):
        for row in range(nrows):
            df_pix = df.Filter(f"col == {col} && row == {row}")
            n_pix = df_pix.Count().GetValue()

            if n_pix == 0:
                continue

            max_cal = get_max_cal(df_pix)
            cal_map[(col, row)] = max_cal

    return cal_map

def get_cal_pixel_cut(df: ROOT.RDataFrame, ncols=16, nrows=16):
    """
    Build a ROOT filter string selecting, for each pixel, the most frequent cal value.
    """
    cal_map = get_cal_per_pixel(df, ncols=ncols, nrows=nrows)

    cuts = []
    for (col, row), cal in cal_map.items():
        cuts.append(
            f"(col == {col} && row == {row} && abs(cal - {cal}) < 2.5)"
        )

    if not cuts:
        return ""

    return " || ".join(cuts)

    
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

def compute_t(df, cut=None):
    """
    Compute: t_bin, ToA and ToT.
    Args:
        df: ROOT.RDataFrame
        cut: float. Cut used .... If None, the cut of each event is used
    Returns:
        df: ROOT.RDataFrame
    """
    if cut is not None:
        df = df.Filter(cut)

    df = compute_tbin(df)
    df = compute_ToA(df)
    df = compute_ToT(df)
    return df

def get_ToA_histograms_limits(t_bin, size = 12.5):
    """
    Get the limits for the histograms

    Delta ToA is 2*t_bin
    
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


def get_cal_histogram_limits(df: ROOT.RDataFrame):
    """
    Get the limits for cal.

    Args:
        df: ROOT.RDataFrame
    Returns:
        min_cal (float)
        max_cal (float)
        bin_number (int)
    """
    min_cal = int(df.Min("cal").GetValue())
    max_cal = int(df.Max("cal").GetValue())

    min_cal = min_cal - 2.5
    max_cal = max_cal + 2.5
    bin_number = int(max_cal - min_cal)

    return min_cal, max_cal, bin_number


def get_most_hit_pixel(df):
    """
    Get the pixel with the highest number of hits in the hit map.

    Args:
        df: ROOT.RDataFrame    
    Returns:
        col (int): Column of the pixel
        row (int): Row of the pixel
    """
    hit_map = pf.hit_map(df, omit_plots=False)
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

def beam_center_from_gaussian(df, name="beam_center"):

    arr = df.AsNumpy(["col", "row"])
    cols = arr["col"]
    rows = arr["row"]

    hcol = ROOT.TH1D(f"hcol_{name}", ";col;Events", 16, -0.5, 15.5)
    hrow = ROOT.TH1D(f"hrow_{name}", ";row;Events", 16, -0.5, 15.5)

    for c in cols:
        hcol.Fill(int(c))

    for r in rows:
        hrow.Fill(int(r))

    peak_col, peak_row = get_most_hit_pixel(df)

    fcol = ROOT.TF1(f"fcol_{name}", "gaus", peak_col-4, peak_col+4)
    frow = ROOT.TF1(f"frow_{name}", "gaus", peak_row-4, peak_row+4)

    hcol.Fit(fcol, "RQ")
    hrow.Fit(frow, "RQ")

    mean_col = fcol.GetParameter(1)
    mean_row = frow.GetParameter(1)

    print(f"[INFO] Beam center from Gaussian fit:")
    print(f" col = {mean_col:.3f}")
    print(f" row = {mean_row:.3f}")

    c = ROOT.TCanvas(f"c_{name}", name, 900, 400)
    c.Divide(2,1)

    c.cd(1)
    hcol.Draw("HIST")
    fcol.Draw("same")

    c.cd(2)
    hrow.Draw("HIST")
    frow.Draw("same")

    c.Update()

    input("Press Enter to continue...")

    return mean_col, mean_row
