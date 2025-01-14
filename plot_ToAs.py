import ROOT
import click
import sifca_utils

sifca_utils.plotting.set_sifca_style()
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen]

def draw_toa_together(df_dict):
    """
    Draw the ToA histograms in the same canvas normalised for the different bins selected

    Args:
        df_dict (dict): Dictionary with the different dataframes
    """
    # Y-axis limits of the histogras
    limits = {}
    limits[0] = 4e3
    limits[1] = 1.2e4
    # Create canvas
    c = ROOT.TCanvas()
    # Divide it for analogical HV = 0 and = 1
    c.Divide(2,1)
    histograms = {0: [], 1: []}
    legends = []
    # Loop over the analogical HV
    for ipad in range(2):
        c.cd(ipad+1)
        # Remove statistics values from the histogram
        ROOT.gStyle.SetOptStat(000000)
        # Create limits histogram
        histograms[ipad].append(ROOT.TH2F("limits", "", 1, 0, 14, 1, 1e-3, limits[ipad]))
        histograms[ipad][-1].Draw()
        histograms[ipad][-1].GetXaxis().SetTitle("ToA/ns")
        histograms[ipad][-1].GetYaxis().SetTitle("Counts")
        histograms[ipad][-1].SetTitle(f"Analogical HV = {ipad}")
        c.Draw()
        opt = "same"
        legends.append(ROOT.TLegend(0.2, 0.8, 0.5, 0.9))

        # Loop over the selected bins
        for i, df_i in df_dict.items():
            # Filter selected dataframe with te Analogical HV
            df_i_filtered = df_i.Filter(f"Analogical_HV == {ipad}")
            # Get t_bin for bin size and compute limits
            t_bin = df_i_filtered.Mean("t_bin").GetValue()
            print(f"Analogical HV {ipad}, bin selected: {i}, t_bin: {t_bin}")
            bin_size = 2*t_bin 
            min_tot = -bin_size/2
            max_tot = 14+bin_size/2
            bin_number = int((max_tot-min_tot)/bin_size)

            # Create histogram
            histograms[ipad].append(df_i_filtered.Histo1D(
                ("ToA", f"Analogical HV {ipad}", bin_number, min_tot, max_tot), "ToA"
            ))
            histograms[ipad][-1].SetDirectory(0)
            histograms[ipad][-1].SetLineColor(colors[int(i)+1])
            legends[-1].AddEntry(histograms[ipad][-1].GetValue(), f"Bin selected {i}", "l")
            histograms[ipad][-1].Draw(opt)
        legends[-1].Draw()
    c.Update()
    input("Press enter to continue...")

def draw_toa_stacked(df_dict, df_15):
    """
    Draw the ToA histograms in the same canvas stacked for the different bins selected

    Args:
        df_dict (dict): Dictionary with the different dataframes
        df_15 (ROOT.RDataFrame): Dataframe with the data for the bin selected 1.5
    """
    
    # Create Canvas
    c = ROOT.TCanvas()
    # Divide it for analogical HV = 0 and = 1
    c.Divide(2,1)
    histograms = {0: [], 1: []}
    legends = []
    stack = {0: ROOT.THStack("stack0", f"Analogical HV 0"), 1: ROOT.THStack("stack1", f"Analogical HV 1")}

    for ipad in range(2):
        c.cd(ipad+1)
        legends.append(ROOT.TLegend(0.2, 0.8, 0.5, 0.9))
        # Filter df_15
        df_15_filtered = df_15.Filter(f"Analogical_HV == {ipad}")
        # Get t_bin for bin size and compute limits
        t_bin = df_15_filtered.Mean("t_bin").GetValue()
        print(f"Analogical HV {ipad}, bins selected -1, 0 and 1, t_bin: {t_bin}")        
        bin_size = 2*t_bin
        min_tot = -bin_size/2
        max_tot = 14+bin_size/2
        bin_number = int((max_tot-min_tot)/bin_size)
        # Loop over the selected bins
        for i, df_i in df_dict.items():
            # Filter selected dataframe with te Analogical HV
            df_i_filtered = df_i.Filter(f"Analogical_HV == {ipad}")
            print(f"Analogical HV {ipad}, bin selected: {i}")
            histograms[ipad].append(df_i_filtered.Histo1D(
                ("ToA", f"Analogical HV {ipad}", bin_number, min_tot, max_tot), "ToA"
            ).GetValue()
            )

            histograms[ipad][-1].SetDirectory(0)
            histograms[ipad][-1].SetLineColor(colors[int(i)+1])
            # Set fill characteristic
            histograms[ipad][-1].SetFillColorAlpha(colors[int(i)+1], 1)
            histograms[ipad][-1].SetFillStyle(3001)

        # Sort histograms by the number of entries first the one with more entries
        histograms[ipad].sort(key=lambda x: x.GetEntries(), reverse=True)
        for histo_i in histograms[ipad]:
            stack[ipad].Add(histo_i)
            legends[-1].AddEntry(histo_i, f"Bin selected {i}", "l")
        
        stack[ipad].Draw("hist fill")
        stack[ipad].GetXaxis().SetTitle("ToA/ns")
        stack[ipad].GetYaxis().SetTitle("Counts")
        stack[ipad].SetTitle(f"Analogical HV = {ipad}")
        legends[-1].Draw()
    c.Update()
    input("Press enter to continue...")
    
@click.command()
@click.argument('inputfiles', nargs=-1)
def main(inputfiles):
    """
    Main function to draw the ToA histograms normalised for the different bins selected
    
    Args:
        inputfiles (list): List with the input files. 
        The name must have the format: Filtered_0.5_X-*.root where X is the selected bin (-1, 0 or 1)
        And one file with the format Filtered_1.5_0-*.root needed to draw the stacked histogram
    """

    # Store in a dictionary the different dataframes
    # Hardcoded for my files names
    df_dict = {}
    for inputfile in inputfiles:
        name = inputfile.split('/')[-1].split('_')[1:3]
        if name[0] == '0.5':
            # remove last 4 characters from the name
            name = name[1][:-5]
            f = ROOT.TFile.Open(inputfile)
            df_dict[name] = ROOT.RDataFrame("Hits", f)
        elif name[0] == '1.5':
            f = ROOT.TFile.Open(inputfile)
            df_15 = ROOT.RDataFrame("Hits", f)
    
    # draw_toa_together(df_dict)

    draw_toa_stacked(df_dict, df_15)

if __name__ == "__main__":
    main()
