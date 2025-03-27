import ROOT
import click
import sifca_utils
import numpy as np

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Utils import utils as u
from Utils import plot_functions as pf
sifca_utils.plotting.set_sifca_style()

######################################################
# Main function                                      #
######################################################

omit_plots = True
ROOT.gROOT.SetBatch(omit_plots)
@click.command()
@click.option('-sb', '--select_bin', required=False, type=int, default = 0, help="Select bin to filter")
@click.argument('inputfiles', nargs = -1)
def main(inputfiles, select_bin):
    max_tot_pixel = {}
    for inputfile in inputfiles:
        # Open the file
        if inputfile.split('.')[-1] != 'root':
            raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")
        name = inputfile.split('/')[-1].split('.')[0]
        # Create dataframe
        df = ROOT.RDataFrame("Hits", inputfile)
        # Filter region
        col_max, row_max = u.get_most_hit_pixel(df)
        
        filter_region = f"col == {col_max} && row == {row_max}"
        max_tot_pixel.setdefault(f"C{col_max}R{row_max}", [])

        print(filter_region)
        df = df.Filter(filter_region)
            
        # Filter in max_cal
        max_cal = u.get_max_cal(df)
        filter_cal = f"abs(cal-({max_cal}+{select_bin}))<2.5"
        print(filter_cal)
        df = df.Filter(filter_cal)
        # Compute needed variables
        df = u.compute_tbin(df)
        df = u.compute_ToA(df)
        df = u.compute_ToT(df)

        # Plot ToA
        # pf.ToA(df, title = name)
        # Plot ToT
        pf.ToT(df, title = name, omit_plots=omit_plots)
        # Print max of the ToT
        tot_max_i = df.Max('ToT').GetValue()
        max_tot_pixel[f"C{col_max}R{row_max}"].append(tot_max_i)
        print(f"Max ToT: {tot_max_i}")
    
    for pos in max_tot_pixel.keys():
        print(f"Max tot for {pos} = {np.mean(np.array(max_tot_pixel[pos]))} +- {np.std(np.array(max_tot_pixel[pos]))}")
    
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
