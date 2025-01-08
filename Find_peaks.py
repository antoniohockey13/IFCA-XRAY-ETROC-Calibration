import sifca_utils.plotting
import ROOT
import sifca_utils
import click

sifca_utils.plotting.set_sifca_style()

def ToT(df):
    """
    Plot the ToT of the ETROC in ns
    
    Args:
        df (ROOT.RDataFrame): RDataFrame with the hits
    
    Returns:
        list: List with the histograms
    """

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
        print(f"Size of the bins: {bin_size}")
        hist = df_i.Histo1D(
            ("ToT", f"Analogical HV {i}", bin_number, min_tot, max_tot), "ToT"
        )
        histograms.append(hist)
    return histograms

def find_peaks(tot_hist,):
    """
    Find the peaks of a histogram using TSpectrum

    Args:
        tot_hist (ROOT.TH1): Histogram with the ToT data
        threshold (float): Threshold for the peak finding algorithm

    Returns:
        list: List with the peak positions
    """
    # Use TSpectrum to find the peaks
    spec = ROOT.TSpectrum()
    threshold = 0.19
    npeaks = spec.Search(tot_hist, sigma = 1, option="goff", threshold=threshold)

    # Peak positions
    peak_pos = [spec.GetPositionX()[i] for i in range(npeaks)]
    print(f"Found {npeaks} peaks at {peak_pos}")
    return peak_pos


@click.command()
@click.argument('inputfile', nargs=1)
def main(inputfile):
    # Open the file
    if inputfile.split('.')[-1] != 'root':
        raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")
    
    f = ROOT.TFile.Open(inputfile)
    df = ROOT.RDataFrame("Hits", f)
    histograms = ToT(df)
    
    # Create canvas
    c_peaks = ROOT.TCanvas()
    c_peaks.Divide(2, 1)
    for i in range(2):
        # Select Canvas
        c_peaks.cd(i+1)

        tot_i = histograms[i].GetValue()
        tot_i.Draw("PE")
        histograms[i].GetXaxis().SetTitle("ToT/ns")
        histograms[i].GetYaxis().SetTitle("Counts")
        histograms[i].SetTitle(f"Analogical HV = {i}")

        # Find the peaks
        peak_pos = find_peaks(tot_i)
        # # Mark the peaks
        marker = ROOT.TMarker()
        marker.SetMarkerStyle(113)
        marker.SetMarkerColor(ROOT.kRed)
        marker.SetMarkerSize(1)
        for pos in peak_pos:
            marker.DrawMarker(pos, int(tot_i.GetBinContent(tot_i.FindBin(pos))))
        
    # Draw canvas
    c_peaks.Draw()
    input("Press enter to continue")


if __name__ == '__main__':
    main()
