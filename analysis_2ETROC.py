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
@click.argument("k2", type=click.Path(exists=True))
@click.argument("k3", type=click.Path(exists=True))
def main(k2, k3):
    cut = ""
    print(f"[INFO] Reading K2: {k2}")
    df_k2 = ROOT.RDataFrame("Hits", k2)
    file_k2 = ROOT.TFile(k2)
    tree_k2 = file_k2.Get("Hits")

    print(f"[INFO] Reading K3: {k3}")
    df_k3 = ROOT.RDataFrame("Hits", k3)
    file_k3 = ROOT.TFile(k3)
    tree_k3 = file_k3.Get("Hits")

    print("Hit Maps")
    hit_map_k2 = pf.hit_map(df_k2)
    hit_map_k3 = pf.hit_map(df_k3)

    tree_k2.AddFriend(tree_k3, "k3")
    print(tree_k2.Show(0))

    print("Correlations")
    c_correlations_col = ROOT.TCanvas("correlations_col")
    h = ROOT.TH2F("correlations_col", cut, 16, 0, 16, 16, 0, 16)
    tree_k2.Draw("col:k3.col>>correlations_col", cut, "COLZ")
    h.GetXaxis().SetTitle("k3 column")
    h.GetYaxis().SetTitle("k2 column")
    c_correlations_col.Draw()
    input("Press enter to continue...")
    c_correlations_row = ROOT.TCanvas("correlations_row")
    h1 = ROOT.TH2F("correlations_row", cut, 16, 0, 16, 16, 0, 16)
    tree_k2.Draw("row:k3.row>>correlations_row", cut, "COLZ")
    h1.GetXaxis().SetTitle("k3 row")
    h1.GetYaxis().SetTitle("k2 row")
    c_correlations_row.Draw()
    input("Press enter to continue...")

    # Filter df
    # max_cal_k2 = u.get_max_cal(df_k2)
    # max_cal_k3 = u.get_max_cal(df_k3)
    # df_k2_filtered = df_k2.Filter(f"cal=={max_cal_k2}")
    # df_k3_filtered = df_k3.Filter(f"cal=={max_cal_k3}")
    # cut += f"cal=={max_cal_k2} && k3.cal=={max_cal_k3}"

    # Get max cal in each pixel
    
# Histograma 16x16
    h_max_cal_k2 = ROOT.TH2D(
        "h2_max_cal_k2",
        "Max CAL per pixel;col;row",
        16, 0, 16,
        16, 0, 16
    )
    h_max_cal_k3 = ROOT.TH2D(
        "h2_max_cal_k3",
        "Max CAL per pixel;col;row",
        16, 0, 16,
        16, 0, 16
    )

    cut_k2 = []
    cut_k3 = []
    for i_col in tqdm(range(16)):
        for i_row in range(16):
            df_k2_icol_irow = df_k2.Filter(f"col == {i_col} && row == {i_row}")
            df_k3_icol_irow = df_k3.Filter(f"col == {i_col} && row == {i_row}")
            i_cal_k2 = u.get_max_cal(df_k2_icol_irow)
            cut_k2.append(f"(col == {i_col} && row == {i_row} && cal == {i_cal_k2})")
            h_max_cal_k2.SetBinContent(i_col+1, i_row+1, i_cal_k2)
            i_cal_k3 = u.get_max_cal(df_k3_icol_irow)
            cut_k3.append(f"(col == {i_col} && row == {i_row} && cal == {i_cal_k3})")
            h_max_cal_k3.SetBinContent(i_col+1, i_row+1, i_cal_k3)
    print("Max Cal Maps")
    c = ROOT.TCanvas()
    h_max_cal_k2.Draw("TEXT")
    c.Draw()
    input("Press Enter...")
    c = ROOT.TCanvas()
    h_max_cal_k3.Draw("TEXT")
    c.Draw()
    input("Press Enter...")

    cut_k2 = " || ".join(cut_k2)
    cut_k3 = " || ".join(cut_k3)
    df_k2_filtered = df_k2.Filter(cut_k2)
    df_k3_filtered = df_k3.Filter(cut_k3)
    print("Hit Maps")
    hit_map_k2 = pf.hit_map(df_k2_filtered)
    hit_map_k3 = pf.hit_map(df_k3_filtered)

    tree_k2.AddFriend(tree_k3, "k3")
    print(tree_k2.Show(0))
    print("Correlations")
    c_correlations_col = ROOT.TCanvas("correlations_col_2")
    h_col2 = ROOT.TH2F("correlations_col2", cut, 16, 0, 16, 16, 0, 16)
    tree_k2.Draw("col:k3.col>>correlations_col2", cut, "COLZ")
    h_col2.GetXaxis().SetTitle("k3 column")
    h_col2.GetYaxis().SetTitle("k2 column")
    c_correlations_col.Draw()
    input("Press enter to continue...")
    c_correlations_row = ROOT.TCanvas("correlations_row_2")
    h_row2 = ROOT.TH2F("correlations_row_2", cut, 16, 0, 16, 16, 0, 16)
    tree_k2.Draw("row:k3.row>>correlations_row_2", cut, "COLZ")
    h_row2.GetXaxis().SetTitle("k3 row")
    h_row2.GetYaxis().SetTitle("k2 row")
    c_correlations_row.Draw()
    input("Press enter to continue...")

    print("ToA")
    df_k2_filtered = u.compute_ToA(df_k2_filtered)
    df_k2_filtered = u.compute_ToT(df_k2_filtered)
    df_k3_filtered = u.compute_ToA(df_k3_filtered)
    df_k3_filtered = u.compute_ToT(df_k3_filtered)
    print(df_k2_filtered.GetColumnNames())
    toa_k2 = pf.ToA(df_k2_filtered)
    toa_k3 = pf.ToA(df_k3_filtered)
    print("ToT")
    tot_k2 = pf.ToT(df_k2_filtered)
    tot_k3 = pf.ToT(df_k3_filtered)
    print("ToT vs ToA")
    tottoa_k2 = pf.ToT_vs_ToA(df_k2_filtered)
    tottoa_k3 = pf.ToT_vs_ToA(df_k3_filtered)
    # c_delta_toa = ROOT.TCanvas("delta_toa")
    # # tree_k2.Draw("
if __name__ == "__main__":
    main()
