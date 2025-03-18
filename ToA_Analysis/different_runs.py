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
@click.argument('inputfiles', nargs=-1)
def main(inputfiles):
    df_dict ={}
    for inputfile in inputfiles:
        # Open the file
        if inputfile.split('.')[-1] != 'root':
            raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")
        name = inputfile.split('/')[-1].split('.')[0]
        df_dict[name] = ROOT.RDataFrame("Hits", inputfile)

    max_cal_dict = {}
    bin_selected = 0
    col_max, row_max = u.get_most_hit_pixel(df_dict)
    for name, df in df_dict.items():
        # Define the Analogical_LV column as the left/right side of the ETROC
        # df = df.Define("Analogical_LV", "floor(col/8)")
        # Filter in Analogical LV
        col_max, row_max = u.get_most_hit_pixel(df_dict)
        filter_region = f"col == {col_max} && row == {row_max}"
        print(filter_region)
        df_i = df.Filter(filter_region)
        # # Filter in cal
        # Remove cal = 0 to compute t_bin (T3/cal = NaN)
        # df = df.Filter("cal>0")
        # max_cal_dict[name] = u.get_max_cal(df)
        # df = df.Filter(f"abs(cal-({max_cal_dict[name]}+{bin_selected}))<0.5")
        # Compute needed variables
        # df = u.compute_tbin(df)
        # df = u.compute_ToA(df)
        # Save the dataframe
        df_dict[name] = df_i
    pf.draw_Cal_together_same_canvas(df_dict)
    # pf.draw_Cal_together_different_canvas(df_dict)
    # for name, df in df_dict.items():
    #     print(name)
    #     pf.hit_map(df)
    # pf.draw_ToA_stacked(df_dict)
    # pf.draw_ToA_normalised(df_dict, y_limit=5e-3)
    # pf.draw_ToA_substraction(df_dict)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
