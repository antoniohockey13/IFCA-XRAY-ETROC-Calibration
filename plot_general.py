import ROOT
import click
import sifca_utils
import utils as u

sifca_utils.plotting.set_sifca_style()

# Set ROOT to batch mode if plots are omitted
omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)
colors = [ROOT.kRed, ROOT.kBlue]

# Map sensor positions
SENSOR_POS = {"6": 1, "7": 3, "8": 4, "9": 2}

######################################################
# General Functions for the ETROC                    #
######################################################

def hit_map(df):
    """
    Plot the hit map of the ETROC. It is a matrix 16x16
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
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
    hist = df.Histo1D(
        ("cal", f"Analogical LV {i}", 1024, -0.5, 1023.5), "cal"
    )
    hist.GetXaxis().SetTitle("Cal")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle()
    hist.Draw()

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

    # Compute histograms limits
    min_tot, max_tot, bin_number = u.get_ToT_histograms_limits(df.Mean("t_bin").GetValue())
        
	# Plot histogram
    hist = df.Histo1D(
        ("ToT", "", bin_number, min_tot, max_tot), "ToT"
    )
    hist.GetXaxis().SetTitle("ToT/ns")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle()
    hist.Draw("")

    canvas.Update()
    if not omit_plots:
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
    
    # Compute histogram limits
    min_toa, max_toa, bin_number = u.get_ToA_histograms_limits(df.Mean("t_bin").GetValue())

	# Plot histogram
    hist = df.Histo1D(
        ("ToA", f"Analogical LV {i}", bin_number, min_toa, max_toa), "ToA"
    )
    hist.GetXaxis().SetTitle("ToA/ns")
    hist.GetYaxis().SetTitle(f"Counts")
    hist.SetTitle(f"")
    hist.Draw()

    canvas.Update()
    if not omit_plots:
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
    hist.SetTitle()
    hist.Draw()

    canvas.Update()
    if not omit_plots:
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
    hist.SetTitle(f"Analogical LV = {i}")
    hist.Draw()

    canvas.Update()
    if not omit_plots:
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

    if not omit_plots:
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

    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")
    return histograms


######################################################
# Main function                                     #
######################################################

@click.command()
@click.argument('inputfile', nargs=1)
def main(inputfile):
    # Open the file
    if inputfile.split('.')[-1] != 'root':
        raise ValueError(f"Input file must have .root extension and it has .{inputfiles.split('.')[-1]}")

    df = ROOT.RDataFrame("Hits", inputfile)
    # Plot the hit map
    hit_map(df)
    # Filter to Analogical_LV
    df = df.Define("Analogical_LV", "floor(col/8)")
    # Plot the Cal
    plot_cal(df)
    df_Ana0 = df.Filter("Analogical_LV == 0")
    df_Ana1 = df.Filter("Analogical_LV == 1")
    max_cal_Ana0 = u.get_max_cal(df_Ana0)
    max_cal_Ana1 = u.get_max_cal(df_Ana1)
    print(f"Max cal Ana0: {max_cal_Ana0}")
    print(f"Max cal Ana1: {max_cal_Ana1}")
    # Filter to the max cal
    df_Ana0 = df_Ana0.Filter(f"abs(cal-{max_cal_Ana0})<0.5")
    df_Ana1 = df_Ana1.Filter(f"abs(cal-{max_cal_Ana1})<0.5")
    print("Filter to max cal done")
    # Compute ToT
    df_Ana0 = u.compute_ToT(df_Ana0)
    df_Ana1 = u.compute_ToT(df_Ana1)
    print("Compute ToT done")
    print(df_Ana0.GetColumnNames())
    # Plot the ToT
    ToT(df_Ana0)
    print("Plot ToT done")
    # Plot the ToA
    toa_histograms = ToA(df)
    
if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
