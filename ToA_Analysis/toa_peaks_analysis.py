import ROOT
import click
import sifca_utils
import utils as u
import plot_functions as pf
import numpy as np

sifca_utils.plotting.set_sifca_style()

# Set ROOT to batch mode if plots are omitted
omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)


######################################################
# Main function                                     #
######################################################

@click.command()
@click.argument('inputfiles', nargs=-1)
def main(inputfiles):
    first_minimum = []
    first_maximum = []
    omega = []
    omega_error = []
    for inputfile in inputfiles:
        # Open the file
        if inputfile.split('.')[-1] != 'root':
            raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")

        df = ROOT.RDataFrame("Hits", inputfile)
        title = inputfile.split('/')[-1].split('.')[0]
        # Define the Analogical_LV column as the left/right side of the ETROC
        df = df.Define("Analogical_LV", "floor(col/8)")
        filter = "col == 5 && row == 6 && cal > 0"
        print(filter)
        df = df.Filter(filter)
        max_cal = u.get_max_cal(df)
        print(f"Max cal : {max_cal}")
        # # Filter to the max cal
        select_bin = 0
        filter = f"abs(cal-({max_cal}+{select_bin}))<2.5"
        print(filter)
        df = df.Filter(filter)
        title = title + f"__{select_bin}"
        # pf.plot_cal(df)
        # toa_code = pf.ToA_CODE(df)

        x_min, x_max, om, om_error =pf.fit_ToA_sin(df = df, title=title)
        pf.fit_ToACODE_sin(df = df, title=title)
        if om != None:
            first_minimum.append(x_min)
            first_maximum.append(x_max)
            omega.append(om)
            omega_error.append(om_error)

        # pf.fast_fourier_transform_ToA(df=df, title=title)

    # print(f"First minimum mean = {np.array(first_minimum).mean()} +/- {np.array(first_minimum).std()}")
    # print(f"First maximum mean = {np.array(first_maximum).mean()} +/- {np.array(first_maximum).std()}")
    omega = np.array(omega)
    period = 2*np.pi/omega
    
    print(f"Period mean = {period.mean()} +/- {period.std()}")


    
if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
