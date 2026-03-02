import ROOT 
import click
import sifca_utils
import os
import math
import numpy as np
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u
from Utils import plot_functions as pf

sifca_utils.plotting.set_sifca_style()

@click.command()
@click.argument("k2", type=click.Path(exists=True))
@click.argument("k3", type=click.Path(exists=True))
def main(k2, k3):

    print(f"[INFO] Reading K2: {k2}")
    df_k2 = ROOT.RDataFrame("Hits", k2)
    file_k2 = ROOT.TFile(k2)
    tree_k2 = file_k2.Get("Hits")

    print(f"[INFO] Reading K3: {k3}")
    df_k3 = ROOT.RDataFrame("Hits", k3)
    file_k3 = ROOT.TFile(k3)
    tree_k3 = file_k3.Get("Hits")

    # print("Hit Maps")
    # hit_map_k2 = pf.hit_map(df_k2)
    # hit_map_k3 = pf.hit_map(df_k3)

    tree_k2.AddFriend(tree_k3, "k3")
    print(tree_k2.Show(0))
    print("Correlations")
    c_correlations_col = ROOT.TCanvas("correlations_col")
    tree_k2.Draw("col:k3.col","","COLZ")
    c_correlations_col.Draw()
    c_correlations_row = ROOT.TCanvas("correlations_row")
    tree_k2.Draw("row:k3.row","","COLZ")
    c_correlations_row.Draw()
    input("Press enter to continue...")

    print("Delta ToA")
    max_cal_k2 = u.get_max_cal(df_k2)
    max_cal_k3 = u.get_max_cal(df_k3)
    c_delta_toa = ROOT.TCanvas("delta_toa")
    tree_k2.Draw("
if __name__ == "__main__":
    main()
