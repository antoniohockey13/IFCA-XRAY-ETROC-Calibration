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
    """
    Studies the evolution of the Cal during the different runs
    """
    for inputfile in inputfiles:
        # Open the file
        if inputfile.split('.')[-1] != 'root':
            raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")

        df = ROOT.RDataFrame("Hits", inputfile)
        title = inputfile.split('/')[-1].split('.')[0]
        # Define the Analogical_LV column as the left/right side of the ETROC
        # df = df.Define("Analogical_LV", "floor(col/8)")
        # filter = "Analogical_LV == 0"
        # filter = "col==5 && row==6"
        col_max, row_max = u.get_most_hit_pixel(df)
        filter = f"col == {col_max} && row == {row_max}"
        print(filter)
        df = df.Filter(filter)
        max_cal = u.get_max_cal(df)
        print(f"Max Cal: {max_cal}")
        select_bin = 0
        filter = f"abs(cal - ({max_cal}+{select_bin}))< 0.5"
        print(filter)
        df = df.Filter(filter)
        # pf.event_number(df)
        df = u.compute_tbin(df)
        df = u.compute_ToA(df)
        pf.ToA_vs_event_number(df, title)

    
if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
