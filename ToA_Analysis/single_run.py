import ROOT
import click
import sifca_utils
import utils as u
import plot_functions as pf

sifca_utils.plotting.set_sifca_style()

# Set ROOT to batch mode if plots are omitted
omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)

# Map sensor positions
SENSOR_POS = {"6": 1, "7": 3, "8": 4, "9": 2}


######################################################
# Main function                                     #
######################################################

@click.command()
@click.argument('inputfile', nargs=1)
def main(inputfile):
    # Open the file
    if inputfile.split('.')[-1] != 'root':
        raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")

    df = ROOT.RDataFrame("Hits", inputfile)
    # Plot the hit map
    pf.hit_map(df)
    # Define the Analogical_LV column as the left/right side of the ETROC
    df = df.Define("Analogical_LV", "floor(col/8)")
    # filter = "Analogical_LV == 0"
    filter = "col == 5 && row == 6 && cal > 0"
    print(filter)
    df = df.Filter(filter)
    # Plot the Cal
    pf.plot_cal(df)
    max_cal = u.get_max_cal(df)
    print(f"Max cal : {max_cal}")
    # Filter to the max cal
    filter = f"abs(cal-{max_cal})<0.5"
    # filter = f"abs(cal-{max_cal})> 2"
    print(filter)
    df = df.Filter(filter)
    # # Compute ToT
    # df = u.compute_ToT(df)
    # # Plot the ToT
    # pf.ToT(df)
    # Plot the ToA
    toa_histograms = pf.ToA(df)
    
if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
