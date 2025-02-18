import ROOT
import click
import sifca_utils

sifca_utils.plotting.set_sifca_style()

# Set ROOT to batch mode if plots are omitted
omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)
colors = [ROOT.kRed, ROOT.kBlue]

# Map sensor positions
SENSOR_POS = {"6": 1, "7": 3, "8": 4, "9": 2}

def hit_map(df):
    """
    Plot the hit map of the ETROC. It is a matrix 16x16
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
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
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press enter to continue...")
    return hit_map
def plot_cal(df):
    """
    Plot the Cal of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 1)

    histograms = {}
    for i in range(2):
        canvas.cd(i+1)
        hist = df.Filter(f"Analogical_LV == {i}").Histo1D(
            ("cal", f"Analogical LV {i}", 1024, -0.5, 1023.5), "cal"
        )
        hist.GetXaxis().SetTitle("Cal")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical LV = {i}")
        hist.Draw()

        histograms[i] = hist

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")

def ToT(df):
    """
    Plot the ToT of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 1)

    histograms = {}
    
    for i in range(2):
        # Delta ToT depends on the floor of the ToT_CODE, it can be 2*t_bin or t_bin, in most of the cases it is 2*t_bin
        # Filter df to select data with the same Cal
        df_i = df.Filter(f"Analogical_LV == {i}")
	# Compute histograms limits
        t_bin = df_i.Mean("t_bin").GetValue()
        bin_size = 2*t_bin
        min_tot = -bin_size/2
        max_tot = 7+bin_size/2
        bin_number = int((max_tot-min_tot)/bin_size)
        print(f"Number of bins: {bin_number}")
        
	# Plot histogram
        canvas.cd(i+1)
        hist = df_i.Histo1D(
            ("ToT", f"Analogical LV {i}", bin_number, min_tot, max_tot), "ToT"
        )
        hist.GetXaxis().SetTitle("ToT/ns")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical LV = {i}")
        hist.Draw("")

        histograms[i] = hist

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")  
    return histograms

def ToT_CODE(df):
    """
    Plot the ToT_CODE of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 1)

    histograms = {}

    for i in range(2):
        canvas.cd(i+1)
	# Plot histogram
        hist = df.Filter(f"Analogical_LV == {i}").Histo1D(
            ("tot_code", f"Analogical LV {i}", 512, -0.5, 511.5), "tot_code"
        )
        hist.GetXaxis().SetTitle("ToT_CODE")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical LV = {i}")
        hist.Draw()

        histograms[i] = hist

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")

def ToA(df):
    """
    Plot the ToA of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 1)

    histograms = {}
    for i in range(2):

        # Delta ToA is t_bin
        # Filter df to select data with the same Cal
        df_i = df.Filter(f"Analogical_LV == {i}")
        # Compute histogram limits
        t_bin = df_i.Mean("t_bin").GetValue()
        bin_size = 2*t_bin
        min_toa = -bin_size/2
        max_toa = 14+bin_size/2
        bin_number = int((max_toa-min_toa)/bin_size)
        print(f"Number of bins: {bin_number}")
        
        canvas.cd(i+1)
	# Plot histogram
        hist = df_i.Histo1D(
            ("ToA", f"Analogical LV {i}", bin_number, min_toa, max_toa), "ToA"
        )
        hist.GetXaxis().SetTitle("ToA/ns")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical LV = {i}")
        hist.Draw()

        histograms[i] = hist

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")
    return histograms

def ToA_CODE(df):
    """
    Plot the ToA_CODE of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 1)

    histograms = {}

    for i in range(2):
        canvas.cd(i+1)
	# Compute histogram limits
        bin_size = 2*1
        min_toa = -bin_size/2
        max_toa = 1024+bin_size/2
        bin_number = int((max_toa-min_toa)/bin_size)
        print(f"Number of bins: {bin_number}")
	# Plot histogram
        hist = df.Filter(f"Analogical_LV == {i}").Histo1D(
            ("toa_code", f"Analogical LV {i}", bin_number, min_toa, max_toa), "toa_code"
        )
        hist.GetXaxis().SetTitle("ToA_CODE")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical LV = {i}")
        hist.Draw()

        histograms[i] = hist

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")

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
        t_bin = df_i.Mean("t_bin").GetValue()
        print(f"Row {i} t_bin: {t_bin}")
        bin_size = 2*t_bin
        min_toa = -bin_size/2
        max_toa = 14+bin_size/2
        bin_number = int((max_toa-min_toa)/bin_size)    

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

    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")
    return histograms

    

def t_bin(df):
    """
    Plot the t_bin of the ETROC
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 1)

    histograms = {}

    for i in range(2):
        canvas.cd(i+1)
        hist = df.Filter(f"Analogical_LV == {i}").Histo1D(
            ("t_bin", f"Analogical LV {i}", 1500, 0., 0.05), "t_bin"
        )
        hist.GetXaxis().SetTitle("t_bin/ns")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical LV = {i}")
        hist.Draw()

        histograms[i] = hist

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")


def ToT_together(df):
    """
    Plot the ToT of the ETROC in ns, plot the analogical and digital LV in the same plot with different colors

    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    df_list = {}
    for i in range(2):
        # Delta ToT depends on the floor of the ToT_CODE, it can be 2*t_bin or t_bin, in most of the cases it is 2*t_bin
        # Filter df to select data with the same Cal
        df_list[i] = df.Filter(f"Analogical_LV == {i}")

    histograms = []
    # Create histogram with the limits (change 1e-3 depending the normalisation)
    ROOT.gStyle.SetOptStat(000000)
    histograms.append(ROOT.TH2F("limits","",1, 0, 7, 1, 1e-3, 0.04))
    histograms[-1].Draw()
    histograms[-1].GetXaxis().SetTitle("ToT/ns")
    histograms[-1].GetYaxis().SetTitle(f"Counts")
    canvas.Draw()
    opt = "same"
    for i, df_i in df_list.items():
	# Compute binning
        t_bin = df_list[i].Mean("t_bin").GetValue()
        print(f"Analogical LV {i} t_bin: {t_bin}")
        bin_size = 2*t_bin
        min_tot = -bin_size/2
        max_tot = 7+bin_size/2
        bin_number = int((max_tot-min_tot)/bin_size)
        histograms.append(df_i.Histo1D(
            ("ToT", f"Analogical LV {i}", bin_number, min_tot, max_tot), "ToT"
        ))
        histograms[-1].SetDirectory(0)
        histograms[-1].SetLineColor(colors[i])
        legend.AddEntry(histograms[-1].GetValue(), f"Analogical LV {i}", "l")
        histograms[-1].DrawNormalized(opt, 1.0)
    legend.Draw()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")  

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

    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")
    return histograms

def fit_ToA_to_sinusoidal(histograms):
    """
    WARNING:
        NOT WORKING PROPERLY 
    Fit the ToA histogram to a sinusoidal function
    NOT WORKING PROPERLY, it is needed to fix the initial parameters of the fit function
    or change the fit function
    Args:
        histograms (dict): Dictionary with the histograms for each pixel
    """
    print("\033[91m***************************************************************\033[0m")
    print("\033[91m ATTENTION \033[0m")
    print("\033[91m This funtion is not working properly \033[0m")
    print("\033[91m***************************************************************\033[0m")


    # Fit function
    fit_function = ROOT.TF1("fit", "[0]*sin([1]*x+[2])+[3]", 0.2, 12.5)
    # Fit function parameters
    fit_function.SetParameter(0, 1)
    fit_function.SetParameter(1, 3.14)
    fit_function.SetParameter(2, 0)
    fit_function.SetParameter(3, 1e3)
    
    # Create canvas
    canvas = ROOT.TCanvas()
    # Divide canvas
    # Prepared for Analogical/Digital difference and to 4 pixels
    if len(histograms) == 2:
        canvas.Divide(2, 1)
        for i, hist in histograms.items():
            print(f"cd canvas {i}")
            canvas.cd(i+1)
            hist.Fit(fit_function, "R")
            hist.Draw("PE")

    elif len(histograms) == 4:
        canvas.Divide(2, 2)
        for i, hist in histograms.items():
            print(f"cd canvas {SENSOR_POS[str(i)]}, column {i}")
            canvas.cd(SENSOR_POS[str(i)])
            hist.Fit(fit_function, "R")
            hist.Draw("PE")
    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")

@click.command()
@click.argument('inputfiles', nargs=-1)
def main(inputfiles):
    # Open the file
    if inputfiles[0].split('.')[-1] != 'root':
        raise ValueError(f"Input file must have .root extension and it has .{inputfiles.split('.')[-1]}")

    df = ROOT.RDataFrame("Hits", list(inputfiles))
    # Plot the hit map
    hit_map(df)
    # Plot the Cal
    plot_cal(df)
    # Plot the ToT
    ToT(df)
    # ToT_CODE(df)

    # Plot the ToT together
    ToT_together(df)
    # Plot the ToA
    toa_histograms = ToA(df)
    # fit_ToA_to_sinusoidal(toa_histograms)
    # ToA_CODE(df)
    # toa_pixel_histograms = ToA_pixel(df)
    # fit_ToA_to_sinusoidal(toa_pixel_histograms)

    # Plot the t_bin
    # t_bin(df)
    # Cal_pixel(df)

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
