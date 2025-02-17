import ROOT
import click
import numpy as np
import sifca_utils
sifca_utils.plotting.set_sifca_style()

colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen]

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
    # Divide it for each pixel
    c.Divide(2,1)
    histograms = {0: [], 1: []}
    legends = []
    stack = {
        0: ROOT.THStack("stack0", f"Analogical LV = 0"), 
        1: ROOT.THStack("stack1", f"Analogical LV = 1"),
        }

    for i_LV in range(2):
        c.cd(i_LV+1)
        legends.append(ROOT.TLegend(0.7, 0.8, 0.9, 0.9))
        
        # Loop over dfs
        i_color = 0
        t_bin = []
        df_filtered = {}
        for i, df_i in df_dict.items():
            # Filter selected dataframe with the LV
            df_filtered[i] = df_i.Filter(f"Analogical_LV == {i_LV}")
            
            # Compute histogram limits
            t_bin.append(df_filtered[i].Mean("t_bin").GetValue())
        
        min_toa, max_toa, bin_number = get_histograms_limits(np.mean(np.array(t_bin)))

        for i, df_i_filtered in df_filtered.items():
            histograms[i_LV].append(df_i_filtered.Histo1D(
                ("ToA", f"Analogical LV = {i_LV}", bin_number, min_toa, max_toa), "ToA"
            ).GetValue()
            )

            histograms[i_LV][-1].SetDirectory(0)
            legends[-1].AddEntry(histograms[i_LV][-1], f"{i}", "l")
            histograms[i_LV][-1].SetLineColor(colors[i_color])

            # Set fill characteristic
            histograms[i_LV][-1].SetFillColorAlpha(colors[i_color], 1)
            histograms[i_LV][-1].SetFillStyle(3001)

            i_color += 1

        # Sort histograms by the number of entries first the one with more entries
        histograms[i_LV].sort(key=lambda x: x.GetEntries(), reverse=True)
        for i, histo_i in enumerate(histograms[i_LV]):
            stack[i_LV].Add(histo_i)
        
        stack[i_LV].Draw("hist fill")
        stack[i_LV].GetXaxis().SetTitle("ToA/ns")
        stack[i_LV].GetYaxis().SetTitle("Counts")
        stack[i_LV].SetTitle(f"Analogical LV {i_LV}")
        legends[-1].Draw()
    c.Update()

    input("Press enter to continue...")

def draw_toa_normalised(df_dict):
    c = ROOT.TCanvas()
    c.Divide(2,1)
    histograms = {0 : [], 1: []}
    legends = []
    for i_LV in range(2):
        c.cd(i_LV+1)

        # Remove statistics values
        ROOT.gStyle.SetOptStat(00000)
        # Create limits histogram 
        # Limits:
        # filter 0 : 7e-3
        # filter 1 : 0.05
        # filter -1 : 0.04
        histograms[i_LV].append(ROOT.TH2F("limits", "", 1, 0, 14, 1, 1e-3, 7e-3))
        histograms[i_LV][-1].Draw()
        histograms[i_LV][-1].GetXaxis().SetTitle("ToA/ns")
        histograms[i_LV][-1].GetYaxis().SetTitle("Counts")
        histograms[i_LV][-1].SetTitle(f"Analogical LV = {i_LV}")
        c.Draw()
        opt = "same"
        legends.append(ROOT.TLegend(0.2, 0.8, 0.5, 0.9))

        # Count to select color for each voltage
        i_color = 0
        # Loop over dfs to plot them
        for i, df_i in df_dict.items():
            df_icol_filtered = df_i.Filter(f"Analogical_LV == {i_LV}")
            # Compute histogram limits
            t_bin = df_icol_filtered.Mean("t_bin").GetValue()
            min_toa, max_toa, bin_number = get_histograms_limits(t_bin)
            # Create histogram
            histograms[i_LV].append(df_icol_filtered.Histo1D(
                ("ToA", f"Analogical LV {i_LV}", bin_number, min_toa, max_toa), "ToA"
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
    input("Press enter to continue...")

@click.command()
@click.argument("inputfiles", nargs=-1)
def main(inputfiles):
    """
    Main function to call the plotting function. Draws the ToA histogramas for the different
    kV used (prepared for 30 and 35 kV).

    Args:
        inputfiles (list): List with the input files format expected: */*-Time.*

        """
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
        df_dict_run[name] = ROOT.RDataFrame("Hits", f)
    
    draw_toa_stacked(df_dict_run)
    draw_toa_normalised(df_dict_run)
if __name__ == "__main__":
    main()
    