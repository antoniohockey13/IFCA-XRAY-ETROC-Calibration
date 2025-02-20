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
    # filter_region = "Analogical_LV == 0"
    filter_region = "col == 5 && row == 6"
    print(filter_region)
    for name, df in df_dict.items():
        # Define the Analogical_LV column as the left/right side of the ETROC
        df = df.Define("Analogical_LV", "floor(col/8)")
        # Filter in Analogical LV
        df = df.Filter(filter_region)
        # Filter in cal
        max_cal_dict[name] = u.get_max_cal(df)
        df = df.Filter(f"abs(cal-{max_cal_dict[name]})<0.5")
        # Save the dataframe
        df_dict[name] = df
    
    pf.draw_ToA_stacked(df_dict)
    
if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
