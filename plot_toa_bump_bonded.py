import ROOT
import click
import numpy as np
import sifca_utils
sifca_utils.plotting.set_sifca_style()

colors = [
    ROOT.kRed+1, ROOT.kBlue+1,ROOT.kGreen+2, ROOT.kRed-7, ROOT.kBlue-7, ROOT.kGreen-5,
    ROOT.kMagenta+1, ROOT.kMagenta-5, ROOT.kOrange+2, ROOT.kOrange-3, ROOT.kCyan+1, ROOT.kCyan-6,
    ROOT.kYellow+2, ROOT.kYellow-7, ROOT.kPink+1, ROOT.kViolet+1, ROOT.kAzure+2, ROOT.kSpring+5, 
    ROOT.kTeal+3, ROOT.kBlack, ROOT.kGray+2
]

def get_histograms_limits(t_bin):
    """
    Get the limits for the histograms
    
    Args:
        t_bin (float)
    """
    bin_size = 2*t_bin
    min_toa = -bin_size/2
    max_toa = 14+bin_size/2
    bin_number = int((max_toa-min_toa)/bin_size)
    return min_toa, max_toa, bin_number

def draw_toa_stacked(df_dict):
    """
    Draw the ToA histograms in the same canvas stacked for the 
    different runs

    Args:
        df_dict (dict): Dictionary with the different dataframes
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
        t_bin.append(df_i.Mean("t_bin").GetValue())
    min_toa, max_toa, bin_number = get_histograms_limits(np.mean(np.array(t_bin)))
    
    for i_color, (i, df_i) in enumerate(df_dict.items()):
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

def draw_toa_normalised(df_dict):
    c = ROOT.TCanvas()
    histograms = []
    
    # Remove statistics values
    ROOT.gStyle.SetOptStat(00000)
    # Create limits histogram 
    # Limits:
    # filter 0 : 7e-3
    # filter 1 : 0.05
    # filter -1 : 0.04
    histograms.append(ROOT.TH2F("limits", "", 1, 0, 14, 1, 1e-3, 0.018))
    histograms[-1].Draw()
    histograms[-1].GetXaxis().SetTitle("ToA/ns")
    histograms[-1].GetYaxis().SetTitle("Counts")
    histograms[-1].SetTitle(f"")
    c.Draw()
    opt = "same"
    legend = ROOT.TLegend(0.2, 0.8, 0.5, 0.9)

    # Loop over df to select binning as the mean
    t_bin = []
    for df_i in df_dict.values():
        t_bin.append(df_i.Mean("t_bin").GetValue())
    min_toa, max_toa, bin_number = get_histograms_limits(np.mean(np.array(t_bin)))

    # Loop over dfs to plot them
    for i_color, (i, df_i) in enumerate(df_dict.items()):
        # Create histogram
        histograms.append(df_i.Histo1D(
                ("ToA", f"", bin_number, min_toa, max_toa), "ToA"
            ).GetValue()
            )
        histograms[-1].SetDirectory(0)
        histograms[-1].SetLineColor(colors[i_color])
        histograms[-1].SetMarkerColor(colors[i_color])
        legend.AddEntry(histograms[-1], f"{i}", "l")
        histograms[-1].DrawNormalized(opt)
        legend.Draw()
    c.Draw()
    input("Press enter to continue...")

def draw_toa_substraction(df_dict):
    c = ROOT.TCanvas()
    histograms = []
    draw_hist = []

    # Loop over df to select binning as the mean
    t_bin = []
    for df_i in df_dict.values():
        t_bin.append(df_i.Mean("t_bin").GetValue())
    t_bin = np.mean(np.array(t_bin))
    min_toa, max_toa, bin_number = get_histograms_limits(t_bin)

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


@click.command()
@click.argument("inputfiles", nargs=-1)
def main(inputfiles):
    """
    Main function to call the plotting function. Draws the ToA histogramas for the different runs
    Args:
        inputfiles (list): List with the input files format expected: */*-Time.*

    """
    df_filters = "col == 5 && row == 6"

    print(f"Filter: {df_filters}")
    df_dict_run = {}
    for inputfile in inputfiles:
        name = inputfile.split("/")[-1].split("-")
        filter = name[0].split("_")[-1]
        if filter == "":
            filter = "-"+name[1]
        date = name[-2]
        hour = name[-1].split(".")[0]
        name = f"{date}-{hour}__{filter}"
        f = ROOT.TFile.Open(inputfile)
        df = ROOT.RDataFrame("Hits", f)
        df_dict_run[name] = ROOT.RDataFrame("Hits", f).Filter(df_filters)

    draw_toa_stacked(df_dict_run)
    draw_toa_normalised(df_dict_run)
    if len(df_dict_run) == 2:
        draw_toa_substraction(df_dict_run)
if __name__ == "__main__":
    main()
