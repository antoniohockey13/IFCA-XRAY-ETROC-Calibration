import sifca_utils.plotting
import ROOT
import click
import sifca_utils
import os

sifca_utils.plotting.set_sifca_style()

# CONSTANTS 
SAME_CAL = True
# DANGER: CAL VALUE
filter_condition = 0.5
# Define store variables
store_tree_name = "Hits"
store_columns = {"row", "col", "cal", "ToA", "ToT", "t_bin", "Analogical_HV", "toa_code", "tot_code"}

# Set ROOT to batch mode if plots are omitted
omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)

def plot_cal_histograms(df, title = "Cal values before filtering"):
    """
    Plot histograms for CAL values and return the max bin for each sensor column.
    Cal goes from 0 to 1023 in integer values.
    """
    canvas = ROOT.TCanvas("c", title)
    canvas.Divide(2, 1)
    max_cal_bins = {}
    histograms = []
    for i in range(2):
        canvas.cd(i+1)
        ROOT.gPad.SetLogy()
        hist = df.Filter(f"Analogical_HV == {i}").Histo1D(
            ("cal", f"Analogical_HV = {i}", 1024, -0.5, 1023.5), "cal"
            )
        hist.GetXaxis().SetTitle("Cal")
        hist.GetYaxis().SetTitle(f"Counts Analogical HV={i}")
        hist.SetTitle(f"Analogical HV = {i}")
        hist.Draw()
        histograms.append(hist)
        # -1 Added because the bin number starts at 1 and the cal value at 0
        max_cal_bins[i] = hist.GetMaximumBin()-1

    canvas.Update()
    if not omit_plots:
        # Keep the canvas open until user input
        input("Press Enter to continue...")  
    return max_cal_bins


def filter_with_same_cal(df, max_cal, filter_condition):
    """
    Filter the data with the same cal value for all the events

    Parameters
    ----------
    df : ROOT.RDataFrame
        Dataframe to filter
    max_cal : dict
        Dictionary with the maximum cal value for each sensor column
    filter_condition : float
        Maximum difference between the cal value and the maximum cal value for each sensor column
    
    Returns
    -------
    df_filtered : ROOT.RDataFrame
        Filtered dataframe
    """
    # Filter and define new columns
    print(f"\033[91mFILTER CONDITION = {filter_condition}\033[0m")
    for i in max_cal:
        filter_expr = (f"Analogical_HV == {i} && abs(cal-{max_cal[i]+1})<{filter_condition}")

        # Apply filter
        df_filtered_i = (df.Filter(filter_expr, "Cal cut"))
        print(df_filtered_i.Report().Print())

        # Define ToT and ToA in ns
        # t_bin = T3/Cal; T3 = 3.125 ns
        # TOA = 12.5-t_bin* TOA_Code
        # TOT = (2*TOT_Code - floor(TOT_Code/32))*t_bin

        # Define new columns
        df_filtered_i = (df_filtered_i
                        .Define("t_bin", f"3.125/{max_cal[i]}")
                        .Define("ToA", "12.5-t_bin*toa_code")
                        .Define("ToT", "(2*tot_code - floor(tot_code/32))*t_bin")
                        )
        
        # Save dataframe
        df_filtered_i.Snapshot(store_tree_name, f"Bin/df{i}.root", store_columns)

    df_filtered = ROOT.RDataFrame(store_tree_name, [f"Bin/df{i}.root" for i in max_cal])    
    return df_filtered


def filter_with_each_cal(df, max_cal, filter_condition):
    """
    Filter the data with the same cal value for all the events

    Parameters
    ----------
    df : ROOT.RDataFrame
        Dataframe to filter
    max_cal : dict
        Dictionary with the maximum cal value for each sensor column
    filter_condition : float
        Maximum difference between the cal value and the maximum cal value for each sensor column
    
    Returns
    -------
    df_filtered : ROOT.RDataFrame
        Filtered dataframe
    """
    # Filter and define new columns
    print(f"\033[91mFILTER CONDITION = {filter_condition}\033[0m")

    condition = []
    for i in max_cal:
        condition.append(f"Analogical_HV == {i} && abs(cal-{max_cal[i]})<{filter_condition}")
    filter_expr = " || ".join(condition)

    # Apply filter
    df_filtered = (df.Filter(filter_expr, "Cal cut"))
    print(df_filtered.Report().Print())

    # Define ToT and ToA in ns
    # t_bin = T3/Cal; T3 = 3.125 ns
    # TOA = 12.5-t_bin* TOA_Code
    # TOT = (2*TOT_Code - floor(TOT_Code/32))*t_bin
    
    # Define new columns
    df_filtered = df_filtered.Define("t_bin", f"3.125/cal")
    df_filtered = df_filtered.Define("ToA", "12.5-t_bin*toa_code")
    df_filtered = df_filtered.Define("ToT", "(2*tot_code - floor(tot_code/32))*t_bin")
    return df_filtered

@click.command()
@click.argument('inputfiles', nargs=-1)
def main(inputfiles):
    """
    Filter raw data with Cal values
    """
    for file in inputfiles:
        # Separate folder and name of the file
        folder, name = file.rsplit("/", 1)
        if name.split('.')[-1] != 'root':
            raise ValueError(f"Input file must have .root extension and it has .{name.split('.')[-1]}")
        os.makedirs(f"{folder}", exist_ok=True)
        os.makedirs(f"Bin", exist_ok=True)
        # Define store file name
        if SAME_CAL:
            store_file_name = f"{folder}/Filtered_{filter_condition}_right_Same_Cal-{name}"
        else:
            store_file_name = f"{folder}/Filtered_{filter_condition}-{name}"
        # Open file and create RDataFrame
        f = ROOT.TFile(file)
        df = ROOT.RDataFrame("Hits", f)
        
        # Define column to know if analogical or digital voltage supply
        df = df.Define("Analogical_HV", "floor(col/8)")
        # Draw histogram with Cal values and get max cal bin for each sensor column
        max_cal = plot_cal_histograms(df=df, title="Cal values before filtering")
        print(max_cal)

        if SAME_CAL:
            # Filter data with the same cal value for all the events
            df_filtered = filter_with_same_cal(df, max_cal, filter_condition)
        else:
            # Filter the data with different cal values for each event
            df_filtered = filter_with_each_cal(df, max_cal, filter_condition)
        print(df_filtered.Report().Print())
        # Plot cal after filtering
        plot_cal_histograms(df_filtered, title="Cal values after filtering")

        # Save filtered data
        df_filtered.Snapshot(store_tree_name, store_file_name, store_columns)
        print(f"New ROOT file saved in {store_file_name}")
        
if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
