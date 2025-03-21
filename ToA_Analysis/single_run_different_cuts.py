import ROOT
import click
import sifca_utils
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Utils import utils as u
from Utils import plot_functions as pf

sifca_utils.plotting.set_sifca_style()

######################################################
# Main function                                     #
######################################################

@click.command()
@click.argument('inputfile', nargs=1)
def main(inputfile):

    # Open the file
    if inputfile.split('.')[-1] != 'root':
        raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")
    name = inputfile.split('/')[-1].split('.')[0]
    # Create dataframe
    df = ROOT.RDataFrame("Hits", inputfile)
    # Filter region
    # filter_region = "col == 5 && row == 6"
    # filter_region = "col == 7 && row == 6"
    # filter_region = "col == 12 && row == 6"
    # filter_region = "Analogical_LV == 1"
    col_max, row_max = u.get_most_hit_pixel(df)
    filter_region = f"col == {col_max} && row == {row_max}"
    print(filter_region)
    # Define the Analogical_LV column as the left/right side of the ETROC
    df = df.Define("Analogical_LV", "floor(col/8)")
    # pf.hit_map(df)
    # Filter in Analogical LV
    df = df.Filter(filter_region)
    # pf.hit_map(df)
    
    # Filter in different max_cal
    max_cal = u.get_max_cal(df)
    filter_cal = [-1, 1]
    print(f"Cal filter to: {filter_cal}")
    df_dict = {}
    for i_filter in filter_cal:
        if i_filter == "-1 and +1":
            filter = f"cal == {max_cal}+1 || cal == {max_cal}-1"
        else:
            filter = f"abs(cal-({max_cal}+{i_filter}))<0.5"
        print(filter)
        df_i = df.Filter(filter)
        # Compute needed variables
        df_i = u.compute_tbin(df_i)
        df_i = u.compute_ToA(df_i)
        # Save the dataframe
        df_dict[name+f"__{i_filter}"] = df_i

    # # Plot cal to make sure filter working properly
    # histograms = []
    # for df_i in df_dict.values():
    #     pf.plot_cal(df_i)
    pf.draw_Cal_together_different_canvas(df_dict)
    pf.draw_ToA_stacked(df_dict)
    pf.draw_ToA_normalised(df_dict, y_limit=0.015)
    pf.draw_ToA_substraction(df_dict)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
