import ROOT
import click
import numpy as np
import sifca_utils

sifca_utils.plotting.set_sifca_style()

# Set ROOT to batch mode if plots are omitted
omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)

colors = [
    ROOT.kRed+1, ROOT.kRed-7, ROOT.kBlue+1, ROOT.kBlue-7, ROOT.kGreen+2, ROOT.kGreen-5,
    ROOT.kMagenta+1, ROOT.kMagenta-5, ROOT.kOrange+2, ROOT.kOrange-3, ROOT.kCyan+1, ROOT.kCyan-6,
    ROOT.kYellow+2, ROOT.kYellow-7, ROOT.kPink+1, ROOT.kViolet+1, ROOT.kAzure+2, ROOT.kSpring+5, 
    ROOT.kTeal+3, ROOT.kBlack, ROOT.kGray+2
]

def plot_cal_normalised(df_dict):
    """
    Plot calibration normalised for different runs
    Args:
    df_dict: dict with the dataframes of the different runs
    
    """
    c = ROOT.TCanvas()
    c.Divide(2,1)
    histograms = {0 : [], 1: []}
    legends = []
    limits = [0.8, 0.4]
    for i_LV in range(2):
        c.cd(i_LV+1) 
        ROOT.gPad.SetLogy()

        # Remove statistics values
        ROOT.gStyle.SetOptStat(00000)
        # Create limits histogram 
        histograms[i_LV].append(ROOT.TH2F("limits", "", 1, 0, 1024, 1, 1e-6, limits[i_LV]))
        histograms[i_LV][-1].Draw()
        histograms[i_LV][-1].GetXaxis().SetTitle("Cal")
        histograms[i_LV][-1].GetYaxis().SetTitle("Counts")
        histograms[i_LV][-1].SetTitle(f"Analogical LV = {i_LV}")
        c.Draw()
        opt = "same"
        legends.append(ROOT.TLegend(0.6, 0.8, 0.9, 0.9))

        # Count to select color for each voltage
        i_color = 0
        # Loop over dfs to plot them
        for i, df_i in df_dict.items():
            df_icol_filtered = df_i.Filter(f"Analogical_LV == {i_LV}")
            # Create histogram
            histograms[i_LV].append(df_icol_filtered.Histo1D(
                ("Cal", f"Analogical LV {i_LV}", 1024, -0.5, 1023.5), "cal"
            ).GetValue()
            )
            histograms[i_LV][-1].SetDirectory(0)
            histograms[i_LV][-1].SetLineColor(colors[i_color])
            histograms[i_LV][-1].SetMarkerColor(colors[i_color])
            legends[-1].AddEntry(histograms[i_LV][-1], f"{i}", "l")
            histograms[i_LV][-1].DrawNormalized(opt+"P")
            i_color += 1
        legends[-1].Draw("")
    c.Update()
    c.SetLogy()
    input("Press enter to continue...")

def plot_cal_different_graphs(df_dict):
    """
    Plot calibration for different runs in different graphs
    Args:
    df_dict: dict with the dataframes of the different runs
    """
    n_pads = len(df_dict)
    c = ROOT.TCanvas()
    if n_pads == 2:
        c.Divide(2,1)
    else:
        c.Divide(int(np.ceil(n_pads/2)),2)
    hist = []
    for i, (name, df) in enumerate(df_dict.items()):
        c.cd(i+1)
        ROOT.gPad.SetLogy()
        hist.append(df.Filter("Analogical_LV == 1").Histo1D(("cal", f"{name}", 1024, -0.5, 1023.5), "cal"))
        hist[-1].SetDirectory(0)
        hist[-1].GetXaxis().SetTitle("Cal")
        hist[-1].GetYaxis().SetTitle("Counts")
        hist[-1].SetTitle(f"{name}")
        hist[-1].Draw()
        hist[-1].SetLineColor(colors[i])
        # -1 Added because the bin number starts at 1 and the cal value at 0
        max_cal_bins = hist[-1].GetMaximumBin()-1
        # Text in the plot
        text = ROOT.TLatex()
        text.SetNDC()
        text.SetTextSize(0.04)
        text.DrawLatex(0.6, 0.7, f"Max cal = {max_cal_bins}")
    c.Update()
    c.Draw()
    input("Press enter to continue...")

@click.command()
@click.argument('inputfiles', nargs = -1)
def main(inputfiles):
    df_dict_run = {}
    for inputfile in inputfiles:
        name = inputfile.split("/")[-1].split("-")
        date = name[-2]
        hour = name[-1].split(".")[0]
        name = f"{date}-{hour}"
        f = ROOT.TFile.Open(inputfile)

        df_dict_run[name] = ROOT.RDataFrame("Hits", f)
        # Define new column 
        df_dict_run[name] = df_dict_run[name].Define("Analogical_LV", "floor(col/8)")

    plot_cal_different_graphs(df_dict_run)
    plot_cal_normalised(df_dict_run)


if __name__ == '__main__':
    main()  

