import ROOT
import sifca_utils
import click

sifca_utils.plotting.set_sifca_style()

colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen]
SENSOR_POS = {"6": 1, "7": 3, "8": 4, "9": 2}

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

def draw_toa(df_dict):
    c = ROOT.TCanvas()
    c.Divide(2,2)
    histograms = {6 : [], 7: [], 8: [], 9: []}
    legends = []
    for icol in range(6, 10):
        c.cd(SENSOR_POS[str(icol)])
        # Remove statistics values
        ROOT.gStyle.SetOptStat(00000)
        # Create limits histogram 
        # Limits:
        # filter 0 : 7e-3
        # filter 1 : 0.05
        # filter -1 : 0.04
        histograms[icol].append(ROOT.TH2F("limits", "", 1, 0, 14, 1, 1e-3, 0.04))
        histograms[icol][-1].Draw()
        histograms[icol][-1].GetXaxis().SetTitle("ToA/ns")
        histograms[icol][-1].GetYaxis().SetTitle("Counts")
        histograms[icol][-1].SetTitle(f"Column = {icol}")
        c.Draw()
        opt = "same"
        legends.append(ROOT.TLegend(0.2, 0.8, 0.5, 0.9))

        # Count to select color for each voltage
        i_color = 0
        # Loop over dfs to plot them
        for i, df_i in df_dict.items():
            df_icol_filtered = df_i.Filter(f"col == {icol}")
            # Compute histogram limits
            t_bin = df_icol_filtered.Mean("t_bin").GetValue()
            min_toa, max_toa, bin_number = get_histograms_limits(t_bin)
            # Create histogram
            histograms[icol].append(df_icol_filtered.Histo1D(
                ("ToA", f"Column {icol}", bin_number, min_toa, max_toa), "ToA"
            ).GetValue()
            )
            histograms[icol][-1].SetDirectory(0)
            histograms[icol][-1].SetLineColor(colors[i_color])
            legends[-1].AddEntry(histograms[icol][-1], f"Voltage {i}", "l")
            histograms[icol][-1].DrawNormalized(opt)
            i_color += 1
        legends[-1].Draw()
    c.Update()
    input("Press enter to continue...")

def draw_toa_stacked_per_pixel(df_dict):
    """
    Draw the ToA histograms in the same canvas stacked for the different kV used

    Args:
        df_dict (dict): Dictionary with the different dataframes
    """
    # Create Canvas
    c = ROOT.TCanvas()
    # Divide it for each pixel
    c.Divide(2,2)
    histograms = {6: [], 7: [], 8: [], 9: []}
    legends = []
    stack = {
        6: ROOT.THStack("stack0", f"Column 6"), 
        7: ROOT.THStack("stack1", f"Column 7"), 
        8: ROOT.THStack("stack2", f"Column 8"),
        9: ROOT.THStack("stack3", f"Column 9")
        }

    for icol in range(6, 10):
        c.cd(SENSOR_POS[str(icol)])
        legends.append(ROOT.TLegend(0.7, 0.8, 0.9, 0.9))
        
                
        # Loop over dfs
        i_color = 0
        for i, df_i in df_dict.items():
            # Filter selected dataframe with te Column
            df_i_filtered = df_i.Filter(f"col == {icol}")
            # Compute histogram limits
            t_bin = df_i_filtered.Mean("t_bin").GetValue()
            min_toa, max_toa, bin_number = get_histograms_limits(t_bin)

            histograms[icol].append(df_i_filtered.Histo1D(
                ("ToA", f"Column {icol}", bin_number, min_toa, max_toa), "ToA"
            ).GetValue()
            )

            histograms[icol][-1].SetDirectory(0)
            legends[-1].AddEntry(histograms[icol][-1], f"Voltage {i}", "l")
            histograms[icol][-1].SetLineColor(colors[i_color])
            # Set fill characteristic
            histograms[icol][-1].SetFillColorAlpha(colors[i_color], 1)
            histograms[icol][-1].SetFillStyle(3001)

            i_color += 1

        # Sort histograms by the number of entries first the one with more entries
        histograms[icol].sort(key=lambda x: x.GetEntries(), reverse=True)
        for i, histo_i in enumerate(histograms[icol]):
            stack[icol].Add(histo_i)
        
        stack[icol].Draw("hist fill")
        stack[icol].GetXaxis().SetTitle("ToA/ns")
        stack[icol].GetYaxis().SetTitle("Counts")
        stack[icol].SetTitle(f"Column {icol}")
        legends[-1].Draw()
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
        If Time = 08_26_42, the kV is 30, if Time = 08_37_11, the kV is 35
    """
    df_dict_kv = {}
    i = 1
    for inputfile in inputfiles:
        name = inputfile.split("/")[-1].split("-")[-1].split(".")[0]
        if name == "08_26_42":
            f = ROOT.TFile.Open(inputfile)
            df_dict_kv[30] = ROOT.RDataFrame("Hits", f)
        elif name == "08_37_11":
            f = ROOT.TFile.Open(inputfile)
            df_dict_kv[35] = ROOT.RDataFrame("Hits", f)
        else:
            print(f"File {inputfile} not recognized, associated with kV = -{i}")
            f = ROOT.TFile.Open(inputfile)
            df_dict_kv[str(-i)] = ROOT.RDataFrame("Hits", f)
            i += 1
    # draw_toa_stacked_per_pixel(df_dict_kv)
    draw_toa(df_dict_kv)

if __name__ == "__main__":
    main()
    
