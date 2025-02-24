import ROOT
import click
import sifca_utils
import utils as u
import plot_functions as pf

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
    filter_region = "col == 5 && row == 6"
    print(filter_region)
    # Define the Analogical_LV column as the left/right side of the ETROC
    df.Define("Analogical_LV", "floor(col/8)")
    # Filter in Analogical LV
    df.Filter(filter_region)
    
    # Filter in different max_cal
    max_cal = u.get_max_cal(df)
    filter_cal = [-1, 0, 1]
    print(f"Cal filter to: {filter_cal}")
    df_dict = {}
    for i_filter in filter_cal:
        print(f"abs(cal-({max_cal}+{i_filter}))<0.5")
        df_i = df.Filter(f"abs(cal-({max_cal}+{i_filter}))<0.5")
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
    pf.draw_ToA_normalised(df_dict, y_limit=5e-3)
    pf.draw_ToA_substraction(df_dict)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
