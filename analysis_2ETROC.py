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

@click.command()
@click.argument("file", type=click.Path(exists=True))
def main(file):
    cut = ""
    print(f"[INFO] Reading: {file}")
    df = ROOT.RDataFrame("tree", file)

    print("Hit Maps")

    c = ROOT.TCanvas()
    c.SetRightMargin(0.2) 
    hit_map = df.Histo2D(("hit_map", "Hit map", 16, -0.5, 15.5, 16, -0.5, 15.5), "col_k2", "row_k2")
    hit_map.GetXaxis().SetTitle("Column")
    hit_map.GetYaxis().SetTitle("Row")
    hit_map.GetZaxis().SetTitle("Hits")
    hit_map.Draw("colz")
    hit_map.SetTitle("K2")
    c.Update()
    c.Draw()
    input("Press enter to continue...")
    c = ROOT.TCanvas()
    c.SetRightMargin(0.2) 
    hit_map = df.Histo2D(("hit_map", "Hit map", 16, -0.5, 15.5, 16, -0.5, 15.5), "col_k3", "row_k3")
    hit_map.GetXaxis().SetTitle("Column")
    hit_map.GetYaxis().SetTitle("Row")
    hit_map.GetZaxis().SetTitle("Hits")
    hit_map.Draw("colz")
    hit_map.SetTitle("K3")
    c.Update()
    c.Draw()
    input("Press enter to continue...")

    print("Correlations")
    c_correlations_col = ROOT.TCanvas("correlations_col")
    correlation_col = df.Histo2D(("correlations_col", "Correlation Col", 16, -0.5, 15.5, 16, -0.5, 15.5), "col_k2", "col_k3")
    correlation_col.GetXaxis().SetTitle("k2 column")
    correlation_col.GetYaxis().SetTitle("k3 column")
    correlation_col.Draw()
    c_correlations_col.Draw()
    input("Press enter to continue...")
    c_correlations_row = ROOT.TCanvas("correlations_row")
    correlation_row = df.Histo2D(("correlations_row", "Correlation Row", 16, -0.5, 15.5, 16, -0.5, 15.5), "row_k2", "row_k3")
    correlation_row.GetXaxis().SetTitle("k2 row")
    correlation_row.GetYaxis().SetTitle("k3 row")
    correlation_row.Draw()
    c_correlations_row.Draw()
    input("Press enter to continue...")

    print("Delta ToA")
    c_delta_toa = ROOT.TCanvas("delta_toa")
    df = df.Define("delta_ToA", "ToA_k2 - ToA_k3")
    delta_toa = df.Histo1D(("delta_toa", "Delta ToA (k2-k3)", 1000, -15, 15), "delta_ToA")
    delta_toa.GetXaxis().SetTitle("Delta ToA [ns]")
    delta_toa.GetYaxis().SetTitle("Counts")
    delta_toa.Draw()
    c_delta_toa.Draw()
    input("Press enter to continue...")
if __name__ == "__main__":
    main()
