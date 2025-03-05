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

def hit_map(df, title=""):
    """
    Plot the hit map of the ETROC. It is a matrix 16x16
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
        title (str): Title of the plot. Default is ""
    Returns:
        hit_map (ROOT.TH2F): Hit map histogram
        max_pixel (int): Pixel with the highest number of entries
    """
    c = ROOT.TCanvas()
    c.SetRightMargin(0.2) 
    hit_map = df.Histo2D(("hit_map", "Hit map", 17, -0.5, 16.5, 17, -0.5, 16.5), "col", "row")
    hit_map.GetXaxis().SetTitle("Column")
    hit_map.GetYaxis().SetTitle("Row")
    hit_map.GetZaxis().SetTitle("Hits")
    hit_map.Draw("colz")
    hit_map.SetTitle(title)
    c.Update()
    c.Draw()
    # Keep the canvas open until user input
    input("Press enter to continue...")
    return hit_map


def plot_cal(df, color = ROOT.kBlack, title="", omit_plots=False):
    """
    Plot the Cal of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
        color (int): Color of the histogram. Default is ROOT.kBlack
        omit_plots (bool): If True, the plot will not be shown. Default is False.
        title (str): Title of the plot. Default is ""
    Returns:
        hist (ROOT.TH1F): Histogram with the cal values
    """
    canvas = ROOT.TCanvas()
    hist = df.Histo1D(
        ("cal", f"", 1024, -0.5, 1023.5), "cal"
    )
    hist.GetXaxis().SetTitle("Cal")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetLineColor(color)
    hist.SetTitle(title)
    hist.SetTitle("")
    hist.Draw()
    # Add text with the max cal
    max_cal = u.get_max_cal(df)
    text = ROOT.TLatex()
    text.SetNDC()
    text.SetTextSize(0.03)
    text.DrawLatex(0.7, 0.8, f"Max Cal: {max_cal}")
    canvas.SetLogy()
    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")
        
    return hist.GetValue()

def ToT(df, title=""):
    """
    Plot the ToT of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
        title (str): Title of the plot. Default is ""
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
    hist.SetTitle(title)
    hist.Draw("")

    canvas.Update()
    # Keep the canvas open until user input
    input("Press Enter to continue...")  
    return hist

def ToT_CODE(df, title=""):
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
    hist.SetTitle(title)
    hist.Draw()

    canvas.Update()
    # Keep the canvas open until user input
    input("Press Enter to continue...")

def ToA(df, title="", omit_plots=False):
    """
    Plot the ToA of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
        title (str): Title of the plot. Default is ""
        omit_plots (bool): If True, the plot will not be shown. Default is False
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
    hist.SetTitle(title)
    hist.Draw()

    # Keep the canvas open until user input
    if not omit_plots:
        canvas.Update()
        input("Press Enter to continue...")
    return hist


def fit_ToA_sin(df=None, toa_histogram=None, title=""):
    """
    Fit the ToA to a sinusoidal function
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits. Default is None.
        toa_histogram (ROOT.TH1F): ToA histogram. Default is None.
        title (str): Title of the plot. Default is None.
    Returns:
        x_max (float): First maximum of the sinusoidal fit
        x_min (float): First minimum of the sinusoidal fit
        omega (float): Angular frequency of the sinusoidal fit
        omega_error (float): Error of the angular frequency of the sinusoidal fit
    """
    try:
        if toa_histogram is None and df is None:
            raise ValueError("Either df or toa_histogram must be provided")
        elif toa_histogram is None:
            toa_histogram = ToA(df, omit_plots=True)
        
        
        # Fit ToA to sinusoidal
        c = ROOT.TCanvas()
        toa_histogram.Draw()
        toa_histogram.GetXaxis().SetTitle("ToA/ns")
        toa_histogram.SetTitle(title)
        fit = ROOT.TF1("fit", "[0]*sin([1]*x+[2])+[3]", 0, 10)
        fit.SetParNames("Amplitude", "Angular Frequency", "Phase", "Offset")
        # Set range to amplitude so it is always positive
        fit.SetParameter("Amplitude", 100)
        fit.SetParLimits(0, 0, 1e6)
        fit.SetParameter("Angular Frequency", 2.5)
        fit.SetParLimits(1, 0, 1e6)
        fit.SetParameter("Phase", 0)
        fit.SetParLimits(2, -2*np.pi, 2*np.pi)
        fit.SetParameter("Offset", 300)
        toa_histogram.Fit(fit, "R")
        fit.Draw("same")
        
        # Add text with period of the fit
        text = ROOT.TLatex()
        text.SetNDC()
        text.SetTextSize(0.03)
        text.DrawLatex(0.7, 0.8, f"Period: {2*np.pi/fit.GetParameter("Angular Frequency"):.3f} ns")
        c.Update()
        c.Draw()
        # Print error of angular frequency
        print(f"Period: {2*np.pi/fit.GetParameter('Angular Frequency')} +- {2*np.pi*np.log(fit.GetParameter('Angular Frequency'))*fit.GetParError(1)} ns")
        # Compute first minimum position
        n = [-5, -3, -1, 1, 3, 5]
        x_min = []
        for i in n:
            x_min.append(((2*i+1)*np.pi/2-fit.GetParameter("Phase"))/fit.GetParameter("Angular Frequency"))
        x_min.sort()
        x_min = list(filter(lambda x: x > 0.6, x_min))[0]
        print(f"First minimum: {x_min:.3f} ns")
        # Compute firs maximum
        n = [-4, -2, 0, 2, 4]
        x_max = []
        for i in n:
            x_max.append(((2*i+1)*np.pi/2-fit.GetParameter("Phase"))/fit.GetParameter("Angular Frequency"))
        x_max.sort()
        x_max = list(filter(lambda x: x > x_min, x_max))[0]
        print(f"First maximum: {x_max:.3f} ns")
        input("Press Enter to continue...")
        return x_max, x_min, fit.GetParameter("Angular Frequency"), fit.GetParError(1)

    

    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
        return

def fast_fourier_transform_ToA(df=None, toa_histogram=None, title=None):
    """
    Compute the Fast Fourier Transform of the ToA histogram
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits. Default is None.
        toa_histogram (ROOT.TH1F): ToA histogram. Default is None.
        title (str): Title of the plot. Default is None.
    """
    try:
        if toa_histogram is None and df is None:
            raise ValueError("Either df or toa_histogram must be provided")
        elif toa_histogram is None:
            toa_histogram = ToA(df, omit_plots=True)
        # Get the TH1 object from the RDataFrame
        toa_histogram = toa_histogram.GetValue()
        # Compute the Fast Fourier Transform
        c = ROOT.TCanvas()
        n_bins = toa_histogram.GetNbinsX()
        n_bins_array = np.array([n_bins], dtype=np.int32)
        # Compute the Fast Fourier Transform
        fft = ROOT.TVirtualFFT.FFT(1, n_bins_array, "R2C M")
        # Fill the FFT with the histogram data
        for i in range(n_bins):
            fft.SetPoint(i, toa_histogram.GetBinContent(i+1))
        fft.Transform()

        # Get real and imaginary parts of the FFT
        re, im = np.zeros(n_bins), np.zeros(n_bins)
        fft.GetPointsComplex(re, im)  

        # Compute magnitude spectrum
        magnitude = np.sqrt(re**2 + im**2)

        # Create a new histogram for the magnitude spectrum
        h_fft = ROOT.TH1D("h_fft", "", n_bins//2, 0, n_bins//2)
        for i in range(n_bins//2):
            h_fft.SetBinContent(i+1, magnitude[i])

        # Draw original histogram and FFT magnitude
        h_fft.GetXaxis().SetTitle("Frequency")
        h_fft.GetYaxis().SetTitle("Magnitude")
        h_fft.SetTitle(title)
        h_fft.Draw()
        c.SetLogy()
        c.Draw()
        input("Press Enter to continue...")


    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
        return

def ToA_CODE(df, title=""):
    """
    Plot the ToA_CODE of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
        title (str): Title of the plot. Default is ""
    """
    canvas = ROOT.TCanvas()

	# Compute histogram limits
    bin_size = 2*1
    min_toa = -bin_size/2
    max_toa = 1024+bin_size/2
    bin_number = int((max_toa-min_toa)/bin_size)

	# Plot histogram
    hist = df.Histo1D(
        ("toa_code", f"", bin_number, min_toa, max_toa), "toa_code"
    )
    hist.GetXaxis().SetTitle("ToA_CODE")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle(title)
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
    try:
        if len(df_dict) != 2:
            raise ValueError("Only two files can be substracted")
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
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
        return
    

def draw_Cal_together_different_canvas(df_dict):
    """
    """
    c = ROOT.TCanvas()
    if len(df_dict) == 2:
        c.Divide(2,1)
    else:
        c.Divide(int(np.ceil(len(df_dict)/2)), 2)
    hist = []
    for i, (name, df) in enumerate(df_dict.items()):
        c.cd(i+1)
        ROOT.gPad.SetLogy()
        hist.append(df.Histo1D(
            ("cal", f"", 1024, -0.5, 1023.5), "cal"
        ).GetValue())
        hist[-1].GetXaxis().SetTitle("Cal")
        hist[-1].GetYaxis().SetTitle(f"Counts")
        hist[-1].SetLineColor(colors[i])
        hist[-1].SetDirectory(0)
        hist[-1].SetTitle(f"{name}")
        hist[-1].Draw()

        # Text in the plot
        text = ROOT.TLatex()
        text.SetNDC()
        text.SetTextSize(0.04)
        text.DrawLatex(0.6, 0.7, f"Max cal = {u.get_max_cal(df)}")
    c.Update()
    c.Draw()
    input("Press enter to continue...")