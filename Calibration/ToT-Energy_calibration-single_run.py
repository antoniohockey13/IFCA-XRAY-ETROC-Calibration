import ROOT
import click
import sifca_utils

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ToA_Analysis import utils as u
from ToA_Analysis import plot_functions as pf
sifca_utils.plotting.set_sifca_style()

######################################################
# Main function                                     #
######################################################

@click.command()
@click.option('-n', '--name', required=True, type=str, help="Name of the files")
@click.option('-sb', '--select_bin', required=False, type=int, default = 0, help="Select bin to filter")
def main(inputfile, select_bin):
    # Open the file
    if inputfile.split('.')[-1] != 'root':
        raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")
    name = inputfile.split('/')[-1].split('.')[0]
    # Create dataframe
    df = ROOT.RDataFrame("Hits", inputfile)
    # Filter region
    col_max, row_max = u.get_most_hit_pixel(df)
    filter_region = f"col == {col_max} && row == {row_max}"
    print(filter_region)
    df = df.Filter(filter_region)
        
    # Filter in max_cal
    max_cal = u.get_max_cal(df)
    select_bin = 0
    filter_cal = f"abs(cal-({max_cal}+{select_bin}))<2.5"
    print(filter_cal)
    df = df.Filter(filter)
    # Compute needed variables
    df = u.compute_tbin(df)
    df = u.compute_ToA(df)
    df = u.compute_ToT(df)

    # Plot ToA
    pf.plot_ToA(df, title = name)
    # Plot ToT
    pf.plot_ToT(df, title = name)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
