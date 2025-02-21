import ROOT
import utils as u
import numpy as np

# Map sensor positions
SENSOR_POS = {"6": 1, "7": 3, "8": 4, "9": 2}

colors = [
    ROOT.kRed+1, ROOT.kBlue+1,ROOT.kGreen+2, ROOT.kRed-7, ROOT.kBlue-7, ROOT.kGreen-5,
    ROOT.kMagenta+1, ROOT.kMagenta-5, ROOT.kOrange+2, ROOT.kOrange-3, ROOT.kCyan+1, ROOT.kCyan-6,
    ROOT.kYellow+2, ROOT.kYellow-7, ROOT.kPink+1, ROOT.kViolet+1, ROOT.kAzure+2, ROOT.kSpring+5, 
    ROOT.kTeal+3, ROOT.kBlack, ROOT.kGray+2
]


######################################################
# General Functions for the ETROC in a single canvas #
# Not to compare plots                               #
######################################################

def hit_map(df):
    """
    Plot the hit map of the ETROC. It is a matrix 16x16
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
        omit_plots (bool): If True, the plot will not be shown. Default is False.
    Returns:
        hit_map (ROOT.TH2F): Hit map histogram
        max_pixel (int): Pixel with the highest number of entries
    """
    c = ROOT.TCanvas()
    c.SetRightMargin(0.2) 
    hit_map = df.Histo2D(("hit_map", "Hit map", 16, 0., 16., 16, 0., 16.), "col", "row")
    hit_map.GetXaxis().SetTitle("Column")
    hit_map.GetYaxis().SetTitle("Row")
    hit_map.GetZaxis().SetTitle("Hits")
    hit_map.Draw("colz")
    c.Update()
    c.Draw()
    # Keep the canvas open until user input
    input("Press enter to continue...")
    return hit_map


def plot_cal(df, color = ROOT.kBlack):
    """
    Plot the Cal of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
        omit_plots (bool): If True, the plot will not be shown. Default is False.
    """
    canvas = ROOT.TCanvas()
    hist = df.Histo1D(
        ("cal", f"", 1024, -0.5, 1023.5), "cal"
    )
    hist.GetXaxis().SetTitle("Cal")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetLineColor(color)
    hist.SetTitle("")
    hist.Draw()
    # Add text with the max cal
    max_cal = u.get_max_cal(df)
    text = ROOT.TLatex()
    text.SetNDC()
    text.SetTextSize(0.03)
    text.DrawLatex(0.7, 0.8, f"Max Cal: {max_cal}")
    canvas.Update()
    
    # Keep the canvas open until user input
    input("Press Enter to continue...")
    return hist

def ToT(df):
    """
    Plot the ToT of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    if "ToT" not in df.GetColumnNames():
        df = u.compute_ToT(df)
    canvas = ROOT.TCanvas()

    # Compute histograms limits
    min_tot, max_tot, bin_number = u.get_ToT_histograms_limits(df.Mean("t_bin").GetValue())
        
	# Plot histogram
    hist = df.Histo1D(
        ("ToT", "", bin_number, min_tot, max_tot), "ToT"
    )
    hist.GetXaxis().SetTitle("ToT/ns")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle("")
    hist.Draw("")

    canvas.Update()
    # Keep the canvas open until user input
    input("Press Enter to continue...")  
    return hist

def ToT_CODE(df):
    """
    Plot the ToT_CODE of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()

	# Plot histogram
    hist = df.Histo1D(
        ("tot_code","", 512, -0.5, 511.5), "tot_code"
        )
    hist.GetXaxis().SetTitle("ToT_CODE")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle(f"")
    hist.Draw()

    canvas.Update()
    # Keep the canvas open until user input
    input("Press Enter to continue...")

def ToA(df):
    """
    Plot the ToA of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    if "ToA" not in df.GetColumnNames():
        df = u.compute_ToA(df)
    canvas = ROOT.TCanvas()
    
    # Compute histogram limits
    min_toa, max_toa, bin_number = u.get_ToA_histograms_limits(df.Mean("t_bin").GetValue())

	# Plot histogram
    hist = df.Histo1D(
        ("ToA", f"", bin_number, min_toa, max_toa), "ToA"
    )
    hist.GetXaxis().SetTitle("ToA/ns")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle(f"")
    hist.Draw()

    canvas.Update()
    # Keep the canvas open until user input
    input("Press Enter to continue...")
    return hist

def ToA_CODE(df):
    """
    Plot the ToA_CODE of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()

	# Compute histogram limits
    bin_size = 2*1
    min_toa = -bin_size/2
    max_toa = 1024+bin_size/2
    bin_number = int((max_toa-min_toa)/bin_size)

	# Plot histogram
    hist = df.Histo1D(
        ("toa_code", f"Analogical LV {i}", bin_number, min_toa, max_toa), "toa_code"
    )
    hist.GetXaxis().SetTitle("ToA_CODE")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle("")
    hist.Draw()

    canvas.Update()
    # Keep the canvas open until user input
    input("Press Enter to continue...")
    

def t_bin(df):
    """
    Plot the t_bin of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()

    hist = df.Histo1D(
        ("t_bin", f"Analogical LV {i}", 1500, 0., 0.05), "t_bin"
    )
    hist.GetXaxis().SetTitle("t_bin/ns")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle(f"")
    hist.Draw()

    canvas.Update()
    # Keep the canvas open until user input
    input("Press Enter to continue...")

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


######################################################
# Stacked plots                                      #
# Functions to compare different runs/cuts           #
######################################################
### TO DO Check function

def draw_ToA_stacked(df_dict):
    """
    Draw the ToA histograms in the same canvas stacked for the
    different runs
    df_dict (dict): Dictionary with the different dataframes
        keys: Name of the run
        values: RDataFrame with the hits
    """
    # Create Canvas
    c = ROOT.TCanvas()
    histograms = []
    stack = ROOT.THStack("stack", f"")

    legend = (ROOT.TLegend(0.7, 0.8, 0.9, 0.9))
        
    # Loop over dfs
    t_bin = []
    # Compute histogram limits
    for df_i in df_dict.values():
        if "t_bin" not in df_i.GetColumnNames():
            df_i = u.compute_tbin(df_i)
        t_bin.append(df_i.Mean("t_bin").GetValue())    
    min_toa, max_toa, bin_number = u.get_ToA_histograms_limits(np.mean(np.array(t_bin)))
    
    for i_color, (i, df_i) in enumerate(df_dict.items()):
        if "ToA" not in df_i.GetColumnNames():
            df_i = u.compute_ToA(df_i)
        
        # Create histogram
        histograms.append(df_i.Histo1D(
            ("ToA", f"", bin_number, min_toa, max_toa), "ToA"
            ).GetValue()
            )

        histograms[-1].SetDirectory(0)
        legend.AddEntry(histograms[-1], f"{i}", "l")
        histograms[-1].SetLineColor(colors[i_color])

        # Set fill characteristic
        histograms[-1].SetFillColorAlpha(colors[i_color], 1)
        histograms[-1].SetFillStyle(3001)
    # Sort histograms by the number of entries first the one with more entries
    histograms.sort(key=lambda x: x.GetEntries(), reverse=True)
    for histo_i in (histograms):
        stack.Add(histo_i)
    stack.Draw("hist fill")
    stack.GetXaxis().SetTitle("ToA/ns")
    stack.GetYaxis().SetTitle("Counts")
    stack.SetTitle(f"")
    legend.Draw()
    c.Update()

    input("Press enter to continue...")


def draw_ToA_normalised(df_dict, y_limit:float=0.05):
    """
    Draw the ToA histograms in the same canvas normalised for the
    different runs
    df_dict (dict): Dictionary with the different dataframes
        keys: Name of the run
        values: RDataFrame with the hits
    y_limit (float): Y limit for the histograms
    """

    c = ROOT.TCanvas()
    histograms = []
    
    # Remove statistics values
    ROOT.gStyle.SetOptStat(00000)
    # Create limits histogram 
    # Limits:
    # filter 0 : 7e-3
    # filter 1 : 0.05
    # filter -1 : 0.04
    histograms.append(ROOT.TH2F("limits", "", 1, 0, 14, 1, 1e-3, y_limit))
    histograms[-1].GetXaxis().SetTitle("ToA/ns")
    histograms[-1].GetYaxis().SetTitle("Counts")
    histograms[-1].SetTitle(f"")
    histograms[-1].Draw()

    legend = ROOT.TLegend(0.2, 0.8, 0.5, 0.9)
    # Loop over df to select binning as the mean
    t_bin = []
    for df_i in df_dict.values():
        if "t_bin" not in df_i.GetColumnNames():
            df_i = u.compute_tbin(df_i)
        t_bin.append(df_i.Mean("t_bin").GetValue())
    min_toa, max_toa, bin_number = u.get_ToA_histograms_limits(np.mean(np.array(t_bin)))

    # Loop over dfs to generate histograms and plot them
    for i_color, (i, df_i) in enumerate(df_dict.items()):
        # Compue ToA if not present
        if "ToA" not in df_i.GetColumnNames():
            df_i = u.compute_ToA(df_i)
        # Create histogram
        histograms.append(df_i.Histo1D(
                ("ToA", f"", bin_number, min_toa, max_toa), "ToA"
            ).GetValue()
            )
        histograms[-1].SetDirectory(0)
        histograms[-1].SetLineColor(colors[i_color])
        histograms[-1].SetMarkerColor(colors[i_color])
        legend.AddEntry(histograms[-1], f"{i}", "l")
        histograms[-1].DrawNormalized("same")
    legend.Draw()
    c.Draw()
    input("Press enter to continue...")


def draw_ToA_substraction(df_dict):
    """
    Draw the substraction of the ToA histograms for the different runs
    df_dict (dict): Dictionary with the different dataframes
        keys: Name of the run
        values: RDataFrame with the hits
    """
    c = ROOT.TCanvas()
    histograms = []
    draw_hist = []

    # Loop over df to select binning as the mean
    t_bin = []
    for df_i in df_dict.values():
        if "t_bin" not in df_i.GetColumnNames():
            df_i = u.compute_tbin(df_i)
        t_bin.append(df_i.Mean("t_bin").GetValue())
    t_bin = np.mean(np.array(t_bin))
    min_toa, max_toa, bin_number = u.get_ToA_histograms_limits(t_bin)

    # Loop over df to create histograms
    for df_i in df_dict.values():
        h = df_i.Histo1D(
            ("ToA", f"", bin_number, min_toa, max_toa), "ToA"
            ).GetValue()
        h.SetDirectory(0)
        # Normalize histogram
        h.Scale(1/h.Integral())
        histograms.append(h)
    # Substract and draw histograms
    draw_hist.append(histograms[0].Clone())
    # Subtract normalized histograms
    draw_hist[-1].Add(histograms[1], -1)  
    draw_hist[-1].SetDirectory(0)
    draw_hist[-1].SetTitle(f"Substraction")
    draw_hist[-1].Draw()
    draw_hist[-1].GetXaxis().SetTitle("ToA/ns")
    draw_hist[-1].GetYaxis().SetTitle("Counts")
    
    c.Draw()
    input("Press enter to continue...")