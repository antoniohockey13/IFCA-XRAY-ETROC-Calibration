import ROOT
import utils as u
import numpy as np

# Map sensor positions
SENSOR_POS = {"6": 1, "7": 3, "8": 4, "9": 2}

######################################################
# Functions prepared for the wirebounded ETROCs      #
# Hardcoded values of the columns used               #
######################################################

def ToA_pixel(df):
    """
    Plot the ToA of the ETROC in for each column 6, 7, 8 and 9. 
    This function is prepared for the wirebounded ETROCs.

    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    
    Returns:
        histograms (list): List with the histograms for each pixel
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 2)
    histograms = {}
    for i in range(6, 10):
        canvas.cd(SENSOR_POS[str(i)])

        # Filter dataframe to select col and obtain t_bin
        df_i = df.Filter(f"col == {i}")
        # Compute histogram limits
        min_toa, max_toa, bin_number = u.get_ToA_histograms_limits(df_i.Mean("t_bin").GetValue())
        print(f"Row {i} t_bin: {df_i.Mean('t_bin').GetValue()}")
        # Create histogram
        hist = df_i.Histo1D(
            ("ToA", f"Row {i}", bin_number, min_toa, max_toa), "ToA"
        )
        # Configure histogram
        hist.GetXaxis().SetTitle("ToA/ns")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Column = {i}")
        hist.Draw()

        histograms[i] = hist

    canvas.Update()
    # Keep the canvas open until user input
    input("Press Enter to continue...")
    return histograms


def Cal_pixel(df):
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 2)
    histograms = {}
    for i in range(6, 10):
        canvas.cd(SENSOR_POS[str(i)])

        # Filter dataframe to select col
        df_i = df.Filter(f"col == {i}")
        bin_size = 1
        min_cal = -bin_size/2
        max_cal = 1024+bin_size/2
        bin_number = int((max_cal-min_cal)/bin_size)        
        print(f"Col: {i} Number of bins: {bin_number}")

        # Create histogram
        hist = df_i.Histo1D(
            ("cal", f"Row {i}", bin_number, min_cal, max_cal), "cal"
        )
        # Configure histogram
        hist.GetXaxis().SetTitle("Cal")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Column = {i}")
        hist.Draw()

        histograms[i] = hist

    canvas.Update()

    # Keep the canvas open until user input
    input("Press Enter to continue...")
    return histograms
