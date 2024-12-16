import sifca_utils.plotting
import ROOT
import click
import sifca_utils

sifca_utils.plotting.set_sifca_style()


# Set ROOT to batch mode if plots are omitted
omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)

# Map sensor positions
SENSOR_POS = {"6": 1, "7": 3, "8": 4, "9": 2}


def plot_cal_histograms(df, title = "Cal values before filtering"):
    """
    Plot histograms for CAL values and return the max bin for each sensor column.
    Cal goes from 0 to 1023 in integer values.
    """
    canvas = ROOT.TCanvas("c", title)
    canvas.Divide(2, 2)

    max_cal_bins = {}
    histograms = []

    for col, pos in SENSOR_POS.items():
        canvas.cd(pos)
        hist = df.Filter(f"row==15 && col=={col}").Histo1D(
            ("cal", f"Column {col}", 1024, 0., 1023), "cal"
        )
        hist.GetXaxis().SetTitle("Cal")
        hist.GetYaxis().SetTitle(f"Counts col={col}")
        hist.SetTitle(f"Column {col}")
        hist.Draw()

        histograms.append(hist)
        max_cal_bins[col] = hist.GetMaximumBin()

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")  
    return max_cal_bins

@click.command()
@click.argument('inputfiles', nargs=-1)
def main(inputfiles):
    """
    Filter raw data with Cal values
    """
    for file in inputfiles:
        # Separate folder and name of the file
        folder, name = file.rsplit("/", 1)
        print(folder, name)

        # Open file and create RDataFrame
        f = ROOT.TFile(file)
        df = ROOT.RDataFrame("Hits", f)

        # Draw histogram with Cal values and get max cal bin for each sensor column
        max_cal = plot_cal_histograms(df=df, title="Cal values before filtering")

        # Filter and define new columns
        # Build filter expression
        filter_expr = " || ".join(
            [f"row==15 && col=={col} && abs(cal-{max_cal[col]})<2.5" for col in max_cal])
        # Apply filter
        df_filtered = df.Filter(filter_expr, "Cal cut")
        print(df.Report().Print())

        # Plot cal after filetering
        plot_cal_histograms(df_filtered, title="Cal values after filtering")
        # Define ToT and ToA in ns
        # t_bin = T3/Cal; T3 = 3.125 ns
        # TOA = t_bin* TOA_Code
        # TOT = (2*TOT_Code - floor(TOT_Code/32))*t_bin

        # Define new columns
        df_filtered = df_filtered.Define("t_bin", "3.125/cal")
        # If same cal value consider for all the events other code needed
        df_filtered = df_filtered.Define("ToA", "t_bin*toa_code")
        df_filtered = df_filtered.Define("ToT", "(2*tot_code - floor(tot_code/32))*t_bin")

        # Save filtered data
        tree_name = "Hits"
        file_name = f"{folder}/Filtered_{name}"
        columns = {"row", "col", "cal", "ToA", "ToT", "t_bin"}
        df_filtered.Snapshot(tree_name, file_name, columns)
        
if __name__ == '__main__':
    main()