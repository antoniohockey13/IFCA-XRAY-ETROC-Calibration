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
    window = []
    for inputfile in inputfiles:
        # Open the file
        if inputfile.split('.')[-1] != 'root':
            raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")

        df = ROOT.RDataFrame("Hits", inputfile)
        title = inputfile.split('/')[-1].split('.')[0]
        if title[0:7] == "2025_02":
            filter = "col == 5 && row == 6 && cal > 0"
        elif title[0:7] == "2025_03":
            filter = "col == 7 && row == 6 && cal > 0"
        else:
            raise ValueError(f"Unknown configuration {title[0:7]}")
        
        # filter = "col == 12 && row == 6 && cal > 0"
        print(filter)
        df = df.Filter(filter)
        max_cal = u.get_max_cal(df)
        print(f"Max cal : {max_cal}")
        # # Filter to the max cal
        select_bin = -1 
        filter = f"abs(cal-({max_cal}+{select_bin}))<0.5"
        print(filter)
        df = df.Filter(filter)
        title = title + f"__{select_bin}"
        # pf.plot_cal(df)
        max_toa_code = df.Max("toa_code").GetValue()
        print(f"Max toa code : {max_toa_code}")
        window_i = max_toa_code/max_cal*3.125
        print(f"Window : {window_i}")
        window.append(window_i)


        x_min, x_max, om, om_error =pf.fit_ToA_sin(df = df, title=title)
        # pf.fit_ToACODE_sin(df = df, title=title)
        if om != None:
            first_minimum.append(x_min)
            first_maximum.append(x_max)
            omega.append(om)
            omega_error.append(om_error)

        # pf.fast_fourier_transform_ToA(df=df, title=title)

    print(f"First minimum mean = {np.array(first_minimum).mean()} +/- {np.array(first_minimum).std()}")
    print(f"First maximum mean = {np.array(first_maximum).mean()} +/- {np.array(first_maximum).std()}")
    omega = np.array(omega)
    period = 2*np.pi/omega
    print(f"Period mean = {period.mean()} +/- {period.std()}")
    print(f"Window mean = {np.array(window).mean()} +/- {np.array(window).std()}")

    
if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
