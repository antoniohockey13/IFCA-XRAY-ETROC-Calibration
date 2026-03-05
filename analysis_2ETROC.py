import ROOT 
import click
import sifca_utils
import os
import math
import numpy as np
import sys
from tqdm import tqdm
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u
from Utils import plot_functions as pf

sifca_utils.plotting.set_sifca_style()

##########################################
# Constants & Units                      #
##########################################
mm = 1
cm = 10 * mm
m = 1e3 * mm
ns = 1
s = 1e9 * ns
PIXEL_SIZE = 1.3 * mm
DELTA_Z = 9 * cm
c = 3e8 * m / s

def GetBeamCenter(hit_map, omit_plots=False):
    
    c_col = ROOT.TCanvas()
    hit_col = hit_map.ProjectionX()
    hit_col.Fit("gaus", "Q")
    hit_col.Draw()
    c_col.Draw()
    fit = hit_col.GetFunction("gaus")
    col_mean = fit.GetParameter(1)
    if not omit_plots:
        input(f"Mean = {col_mean}. Press enter to continue...")
    c_row = ROOT.TCanvas()
    hit_row = hit_map.ProjectionY()
    hit_row.Fit("gaus", "Q")
    hit_row.Draw()
    c_row.Draw()
    fit = hit_row.GetFunction("gaus")
    row_mean = fit.GetParameter(1)
    if not omit_plots:
        input(f"Mean = {row_mean}. Press enter to continue...")
    return [col_mean, row_mean]
    


@click.command()
@click.argument("file", type=click.Path(exists=True))
def main(file):
    cut = ""
    print(f"[INFO] Reading: {file}")
    df = ROOT.RDataFrame("tree", file)

    # Assuming K3 in front
    print("Hit Maps")
    hit_map_k3 = pf.hit_map(df, kintex="_k3")
    hit_map_k2 = pf.hit_map(df, kintex="_k2")

    print("Align planes")
    # Assume beam spot is a straight line and hits both planes, then it must be aligned
    # To find center fit to a gaussian the hit map
    k3_center = GetBeamCenter(hit_map_k3, omit_plots=True)
    k2_center = GetBeamCenter(hit_map_k2, omit_plots=True)

    print("Correlations")
    c_correlations = ROOT.TCanvas("correlations")
    c_correlations.Divide(2,2)
    c_correlations.cd(1)
    correlation_colcol = df.Histo2D(("correlations_colcol", "Correlation ColCol", 16, -0.5, 15.5, 16, -0.5, 15.5), "col_k2", "col_k3")
    correlation_colcol.GetXaxis().SetTitle("k2 column")
    correlation_colcol.GetYaxis().SetTitle("k3 column")
    correlation_colcol.Draw()
    c_correlations.cd(2)
    correlation_rowrow = df.Histo2D(("correlations_rowrow", "Correlation RowRow", 16, -0.5, 15.5, 16, -0.5, 15.5), "row_k2", "row_k3")
    correlation_rowrow.GetXaxis().SetTitle("k2 row")
    correlation_rowrow.GetYaxis().SetTitle("k3 row")
    correlation_rowrow.Draw()
    c_correlations.cd(3)
    correlation_colrow = df.Histo2D(("correlations_colrow", "Correlation ColRow", 16, -0.5, 15.5, 16, -0.5, 15.5), "col_k2", "row_k3")
    correlation_colrow.GetXaxis().SetTitle("k2 column")
    correlation_colrow.GetYaxis().SetTitle("k3 row")
    correlation_colrow.Draw()
    c_correlations.cd(4)
    correlation_rowcol = df.Histo2D(("correlations_rowcol", "Correlation RowCol", 16, -0.5, 15.5, 16, -0.5, 15.5), "row_k2", "col_k3")
    correlation_rowcol.GetXaxis().SetTitle("k2 row")
    correlation_rowcol.GetYaxis().SetTitle("k3 column")
    correlation_rowcol.Draw()
    c_correlations.Draw()
    input("Press enter to continue...")

    print("Delta ToA")
    c_delta_toa = ROOT.TCanvas("delta_toa")
    df = df.Define("delta_ToA", "ToA_k3 - ToA_k2")
    delta_toa = df.Histo1D(("delta_toa", "Delta ToA (k3-k2)", 1000, -15, 15), "delta_ToA")
    delta_toa.GetXaxis().SetTitle("Delta ToA [ns]")
    delta_toa.GetYaxis().SetTitle("Counts")
    delta_toa.Draw()
    c_delta_toa.Draw()
    input("Press enter to continue...")
    
    print("Compton Angle from geometry")
    # Define new positions with respect to beam center x_beam, y_beam
    df = df.Define("x_k3_beam", f"(col_k3-{k3_center[0]})*{PIXEL_SIZE}").Define("y_k3_beam", f"(row_k3-{k3_center[1]})*{PIXEL_SIZE}")
    df = df.Define("x_k2_beam", f"(col_k2-{k2_center[0]})*{PIXEL_SIZE}").Define("y_k2_beam", f"(row_k2-{k2_center[1]})*{PIXEL_SIZE}")
    
    # Now we can use this coordinates to compute the Compton Angle
    df = df.Define("compton_angle_geo", f"""acos({DELTA_Z}/
        (sqrt(  (x_k2_beam-x_k3_beam)*(x_k2_beam-x_k3_beam) + 
                (y_k2_beam-y_k3_beam)*(y_k2_beam-y_k3_beam) +{DELTA_Z}*{DELTA_Z}) ))""")
    c_compton = ROOT.TCanvas("compton")
    legend = ROOT.TLegend()
    h_compton_geo = df.Histo1D(("h_compton_geo", "Compton Angle", 500, 0, 3.14), "compton_angle_geo")
    h_compton_geo.GetXaxis().SetTitle("Compton Angle [rad]")
    h_compton_geo.GetYaxis().SetTitle("Counts")
    h_compton_geo.SetLineColor(ROOT.kBlue)
    legend.AddEntry(h_compton_geo.GetPtr(), "Compton angle from geometry", "l")
    h_compton_geo.Draw()
    c_compton.Draw()
    input("Press enter to continue...")

    print("Compton angle from ToF")
    df = df.Define("compton_angle_tof", f"acos({DELTA_Z}/({c}*delta_ToA))")
    h_compton_tof = df.Histo1D(("h_compton_tof", "Compton Angle", 500, 0, 3.14), "compton_angle_tof")
    h_compton_tof.Draw("same")
    legend.AddEntry(h_compton_tof.GetPtr(), "Compton angle from ToF", "l")
    legend.Draw()
    c_compton.Draw()
    input("Press enter to continue...")

    # df_filter = df.Filter("compton_angle_tof < 1.5")
    # 
    # print("Delta ToA Filtered by Compton Angle ToF")
    # c_delta_toa = ROOT.TCanvas("delta_toa_1")
    # delta_toa = df_filter.Histo1D(("delta_toa_1", "Delta ToA (k3-k2)", 1000, -15, 15), "delta_ToA")
    # delta_toa.GetXaxis().SetTitle("Delta ToA [ns]")
    # delta_toa.GetYaxis().SetTitle("Counts")
    # delta_toa.Draw()
    # c_delta_toa.Draw()
    # input("Press enter to continue...")


if __name__ == "__main__":
    main()
