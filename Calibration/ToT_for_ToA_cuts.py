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

omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)
@click.command()
@click.option('-sb', '--select_bin', required=False, type=int, default = 0, help="Select bin to filter")
@click.argument('inputfiles', nargs = -1)
def main(inputfiles, select_bin):
    # Open the file
    for inputfile in inputfiles:
        print(inputfile)
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
        filter_cal = f"abs(cal-({max_cal}+{select_bin}))<2.5"
        print(filter_cal)
        df = df.Filter(filter_cal)

        # Compute needed variables
        df = u.compute_tbin(df)
        df = u.compute_ToA(df)
        df = u.compute_ToT(df)

        df_dict = {}
        cut_number = 5
        prev_cut = 0
        for i in range(cut_number):
            cut = 12.5/cut_number * (i+1)
            df_i = df.Filter(f"ToA>={prev_cut} && ToA<={cut}")
            prev_cut = cut
            df_dict[f"ToA_{cut:.2f}"] = df_i
        
        for key_i, df_i in df_dict.items():
            # pf.ToA(df_i, title=key_i)
            # pf.ToT(df_i, title=key_i, omit_plots=omit_plots)
            # Print max of the ToT
            print(f"ToT max: {df_i.Max('ToT').GetValue()}, ToT mean: {df_i.Mean('ToT').GetValue()}, ToT std dev: {df_i.StdDev('ToT').GetValue()}")
        
        pf.draw_ToT_together_same_canvas(df_dict)
if __name__ == "__main__":
    main()