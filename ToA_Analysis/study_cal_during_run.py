import ROOT
import click
import sifca_utils
import utils as u
import plot_functions as pf
import numpy as np

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
        df = df.Define("Analogical_LV", "floor(col/8)")
        filter = "Analogical_LV == 1"
        print(filter)
        df = df.Filter(filter)
        # pf.event_number(df)
        pf.cal_vs_event_number(df, title)

    
if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
