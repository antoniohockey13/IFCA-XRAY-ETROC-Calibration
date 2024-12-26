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
        bin_size = 0.033
        min_tot = 0
        max_tot = 7
        bin_number = int((max_tot-min_tot)/bin_size)
        hist = df.Filter(f"Analogical_HV == {i}").Histo1D(
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
    npeaks = spec.Search(tot_hist, sigma = 1, option="no", threshold=threshold)

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

    tot_ana = histograms[0].GetValue()
    peak_pos = find_peaks(tot_ana)

    # Create canvas
    c_peaks = ROOT.TCanvas()

    # Draw histogram
    tot_ana.Draw("PE")
    tot_ana.GetXaxis().SetTitle("ToT/ns")
    tot_ana.GetYaxis().SetTitle("Counts")

    # Mark the peaks
    marker = ROOT.TMarker()
    marker.SetMarkerStyle(20)
    marker.SetMarkerColor(ROOT.kRed)
    for pos in peak_pos:
        marker.DrawMarker(pos, tot_ana.GetBinContent(tot_ana.FindBin(pos)))
    
    # Draw canvas
    c_peaks.Draw()
    input("Press enter to continue")


if __name__ == '__main__':
    main()