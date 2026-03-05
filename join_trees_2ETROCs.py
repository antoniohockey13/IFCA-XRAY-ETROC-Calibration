import ROOT
import click
import numpy as np
import os
from tqdm import tqdm
from array import array
from Utils import utils as u

@click.command()
@click.argument("k2", type=click.Path(exists=True))
@click.argument("k3", type=click.Path(exists=True))
def main(k2, k3):
    
    run_dir = os.path.dirname(os.path.abspath(k2))  
    k_dir = os.path.basename(os.path.dirname(run_dir)) 
    run_name = os.path.splitext(os.path.basename(k2))[0]
    out_dir = f"{k_dir}/Joined"
    file_name = f"{out_dir}/{run_name}.root"
    os.makedirs(out_dir, exist_ok=True)

    print(f"[INFO] Reading K2: {k2}")
    df_k2 = ROOT.RDataFrame("Hits", k2)

    print(f"[INFO] Reading K3: {k3}")
    df_k3 = ROOT.RDataFrame("Hits", k3)


    # Compute max cal
    print("Compute and filter by the mode of cal values in eaxh pixel")
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
            cut_k2.append(f"(col == {i_col} && row == {i_row} && abs(cal - {i_cal_k2})<1)")
            h_max_cal_k2.SetBinContent(i_col+1, i_row+1, i_cal_k2)
            i_cal_k3 = u.get_max_cal(df_k3_icol_irow)
            cut_k3.append(f"(col == {i_col} && row == {i_row} && abs(cal - {i_cal_k3})<1)")
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
    df_k2 = df_k2.Filter(cut_k2)
    df_k3 = df_k3.Filter(cut_k3)

    print("Define ToA and ToT columns")
    df_k2 = u.compute_ToA(df_k2)
    df_k2 = u.compute_ToT(df_k2)
    df_k3 = u.compute_ToA(df_k3)
    df_k3 = u.compute_ToT(df_k3)

    columns = ["event_id_", "col", "row", "ToA", "ToT", "cal"]
    data_k2 = df_k2.AsNumpy(columns)
    data_k3 = df_k3.AsNumpy(columns)

    # event_ids of each ETROC
    ids_k2 = data_k2["event_id_"]
    ids_k3 = data_k3["event_id_"]
    common_ids = list(set(ids_k2) & set(ids_k3))
    print(f"Number of common event_id_: {len(common_ids)}")

    # Filter common events
    mask_k2 = np.isin(ids_k2, common_ids)
    mask_k3 = np.isin(ids_k3, common_ids)
    
    toa1 = data_k2["ToA"][mask_k2]
    tot1 = data_k2["ToT"][mask_k2]
    col1 = data_k2["col"][mask_k2]
    row1 = data_k2["row"][mask_k2]
    cal1 = data_k2["cal"][mask_k2]
    eventid1 = data_k2["event_id_"][mask_k2]
    
    toa2 = data_k3["ToA"][mask_k3]
    tot2 = data_k3["ToT"][mask_k3]
    col2 = data_k3["col"][mask_k3]
    cal2 = data_k3["cal"][mask_k3]
    row2 = data_k3["row"][mask_k3]
    eventid2 = data_k3["event_id_"][mask_k3]
    
    # ROOT file
    f = ROOT.TFile(file_name, "RECREATE")
    t = ROOT.TTree("tree", "tree")
    
    # Create branches
    arrs = {
        "ToA_k2": array('d', [0.0]),
        "ToT_k2": array('d', [0.0]),
        "col_k2": array('i', [0]),
        "row_k2": array('i', [0]),
        "cal_k2": array('i', [0]),
        "event_id_k2": array('i', [0]),
        "ToA_k3": array('d', [0.0]),
        "ToT_k3": array('d', [0.0]),
        "col_k3": array('i', [0]),
        "row_k3": array('i', [0]),
        "cal_k3": array('i', [0]),
        "event_id_k3": array('i', [0])
    }
    
    for name in arrs:
        dtype = 'D' if arrs[name].typecode == 'd' else 'I'
        t.Branch(name, arrs[name], f"{name}/{dtype}")
    
    # Fill tree
    print(len(toa1), len(toa2))
    n_events = min(len(toa1), len(toa2))
    
    for i in range(n_events):
        arrs["ToA_k2"][0] = toa1[i]
        arrs["ToT_k2"][0] = tot1[i]
        arrs["col_k2"][0] = col1[i]
        arrs["cal_k2"][0] = cal1[i]
        arrs["row_k2"][0] = row1[i]
        arrs["event_id_k2"][0] = eventid1[i]
    
        arrs["ToA_k3"][0] = toa2[i]
        arrs["ToT_k3"][0] = tot2[i]
        arrs["col_k3"][0] = col2[i]
        arrs["row_k3"][0] = row2[i]
        arrs["cal_k3"][0] = cal2[i]
        arrs["event_id_k3"][0] = eventid2[i]
    
        t.Fill()
    f.Write()
    f.Close()
    
    print(f"ROOT file stored as '{file_name}'")

    # Total number of entries
    # n_k2 = df_k2.Count().GetValue()
    # n_k3 = df_k3.Count().GetValue()

    # ids_k2 = set(df_k2.AsNumpy(["event_id_"])["event_id_"])
    # ids_k3 = set(df_k3.AsNumpy(["event_id_"])["event_id_"])

    # u_k2 = len(np.unique(ids_k2))
    # u_k3 = len(np.unique(ids_k3))

    # print(f"K2: {n_k2} entries, {u_k2} unique event_id_")
    # print(f"K3: {n_k3} entries, {u_k3} unique event_id_")


    # common_ids = ids_k2 & ids_k3
    # print("Common events:", len(common_ids))
    # print("Only in K2:", len(ids_k2 - ids_k3))
    # print("Only in K3:", len(ids_k3 - ids_k2))

    # # Find commond ids

    # # Filter df to have only those events
    # cut = [f"event_id_ == {x}" for x in common_ids]
    # cut = " || ".join(cut)
    # print(cut)
    # df_k2 = df_k2.Filter(cut)
    # df_k3 = df_k3.Filter(cut)
    # 

if __name__ == "__main__":
    main()
