import ROOT
import click
import sifca_utils
import utils as u
import plot_functions as pf

sifca_utils.plotting.set_sifca_style()

# Set ROOT to batch mode if plots are omitted
omit_plots = False
ROOT.gROOT.SetBatch(omit_plots)

# Map sensor positions
SENSOR_POS = {"6": 1, "7": 3, "8": 4, "9": 2}


######################################################
# Main function                                     #
######################################################

@click.command()
@click.argument('inputfile', nargs=1)
def main(inputfile):
    # Open the file
    if inputfile.split('.')[-1] != 'root':
        raise ValueError(f"Input file must have .root extension and it has .{inputfile.split('.')[-1]}")

    df = ROOT.RDataFrame("Hits", inputfile)
    title = inputfile.split('/')[-1].split('.')[0]
    # Plot the hit map
    # pf.hit_map(df)

    # Define the Analogical_LV column as the left/right side of the ETROC
    df = df.Define("Analogical_LV", "floor(col/8)")
    # filter = "Analogical_LV == 0"
    filter = "col == 12 && row == 6 && cal > 0"
    print(filter)
    df = df.Filter(filter)
    # pf.hit_map(df)

    # # Plot the Cal
    # pf.plot_cal(df)

    # # Get relation between number hits cal = -1,0,1
    # rel01, rel0m1, rel01m1 = u.get_Cal_relation(df)
    # print(f"Relation 0/1: {rel01}")
    # print(f"Relation 0/(-1): {rel0m1}")
    # print(f"Relation 0/(1+(-1)): {rel01m1}")

    # # Get the mean cal
    # mean_cal, sigma = u.get_mean_cal(df)
    # print(f"Mean cal : {mean_cal}+-{sigma}")
    
    # # Get the max cal
    max_cal = u.get_max_cal(df)
    print(f"Max cal : {max_cal}")

    # Filter to the max cal
    select_bin = 0
    filter = f"abs(cal-({max_cal}+{select_bin}))<0.5"
    # # filter = f"cal == {max_cal}+1 || cal == {max_cal}-1"
    # # filter = f"abs(cal-{max_cal})< 0.5"
    # # filter = "cal > 0"
    print(filter)
    df = df.Filter(filter)
    # pf.plot_cal(df)

    # pf.ToA_CODE(df)
    # Compute ToT
    df = u.compute_ToT(df)
    # Plot the ToT
    pf.ToT(df, title=title)

    ######################################################
    # Plot ToA with mean Cal, each one Cal and max Cal   #
    ######################################################
    # # Compute ToA
    # df_mean = u.compute_ToA(df, mean_cal)
    # # Plot the ToA
    # h_mean = pf.ToA(df_mean, title=title)
    # df_max = u.compute_ToA(df, max_cal)
    # # Plot the ToA
    # h_max = pf.ToA(df_max, title=title)
    # df_each = u.compute_ToA(df)
    # h_each = pf.ToA(df_each, title=title)
    # # Plot both histograms together
    # ROOT.gStyle.SetOptStat(0)
    # c = ROOT.TCanvas()
    # # Legend
    # legend = ROOT.TLegend(0.4, 0.2, 0.6, 0.4)
    # h_mean.SetLineColor(ROOT.kRed)
    # h_mean.Draw()
    # legend.AddEntry(h_mean.GetValue(), f"Mean cal: {mean_cal:.2f}", "l")
    # h_max.SetLineColor(ROOT.kBlue)
    # h_max.Draw("same")
    # legend.AddEntry(h_max.GetValue(), f"Max cal: {max_cal:.2f}", "l")
    # h_each.SetLineColor(ROOT.kGreen)
    # h_each.Draw("same")
    # legend.AddEntry(h_each.GetValue(), f"Each cal", "l")
    # legend.Draw()
    # c.Draw()
    # input("Press Enter to continue...")
    # toa_histograms = pf.ToA(df, title=title, omit_plots=True)
    # pf.fit_ToA_sin(toa_histogram = toa_histograms)

    
if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
