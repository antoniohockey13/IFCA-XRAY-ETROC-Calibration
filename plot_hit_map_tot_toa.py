import ROOT
import click
import sifca_utils
import numpy as np

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

def ToT(df):
    """
    Plot the ToT of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 1)

    histograms = []
    
    for i in range(2):
        # Delta ToT depends on the floor of the ToT_CODE, it can be 2*t_bin or t_bin, in most of the cases it is 2*t_bin
        # Filter df to select data with the same Cal
        df_i = df.Filter(f"Analogical_HV == {i}")
        t_bin = df_i.Mean("t_bin").GetValue()
        bin_size = 2*t_bin
        min_tot = -bin_size/2
        max_tot = 7+bin_size/2
        bin_number = int((max_tot-min_tot)/bin_size)
        print(f"Number of bins: {bin_number}")
        
        canvas.cd(i+1)
        hist = df_i.Histo1D(
            ("ToT", f"Analogical HV {i}", bin_number, min_tot, max_tot), "ToT"
        )
        hist.GetXaxis().SetTitle("ToT/ns")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical HV = {i}")
        hist.Draw("")

        histograms.append(hist)

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")  
    return histograms

def ToA(df):
    """
    Plot the ToA of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    """
    canvas = ROOT.TCanvas()
    canvas.Divide(2, 1)

    histograms = []
    for i in range(2):
        # Delta ToA is t_bin
        # Filter df to select data with the same Cal
        df_i = df.Filter(f"Analogical_HV == {i}")
        t_bin = df_i.Mean("t_bin").GetValue()
        bin_size = 2*t_bin
        min_toa = -bin_size/2
        max_toa = 14+bin_size/2
        bin_number = int((max_toa-min_toa)/bin_size)
        print(f"Number of bins: {bin_number}")
        canvas.cd(i+1)
        hist = df_i.Histo1D(
            ("ToA", f"Analogical HV {i}", bin_number, min_toa, max_toa), "ToA"
        )
        hist.GetXaxis().SetTitle("ToA/ns")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical HV = {i}")
        hist.Draw()

        histograms.append(hist)

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

    histograms = []

    for i in range(2):
        canvas.cd(i+1)
        hist = df.Filter(f"Analogical_HV == {i}").Histo1D(
            ("t_bin", f"Analogical HV {i}", 1500, 0., 0.05), "t_bin"
        )
        hist.GetXaxis().SetTitle("t_bin/ns")
        hist.GetYaxis().SetTitle(f"Counts")
        hist.SetTitle(f"Analogical HV = {i}")
        hist.Draw()

        histograms.append(hist)

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")


def ToT_together(df):
    canvas = ROOT.TCanvas()
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    df_list = {}
    # t_bin = -1
    for i in range(2):
        # Delta ToT depends on the floor of the ToT_CODE, it can be 2*t_bin or t_bin, in most of the cases it is 2*t_bin
        # Filter df to select data with the same Cal
        df_list[i] = df.Filter(f"Analogical_HV == {i}")
    #     t_bin = max(t_bin, df_list[i].Mean("t_bin").GetValue())
    #     print(f"Analogical HV {i} t_bin: {t_bin}")

    # bin_size = 2*t_bin
    # min_tot = -bin_size/2
    # max_tot = 7+bin_size/2
    # bin_number = int((max_tot-min_tot)/bin_size)
    # print(f"Number of bins: {bin_number}")
    histograms = []
    ROOT.gStyle.SetOptStat(000000)
    histograms.append(ROOT.TH2F("limits","",1, 0, 7, 1, 1e-3, 0.04))
    histograms[-1].Draw()
    histograms[-1].GetXaxis().SetTitle("ToT/ns")
    histograms[-1].GetYaxis().SetTitle(f"Counts")
    canvas.Draw()
    opt = "same"
    for i, df_i in df_list.items():
        t_bin = df_list[i].Mean("t_bin").GetValue()
        print(f"Analogical HV {i} t_bin: {t_bin}")
        bin_size = 2*t_bin
        min_tot = -bin_size/2
        max_tot = 7+bin_size/2
        bin_number = int((max_tot-min_tot)/bin_size)
        histograms.append(df_i.Histo1D(
            ("ToT", f"Analogical HV {i}", bin_number, min_tot, max_tot), "ToT"
        ))
        histograms[-1].SetDirectory(0)
        histograms[-1].SetLineColor(colors[i])
        legend.AddEntry(histograms[-1].GetValue(), f"Analogical HV {i}", "l")
        histograms[-1].DrawNormalized(opt, 1.0)
    legend.Draw()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")  


@click.command()
@click.argument('inputfile', nargs=1)
def main(inputfile):
    # Open the file
    if inputfile.split('.')[-1] != 'root':
        raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")
    
    f = ROOT.TFile.Open(inputfile)
    df = ROOT.RDataFrame("Hits", f)

    # Plot the hit map
    # hit_map(df)

    # Plot the ToT
    ToT(df)

    # Plot the ToT together
    ToT_together(df)
    # Plot the ToA
    ToA(df)

    # Plot the t_bin
    # t_bin(df)

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")